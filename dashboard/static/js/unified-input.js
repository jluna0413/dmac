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
        this.currentSearchEngine = 'duckduckgo'; // Default search engine
        this.isThinking = false;
        this.isResearching = false;
        this.isListening = false;
        this.uploadedFiles = [];

        // Hot word triggers
        this.researchHotWords = [
            'search', 'look up', 'find', 'google', 'web', 'internet',
            'current', 'latest', 'recent', 'now', 'today', 'what is the',
            'research', 'browse', 'online', 'information'
        ];

        this.thinkingHotWords = [
            'think', 'ponder', 'analyze', 'consider', 'reflect', 'contemplate',
            'deep dive', 'deep thinking', 'deep analysis', 'carefully', 'thoroughly'
        ];

        this.deepResearchHotWords = [
            'research', 'brainstorm', 'investigate', 'explore', 'study',
            'deep research', 'comprehensive', 'extensive', 'in-depth', 'detailed'
        ];

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
        // Find the input container that's already in the DOM
        this.inputContainer = document.getElementById('input-container');

        // Find the chat container that's already in the DOM
        this.chatContainer = document.getElementById('chat-container');

        // Find the model selector container in the sidebar
        this.modelSelectorContainer = document.getElementById('model-selector-container');

        // Set up sidebar button handlers
        this.setupSidebarButtons();

        // Set up the input container HTML
        this.inputContainer.innerHTML = `
            <div class="tools-container">
                <div class="tools-row">
                    <button id="sidebar-research-button" class="tool-button">
                        <i class="fas fa-search"></i> Web Search
                    </button>
                    <button id="sidebar-think-button" class="tool-button">
                        <i class="fas fa-brain"></i> Deep Thinking
                    </button>
                    <button id="sidebar-opencanvas-button" class="tool-button">
                        <i class="fas fa-project-diagram"></i> Open Canvas
                    </button>
                </div>
            </div>
            <div class="input-group">
                <button id="voice-button" class="btn input-group-prepend" title="Voice Input">
                    <i class="fas fa-microphone"></i>
                </button>
                <textarea id="user-input" class="form-control" placeholder="Message DMac..." rows="1"></textarea>
                <div class="input-group-append d-flex">
                    <button id="upload-button" class="tool-pill" title="Upload Files">
                        <i class="fas fa-upload"></i> Files
                    </button>
                    <button id="send-button" class="btn">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
                <input type="file" id="file-upload" multiple style="display: none;">
            </div>
            <div id="uploaded-files-container" class="uploaded-files-container" style="display: none;">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <h6 class="mb-0">Uploaded Files</h6>
                    <button id="clear-files-button" class="btn btn-sm btn-outline-danger">
                        <i class="fas fa-trash"></i> Clear All
                    </button>
                </div>
                <div id="uploaded-files-list" class="uploaded-files-list"></div>
            </div>
            <div id="thinking-indicator" class="thinking-indicator" style="display: none;">
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
     * Set up sidebar buttons and tool buttons
     */
    setupSidebarButtons() {
        // Set up model selection from the dropdown menu
        this.setupModelSelectors();

        // Set up Ollama models list
        this.loadOllamaModels();

        // Set up model item click handlers
        this.setupModelItemClickHandlers();

        // Set up tool buttons
        this.setupToolButtons();
    }

    /**
     * Set up model selectors
     */
    setupModelSelectors() {
        // Create model selector in the sidebar (legacy - will be hidden but kept for compatibility)
        if (this.modelSelectorContainer) {
            this.modelSelectorContainer.innerHTML = `
                <select id="model-selector" class="form-select form-select-sm w-100" style="display: none;">
                    <option value="" disabled>Select a model</option>
                </select>
            `;
        }

        // Set up dropdown handlers after a short delay to ensure DOM is ready
        setTimeout(() => {
            this.setupDropdownHandlers();
        }, 500);
    }

    /**
     * Set up dropdown handlers
     */
    setupDropdownHandlers() {
        console.log('Setting up dropdown handlers');

        // Set up provider dropdown click handlers
        document.querySelectorAll('.provider-item').forEach(item => {
            console.log('Found provider item:', item.dataset.provider);
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const provider = item.dataset.provider;
                console.log('Provider clicked:', provider);
                this.selectProvider(provider, item.textContent.trim());
            });
        });

        // Set up model dropdown click handlers
        document.querySelectorAll('.dropdown-item.model-item').forEach(item => {
            if (item.dataset.model && !item.classList.contains('loading')) {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    const modelId = item.dataset.model;
                    const modelName = item.textContent.trim();
                    this.selectModel(modelId, modelName);
                });
            }
        });
    }

    /**
     * Select a provider
     */
    selectProvider(provider, providerName) {
        // Update the selected provider display
        const selectedProvider = document.getElementById('selected-provider');
        if (selectedProvider) {
            selectedProvider.textContent = providerName;
        }

        // Hide all model lists
        document.querySelectorAll('.model-list').forEach(list => {
            list.style.display = 'none';
        });

        // Show the selected provider's models
        const modelList = document.getElementById(`${provider}-models`);
        if (modelList) {
            modelList.style.display = 'block';

            // If it's Ollama, load the models
            if (provider === 'ollama') {
                this.loadOllamaModels();
            }
        }

        // Update the model dropdown text
        const selectedModel = document.getElementById('selected-model');
        if (selectedModel) {
            selectedModel.textContent = `Select ${providerName} Model`;
        }
    }

    /**
     * Load Ollama models
     */
    loadOllamaModels() {
        const ollamaModelsList = document.getElementById('ollama-models-list');
        if (!ollamaModelsList) {
            console.error('Ollama models list element not found');
            return;
        }

        console.log('Loading Ollama models...');

        // Show loading indicator
        ollamaModelsList.innerHTML = `<li><a class="dropdown-item model-item loading" href="#">Loading models...</a></li>`;

        // Fetch Ollama models
        fetch('/api/ollama/models')
            .then(response => response.json())
            .then(data => {
                console.log('Ollama models response:', data);

                if (data.models && data.models.length > 0) {
                    // Clear loading indicator
                    ollamaModelsList.innerHTML = '';

                    // Add models to the list
                    data.models.forEach(model => {
                        if (!model.name) return; // Skip models without names

                        const li = document.createElement('li');
                        const modelItem = document.createElement('a');
                        modelItem.className = 'dropdown-item model-item';
                        modelItem.href = '#';
                        modelItem.dataset.model = model.id || model.name;
                        modelItem.textContent = model.name;

                        // Add click handler using bind to preserve 'this' context
                        const self = this;
                        modelItem.onclick = function (e) {
                            e.preventDefault();
                            e.stopPropagation();
                            console.log('Model clicked:', model.name);
                            self.selectModel(model.id || model.name, model.name);

                            // Close the dropdown manually
                            const dropdown = document.getElementById('modelSelectionDropdown');
                            if (dropdown) {
                                const bsDropdown = bootstrap.Dropdown.getInstance(dropdown);
                                if (bsDropdown) {
                                    bsDropdown.hide();
                                }
                            }
                        };

                        li.appendChild(modelItem);
                        ollamaModelsList.appendChild(li);

                        console.log('Added model to list:', model.name);
                    });
                } else {
                    ollamaModelsList.innerHTML = `<li><a class="dropdown-item model-item disabled" href="#">No models found</a></li>`;
                    console.warn('No Ollama models found');
                }
            })
            .catch(error => {
                console.error('Error loading Ollama models:', error);
                ollamaModelsList.innerHTML = `<li><a class="dropdown-item model-item disabled" href="#">Error loading models</a></li>`;
            });
    }

    /**
     * Set up model item click handlers
     */
    setupModelItemClickHandlers() {
        // This is now handled in setupModelSelectors
    }

    /**
     * Select a model
     */
    selectModel(modelId, modelName) {
        // Update the current model display
        const currentModelDisplay = document.getElementById('current-model-display');
        if (currentModelDisplay) {
            currentModelDisplay.textContent = modelName;
        }

        // Update the selected model dropdown text
        const selectedModel = document.getElementById('selected-model');
        if (selectedModel) {
            selectedModel.textContent = modelName;
        }

        // Update the model selector (legacy)
        const modelSelector = document.getElementById('model-selector');
        if (modelSelector) {
            // Check if the option exists, if not add it
            let option = Array.from(modelSelector.options).find(opt => opt.value === modelId);
            if (!option) {
                option = new Option(modelName, modelId);
                modelSelector.add(option);
            }
            modelSelector.value = modelId;
        }

        // Remove active class from all model items
        document.querySelectorAll('.dropdown-item.model-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to the clicked model item
        const selectedItem = document.querySelector(`.dropdown-item.model-item[data-model="${modelId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }

        // Show toast notification
        this.showToast('Model Selected', `Selected model: ${modelName}`);

        // Show model info content and hide placeholder
        const modelInfoPlaceholder = document.getElementById('model-info-placeholder');
        const modelInfoContent = document.getElementById('model-info-content');
        if (modelInfoPlaceholder && modelInfoContent) {
            modelInfoPlaceholder.style.display = 'none';
            modelInfoContent.style.display = 'block';
        }

        // Update capabilities based on the selected model
        this.updateModelCapabilities(modelId);
    }

    /**
     * Update model capabilities based on the selected model
     */
    updateModelCapabilities(modelId) {
        // This is a placeholder - in a real implementation, you would fetch the model's capabilities
        // and update the UI accordingly

        // For now, we'll just simulate different capabilities for different providers
        const isGemini = modelId.startsWith('gemini');
        const isGPT4 = modelId.includes('gpt-4');
        const isOllama = !modelId.includes('-') || modelId.includes('ollama');
        const isDeepSeek = modelId.includes('deepseek');

        // Update vision capability
        const visionCapability = document.querySelector('.model-capability-item:nth-child(3) .capability-badge');
        if (visionCapability) {
            if (isGemini || isGPT4) {
                visionCapability.className = 'capability-badge available';
                visionCapability.innerHTML = '<i class="fas fa-check"></i>';
            } else {
                visionCapability.className = 'capability-badge unavailable';
                visionCapability.innerHTML = '<i class="fas fa-times"></i>';
            }
        }

        // Update model details
        const typeValue = document.querySelector('.model-detail-item:nth-child(1) .detail-value');
        const paramsValue = document.querySelector('.model-detail-item:nth-child(2) .detail-value');
        const contextValue = document.querySelector('.model-detail-item:nth-child(3) .detail-value');
        const providerValue = document.querySelector('.model-detail-item:nth-child(4) .detail-value');

        if (typeValue) {
            if (isDeepSeek && modelId.includes('coder')) {
                typeValue.textContent = 'Code Generation Model';
            } else if (modelId.includes('gemma') || modelId.includes('llama')) {
                typeValue.textContent = 'Open Source LLM';
            } else {
                typeValue.textContent = 'Large Language Model';
            }
        }

        if (paramsValue) {
            if (isGPT4 && modelId.includes('o')) {
                paramsValue.textContent = '1.8 trillion';
            } else if (isGPT4) {
                paramsValue.textContent = '1.5 trillion';
            } else if (isGemini && modelId.includes('pro')) {
                paramsValue.textContent = '1 trillion';
            } else if (modelId.includes('gemma3:12b')) {
                paramsValue.textContent = '12 billion';
            } else if (modelId.includes('gemma3:8b') || modelId.includes('gemma:7b')) {
                paramsValue.textContent = '8 billion';
            } else if (modelId.includes('llama3:8b')) {
                paramsValue.textContent = '8 billion';
            } else if (modelId.includes('mistral')) {
                paramsValue.textContent = '7 billion';
            } else if (isOllama && !modelId.includes('gemma') && !modelId.includes('llama')) {
                paramsValue.textContent = 'Varies';
            } else {
                paramsValue.textContent = 'Unknown';
            }
        }

        if (contextValue) {
            if (isGPT4 || (isGemini && modelId.includes('pro'))) {
                contextValue.textContent = '128K tokens';
            } else if (modelId.includes('gemma3:12b')) {
                contextValue.textContent = '32K tokens';
            } else if (modelId.includes('llama3')) {
                contextValue.textContent = '16K tokens';
            } else if (isOllama) {
                contextValue.textContent = '8K tokens';
            } else {
                contextValue.textContent = '4K tokens';
            }
        }

        if (providerValue) {
            if (isGemini) {
                providerValue.textContent = 'Google';
            } else if (isGPT4 || modelId.includes('gpt')) {
                providerValue.textContent = 'OpenAI';
            } else if (isDeepSeek) {
                providerValue.textContent = 'DeepSeek';
            } else if (modelId.includes('hf-')) {
                providerValue.textContent = 'HuggingFace';
            } else if (modelId.includes('openrouter')) {
                providerValue.textContent = 'OpenRouter';
            } else if (isOllama) {
                providerValue.textContent = 'Ollama';
            } else if (modelId.includes('lmstudio')) {
                providerValue.textContent = 'LM Studio';
            } else {
                providerValue.textContent = 'Unknown';
            }
        }
    }

    /**
     * Set up tool buttons
     */
    setupToolButtons() {
        // Set up tool buttons above input
        const sidebarResearchButton = document.getElementById('sidebar-research-button');
        if (sidebarResearchButton) {
            sidebarResearchButton.addEventListener('click', () => {
                this.toggleResearchMode(true);
                this.updateToolButtonState(sidebarResearchButton, this.isResearching);
            });
        }

        const sidebarThinkButton = document.getElementById('sidebar-think-button');
        if (sidebarThinkButton) {
            sidebarThinkButton.addEventListener('click', () => {
                this.toggleThinkingMode(true);
                this.updateToolButtonState(sidebarThinkButton, this.isThinking);
            });
        }

        const sidebarOpenCanvasButton = document.getElementById('sidebar-opencanvas-button');
        if (sidebarOpenCanvasButton) {
            sidebarOpenCanvasButton.addEventListener('click', () => this.openCanvas());
        }

        // Set up research button in input area
        const researchButton = document.getElementById('research-button');
        if (researchButton) {
            researchButton.addEventListener('click', () => {
                this.toggleResearchMode(true);
                this.updateToolButtonState(sidebarResearchButton, this.isResearching);
            });
        }

        // Set up think button in input area
        const thinkButton = document.getElementById('think-button');
        if (thinkButton) {
            thinkButton.addEventListener('click', () => {
                this.toggleThinkingMode(true);
                this.updateToolButtonState(sidebarThinkButton, this.isThinking);
            });
        }

        // Set up new chat button
        const newChatButton = document.getElementById('new-chat-button');
        if (newChatButton) {
            newChatButton.addEventListener('click', () => this.startNewChat());
        }

        // Set up clear history button
        const clearHistoryButton = document.getElementById('clear-history-button');
        if (clearHistoryButton) {
            clearHistoryButton.addEventListener('click', () => this.clearChatHistory());
        }
    }

    /**
     * Update tool button state
     */
    updateToolButtonState(button, isActive) {
        if (button) {
            if (isActive) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        }
    }

    /**
     * Start a new chat
     */
    startNewChat() {
        // Clear the chat container
        this.chatContainer.innerHTML = `
            <div class="message assistant-message">
                <div class="message-content">
                    <h4>Welcome to DMac AI Assistant</h4>
                    <p>I'm here to help you with your tasks. How can I assist you today?</p>
                </div>
            </div>
        `;

        // Clear uploaded files
        this.clearUploadedFiles();

        // Reset modes
        this.isThinking = false;
        this.isResearching = false;

        // Update chat history
        this.updateChatHistory('New Chat', 'Welcome to DMac AI Assistant...', true);
    }

    /**
     * Clear chat history
     */
    clearChatHistory() {
        // Clear the chat history list
        const chatHistoryList = document.getElementById('chat-history-list');
        if (chatHistoryList) {
            chatHistoryList.innerHTML = `
                <div class="chat-history-item active">
                    <div class="chat-title">Current Chat</div>
                    <div class="chat-preview">Welcome to DMac AI Assistant...</div>
                </div>
            `;
        }

        // Start a new chat
        this.startNewChat();
    }

    /**
     * Update chat history
     */
    updateChatHistory(title, preview, isActive = false) {
        const chatHistoryList = document.getElementById('chat-history-list');
        if (!chatHistoryList) return;

        // Remove active class from all items
        if (isActive) {
            const activeItems = chatHistoryList.querySelectorAll('.chat-history-item.active');
            activeItems.forEach(item => item.classList.remove('active'));
        }

        // Create new history item
        const historyItem = document.createElement('div');
        historyItem.className = `chat-history-item${isActive ? ' active' : ''}`;
        historyItem.innerHTML = `
            <div class="chat-title">${title}</div>
            <div class="chat-preview">${preview}</div>
        `;

        // Add click event to load this chat
        historyItem.addEventListener('click', () => {
            // In a real app, this would load the chat from storage
            const activeItems = chatHistoryList.querySelectorAll('.chat-history-item.active');
            activeItems.forEach(item => item.classList.remove('active'));
            historyItem.classList.add('active');
        });

        // Add to the list
        if (isActive) {
            chatHistoryList.prepend(historyItem);
        } else {
            chatHistoryList.appendChild(historyItem);
        }
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
        researchButton.addEventListener('click', () => this.toggleResearchMode(true));

        // Search engine options
        const searchEngineOptions = document.querySelectorAll('.search-engine');
        searchEngineOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const engine = e.target.closest('.search-engine').getAttribute('data-engine');
                this.setSearchEngine(engine);
            });
        });

        // Clear search cache
        const clearSearchCache = document.getElementById('clear-search-cache');
        clearSearchCache.addEventListener('click', (e) => {
            e.preventDefault();
            this.clearSearchCache();
        });

        // Think button
        const thinkButton = document.getElementById('think-button');
        thinkButton.addEventListener('click', () => this.toggleThinkingMode(true));

        // OpenCanvas button
        const openCanvasButton = document.getElementById('opencanvas-button');
        openCanvasButton.addEventListener('click', () => this.openCanvas());

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
                background-color: var(--gemini-surface);
                padding: 16px 24px;
                border-top: 1px solid var(--gemini-gray-200);
                z-index: 100;
                max-height: 160px;
                overflow-y: auto;
                font-family: var(--gemini-font);
            }

            .chat-container {
                margin-bottom: 160px;
                padding: 16px 24px;
                overflow-y: auto;
                height: calc(100vh - 160px);
                scroll-behavior: smooth;
                background-color: var(--gemini-background);
                font-family: var(--gemini-font);
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

            .web-search-note {
                text-align: center;
                margin-bottom: 15px;
                color: var(--bs-secondary);
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

        // Add a global function to manually select a provider (for testing)
        window.selectProvider = (provider) => {
            console.log('Manual provider selection:', provider);
            this.selectProvider(provider, provider.charAt(0).toUpperCase() + provider.slice(1));
        };
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

        // Check for hot words and activate appropriate modes
        this.detectAndActivateHotWords(message);

        // Clear the input
        userInput.value = '';

        // Add the message to the chat
        this.addMessageToChat(message, 'user');

        // Update chat history with the first few words of the message
        const previewText = message.length > 30 ? message.substring(0, 30) + '...' : message;
        this.updateChatHistory(previewText, 'You: ' + previewText, true);

        // Prepare the request data
        const requestData = {
            message: message,
            model: this.currentModel,
            files: this.uploadedFiles,
            deep_research: this.isResearching,
            deep_thinking: this.isThinking,
            // Add search engine if research mode is active
            search_engine: this.isResearching ? this.currentSearchEngine : null,
            // Add anti-hallucination instructions
            instructions: {
                prevent_hallucinations: true,
                admit_uncertainty: true,
                verify_facts: true,
                use_web_search: this.isResearching
            }
        };

        // Show thinking indicator
        this.addThinkingIndicator();

        // Send the request to the API
        fetch('/api/chat', {
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

                // Add the response to the chat
                if (data.response) {
                    this.addMessageToChat(data.response, 'assistant');

                    // Show if web search was used
                    if (data.used_web_search) {
                        const webSearchNote = document.createElement('div');
                        webSearchNote.className = 'web-search-note';

                        // Show which search engine was used
                        const engineName = data.search_engine === 'google' ? 'Google' : 'DuckDuckGo';
                        const searchQuery = data.search_query ? `for "${data.search_query}"` : '';

                        webSearchNote.innerHTML = `<small><i class="fas fa-search"></i> ${engineName} search was used ${searchQuery} to provide up-to-date information</small>`;
                        this.chatContainer.appendChild(webSearchNote);
                    }

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

        // Add feedback UI for assistant messages
        if (sender === 'assistant' && window.feedbackSystem) {
            const messageId = `msg-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
            window.feedbackSystem.addFeedbackUI(messageDiv, messageId);
        }

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
            thinkingText = 'Researching the web for up-to-date information';
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
     *
     * @param {boolean} showToast - Whether to show a toast notification (default: false)
     */
    toggleResearchMode(showToast = false) {
        const researchButton = document.getElementById('research-button');
        const sidebarResearchButton = document.getElementById('sidebar-research-button');

        this.isResearching = !this.isResearching;

        if (this.isResearching) {
            // Update button states
            if (researchButton) researchButton.classList.add('active');
            if (sidebarResearchButton) sidebarResearchButton.classList.add('active');

            // If thinking mode is on, turn it off
            if (this.isThinking) {
                this.toggleThinkingMode(false);
            }

            // Show indicator with current search engine
            const engineName = this.currentSearchEngine === 'google' ? 'Google' : 'DuckDuckGo';
            document.getElementById('thinking-indicator').style.display = 'block';
            document.getElementById('thinking-text').textContent = `Web search mode activated - Using ${engineName} to find up-to-date information`;

            // Show toast if requested
            if (showToast) {
                this.showToast('Web Search', `Web search mode activated using ${engineName}`);
            }
        } else {
            // Update button states
            if (researchButton) researchButton.classList.remove('active');
            if (sidebarResearchButton) sidebarResearchButton.classList.remove('active');

            // Hide indicator
            document.getElementById('thinking-indicator').style.display = 'none';

            // Show toast if requested
            if (showToast) {
                this.showToast('Web Search', 'Web search mode deactivated');
            }
        }
    }

    /**
     * Set the search engine to use
     *
     * @param {string} engine - The search engine to use
     */
    setSearchEngine(engine) {
        this.currentSearchEngine = engine;

        // Update UI to show selected engine
        const engineName = engine === 'google' ? 'Google' : 'DuckDuckGo';
        const researchButton = document.getElementById('research-button');
        researchButton.title = `Research using ${engineName}`;

        // If research mode is active, update the indicator
        if (this.isResearching) {
            document.getElementById('thinking-text').textContent = `Web search mode activated - Using ${engineName} to find up-to-date information`;
        }

        // Show toast notification
        this.showToast('Search Engine', `Set search engine to ${engineName}`);
    }

    /**
     * Clear the search cache
     */
    clearSearchCache() {
        fetch('/api/web-search/clear-cache', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showToast('Cache Cleared', 'Search cache has been cleared successfully');
                } else {
                    this.showToast('Error', data.error || 'Failed to clear search cache');
                }
            })
            .catch(error => {
                console.error('Error clearing search cache:', error);
                this.showToast('Error', 'Failed to clear search cache');
            });
    }

    /**
     * Detect hot words in the message and activate appropriate modes
     *
     * @param {string} message - The user's message
     */
    detectAndActivateHotWords(message) {
        if (!message) return;

        const messageLower = message.toLowerCase();
        let modeActivated = false;

        // Check for research hot words
        if (!modeActivated && this.containsAnyHotWord(messageLower, this.researchHotWords)) {
            // If not already in research mode, activate it
            if (!this.isResearching) {
                this.toggleResearchMode(false);
                this.showToast('Web Search', 'Web search mode activated based on your message');
            }
            modeActivated = true;
        }

        // Check for thinking hot words
        if (!modeActivated && this.containsAnyHotWord(messageLower, this.thinkingHotWords)) {
            // If not already in thinking mode, activate it
            if (!this.isThinking) {
                this.toggleThinkingMode(false);
                this.showToast('Deep Thinking', 'Deep thinking mode activated based on your message');
            }
            modeActivated = true;
        }

        // Check for deep research hot words
        if (!modeActivated && this.containsAnyHotWord(messageLower, this.deepResearchHotWords)) {
            // For now, deep research is a combination of research and thinking
            if (!this.isResearching) {
                this.toggleResearchMode(false);
            }
            if (!this.isThinking) {
                this.toggleThinkingMode(false);
            }
            this.showToast('Deep Research', 'Deep research mode activated based on your message');
            modeActivated = true;
        }
    }

    /**
     * Check if a message contains any of the hot words
     *
     * @param {string} message - The user's message (lowercase)
     * @param {string[]} hotWords - Array of hot words to check for
     * @returns {boolean} - True if the message contains any of the hot words
     */
    containsAnyHotWord(message, hotWords) {
        return hotWords.some(word => message.includes(word));
    }

    /**
     * Toggle thinking mode
     *
     * @param {boolean} showToast - Whether to show a toast notification (default: false)
     */
    toggleThinkingMode(showToast = false) {
        const thinkButton = document.getElementById('think-button');
        const sidebarThinkButton = document.getElementById('sidebar-think-button');

        this.isThinking = !this.isThinking;

        if (this.isThinking) {
            // Update button states
            if (thinkButton) thinkButton.classList.add('active');
            if (sidebarThinkButton) sidebarThinkButton.classList.add('active');

            // If research mode is on, turn it off
            if (this.isResearching) {
                this.toggleResearchMode(false);
            }

            // Show indicator
            document.getElementById('thinking-indicator').style.display = 'block';
            document.getElementById('thinking-text').textContent = 'Deep thinking mode activated...';

            // Show toast if requested
            if (showToast) {
                this.showToast('Deep Thinking', 'Deep thinking mode activated');
            }
        } else {
            // Update button states
            if (thinkButton) thinkButton.classList.remove('active');
            if (sidebarThinkButton) sidebarThinkButton.classList.remove('active');

            // Hide indicator
            document.getElementById('thinking-indicator').style.display = 'none';

            // Show toast if requested
            if (showToast) {
                this.showToast('Deep Thinking', 'Deep thinking mode deactivated');
            }
        }
    }

    /**
     * Open the Langchain OpenCanvas interface
     */
    openCanvas() {
        const openCanvasButton = document.getElementById('opencanvas-button');

        // Toggle active state for visual feedback
        openCanvasButton.classList.add('active');
        setTimeout(() => {
            openCanvasButton.classList.remove('active');
        }, 300);

        // Show a message in the chat
        this.addMessageToChat('Opening Langchain OpenCanvas interface...', 'system');

        // Make an API call to open the OpenCanvas interface
        fetch('/api/opencanvas/open', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_conversation: this.getConversationHistory()
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // If successful, open the URL in a new tab/window
                    if (data.url) {
                        window.open(data.url, '_blank');
                    }
                } else {
                    // Show error message
                    this.addMessageToChat('Error opening OpenCanvas: ' + (data.error || 'Unknown error'), 'system');
                }
            })
            .catch(error => {
                console.error('Error opening OpenCanvas:', error);
                this.addMessageToChat('Error opening OpenCanvas. Please try again later.', 'system');
            });
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

    /**
     * Get the current conversation history
     * @returns {Array} Array of message objects
     */
    getConversationHistory() {
        const messages = [];
        const messageElements = this.chatContainer.querySelectorAll('.message');

        messageElements.forEach(element => {
            let role = 'user';
            if (element.classList.contains('assistant-message')) {
                role = 'assistant';
            } else if (element.classList.contains('system-message')) {
                role = 'system';
            }

            const content = element.querySelector('.message-content').textContent.trim();
            messages.push({
                role: role,
                content: content
            });
        });

        return messages;
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
