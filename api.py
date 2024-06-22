from flask import Flask, request, jsonify, render_template
from groq import Groq
import os

app = Flask(__name__)
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = 'llama3-70b-8192'

def generate_interview_questions(domain):
    """Generate interview questions based on the given domain using Groq API"""
    system_message = "You are an expert interviewer tasked with generating relevant and approachable interview questions for entry-level positions."
    user_message = f"""Generate 5 interview-friendly questions for a student applying for a position in {domain}. The questions should be:
    1. Specific to the domain
    2. Suitable for entry-level or internship positions
    3. Answerable in a few sentences
    4. Focused on fundamental concepts rather than advanced topics
    5. Designed to assess basic understanding and enthusiasm for the field
    Provide only the questions without any numbering or additional commentary."""

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

    # Extract the generated questions from the response
    generated_content = response.choices[0].message.content
    
    # Split the content into individual questions and ensure we have exactly 5
    questions = [q.strip() for q in generated_content.split('\n') if q.strip()][:5]

    return questions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions', methods=['GET'])
def questions():
    domain = request.args.get('domain', '')
    if not domain:
        return jsonify({'error': 'Missing domain'}), 400
    questions = generate_interview_questions(domain)
    return jsonify({"questions": questions})

if __name__ == '__main__':
    app.run(debug=True)
