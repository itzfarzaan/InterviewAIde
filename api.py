from flask import Flask, request, jsonify, render_template, session
from groq import Groq
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'llama3-70b-8192'

def validate_and_extract_domains(input_text):
    """Use the Groq model to validate the input and extract relevant domains"""
    system_message = """You are an AI assistant tasked with analyzing a user's input about their professional background or interests. 
    Your job is to:
    1. Determine if the input is a valid description of professional domains, fields of study, or job titles.
    2. Extract relevant domains or fields mentioned in the input.
    3. Ignore any irrelevant or personal information.
    
    Respond with:
    - 'Invalid: [reason]' if the input is gibberish or completely unrelated to professional domains.
    - 'Valid: [extracted domains]' if the input contains valid professional information."""
    
    user_message = f"Analyze this input and extract relevant professional domains or fields: '{input_text}'"

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=200,
        temperature=0.3
    )

    result = response.choices[0].message.content.strip()
    is_valid = result.lower().startswith('valid')
    return is_valid, result

def generate_interview_questions(domains):
    """Generate interview questions based on the given domains using Groq API"""
    system_message = """You are an expert interviewer tasked with generating relevant and insightful interview questions for any job position in any field. 
    Focus on questions that can be answered verbally and demonstrate understanding of concepts, problem-solving approaches, and best practices in the specified domains."""
    
    user_message = f"""Generate 5 interview questions for a position related to the following domains: {domains}. Each question should:
    1. Be directly related to one or more of the specified domains
    2. Be suitable for verbal answers in an interview setting
    3. Focus on relevant skills, experiences, or scenarios in the fields
    4. Be clear and concise
    5. Be appropriate for assessing a candidate's suitability for roles in these domains
    Provide only the questions, one per line, without any additional text or numbering."""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )

    generated_content = response.choices[0].message.content
    questions = [q.strip() for q in generated_content.split('\n') if q.strip()][:5]
    return questions

def generate_final_feedback(questions, answers):
    """Generate cumulative feedback for all answers"""
    system_message = "You are an AI assistant providing cumulative feedback on a developer interview focusing on their knowledge in their domain."
    user_message = "Here are the questions and answers from the interview:\n\n"
    for q, a in zip(questions, answers):
        user_message += f"Q: {q}\nA: {a}\n\n"
    user_message += "Provide concise, constructive feedback on the overall performance. Highlight strengths and areas for improvement."

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )

    return response.choices[0].message.content

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/start_interview', methods=['POST'])
# def start_interview():
#     user_input = request.json.get('domain')
#     if not user_input:
#         return jsonify({'error': 'Missing input'}), 400
    
#     is_valid, validation_message = validate_and_extract_domains(user_input)
#     if not is_valid:
#         return jsonify({'error': validation_message}), 400
    
#     # Extract domains from the validation message
#     domains = validation_message.split(':', 1)[1].strip()
    
#     questions = generate_interview_questions(domains)
#     session['questions'] = questions
#     session['current_question'] = 0
#     session['answers'] = []
#     return jsonify({"question": questions[0]})

@app.route('/answer_question', methods=['POST'])
def answer_question():
    answer = request.json.get('answer')
    if 'questions' not in session:
        return jsonify({'error': 'No active interview'}), 400

    current_question = session['current_question']
    questions = session['questions']
    
    session['answers'].append(answer)

    session['current_question'] += 1
    if session['current_question'] < len(questions):
        next_question = questions[session['current_question']]
        return jsonify({"next_question": next_question})
    else:
        final_feedback = generate_final_feedback(questions, session['answers'])
        session.clear()
        return jsonify({"final_feedback": final_feedback})


# @app.route('/get_practice_question', methods=['GET'])
# def get_practice_question():
#     # This should return the next question in the practice interview
#     # You might want to keep track of the current question index in the session
#     if 'practice_questions' not in session:
#         session['practice_questions'] = generate_interview_questions("general")  # Or use a specific domain
#         session['current_question'] = 0
    
#     if session['current_question'] < len(session['practice_questions']):
#         question = session['practice_questions'][session['current_question']]
#         session['current_question'] += 1
#         return jsonify({"question": question})
#     else:
#         return jsonify({"question": None})  # No more questions

@app.route('/start_interview', methods=['POST'])
def start_interview():
    user_input = request.json.get('domain')
    if not user_input:
        return jsonify({'error': 'Missing input'}), 400
    
    is_valid, validation_message = validate_and_extract_domains(user_input)
    if not is_valid:
        return jsonify({'error': validation_message}), 400
    
    # Extract domains from the validation message
    domains = validation_message.split(':', 1)[1].strip()
    
    questions = generate_interview_questions(domains)
    return jsonify({"questions": questions})

# Remove or comment out the /get_practice_question route as it's no longer needed


# @app.route('/generate_feedback', methods=['POST'])
# def generate_feedback():
#     data = request.json
#     questions = data.get('questions', [])
#     answers = data.get('answers', [])
    
#     if len(questions) != len(answers):
#         return jsonify({'error': 'Mismatch in number of questions and answers'}), 400
    
#     # Prepare the input for the AI model
#     interview_summary = "Interview Summary:\n"
#     for q, a in zip(questions, answers):
#         interview_summary += f"Q: {q}\nA: {a}\n\n"
    
#     prompt = f"""As an AI interview assistant, analyze the following interview and provide constructive feedback:

# {interview_summary}

# Please provide feedback on:
# 1. Overall performance
# 2. Strengths demonstrated
# 3. Areas for improvement
# 4. Specific advice for future interviews

# Feedback:"""

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": "You are an AI interview assistant providing feedback on practice interviews."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=500,
#         temperature=0.7
#     )

#     feedback = response.choices[0].message.content.strip()
#     return jsonify({"feedback": feedback})


@app.route('/generate_feedback', methods=['POST'])
def generate_feedback():
    try:
        data = request.json
        mode = data.get('mode', '')
        questions = data.get('questions', [])
        answers = data.get('answers', [])
        
        print(f"Generating feedback for {mode} mode")
        print("Received questions:", questions)
        print("Received answers:", answers)
        
        if len(questions) != len(answers):
            print(f"Mismatch in number of questions ({len(questions)}) and answers ({len(answers)})")
            return jsonify({'error': 'Mismatch in number of questions and answers'}), 400
        
        # Prepare the input for the AI model
        interview_summary = "Interview Summary:\n"
        for q, a in zip(questions, answers):
            interview_summary += f"Q: {q}\nA: {a}\n\n"
        
        print("Interview summary:", interview_summary)
        
        prompt = f"""As an AI interview assistant, analyze the following {mode} interview and provide constructive feedback:

{interview_summary}

Please provide feedback on:
1. Overall performance
2. Strengths demonstrated
3. Areas for improvement
4. Specific advice for future interviews

Feedback:"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"You are an AI interview assistant providing feedback on {mode} interviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        feedback = response.choices[0].message.content.strip()
        print("Generated feedback:", feedback)
        return jsonify({"feedback": feedback})
    except Exception as e:
        print("Error in generate_feedback:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)