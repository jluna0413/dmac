"""
OpenCanvas workflow for DMac.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from aiohttp import web
except ImportError:
    # For development without aiohttp installed
    class web:
        class Request: pass
        class Response: pass
        class Application: pass
        class AppRunner: pass
        class TCPSite: pass

        @staticmethod
        def json_response(data, status=200):
            return {"data": data, "status": status}

from config.config import config

logger = logging.getLogger('dmac.ui.opencanvas')


class OpenCanvasWorkflow:
    """OpenCanvas workflow for DMac."""

    def __init__(self):
        """Initialize the OpenCanvas workflow."""
        self.enabled = config.get('ui.opencanvas.enabled', True)
        self.port = config.get('ui.opencanvas.port', 8082)
        self.host = config.get('ui.opencanvas.host', 'localhost')
        self.static_dir = Path(__file__).parent / 'static'
        self.templates_dir = Path(__file__).parent / 'templates'
        self.workflows_dir = Path(__file__).parent / 'workflows'
        self.app = None
        self.runner = None
        self.site = None
        self.logger = logging.getLogger('dmac.ui.opencanvas')

        # Workflow data
        self.workflows = {}

    async def initialize(self) -> bool:
        """Initialize the OpenCanvas workflow.

        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("OpenCanvas workflow is disabled in the configuration")
            return False

        self.logger.info("Initializing OpenCanvas workflow")

        try:
            # Create the necessary directories if they don't exist
            os.makedirs(self.static_dir, exist_ok=True)
            os.makedirs(self.templates_dir, exist_ok=True)
            os.makedirs(self.workflows_dir, exist_ok=True)

            # Create the necessary static files
            await self._create_static_files()

            # Create the necessary template files
            await self._create_template_files()

            # Load existing workflows
            await self._load_workflows()

            self.logger.info("OpenCanvas workflow initialized")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing OpenCanvas workflow: {e}")
            return False

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
    <title>DMac - OpenCanvas Workflow</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <h1>DMac OpenCanvas Workflow</h1>
        <nav>
            <ul>
                <li><a href="/">Dashboard</a></li>
                <li><a href="/workflows">Workflows</a></li>
                <li><a href="/editor">Editor</a></li>
                <li><a href="/settings">Settings</a></li>
            </ul>
        </nav>
    </header>

    <div class="container">
        <h2>Welcome to OpenCanvas Workflow</h2>
        <p>Create and manage workflows for the DMac AI agent swarm.</p>

        <div class="workflow-list">
            <!-- Workflow cards will be added here dynamically -->
        </div>
    </div>

    <footer>
        <p>DMac OpenCanvas Workflow &copy; 2023</p>
    </footer>

    <script src="/static/script.js"></script>
</body>
</html>
""")

        # Create editor.html
        editor_file = self.templates_dir / 'editor.html'
        with open(editor_file, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DMac - OpenCanvas Workflow Editor</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <h1>DMac OpenCanvas Workflow Editor</h1>
        <nav>
            <ul>
                <li><a href="/">Dashboard</a></li>
                <li><a href="/workflows">Workflows</a></li>
                <li><a href="/editor">Editor</a></li>
                <li><a href="/settings">Settings</a></li>
            </ul>
        </nav>
    </header>

    <div class="container">
        <div class="workflow-header">
            <div>
                <label for="workflow-name">Workflow Name:</label>
                <input type="text" id="workflow-name" placeholder="Untitled Workflow">
            </div>
            <div>
                <label for="workflow-description">Description:</label>
                <input type="text" id="workflow-description" placeholder="Workflow description">
            </div>
        </div>

        <div class="toolbar">
            <button id="add-agent-node">Add Agent</button>
            <button id="add-tool-node">Add Tool</button>
            <button id="add-data-node">Add Data</button>
            <button id="add-output-node">Add Output</button>
            <button id="save-workflow">Save Workflow</button>
        </div>

        <div class="editor-layout">
            <div id="workflow-canvas" class="workflow-canvas">
                <!-- Nodes and connections will be added here dynamically -->
            </div>

            <div id="properties-panel" class="properties-panel">
                <h2>Properties</h2>
                <p>Select a node to edit its properties.</p>
            </div>
        </div>
    </div>

    <footer>
        <p>DMac OpenCanvas Workflow &copy; 2023</p>
    </footer>

    <script src="/static/script.js"></script>
</body>
</html>
""")

        # Create workflows.html
        workflows_file = self.templates_dir / 'workflows.html'
        with open(workflows_file, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DMac - OpenCanvas Workflows</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <h1>DMac OpenCanvas Workflows</h1>
        <nav>
            <ul>
                <li><a href="/">Dashboard</a></li>
                <li><a href="/workflows">Workflows</a></li>
                <li><a href="/editor">Editor</a></li>
                <li><a href="/settings">Settings</a></li>
            </ul>
        </nav>
    </header>

    <div class="container">
        <div class="workflows-header">
            <h2>Your Workflows</h2>
            <button onclick="location.href='/editor'">Create New Workflow</button>
        </div>

        <div id="workflow-list" class="workflow-list">
            <!-- Workflow cards will be added here dynamically -->
        </div>
    </div>

    <footer>
        <p>DMac OpenCanvas Workflow &copy; 2023</p>
    </footer>

    <script>
        // Fetch workflows when the page loads
        document.addEventListener('DOMContentLoaded', function() {
            fetchWorkflows();
        });

        function fetchWorkflows() {
            fetch('/api/workflows')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayWorkflows(data.workflows);
                    } else {
                        alert('Error fetching workflows: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error fetching workflows:', error);
                });
        }

        function displayWorkflows(workflows) {
            const workflowList = document.getElementById('workflow-list');
            workflowList.innerHTML = '';

            if (workflows.length === 0) {
                workflowList.innerHTML = '<p>No workflows found. Create your first workflow!</p>';
                return;
            }

            workflows.forEach(workflow => {
                const card = document.createElement('div');
                card.className = 'workflow-card';
                card.onclick = function() {
                    location.href = `/editor?id=${workflow.id}`;
                };

                const created = new Date(workflow.created).toLocaleString();
                const updated = new Date(workflow.updated).toLocaleString();

                card.innerHTML = `
                    <h3>${workflow.name}</h3>
                    <p>${workflow.description}</p>
                    <div class="workflow-meta">
                        <span>Created: ${created}</span>
                        <span>Updated: ${updated}</span>
                    </div>
                `;

                workflowList.appendChild(card);
            });
        }
    </script>
</body>
</html>
""")

    async def _create_static_files(self) -> None:
        """Create the necessary static files."""
        # CSS and JavaScript files were created in the previous method
        pass

    async def _load_workflows(self) -> None:
        """Load existing workflows from files."""
        workflow_files = list(self.workflows_dir.glob('*.json'))

        for file_path in workflow_files:
            try:
                with open(file_path, 'r') as f:
                    workflow = json.load(f)
                    self.workflows[workflow['id']] = workflow
            except Exception as e:
                self.logger.exception(f"Error loading workflow from {file_path}: {e}")

        self.logger.info(f"Loaded {len(self.workflows)} workflows")

    async def start_server(self) -> bool:
        """Start the OpenCanvas workflow server.

        Returns:
            True if the server was started successfully, False otherwise.
        """
        if not self.enabled:
            self.logger.warning("OpenCanvas workflow is disabled")
            return False

        if self.app:
            self.logger.warning("OpenCanvas workflow server is already running")
            return True

        self.logger.info(f"Starting OpenCanvas workflow server on {self.host}:{self.port}")

        try:
            # Create the aiohttp application
            self.app = web.Application()

            # Set up routes
            self.app.router.add_static('/static', self.static_dir)
            self.app.router.add_get('/', self.handle_index)
            self.app.router.add_get('/workflows', self.handle_workflows)
            self.app.router.add_get('/editor', self.handle_editor)
            self.app.router.add_get('/api/workflows', self.handle_api_workflows_get)
            self.app.router.add_get('/api/workflows/{workflow_id}', self.handle_api_workflow_get)
            self.app.router.add_post('/api/workflows', self.handle_api_workflows_post)

            # Start the server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()

            self.logger.info(f"OpenCanvas workflow server started on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.exception(f"Error starting OpenCanvas workflow server: {e}")
            return False

    async def stop_server(self) -> None:
        """Stop the OpenCanvas workflow server."""
        if not self.app:
            return

        self.logger.info("Stopping OpenCanvas workflow server")

        try:
            if self.site:
                await self.site.stop()
                self.site = None

            if self.runner:
                await self.runner.cleanup()
                self.runner = None

            self.app = None

            self.logger.info("OpenCanvas workflow server stopped")
        except Exception as e:
            self.logger.exception(f"Error stopping OpenCanvas workflow server: {e}")

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

    async def handle_workflows(self, request: web.Request) -> web.Response:
        """Handle the workflows page request.

        Args:
            request: The HTTP request.

        Returns:
            The HTTP response.
        """
        # Read the workflows.html template
        workflows_path = self.templates_dir / 'workflows.html'
        with open(workflows_path, 'r') as f:
            content = f.read()

        return web.Response(text=content, content_type='text/html')

    async def handle_editor(self, request: web.Request) -> web.Response:
        """Handle the editor page request.

        Args:
            request: The HTTP request.

        Returns:
            The HTTP response.
        """
        # Read the editor.html template
        editor_path = self.templates_dir / 'editor.html'
        with open(editor_path, 'r') as f:
            content = f.read()

        return web.Response(text=content, content_type='text/html')

    async def handle_api_workflows_get(self, request: web.Request) -> web.Response:
        """Handle the GET /api/workflows request.

        Args:
            request: The HTTP request.

        Returns:
            The HTTP response.
        """
        # Return all workflows
        return web.json_response({
            "success": True,
            "workflows": list(self.workflows.values())
        })

    async def handle_api_workflow_get(self, request: web.Request) -> web.Response:
        """Handle the GET /api/workflows/{workflow_id} request.

        Args:
            request: The HTTP request.

        Returns:
            The HTTP response.
        """
        # Get the workflow ID from the URL
        workflow_id = request.match_info['workflow_id']

        # Check if the workflow exists
        if workflow_id not in self.workflows:
            return web.json_response({
                "success": False,
                "error": f"Workflow {workflow_id} not found"
            }, status=404)

        # Return the workflow
        return web.json_response({
            "success": True,
            "workflow": self.workflows[workflow_id]
        })

    async def handle_api_workflows_post(self, request: web.Request) -> web.Response:
        """Handle the POST /api/workflows request.

        Args:
            request: The HTTP request.

        Returns:
            The HTTP response.
        """
        try:
            # Parse the request body
            workflow = await request.json()

            # Validate the workflow
            if 'id' not in workflow:
                return web.json_response({
                    "success": False,
                    "error": "Workflow ID is required"
                }, status=400)

            # Save the workflow
            self.workflows[workflow['id']] = workflow

            # Save to file
            file_path = self.workflows_dir / f"{workflow['id']}.json"
            with open(file_path, 'w') as f:
                json.dump(workflow, f, indent=2)

            return web.json_response({
                "success": True,
                "workflow": workflow
            })
        except Exception as e:
            self.logger.exception(f"Error saving workflow: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def create_workflow(self, name: str, description: str) -> Dict[str, Any]:
        """Create a new workflow.

        Args:
            name: The name of the workflow.
            description: The description of the workflow.

        Returns:
            The created workflow.
        """
        # Create a new workflow
        workflow_id = str(int(time.time()))
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "created": time.time(),
            "updated": time.time(),
            "nodes": [],
            "connections": []
        }

        # Save the workflow
        self.workflows[workflow_id] = workflow

        # Save to file
        file_path = self.workflows_dir / f"{workflow_id}.json"
        with open(file_path, 'w') as f:
            json.dump(workflow, f, indent=2)

        return workflow

    async def cleanup(self) -> None:
        """Clean up resources used by the OpenCanvas workflow."""
        self.logger.info("Cleaning up OpenCanvas workflow")

        # Stop the server
        await self.stop_server()

        self.logger.info("OpenCanvas workflow cleaned up")
        # Create CSS file
        css_file = self.static_dir / 'style.css'
        with open(css_file, 'w') as f:
            f.write("""
/* OpenCanvas workflow styles */
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

.workflow-canvas {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-top: 20px;
    min-height: 600px;
    position: relative;
}

.node {
    position: absolute;
    width: 150px;
    height: 80px;
    background-color: #3498db;
    color: white;
    border-radius: 8px;
    padding: 10px;
    cursor: move;
    user-select: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.node-agent {
    background-color: #3498db;
}

.node-tool {
    background-color: #2ecc71;
}

.node-data {
    background-color: #e74c3c;
}

.node-output {
    background-color: #f39c12;
}

.node-title {
    font-weight: bold;
    margin-bottom: 5px;
}

.node-type {
    font-size: 0.8rem;
    opacity: 0.8;
}

.connection {
    position: absolute;
    background-color: #7f8c8d;
    height: 2px;
    transform-origin: 0 0;
    z-index: -1;
}

.connection-point {
    position: absolute;
    width: 10px;
    height: 10px;
    background-color: #7f8c8d;
    border-radius: 50%;
    cursor: pointer;
}

.connection-point-input {
    top: -5px;
    left: 50%;
    transform: translateX(-50%);
}

.connection-point-output {
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
}

.toolbar {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.toolbar button {
    padding: 8px 16px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.toolbar button:hover {
    background-color: #2980b9;
}

.properties-panel {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-top: 20px;
}

.properties-panel h2 {
    margin-top: 0;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    font-size: 1.2rem;
}

.property-group {
    margin-bottom: 15px;
}

.property-label {
    font-weight: bold;
    margin-bottom: 5px;
}

.property-input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.workflow-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.workflow-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 20px;
    cursor: pointer;
    transition: transform 0.2s;
}

.workflow-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.workflow-card h3 {
    margin-top: 0;
    margin-bottom: 10px;
}

.workflow-card p {
    color: #7f8c8d;
    margin-bottom: 15px;
}

.workflow-card .workflow-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: #95a5a6;
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

    .workflow-list {
        grid-template-columns: 1fr;
    }
}
""")

        # Create JavaScript file
        js_file = self.static_dir / 'script.js'
        with open(js_file, 'w') as f:
            f.write("""
// OpenCanvas workflow scripts
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the workflow canvas
    initWorkflowCanvas();

    // Set up event listeners
    setupEventListeners();
});

let selectedNode = null;
let dragging = false;
let dragOffsetX = 0;
let dragOffsetY = 0;
let connecting = false;
let startConnectionNode = null;
let connections = [];

function initWorkflowCanvas() {
    // Load the workflow if one is selected
    const workflowId = getUrlParameter('id');
    if (workflowId) {
        loadWorkflow(workflowId);
    }
}

function setupEventListeners() {
    // Add node buttons
    document.getElementById('add-agent-node').addEventListener('click', function() {
        addNode('agent', 'New Agent', 100, 100);
    });

    document.getElementById('add-tool-node').addEventListener('click', function() {
        addNode('tool', 'New Tool', 100, 250);
    });

    document.getElementById('add-data-node').addEventListener('click', function() {
        addNode('data', 'New Data', 100, 400);
    });

    document.getElementById('add-output-node').addEventListener('click', function() {
        addNode('output', 'New Output', 300, 100);
    });

    // Save workflow button
    document.getElementById('save-workflow').addEventListener('click', function() {
        saveWorkflow();
    });

    // Canvas event listeners for dragging
    const canvas = document.getElementById('workflow-canvas');
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
}

function addNode(type, title, x, y) {
    const canvas = document.getElementById('workflow-canvas');
    const node = document.createElement('div');
    node.className = `node node-${type}`;
    node.dataset.type = type;
    node.dataset.id = Date.now().toString();
    node.style.left = `${x}px`;
    node.style.top = `${y}px`;

    node.innerHTML = `
        <div class="node-title">${title}</div>
        <div class="node-type">${type}</div>
        <div class="connection-point connection-point-input" data-node-id="${node.dataset.id}"></div>
        <div class="connection-point connection-point-output" data-node-id="${node.dataset.id}"></div>
    `;

    canvas.appendChild(node);

    // Add event listeners to connection points
    const inputPoint = node.querySelector('.connection-point-input');
    const outputPoint = node.querySelector('.connection-point-output');

    inputPoint.addEventListener('mousedown', startConnection);
    outputPoint.addEventListener('mousedown', startConnection);

    // Select the node
    selectNode(node);
}

function selectNode(node) {
    // Deselect previous node
    if (selectedNode) {
        selectedNode.classList.remove('selected');
    }

    // Select new node
    selectedNode = node;
    selectedNode.classList.add('selected');

    // Update properties panel
    updatePropertiesPanel(node);
}

function updatePropertiesPanel(node) {
    const panel = document.getElementById('properties-panel');
    const nodeType = node.dataset.type;
    const nodeId = node.dataset.id;
    const nodeTitle = node.querySelector('.node-title').textContent;

    let html = `
        <h2>Properties</h2>
        <div class="property-group">
            <div class="property-label">ID</div>
            <input type="text" class="property-input" id="property-id" value="${nodeId}" readonly>
        </div>
        <div class="property-group">
            <div class="property-label">Title</div>
            <input type="text" class="property-input" id="property-title" value="${nodeTitle}">
        </div>
        <div class="property-group">
            <div class="property-label">Type</div>
            <input type="text" class="property-input" id="property-type" value="${nodeType}" readonly>
        </div>
    `;

    // Add type-specific properties
    if (nodeType === 'agent') {
        html += `
            <div class="property-group">
                <div class="property-label">Agent Type</div>
                <select class="property-input" id="property-agent-type">
                    <option value="coding">Coding Agent</option>
                    <option value="design">Design Agent</option>
                    <option value="manufacturing">Manufacturing Agent</option>
                    <option value="ui">UI Agent</option>
                    <option value="iot">IoT Agent</option>
                </select>
            </div>
        `;
    } else if (nodeType === 'tool') {
        html += `
            <div class="property-group">
                <div class="property-label">Tool Type</div>
                <select class="property-input" id="property-tool-type">
                    <option value="code-generation">Code Generation</option>
                    <option value="3d-modeling">3D Modeling</option>
                    <option value="image-generation">Image Generation</option>
                    <option value="text-analysis">Text Analysis</option>
                </select>
            </div>
        `;
    }

    // Add apply button
    html += `
        <div class="property-group">
            <button id="apply-properties">Apply</button>
        </div>
    `;

    panel.innerHTML = html;

    // Add event listener to apply button
    document.getElementById('apply-properties').addEventListener('click', function() {
        applyProperties(node);
    });
}

function applyProperties(node) {
    // Update node title
    const title = document.getElementById('property-title').value;
    node.querySelector('.node-title').textContent = title;

    // Update type-specific properties
    const nodeType = node.dataset.type;
    if (nodeType === 'agent') {
        // Update agent type if needed
    } else if (nodeType === 'tool') {
        // Update tool type if needed
    }
}

function handleMouseDown(e) {
    // Check if we clicked on a node
    if (e.target.classList.contains('node') || e.target.parentElement.classList.contains('node')) {
        const node = e.target.classList.contains('node') ? e.target : e.target.parentElement;

        // Select the node
        selectNode(node);

        // Start dragging
        dragging = true;
        const rect = node.getBoundingClientRect();
        dragOffsetX = e.clientX - rect.left;
        dragOffsetY = e.clientY - rect.top;
    }
}

function handleMouseMove(e) {
    if (dragging && selectedNode) {
        // Move the node
        const canvas = document.getElementById('workflow-canvas');
        const canvasRect = canvas.getBoundingClientRect();

        const x = e.clientX - canvasRect.left - dragOffsetX;
        const y = e.clientY - canvasRect.top - dragOffsetY;

        selectedNode.style.left = `${x}px`;
        selectedNode.style.top = `${y}px`;

        // Update connections
        updateConnections();
    } else if (connecting) {
        // Update temporary connection line
        updateTemporaryConnection(e);
    }
}

function handleMouseUp(e) {
    if (dragging) {
        dragging = false;
    }

    if (connecting) {
        // Check if we're over a connection point
        const element = document.elementFromPoint(e.clientX, e.clientY);
        if (element && element.classList.contains('connection-point')) {
            // Create a connection
            createConnection(startConnectionNode, element);
        }

        // Remove temporary connection line
        removeTemporaryConnection();
        connecting = false;
        startConnectionNode = null;
    }
}

function startConnection(e) {
    e.stopPropagation();
    connecting = true;
    startConnectionNode = e.target;

    // Create temporary connection line
    createTemporaryConnection(e);
}

function createTemporaryConnection(e) {
    const canvas = document.getElementById('workflow-canvas');
    const temp = document.createElement('div');
    temp.id = 'temp-connection';
    temp.className = 'connection';
    canvas.appendChild(temp);

    // Position and size will be updated in updateTemporaryConnection
    updateTemporaryConnection(e);
}

function updateTemporaryConnection(e) {
    const temp = document.getElementById('temp-connection');
    if (!temp || !startConnectionNode) return;

    const canvas = document.getElementById('workflow-canvas');
    const canvasRect = canvas.getBoundingClientRect();

    const startRect = startConnectionNode.getBoundingClientRect();
    const startX = startRect.left + startRect.width / 2 - canvasRect.left;
    const startY = startRect.top + startRect.height / 2 - canvasRect.top;

    const endX = e.clientX - canvasRect.left;
    const endY = e.clientY - canvasRect.top;

    // Calculate length and angle
    const dx = endX - startX;
    const dy = endY - startY;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;

    // Update the connection line
    temp.style.width = `${length}px`;
    temp.style.left = `${startX}px`;
    temp.style.top = `${startY}px`;
    temp.style.transform = `rotate(${angle}deg)`;
}

function removeTemporaryConnection() {
    const temp = document.getElementById('temp-connection');
    if (temp) {
        temp.remove();
    }
}

function createConnection(startPoint, endPoint) {
    // Don't connect a point to itself
    if (startPoint === endPoint) return;

    // Don't connect two inputs or two outputs
    const startIsInput = startPoint.classList.contains('connection-point-input');
    const endIsInput = endPoint.classList.contains('connection-point-input');
    if (startIsInput && endIsInput) return;
    if (!startIsInput && !endIsInput) return;

    // Ensure start is always an output and end is always an input
    if (startIsInput) {
        const temp = startPoint;
        startPoint = endPoint;
        endPoint = temp;
    }

    // Get node IDs
    const startNodeId = startPoint.dataset.nodeId;
    const endNodeId = endPoint.dataset.nodeId;

    // Don't connect a node to itself
    if (startNodeId === endNodeId) return;

    // Check if connection already exists
    for (const conn of connections) {
        if (conn.startNodeId === startNodeId && conn.endNodeId === endNodeId) {
            return;
        }
    }

    // Create the connection object
    const connection = {
        id: Date.now().toString(),
        startNodeId: startNodeId,
        endNodeId: endNodeId,
        element: null
    };

    // Create the connection element
    const canvas = document.getElementById('workflow-canvas');
    const connElement = document.createElement('div');
    connElement.className = 'connection';
    connElement.dataset.id = connection.id;
    canvas.appendChild(connElement);

    connection.element = connElement;
    connections.push(connection);

    // Update the connection position
    updateConnection(connection);
}

function updateConnections() {
    for (const connection of connections) {
        updateConnection(connection);
    }
}

function updateConnection(connection) {
    const startNode = document.querySelector(`.node[data-id="${connection.startNodeId}"]`);
    const endNode = document.querySelector(`.node[data-id="${connection.endNodeId}"]`);

    if (!startNode || !endNode || !connection.element) return;

    const startPoint = startNode.querySelector('.connection-point-output');
    const endPoint = endNode.querySelector('.connection-point-input');

    const startRect = startPoint.getBoundingClientRect();
    const endRect = endPoint.getBoundingClientRect();
    const canvasRect = document.getElementById('workflow-canvas').getBoundingClientRect();

    const startX = startRect.left + startRect.width / 2 - canvasRect.left;
    const startY = startRect.top + startRect.height / 2 - canvasRect.top;
    const endX = endRect.left + endRect.width / 2 - canvasRect.left;
    const endY = endRect.top + endRect.height / 2 - canvasRect.top;

    // Calculate length and angle
    const dx = endX - startX;
    const dy = endY - startY;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;

    // Update the connection line
    connection.element.style.width = `${length}px`;
    connection.element.style.left = `${startX}px`;
    connection.element.style.top = `${startY}px`;
    connection.element.style.transform = `rotate(${angle}deg)`;
}

function saveWorkflow() {
    // Get workflow data
    const name = document.getElementById('workflow-name').value || 'Untitled Workflow';
    const description = document.getElementById('workflow-description').value || 'No description';

    // Get all nodes
    const nodes = [];
    document.querySelectorAll('.node').forEach(node => {
        nodes.push({
            id: node.dataset.id,
            type: node.dataset.type,
            title: node.querySelector('.node-title').textContent,
            x: parseInt(node.style.left),
            y: parseInt(node.style.top)
        });
    });

    // Get all connections
    const connectionData = connections.map(conn => ({
        id: conn.id,
        startNodeId: conn.startNodeId,
        endNodeId: conn.endNodeId
    }));

    // Create workflow data
    const workflow = {
        id: getUrlParameter('id') || Date.now().toString(),
        name: name,
        description: description,
        created: new Date().toISOString(),
        updated: new Date().toISOString(),
        nodes: nodes,
        connections: connectionData
    };

    // Send to server
    fetch('/api/workflows', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(workflow)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Workflow saved successfully!');
            // Redirect to workflow list if this is a new workflow
            if (!getUrlParameter('id')) {
                window.location.href = '/workflows';
            }
        } else {
            alert('Error saving workflow: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error saving workflow: ' + error);
    });
}

function loadWorkflow(workflowId) {
    fetch(`/api/workflows/${workflowId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const workflow = data.workflow;

            // Set workflow name and description
            document.getElementById('workflow-name').value = workflow.name;
            document.getElementById('workflow-description').value = workflow.description;

            // Clear canvas
            const canvas = document.getElementById('workflow-canvas');
            canvas.innerHTML = '';

            // Add nodes
            workflow.nodes.forEach(node => {
                addNode(node.type, node.title, node.x, node.y);
                // Update node ID to match saved ID
                const nodeElement = document.querySelector(`.node:last-child`);
                nodeElement.dataset.id = node.id;
            });

            // Add connections
            connections = [];
            workflow.connections.forEach(conn => {
                const startPoint = document.querySelector(`.node[data-id="${conn.startNodeId}"] .connection-point-output`);
                const endPoint = document.querySelector(`.node[data-id="${conn.endNodeId}"] .connection-point-input`);
                if (startPoint && endPoint) {
                    createConnection(startPoint, endPoint);
                }
            });
        } else {
            alert('Error loading workflow: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error loading workflow: ' + error);
    });
}

function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}
""")
