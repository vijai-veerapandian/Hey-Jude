// Theme Toggle Logic
const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
    document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
});

// File Upload Logic (same as before)
// ...

// Chat Logic (similar to before, but now within this single page)
document.getElementById('chatForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const userInput = document.getElementById('userInput');
    const query = userInput.value;
    if (!query) return;
    
    appendMessage('User', query);
    userInput.value = '';

    appendMessage('AI', 'Thinking...', true);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const result = await response.json();
        const aiResponse = result.response || result.error;
        
        removeThinkingMessage();
        appendMessage('AI', aiResponse);
    } catch (error) {
        removeThinkingMessage();
        appendMessage('AI', `Error: ${error.message}`);
    }
});

// Helper functions for chat display
function appendMessage(sender, message, isThinking = false) {
    // ... (logic from previous script) ...
}
function removeThinkingMessage() {
    // ... (logic from previous script) ...
}

// Logic to show chat after upload
document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    // ... (upload logic from previous script) ...
    if (response.ok) {
        document.getElementById('model-info').style.display = 'none';
        document.getElementById('chat-interface').style.display = 'block';
    }
});
