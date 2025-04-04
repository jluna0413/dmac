"""
SwarmUI dashboard for DMac.
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp
from aiohttp import web

from config.config import config

logger = logging.getLogger('dmac.ui.swarmui')


class SwarmUIDashboard:
    """SwarmUI dashboard for DMac."""
    
    def __init__(self):
        """Initialize the SwarmUI dashboard."""
        self.enabled = config.get('ui.swarmui.enabled', True)
        self.port = config.get('ui.swarmui.port', 8080)
        self.host = config.get('ui.swarmui.host', 'localhost')
        self.static_dir = Path(__file__).parent / 'static'
        self.templates_dir = Path(__file__).parent / 'templates'
        self.app = None
        self.runner = None
        self.site = None
        self.process = None
        self.logger = logging.getLogger('dmac.ui.swarmui')
        
        # Dashboard data
        self.agents = {}
        self.tasks = {}
        self.system_status = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'uptime': 0,
            'start_time': time.time(),
        }
    
    async def initialize(self) -> bool:
        """Initialize the SwarmUI dashboard.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("SwarmUI dashboard is disabled in the configuration")
            return False
        
        self.logger.info("Initializing SwarmUI dashboard")
        
        try:
            # Create the static and templates directories if they don't exist
            os.makedirs(self.static_dir, exist_ok=True)
            os.makedirs(self.templates_dir, exist_ok=True)
            
            # Create the necessary static files
            await self._create_static_files()
            
            # Create the necessary template files
            await self._create_template_files()
            
            self.logger.info("SwarmUI dashboard initialized")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing SwarmUI dashboard: {e}")
            return False
    
    async def _create_static_files(self) -> None:
        """Create the necessary static files."""
        # Create CSS file
        css_file = self.static_dir / 'style.css'
        with open(css_file, 'w') as f:
            f.write("""
/* SwarmUI dashboard styles */
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

.card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.card h2 {
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

.status-active {
    background-color: #2ecc71;
}

.status-inactive {
    background-color: #e74c3c;
}

.status-warning {
    background-color: #f39c12;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

table th, table td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

table th {
    font-weight: bold;
}

.progress-bar {
    height: 8px;
    background-color: #ecf0f1;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 5px;
}

.progress-bar-fill {
    height: 100%;
    background-color: #3498db;
}

.task-list {
    max-height: 300px;
    overflow-y: auto;
}

.task-item {
    padding: 10px;
    border-bottom: 1px solid #eee;
}

.task-item:last-child {
    border-bottom: none;
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
}

.task-title {
    font-weight: bold;
}

.task-status {
    font-size: 0.8rem;
    padding: 2px 6px;
    border-radius: 4px;
}

.status-completed {
    background-color: #2ecc71;
    color: white;
}

.status-running {
    background-color: #3498db;
    color: white;
}

.status-error {
    background-color: #e74c3c;
    color: white;
}

.status-planning {
    background-color: #f39c12;
    color: white;
}

.task-details {
    font-size: 0.9rem;
    color: #7f8c8d;
}

.agent-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
}

.agent-item {
    background-color: #f8f9fa;
    border-radius: 4px;
    padding: 10px;
    text-align: center;
}

.agent-icon {
    font-size: 2rem;
    margin-bottom: 5px;
}

.agent-name {
    font-weight: bold;
    margin-bottom: 5px;
}

.agent-status {
    font-size: 0.8rem;
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
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
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
}
""")
        
        # Create JavaScript file
        js_file = self.static_dir / 'script.js'
        with open(js_file, 'w') as f:
            f.write("""
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
                    <div class="agent-icon">🤖</div>
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
    <title>DMac - SwarmUI Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <h1>DMac SwarmUI Dashboard</h1>
        <nav>
            <ul>
                <li><a href="/">Dashboard</a></li>
                <li><a href="/agents">Agents</a></li>
                <li><a href="/tasks">Tasks</a></li>
                <li><a href="/settings">Settings</a></li>
            </ul>
        </nav>
    </header>
    
    <div class="container">
        <div class="dashboard-grid">
            <div class="card">
                <h2>System Status</h2>
                <table>
                    <tr>
                        <td>CPU Usage</td>
                        <td id="cpu-usage-value">0%</td>
                    </tr>
                    <tr>
                        <td colspan="2">
                            <div class="progress-bar">
                                <div id="cpu-usage-bar" class="progress-bar-fill" style="width: 0%"></div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>Memory Usage</td>
                        <td id="memory-usage-value">0%</td>
                    </tr>
                    <tr>
                        <td colspan="2">
                            <div class="progress-bar">
                                <div id="memory-usage-bar" class="progress-bar-fill" style="width: 0%"></div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>Disk Usage</td>
                        <td id="disk-usage-value">0%</td>
                    </tr>
                    <tr>
                        <td colspan="2">
                            <div class="progress-bar">
                                <div id="disk-usage-bar" class="progress-bar-fill" style="width: 0%"></div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>Uptime</td>
                        <td id="uptime-value">0s</td>
                    </tr>
                </table>
            </div>
            
            <div class="card">
                <h2>Agent Status</h2>
                <div id="agent-list" class="agent-list">
                    <!-- Agent items will be added here dynamically -->
                </div>
            </div>
            
            <div class="card">
                <h2>Recent Tasks</h2>
                <div id="task-list" class="task-list">
                    <!-- Task items will be added here dynamically -->
                </div>
            </div>
            
            <div class="card">
                <h2>Quick Actions</h2>
                <div class="quick-actions">
                    <button onclick="location.href='/new-task'">New Task</button>
                    <button onclick="location.href='/agents'">Manage Agents</button>
                    <button onclick="location.href='/settings'">Settings</button>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <p>DMac SwarmUI Dashboard &copy; 2023</p>
    </footer>
    
    <script src="/static/script.js"></script>
</body>
</html>
""")
    
    async def start_server(self) -> bool:
        """Start the SwarmUI dashboard server.
        
        Returns:
            True if the server was started successfully, False otherwise.
        """
        if not self.enabled:
            self.logger.warning("SwarmUI dashboard is disabled")
            return False
        
        if self.app:
            self.logger.warning("SwarmUI dashboard server is already running")
            return True
        
        self.logger.info(f"Starting SwarmUI dashboard server on {self.host}:{self.port}")
        
        try:
            # Create the aiohttp application
            self.app = web.Application()
            
            # Set up routes
            self.app.router.add_static('/static', self.static_dir)
            self.app.router.add_get('/', self.handle_index)
            self.app.router.add_get('/api/system-status', self.handle_system_status)
            self.app.router.add_get('/api/agents', self.handle_agents)
            self.app.router.add_get('/api/tasks', self.handle_tasks)
            
            # Start the server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            self.logger.info(f"SwarmUI dashboard server started on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.exception(f"Error starting SwarmUI dashboard server: {e}")
            return False
    
    async def stop_server(self) -> None:
        """Stop the SwarmUI dashboard server."""
        if not self.app:
            return
        
        self.logger.info("Stopping SwarmUI dashboard server")
        
        try:
            if self.site:
                await self.site.stop()
                self.site = None
            
            if self.runner:
                await self.runner.cleanup()
                self.runner = None
            
            self.app = None
            
            self.logger.info("SwarmUI dashboard server stopped")
        except Exception as e:
            self.logger.exception(f"Error stopping SwarmUI dashboard server: {e}")
    
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
    
    async def handle_system_status(self, request: web.Request) -> web.Response:
        """Handle the system status API request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        # Update the system status
        self._update_system_status()
        
        return web.json_response(self.system_status)
    
    async def handle_agents(self, request: web.Request) -> web.Response:
        """Handle the agents API request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        return web.json_response(self.agents)
    
    async def handle_tasks(self, request: web.Request) -> web.Response:
        """Handle the tasks API request.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        return web.json_response(self.tasks)
    
    def _update_system_status(self) -> None:
        """Update the system status."""
        try:
            import psutil
            
            # Update CPU usage
            self.system_status['cpu_usage'] = psutil.cpu_percent()
            
            # Update memory usage
            memory = psutil.virtual_memory()
            self.system_status['memory_usage'] = memory.percent
            
            # Update disk usage
            disk = psutil.disk_usage('/')
            self.system_status['disk_usage'] = disk.percent
            
            # Update uptime
            self.system_status['uptime'] = time.time() - self.system_status['start_time']
        except ImportError:
            # If psutil is not available, use simulated values
            self.system_status['cpu_usage'] = 50
            self.system_status['memory_usage'] = 60
            self.system_status['disk_usage'] = 70
            self.system_status['uptime'] = time.time() - self.system_status['start_time']
    
    def update_agent_status(self, agent_id: str, agent_data: Dict[str, Any]) -> None:
        """Update the status of an agent.
        
        Args:
            agent_id: The ID of the agent.
            agent_data: The agent data.
        """
        self.agents[agent_id] = agent_data
    
    def update_task_status(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Update the status of a task.
        
        Args:
            task_id: The ID of the task.
            task_data: The task data.
        """
        self.tasks[task_id] = task_data
    
    async def cleanup(self) -> None:
        """Clean up resources used by the SwarmUI dashboard."""
        self.logger.info("Cleaning up SwarmUI dashboard")
        
        # Stop the server
        await self.stop_server()
        
        self.logger.info("SwarmUI dashboard cleaned up")
