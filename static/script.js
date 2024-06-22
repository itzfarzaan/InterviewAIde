function sendPrompt() {
    const prompt = document.getElementById('prompt').value;
    if (prompt) {
        fetch(`/questions?domain=${prompt}`)
            .then(response => response.json())
            .then(data => {
                const chatWindow = document.getElementById('chat-window');
                const userMessage = document.createElement('div');
                userMessage.className = 'message user-message';
                userMessage.innerText = prompt;
                chatWindow.appendChild(userMessage);

                if (data.questions) {
                    data.questions.forEach(question => {
                        const aiMessage = document.createElement('div');
                        aiMessage.className = 'message ai-message';
                        aiMessage.innerText = question;
                        chatWindow.appendChild(aiMessage);
                    });
                } else {
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'message ai-message';
                    errorMessage.innerText = 'Error: ' + data.error;
                    chatWindow.appendChild(errorMessage);
                }

                chatWindow.scrollTop = chatWindow.scrollHeight;
            })
            .catch(error => console.error('Error:', error));
    }
}
