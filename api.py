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
    session['questions'] = questions
    session['current_question'] = 0
    session['answers'] = []
    return jsonify({"question": questions[0]})

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

if __name__ == '__main__':
    app.run(debug=True)