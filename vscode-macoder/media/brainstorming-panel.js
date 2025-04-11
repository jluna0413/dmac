// @ts-check

(function() {
    // Get VS Code API
    const vscode = acquireVsCodeApi();
    
    // Elements
    let sessionsTab;
    let roadmapsTab;
    let sessionsView;
    let sessionView;
    let roadmapsView;
    let roadmapView;
    let sessionsList;
    let roadmapsList;
    let newSessionButton;
    let backToSessionsButton;
    let backToRoadmapsButton;
    let generateIdeasButton;
    let createRoadmapButton;
    let addIdeaButton;
    let sessionTitle;
    let sessionDescription;
    let ideasList;
    let roadmapTitle;
    let roadmapDescription;
    let itemsList;
    
    // State
    let sessions = [];
    let roadmaps = [];
    let activeSessionId = null;
    let activeRoadmapId = null;
    
    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        // Get elements
        sessionsTab = document.getElementById('sessionsTab');
        roadmapsTab = document.getElementById('roadmapsTab');
        sessionsView = document.getElementById('sessionsView');
        sessionView = document.getElementById('sessionView');
        roadmapsView = document.getElementById('roadmapsView');
        roadmapView = document.getElementById('roadmapView');
        sessionsList = document.getElementById('sessionsList');
        roadmapsList = document.getElementById('roadmapsList');
        newSessionButton = document.getElementById('newSessionButton');
        backToSessionsButton = document.getElementById('backToSessionsButton');
        backToRoadmapsButton = document.getElementById('backToRoadmapsButton');
        generateIdeasButton = document.getElementById('generateIdeasButton');
        createRoadmapButton = document.getElementById('createRoadmapButton');
        addIdeaButton = document.getElementById('addIdeaButton');
        sessionTitle = document.getElementById('sessionTitle');
        sessionDescription = document.getElementById('sessionDescription');
        ideasList = document.getElementById('ideasList');
        roadmapTitle = document.getElementById('roadmapTitle');
        roadmapDescription = document.getElementById('roadmapDescription');
        itemsList = document.getElementById('itemsList');
        
        // Set up event listeners
        setupEventListeners();
        
        // Restore state
        const state = vscode.getState();
        if (state) {
            sessions = state.sessions || [];
            roadmaps = state.roadmaps || [];
            activeSessionId = state.activeSessionId || null;
            activeRoadmapId = state.activeRoadmapId || null;
        }
    });
    
    // Set up event listeners
    function setupEventListeners() {
        // Tab navigation
        sessionsTab.addEventListener('click', () => {
            showSessions();
        });
        
        roadmapsTab.addEventListener('click', () => {
            showRoadmaps();
        });
        
        // Session actions
        newSessionButton.addEventListener('click', () => {
            createNewSession();
        });
        
        backToSessionsButton.addEventListener('click', () => {
            showSessions();
        });
        
        generateIdeasButton.addEventListener('click', () => {
            generateIdeas();
        });
        
        createRoadmapButton.addEventListener('click', () => {
            createRoadmap();
        });
        
        addIdeaButton.addEventListener('click', () => {
            addIdea();
        });
        
        // Roadmap actions
        backToRoadmapsButton.addEventListener('click', () => {
            showRoadmaps();
        });
    }
    
    // Handle messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.command) {
            case 'updateSessionsList':
                sessions = message.sessions;
                renderSessionsList();
                saveState();
                break;
            case 'updateSessionView':
                renderSessionView(message.session);
                saveState();
                break;
            case 'updateRoadmapsList':
                roadmaps = message.roadmaps;
                renderRoadmapsList();
                saveState();
                break;
            case 'updateRoadmapView':
                renderRoadmapView(message.roadmap);
                saveState();
                break;
        }
    });
    
    // Save state
    function saveState() {
        vscode.setState({
            sessions,
            roadmaps,
            activeSessionId,
            activeRoadmapId
        });
    }
    
    // Show sessions view
    function showSessions() {
        sessionsTab.classList.add('active');
        roadmapsTab.classList.remove('active');
        
        sessionsView.classList.remove('hidden');
        sessionView.classList.add('hidden');
        roadmapsView.classList.add('hidden');
        roadmapView.classList.add('hidden');
        
        vscode.postMessage({
            command: 'showSessions'
        });
    }
    
    // Show roadmaps view
    function showRoadmaps() {
        sessionsTab.classList.remove('active');
        roadmapsTab.classList.add('active');
        
        sessionsView.classList.add('hidden');
        sessionView.classList.add('hidden');
        roadmapsView.classList.remove('hidden');
        roadmapView.classList.add('hidden');
        
        vscode.postMessage({
            command: 'showRoadmaps'
        });
    }
    
    // Create a new session
    function createNewSession() {
        // Show input dialog
        const topicInput = document.createElement('input');
        topicInput.type = 'text';
        topicInput.placeholder = 'Session Topic';
        
        const descriptionInput = document.createElement('textarea');
        descriptionInput.placeholder = 'Session Description';
        
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h2>Create New Session</h2>
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
                command: 'createSession',
                topic,
                description
            });
            
            document.body.removeChild(dialog);
        });
    }
    
    // Render sessions list
    function renderSessionsList() {
        if (sessions.length === 0) {
            sessionsList.innerHTML = '<div class="empty-state">No sessions yet</div>';
            return;
        }
        
        sessionsList.innerHTML = '';
        
        for (const session of sessions) {
            const sessionElement = document.createElement('div');
            sessionElement.className = 'session-item';
            sessionElement.innerHTML = `
                <div class="session-item-header">
                    <h3>${session.topic}</h3>
                    <div class="session-item-actions">
                        <button class="delete-button">Delete</button>
                    </div>
                </div>
                <div class="session-item-description">${session.description}</div>
                <div class="session-item-meta">
                    <span>${formatDate(session.createdAt)}</span>
                    <span>${session.ideas.length} ideas</span>
                </div>
            `;
            
            sessionElement.addEventListener('click', event => {
                if (!event.target.classList.contains('delete-button')) {
                    openSession(session.id);
                }
            });
            
            const deleteButton = sessionElement.querySelector('.delete-button');
            deleteButton.addEventListener('click', event => {
                event.stopPropagation();
                deleteSession(session.id);
            });
            
            sessionsList.appendChild(sessionElement);
        }
    }
    
    // Open a session
    function openSession(sessionId) {
        activeSessionId = sessionId;
        
        vscode.postMessage({
            command: 'openSession',
            sessionId
        });
    }
    
    // Delete a session
    function deleteSession(sessionId) {
        if (confirm('Are you sure you want to delete this session?')) {
            vscode.postMessage({
                command: 'deleteSession',
                sessionId
            });
        }
    }
    
    // Render session view
    function renderSessionView(session) {
        activeSessionId = session.id;
        
        sessionsTab.classList.add('active');
        roadmapsTab.classList.remove('active');
        
        sessionsView.classList.add('hidden');
        sessionView.classList.remove('hidden');
        roadmapsView.classList.add('hidden');
        roadmapView.classList.add('hidden');
        
        sessionTitle.textContent = session.topic;
        sessionDescription.textContent = session.description;
        
        renderIdeasList(session.ideas);
    }
    
    // Render ideas list
    function renderIdeasList(ideas) {
        if (ideas.length === 0) {
            ideasList.innerHTML = '<div class="empty-state">No ideas yet</div>';
            return;
        }
        
        ideasList.innerHTML = '';
        
        for (const idea of ideas) {
            const ideaElement = document.createElement('div');
            ideaElement.className = 'idea-item';
            ideaElement.dataset.id = idea.id;
            
            ideaElement.innerHTML = `
                <div class="idea-item-header">
                    <div class="idea-item-category">${idea.category}</div>
                    <div class="idea-item-actions">
                        <button class="delete-button">Delete</button>
                    </div>
                </div>
                <div class="idea-item-content">${idea.content}</div>
                <div class="idea-item-tags">
                    ${idea.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            `;
            
            const deleteButton = ideaElement.querySelector('.delete-button');
            deleteButton.addEventListener('click', () => {
                deleteIdea(idea.id);
            });
            
            ideasList.appendChild(ideaElement);
            
            // Render children
            if (idea.children && idea.children.length > 0) {
                const childrenContainer = document.createElement('div');
                childrenContainer.className = 'idea-children';
                
                for (const child of idea.children) {
                    const childElement = document.createElement('div');
                    childElement.className = 'idea-item child';
                    childElement.dataset.id = child.id;
                    
                    childElement.innerHTML = `
                        <div class="idea-item-header">
                            <div class="idea-item-category">${child.category}</div>
                            <div class="idea-item-actions">
                                <button class="delete-button">Delete</button>
                            </div>
                        </div>
                        <div class="idea-item-content">${child.content}</div>
                        <div class="idea-item-tags">
                            ${child.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    `;
                    
                    const deleteButton = childElement.querySelector('.delete-button');
                    deleteButton.addEventListener('click', () => {
                        deleteIdea(child.id);
                    });
                    
                    childrenContainer.appendChild(childElement);
                }
                
                ideaElement.appendChild(childrenContainer);
            }
        }
    }
    
    // Add an idea
    function addIdea() {
        if (!activeSessionId) {
            return;
        }
        
        // Show input dialog
        const contentInput = document.createElement('textarea');
        contentInput.placeholder = 'Idea Content';
        
        const categoryInput = document.createElement('input');
        categoryInput.type = 'text';
        categoryInput.placeholder = 'Category (e.g., feature, improvement, solution)';
        
        const tagsInput = document.createElement('input');
        tagsInput.type = 'text';
        tagsInput.placeholder = 'Tags (comma-separated)';
        
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h2>Add Idea</h2>
                <div class="dialog-form">
                    <div class="form-group">
                        <label for="content">Content:</label>
                        <div id="contentContainer"></div>
                    </div>
                    <div class="form-group">
                        <label for="category">Category:</label>
                        <div id="categoryContainer"></div>
                    </div>
                    <div class="form-group">
                        <label for="tags">Tags:</label>
                        <div id="tagsContainer"></div>
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
        document.getElementById('categoryContainer').appendChild(categoryInput);
        document.getElementById('tagsContainer').appendChild(tagsInput);
        
        const cancelButton = document.getElementById('cancelButton');
        const addButton = document.getElementById('addButton');
        
        cancelButton.addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
        
        addButton.addEventListener('click', () => {
            const content = contentInput.value.trim();
            const category = categoryInput.value.trim() || 'general';
            const tags = tagsInput.value.split(',').map(tag => tag.trim()).filter(tag => tag);
            
            if (!content) {
                alert('Please enter content');
                return;
            }
            
            vscode.postMessage({
                command: 'addIdea',
                sessionId: activeSessionId,
                content,
                category,
                tags
            });
            
            document.body.removeChild(dialog);
        });
    }
    
    // Delete an idea
    function deleteIdea(ideaId) {
        if (confirm('Are you sure you want to delete this idea?')) {
            vscode.postMessage({
                command: 'deleteIdea',
                sessionId: activeSessionId,
                ideaId
            });
        }
    }
    
    // Generate ideas
    function generateIdeas() {
        if (!activeSessionId) {
            return;
        }
        
        // Show input dialog
        const countInput = document.createElement('input');
        countInput.type = 'number';
        countInput.min = '1';
        countInput.max = '10';
        countInput.value = '5';
        
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h2>Generate Ideas</h2>
                <div class="dialog-form">
                    <div class="form-group">
                        <label for="count">Number of ideas to generate:</label>
                        <div id="countContainer"></div>
                    </div>
                </div>
                <div class="dialog-buttons">
                    <button id="cancelButton" class="secondary-button">Cancel</button>
                    <button id="generateButton" class="primary-button">Generate</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        document.getElementById('countContainer').appendChild(countInput);
        
        const cancelButton = document.getElementById('cancelButton');
        const generateButton = document.getElementById('generateButton');
        
        cancelButton.addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
        
        generateButton.addEventListener('click', () => {
            const count = parseInt(countInput.value);
            
            if (isNaN(count) || count < 1 || count > 10) {
                alert('Please enter a number between 1 and 10');
                return;
            }
            
            vscode.postMessage({
                command: 'generateIdeas',
                sessionId: activeSessionId,
                count
            });
            
            document.body.removeChild(dialog);
        });
    }
    
    // Create a roadmap
    function createRoadmap() {
        if (!activeSessionId) {
            return;
        }
        
        // Show input dialog
        const titleInput = document.createElement('input');
        titleInput.type = 'text';
        titleInput.placeholder = 'Roadmap Title';
        
        const descriptionInput = document.createElement('textarea');
        descriptionInput.placeholder = 'Roadmap Description';
        
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h2>Create Roadmap</h2>
                <div class="dialog-form">
                    <div class="form-group">
                        <label for="title">Title:</label>
                        <div id="titleContainer"></div>
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
        
        document.getElementById('titleContainer').appendChild(titleInput);
        document.getElementById('descriptionContainer').appendChild(descriptionInput);
        
        const cancelButton = document.getElementById('cancelButton');
        const createButton = document.getElementById('createButton');
        
        cancelButton.addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
        
        createButton.addEventListener('click', () => {
            const title = titleInput.value.trim();
            const description = descriptionInput.value.trim();
            
            if (!title) {
                alert('Please enter a title');
                return;
            }
            
            vscode.postMessage({
                command: 'createRoadmap',
                sessionId: activeSessionId,
                title,
                description
            });
            
            document.body.removeChild(dialog);
        });
    }
    
    // Render roadmaps list
    function renderRoadmapsList() {
        if (roadmaps.length === 0) {
            roadmapsList.innerHTML = '<div class="empty-state">No roadmaps yet</div>';
            return;
        }
        
        roadmapsList.innerHTML = '';
        
        for (const roadmap of roadmaps) {
            const roadmapElement = document.createElement('div');
            roadmapElement.className = 'roadmap-item';
            roadmapElement.innerHTML = `
                <div class="roadmap-item-header">
                    <h3>${roadmap.title}</h3>
                    <div class="roadmap-item-actions">
                        <button class="delete-button">Delete</button>
                    </div>
                </div>
                <div class="roadmap-item-description">${roadmap.description}</div>
                <div class="roadmap-item-meta">
                    <span>${formatDate(roadmap.createdAt)}</span>
                    <span>${roadmap.items.length} items</span>
                </div>
            `;
            
            roadmapElement.addEventListener('click', event => {
                if (!event.target.classList.contains('delete-button')) {
                    openRoadmap(roadmap.id);
                }
            });
            
            const deleteButton = roadmapElement.querySelector('.delete-button');
            deleteButton.addEventListener('click', event => {
                event.stopPropagation();
                deleteRoadmap(roadmap.id);
            });
            
            roadmapsList.appendChild(roadmapElement);
        }
    }
    
    // Open a roadmap
    function openRoadmap(roadmapId) {
        activeRoadmapId = roadmapId;
        
        vscode.postMessage({
            command: 'openRoadmap',
            roadmapId
        });
    }
    
    // Delete a roadmap
    function deleteRoadmap(roadmapId) {
        if (confirm('Are you sure you want to delete this roadmap?')) {
            vscode.postMessage({
                command: 'deleteRoadmap',
                roadmapId
            });
        }
    }
    
    // Render roadmap view
    function renderRoadmapView(roadmap) {
        activeRoadmapId = roadmap.id;
        
        sessionsTab.classList.remove('active');
        roadmapsTab.classList.add('active');
        
        sessionsView.classList.add('hidden');
        sessionView.classList.add('hidden');
        roadmapsView.classList.add('hidden');
        roadmapView.classList.remove('hidden');
        
        roadmapTitle.textContent = roadmap.title;
        roadmapDescription.textContent = roadmap.description;
        
        renderItemsList(roadmap.items);
    }
    
    // Render items list
    function renderItemsList(items) {
        if (items.length === 0) {
            itemsList.innerHTML = '<div class="empty-state">No items yet</div>';
            return;
        }
        
        itemsList.innerHTML = '';
        
        for (const item of items) {
            const itemElement = document.createElement('div');
            itemElement.className = `roadmap-item-card priority-${item.priority} status-${item.status}`;
            itemElement.dataset.id = item.id;
            
            itemElement.innerHTML = `
                <div class="roadmap-item-card-header">
                    <h3>${item.title}</h3>
                    <div class="roadmap-item-card-meta">
                        <span class="priority">${item.priority}</span>
                        <span class="status">${item.status}</span>
                    </div>
                </div>
                <div class="roadmap-item-card-description">${item.description}</div>
                <div class="roadmap-item-card-details">
                    ${item.estimatedTime ? `<div class="estimated-time">Estimated: ${item.estimatedTime}</div>` : ''}
                    ${item.dependencies.length > 0 ? `<div class="dependencies">Dependencies: ${item.dependencies.join(', ')}</div>` : ''}
                </div>
                <div class="roadmap-item-card-tags">
                    ${item.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
                <div class="roadmap-item-card-actions">
                    <select class="status-select">
                        <option value="pending" ${item.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="in_progress" ${item.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                        <option value="completed" ${item.status === 'completed' ? 'selected' : ''}>Completed</option>
                    </select>
                </div>
            `;
            
            const statusSelect = itemElement.querySelector('.status-select');
            statusSelect.addEventListener('change', () => {
                updateItemStatus(item.id, statusSelect.value);
            });
            
            itemsList.appendChild(itemElement);
            
            // Render children
            if (item.children && item.children.length > 0) {
                const childrenContainer = document.createElement('div');
                childrenContainer.className = 'roadmap-item-children';
                
                for (const child of item.children) {
                    const childElement = document.createElement('div');
                    childElement.className = `roadmap-item-card child priority-${child.priority} status-${child.status}`;
                    childElement.dataset.id = child.id;
                    
                    childElement.innerHTML = `
                        <div class="roadmap-item-card-header">
                            <h4>${child.title}</h4>
                            <div class="roadmap-item-card-meta">
                                <span class="priority">${child.priority}</span>
                                <span class="status">${child.status}</span>
                            </div>
                        </div>
                        <div class="roadmap-item-card-description">${child.description}</div>
                        <div class="roadmap-item-card-details">
                            ${child.estimatedTime ? `<div class="estimated-time">Estimated: ${child.estimatedTime}</div>` : ''}
                            ${child.dependencies.length > 0 ? `<div class="dependencies">Dependencies: ${child.dependencies.join(', ')}</div>` : ''}
                        </div>
                        <div class="roadmap-item-card-tags">
                            ${child.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                        <div class="roadmap-item-card-actions">
                            <select class="status-select">
                                <option value="pending" ${child.status === 'pending' ? 'selected' : ''}>Pending</option>
                                <option value="in_progress" ${child.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                                <option value="completed" ${child.status === 'completed' ? 'selected' : ''}>Completed</option>
                            </select>
                        </div>
                    `;
                    
                    const statusSelect = childElement.querySelector('.status-select');
                    statusSelect.addEventListener('change', () => {
                        updateItemStatus(child.id, statusSelect.value);
                    });
                    
                    childrenContainer.appendChild(childElement);
                }
                
                itemsList.appendChild(childrenContainer);
            }
        }
    }
    
    // Update item status
    function updateItemStatus(itemId, status) {
        vscode.postMessage({
            command: 'updateRoadmapItem',
            roadmapId: activeRoadmapId,
            itemId,
            updates: {
                status
            }
        });
    }
    
    // Format date
    function formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
})();
