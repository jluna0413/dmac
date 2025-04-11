/**
 * Voice Interaction Module
 *
 * This module provides voice interaction functionality for the DMac application.
 */

class VoiceInteraction {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.initializeSpeechRecognition();
        this.voices = [];
        this.preferredVoice = null;
        this.initializeVoices();
    }

    /**
     * Initialize the speech recognition functionality
     */
    initializeSpeechRecognition() {
        console.log('Initializing speech recognition...');

        // Check for different speech recognition APIs
        if ('webkitSpeechRecognition' in window) {
            console.log('Using webkitSpeechRecognition');
            this.recognition = new webkitSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            console.log('Using standard SpeechRecognition');
            this.recognition = new SpeechRecognition();
        } else {
            console.warn('Speech recognition not supported in this browser');
            return;
        }

        // Configure the recognition object
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateMicrophoneUI(true);
            console.log('Voice recognition started');
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateMicrophoneUI(false);
            console.log('Voice recognition ended');
        };

        this.recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            this.isListening = false;
            this.updateMicrophoneUI(false);

            // Show error message to user
            if (event.error === 'not-allowed') {
                alert('Microphone access denied. Please allow microphone access in your browser settings.');
            } else if (event.error === 'no-speech') {
                console.log('No speech detected');
            } else {
                console.error('Speech recognition error:', event.error);
            }
        };

        console.log('Speech recognition initialized successfully');
    }

    /**
     * Initialize the speech synthesis voices
     */
    initializeVoices() {
        // Get the available voices
        this.voices = this.synthesis.getVoices();

        // If voices are not loaded yet, wait for them
        if (this.voices.length === 0) {
            this.synthesis.addEventListener('voiceschanged', () => {
                this.voices = this.synthesis.getVoices();
                this.selectPreferredVoice();
            });
        } else {
            this.selectPreferredVoice();
        }
    }

    /**
     * Select a preferred voice (female English voice if available)
     */
    selectPreferredVoice() {
        // Try to find a female English voice
        for (let voice of this.voices) {
            if (voice.lang.includes('en-') && voice.name.toLowerCase().includes('female')) {
                this.preferredVoice = voice;
                console.log('Selected preferred voice:', voice.name);
                break;
            }
        }

        // If no female English voice found, try any English voice
        if (!this.preferredVoice) {
            for (let voice of this.voices) {
                if (voice.lang.includes('en-')) {
                    this.preferredVoice = voice;
                    console.log('Selected fallback voice:', voice.name);
                    break;
                }
            }
        }

        // If still no voice found, use the first available voice
        if (!this.preferredVoice && this.voices.length > 0) {
            this.preferredVoice = this.voices[0];
            console.log('Selected default voice:', voice.name);
        }
    }

    /**
     * Update the microphone UI to reflect the current listening state
     * @param {boolean} isListening - Whether the system is currently listening
     */
    updateMicrophoneUI(isListening) {
        // Only update the main voice button in the footer
        const mainVoiceButton = document.querySelector('#voice-button');
        // And any voice input buttons that are not in the footer
        const otherMicButtons = Array.from(document.querySelectorAll('.voice-input-btn')).filter(btn => !btn.closest('.footer'));

        const micButtons = mainVoiceButton ? [mainVoiceButton, ...otherMicButtons] : otherMicButtons;

        console.log('Updating microphone UI, found buttons:', micButtons.length);

        micButtons.forEach(button => {
            if (isListening) {
                button.classList.add('active');
                button.innerHTML = '<i class="fas fa-microphone-alt"></i>';
                console.log('Set button to listening state:', button.id || button.className);
            } else {
                button.classList.remove('active');
                button.innerHTML = '<i class="fas fa-microphone"></i>';
                console.log('Set button to not listening state:', button.id || button.className);
            }
        });
    }

    /**
     * Start listening for voice input
     * @param {Function} callback - Function to call with the recognized text
     */
    startListening(callback) {
        console.log('Starting voice recognition...');

        if (!this.recognition) {
            console.error('Speech recognition not supported or not initialized');
            // Try to initialize again
            this.initializeSpeechRecognition();

            if (!this.recognition) {
                alert('Speech recognition is not supported in your browser');
                return;
            }
        }

        if (this.isListening) {
            console.log('Already listening, stopping first...');
            this.stopListening();
            return;
        }

        this.recognition.onresult = (event) => {
            console.log('Got speech recognition result:', event);
            const transcript = event.results[0][0].transcript;
            console.log('Voice recognized:', transcript);

            if (callback && typeof callback === 'function') {
                callback(transcript);
            }
        };

        try {
            console.log('Starting speech recognition...');
            this.recognition.start();
            console.log('Speech recognition started');
            this.updateMicrophoneUI(true);
        } catch (error) {
            console.error('Error starting speech recognition:', error);
            this.updateMicrophoneUI(false);
            alert('Error starting speech recognition: ' + error.message);
        }
    }

    /**
     * Stop listening for voice input
     */
    stopListening() {
        console.log('Stopping voice recognition...');

        if (!this.recognition) {
            console.error('Speech recognition not available');
            return;
        }

        try {
            if (this.isListening) {
                this.recognition.stop();
                console.log('Speech recognition stopped');
            } else {
                console.log('Not currently listening, nothing to stop');
            }
            this.updateMicrophoneUI(false);
        } catch (error) {
            console.error('Error stopping speech recognition:', error);
        }
    }

    /**
     * Speak the provided text
     * @param {string} text - The text to speak
     * @param {Function} callback - Optional callback function to call when speech is complete
     */
    speak(text, callback) {
        if (!this.synthesis) {
            console.error('Speech synthesis not supported');
            return;
        }

        // Cancel any ongoing speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        // Set the preferred voice if available
        if (this.preferredVoice) {
            utterance.voice = this.preferredVoice;
        }

        // Set speech properties
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Set callback for when speech is complete
        if (callback && typeof callback === 'function') {
            utterance.onend = callback;
        }

        // Speak the text
        this.synthesis.speak(utterance);
    }

    /**
     * Process voice input and get a response from the AI
     * @param {string} text - The voice input text
     * @param {string} model - The model to use for generating a response
     * @param {Function} callback - Function to call with the AI response
     */
    async processVoiceInput(text, model, callback) {
        try {
            // Show loading indicator
            const loadingIndicator = document.getElementById('voice-loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.classList.remove('d-none');
            }

            // Call the API to process the voice input
            const response = await fetch('/api/voice/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    model: model
                })
            });

            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.classList.add('d-none');
            }

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                // Speak the response
                this.speak(data.response, () => {
                    if (callback && typeof callback === 'function') {
                        callback(data.response);
                    }
                });
            } else {
                console.error('Error processing voice input:', data.error);
                this.speak('I\'m sorry, I encountered an error processing your request.');
            }
        } catch (error) {
            console.error('Error calling voice processing API:', error);

            // Hide loading indicator
            const loadingIndicator = document.getElementById('voice-loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.classList.add('d-none');
            }

            this.speak('I\'m sorry, I encountered an error processing your request.');
        }
    }
}

// Create a global instance of the voice interaction module
const voiceInteraction = new VoiceInteraction();

/**
 * Add voice interaction buttons to the page
 */
function addVoiceInteractionButtons() {
    // Add voice input buttons to all input fields
    const inputFields = document.querySelectorAll('input[type="text"], textarea');

    inputFields.forEach(input => {
        // Skip if the input already has a voice button
        if (input.parentElement.querySelector('.voice-input-btn')) {
            return;
        }

        // Skip the chat input area which already has a voice button
        if (input.id === 'user-input') {
            return;
        }

        // Skip inputs in the footer
        if (input.closest('.footer')) {
            return;
        }

        // Create a wrapper if the input doesn't have one
        let wrapper = input.parentElement;
        if (!wrapper.classList.contains('input-group')) {
            // Create a wrapper for the input
            wrapper = document.createElement('div');
            wrapper.className = 'input-group';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);
        }

        // Create the voice input button
        const voiceButton = document.createElement('button');
        voiceButton.type = 'button';
        voiceButton.className = 'btn btn-outline-secondary voice-input-btn';
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceButton.title = 'Voice Input';

        // Add click event to the button
        voiceButton.addEventListener('click', () => {
            voiceInteraction.startListening(text => {
                input.value = text;

                // Trigger input event to update any listeners
                const event = new Event('input', { bubbles: true });
                input.dispatchEvent(event);

                // If this is a search input, trigger search
                if (input.classList.contains('search-input') || input.id.includes('search')) {
                    const form = input.closest('form');
                    if (form) {
                        form.dispatchEvent(new Event('submit'));
                    }
                }
            });
        });

        // Add the button to the wrapper
        wrapper.appendChild(voiceButton);
    });

    // Add global voice assistant button to the navbar
    const navbar = document.querySelector('.navbar-nav');
    if (navbar && !document.getElementById('voice-assistant-btn')) {
        const voiceAssistantItem = document.createElement('li');
        voiceAssistantItem.className = 'nav-item';

        const voiceAssistantButton = document.createElement('a');
        voiceAssistantButton.href = '#';
        voiceAssistantButton.className = 'nav-link';
        voiceAssistantButton.id = 'voice-assistant-btn';
        voiceAssistantButton.innerHTML = '<i class="fas fa-comment-alt"></i> Voice Assistant';

        voiceAssistantButton.addEventListener('click', (e) => {
            e.preventDefault();
            showVoiceAssistantModal();
        });

        voiceAssistantItem.appendChild(voiceAssistantButton);
        navbar.appendChild(voiceAssistantItem);
    }
}

/**
 * Show the voice assistant modal
 */
function showVoiceAssistantModal() {
    // Create the modal if it doesn't exist
    if (!document.getElementById('voice-assistant-modal')) {
        const modalHTML = `
            <div class="modal fade" id="voice-assistant-modal" tabindex="-1" aria-labelledby="voiceAssistantModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="voiceAssistantModalLabel">Voice Assistant</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div id="voice-conversation-container" class="mb-3" style="max-height: 300px; overflow-y: auto;">
                                <div class="assistant-message">
                                    <div class="message-content">
                                        How can I help you today?
                                    </div>
                                </div>
                            </div>
                            <div id="voice-loading-indicator" class="text-center mb-3 d-none">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p>Processing your request...</p>
                            </div>
                            <div class="input-group">
                                <input type="text" id="voice-assistant-input" class="form-control" placeholder="Type or speak your message...">
                                <button class="btn btn-primary voice-input-btn" type="button">
                                    <i class="fas fa-microphone"></i>
                                </button>
                                <button class="btn btn-primary" type="button" id="voice-assistant-send">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                            <div class="form-group mt-3">
                                <label for="voice-assistant-model" class="form-label">Model</label>
                                <select id="voice-assistant-model" class="form-select">
                                    <!-- Models will be populated dynamically -->
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add the modal to the body
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHTML;
        document.body.appendChild(modalContainer.firstElementChild);

        // Initialize the modal
        initializeVoiceAssistantModal();
    }

    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('voice-assistant-modal'));
    modal.show();
}

/**
 * Initialize the voice assistant modal
 */
function initializeVoiceAssistantModal() {
    const modal = document.getElementById('voice-assistant-modal');
    const input = document.getElementById('voice-assistant-input');
    const sendButton = document.getElementById('voice-assistant-send');
    const modelSelect = document.getElementById('voice-assistant-model');
    const voiceButton = modal.querySelector('.voice-input-btn');
    const conversationContainer = document.getElementById('voice-conversation-container');

    // Load available models
    fetch('/api/ollama/models')
        .then(response => response.json())
        .then(data => {
            if (data.models && data.models.length > 0) {
                // Clear existing options
                modelSelect.innerHTML = '';

                // Add models to the select
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = model.name;
                    modelSelect.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error loading models:', error));

    // Handle voice input button click
    voiceButton.addEventListener('click', () => {
        voiceInteraction.startListening(text => {
            input.value = text;
            processAssistantInput(text);
        });
    });

    // Handle send button click
    sendButton.addEventListener('click', () => {
        const text = input.value.trim();
        if (text) {
            processAssistantInput(text);
        }
    });

    // Handle enter key press
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const text = input.value.trim();
            if (text) {
                processAssistantInput(text);
            }
        }
    });

    // Process input and get response from the AI
    function processAssistantInput(text) {
        // Clear the input
        input.value = '';

        // Add user message to the conversation
        addMessageToConversation(text, 'user');

        // Get the selected model
        const model = modelSelect.value;

        // Process the input and get a response
        voiceInteraction.processVoiceInput(text, model, response => {
            // Add assistant message to the conversation
            addMessageToConversation(response, 'assistant');
        });
    }

    // Add a message to the conversation
    function addMessageToConversation(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = sender + '-message';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = text;

        messageDiv.appendChild(messageContent);
        conversationContainer.appendChild(messageDiv);

        // Scroll to the bottom
        conversationContainer.scrollTop = conversationContainer.scrollHeight;
    }
}

// Initialize voice interaction when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add voice interaction buttons to the page
    addVoiceInteractionButtons();

    // Re-add buttons when the DOM changes (for dynamically added elements)
    const observer = new MutationObserver(() => {
        addVoiceInteractionButtons();
    });

    observer.observe(document.body, { childList: true, subtree: true });
});
