const vscode = require('vscode');
const axios = require('axios');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('DMac extension is now active');

    // Get configuration
    const config = vscode.workspace.getConfiguration('dmac');
    const serverUrl = config.get('serverUrl');

    // Register commands
    const startAgentCommand = vscode.commands.registerCommand('dmac.startAgent', async () => {
        try {
            // Show quick pick to select agent type
            const agentType = await vscode.window.showQuickPick(
                ['Code Assistant', 'Web Researcher', 'Task Executor', 'WebArena Agent'],
                { placeHolder: 'Select agent type' }
            );

            if (!agentType) return;

            // Show input box to name the agent
            const agentName = await vscode.window.showInputBox({
                placeHolder: 'Enter a name for your agent',
                value: `${agentType.replace(' ', '')}_${new Date().getTime().toString().slice(-4)}`
            });

            if (!agentName) return;

            // Create the agent
            const response = await axios.post(`${serverUrl}/api/agents`, {
                name: agentName,
                type: agentType.toLowerCase().replace(' ', '_')
            });

            if (response.data && response.data.success) {
                vscode.window.showInformationMessage(`Agent "${agentName}" created successfully!`);
                // Refresh the agents view
                vscode.commands.executeCommand('dmacAgents.refresh');
            } else {
                vscode.window.showErrorMessage(`Failed to create agent: ${response.data.error || 'Unknown error'}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error creating agent: ${error.message}`);
        }
    });

    const chatCommand = vscode.commands.registerCommand('dmac.chat', async () => {
        // Create and show a new webview panel
        const panel = vscode.window.createWebviewPanel(
            'dmacChat',
            'DMac Chat',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        // Set the HTML content
        panel.webview.html = getChatWebviewContent(serverUrl);

        // Handle messages from the webview
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'sendMessage':
                        try {
                            const response = await axios.post(`${serverUrl}/api/chat/message`, {
                                message: message.text,
                                model: message.model || config.get('defaultModel')
                            });

                            if (response.data && response.data.success) {
                                panel.webview.postMessage({
                                    command: 'receiveMessage',
                                    text: response.data.response,
                                    sender: 'assistant'
                                });
                            } else {
                                panel.webview.postMessage({
                                    command: 'receiveMessage',
                                    text: `Error: ${response.data.error || 'Unknown error'}`,
                                    sender: 'system'
                                });
                            }
                        } catch (error) {
                            panel.webview.postMessage({
                                command: 'receiveMessage',
                                text: `Error: ${error.message}`,
                                sender: 'system'
                            });
                        }
                        break;
                }
            },
            undefined,
            context.subscriptions
        );
    });

    const generateCodeCommand = vscode.commands.registerCommand('dmac.generateCode', async () => {
        // Show input box for code generation prompt
        const prompt = await vscode.window.showInputBox({
            placeHolder: 'Describe the code you want to generate',
            prompt: 'Enter a description of the code you want to generate'
        });

        if (!prompt) return;

        try {
            // Get the active editor
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor found');
                return;
            }

            // Get the current file language
            const language = editor.document.languageId;

            // Show progress indicator
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Generating code...',
                cancellable: false
            }, async (progress) => {
                try {
                    // Call the API to generate code
                    const response = await axios.post(`${serverUrl}/api/code/generate`, {
                        prompt,
                        language,
                        model: config.get('defaultModel')
                    });

                    if (response.data && response.data.success) {
                        // Insert the generated code at the cursor position
                        editor.edit(editBuilder => {
                            editBuilder.insert(editor.selection.active, response.data.code);
                        });
                    } else {
                        vscode.window.showErrorMessage(`Failed to generate code: ${response.data.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    vscode.window.showErrorMessage(`Error generating code: ${error.message}`);
                }
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });

    const explainCodeCommand = vscode.commands.registerCommand('dmac.explainCode', async () => {
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        // Get the selected text
        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);

        if (!selectedText) {
            vscode.window.showErrorMessage('No code selected');
            return;
        }

        try {
            // Show progress indicator
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Analyzing code...',
                cancellable: false
            }, async (progress) => {
                try {
                    // Call the API to explain code
                    const response = await axios.post(`${serverUrl}/api/code/explain`, {
                        code: selectedText,
                        language: editor.document.languageId,
                        model: config.get('defaultModel')
                    });

                    if (response.data && response.data.success) {
                        // Show the explanation in a new webview panel
                        const panel = vscode.window.createWebviewPanel(
                            'dmacCodeExplanation',
                            'Code Explanation',
                            vscode.ViewColumn.Beside,
                            { enableScripts: true }
                        );

                        panel.webview.html = getExplanationWebviewContent(selectedText, response.data.explanation);
                    } else {
                        vscode.window.showErrorMessage(`Failed to explain code: ${response.data.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    vscode.window.showErrorMessage(`Error explaining code: ${error.message}`);
                }
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });

    const optimizeCodeCommand = vscode.commands.registerCommand('dmac.optimizeCode', async () => {
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        // Get the selected text
        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);

        if (!selectedText) {
            vscode.window.showErrorMessage('No code selected');
            return;
        }

        try {
            // Show progress indicator
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Optimizing code...',
                cancellable: false
            }, async (progress) => {
                try {
                    // Call the API to optimize code
                    const response = await axios.post(`${serverUrl}/api/code/optimize`, {
                        code: selectedText,
                        language: editor.document.languageId,
                        model: config.get('defaultModel')
                    });

                    if (response.data && response.data.success) {
                        // Show diff view
                        const optimizedCode = response.data.optimizedCode;
                        
                        // Create a new untitled document with the optimized code
                        const document = await vscode.workspace.openTextDocument({
                            content: optimizedCode,
                            language: editor.document.languageId
                        });
                        
                        await vscode.window.showTextDocument(document, vscode.ViewColumn.Beside);
                        
                        // Show apply button
                        const apply = await vscode.window.showInformationMessage(
                            'Code optimization complete. Would you like to apply these changes?',
                            'Apply',
                            'Cancel'
                        );
                        
                        if (apply === 'Apply') {
                            editor.edit(editBuilder => {
                                editBuilder.replace(selection, optimizedCode);
                            });
                        }
                    } else {
                        vscode.window.showErrorMessage(`Failed to optimize code: ${response.data.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    vscode.window.showErrorMessage(`Error optimizing code: ${error.message}`);
                }
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });

    const debugCodeCommand = vscode.commands.registerCommand('dmac.debugCode', async () => {
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        // Get the selected text
        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);

        if (!selectedText) {
            vscode.window.showErrorMessage('No code selected');
            return;
        }

        try {
            // Show progress indicator
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Debugging code...',
                cancellable: false
            }, async (progress) => {
                try {
                    // Call the API to debug code
                    const response = await axios.post(`${serverUrl}/api/code/debug`, {
                        code: selectedText,
                        language: editor.document.languageId,
                        model: config.get('defaultModel')
                    });

                    if (response.data && response.data.success) {
                        // Show the debug results in a new webview panel
                        const panel = vscode.window.createWebviewPanel(
                            'dmacCodeDebug',
                            'Code Debug Results',
                            vscode.ViewColumn.Beside,
                            { enableScripts: true }
                        );

                        panel.webview.html = getDebugWebviewContent(selectedText, response.data.issues, response.data.fixedCode);
                        
                        // Handle messages from the webview
                        panel.webview.onDidReceiveMessage(
                            async message => {
                                if (message.command === 'applyFix') {
                                    editor.edit(editBuilder => {
                                        editBuilder.replace(selection, message.fixedCode);
                                    });
                                }
                            },
                            undefined,
                            context.subscriptions
                        );
                    } else {
                        vscode.window.showErrorMessage(`Failed to debug code: ${response.data.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    vscode.window.showErrorMessage(`Error debugging code: ${error.message}`);
                }
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });

    // Register the commands
    context.subscriptions.push(startAgentCommand);
    context.subscriptions.push(chatCommand);
    context.subscriptions.push(generateCodeCommand);
    context.subscriptions.push(explainCodeCommand);
    context.subscriptions.push(optimizeCodeCommand);
    context.subscriptions.push(debugCodeCommand);

    // Create the agents tree view provider
    const agentsProvider = new AgentsTreeDataProvider(serverUrl);
    vscode.window.registerTreeDataProvider('dmacAgents', agentsProvider);
    
    // Register a command to refresh the agents view
    const refreshAgentsCommand = vscode.commands.registerCommand('dmacAgents.refresh', () => {
        agentsProvider.refresh();
    });
    
    context.subscriptions.push(refreshAgentsCommand);
}

// This method is called when your extension is deactivated
function deactivate() {}

// Helper function to get the chat webview content
function getChatWebviewContent(serverUrl) {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DMac Chat</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                padding: 0;
                margin: 0;
                display: flex;
                flex-direction: column;
                height: 100vh;
                color: var(--vscode-editor-foreground);
                background-color: var(--vscode-editor-background);
            }
            .chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
            }
            .message {
                margin-bottom: 16px;
                padding: 12px;
                border-radius: 8px;
                max-width: 80%;
            }
            .user-message {
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                align-self: flex-end;
                margin-left: auto;
            }
            .assistant-message {
                background-color: var(--vscode-editor-inactiveSelectionBackground);
                color: var(--vscode-editor-foreground);
                align-self: flex-start;
            }
            .system-message {
                background-color: var(--vscode-editorError-foreground);
                color: white;
                align-self: center;
                margin: 0 auto;
                text-align: center;
            }
            .input-container {
                display: flex;
                padding: 16px;
                border-top: 1px solid var(--vscode-panel-border);
            }
            #message-input {
                flex: 1;
                padding: 8px;
                border: 1px solid var(--vscode-input-border);
                border-radius: 4px;
                background-color: var(--vscode-input-background);
                color: var(--vscode-input-foreground);
                margin-right: 8px;
            }
            #send-button {
                padding: 8px 16px;
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            #send-button:hover {
                background-color: var(--vscode-button-hoverBackground);
            }
            .model-selector {
                margin-bottom: 16px;
                display: flex;
                align-items: center;
            }
            .model-selector label {
                margin-right: 8px;
            }
            #model-select {
                padding: 4px;
                background-color: var(--vscode-dropdown-background);
                color: var(--vscode-dropdown-foreground);
                border: 1px solid var(--vscode-dropdown-border);
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="model-selector">
            <label for="model-select">Model:</label>
            <select id="model-select">
                <option value="gemma3:12b">Gemma 3 (12B)</option>
                <option value="llama3:8b">Llama 3 (8B)</option>
                <option value="mistral:7b">Mistral (7B)</option>
                <option value="gemini-pro">Gemini Pro</option>
            </select>
        </div>
        <div class="chat-container" id="chat-container">
            <div class="message assistant-message">
                Hello! I'm DMac AI Assistant. How can I help you today?
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="message-input" placeholder="Type your message here...">
            <button id="send-button">Send</button>
        </div>
        <script>
            (function() {
                const vscode = acquireVsCodeApi();
                const chatContainer = document.getElementById('chat-container');
                const messageInput = document.getElementById('message-input');
                const sendButton = document.getElementById('send-button');
                const modelSelect = document.getElementById('model-select');

                // Function to add a message to the chat
                function addMessage(text, sender) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = \`message \${sender}-message\`;
                    messageDiv.textContent = text;
                    chatContainer.appendChild(messageDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }

                // Handle send button click
                sendButton.addEventListener('click', sendMessage);

                // Handle Enter key press
                messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });

                // Function to send a message
                function sendMessage() {
                    const text = messageInput.value.trim();
                    if (!text) return;

                    // Add user message to chat
                    addMessage(text, 'user');

                    // Clear input
                    messageInput.value = '';

                    // Send message to extension
                    vscode.postMessage({
                        command: 'sendMessage',
                        text: text,
                        model: modelSelect.value
                    });
                }

                // Handle messages from the extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.command) {
                        case 'receiveMessage':
                            addMessage(message.text, message.sender);
                            break;
                    }
                });
            }());
        </script>
    </body>
    </html>`;
}

// Helper function to get the explanation webview content
function getExplanationWebviewContent(code, explanation) {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Explanation</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                padding: 16px;
                color: var(--vscode-editor-foreground);
                background-color: var(--vscode-editor-background);
            }
            .code-container {
                background-color: var(--vscode-editor-inactiveSelectionBackground);
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 16px;
                white-space: pre-wrap;
                font-family: 'Courier New', Courier, monospace;
                overflow-x: auto;
            }
            .explanation-container {
                background-color: var(--vscode-editor-inactiveSelectionBackground);
                padding: 16px;
                border-radius: 8px;
                white-space: pre-wrap;
            }
            h2 {
                color: var(--vscode-editor-foreground);
                border-bottom: 1px solid var(--vscode-panel-border);
                padding-bottom: 8px;
            }
        </style>
    </head>
    <body>
        <h2>Original Code</h2>
        <div class="code-container">${escapeHtml(code)}</div>
        
        <h2>Explanation</h2>
        <div class="explanation-container">${formatExplanation(explanation)}</div>
    </body>
    </html>`;
}

// Helper function to get the debug webview content
function getDebugWebviewContent(code, issues, fixedCode) {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Debug Results</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                padding: 16px;
                color: var(--vscode-editor-foreground);
                background-color: var(--vscode-editor-background);
            }
            .code-container {
                background-color: var(--vscode-editor-inactiveSelectionBackground);
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 16px;
                white-space: pre-wrap;
                font-family: 'Courier New', Courier, monospace;
                overflow-x: auto;
            }
            .issues-container {
                margin-bottom: 16px;
            }
            .issue {
                background-color: var(--vscode-editor-inactiveSelectionBackground);
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
            }
            .issue-title {
                font-weight: bold;
                color: var(--vscode-editorError-foreground);
                margin-bottom: 4px;
            }
            .fixed-code-container {
                background-color: var(--vscode-editor-inactiveSelectionBackground);
                padding: 16px;
                border-radius: 8px;
                white-space: pre-wrap;
                font-family: 'Courier New', Courier, monospace;
                overflow-x: auto;
                margin-bottom: 16px;
            }
            h2 {
                color: var(--vscode-editor-foreground);
                border-bottom: 1px solid var(--vscode-panel-border);
                padding-bottom: 8px;
            }
            .button-container {
                display: flex;
                justify-content: flex-end;
            }
            #apply-button {
                padding: 8px 16px;
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            #apply-button:hover {
                background-color: var(--vscode-button-hoverBackground);
            }
        </style>
    </head>
    <body>
        <h2>Original Code</h2>
        <div class="code-container">${escapeHtml(code)}</div>
        
        <h2>Issues Found</h2>
        <div class="issues-container">
            ${formatIssues(issues)}
        </div>
        
        <h2>Fixed Code</h2>
        <div class="fixed-code-container">${escapeHtml(fixedCode)}</div>
        
        <div class="button-container">
            <button id="apply-button">Apply Fix</button>
        </div>
        
        <script>
            (function() {
                const vscode = acquireVsCodeApi();
                const applyButton = document.getElementById('apply-button');
                
                applyButton.addEventListener('click', () => {
                    vscode.postMessage({
                        command: 'applyFix',
                        fixedCode: ${JSON.stringify(fixedCode)}
                    });
                });
            }());
        </script>
    </body>
    </html>`;
}

// Helper function to escape HTML
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Helper function to format explanation text
function formatExplanation(text) {
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

// Helper function to format issues
function formatIssues(issues) {
    if (!issues || issues.length === 0) {
        return '<div class="issue">No issues found.</div>';
    }
    
    return issues.map(issue => `
        <div class="issue">
            <div class="issue-title">${issue.title}</div>
            <div class="issue-description">${issue.description}</div>
        </div>
    `).join('');
}

// Agents tree data provider
class AgentsTreeDataProvider {
    constructor(serverUrl) {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.serverUrl = serverUrl;
    }

    refresh() {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element) {
        return element;
    }

    async getChildren(element) {
        if (element) {
            return [];
        } else {
            try {
                const response = await axios.get(`${this.serverUrl}/api/agents`);
                if (response.data && response.data.agents) {
                    return response.data.agents.map(agent => {
                        const treeItem = new vscode.TreeItem(agent.name);
                        treeItem.description = agent.type;
                        treeItem.tooltip = `ID: ${agent.id}\nType: ${agent.type}`;
                        treeItem.contextValue = 'agent';
                        treeItem.iconPath = new vscode.ThemeIcon('robot');
                        return treeItem;
                    });
                }
                return [];
            } catch (error) {
                vscode.window.showErrorMessage(`Error fetching agents: ${error.message}`);
                return [];
            }
        }
    }
}

module.exports = {
    activate,
    deactivate
};
