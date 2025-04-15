import * as vscode from 'vscode';
import { MaCoderApiClient } from './api-client';

/**
 * Step in a Next Edit sequence.
 */
interface NextEditStep {
    id: string;
    description: string;
    code?: string;
    filePath?: string;
    lineNumber?: number;
    completed: boolean;
}

/**
 * Next Edit panel for MaCoder.
 */
export class NextEditPanel {
    public static currentPanel: NextEditPanel | undefined;
    private static readonly viewType = 'macoderNextEdit';

    private readonly panel: vscode.WebviewPanel;
    private readonly extensionUri: vscode.Uri;
    private readonly apiClient: MaCoderApiClient;
    private steps: NextEditStep[] = [];
    private currentStepIndex: number = -1;
    private disposables: vscode.Disposable[] = [];
    private checkpoints: Map<string, string> = new Map();

    /**
     * Create or show a Next Edit panel.
     * 
     * @param extensionUri The URI of the extension
     * @param apiClient The API client
     */
    public static createOrShow(extensionUri: vscode.Uri, apiClient: MaCoderApiClient): NextEditPanel {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it
        if (NextEditPanel.currentPanel) {
            NextEditPanel.currentPanel.panel.reveal(column);
            return NextEditPanel.currentPanel;
        }

        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel(
            NextEditPanel.viewType,
            'MaCoder Next Edit',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media')
                ]
            }
        );

        NextEditPanel.currentPanel = new NextEditPanel(panel, extensionUri, apiClient);
        return NextEditPanel.currentPanel;
    }

    /**
     * Create a new Next Edit panel.
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
                    case 'startNextEdit':
                        await this.startNextEdit(message.description);
                        break;
                    case 'applyStep':
                        await this.applyStep(message.stepId);
                        break;
                    case 'nextStep':
                        this.goToNextStep();
                        break;
                    case 'prevStep':
                        this.goToPrevStep();
                        break;
                    case 'createCheckpoint':
                        await this.createCheckpoint();
                        break;
                    case 'restoreCheckpoint':
                        await this.restoreCheckpoint(message.checkpointId);
                        break;
                }
            },
            null,
            this.disposables
        );
    }

    /**
     * Dispose of the Next Edit panel.
     */
    public dispose() {
        NextEditPanel.currentPanel = undefined;

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
     * Start a new Next Edit sequence.
     * 
     * @param description The description of the changes to make
     */
    private async startNextEdit(description: string): Promise<void> {
        try {
            // Show loading indicator
            this.panel.webview.postMessage({ command: 'showLoading' });

            // Get active editor information for context
            const editor = vscode.window.activeTextEditor;
            let fileContext = '';
            let language = '';
            let filePath = '';
            
            if (editor) {
                const document = editor.document;
                fileContext = document.getText();
                language = document.languageId;
                filePath = document.uri.fsPath;
            }

            // Create a checkpoint before starting
            await this.createCheckpoint();

            // Generate steps using the API
            // This is a simplified implementation - in a real implementation,
            // you would use a more sophisticated approach to generate steps
            const response = await this.apiClient.generateCode(
                `Generate a step-by-step plan for the following task:\n\n${description}\n\nCurrent file context: ${fileContext ? fileContext.substring(0, 1000) + '...' : 'None'}\n\nFormat the response as a JSON array of steps, where each step has a description and optional code to apply.`,
                language
            );

            if (response.success) {
                try {
                    // Parse steps from the response
                    const codeMatch = response.code.match(/```json\s*([\s\S]*?)\s*```/);
                    const jsonString = codeMatch ? codeMatch[1] : response.code;
                    
                    // Try to parse as JSON
                    const parsedSteps = JSON.parse(jsonString);
                    
                    if (Array.isArray(parsedSteps)) {
                        this.steps = parsedSteps.map((step, index) => ({
                            id: `step-${index}`,
                            description: step.description,
                            code: step.code,
                            filePath: step.filePath || filePath,
                            lineNumber: step.lineNumber,
                            completed: false
                        }));
                        
                        this.currentStepIndex = 0;
                        this.updateWebview();
                    } else {
                        throw new Error('Invalid steps format');
                    }
                } catch (parseError) {
                    console.error('Error parsing steps:', parseError);
                    
                    // Fallback: create a single step with the entire response
                    this.steps = [{
                        id: 'step-0',
                        description: 'Apply the generated code',
                        code: response.code,
                        filePath: filePath,
                        completed: false
                    }];
                    
                    this.currentStepIndex = 0;
                    this.updateWebview();
                }
            } else {
                vscode.window.showErrorMessage('Failed to generate Next Edit steps');
            }
        } catch (error) {
            console.error('Error starting Next Edit:', error);
            vscode.window.showErrorMessage('Error starting Next Edit');
        } finally {
            // Hide loading indicator
            this.panel.webview.postMessage({ command: 'hideLoading' });
        }
    }

    /**
     * Apply a step in the Next Edit sequence.
     * 
     * @param stepId The ID of the step to apply
     */
    private async applyStep(stepId: string): Promise<void> {
        const step = this.steps.find(s => s.id === stepId);
        if (!step || !step.code) {
            return;
        }

        try {
            // Create a checkpoint before applying the step
            await this.createCheckpoint();

            // If the step specifies a file path, open that file
            if (step.filePath) {
                const document = await vscode.workspace.openTextDocument(step.filePath);
                const editor = await vscode.window.showTextDocument(document);

                // If the step specifies a line number, move the cursor there
                if (step.lineNumber) {
                    const position = new vscode.Position(step.lineNumber - 1, 0);
                    editor.selection = new vscode.Selection(position, position);
                    editor.revealRange(new vscode.Range(position, position));
                }

                // Apply the code
                await editor.edit((editBuilder) => {
                    if (editor.selection.isEmpty) {
                        // Insert at cursor position
                        editBuilder.insert(editor.selection.active, step.code!);
                    } else {
                        // Replace selected text
                        editBuilder.replace(editor.selection, step.code!);
                    }
                });
            } else {
                // If no file path is specified, apply to the active editor
                const editor = vscode.window.activeTextEditor;
                if (editor) {
                    await editor.edit((editBuilder) => {
                        if (editor.selection.isEmpty) {
                            // Insert at cursor position
                            editBuilder.insert(editor.selection.active, step.code!);
                        } else {
                            // Replace selected text
                            editBuilder.replace(editor.selection, step.code!);
                        }
                    });
                }
            }

            // Mark the step as completed
            step.completed = true;
            this.updateWebview();

            // If this is the last step, show a completion message
            if (this.currentStepIndex === this.steps.length - 1) {
                vscode.window.showInformationMessage('Next Edit sequence completed!');
            } else {
                // Otherwise, move to the next step
                this.goToNextStep();
            }
        } catch (error) {
            console.error('Error applying step:', error);
            vscode.window.showErrorMessage('Error applying step');
        }
    }

    /**
     * Go to the next step in the sequence.
     */
    private goToNextStep(): void {
        if (this.currentStepIndex < this.steps.length - 1) {
            this.currentStepIndex++;
            this.updateWebview();
        }
    }

    /**
     * Go to the previous step in the sequence.
     */
    private goToPrevStep(): void {
        if (this.currentStepIndex > 0) {
            this.currentStepIndex--;
            this.updateWebview();
        }
    }

    /**
     * Create a checkpoint of the current workspace state.
     */
    private async createCheckpoint(): Promise<void> {
        try {
            // In a real implementation, you would save the state of all open files
            // For simplicity, we'll just save the active editor's content
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const document = editor.document;
                const content = document.getText();
                const filePath = document.uri.fsPath;
                const timestamp = Date.now();
                const checkpointId = `checkpoint-${timestamp}`;
                
                this.checkpoints.set(checkpointId, content);
                
                // Notify the webview
                this.panel.webview.postMessage({
                    command: 'checkpointCreated',
                    checkpointId,
                    timestamp,
                    filePath
                });
            }
        } catch (error) {
            console.error('Error creating checkpoint:', error);
            vscode.window.showErrorMessage('Error creating checkpoint');
        }
    }

    /**
     * Restore a checkpoint.
     * 
     * @param checkpointId The ID of the checkpoint to restore
     */
    private async restoreCheckpoint(checkpointId: string): Promise<void> {
        try {
            const content = this.checkpoints.get(checkpointId);
            if (!content) {
                vscode.window.showErrorMessage('Checkpoint not found');
                return;
            }

            // Restore the content to the active editor
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                await editor.edit((editBuilder) => {
                    const fullRange = new vscode.Range(
                        new vscode.Position(0, 0),
                        new vscode.Position(editor.document.lineCount, 0)
                    );
                    editBuilder.replace(fullRange, content);
                });
                
                vscode.window.showInformationMessage('Checkpoint restored');
            }
        } catch (error) {
            console.error('Error restoring checkpoint:', error);
            vscode.window.showErrorMessage('Error restoring checkpoint');
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
        // Format steps as HTML
        const stepsHtml = this.steps.map((step, index) => {
            const isCurrent = index === this.currentStepIndex;
            const isCompleted = step.completed;
            
            return `
                <div class="step ${isCurrent ? 'current' : ''} ${isCompleted ? 'completed' : ''}">
                    <div class="step-header">
                        <span class="step-number">${index + 1}</span>
                        <span class="step-status">${isCompleted ? '✓' : ''}</span>
                    </div>
                    <div class="step-content">
                        <div class="step-description">${this.escapeHtml(step.description)}</div>
                        ${step.code ? `
                            <pre><code>${this.escapeHtml(step.code)}</code></pre>
                            <button class="apply-step-button" data-step-id="${step.id}">Apply</button>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');

        // Format checkpoints as HTML
        const checkpointsHtml = Array.from(this.checkpoints.entries()).map(([id, _]) => {
            const timestamp = id.replace('checkpoint-', '');
            const date = new Date(parseInt(timestamp));
            const timeString = date.toLocaleTimeString();
            
            return `
                <div class="checkpoint">
                    <span class="checkpoint-time">${timeString}</span>
                    <button class="restore-checkpoint-button" data-checkpoint-id="${id}">Restore</button>
                </div>
            `;
        }).join('');

        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>MaCoder Next Edit</title>
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
                    .container {
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                    }
                    .input-container {
                        padding: 16px;
                        background-color: var(--vscode-editor-background);
                        border-bottom: 1px solid var(--vscode-panel-border);
                    }
                    #task-input {
                        width: 100%;
                        padding: 8px;
                        border: 1px solid var(--vscode-input-border);
                        background-color: var(--vscode-input-background);
                        color: var(--vscode-input-foreground);
                        border-radius: 4px;
                        resize: none;
                        min-height: 40px;
                    }
                    #start-button {
                        margin-top: 8px;
                        padding: 8px 16px;
                        background-color: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    #start-button:hover {
                        background-color: var(--vscode-button-hoverBackground);
                    }
                    .steps-container {
                        flex: 1;
                        overflow-y: auto;
                        padding: 16px;
                    }
                    .step {
                        margin-bottom: 16px;
                        padding: 12px;
                        border-radius: 6px;
                        background-color: var(--vscode-editor-inactiveSelectionBackground);
                        opacity: 0.7;
                    }
                    .step.current {
                        background-color: var(--vscode-editor-selectionBackground);
                        opacity: 1;
                        border-left: 4px solid var(--vscode-activityBarBadge-background);
                    }
                    .step.completed {
                        opacity: 0.5;
                    }
                    .step-header {
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 8px;
                    }
                    .step-number {
                        font-weight: bold;
                    }
                    .step-status {
                        color: var(--vscode-terminal-ansiGreen);
                    }
                    .step-content {
                        white-space: pre-wrap;
                    }
                    .step-description {
                        margin-bottom: 8px;
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
                    .apply-step-button {
                        background-color: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        margin-top: 4px;
                        cursor: pointer;
                    }
                    .apply-step-button:hover {
                        background-color: var(--vscode-button-hoverBackground);
                    }
                    .navigation {
                        display: flex;
                        justify-content: space-between;
                        padding: 16px;
                        background-color: var(--vscode-editor-background);
                        border-top: 1px solid var(--vscode-panel-border);
                    }
                    .nav-button {
                        padding: 8px 16px;
                        background-color: var(--vscode-button-secondaryBackground);
                        color: var(--vscode-button-secondaryForeground);
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    .nav-button:hover {
                        background-color: var(--vscode-button-secondaryHoverBackground);
                    }
                    .nav-button:disabled {
                        opacity: 0.5;
                        cursor: not-allowed;
                    }
                    .checkpoints-container {
                        padding: 16px;
                        background-color: var(--vscode-editor-background);
                        border-top: 1px solid var(--vscode-panel-border);
                    }
                    .checkpoints-header {
                        font-weight: bold;
                        margin-bottom: 8px;
                    }
                    .checkpoints-list {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 8px;
                    }
                    .checkpoint {
                        display: flex;
                        align-items: center;
                        padding: 4px 8px;
                        background-color: var(--vscode-editor-inactiveSelectionBackground);
                        border-radius: 4px;
                    }
                    .checkpoint-time {
                        margin-right: 8px;
                    }
                    .restore-checkpoint-button {
                        background-color: var(--vscode-button-secondaryBackground);
                        color: var(--vscode-button-secondaryForeground);
                        border: none;
                        border-radius: 4px;
                        padding: 2px 4px;
                        font-size: 0.8em;
                        cursor: pointer;
                    }
                    .restore-checkpoint-button:hover {
                        background-color: var(--vscode-button-secondaryHoverBackground);
                    }
                    .loading-overlay {
                        display: none;
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(0, 0, 0, 0.5);
                        justify-content: center;
                        align-items: center;
                        z-index: 1000;
                    }
                    .loading-spinner {
                        width: 40px;
                        height: 40px;
                        border: 4px solid rgba(255, 255, 255, 0.3);
                        border-radius: 50%;
                        border-top-color: var(--vscode-activityBarBadge-background);
                        animation: spin 1s ease-in-out infinite;
                    }
                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="input-container">
                        <textarea id="task-input" placeholder="Describe the changes you want to make..." rows="3"></textarea>
                        <button id="start-button">Start Next Edit</button>
                    </div>
                    <div class="steps-container">
                        ${this.steps.length > 0 ? stepsHtml : '<div class="empty-state">No steps yet. Describe the changes you want to make and click "Start Next Edit".</div>'}
                    </div>
                    ${this.steps.length > 0 ? `
                        <div class="navigation">
                            <button id="prev-button" class="nav-button" ${this.currentStepIndex <= 0 ? 'disabled' : ''}>Previous</button>
                            <button id="create-checkpoint-button" class="nav-button">Create Checkpoint</button>
                            <button id="next-button" class="nav-button" ${this.currentStepIndex >= this.steps.length - 1 ? 'disabled' : ''}>Next</button>
                        </div>
                    ` : ''}
                    ${this.checkpoints.size > 0 ? `
                        <div class="checkpoints-container">
                            <div class="checkpoints-header">Checkpoints</div>
                            <div class="checkpoints-list">
                                ${checkpointsHtml}
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="loading-overlay" id="loading-overlay">
                    <div class="loading-spinner"></div>
                </div>
                <script>
                    const vscode = acquireVsCodeApi();
                    const taskInput = document.getElementById('task-input');
                    const startButton = document.getElementById('start-button');
                    const loadingOverlay = document.getElementById('loading-overlay');
                    
                    // Start Next Edit when clicking the start button
                    startButton.addEventListener('click', () => {
                        const description = taskInput.value.trim();
                        if (description) {
                            vscode.postMessage({
                                command: 'startNextEdit',
                                description: description
                            });
                        }
                    });
                    
                    // Apply step when clicking an apply step button
                    document.addEventListener('click', (event) => {
                        if (event.target.classList.contains('apply-step-button')) {
                            const stepId = event.target.getAttribute('data-step-id');
                            vscode.postMessage({
                                command: 'applyStep',
                                stepId: stepId
                            });
                        }
                    });
                    
                    // Restore checkpoint when clicking a restore checkpoint button
                    document.addEventListener('click', (event) => {
                        if (event.target.classList.contains('restore-checkpoint-button')) {
                            const checkpointId = event.target.getAttribute('data-checkpoint-id');
                            vscode.postMessage({
                                command: 'restoreCheckpoint',
                                checkpointId: checkpointId
                            });
                        }
                    });
                    
                    // Navigation buttons
                    const prevButton = document.getElementById('prev-button');
                    const nextButton = document.getElementById('next-button');
                    const createCheckpointButton = document.getElementById('create-checkpoint-button');
                    
                    if (prevButton) {
                        prevButton.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'prevStep'
                            });
                        });
                    }
                    
                    if (nextButton) {
                        nextButton.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'nextStep'
                            });
                        });
                    }
                    
                    if (createCheckpointButton) {
                        createCheckpointButton.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'createCheckpoint'
                            });
                        });
                    }
                    
                    // Handle messages from the extension
                    window.addEventListener('message', (event) => {
                        const message = event.data;
                        switch (message.command) {
                            case 'showLoading':
                                loadingOverlay.style.display = 'flex';
                                break;
                            case 'hideLoading':
                                loadingOverlay.style.display = 'none';
                                break;
                            case 'checkpointCreated':
                                // This will be handled by the extension refreshing the webview
                                break;
                        }
                    });
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
