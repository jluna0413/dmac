/**
 * Chat functionality for DMac.
 * 
 * This script provides functionality for the chat interface.
 */

// Auto-resize textarea
const chatInput = document.getElementById('chat-input');

chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = chatInput.scrollHeight + 'px';
});

// Send message
document.getElementById('send-message-btn').addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    document.getElementById('chat-messages').appendChild(typingIndicator);
    
    try {
        // Get agent ID from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const agentId = urlParams.get('agent') || 'cody';
        
        // Send message to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                agent_id: agentId
            })
        });
        
        // Remove typing indicator
        typingIndicator.remove();
        
        if (response.ok) {
            const data = await response.json();
            addMessage(data.response, 'agent');
        } else {
            const errorData = await response.json();
            addMessage(`Error: ${errorData.error || 'Unknown error'}`, 'agent');
        }
    } catch (error) {
        // Remove typing indicator
        typingIndicator.remove();
        
        console.error('Error sending message:', error);
        addMessage(`I encountered an error while processing your request. Please try again later.`, 'agent');
    }
}

function addMessage(text, sender) {
    const messagesContainer = document.getElementById('chat-messages');
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Create avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    const avatarImg = document.createElement('img');
    avatarImg.src = sender === 'user' 
        ? '/static/images/user-avatar.png' 
        : '/static/images/agents/cody.svg';
    avatarImg.alt = sender === 'user' ? 'You' : 'Cody';
    
    avatarDiv.appendChild(avatarImg);
    
    // Create message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    const textP = document.createElement('p');
    textP.textContent = text;
    
    textDiv.appendChild(textP);
    
    // Create time
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    
    const now = new Date();
    const hours = now.getHours() % 12 || 12;
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const ampm = now.getHours() >= 12 ? 'PM' : 'AM';
    
    timeDiv.textContent = `${hours}:${minutes} ${ampm}`;
    
    // Assemble message
    contentDiv.appendChild(textDiv);
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    // Add to chat
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// New chat button
document.getElementById('new-chat-btn').addEventListener('click', () => {
    // Clear chat messages
    document.getElementById('chat-messages').innerHTML = '';
    
    // Add welcome message
    addMessage("Hi there! I'm Cody, your code assistant. How can I help you today?", 'agent');
});

// Web scraping button
document.querySelector('.chat-tools button[title="Web Scraping"]').addEventListener('click', () => {
    document.getElementById('web-scrape-modal').classList.add('active');
});

// Handle modal close button
document.querySelector('.close-btn').addEventListener('click', () => {
    document.getElementById('web-scrape-modal').classList.remove('active');
});

// Handle cancel scrape button
document.getElementById('cancel-scrape-btn').addEventListener('click', () => {
    document.getElementById('web-scrape-modal').classList.remove('active');
});

// Handle start scrape button
document.getElementById('start-scrape-btn').addEventListener('click', async () => {
    const url = document.getElementById('scrape-url').value;
    const depth = document.getElementById('scrape-depth').value;
    const maxPages = document.getElementById('scrape-max-pages').value;
    const createDataset = document.getElementById('scrape-dataset').checked;
    
    if (!url) {
        alert('Please enter a URL to scrape.');
        return;
    }
    
    // Close the modal
    document.getElementById('web-scrape-modal').classList.remove('active');
    
    // Add message to chat
    addMessage(`I'll scrape ${url} for you.`, 'agent');
    
    try {
        // Send web scraping request to API
        const response = await fetch('/api/web-scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                depth: depth,
                max_pages: maxPages,
                create_dataset: createDataset
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            addMessage(data.response, 'agent');
        } else {
            const errorData = await response.json();
            addMessage(`Error: ${errorData.error || 'Unknown error'}`, 'agent');
        }
    } catch (error) {
        console.error('Error processing web scraping:', error);
        addMessage(`I encountered an error while scraping the web. Please try again later.`, 'agent');
    }
});

// Typing indicator styles
const style = document.createElement('style');
style.textContent = `
    /* Typing Indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        margin: 10px 0;
    }
    
    .typing-indicator span {
        height: 8px;
        width: 8px;
        float: left;
        margin: 0 1px;
        background-color: #9E9EA1;
        display: block;
        border-radius: 50%;
        opacity: 0.4;
    }
    
    .typing-indicator span:nth-of-type(1) {
        animation: 1s blink infinite 0.3333s;
    }
    
    .typing-indicator span:nth-of-type(2) {
        animation: 1s blink infinite 0.6666s;
    }
    
    .typing-indicator span:nth-of-type(3) {
        animation: 1s blink infinite 0.9999s;
    }
    
    @keyframes blink {
        50% {
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
