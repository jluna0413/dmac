import * as vscode from 'vscode';
import { AutonomousMode, Task, TaskStatus } from './autonomous-mode';
import { formatDate } from './utils';

/**
 * Autonomous mode panel
 */
export class AutonomousPanel {
    public static readonly viewType = 'macoder.autonomousPanel';
    
    private panel: vscode.WebviewPanel;
    private autonomousMode: AutonomousMode;
    private disposables: vscode.Disposable[] = [];
    
    /**
     * Create a new AutonomousPanel
     * 
     * @param extensionUri The extension URI
     * @param autonomousMode The autonomous mode
     */
    private constructor(
        private readonly extensionUri: vscode.Uri,
        autonomousMode: AutonomousMode
    ) {
        this.autonomousMode = autonomousMode;
        
        // Create the webview panel
        this.panel = vscode.window.createWebviewPanel(
            AutonomousPanel.viewType,
            'MaCoder Autonomous Mode',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media')
                ]
            }
        );
        
        // Set the webview's initial html content
        this.panel.webview.html = this.getHtmlForWebview();
        
        // Listen for messages from the webview
        this.panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'toggleAutonomousMode':
                        this.autonomousMode.toggle();
                        this.updateWebview();
                        return;
                    case 'executeTask':
                        this.executeTask(message.description);
                        return;
                    case 'cancelTask':
                        this.autonomousMode.cancelTask(message.taskId);
                        this.updateWebview();
                        return;
                }
            },
            null,
            this.disposables
        );
        
        // Listen for task updates
        this.autonomousMode.onTaskUpdated(() => {
            this.updateWebview();
        });
        
        // Update the webview when the panel becomes visible
        this.panel.onDidChangeViewState(
            e => {
                if (this.panel.visible) {
                    this.updateWebview();
                }
            },
            null,
            this.disposables
        );
        
        // Clean up resources when the panel is closed
        this.panel.onDidDispose(
            () => this.dispose(),
            null,
            this.disposables
        );
        
        // Initial update
        this.updateWebview();
    }
    
    /**
     * Create or show the autonomous panel
     * 
     * @param extensionUri The extension URI
     * @param autonomousMode The autonomous mode
     */
    public static createOrShow(extensionUri: vscode.Uri, autonomousMode: AutonomousMode): AutonomousPanel {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
            
        // If we already have a panel, show it
        if (AutonomousPanel.currentPanel) {
            AutonomousPanel.currentPanel.panel.reveal(column);
            return AutonomousPanel.currentPanel;
        }
        
        // Otherwise, create a new panel
        AutonomousPanel.currentPanel = new AutonomousPanel(extensionUri, autonomousMode);
        return AutonomousPanel.currentPanel;
    }
    
    /**
     * Current panel instance
     */
    private static currentPanel: AutonomousPanel | undefined;
    
    /**
     * Execute a task
     * 
     * @param description The task description
     */
    private async executeTask(description: string): Promise<void> {
        try {
            await this.autonomousMode.executeTask(description);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to execute task: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Update the webview content
     */
    private updateWebview(): void {
        // Get tasks
        const rootTasks = this.autonomousMode.getRootTasks();
        
        // Update the webview
        this.panel.webview.postMessage({
            command: 'updateTasks',
            tasks: rootTasks,
            isActive: this.autonomousMode.isActive(),
            activeTaskId: this.autonomousMode.getActiveTask()?.id
        });
    }
    
    /**
     * Get the HTML for the webview
     */
    private getHtmlForWebview(): string {
        // Get the local path to main script and stylesheet
        const scriptUri = this.panel.webview.asWebviewUri(
            vscode.Uri.joinPath(this.extensionUri, 'media', 'autonomous-panel.js')
        );
        
        const styleUri = this.panel.webview.asWebviewUri(
            vscode.Uri.joinPath(this.extensionUri, 'media', 'autonomous-panel.css')
        );
        
        // Use a nonce to only allow specific scripts to be run
        const nonce = getNonce();
        
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${this.panel.webview.cspSource}; script-src 'nonce-${nonce}';">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="${styleUri}" rel="stylesheet">
            <title>MaCoder Autonomous Mode</title>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MaCoder Autonomous Mode</h1>
                    <button id="toggleButton" class="toggle-button">Start</button>
                </div>
                
                <div class="task-form">
                    <h2>Create Task</h2>
                    <div class="form-group">
                        <label for="taskDescription">Task Description:</label>
                        <textarea id="taskDescription" placeholder="Describe what you want MaCoder to do..."></textarea>
                    </div>
                    <button id="executeButton" class="execute-button">Execute Task</button>
                </div>
                
                <div class="tasks-container">
                    <h2>Tasks</h2>
                    <div id="tasksList" class="tasks-list">
                        <div class="empty-state">No tasks yet</div>
                    </div>
                </div>
            </div>
            
            <script nonce="${nonce}" src="${scriptUri}"></script>
        </body>
        </html>`;
    }
    
    /**
     * Dispose the panel
     */
    public dispose(): void {
        AutonomousPanel.currentPanel = undefined;
        
        // Clean up resources
        this.panel.dispose();
        
        while (this.disposables.length) {
            const disposable = this.disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}

/**
 * Get a nonce
 */
function getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
