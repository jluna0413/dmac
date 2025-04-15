import * as vscode from 'vscode';

// Basic API client for communicating with LLM providers
class BasicApiClient {
    private modelName: string;

    constructor(modelName: string = 'default') {
        this.modelName = modelName;
    }

    async generateCompletion(prompt: string): Promise<string> {
        // In a real implementation, this would call an LLM API
        // For now, we'll just return a mock response
        return `Generated response for prompt: ${prompt}\nUsing model: ${this.modelName}`;
    }

    async explainCode(code: string): Promise<string> {
        return `Explanation for code:\n${code}\n\nThis code appears to be a simple example.`;
    }

    async refactorCode(code: string, instructions: string): Promise<string> {
        return `Refactored code based on instructions: ${instructions}\n\n${code}\n// Refactored with improved structure`;
    }

    async generateCode(instructions: string): Promise<string> {
        return `// Generated code based on: ${instructions}\nfunction example() {\n  console.log("Hello, world!");\n  // Implementation would go here\n}`;
    }
}

// Basic chat panel for interacting with the LLM
class ChatPanel {
    public static readonly viewType = 'macoder.chatPanel';
    private static currentPanel: ChatPanel | undefined;
    private readonly panel: vscode.WebviewPanel;
    private readonly apiClient: BasicApiClient;
    private disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, apiClient: BasicApiClient) {
        this.panel = panel;
        this.apiClient = apiClient;

        // Set the webview's initial html content
        this.updateWebview();

        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programmatically
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);

        // Handle messages from the webview
        this.panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'sendMessage':
                        const response = await this.apiClient.generateCompletion(message.text);
                        this.panel.webview.postMessage({ command: 'receiveMessage', text: response });
                        break;
                }
            },
            null,
            this.disposables
        );
    }

    public static createOrShow(extensionUri: vscode.Uri, apiClient: BasicApiClient) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it.
        if (ChatPanel.currentPanel) {
            ChatPanel.currentPanel.panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel.
        const panel = vscode.window.createWebviewPanel(
            ChatPanel.viewType,
            'MaCoder Chat',
            column || vscode.ViewColumn.One,
            {
                // Enable javascript in the webview
                enableScripts: true,
                // Restrict the webview to only loading content from our extension's directory
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        ChatPanel.currentPanel = new ChatPanel(panel, apiClient);
    }

    private updateWebview() {
        this.panel.webview.html = this.getHtmlForWebview();
    }

    private getHtmlForWebview() {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MaCoder Chat</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 0;
                    margin: 0;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                .container {
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .chat-container {
                    flex: 1;
                    overflow-y: auto;
                    margin-bottom: 20px;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                    padding: 10px;
                }
                .message {
                    margin-bottom: 10px;
                    padding: 10px;
                    border-radius: 4px;
                }
                .user-message {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    align-self: flex-end;
                }
                .bot-message {
                    background-color: var(--vscode-editor-selectionBackground);
                }
                .input-container {
                    display: flex;
                }
                #messageInput {
                    flex: 1;
                    padding: 8px;
                    border: 1px solid var(--vscode-input-border);
                    background-color: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border-radius: 4px;
                    margin-right: 10px;
                }
                button {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MaCoder Chat</h1>
                <div class="chat-container" id="chatContainer"></div>
                <div class="input-container">
                    <input type="text" id="messageInput" placeholder="Type your message here...">
                    <button id="sendButton">Send</button>
                </div>
            </div>
            <script>
                const vscode = acquireVsCodeApi();
                const chatContainer = document.getElementById('chatContainer');
                const messageInput = document.getElementById('messageInput');
                const sendButton = document.getElementById('sendButton');

                // Add a message to the chat
                function addMessage(text, isUser) {
                    const messageElement = document.createElement('div');
                    messageElement.className = isUser ? 'message user-message' : 'message bot-message';
                    messageElement.textContent = text;
                    chatContainer.appendChild(messageElement);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }

                // Send a message
                function sendMessage() {
                    const text = messageInput.value.trim();
                    if (text) {
                        addMessage(text, true);
                        vscode.postMessage({
                            command: 'sendMessage',
                            text
                        });
                        messageInput.value = '';
                    }
                }

                // Handle messages from the extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.command) {
                        case 'receiveMessage':
                            addMessage(message.text, false);
                            break;
                    }
                });

                // Event listeners
                sendButton.addEventListener('click', sendMessage);
                messageInput.addEventListener('keypress', event => {
                    if (event.key === 'Enter') {
                        sendMessage();
                    }
                });

                // Add welcome message
                addMessage('Welcome to MaCoder! How can I help you today?', false);
            </script>
        </body>
        </html>`;
    }

    private dispose() {
        ChatPanel.currentPanel = undefined;

        // Clean up our resources
        this.panel.dispose();

        while (this.disposables.length) {
            const x = this.disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
}

// Activate the extension
export function activate(context: vscode.ExtensionContext) {
    console.log('MaCoder extension is now active!');

    // Create API client
    const apiClient = new BasicApiClient();

    // Register commands
    const startChatCommand = vscode.commands.registerCommand('macoder.startChat', () => {
        ChatPanel.createOrShow(context.extensionUri, apiClient);
    });

    const generateCodeCommand = vscode.commands.registerCommand('macoder.generateCode', async () => {
        const instructions = await vscode.window.showInputBox({
            prompt: 'Enter instructions for code generation',
            placeHolder: 'Create a function that...'
        });

        if (!instructions) {
            return; // User cancelled
        }

        try {
            const generatedCode = await apiClient.generateCode(instructions);
            
            // Create a new document with the generated code
            const document = await vscode.workspace.openTextDocument({
                content: generatedCode,
                language: 'javascript' // Default to JavaScript
            });
            
            await vscode.window.showTextDocument(document);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate code: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    const explainCodeCommand = vscode.commands.registerCommand('macoder.explainCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        // Get selected code or entire document
        const selection = editor.selection;
        const code = selection.isEmpty
            ? editor.document.getText()
            : editor.document.getText(selection);

        if (!code) {
            vscode.window.showErrorMessage('No code to explain');
            return;
        }

        try {
            const explanation = await apiClient.explainCode(code);
            
            // Show explanation in a new document
            const document = await vscode.workspace.openTextDocument({
                content: explanation,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(document, vscode.ViewColumn.Beside);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to explain code: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    const refactorCodeCommand = vscode.commands.registerCommand('macoder.refactorCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        // Get selected code or entire document
        const selection = editor.selection;
        const code = selection.isEmpty
            ? editor.document.getText()
            : editor.document.getText(selection);

        if (!code) {
            vscode.window.showErrorMessage('No code to refactor');
            return;
        }

        // Get refactoring instructions
        const instructions = await vscode.window.showInputBox({
            prompt: 'Enter refactoring instructions',
            placeHolder: 'Improve performance, add comments, etc.'
        });

        if (!instructions) {
            return; // User cancelled
        }

        try {
            const refactoredCode = await apiClient.refactorCode(code, instructions);
            
            // Show refactored code in a new document
            const document = await vscode.workspace.openTextDocument({
                content: refactoredCode,
                language: editor.document.languageId
            });
            
            await vscode.window.showTextDocument(document, vscode.ViewColumn.Beside);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to refactor code: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    // Show information command (already implemented in the minimal version)
    const showInfoCommand = vscode.commands.registerCommand('macoder.showInfo', () => {
        vscode.window.showInformationMessage('MaCoder VS Code Extension v0.3.0-alpha');
    });

    // Add commands to subscriptions
    context.subscriptions.push(
        startChatCommand,
        generateCodeCommand,
        explainCodeCommand,
        refactorCodeCommand,
        showInfoCommand
    );
}

// Deactivate the extension
export function deactivate() {}
