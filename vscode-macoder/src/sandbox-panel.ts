import * as vscode from 'vscode';
import { LocalCodeSandbox, SandboxTest, SandboxResult } from './code-sandbox';

/**
 * Sandbox panel
 */
export class SandboxPanel {
    public static readonly viewType = 'macoder.sandboxPanel';
    
    private panel: vscode.WebviewPanel;
    private sandbox: LocalCodeSandbox;
    private disposables: vscode.Disposable[] = [];
    private activeTestId: string | null = null;
    private mode: 'tests' | 'test' | 'execute' = 'tests';
    
    /**
     * Create a new SandboxPanel
     * 
     * @param extensionUri The extension URI
     * @param sandbox The sandbox
     */
    private constructor(
        private readonly extensionUri: vscode.Uri,
        sandbox: LocalCodeSandbox
    ) {
        this.sandbox = sandbox;
        
        // Create the webview panel
        this.panel = vscode.window.createWebviewPanel(
            SandboxPanel.viewType,
            'MaCoder Sandbox',
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
                    case 'createTest':
                        this.createTest(message.name, message.code, message.language);
                        return;
                    case 'runTest':
                        this.runTest(message.testId);
                        return;
                    case 'openTest':
                        this.openTest(message.testId);
                        return;
                    case 'deleteTest':
                        this.deleteTest(message.testId);
                        return;
                    case 'executeCode':
                        this.executeCode(message.code, message.language);
                        return;
                    case 'showTests':
                        this.showTests();
                        return;
                    case 'showExecute':
                        this.showExecute();
                        return;
                }
            },
            null,
            this.disposables
        );
        
        // Listen for test updates
        this.sandbox.onTestCreated(test => {
            this.updateTestsList();
        });
        
        this.sandbox.onTestRun(test => {
            if (this.mode === 'test' && this.activeTestId === test.id) {
                this.updateTestView(test);
            }
        });
        
        this.sandbox.onTestDeleted(testId => {
            if (this.mode === 'test' && this.activeTestId === testId) {
                this.showTests();
            } else {
                this.updateTestsList();
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
     * Create or show the sandbox panel
     * 
     * @param extensionUri The extension URI
     * @param sandbox The sandbox
     */
    public static createOrShow(extensionUri: vscode.Uri, sandbox: LocalCodeSandbox): SandboxPanel {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
            
        // If we already have a panel, show it
        if (SandboxPanel.currentPanel) {
            SandboxPanel.currentPanel.panel.reveal(column);
            return SandboxPanel.currentPanel;
        }
        
        // Otherwise, create a new panel
        SandboxPanel.currentPanel = new SandboxPanel(extensionUri, sandbox);
        return SandboxPanel.currentPanel;
    }
    
    /**
     * Current panel instance
     */
    private static currentPanel: SandboxPanel | undefined;
    
    /**
     * Create a test
     * 
     * @param name The test name
     * @param code The test code
     * @param language The test language
     */
    private createTest(name: string, code: string, language: string): void {
        try {
            const test = this.sandbox.createTest(name, code, language);
            this.openTest(test.id);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create test: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Run a test
     * 
     * @param testId The test ID
     */
    private async runTest(testId: string): Promise<void> {
        try {
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Running test...',
                    cancellable: false
                },
                async () => {
                    await this.sandbox.runTest(testId);
                }
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to run test: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Open a test
     * 
     * @param testId The test ID
     */
    private openTest(testId: string): void {
        try {
            const test = this.sandbox.getTest(testId);
            if (!test) {
                throw new Error('Test not found');
            }
            
            this.activeTestId = testId;
            this.mode = 'test';
            this.updateTestView(test);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open test: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Delete a test
     * 
     * @param testId The test ID
     */
    private deleteTest(testId: string): void {
        try {
            const success = this.sandbox.deleteTest(testId);
            if (!success) {
                throw new Error('Failed to delete test');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to delete test: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Execute code
     * 
     * @param code The code to execute
     * @param language The language
     */
    private async executeCode(code: string, language: string): Promise<void> {
        try {
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Executing code...',
                    cancellable: false
                },
                async () => {
                    const result = await this.sandbox.executeCode(code, language);
                    this.updateExecuteResult(result);
                }
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to execute code: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
    
    /**
     * Show the tests list
     */
    private showTests(): void {
        this.activeTestId = null;
        this.mode = 'tests';
        this.updateTestsList();
    }
    
    /**
     * Show the execute view
     */
    private showExecute(): void {
        this.activeTestId = null;
        this.mode = 'execute';
        this.updateExecuteView();
    }
    
    /**
     * Update the webview content
     */
    private updateWebview(): void {
        switch (this.mode) {
            case 'tests':
                this.updateTestsList();
                break;
            case 'test':
                if (this.activeTestId) {
                    const test = this.sandbox.getTest(this.activeTestId);
                    if (test) {
                        this.updateTestView(test);
                    } else {
                        this.showTests();
                    }
                } else {
                    this.showTests();
                }
                break;
            case 'execute':
                this.updateExecuteView();
                break;
        }
    }
    
    /**
     * Update the tests list
     */
    private updateTestsList(): void {
        const tests = this.sandbox.getAllTests();
        
        this.panel.webview.postMessage({
            command: 'updateTestsList',
            tests
        });
    }
    
    /**
     * Update the test view
     * 
     * @param test The test to view
     */
    private updateTestView(test: SandboxTest): void {
        this.panel.webview.postMessage({
            command: 'updateTestView',
            test
        });
    }
    
    /**
     * Update the execute view
     */
    private updateExecuteView(): void {
        this.panel.webview.postMessage({
            command: 'updateExecuteView'
        });
    }
    
    /**
     * Update the execute result
     * 
     * @param result The execution result
     */
    private updateExecuteResult(result: SandboxResult): void {
        this.panel.webview.postMessage({
            command: 'updateExecuteResult',
            result
        });
    }
    
    /**
     * Get the HTML for the webview
     */
    private getHtmlForWebview(): string {
        // Get the local path to main script and stylesheet
        const scriptUri = this.panel.webview.asWebviewUri(
            vscode.Uri.joinPath(this.extensionUri, 'media', 'sandbox-panel.js')
        );
        
        const styleUri = this.panel.webview.asWebviewUri(
            vscode.Uri.joinPath(this.extensionUri, 'media', 'sandbox-panel.css')
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
            <title>MaCoder Sandbox</title>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MaCoder Sandbox</h1>
                    <div class="tabs">
                        <button id="testsTab" class="tab active">Tests</button>
                        <button id="executeTab" class="tab">Execute Code</button>
                    </div>
                </div>
                
                <div id="testsView" class="view">
                    <div class="tests-header">
                        <h2>Test Cases</h2>
                        <button id="newTestButton" class="primary-button">New Test</button>
                    </div>
                    
                    <div id="testsList" class="tests-list">
                        <div class="empty-state">No tests yet</div>
                    </div>
                </div>
                
                <div id="testView" class="view hidden">
                    <div class="test-header">
                        <button id="backToTestsButton" class="back-button">← Back to Tests</button>
                        <h2 id="testName">Test Name</h2>
                    </div>
                    
                    <div class="test-content">
                        <div class="test-code-section">
                            <h3>Code</h3>
                            <div class="language-label">Language: <span id="testLanguage">javascript</span></div>
                            <pre id="testCode" class="code-block"></pre>
                        </div>
                        
                        <div class="test-actions">
                            <button id="runTestButton" class="primary-button">Run Test</button>
                            <button id="deleteTestButton" class="secondary-button">Delete Test</button>
                        </div>
                        
                        <div id="testResultSection" class="test-result-section hidden">
                            <h3>Result</h3>
                            <div class="result-status">Status: <span id="testResultStatus">Success</span></div>
                            <div class="result-time">Execution Time: <span id="testResultTime">0</span> ms</div>
                            
                            <div class="result-output-section">
                                <h4>Output</h4>
                                <pre id="testResultOutput" class="result-output"></pre>
                            </div>
                            
                            <div id="testResultErrorSection" class="result-error-section hidden">
                                <h4>Error</h4>
                                <pre id="testResultError" class="result-error"></pre>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="executeView" class="view hidden">
                    <div class="execute-header">
                        <h2>Execute Code</h2>
                    </div>
                    
                    <div class="execute-content">
                        <div class="language-selection">
                            <label for="executeLanguage">Language:</label>
                            <select id="executeLanguage">
                                <option value="javascript">JavaScript</option>
                                <option value="typescript">TypeScript</option>
                                <option value="python">Python</option>
                                <option value="java">Java</option>
                                <option value="c">C</option>
                                <option value="cpp">C++</option>
                                <option value="csharp">C#</option>
                                <option value="go">Go</option>
                                <option value="ruby">Ruby</option>
                                <option value="php">PHP</option>
                                <option value="rust">Rust</option>
                                <option value="shell">Shell</option>
                                <option value="powershell">PowerShell</option>
                            </select>
                        </div>
                        
                        <div class="code-input-section">
                            <h3>Code</h3>
                            <textarea id="executeCode" class="code-input" placeholder="Enter your code here..."></textarea>
                        </div>
                        
                        <div class="execute-actions">
                            <button id="executeButton" class="primary-button">Execute</button>
                            <button id="saveAsTestButton" class="secondary-button">Save as Test</button>
                        </div>
                        
                        <div id="executeResultSection" class="execute-result-section hidden">
                            <h3>Result</h3>
                            <div class="result-status">Status: <span id="executeResultStatus">Success</span></div>
                            <div class="result-time">Execution Time: <span id="executeResultTime">0</span> ms</div>
                            
                            <div class="result-output-section">
                                <h4>Output</h4>
                                <pre id="executeResultOutput" class="result-output"></pre>
                            </div>
                            
                            <div id="executeResultErrorSection" class="result-error-section hidden">
                                <h4>Error</h4>
                                <pre id="executeResultError" class="result-error"></pre>
                            </div>
                        </div>
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
        SandboxPanel.currentPanel = undefined;
        
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
