// @ts-check

(function() {
    // Get VS Code API
    const vscode = acquireVsCodeApi();
    
    // Elements
    const toggleButton = document.getElementById('toggleButton');
    const executeButton = document.getElementById('executeButton');
    const taskDescription = document.getElementById('taskDescription');
    const tasksList = document.getElementById('tasksList');
    
    // State
    let isActive = false;
    let activeTaskId = null;
    let tasks = [];
    
    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        // Set up event listeners
        toggleButton.addEventListener('click', toggleAutonomousMode);
        executeButton.addEventListener('click', executeTask);
        
        // Restore state
        const state = vscode.getState();
        if (state) {
            isActive = state.isActive || false;
            tasks = state.tasks || [];
            activeTaskId = state.activeTaskId || null;
            updateUI();
        }
    });
    
    // Handle messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.command) {
            case 'updateTasks':
                isActive = message.isActive;
                tasks = message.tasks;
                activeTaskId = message.activeTaskId;
                updateUI();
                
                // Save state
                vscode.setState({ isActive, tasks, activeTaskId });
                break;
        }
    });
    
    /**
     * Toggle autonomous mode
     */
    function toggleAutonomousMode() {
        vscode.postMessage({
            command: 'toggleAutonomousMode'
        });
    }
    
    /**
     * Execute a task
     */
    function executeTask() {
        const description = taskDescription.value.trim();
        if (!description) {
            return;
        }
        
        vscode.postMessage({
            command: 'executeTask',
            description
        });
        
        // Clear the input
        taskDescription.value = '';
    }
    
    /**
     * Cancel a task
     * 
     * @param {string} taskId The task ID
     */
    function cancelTask(taskId) {
        vscode.postMessage({
            command: 'cancelTask',
            taskId
        });
    }
    
    /**
     * Update the UI
     */
    function updateUI() {
        // Update toggle button
        toggleButton.textContent = isActive ? 'Stop' : 'Start';
        toggleButton.classList.toggle('active', isActive);
        
        // Update execute button
        executeButton.disabled = !isActive;
        
        // Update tasks list
        renderTasks();
    }
    
    /**
     * Render tasks
     */
    function renderTasks() {
        // Clear tasks list
        tasksList.innerHTML = '';
        
        if (tasks.length === 0) {
            tasksList.innerHTML = '<div class="empty-state">No tasks yet</div>';
            return;
        }
        
        // Sort tasks by creation time (newest first)
        const sortedTasks = [...tasks].sort((a, b) => b.createdAt - a.createdAt);
        
        // Render tasks
        for (const task of sortedTasks) {
            const taskElement = createTaskElement(task);
            tasksList.appendChild(taskElement);
        }
    }
    
    /**
     * Create a task element
     * 
     * @param {any} task The task
     * @returns {HTMLElement} The task element
     */
    function createTaskElement(task) {
        const taskElement = document.createElement('div');
        taskElement.className = 'task';
        taskElement.dataset.id = task.id;
        
        // Add active class if this is the active task
        if (task.id === activeTaskId) {
            taskElement.classList.add('active');
        }
        
        // Add status class
        taskElement.classList.add(task.status);
        
        // Create task header
        const taskHeader = document.createElement('div');
        taskHeader.className = 'task-header';
        
        // Create task title
        const taskTitle = document.createElement('div');
        taskTitle.className = 'task-title';
        taskTitle.textContent = task.description;
        taskHeader.appendChild(taskTitle);
        
        // Create task status
        const taskStatus = document.createElement('div');
        taskStatus.className = 'task-status';
        taskStatus.textContent = formatStatus(task.status);
        taskHeader.appendChild(taskStatus);
        
        taskElement.appendChild(taskHeader);
        
        // Create task details
        const taskDetails = document.createElement('div');
        taskDetails.className = 'task-details';
        
        // Add created time
        const createdTime = document.createElement('div');
        createdTime.className = 'task-time';
        createdTime.textContent = `Created: ${formatTime(task.createdAt)}`;
        taskDetails.appendChild(createdTime);
        
        // Add started time if available
        if (task.startedAt) {
            const startedTime = document.createElement('div');
            startedTime.className = 'task-time';
            startedTime.textContent = `Started: ${formatTime(task.startedAt)}`;
            taskDetails.appendChild(startedTime);
        }
        
        // Add completed time if available
        if (task.completedAt) {
            const completedTime = document.createElement('div');
            completedTime.className = 'task-time';
            completedTime.textContent = `Completed: ${formatTime(task.completedAt)}`;
            taskDetails.appendChild(completedTime);
        }
        
        // Add error if available
        if (task.error) {
            const errorElement = document.createElement('div');
            errorElement.className = 'task-error';
            errorElement.textContent = `Error: ${task.error}`;
            taskDetails.appendChild(errorElement);
        }
        
        // Add result if available
        if (task.result) {
            const resultElement = document.createElement('div');
            resultElement.className = 'task-result';
            resultElement.textContent = `Result: ${formatResult(task.result)}`;
            taskDetails.appendChild(resultElement);
        }
        
        taskElement.appendChild(taskDetails);
        
        // Add cancel button if task is in progress
        if (task.status === 'in_progress') {
            const cancelButton = document.createElement('button');
            cancelButton.className = 'cancel-button';
            cancelButton.textContent = 'Cancel';
            cancelButton.addEventListener('click', () => cancelTask(task.id));
            taskElement.appendChild(cancelButton);
        }
        
        // Add subtasks if available
        if (task.subtasks && task.subtasks.length > 0) {
            const subtasksContainer = document.createElement('div');
            subtasksContainer.className = 'subtasks-container';
            
            const subtasksHeader = document.createElement('div');
            subtasksHeader.className = 'subtasks-header';
            subtasksHeader.textContent = 'Subtasks';
            subtasksContainer.appendChild(subtasksHeader);
            
            const subtasksList = document.createElement('div');
            subtasksList.className = 'subtasks-list';
            
            // Sort subtasks by creation time
            const sortedSubtasks = [...task.subtasks].sort((a, b) => a.createdAt - b.createdAt);
            
            for (const subtask of sortedSubtasks) {
                const subtaskElement = createSubtaskElement(subtask);
                subtasksList.appendChild(subtaskElement);
            }
            
            subtasksContainer.appendChild(subtasksList);
            taskElement.appendChild(subtasksContainer);
        }
        
        return taskElement;
    }
    
    /**
     * Create a subtask element
     * 
     * @param {any} subtask The subtask
     * @returns {HTMLElement} The subtask element
     */
    function createSubtaskElement(subtask) {
        const subtaskElement = document.createElement('div');
        subtaskElement.className = 'subtask';
        subtaskElement.dataset.id = subtask.id;
        
        // Add status class
        subtaskElement.classList.add(subtask.status);
        
        // Create subtask header
        const subtaskHeader = document.createElement('div');
        subtaskHeader.className = 'subtask-header';
        
        // Create subtask title
        const subtaskTitle = document.createElement('div');
        subtaskTitle.className = 'subtask-title';
        subtaskTitle.textContent = subtask.description;
        subtaskHeader.appendChild(subtaskTitle);
        
        // Create subtask status
        const subtaskStatus = document.createElement('div');
        subtaskStatus.className = 'subtask-status';
        subtaskStatus.textContent = formatStatus(subtask.status);
        subtaskHeader.appendChild(subtaskStatus);
        
        subtaskElement.appendChild(subtaskHeader);
        
        return subtaskElement;
    }
    
    /**
     * Format a status
     * 
     * @param {string} status The status
     * @returns {string} The formatted status
     */
    function formatStatus(status) {
        switch (status) {
            case 'pending':
                return 'Pending';
            case 'in_progress':
                return 'In Progress';
            case 'completed':
                return 'Completed';
            case 'failed':
                return 'Failed';
            case 'cancelled':
                return 'Cancelled';
            default:
                return status;
        }
    }
    
    /**
     * Format a time
     * 
     * @param {number} time The time
     * @returns {string} The formatted time
     */
    function formatTime(time) {
        return new Date(time).toLocaleString();
    }
    
    /**
     * Format a result
     * 
     * @param {any} result The result
     * @returns {string} The formatted result
     */
    function formatResult(result) {
        if (typeof result === 'object') {
            return result.message || JSON.stringify(result);
        }
        
        return String(result);
    }
})();
