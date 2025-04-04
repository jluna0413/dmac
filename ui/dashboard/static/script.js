
// Dashboard scripts
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the dashboard
    initDashboard();
    
    // Set up event listeners
    setupEventListeners();
    
    // Refresh the dashboard every 5 seconds
    setInterval(refreshDashboard, 5000);
});

function initDashboard() {
    // Load the initial data
    fetchComponentStatus();
    fetchAgentStatus();
    fetchTaskStatus();
    fetchModelStatus();
}

function setupEventListeners() {
    // Add event listeners for buttons
    document.querySelectorAll('.open-component-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            const componentName = this.dataset.component;
            openComponent(componentName);
        });
    });
}

function refreshDashboard() {
    // Refresh the dashboard data
    fetchComponentStatus();
    fetchAgentStatus();
    fetchTaskStatus();
    fetchModelStatus();
}

function fetchComponentStatus() {
    fetch('/api/components')
        .then(response => response.json())
        .then(data => {
            updateComponentStatus(data);
        })
        .catch(error => {
            console.error('Error fetching component status:', error);
        });
}

function updateComponentStatus(data) {
    const componentList = document.getElementById('component-list');
    if (!componentList) return;
    
    componentList.innerHTML = '';
    
    for (const [name, status] of Object.entries(data)) {
        const li = document.createElement('li');
        
        const statusClass = status.running ? 'status-running' : (status.enabled ? 'status-stopped' : 'status-disabled');
        
        li.innerHTML = `
            <div>
                <span class="component-name">${name}</span>
                <div class="component-status">
                    <span class="status-indicator ${statusClass}"></span>
                    ${status.running ? 'Running' : (status.enabled ? 'Stopped' : 'Disabled')}
                    ${status.url ? `(${status.url})` : ''}
                </div>
            </div>
            <div class="component-actions">
                <button class="open-component-btn" data-component="${name}" ${status.running ? '' : 'disabled'}>Open</button>
            </div>
        `;
        
        componentList.appendChild(li);
    }
    
    // Re-attach event listeners
    document.querySelectorAll('.open-component-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            const componentName = this.dataset.component;
            openComponent(componentName);
        });
    });
}

function openComponent(componentName) {
    fetch(`/api/components/${componentName}/open`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`Opening ${componentName}...`);
            } else {
                console.error(`Error opening ${componentName}: ${data.error}`);
            }
        })
        .catch(error => {
            console.error(`Error opening ${componentName}:`, error);
        });
}

function fetchAgentStatus() {
    fetch('/api/agents')
        .then(response => response.json())
        .then(data => {
            updateAgentStatus(data);
        })
        .catch(error => {
            console.error('Error fetching agent status:', error);
        });
}

function updateAgentStatus(data) {
    const agentList = document.getElementById('agent-list');
    if (!agentList) return;
    
    agentList.innerHTML = '';
    
    if (Object.keys(data).length === 0) {
        agentList.innerHTML = '<li>No agents available</li>';
        return;
    }
    
    for (const [id, agent] of Object.entries(data)) {
        const li = document.createElement('li');
        
        const stateClass = `agent-state-${agent.state.toLowerCase()}`;
        
        li.innerHTML = `
            <div class="agent-name">${agent.name}</div>
            <div class="agent-type">${agent.agent_type}</div>
            <div class="agent-state ${stateClass}">
                State: ${agent.state}
            </div>
        `;
        
        agentList.appendChild(li);
    }
}

function fetchTaskStatus() {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            updateTaskStatus(data);
        })
        .catch(error => {
            console.error('Error fetching task status:', error);
        });
}

function updateTaskStatus(data) {
    const taskList = document.getElementById('task-list');
    if (!taskList) return;
    
    taskList.innerHTML = '';
    
    if (Object.keys(data).length === 0) {
        taskList.innerHTML = '<li>No tasks available</li>';
        return;
    }
    
    for (const [id, task] of Object.entries(data)) {
        const li = document.createElement('li');
        
        const statusClass = `task-status-${task.status.toLowerCase()}`;
        
        li.innerHTML = `
            <div class="task-prompt">${task.prompt}</div>
            <div class="task-status ${statusClass}">
                Status: ${task.status}
            </div>
        `;
        
        taskList.appendChild(li);
    }
}

function fetchModelStatus() {
    fetch('/api/models')
        .then(response => response.json())
        .then(data => {
            updateModelStatus(data);
        })
        .catch(error => {
            console.error('Error fetching model status:', error);
        });
}

function updateModelStatus(data) {
    const modelList = document.getElementById('model-list');
    if (!modelList) return;
    
    modelList.innerHTML = '';
    
    if (Object.keys(data).length === 0) {
        modelList.innerHTML = '<li>No models available</li>';
        return;
    }
    
    for (const [name, model] of Object.entries(data)) {
        const li = document.createElement('li');
        
        li.innerHTML = `
            <div class="model-name">${name}</div>
            <div class="model-type">${model.type}</div>
            <div class="model-usage">
                Usage: ${model.usage_count} requests
            </div>
        `;
        
        modelList.appendChild(li);
    }
}
