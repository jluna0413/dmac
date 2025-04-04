
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
    name = name.replace(/[\[]/, '\[').replace(/[\]]/, '\]');
    const regex = new RegExp('[\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}
