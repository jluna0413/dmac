import * as vscode from 'vscode';
import { DeepReasoningManager, ReasoningChain, ReasoningStep } from './deep-reasoning';
import { formatDate } from './utils';

/**
 * Deep reasoning panel
 */
export class DeepReasoningPanel {
    public static readonly viewType = 'macoder.deepReasoningPanel';
    
    private panel: vscode.WebviewPanel;
    private reasoningManager: DeepReasoningManager;
    private disposables: vscode.Disposable[] = [];
    private activeChainId: string | null = null;
    private mode: 'chains' | 'chain' = 'chains';
    
    /**
     * Create a new DeepReasoningPanel
     * 
     * @param extensionUri The extension URI
     * @param reasoningManager The deep reasoning manager
     */
    private constructor(
        private readonly extensionUri: vscode.Uri,
        reasoningManager: DeepReasoningManager
    ) {
        this.reasoningManager = reasoningManager;
        
        // Create the webview panel
        this.panel = vscode.window.createWebviewPanel(
            DeepReasoningPanel.viewType,
            'MaCoder Deep Reasoning',
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
                    case 'createChain':
                        this.createChain(message.topic, message.description);
                        return;
                    case 'openChain':
                        this.openChain(message.chainId);
                        return;
                    case 'updateChain':
                        this.updateChain(message.chainId, message.updates);
                        return;
                    case 'deleteChain':
                        this.deleteChain(message.chainId);
                        return;
                    case 'addStep':
                        this.addStep(message.chainId, message.content, message.type);
                        return;
                    case 'performReasoning':
                        this.performReasoning(message.problem, message.context);
                        return;
                    case 'showChains':
                        this.showChains();
                        return;
                }
            },
            null,
            this.disposables
        );
        
        // Listen for chain updates
        this.reasoningManager.onChainUpdated(chain => {
            if (this.mode === 'chains') {
                this.updateChainsList();
            } else if (this.mode === 'chain' && this.activeChainId === chain.id) {
                this.updateChainView(chain);
            }
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
     * Create or show the deep reasoning panel
     * 
     * @param extensionUri The extension URI
     * @param reasoningManager The deep reasoning manager
     */
    public static createOrShow(extensionUri: vscode.Uri, reasoningManager: DeepReasoningManager): DeepReasoningPanel {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
            
        // If we already have a panel, show it
        if (DeepReasoningPanel.currentPanel) {
            DeepReasoningPanel.currentPanel.panel.reveal(column);
            return DeepReasoningPanel.currentPanel;
        }
        
        // Otherwise, create a new panel
        DeepReasoningPanel.currentPanel = new DeepReasoningPanel(extensionUri, reasoningManager);
        return DeepReasoningPanel.currentPanel;
    }
    
    /**
     * Current panel instance
     */
    private static currentPanel: DeepReasoningPanel | undefined;
    
    /**
     * Create a new chain
     * 
     * @param topic The chain topic
     * @param description The chain description
     */
    private createChain(topic: string, description: string): void {
        try {
            const chain = this.reasoningManager.createChain(topic, description);
            this.openChain(chain.id);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create chain: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Open a chain
     * 
     * @param chainId The chain ID
     */
    private openChain(chainId: string): void {
        try {
            const chain = this.reasoningManager.getChain(chainId);
            if (!chain) {
                throw new Error('Chain not found');
            }
            
            this.activeChainId = chainId;
            this.mode = 'chain';
            this.updateChainView(chain);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open chain: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Update a chain
     * 
     * @param chainId The chain ID
     * @param updates The updates to apply
     */
    private updateChain(chainId: string, updates: Partial<ReasoningChain>): void {
        try {
            const success = this.reasoningManager.updateChain(chainId, updates);
            if (!success) {
                throw new Error('Failed to update chain');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update chain: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Delete a chain
     * 
     * @param chainId The chain ID
     */
    private deleteChain(chainId: string): void {
        try {
            const success = this.reasoningManager.deleteChain(chainId);
            if (!success) {
                throw new Error('Failed to delete chain');
            }
            
            // If this is the active chain, go back to chains list
            if (this.activeChainId === chainId) {
                this.showChains();
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to delete chain: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Add a step to a chain
     * 
     * @param chainId The chain ID
     * @param content The step content
     * @param type The step type
     */
    private addStep(
        chainId: string,
        content: string,
        type: 'observation' | 'thought' | 'action' | 'conclusion'
    ): void {
        try {
            const step = this.reasoningManager.addStep(chainId, content, type);
            if (!step) {
                throw new Error('Failed to add step');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to add step: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Perform reasoning on a problem
     * 
     * @param problem The problem to reason about
     * @param context Additional context
     */
    private async performReasoning(problem: string, context: string): Promise<void> {
        try {
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Performing deep reasoning...',
                    cancellable: false
                },
                async () => {
                    const chain = await this.reasoningManager.performReasoning(problem, context);
                    this.openChain(chain.id);
                }
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to perform reasoning: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Show the chains list
     */
    private showChains(): void {
        this.activeChainId = null;
        this.mode = 'chains';
        this.updateChainsList();
    }
    
    /**
     * Update the webview content
     */
    private updateWebview(): void {
        switch (this.mode) {
            case 'chains':
                this.updateChainsList();
                break;
            case 'chain':
                if (this.activeChainId) {
                    const chain = this.reasoningManager.getChain(this.activeChainId);
                    if (chain) {
                        this.updateChainView(chain);
                    } else {
                        this.showChains();
                    }
                } else {
                    this.showChains();
                }
                break;
        }
    }
    
    /**
     * Update the chains list
     */
    private updateChainsList(): void {
        const chains = this.reasoningManager.getAllChains();
        
        this.panel.webview.postMessage({
            command: 'updateChainsList',
            chains
        });
    }
    
    /**
     * Update the chain view
     * 
     * @param chain The chain to view
     */
    private updateChainView(chain: ReasoningChain): void {
        this.panel.webview.postMessage({
            command: 'updateChainView',
            chain
        });
    }
    
    /**
     * Get the HTML for the webview
     */
    private getHtmlForWebview(): string {
        // Get the local path to main script and stylesheet
        const scriptUri = this.panel.webview.asWebviewUri(
            vscode.Uri.joinPath(this.extensionUri, 'media', 'deep-reasoning-panel.js')
        );
        
        const styleUri = this.panel.webview.asWebviewUri(
            vscode.Uri.joinPath(this.extensionUri, 'media', 'deep-reasoning-panel.css')
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
            <title>MaCoder Deep Reasoning</title>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MaCoder Deep Reasoning</h1>
                </div>
                
                <div id="chainsView" class="view">
                    <div class="chains-header">
                        <h2>Reasoning Chains</h2>
                        <button id="newChainButton" class="primary-button">New Chain</button>
                    </div>
                    
                    <div id="chainsList" class="chains-list">
                        <div class="empty-state">No reasoning chains yet</div>
                    </div>
                    
                    <div class="reasoning-form">
                        <h2>Perform Deep Reasoning</h2>
                        <div class="form-group">
                            <label for="problemInput">Problem:</label>
                            <textarea id="problemInput" placeholder="Describe the problem you want to reason about..."></textarea>
                        </div>
                        <div class="form-group">
                            <label for="contextInput">Context (optional):</label>
                            <textarea id="contextInput" placeholder="Provide any additional context..."></textarea>
                        </div>
                        <button id="performReasoningButton" class="primary-button">Perform Reasoning</button>
                    </div>
                </div>
                
                <div id="chainView" class="view hidden">
                    <div class="chain-header">
                        <button id="backToChainsButton" class="back-button">← Back to Chains</button>
                        <h2 id="chainTitle">Chain Title</h2>
                    </div>
                    
                    <div id="chainDescription" class="chain-description"></div>
                    
                    <div class="steps-header">
                        <h3>Reasoning Steps</h3>
                        <button id="addStepButton" class="secondary-button">Add Step</button>
                    </div>
                    
                    <div id="stepsList" class="steps-list">
                        <div class="empty-state">No steps yet</div>
                    </div>
                    
                    <div id="conclusionSection" class="conclusion-section hidden">
                        <h3>Conclusion</h3>
                        <div id="conclusionContent" class="conclusion-content"></div>
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
        DeepReasoningPanel.currentPanel = undefined;
        
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
