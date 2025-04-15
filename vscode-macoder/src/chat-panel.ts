import * as vscode from 'vscode';
import { MaCoderApiClient } from './api-client';

/**
 * Message type for chat.
 */
interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
}

/**
 * Chat panel for MaCoder.
 */
export class ChatPanel {
    public static currentPanel: ChatPanel | undefined;
    private static readonly viewType = 'macoderChat';

    private readonly panel: vscode.WebviewPanel;
    private readonly extensionUri: vscode.Uri;
    private readonly apiClient: MaCoderApiClient;
    private messages: ChatMessage[] = [];
    private disposables: vscode.Disposable[] = [];

    /**
     * Create or show a chat panel.
     * 
     * @param extensionUri The URI of the extension
     * @param apiClient The API client
     */
    public static createOrShow(extensionUri: vscode.Uri, apiClient: MaCoderApiClient): ChatPanel {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it
        if (ChatPanel.currentPanel) {
            ChatPanel.currentPanel.panel.reveal(column);
            return ChatPanel.currentPanel;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            ChatPanel.viewType,
            'MaCoder Chat',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media')
                ]
            }
        );

        ChatPanel.currentPanel = new ChatPanel(panel, extensionUri, apiClient);
        return ChatPanel.currentPanel;
    }

    /**
     * Create a new chat panel.
     * 
     * @param panel The webview panel
     * @param extensionUri The URI of the extension
     * @param apiClient The API client
     */
    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, apiClient: MaCoderApiClient) {
        this.panel = panel;
        this.extensionUri = extensionUri;
        this.apiClient = apiClient;

        // Set the webview's initial html content
        this.updateWebview();

        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programmatically
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);

        // Handle messages from the webview
        this.panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'sendMessage':
                        await this.sendMessage(message.text);
                        break;
                    case 'clearChat':
                        this.clearChat();
                        break;
                    case 'applyCode':
                        this.applyCode(message.code);
                        break;
                }
            },
            null,
            this.disposables
        );

        // Add welcome message
        this.addMessage({
            role: 'system',
            content: 'Welcome to MaCoder Chat! How can I help you with your code today?',
            timestamp: Date.now()
        });
    }

    /**
     * Dispose of the chat panel.
     */
    public dispose() {
        ChatPanel.currentPanel = undefined;

        // Clean up resources
        this.panel.dispose();

        while (this.disposables.length) {
            const disposable = this.disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }

    /**
     * Send a message to the chat.
     * 
     * @param text The message text
     */
    private async sendMessage(text: string): Promise<void> {
        // Add user message
        this.addMessage({
            role: 'user',
            content: text,
            timestamp: Date.now()
        });

        try {
            // Show typing indicator
            this.panel.webview.postMessage({ command: 'showTyping' });

            // Get active editor information for context
            const editor = vscode.window.activeTextEditor;
            let fileContext = '';
            let language = '';
            
            if (editor) {
                const document = editor.document;
                fileContext = document.getText();
                language = document.languageId;
            }

            // Generate response using the API
            const response = await this.apiClient.generateCode(
                `User message: ${text}\n\nCurrent file context: ${fileContext ? fileContext.substring(0, 1000) + '...' : 'None'}`,
                language
            );

            // Add assistant message
            if (response.success) {
                this.addMessage({
                    role: 'assistant',
                    content: response.code || 'I generated some code for you, but it seems to be empty.',
                    timestamp: Date.now()
                });
            } else {
                this.addMessage({
                    role: 'assistant',
                    content: 'Sorry, I encountered an error while processing your request.',
                    timestamp: Date.now()
                });
            }
        } catch (error) {
            console.error('Error sending message:', error);
            
            // Add error message
            this.addMessage({
                role: 'assistant',
                content: 'Sorry, an error occurred while processing your message.',
                timestamp: Date.now()
            });
        } finally {
            // Hide typing indicator
            this.panel.webview.postMessage({ command: 'hideTyping' });
        }
    }

    /**
     * Add a message to the chat.
     * 
     * @param message The message to add
     */
    private addMessage(message: ChatMessage): void {
        this.messages.push(message);
        this.updateWebview();
    }

    /**
     * Clear the chat.
     */
    private clearChat(): void {
        this.messages = [];
        this.updateWebview();
    }

    /**
     * Apply code to the active editor.
     * 
     * @param code The code to apply
     */
    private applyCode(code: string): void {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            editor.edit((editBuilder) => {
                const selection = editor.selection;
                if (selection.isEmpty) {
                    // Insert at cursor position
                    editBuilder.insert(selection.active, code);
                } else {
                    // Replace selected text
                    editBuilder.replace(selection, code);
                }
            });
        }
    }

    /**
     * Update the webview content.
     */
    private updateWebview(): void {
        this.panel.webview.html = this.getHtmlForWebview();
    }

    /**
     * Get the HTML for the webview.
     * 
     * @returns The HTML for the webview
     */
    private getHtmlForWebview(): string {
        // Format messages as HTML
        const messagesHtml = this.messages.map((message) => {
            const date = new Date(message.timestamp);
            const timeString = date.toLocaleTimeString();
            
            // Format code blocks
            let content = message.content.replace(/```([\s\S]*?)```/g, (match, code) => {
                return `<pre><code>${this.escapeHtml(code)}</code></pre>
                        <button class="apply-code-button" data-code="${this.escapeHtml(code)}">Apply Code</button>`;
            });
            
            // Format inline code
            content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            // Format links
            content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
            
            // Format line breaks
            content = content.replace(/\n/g, '<br>');
            
            return `
                <div class="message ${message.role}">
                    <div class="message-header">
                        <span class="message-role">${message.role}</span>
                        <span class="message-time">${timeString}</span>
                    </div>
                    <div class="message-content">${content}</div>
                </div>
            `;
        }).join('');

        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>MaCoder Chat</title>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        font-size: var(--vscode-font-size);
                        color: var(--vscode-foreground);
                        background-color: var(--vscode-editor-background);
                        padding: 0;
                        margin: 0;
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                    }
                    .chat-container {
                        flex: 1;
                        overflow-y: auto;
                        padding: 16px;
                    }
                    .message {
                        margin-bottom: 16px;
                        padding: 12px;
                        border-radius: 6px;
                    }
                    .message.user {
                        background-color: var(--vscode-editor-inactiveSelectionBackground);
                        margin-left: 20%;
                    }
                    .message.assistant {
                        background-color: var(--vscode-editor-selectionBackground);
                        margin-right: 20%;
                    }
                    .message.system {
                        background-color: var(--vscode-badge-background);
                        color: var(--vscode-badge-foreground);
                        margin-left: 10%;
                        margin-right: 10%;
                    }
                    .message-header {
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 8px;
                        font-size: 0.8em;
                        opacity: 0.8;
                    }
                    .message-content {
                        white-space: pre-wrap;
                    }
                    pre {
                        background-color: var(--vscode-textCodeBlock-background);
                        padding: 8px;
                        border-radius: 4px;
                        overflow-x: auto;
                    }
                    code {
                        font-family: var(--vscode-editor-font-family);
                        font-size: var(--vscode-editor-font-size);
                    }
                    .input-container {
                        display: flex;
                        padding: 16px;
                        background-color: var(--vscode-editor-background);
                        border-top: 1px solid var(--vscode-panel-border);
                    }
                    #message-input {
                        flex: 1;
                        padding: 8px;
                        border: 1px solid var(--vscode-input-border);
                        background-color: var(--vscode-input-background);
                        color: var(--vscode-input-foreground);
                        border-radius: 4px;
                        resize: none;
                        min-height: 40px;
                        max-height: 120px;
                    }
                    #send-button {
                        margin-left: 8px;
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
                    .typing-indicator {
                        display: none;
                        padding: 12px;
                        margin-right: 20%;
                        border-radius: 6px;
                        background-color: var(--vscode-editor-selectionBackground);
                    }
                    .typing-indicator span {
                        display: inline-block;
                        width: 8px;
                        height: 8px;
                        border-radius: 50%;
                        background-color: var(--vscode-foreground);
                        margin-right: 4px;
                        animation: typing 1s infinite;
                    }
                    .typing-indicator span:nth-child(2) {
                        animation-delay: 0.2s;
                    }
                    .typing-indicator span:nth-child(3) {
                        animation-delay: 0.4s;
                    }
                    @keyframes typing {
                        0%, 100% { opacity: 0.3; }
                        50% { opacity: 1; }
                    }
                    .apply-code-button {
                        background-color: var(--vscode-button-secondaryBackground);
                        color: var(--vscode-button-secondaryForeground);
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        margin-top: 4px;
                        cursor: pointer;
                    }
                    .apply-code-button:hover {
                        background-color: var(--vscode-button-secondaryHoverBackground);
                    }
                    .toolbar {
                        display: flex;
                        justify-content: flex-end;
                        padding: 8px 16px;
                        background-color: var(--vscode-editor-background);
                        border-bottom: 1px solid var(--vscode-panel-border);
                    }
                    .toolbar button {
                        background-color: transparent;
                        color: var(--vscode-foreground);
                        border: none;
                        padding: 4px 8px;
                        cursor: pointer;
                        opacity: 0.8;
                    }
                    .toolbar button:hover {
                        opacity: 1;
                    }
                </style>
            </head>
            <body>
                <div class="toolbar">
                    <button id="clear-button">Clear Chat</button>
                </div>
                <div class="chat-container">
                    ${messagesHtml}
                    <div class="typing-indicator" id="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                <div class="input-container">
                    <textarea id="message-input" placeholder="Type a message..." rows="1"></textarea>
                    <button id="send-button">Send</button>
                </div>
                <script>
                    const vscode = acquireVsCodeApi();
                    const messageInput = document.getElementById('message-input');
                    const sendButton = document.getElementById('send-button');
                    const clearButton = document.getElementById('clear-button');
                    const typingIndicator = document.getElementById('typing-indicator');
                    const chatContainer = document.querySelector('.chat-container');
                    
                    // Auto-scroll to bottom
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
                    // Send message when clicking the send button
                    sendButton.addEventListener('click', () => {
                        sendMessage();
                    });
                    
                    // Send message when pressing Enter (without Shift)
                    messageInput.addEventListener('keydown', (event) => {
                        if (event.key === 'Enter' && !event.shiftKey) {
                            event.preventDefault();
                            sendMessage();
                        }
                    });
                    
                    // Clear chat when clicking the clear button
                    clearButton.addEventListener('click', () => {
                        vscode.postMessage({
                            command: 'clearChat'
                        });
                    });
                    
                    // Apply code when clicking an apply code button
                    document.addEventListener('click', (event) => {
                        if (event.target.classList.contains('apply-code-button')) {
                            const code = event.target.getAttribute('data-code');
                            vscode.postMessage({
                                command: 'applyCode',
                                code: code
                            });
                        }
                    });
                    
                    // Auto-resize textarea
                    messageInput.addEventListener('input', () => {
                        messageInput.style.height = 'auto';
                        messageInput.style.height = messageInput.scrollHeight + 'px';
                    });
                    
                    // Handle messages from the extension
                    window.addEventListener('message', (event) => {
                        const message = event.data;
                        switch (message.command) {
                            case 'showTyping':
                                typingIndicator.style.display = 'block';
                                chatContainer.scrollTop = chatContainer.scrollHeight;
                                break;
                            case 'hideTyping':
                                typingIndicator.style.display = 'none';
                                chatContainer.scrollTop = chatContainer.scrollHeight;
                                break;
                        }
                    });
                    
                    function sendMessage() {
                        const text = messageInput.value.trim();
                        if (text) {
                            vscode.postMessage({
                                command: 'sendMessage',
                                text: text
                            });
                            messageInput.value = '';
                            messageInput.style.height = 'auto';
                        }
                    }
                </script>
            </body>
            </html>
        `;
    }

    /**
     * Escape HTML special characters.
     * 
     * @param text The text to escape
     * @returns The escaped text
     */
    private escapeHtml(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}
