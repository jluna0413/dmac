
// SwarmUI dashboard scripts
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the dashboard
    initDashboard();

    // Set up periodic updates
    setInterval(updateDashboard, 5000);
});

function initDashboard() {
    // Initialize charts and other components
    updateSystemStatus();
    updateAgentStatus();
    updateTaskList();
}

function updateDashboard() {
    // Update all dashboard components
    updateSystemStatus();
    updateAgentStatus();
    updateTaskList();
}

function updateSystemStatus() {
    // Fetch system status from the API
    fetch('/api/system-status')
        .then(response => response.json())
        .then(data => {
            // Update CPU usage
            document.getElementById('cpu-usage-value').textContent = data.cpu_usage + '%';
            document.getElementById('cpu-usage-bar').style.width = data.cpu_usage + '%';

            // Update memory usage
            document.getElementById('memory-usage-value').textContent = data.memory_usage + '%';
            document.getElementById('memory-usage-bar').style.width = data.memory_usage + '%';

            // Update disk usage
            document.getElementById('disk-usage-value').textContent = data.disk_usage + '%';
            document.getElementById('disk-usage-bar').style.width = data.disk_usage + '%';

            // Update uptime
            const uptime = formatUptime(data.uptime);
            document.getElementById('uptime-value').textContent = uptime;
        })
        .catch(error => {
            console.error('Error fetching system status:', error);
        });
}

function updateAgentStatus() {
    // Fetch agent status from the API
    fetch('/api/agents')
        .then(response => response.json())
        .then(data => {
            const agentList = document.getElementById('agent-list');
            agentList.innerHTML = '';

            // Add each agent to the list
            for (const agentId in data) {
                const agent = data[agentId];
                const agentItem = document.createElement('div');
                agentItem.className = 'agent-item';

                const statusClass = agent.state === 'IDLE' ? 'status-active' :
                                   agent.state === 'ERROR' ? 'status-inactive' : 'status-warning';

                agentItem.innerHTML = `
                    <div class="agent-icon">[AI]</div>
                    <div class="agent-name">${agent.name}</div>
                    <div class="agent-status">
                        <span class="status-indicator ${statusClass}"></span>
                        ${agent.state}
                    </div>
                `;

                agentList.appendChild(agentItem);
            }
        })
        .catch(error => {
            console.error('Error fetching agent status:', error);
        });
}

function updateTaskList() {
    // Fetch task list from the API
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            const taskList = document.getElementById('task-list');
            taskList.innerHTML = '';

            // Add each task to the list
            for (const taskId in data) {
                const task = data[taskId];
                const taskItem = document.createElement('div');
                taskItem.className = 'task-item';

                const statusClass = task.status === 'completed' ? 'status-completed' :
                                   task.status === 'error' ? 'status-error' :
                                   task.status === 'running' ? 'status-running' : 'status-planning';

                const createdAt = new Date(task.created_at * 1000).toLocaleString();
                const updatedAt = new Date(task.updated_at * 1000).toLocaleString();

                taskItem.innerHTML = `
                    <div class="task-header">
                        <div class="task-title">${task.prompt.substring(0, 50)}${task.prompt.length > 50 ? '...' : ''}</div>
                        <div class="task-status ${statusClass}">${task.status}</div>
                    </div>
                    <div class="task-details">
                        <div>Created: ${createdAt}</div>
                        <div>Updated: ${updatedAt}</div>
                    </div>
                `;

                taskList.appendChild(taskItem);
            }
        })
        .catch(error => {
            console.error('Error fetching task list:', error);
        });
}

function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    let result = '';
    if (days > 0) result += days + 'd ';
    if (hours > 0) result += hours + 'h ';
    if (minutes > 0) result += minutes + 'm ';
    if (secs > 0 || result === '') result += secs + 's';

    return result;
}
