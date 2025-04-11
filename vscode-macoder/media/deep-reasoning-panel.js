// @ts-check

(function() {
    // Get VS Code API
    const vscode = acquireVsCodeApi();
    
    // Elements
    let chainsView;
    let chainView;
    let chainsList;
    let newChainButton;
    let backToChainsButton;
    let addStepButton;
    let chainTitle;
    let chainDescription;
    let stepsList;
    let conclusionSection;
    let conclusionContent;
    let problemInput;
    let contextInput;
    let performReasoningButton;
    
    // State
    let chains = [];
    let activeChainId = null;
    
    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        // Get elements
        chainsView = document.getElementById('chainsView');
        chainView = document.getElementById('chainView');
        chainsList = document.getElementById('chainsList');
        newChainButton = document.getElementById('newChainButton');
        backToChainsButton = document.getElementById('backToChainsButton');
        addStepButton = document.getElementById('addStepButton');
        chainTitle = document.getElementById('chainTitle');
        chainDescription = document.getElementById('chainDescription');
        stepsList = document.getElementById('stepsList');
        conclusionSection = document.getElementById('conclusionSection');
        conclusionContent = document.getElementById('conclusionContent');
        problemInput = document.getElementById('problemInput');
        contextInput = document.getElementById('contextInput');
        performReasoningButton = document.getElementById('performReasoningButton');
        
        // Set up event listeners
        setupEventListeners();
        
        // Restore state
        const state = vscode.getState();
        if (state) {
            chains = state.chains || [];
            activeChainId = state.activeChainId || null;
        }
    });
    
    // Set up event listeners
    function setupEventListeners() {
        // Chain actions
        newChainButton.addEventListener('click', () => {
            createNewChain();
        });
        
        backToChainsButton.addEventListener('click', () => {
            showChains();
        });
        
        addStepButton.addEventListener('click', () => {
            addStep();
        });
        
        performReasoningButton.addEventListener('click', () => {
            performReasoning();
        });
    }
    
    // Handle messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.command) {
            case 'updateChainsList':
                chains = message.chains;
                renderChainsList();
                saveState();
                break;
            case 'updateChainView':
                renderChainView(message.chain);
                saveState();
                break;
        }
    });
    
    // Save state
    function saveState() {
        vscode.setState({
            chains,
            activeChainId
        });
    }
    
    // Show chains view
    function showChains() {
        chainsView.classList.remove('hidden');
        chainView.classList.add('hidden');
        
        vscode.postMessage({
            command: 'showChains'
        });
    }
    
    // Create a new chain
    function createNewChain() {
        // Show input dialog
        const topicInput = document.createElement('input');
        topicInput.type = 'text';
        topicInput.placeholder = 'Chain Topic';
        
        const descriptionInput = document.createElement('textarea');
        descriptionInput.placeholder = 'Chain Description';
        
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h2>Create New Reasoning Chain</h2>
                <div class="dialog-form">
                    <div class="form-group">
                        <label for="topic">Topic:</label>
                        <div id="topicContainer"></div>
                    </div>
                    <div class="form-group">
                        <label for="description">Description:</label>
                        <div id="descriptionContainer"></div>
                    </div>
                </div>
                <div class="dialog-buttons">
                    <button id="cancelButton" class="secondary-button">Cancel</button>
                    <button id="createButton" class="primary-button">Create</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        document.getElementById('topicContainer').appendChild(topicInput);
        document.getElementById('descriptionContainer').appendChild(descriptionInput);
        
        const cancelButton = document.getElementById('cancelButton');
        const createButton = document.getElementById('createButton');
        
        cancelButton.addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
        
        createButton.addEventListener('click', () => {
            const topic = topicInput.value.trim();
            const description = descriptionInput.value.trim();
            
            if (!topic) {
                alert('Please enter a topic');
                return;
            }
            
            vscode.postMessage({
                command: 'createChain',
                topic,
                description
            });
            
            document.body.removeChild(dialog);
        });
    }
    
    // Render chains list
    function renderChainsList() {
        if (chains.length === 0) {
            chainsList.innerHTML = '<div class="empty-state">No reasoning chains yet</div>';
            return;
        }
        
        chainsList.innerHTML = '';
        
        for (const chain of chains) {
            const chainElement = document.createElement('div');
            chainElement.className = 'chain-item';
            chainElement.innerHTML = `
                <div class="chain-item-header">
                    <h3>${chain.topic}</h3>
                    <div class="chain-item-actions">
                        <button class="delete-button">Delete</button>
                    </div>
                </div>
                <div class="chain-item-description">${chain.description}</div>
                <div class="chain-item-meta">
                    <span>${formatDate(chain.createdAt)}</span>
                    <span>${chain.steps.length} steps</span>
                </div>
            `;
            
            chainElement.addEventListener('click', event => {
                if (!event.target.classList.contains('delete-button')) {
                    openChain(chain.id);
                }
            });
            
            const deleteButton = chainElement.querySelector('.delete-button');
            deleteButton.addEventListener('click', event => {
                event.stopPropagation();
                deleteChain(chain.id);
            });
            
            chainsList.appendChild(chainElement);
        }
    }
    
    // Open a chain
    function openChain(chainId) {
        activeChainId = chainId;
        
        vscode.postMessage({
            command: 'openChain',
            chainId
        });
    }
    
    // Delete a chain
    function deleteChain(chainId) {
        if (confirm('Are you sure you want to delete this reasoning chain?')) {
            vscode.postMessage({
                command: 'deleteChain',
                chainId
            });
        }
    }
    
    // Render chain view
    function renderChainView(chain) {
        activeChainId = chain.id;
        
        chainsView.classList.add('hidden');
        chainView.classList.remove('hidden');
        
        chainTitle.textContent = chain.topic;
        chainDescription.textContent = chain.description;
        
        renderStepsList(chain.steps);
        
        // Show conclusion if available
        if (chain.conclusion) {
            conclusionSection.classList.remove('hidden');
            conclusionContent.textContent = chain.conclusion;
        } else {
            conclusionSection.classList.add('hidden');
        }
    }
    
    // Render steps list
    function renderStepsList(steps) {
        if (steps.length === 0) {
            stepsList.innerHTML = '<div class="empty-state">No steps yet</div>';
            return;
        }
        
        stepsList.innerHTML = '';
        
        for (const step of steps) {
            const stepElement = document.createElement('div');
            stepElement.className = `step-item ${step.type}`;
            stepElement.dataset.id = step.id;
            
            stepElement.innerHTML = `
                <div class="step-item-header">
                    <div class="step-item-type">${formatStepType(step.type)}</div>
                    <div class="step-item-time">${formatDate(step.createdAt)}</div>
                </div>
                <div class="step-item-content">${step.content}</div>
            `;
            
            stepsList.appendChild(stepElement);
        }
    }
    
    // Add a step
    function addStep() {
        if (!activeChainId) {
            return;
        }
        
        // Show input dialog
        const contentInput = document.createElement('textarea');
        contentInput.placeholder = 'Step Content';
        
        const typeSelect = document.createElement('select');
        typeSelect.innerHTML = `
            <option value="observation">Observation</option>
            <option value="thought">Thought</option>
            <option value="action">Action</option>
            <option value="conclusion">Conclusion</option>
        `;
        
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h2>Add Step</h2>
                <div class="dialog-form">
                    <div class="form-group">
                        <label for="content">Content:</label>
                        <div id="contentContainer"></div>
                    </div>
                    <div class="form-group">
                        <label for="type">Type:</label>
                        <div id="typeContainer"></div>
                    </div>
                </div>
                <div class="dialog-buttons">
                    <button id="cancelButton" class="secondary-button">Cancel</button>
                    <button id="addButton" class="primary-button">Add</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        document.getElementById('contentContainer').appendChild(contentInput);
        document.getElementById('typeContainer').appendChild(typeSelect);
        
        const cancelButton = document.getElementById('cancelButton');
        const addButton = document.getElementById('addButton');
        
        cancelButton.addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
        
        addButton.addEventListener('click', () => {
            const content = contentInput.value.trim();
            const type = typeSelect.value;
            
            if (!content) {
                alert('Please enter content');
                return;
            }
            
            vscode.postMessage({
                command: 'addStep',
                chainId: activeChainId,
                content,
                type
            });
            
            document.body.removeChild(dialog);
        });
    }
    
    // Perform reasoning
    function performReasoning() {
        const problem = problemInput.value.trim();
        const context = contextInput.value.trim();
        
        if (!problem) {
            alert('Please enter a problem');
            return;
        }
        
        vscode.postMessage({
            command: 'performReasoning',
            problem,
            context
        });
        
        // Clear inputs
        problemInput.value = '';
        contextInput.value = '';
    }
    
    // Format step type
    function formatStepType(type) {
        switch (type) {
            case 'observation':
                return 'Observation';
            case 'thought':
                return 'Thought';
            case 'action':
                return 'Action';
            case 'conclusion':
                return 'Conclusion';
            default:
                return type;
        }
    }
    
    // Format date
    function formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
})();
