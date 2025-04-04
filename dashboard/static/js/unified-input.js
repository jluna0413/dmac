/**
 * Unified Input Module
 *
 * This module provides a unified interface for various input methods:
 * - Voice input
 * - File/media upload
 * - Deep research
 * - Deep thinking mode
 */

class UnifiedInput {
    constructor(chatContainerId = 'chat-container', inputContainerId = 'input-container') {
        this.chatContainer = document.getElementById(chatContainerId);
        this.inputContainer = document.getElementById(inputContainerId);
        this.currentModel = 'gemma3:12b'; // Default model
        this.isThinking = false;
        this.isResearching = false;
        this.isListening = false;
        this.uploadedFiles = [];

        // Initialize the voice interaction
        this.voiceInteraction = new VoiceInteraction();

        // Initialize the UI
        this.initializeUI();

        // Load available models
        this.loadModels();
    }

    /**
     * Initialize the unified input UI
     */
    initializeUI() {
        // Create the input container if it doesn't exist
        if (!this.inputContainer) {
            this.inputContainer = document.createElement('div');
            this.inputContainer.id = 'input-container';
            this.inputContainer.className = 'unified-input-container';
            document.body.appendChild(this.inputContainer);
        }

        // Create the chat container if it doesn't exist
        if (!this.chatContainer) {
            this.chatContainer = document.createElement('div');
            this.chatContainer.id = 'chat-container';
            this.chatContainer.className = 'chat-container';
            document.body.insertBefore(this.chatContainer, this.inputContainer);
        }

        // Set up the input container HTML
        this.inputContainer.innerHTML = `
            <div class="input-group mb-2">
                <button id="voice-button" class="btn btn-outline-secondary input-group-prepend" title="Voice Input">
                    <i class="fas fa-microphone"></i>
                </button>
                <textarea id="user-input" class="form-control" placeholder="Type your message here..." rows="2"></textarea>
                <div class="input-group-append d-flex">
                    <button id="upload-button" class="btn btn-outline-secondary" title="Upload Files">
                        <i class="fas fa-upload"></i>
                    </button>
                    <button id="research-button" class="btn btn-outline-secondary" title="Deep Research">
                        <i class="fas fa-search"></i>
                    </button>
                    <button id="think-button" class="btn btn-outline-secondary" title="Deep Thinking Mode">
                        <i class="fas fa-brain"></i>
                    </button>
                    <button id="send-button" class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
                <input type="file" id="file-upload" multiple style="display: none;">
            </div>
            <div class="input-tools d-flex justify-content-center align-items-center">
                <div class="model-selector">
                    <select id="model-selector" class="form-select form-select-sm">
                        <option value="" disabled>Select a model</option>
                    </select>
                </div>
            </div>
            <div id="uploaded-files-container" class="uploaded-files-container mt-2" style="display: none;">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <h6 class="mb-0">Uploaded Files</h6>
                    <button id="clear-files-button" class="btn btn-sm btn-outline-danger">
                        <i class="fas fa-trash"></i> Clear All
                    </button>
                </div>
                <div id="uploaded-files-list" class="uploaded-files-list"></div>
            </div>
            <div id="thinking-indicator" class="thinking-indicator mt-2" style="display: none;">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                        <span class="visually-hidden">Thinking...</span>
                    </div>
                    <span id="thinking-text">Deep thinking mode activated...</span>
                </div>
            </div>
        `;

        // Add event listeners
        this.addEventListeners();

        // Add styles
        this.addStyles();
    }

    /**
     * Add event listeners to the UI elements
     */
    addEventListeners() {
        // Send button
        const sendButton = document.getElementById('send-button');
        sendButton.addEventListener('click', () => this.sendMessage());

        // User input (for Enter key)
        const userInput = document.getElementById('user-input');
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Voice button
        const voiceButton = document.getElementById('voice-button');
        voiceButton.addEventListener('click', () => this.toggleVoiceInput());

        // Upload button
        const uploadButton = document.getElementById('upload-button');
        const fileUpload = document.getElementById('file-upload');

        uploadButton.addEventListener('click', () => {
            fileUpload.click();
        });

        fileUpload.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        // Clear files button
        const clearFilesButton = document.getElementById('clear-files-button');
        clearFilesButton.addEventListener('click', () => this.clearUploadedFiles());

        // Research button
        const researchButton = document.getElementById('research-button');
        researchButton.addEventListener('click', () => this.toggleResearchMode());

        // Think button
        const thinkButton = document.getElementById('think-button');
        thinkButton.addEventListener('click', () => this.toggleThinkingMode());

        // Model selector
        const modelSelector = document.getElementById('model-selector');
        modelSelector.addEventListener('change', (e) => {
            this.currentModel = e.target.value;
        });
    }

    /**
     * Add CSS styles for the unified input
     */
    addStyles() {
        // Check if styles already exist
        if (document.getElementById('unified-input-styles')) {
            return;
        }

        // Create style element
        const style = document.createElement('style');
        style.id = 'unified-input-styles';

        // Add CSS
        style.textContent = `
            .unified-input-container {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: var(--bs-body-bg);
                padding: 15px;
                border-top: 1px solid var(--bs-border-color);
                z-index: 1000;
            }

            .chat-container {
                margin-bottom: 150px;
                padding: 15px;
                overflow-y: auto;
                height: calc(100vh - 150px);
            }

            .tool-button {
                margin-right: 5px;
                width: 40px;
                height: 40px;
                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
            }

            .tool-button.active {
                background-color: var(--bs-primary);
                color: white;
            }

            .uploaded-files-list {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }

            .uploaded-file {
                background-color: var(--bs-light);
                border-radius: 5px;
                padding: 5px 10px;
                display: flex;
                align-items: center;
                max-width: 200px;
            }

            .uploaded-file .file-icon {
                margin-right: 5px;
            }

            .uploaded-file .file-name {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                flex: 1;
            }

            .uploaded-file .remove-file {
                cursor: pointer;
                margin-left: 5px;
                color: var(--bs-danger);
            }

            .message {
                margin-bottom: 15px;
                display: flex;
                flex-direction: column;
            }

            .user-message {
                align-items: flex-end;
            }

            .assistant-message {
                align-items: flex-start;
            }

            .message-content {
                max-width: 80%;
                padding: 10px 15px;
                border-radius: 10px;
            }

            .user-message .message-content {
                background-color: var(--bs-primary);
                color: white;
            }

            .assistant-message .message-content {
                background-color: var(--bs-light);
            }

            .thinking-dots {
                display: inline-block;
            }

            .thinking-dots::after {
                content: '';
                animation: thinking 1.5s infinite;
            }

            @keyframes thinking {
                0% { content: '.'; }
                33% { content: '..'; }
                66% { content: '...'; }
                100% { content: '.'; }
            }

            /* Dark mode adjustments */
            [data-theme="dark"] .uploaded-file {
                background-color: var(--bs-dark);
            }

            [data-theme="dark"] .assistant-message .message-content {
                background-color: var(--bs-dark);
            }
        `;

        // Add to document
        document.head.appendChild(style);
    }

    /**
     * Load available models from the API
     */
    loadModels() {
        fetch('/api/ollama/models')
            .then(response => response.json())
            .then(data => {
                if (data.models && data.models.length > 0) {
                    const modelSelector = document.getElementById('model-selector');

                    // Clear existing options
                    modelSelector.innerHTML = '';

                    // Add models to the select
                    data.models.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = model.name;

                        // Set as selected if it matches the current model
                        if (model.name === this.currentModel) {
                            option.selected = true;
                        }

                        modelSelector.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error loading models:', error));
    }

    /**
     * Send a message to the AI
     */
    sendMessage() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();

        if (!message && this.uploadedFiles.length === 0) {
            return;
        }

        // Clear the input
        userInput.value = '';

        // Add the message to the chat
        this.addMessageToChat(message, 'user');

        // Prepare the request data
        const requestData = {
            message: message,
            model: this.currentModel,
            files: this.uploadedFiles,
            deep_research: this.isResearching,
            deep_thinking: this.isThinking
        };

        // Show thinking indicator
        this.addThinkingIndicator();

        // Send the request to the API
        fetch('/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
            .then(response => response.json())
            .then(data => {
                // Remove thinking indicator
                this.removeThinkingIndicator();

                if (data.success) {
                    // Add the response to the chat
                    this.addMessageToChat(data.response, 'assistant');

                    // Clear uploaded files if any
                    if (this.uploadedFiles.length > 0) {
                        this.clearUploadedFiles();
                    }

                    // Reset modes
                    this.resetModes();
                } else {
                    // Add error message
                    this.addMessageToChat('Error: ' + (data.error || 'Unknown error'), 'assistant');
                }
            })
            .catch(error => {
                console.error('Error sending message:', error);

                // Remove thinking indicator
                this.removeThinkingIndicator();

                // Add error message
                this.addMessageToChat('Error: Could not connect to the server.', 'assistant');
            });
    }

    /**
     * Add a message to the chat
     * @param {string} message - The message text
     * @param {string} sender - The sender ('user' or 'assistant')
     */
    addMessageToChat(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        // If the message is empty and there are uploaded files, show a file message
        if (!message && sender === 'user' && this.uploadedFiles.length > 0) {
            messageContent.innerHTML = `<p>Sent ${this.uploadedFiles.length} file(s)</p>`;
        } else {
            // Process markdown if it's from the assistant
            if (sender === 'assistant') {
                // Use a markdown library or simple regex for basic formatting
                const formattedMessage = this.formatMarkdown(message);
                messageContent.innerHTML = formattedMessage;
            } else {
                // Escape HTML for user messages
                messageContent.textContent = message;
            }
        }

        messageDiv.appendChild(messageContent);
        this.chatContainer.appendChild(messageDiv);

        // Scroll to the bottom
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    /**
     * Format markdown text to HTML
     * @param {string} text - The markdown text
     * @returns {string} - The HTML formatted text
     */
    formatMarkdown(text) {
        // This is a very simple markdown formatter
        // For a real implementation, use a library like marked.js

        // Code blocks
        text = text.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');

        // Bold
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Links
        text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');

        // Lists
        text = text.replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>');
        text = text.replace(/<li>(.*?)<\/li>/gs, '<ul>$&</ul>');

        // Paragraphs
        text = text.replace(/\n\n/g, '</p><p>');
        text = '<p>' + text + '</p>';

        return text;
    }

    /**
     * Add a thinking indicator to the chat
     */
    addThinkingIndicator() {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'message assistant-message thinking-message';
        thinkingDiv.id = 'thinking-message';

        const thinkingContent = document.createElement('div');
        thinkingContent.className = 'message-content';

        // Different text based on modes
        let thinkingText = 'Thinking';
        if (this.isThinking) {
            thinkingText = 'Deep thinking';
        } else if (this.isResearching) {
            thinkingText = 'Researching';
        }

        thinkingContent.innerHTML = `<p>${thinkingText}<span class="thinking-dots"></span></p>`;

        thinkingDiv.appendChild(thinkingContent);
        this.chatContainer.appendChild(thinkingDiv);

        // Scroll to the bottom
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    /**
     * Remove the thinking indicator from the chat
     */
    removeThinkingIndicator() {
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }
    }

    /**
     * Toggle voice input mode
     */
    toggleVoiceInput() {
        const voiceButton = document.getElementById('voice-button');

        if (this.isListening) {
            // Stop listening
            this.voiceInteraction.stopListening();
            this.isListening = false;
            voiceButton.classList.remove('active');
        } else {
            // Start listening
            this.voiceInteraction.startListening(text => {
                const userInput = document.getElementById('user-input');
                userInput.value = text;
                this.isListening = false;
                voiceButton.classList.remove('active');

                // Auto-send if in research or thinking mode
                if (this.isResearching || this.isThinking) {
                    this.sendMessage();
                }
            });

            this.isListening = true;
            voiceButton.classList.add('active');
        }
    }

    /**
     * Handle file upload
     * @param {FileList} files - The uploaded files
     */
    handleFileUpload(files) {
        if (!files || files.length === 0) {
            return;
        }

        const uploadedFilesContainer = document.getElementById('uploaded-files-container');
        const uploadedFilesList = document.getElementById('uploaded-files-list');

        // Show the container
        uploadedFilesContainer.style.display = 'block';

        // Process each file
        Array.from(files).forEach(file => {
            // Create a file object
            const fileObj = {
                name: file.name,
                type: file.type,
                size: file.size,
                content: null
            };

            // Read the file content
            const reader = new FileReader();

            reader.onload = (e) => {
                fileObj.content = e.target.result;
                this.uploadedFiles.push(fileObj);

                // Add the file to the UI
                this.addFileToUI(fileObj);
            };

            reader.readAsDataURL(file);
        });
    }

    /**
     * Add a file to the UI
     * @param {Object} file - The file object
     */
    addFileToUI(file) {
        const uploadedFilesList = document.getElementById('uploaded-files-list');

        const fileDiv = document.createElement('div');
        fileDiv.className = 'uploaded-file';
        fileDiv.dataset.fileName = file.name;

        // Determine the file icon based on type
        let fileIcon = 'fa-file';
        if (file.type.startsWith('image/')) {
            fileIcon = 'fa-file-image';
        } else if (file.type.startsWith('video/')) {
            fileIcon = 'fa-file-video';
        } else if (file.type.startsWith('audio/')) {
            fileIcon = 'fa-file-audio';
        } else if (file.type.startsWith('text/')) {
            fileIcon = 'fa-file-alt';
        } else if (file.type.includes('pdf')) {
            fileIcon = 'fa-file-pdf';
        } else if (file.type.includes('word')) {
            fileIcon = 'fa-file-word';
        } else if (file.type.includes('excel') || file.type.includes('spreadsheet')) {
            fileIcon = 'fa-file-excel';
        } else if (file.type.includes('zip') || file.type.includes('compressed')) {
            fileIcon = 'fa-file-archive';
        } else if (file.type.includes('code') || file.name.match(/\.(js|py|java|c|cpp|html|css)$/)) {
            fileIcon = 'fa-file-code';
        }

        fileDiv.innerHTML = `
            <span class="file-icon"><i class="fas ${fileIcon}"></i></span>
            <span class="file-name" title="${file.name}">${file.name}</span>
            <span class="remove-file" data-file-name="${file.name}"><i class="fas fa-times"></i></span>
        `;

        // Add event listener to remove button
        fileDiv.querySelector('.remove-file').addEventListener('click', () => {
            this.removeFile(file.name);
        });

        uploadedFilesList.appendChild(fileDiv);
    }

    /**
     * Remove a file from the uploaded files
     * @param {string} fileName - The name of the file to remove
     */
    removeFile(fileName) {
        // Remove from the array
        this.uploadedFiles = this.uploadedFiles.filter(file => file.name !== fileName);

        // Remove from the UI
        const fileDiv = document.querySelector(`.uploaded-file[data-file-name="${fileName}"]`);
        if (fileDiv) {
            fileDiv.remove();
        }

        // Hide the container if no files left
        if (this.uploadedFiles.length === 0) {
            document.getElementById('uploaded-files-container').style.display = 'none';
        }
    }

    /**
     * Clear all uploaded files
     */
    clearUploadedFiles() {
        // Clear the array
        this.uploadedFiles = [];

        // Clear the UI
        document.getElementById('uploaded-files-list').innerHTML = '';

        // Hide the container
        document.getElementById('uploaded-files-container').style.display = 'none';
    }

    /**
     * Toggle research mode
     */
    toggleResearchMode() {
        const researchButton = document.getElementById('research-button');

        this.isResearching = !this.isResearching;

        if (this.isResearching) {
            researchButton.classList.add('active');

            // If thinking mode is on, turn it off
            if (this.isThinking) {
                this.toggleThinkingMode();
            }

            // Show indicator
            document.getElementById('thinking-indicator').style.display = 'block';
            document.getElementById('thinking-text').textContent = 'Deep research mode activated...';
        } else {
            researchButton.classList.remove('active');

            // Hide indicator
            document.getElementById('thinking-indicator').style.display = 'none';
        }
    }

    /**
     * Toggle thinking mode
     */
    toggleThinkingMode() {
        const thinkButton = document.getElementById('think-button');

        this.isThinking = !this.isThinking;

        if (this.isThinking) {
            thinkButton.classList.add('active');

            // If research mode is on, turn it off
            if (this.isResearching) {
                this.toggleResearchMode();
            }

            // Show indicator
            document.getElementById('thinking-indicator').style.display = 'block';
            document.getElementById('thinking-text').textContent = 'Deep thinking mode activated...';
        } else {
            thinkButton.classList.remove('active');

            // Hide indicator
            document.getElementById('thinking-indicator').style.display = 'none';
        }
    }

    /**
     * Reset all modes
     */
    resetModes() {
        // Reset research mode
        if (this.isResearching) {
            this.toggleResearchMode();
        }

        // Reset thinking mode
        if (this.isThinking) {
            this.toggleThinkingMode();
        }

        // Reset voice input
        if (this.isListening) {
            this.toggleVoiceInput();
        }
    }
}

// Initialize the unified input when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on a page that should have the unified input
    const chatPages = ['/chat', '/assistant', '/'];
    const currentPath = window.location.pathname;

    if (chatPages.includes(currentPath)) {
        window.unifiedInput = new UnifiedInput();
    }
});
