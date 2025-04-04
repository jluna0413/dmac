"""
Dashboard for DMac.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from aiohttp import web

from config.config import config

logger = logging.getLogger('dmac.ui.dashboard')


class Dashboard:
    """Dashboard for DMac."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.enabled = config.get('ui.dashboard.enabled', True)
        self.port = config.get('ui.dashboard.port', 8079)
        self.host = config.get('ui.dashboard.host', 'localhost')
        self.static_dir = Path(__file__).parent / 'static'
        self.templates_dir = Path(__file__).parent / 'templates'
        self.app = None
        self.runner = None
        self.site = None
        self.logger = logging.getLogger('dmac.ui.dashboard')
        
        # Component status
        self.component_status = {}
        
        # System status
        self.system_status = {
            'agents': {},
            'tasks': {},
            'models': {},
        }
    
    async def initialize(self) -> bool:
        """Initialize the dashboard.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("Dashboard is disabled in the configuration")
            return False
        
        self.logger.info("Initializing dashboard")
        
        try:
            # Create the necessary directories if they don't exist
            os.makedirs(self.static_dir, exist_ok=True)
            os.makedirs(self.templates_dir, exist_ok=True)
            
            # Create the necessary static files
            await self._create_static_files()
            
            # Create the necessary template files
            await self._create_template_files()
            
            self.logger.info("Dashboard initialized")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing dashboard: {e}")
            return False
    
    async def _create_static_files(self) -> None:
        """Create the necessary static files."""
        # Create CSS file
        css_file = self.static_dir / 'style.css'
        with open(css_file, 'w') as f:
            f.write("""
/* Dashboard styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

header h1 {
    margin: 0;
    font-size: 1.8rem;
}

nav ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
}

nav ul li {
    margin-left: 20px;
}

nav ul li a {
    color: white;
    text-decoration: none;
}

nav ul li a:hover {
    text-decoration: underline;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.dashboard-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.dashboard-card h2 {
    margin-top: 0;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    font-size: 1.2rem;
}

.status-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 5px;
}

.status-running {
    background-color: #2ecc71;
}

.status-stopped {
    background-color: #e74c3c;
}

.status-disabled {
    background-color: #95a5a6;
}

.component-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.component-list li {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.component-list li:last-child {
    border-bottom: none;
}

.component-name {
    font-weight: bold;
}

.component-status {
    font-size: 0.9rem;
    color: #7f8c8d;
}

.component-actions {
    display: flex;
    gap: 5px;
}

.component-actions button {
    padding: 5px 10px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
}

.component-actions button:hover {
    background-color: #2980b9;
}

.component-actions button:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
}

.agent-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.agent-list li {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

.agent-list li:last-child {
    border-bottom: none;
}

.agent-name {
    font-weight: bold;
}

.agent-type {
    font-size: 0.9rem;
    color: #7f8c8d;
}

.agent-state {
    font-size: 0.9rem;
    margin-top: 5px;
}

.agent-state-idle {
    color: #2ecc71;
}

.agent-state-busy {
    color: #f39c12;
}

.agent-state-error {
    color: #e74c3c;
}

.task-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.task-list li {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

.task-list li:last-child {
    border-bottom: none;
}

.task-prompt {
    font-weight: bold;
    margin-bottom: 5px;
}

.task-status {
    font-size: 0.9rem;
    margin-top: 5px;
}

.task-status-pending {
    color: #3498db;
}

.task-status-running {
    color: #f39c12;
}

.task-status-completed {
    color: #2ecc71;
}

.task-status-failed {
    color: #e74c3c;
}

.model-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.model-list li {
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

.model-list li:last-child {
    border-bottom: none;
}

.model-name {
    font-weight: bold;
}

.model-type {
    font-size: 0.9rem;
    color: #7f8c8d;
}

.model-usage {
    font-size: 0.9rem;
    margin-top: 5px;
}

footer {
    margin-top: 40px;
    text-align: center;
    padding: 20px;
    color: #7f8c8d;
    font-size: 0.9rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    header {
        flex-direction: column;
    }
    
    nav ul {
        margin-top: 10px;
    }
    
    nav ul li {
        margin-left: 10px;
        margin-right: 10px;
    }
    
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
}
""")
        
        # Create JavaScript file
        js_file = self.static_dir / 'script.js'
        with open(js_file, 'w') as f:
            f.write("""
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
""")
    
    async def _create_template_files(self) -> None:
        """Create the necessary template files."""
        # Create index.html
        index_file = self.templates_dir / 'index.html'
        with open(index_file, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DMac Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <h1>DMac Dashboard</h1>
        <nav>
            <ul>
                <li><a href="/">Dashboard</a></li>
                <li><a href="/agents">Agents</a></li>
                <li><a href="/tasks">Tasks</a></li>
                <li><a href="/models">Models</a></li>
                <li><a href="/settings">Settings</a></li>
            </ul>
        </nav>
    </header>
    
    <div class="container">
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <h2>UI Components</h2>
                <ul id="component-list" class="component-list">
                    <!-- Component items will be added here dynamically -->
                    <li>Loading components...</li>
                </ul>
            </div>
            
            <div class="dashboard-card">
                <h2>Active Agents</h2>
                <ul id="agent-list" class="agent-list">
                    <!-- Agent items will be added here dynamically -->
                    <li>Loading agents...</li>
                </ul>
            </div>
            
            <div class="dashboard-card">
                <h2>Recent Tasks</h2>
                <ul id="task-list" class="task-list">
                    <!-- Task items will be added here dynamically -->
                    <li>Loading tasks...</li>
                </ul>
            </div>
            
            <div class="dashboard-card">
                <h2>Models</h2>
                <ul id="model-list" class="model-list">
                    <!-- Model items will be added here dynamically -->
                    <li>Loading models...</li>
                </ul>
            </div>
        </div>
    </div>
    
    <footer>
        <p>DMac Dashboard &copy; 2023</p>
    </footer>
    
    <script src="/static/script.js"></script>
</body>
</html>
""")
    
    async def start_server(self) -> bool:
        """Start the dashboard server.
        
        Returns:
            True if the server was started successfully, False otherwise.
        """
        if not self.enabled:
            self.logger.warning("Dashboard is disabled")
            return False
        
        if self.app:
            self.logger.warning("Dashboard server is already running")
            return True
        
        self.logger.info(f"Starting dashboard server on {self.host}:{self.port}")
        
        try:
            # Create the aiohttp application
            self.app = web.Application()
            
            # Set up routes
            self.app.router.add_static('/static', self.static_dir)
            self.app.router.add_get('/', self.handle_index)
            self.app.router.add_get('/api/components', self.handle_api_components_get)
            self.app.router.add_get('/api/components/{component_name}', self.handle_api_component_get)
            self.app.router.add_post('/api/components/{component_name}/open', self.handle_api_component_open)
            self.app.router.add_get('/api/agents', self.handle_api_agents_get)
            self.app.router.add_get('/api/tasks', self.handle_api_tasks_get)
            self.app.router.add_get('/api/models', self.handle_api_models_get)
            
            # Start the server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            self.logger.info(f"Dashboard server started on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.exception(f"Error starting dashboard server: {e}")
            return False
    
    async def stop_server(self) -> None:
        """Stop the dashboard server."""
        if not self.app:
            return
        
        self.logger.info("Stopping dashboard server")
        
        try:
            if self.site:
                await self.site.stop()
                self.site = None
            
            if self.runner:
                await self.runner.cleanup()
                self.runner = None
            
            self.app = None
            
            self.logger.info("Dashboard server stopped")
        except Exception as e:
            self.logger.exception(f"Error stopping dashboard server: {e}")
    
    async def handle_index(self, request: web.Request) -> web.Response:
        """Handle the index page request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        # Read the index.html template
        index_path = self.templates_dir / 'index.html'
        with open(index_path, 'r') as f:
            content = f.read()
        
        return web.Response(text=content, content_type='text/html')
    
    async def handle_api_components_get(self, request: web.Request) -> web.Response:
        """Handle the GET /api/components request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        return web.json_response(self.component_status)
    
    async def handle_api_component_get(self, request: web.Request) -> web.Response:
        """Handle the GET /api/components/{component_name} request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        component_name = request.match_info['component_name']
        
        if component_name not in self.component_status:
            return web.json_response({
                'success': False,
                'error': f"Component {component_name} not found"
            }, status=404)
        
        return web.json_response(self.component_status[component_name])
    
    async def handle_api_component_open(self, request: web.Request) -> web.Response:
        """Handle the POST /api/components/{component_name}/open request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        component_name = request.match_info['component_name']
        
        if component_name not in self.component_status:
            return web.json_response({
                'success': False,
                'error': f"Component {component_name} not found"
            }, status=404)
        
        if not self.component_status[component_name]['running']:
            return web.json_response({
                'success': False,
                'error': f"Component {component_name} is not running"
            }, status=400)
        
        # In a real implementation, you would open the component in a web browser
        # For now, we'll just simulate success
        
        return web.json_response({
            'success': True,
            'message': f"Opening {component_name}",
            'url': self.component_status[component_name]['url']
        })
    
    async def handle_api_agents_get(self, request: web.Request) -> web.Response:
        """Handle the GET /api/agents request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        return web.json_response(self.system_status['agents'])
    
    async def handle_api_tasks_get(self, request: web.Request) -> web.Response:
        """Handle the GET /api/tasks request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        return web.json_response(self.system_status['tasks'])
    
    async def handle_api_models_get(self, request: web.Request) -> web.Response:
        """Handle the GET /api/models request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        return web.json_response(self.system_status['models'])
    
    def update_component_status(self, component_status: Dict[str, Any]) -> None:
        """Update the component status.
        
        Args:
            component_status: The component status.
        """
        self.component_status = component_status
    
    def update_agent_status(self, agent_id: str, status: Dict[str, Any]) -> None:
        """Update the status of an agent.
        
        Args:
            agent_id: The ID of the agent.
            status: The status of the agent.
        """
        self.system_status['agents'][agent_id] = status
    
    def update_task_status(self, task_id: str, status: Dict[str, Any]) -> None:
        """Update the status of a task.
        
        Args:
            task_id: The ID of the task.
            status: The status of the task.
        """
        self.system_status['tasks'][task_id] = status
    
    def update_model_status(self, model_name: str, status: Dict[str, Any]) -> None:
        """Update the status of a model.
        
        Args:
            model_name: The name of the model.
            status: The status of the model.
        """
        self.system_status['models'][model_name] = status
    
    async def cleanup(self) -> None:
        """Clean up resources used by the dashboard."""
        self.logger.info("Cleaning up dashboard")
        
        # Stop the server
        await self.stop_server()
        
        self.logger.info("Dashboard cleaned up")
