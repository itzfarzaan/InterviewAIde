let isInterviewStarted = false;
let isDomainProvided = false;

window.onload = function() {
    const initialMessage = "Enter your domain/your profession/your educational background. After entering your details, only reply to the questions with an answer. Do not type anything else.";
    displayMessage(initialMessage, 'ai-message');
};

function handleUserInput() {
    const userInput = document.getElementById('user-input').value.trim();
    if (userInput) {
        if (!isDomainProvided) {
            startInterview(userInput);
        } else {
            submitAnswer(userInput);
        }
        document.getElementById('user-input').value = '';
    }
}

function startInterview(domain) {
    fetch('/start_interview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain: domain }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            displayMessage(data.error, 'ai-message');
        } else {
            isDomainProvided = true;
            isInterviewStarted = true;
            displayMessage(domain, 'user-message');
            displayMessage(data.question, 'ai-message');
        }
    })
    .catch(error => console.error('Error:', error));
}

function submitAnswer(answer) {
    fetch('/answer_question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer: answer }),
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(answer, 'user-message');
        if (data.next_question) {
            displayMessage(data.next_question, 'ai-message');
        } else if (data.final_feedback) {
            displayMessage("Thank you for completing the interview. Here's your overall feedback:", 'ai-message');
            displayMessage(data.final_feedback, 'ai-message');
            isInterviewStarted = false;
        }
    })
    .catch(error => console.error('Error:', error));
}

function displayMessage(message, className) {
    const chatWindow = document.getElementById('chat-window');
    const messageElement = document.createElement('div');
    messageElement.className = 'message ' + className;
    messageElement.innerText = message;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}