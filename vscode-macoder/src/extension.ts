import * as vscode from 'vscode';
import { ExtensionContext, window, commands, workspace, languages } from 'vscode';
import { MaCoderApiClient } from './api-client';
import { StandaloneApiClient } from './standalone-api-client';
import { HybridApiClient } from './hybrid-api-client';
import { ChatPanel } from './chat-panel';
import { NextEditPanel } from './next-edit-panel';
import { MaCoderCompletionItemProvider } from './completions-provider';
import { LaminarService } from './laminar-service';
import { LocalModelInterface } from './local-model-interface';
import { ProjectIndexer } from './project-indexer';
import { AutonomousMode } from './autonomous-mode';
import { AutonomousPanel } from './autonomous-panel';
import { BrainstormingManager } from './brainstorming';
import { BrainstormingPanel } from './brainstorming-panel';
import { DeepReasoningManager } from './deep-reasoning';
import { DeepReasoningPanel } from './deep-reasoning-panel';
import { CodeVerificationManager } from './code-verification';
import { FileCodeEditLogger } from './code-edit-logger';
import { CodeEditTracker } from './code-edit-tracker';
import { LocalCodeSandbox } from './code-sandbox';
import { SandboxPanel } from './sandbox-panel';

/**
 * This method is called when the extension is activated.
 * Extension is activated the first time the command is executed.
 */
export function activate(context: ExtensionContext) {
    console.log('MaCoder extension is now active');

    // Load configuration
    const config = workspace.getConfiguration('macoder');
    const serverUrl = config.get<string>('serverUrl') || 'http://localhost:1302';
    const modelName = config.get<string>('modelName') || 'gemma3:12b';
    const enableCompletions = config.get<boolean>('enableCompletions') || true;
    const enableChat = config.get<boolean>('enableChat') || true;
    const enableNextEdit = config.get<boolean>('enableNextEdit') || true;

    // Initialize Laminar service
    const laminarService = LaminarService.getInstance();
    laminarService.initialize().then(() => {
        console.log('Laminar service initialized');
    }).catch(error => {
        console.error('Failed to initialize Laminar service:', error);
    });

    // Initialize local model interface
    const localModelInterface = LocalModelInterface.getInstance();

    // Initialize project indexer
    const projectIndexer = ProjectIndexer.getInstance();

    // Get configuration for hybrid mode
    const preferStandalone = config.get<boolean>('preferStandalone') || false;

    // Create hybrid API client
    const apiClient = new HybridApiClient(serverUrl, modelName, preferStandalone);

    // Initialize autonomous mode
    const autonomousMode = AutonomousMode.getInstance(apiClient);

    // Initialize brainstorming manager
    const brainstormingManager = BrainstormingManager.getInstance(apiClient);

    // Initialize deep reasoning manager
    const deepReasoningManager = DeepReasoningManager.getInstance(apiClient);

    // Initialize code verification manager
    const codeVerificationManager = CodeVerificationManager.getInstance(apiClient);

    // Initialize code edit logger and tracker if enabled
    const enableCodeEditLogging = workspace.getConfiguration('macoder').get('enableCodeEditLogging', true);
    let codeEditLogger: FileCodeEditLogger | undefined;
    let codeEditTracker: CodeEditTracker | undefined;

    if (enableCodeEditLogging) {
        codeEditLogger = FileCodeEditLogger.getInstance(context);
        codeEditTracker = CodeEditTracker.getInstance(codeEditLogger);

        // Start an initial edit session
        codeEditTracker.startSession('Initial session');
    }

    // Initialize sandbox if enabled
    const enableSandbox = workspace.getConfiguration('macoder').get('enableSandbox', true);
    let sandbox: LocalCodeSandbox | undefined;

    if (enableSandbox) {
        sandbox = LocalCodeSandbox.getInstance(context);
    }

    // Wait for client initialization
    setTimeout(() => {
        // Display activation message
        const mode = apiClient.getCurrentMode();
        if (mode === 'standalone') {
            window.showInformationMessage('MaCoder is now active in standalone mode!');
        } else {
            window.showInformationMessage('MaCoder is now active with DMac server integration!');
        }
    }, 1000); // Give the client a second to check DMac availability

    // Register commands
    const startChatCommand = commands.registerCommand('macoder.startChat', () => {
        window.showInformationMessage('Starting MaCoder chat...');
        ChatPanel.createOrShow(context.extensionUri, apiClient);
    });

    const nextEditCommand = commands.registerCommand('macoder.nextEdit', () => {
        window.showInformationMessage('Starting MaCoder next edit...');
        NextEditPanel.createOrShow(context.extensionUri, apiClient);
    });

    const generateCodeCommand = commands.registerCommand('macoder.generateCode', async () => {
        const editor = window.activeTextEditor;
        if (!editor) {
            window.showWarningMessage('No active editor');
            return;
        }

        const prompt = await window.showInputBox({
            prompt: 'Enter a description of the code you want to generate',
            placeHolder: 'Generate a function that...',
        });

        if (!prompt) {
            return;
        }

        window.showInformationMessage('Generating code with MaCoder...');

        // Get Laminar service
        const laminarService = LaminarService.getInstance();

        try {
            // Use Laminar to trace the code generation
            const response = await laminarService.trace('generateCode', async () => {
                const result = await apiClient.generateCode(prompt, editor.document.languageId);

                // Add to dataset if Laminar is enabled
                if (laminarService.isEnabled() && result.success) {
                    await laminarService.addToDataset('code_generation', {
                        prompt,
                        language: editor.document.languageId,
                        timestamp: new Date().toISOString()
                    }, {
                        code: result.code
                    });
                }

                return result;
            });

            if (response.success && response.code) {
                editor.edit(editBuilder => {
                    if (editor.selection.isEmpty) {
                        editBuilder.insert(editor.selection.active, response.code);
                    } else {
                        editBuilder.replace(editor.selection, response.code);
                    }
                });
            } else {
                window.showErrorMessage('Failed to generate code');
            }
        } catch (error) {
            console.error('Error generating code:', error);
            window.showErrorMessage('Error generating code');
        }
    });

    const explainCodeCommand = commands.registerCommand('macoder.explainCode', async () => {
        const editor = window.activeTextEditor;
        if (editor) {
            const selection = editor.selection;
            const text = editor.document.getText(selection);
            if (text) {
                window.showInformationMessage('Explaining selected code...');

                try {
                    const response = await apiClient.explainCode(text, editor.document.languageId);

                    if (response.success && response.explanation) {
                        // Show explanation in a new editor
                        const doc = await workspace.openTextDocument({
                            content: response.explanation,
                            language: 'markdown'
                        });
                        await window.showTextDocument(doc, { viewColumn: vscode.ViewColumn.Beside });
                    } else {
                        window.showErrorMessage('Failed to explain code');
                    }
                } catch (error) {
                    console.error('Error explaining code:', error);
                    window.showErrorMessage('Error explaining code');
                }
            } else {
                window.showWarningMessage('Please select some code to explain.');
            }
        }
    });

    const refactorCodeCommand = commands.registerCommand('macoder.refactorCode', async () => {
        const editor = window.activeTextEditor;
        if (editor) {
            const selection = editor.selection;
            const text = editor.document.getText(selection);
            if (text) {
                try {
                    // Ask for refactoring instructions
                    const instructions = await window.showInputBox({
                        prompt: 'Enter refactoring instructions',
                        placeHolder: 'e.g., "Optimize for performance" or "Convert to async/await"',
                        ignoreFocusOut: true
                    });

                    if (!instructions) {
                        return; // User cancelled
                    }

                    window.showInformationMessage('Refactoring selected code...');

                    // Show progress indicator
                    const result = await window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: 'Refactoring code...',
                        cancellable: false
                    }, async (progress) => {
                        progress.report({ increment: 0, message: 'Analyzing code...' });

                        // Get the language ID of the current document
                        const language = editor.document.languageId;

                        // Call the API to refactor the code
                        const response = await apiClient.refactorCode(text, instructions, language);

                        progress.report({ increment: 100, message: 'Done!' });
                        return response;
                    });

                    // Check if the API call was successful
                    if (result.success) {
                        // Replace the selected code with the refactored code
                        editor.edit(editBuilder => {
                            editBuilder.replace(selection, result.code);
                        });
                        window.showInformationMessage('Code refactoring complete!');
                    } else {
                        window.showErrorMessage(`Failed to refactor code: ${result.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    window.showErrorMessage(`Error refactoring code: ${error instanceof Error ? error.message : 'Unknown error'}`);
                }
            } else {
                window.showWarningMessage('Please select some code to refactor.');
            }
        } else {
            window.showWarningMessage('No active editor.');
        }
    });

    const findBugsCommand = commands.registerCommand('macoder.findBugs', async () => {
        const editor = window.activeTextEditor;
        if (editor) {
            const selection = editor.selection;
            const text = editor.document.getText(selection);
            if (text) {
                try {
                    window.showInformationMessage('Finding bugs in selected code...');

                    // Show progress indicator
                    const result = await window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: 'Analyzing code for bugs...',
                        cancellable: false
                    }, async (progress) => {
                        progress.report({ increment: 0, message: 'Analyzing code...' });

                        // Get the language ID of the current document
                        const language = editor.document.languageId;

                        // Call the API to find bugs in the code
                        const response = await apiClient.findBugs(text, language);

                        progress.report({ increment: 100, message: 'Done!' });
                        return response;
                    });

                    // Check if the API call was successful
                    if (result.success) {
                        // Create and show a new webview panel for bug results
                        const panel = vscode.window.createWebviewPanel(
                            'macoderBugs',
                            'Bug Analysis Results',
                            vscode.ViewColumn.Beside,
                            { enableScripts: true }
                        );

                        // Generate HTML content for bug results
                        panel.webview.html = getBugResultsWebviewContent(text, result.bugs, result.fixedCode);

                        // Handle messages from the webview
                        panel.webview.onDidReceiveMessage(
                            async message => {
                                if (message.command === 'applyFix') {
                                    editor.edit(editBuilder => {
                                        editBuilder.replace(selection, message.fixedCode);
                                    });
                                    window.showInformationMessage('Applied fixed code!');
                                }
                            }
                        );

                        window.showInformationMessage('Bug analysis complete! View results in the panel.');
                    } else {
                        window.showErrorMessage(`Failed to analyze code for bugs: ${result.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    window.showErrorMessage(`Error analyzing code for bugs: ${error instanceof Error ? error.message : 'Unknown error'}`);
                }
            } else {
                window.showWarningMessage('Please select some code to analyze for bugs.');
            }
        } else {
            window.showWarningMessage('No active editor.');
        }
    });

    /**
     * Generate HTML content for bug results webview
     *
     * @param originalCode Original code
     * @param bugs List of bugs found
     * @param fixedCode Fixed code
     * @returns HTML content
     */
    function getBugResultsWebviewContent(originalCode: string, bugs: any[], fixedCode: string): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MaCoder Bug Analysis</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                h1, h2, h3 {
                    color: var(--vscode-editor-foreground);
                }
                .bug-container {
                    margin-bottom: 20px;
                    padding: 10px;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 5px;
                }
                .bug-title {
                    font-weight: bold;
                    color: var(--vscode-terminal-ansiRed);
                }
                .bug-description {
                    margin-top: 5px;
                    margin-bottom: 10px;
                }
                .bug-location {
                    font-family: monospace;
                    background-color: var(--vscode-editor-lineHighlightBackground);
                    padding: 2px 5px;
                    border-radius: 3px;
                }
                .code-container {
                    margin-top: 20px;
                    margin-bottom: 20px;
                }
                .code-header {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .code-content {
                    font-family: monospace;
                    white-space: pre-wrap;
                    padding: 10px;
                    background-color: var(--vscode-editor-background);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 5px;
                    overflow-x: auto;
                }
                .fixed-code {
                    background-color: var(--vscode-diffEditor-insertedTextBackground);
                }
                .button-container {
                    margin-top: 20px;
                    text-align: right;
                }
                button {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 12px;
                    border-radius: 3px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
            </style>
        </head>
        <body>
            <h1>Bug Analysis Results</h1>

            <h2>Found Issues (${bugs.length})</h2>
            ${bugs.length === 0 ? '<p>No issues found in the code.</p>' : ''}
            ${bugs.map((bug, index) => `
                <div class="bug-container">
                    <div class="bug-title">${index + 1}. ${bug.title}</div>
                    <div class="bug-description">${bug.description}</div>
                    ${bug.location ? `<div class="bug-location">Location: ${bug.location}</div>` : ''}
                </div>
            `).join('')}

            <div class="code-container">
                <div class="code-header">Original Code:</div>
                <pre class="code-content">${escapeHtml(originalCode)}</pre>
            </div>

            ${fixedCode ? `
                <div class="code-container">
                    <div class="code-header">Fixed Code:</div>
                    <pre class="code-content fixed-code">${escapeHtml(fixedCode)}</pre>
                </div>

                <div class="button-container">
                    <button id="apply-fix-button">Apply Fixed Code</button>
                </div>
            ` : ''}

            <script>
                (function() {
                    const vscode = acquireVsCodeApi();

                    // Add event listener to the apply fix button
                    const applyFixButton = document.getElementById('apply-fix-button');
                    if (applyFixButton) {
                        applyFixButton.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'applyFix',
                                fixedCode: ${JSON.stringify(fixedCode)}
                            });
                        });
                    }
                })();
            </script>
        </body>
        </html>`;
    }

    /**
     * Escape HTML special characters
     *
     * @param text Text to escape
     * @returns Escaped text
     */
    function escapeHtml(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    const generateTestsCommand = commands.registerCommand('macoder.generateTests', async () => {
        const editor = window.activeTextEditor;
        if (editor) {
            const selection = editor.selection;
            const text = editor.document.getText(selection);
            if (text) {
                try {
                    window.showInformationMessage('Generating tests for selected code...');

                    // Show progress indicator
                    const result = await window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: 'Generating tests...',
                        cancellable: false
                    }, async (progress) => {
                        progress.report({ increment: 0, message: 'Analyzing code...' });

                        // Get the language ID of the current document
                        const language = editor.document.languageId;

                        // Call the API to generate tests for the code
                        const response = await apiClient.generateTests(text, language);

                        progress.report({ increment: 100, message: 'Done!' });
                        return response;
                    });

                    // Check if the API call was successful
                    if (result.success) {
                        // Create a new document with the generated tests
                        let testFileName = '';
                        const currentFileName = editor.document.fileName;

                        // Determine test file name based on language
                        if (currentFileName) {
                            const fileNameWithoutExt = currentFileName.replace(/\.[^/.]+$/, '');
                            const extension = editor.document.fileName.split('.').pop();

                            switch (editor.document.languageId) {
                                case 'javascript':
                                    testFileName = `${fileNameWithoutExt}.test.js`;
                                    break;
                                case 'typescript':
                                    testFileName = `${fileNameWithoutExt}.test.ts`;
                                    break;
                                case 'python':
                                    testFileName = `test_${fileNameWithoutExt.split('/').pop()}.py`;
                                    break;
                                case 'java':
                                    testFileName = `${fileNameWithoutExt}Test.java`;
                                    break;
                                default:
                                    testFileName = `${fileNameWithoutExt}.test.${extension}`;
                            }
                        }

                        // Create a new untitled document with the generated tests
                        const testDocument = await vscode.workspace.openTextDocument({
                            language: editor.document.languageId,
                            content: result.tests
                        });

                        // Show the document
                        await vscode.window.showTextDocument(testDocument, { preview: false, viewColumn: vscode.ViewColumn.Beside });

                        window.showInformationMessage('Test generation complete!');
                    } else {
                        window.showErrorMessage(`Failed to generate tests: ${result.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    window.showErrorMessage(`Error generating tests: ${error instanceof Error ? error.message : 'Unknown error'}`);
                }
            } else {
                window.showWarningMessage('Please select some code to generate tests for.');
            }
        } else {
            window.showWarningMessage('No active editor.');
        }
    });

    const documentCodeCommand = commands.registerCommand('macoder.documentCode', async () => {
        const editor = window.activeTextEditor;
        if (editor) {
            const selection = editor.selection;
            const text = editor.document.getText(selection);
            if (text) {
                try {
                    window.showInformationMessage('Documenting selected code...');

                    // Show progress indicator
                    const result = await window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: 'Documenting code...',
                        cancellable: false
                    }, async (progress) => {
                        progress.report({ increment: 0, message: 'Analyzing code...' });

                        // Get the language ID of the current document
                        const language = editor.document.languageId;

                        // Call the API to document the code
                        const response = await apiClient.documentCode(text, language);

                        progress.report({ increment: 100, message: 'Done!' });
                        return response;
                    });

                    // Check if the API call was successful
                    if (result.success) {
                        // Replace the selected code with the documented code
                        editor.edit(editBuilder => {
                            editBuilder.replace(selection, result.code);
                        });
                        window.showInformationMessage('Code documentation complete!');
                    } else {
                        window.showErrorMessage(`Failed to document code: ${result.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    window.showErrorMessage(`Error documenting code: ${error instanceof Error ? error.message : 'Unknown error'}`);
                }
            } else {
                window.showWarningMessage('Please select some code to document.');
            }
        } else {
            window.showWarningMessage('No active editor.');
        }
    });

    const benchmarkModelsCommand = commands.registerCommand('macoder.benchmarkModels', async () => {
        try {
            // Get the benchmark models from configuration
            const config = workspace.getConfiguration('macoder');
            const benchmarkModels = config.get<string[]>('benchmarkModels') || ['gemma3:12b', 'qwen2.5-coder:1.5b-base', 'llama3:8b'];

            // Create quick pick items for benchmark tasks
            const tasks = [
                { label: 'Code Generation', description: 'Benchmark code generation capabilities', task: 'generate_code' },
                { label: 'Code Completion', description: 'Benchmark code completion capabilities', task: 'complete_code' },
                { label: 'Code Explanation', description: 'Benchmark code explanation capabilities', task: 'explain_code' },
                { label: 'Code Refactoring', description: 'Benchmark code refactoring capabilities', task: 'refactor_code' },
                { label: 'Bug Finding', description: 'Benchmark bug finding capabilities', task: 'find_bugs' },
                { label: 'Test Generation', description: 'Benchmark test generation capabilities', task: 'generate_tests' }
            ];

            // Show quick pick to select benchmark task
            const selectedTask = await window.showQuickPick(tasks, {
                placeHolder: 'Select a benchmark task',
                ignoreFocusOut: true
            });

            if (!selectedTask) {
                return; // User cancelled
            }

            // Show progress indicator
            const result = await window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `Benchmarking models for ${selectedTask.label}...`,
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Starting benchmark...' });

                // Get sample code if needed
                let data = {};
                if (['complete_code', 'explain_code', 'refactor_code', 'find_bugs', 'generate_tests'].includes(selectedTask.task)) {
                    // Get active editor text or ask for sample code
                    const editor = window.activeTextEditor;
                    let code = '';
                    let language = '';

                    if (editor) {
                        // Use selected text or entire document
                        const selection = editor.selection;
                        code = selection.isEmpty ? editor.document.getText() : editor.document.getText(selection);
                        language = editor.document.languageId;
                    } else {
                        // Ask for sample code
                        code = await window.showInputBox({
                            prompt: 'Enter sample code for benchmarking',
                            placeHolder: 'function example() { /* code here */ }',
                            ignoreFocusOut: true,
                            multiline: true
                        }) || '';

                        // Ask for language
                        language = await window.showQuickPick(
                            ['javascript', 'typescript', 'python', 'java', 'c', 'cpp', 'csharp', 'go', 'rust'],
                            { placeHolder: 'Select programming language' }
                        ) || 'javascript';
                    }

                    if (!code) {
                        window.showWarningMessage('Benchmark cancelled: No code provided');
                        return { success: false, error: 'No code provided' };
                    }

                    data = { code, language };
                } else if (selectedTask.task === 'generate_code') {
                    // Ask for prompt
                    const prompt = await window.showInputBox({
                        prompt: 'Enter a prompt for code generation',
                        placeHolder: 'Generate a function that sorts an array of objects by a property',
                        ignoreFocusOut: true
                    });

                    if (!prompt) {
                        window.showWarningMessage('Benchmark cancelled: No prompt provided');
                        return { success: false, error: 'No prompt provided' };
                    }

                    // Ask for language
                    const language = await window.showQuickPick(
                        ['javascript', 'typescript', 'python', 'java', 'c', 'cpp', 'csharp', 'go', 'rust'],
                        { placeHolder: 'Select programming language' }
                    );

                    if (!language) {
                        window.showWarningMessage('Benchmark cancelled: No language selected');
                        return { success: false, error: 'No language selected' };
                    }

                    data = { prompt, language };
                }

                progress.report({ increment: 20, message: 'Running benchmark...' });

                // Call the API to benchmark models
                const response = await apiClient.benchmarkModels(selectedTask.task, benchmarkModels, data);

                progress.report({ increment: 100, message: 'Done!' });
                return response;
            });

            // Check if the API call was successful
            if (result.success) {
                // Create and show a new webview panel for results
                const panel = vscode.window.createWebviewPanel(
                    'macoderBenchmark',
                    `Benchmark Results: ${selectedTask?.label || 'Models'}`,
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                // Generate HTML content for benchmark results
                panel.webview.html = getBenchmarkResultsWebviewContent(result.results, selectedTask?.label || 'Models');

                window.showInformationMessage('Benchmark complete! View results in the panel.');
            } else {
                window.showErrorMessage(`Failed to benchmark models: ${result.error || 'Unknown error'}`);
            }
        } catch (error) {
            window.showErrorMessage(`Error benchmarking models: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    });

    /**
     * Generate HTML content for benchmark results webview
     *
     * @param results Benchmark results
     * @param taskName Name of the benchmark task
     * @returns HTML content
     */
    function getBenchmarkResultsWebviewContent(results: any, taskName: string): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MaCoder Benchmark Results</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                }
                h1, h2, h3 {
                    color: var(--vscode-editor-foreground);
                }
                .benchmark-container {
                    margin-bottom: 30px;
                }
                .results-table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 20px;
                }
                .results-table th, .results-table td {
                    border: 1px solid var(--vscode-panel-border);
                    padding: 8px 12px;
                    text-align: left;
                }
                .results-table th {
                    background-color: var(--vscode-editor-lineHighlightBackground);
                    font-weight: bold;
                }
                .results-table tr:nth-child(even) {
                    background-color: var(--vscode-editor-lineHighlightBackground);
                }
                .model-name {
                    font-weight: bold;
                }
                .metric-value {
                    text-align: right;
                }
                .winner {
                    color: var(--vscode-terminal-ansiGreen);
                    font-weight: bold;
                }
                .chart-container {
                    margin-top: 30px;
                    height: 300px;
                }
            </style>
        </head>
        <body>
            <h1>MaCoder Benchmark Results</h1>
            <h2>${taskName} Benchmark</h2>

            <div class="benchmark-container">
                <h3>Performance Metrics</h3>
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Success Rate</th>
                            <th>Execution Time (ms)</th>
                            <th>Quality Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map((result: any) => {
            const isWinner = result.isWinner ? 'winner' : '';
            return `<tr>
                                <td class="model-name ${isWinner}">${result.model}</td>
                                <td class="metric-value ${isWinner}">${(result.successRate * 100).toFixed(1)}%</td>
                                <td class="metric-value ${isWinner}">${result.executionTime.toFixed(0)}</td>
                                <td class="metric-value ${isWinner}">${result.qualityScore.toFixed(1)}/10</td>
                            </tr>`;
        }).join('')}
                    </tbody>
                </table>

                <h3>Summary</h3>
                <p>${getBenchmarkSummary(results)}</p>
            </div>
        </body>
        </html>`;
    }

    /**
     * Generate a summary of benchmark results
     *
     * @param results Benchmark results
     * @returns Summary text
     */
    function getBenchmarkSummary(results: any[]): string {
        // Find the winner (model with highest quality score)
        const winner = results.reduce((prev, current) => {
            return (prev.qualityScore > current.qualityScore) ? prev : current;
        });

        // Find the fastest model
        const fastest = results.reduce((prev, current) => {
            return (prev.executionTime < current.executionTime) ? prev : current;
        });

        // Generate summary text
        return `<strong>${winner.model}</strong> achieved the highest quality score (${winner.qualityScore.toFixed(1)}/10) with a success rate of ${(winner.successRate * 100).toFixed(1)}%. ` +
            `<strong>${fastest.model}</strong> was the fastest with an execution time of ${fastest.executionTime.toFixed(0)}ms.`;
    }

    // Add toggle mode command
    const toggleModeCommand = commands.registerCommand('macoder.toggleMode', async () => {
        const currentMode = apiClient.getCurrentMode();
        const newMode = currentMode === 'dmac' ? 'standalone' : 'dmac';

        // Update configuration
        await workspace.getConfiguration('macoder').update('preferStandalone', newMode === 'standalone', true);

        // Update client mode
        apiClient.setPreferredMode(newMode === 'standalone');

        // Show message
        window.showInformationMessage(`MaCoder is now in ${newMode} mode`);
    });

    // Add switch model provider command
    const switchModelProviderCommand = commands.registerCommand('macoder.switchModelProvider', async () => {
        // Get available providers
        const localModelInterface = LocalModelInterface.getInstance();
        const providers = Array.from(localModelInterface.getProviders().keys());

        if (providers.length === 0) {
            window.showErrorMessage('No model providers available');
            return;
        }

        // Get current provider
        const config = workspace.getConfiguration('macoder');
        const currentProvider = config.get<string>('localModelProvider') || 'ollama';

        // Show quick pick to select provider
        const selectedProvider = await window.showQuickPick(providers, {
            placeHolder: 'Select a model provider',
            canPickMany: false
        });

        if (!selectedProvider) {
            return; // User cancelled
        }

        // Update configuration
        await config.update('localModelProvider', selectedProvider, true);

        // Restart the local model interface
        await localModelInterface.restartWithProvider(selectedProvider);

        // Show message
        window.showInformationMessage(`Switched to ${selectedProvider} model provider`);
    });

    // Add toggle autonomous mode command
    const toggleAutonomousModeCommand = commands.registerCommand('macoder.toggleAutonomousMode', () => {
        autonomousMode.toggle();

        // Show message
        const isActive = autonomousMode.isActive();
        window.showInformationMessage(`Autonomous mode ${isActive ? 'started' : 'stopped'}`);
    });

    // Add show autonomous panel command
    const showAutonomousPanelCommand = commands.registerCommand('macoder.showAutonomousPanel', () => {
        AutonomousPanel.createOrShow(context.extensionUri, autonomousMode);
    });

    // Add execute task command
    const executeTaskCommand = commands.registerCommand('macoder.executeTask', async () => {
        // Get task description from user
        const taskDescription = await window.showInputBox({
            prompt: 'Enter a task description',
            placeHolder: 'Generate a function that...',
        });

        if (!taskDescription) {
            return; // User cancelled
        }

        // Check if autonomous mode is active
        if (!autonomousMode.isActive()) {
            // Ask user if they want to start autonomous mode
            const startAutonomousMode = await window.showInformationMessage(
                'Autonomous mode is not active. Do you want to start it?',
                'Yes', 'No'
            );

            if (startAutonomousMode !== 'Yes') {
                return; // User cancelled
            }

            // Start autonomous mode
            autonomousMode.start();
        }

        // Show autonomous panel
        AutonomousPanel.createOrShow(context.extensionUri, autonomousMode);

        // Execute task
        try {
            await autonomousMode.executeTask(taskDescription);
        } catch (error) {
            window.showErrorMessage(`Failed to execute task: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    // Add refresh index command
    const refreshIndexCommand = commands.registerCommand('macoder.refreshIndex', async () => {
        try {
            // Show progress notification
            await window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Refreshing code index...',
                cancellable: false
            }, async (progress) => {
                // Refresh the index
                await projectIndexer.refreshIndex();

                // Show success message
                window.showInformationMessage('Code index refreshed successfully');
            });
        } catch (error) {
            window.showErrorMessage(`Failed to refresh index: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    // Add show brainstorming panel command
    const showBrainstormingPanelCommand = commands.registerCommand('macoder.showBrainstormingPanel', () => {
        BrainstormingPanel.createOrShow(context.extensionUri, brainstormingManager);
    });

    // Add show deep reasoning panel command
    const showDeepReasoningPanelCommand = commands.registerCommand('macoder.showDeepReasoningPanel', () => {
        DeepReasoningPanel.createOrShow(context.extensionUri, deepReasoningManager);
    });

    // Add perform deep reasoning command
    const performDeepReasoningCommand = commands.registerCommand('macoder.performDeepReasoning', async () => {
        // Get problem from user
        const problem = await window.showInputBox({
            prompt: 'Enter a problem to reason about',
            placeHolder: 'How to implement a caching system for...',
        });

        if (!problem) {
            return; // User cancelled
        }

        // Get context from user (optional)
        const context = await window.showInputBox({
            prompt: 'Enter additional context (optional)',
            placeHolder: 'The system needs to handle...',
        });

        // Show deep reasoning panel
        const panel = DeepReasoningPanel.createOrShow(context.extensionUri, deepReasoningManager);

        // Perform reasoning
        try {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Performing deep reasoning...',
                cancellable: false
            }, async () => {
                await deepReasoningManager.performReasoning(problem, context || '');
            });
        } catch (error) {
            window.showErrorMessage(`Failed to perform reasoning: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    // Add verify code command
    const verifyCodeCommand = commands.registerCommand('macoder.verifyCode', async () => {
        // Get active editor
        const editor = window.activeTextEditor;
        if (!editor) {
            window.showErrorMessage('No active editor');
            return;
        }

        // Get selected code or entire document
        const selection = editor.selection;
        const code = selection.isEmpty
            ? editor.document.getText()
            : editor.document.getText(selection);

        if (!code) {
            window.showErrorMessage('No code to verify');
            return;
        }

        // Get language
        const language = editor.document.languageId;

        // Create verification session
        const session = codeVerificationManager.createSession(code, language);

        // Verify code
        try {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Verifying code...',
                cancellable: false
            }, async (progress) => {
                // Verify code
                const results = await codeVerificationManager.verifyCode(session.id);

                // Show results
                let totalIssues = 0;
                for (const result of results.values()) {
                    totalIssues += result.issues.length;
                }

                if (totalIssues === 0) {
                    window.showInformationMessage('Code verification passed with no issues');
                } else {
                    // Show issues in problems panel
                    const diagnosticCollection = vscode.languages.createDiagnosticCollection('macoder-verification');
                    const diagnostics: vscode.Diagnostic[] = [];

                    for (const [verifierName, result] of results.entries()) {
                        for (const issue of result.issues) {
                            const range = new vscode.Range(
                                issue.line ? issue.line - 1 : 0,
                                issue.column ? issue.column - 1 : 0,
                                issue.line ? issue.line - 1 : 0,
                                issue.column ? issue.column - 1 : 100
                            );

                            let severity: vscode.DiagnosticSeverity;
                            switch (issue.type) {
                                case 'error':
                                    severity = vscode.DiagnosticSeverity.Error;
                                    break;
                                case 'warning':
                                    severity = vscode.DiagnosticSeverity.Warning;
                                    break;
                                case 'info':
                                    severity = vscode.DiagnosticSeverity.Information;
                                    break;
                                default:
                                    severity = vscode.DiagnosticSeverity.Information;
                            }

                            const diagnostic = new vscode.Diagnostic(
                                range,
                                `${verifierName}: ${issue.message}`,
                                severity
                            );

                            diagnostics.push(diagnostic);
                        }
                    }

                    diagnosticCollection.set(editor.document.uri, diagnostics);

                    // Show summary message
                    window.showWarningMessage(`Code verification found ${totalIssues} issues`);
                }
            });
        } catch (error) {
            window.showErrorMessage(`Failed to verify code: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    // Add start edit session command
    const startEditSessionCommand = commands.registerCommand('macoder.startEditSession', async () => {
        // Check if code edit logging is enabled
        if (!enableCodeEditLogging || !codeEditTracker) {
            window.showErrorMessage('Code edit logging is disabled. Enable it in settings and reload the window.');
            return;
        }

        // Get description from user
        const description = await window.showInputBox({
            prompt: 'Enter a description for the edit session',
            placeHolder: 'Implementing feature X...',
        });

        if (description === undefined) {
            return; // User cancelled
        }

        // Start a new session
        const sessionId = codeEditTracker.startSession(description || 'Unnamed session');

        // Show confirmation message
        window.showInformationMessage(`Started new edit session${description ? `: ${description}` : ''}`);
    });

    // Add end edit session command
    const endEditSessionCommand = commands.registerCommand('macoder.endEditSession', () => {
        // Check if code edit logging is enabled
        if (!enableCodeEditLogging || !codeEditTracker) {
            window.showErrorMessage('Code edit logging is disabled. Enable it in settings and reload the window.');
            return;
        }

        // End the current session
        codeEditTracker.endCurrentSession();

        // Show confirmation message
        window.showInformationMessage('Ended current edit session');
    });

    // Add show sandbox panel command
    const showSandboxPanelCommand = commands.registerCommand('macoder.showSandboxPanel', () => {
        // Check if sandbox is enabled
        if (!enableSandbox || !sandbox) {
            window.showErrorMessage('Sandbox is disabled. Enable it in settings and reload the window.');
            return;
        }

        SandboxPanel.createOrShow(context.extensionUri, sandbox);
    });

    // Add execute code in sandbox command
    const executeCodeInSandboxCommand = commands.registerCommand('macoder.executeCodeInSandbox', async () => {
        // Check if sandbox is enabled
        if (!enableSandbox || !sandbox) {
            window.showErrorMessage('Sandbox is disabled. Enable it in settings and reload the window.');
            return;
        }

        // Get active editor
        const editor = window.activeTextEditor;
        if (!editor) {
            window.showErrorMessage('No active editor');
            return;
        }

        // Get selected code or entire document
        const selection = editor.selection;
        const code = selection.isEmpty
            ? editor.document.getText()
            : editor.document.getText(selection);

        if (!code) {
            window.showErrorMessage('No code to execute');
            return;
        }

        // Get language
        const language = editor.document.languageId;

        // Show sandbox panel
        const panel = SandboxPanel.createOrShow(context.extensionUri, sandbox);

        // Execute code
        try {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Executing code in sandbox...',
                cancellable: false
            }, async () => {
                await sandbox.executeCode(code, language);
            });
        } catch (error) {
            window.showErrorMessage(`Failed to execute code: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    // Add commands to subscriptions
    context.subscriptions.push(
        startChatCommand,
        nextEditCommand,
        generateCodeCommand,
        explainCodeCommand,
        refactorCodeCommand,
        findBugsCommand,
        generateTestsCommand,
        documentCodeCommand,
        benchmarkModelsCommand,
        toggleModeCommand,
        switchModelProviderCommand,
        toggleAutonomousModeCommand,
        showAutonomousPanelCommand,
        executeTaskCommand,
        refreshIndexCommand,
        showBrainstormingPanelCommand,
        showDeepReasoningPanelCommand,
        performDeepReasoningCommand,
        verifyCodeCommand,
        startEditSessionCommand,
        endEditSessionCommand,
        showSandboxPanelCommand,
        executeCodeInSandboxCommand
    );

    // Create status bar item
    const statusBarItem = window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);

    // Update status bar with current mode
    const updateStatusBar = () => {
        const mode = apiClient.getCurrentMode();
        statusBarItem.text = `$(code) MaCoder [${mode}]`;
        statusBarItem.tooltip = `MaCoder - Using ${modelName} in ${mode} mode`;
    };

    // Initial update
    updateStatusBar();

    // Set command and show
    statusBarItem.command = 'macoder.startChat';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Update status bar when mode changes
    apiClient.onModeChange(() => {
        updateStatusBar();
    });

    // Register completion provider if enabled
    if (enableCompletions) {
        // Create completion provider
        const completionProvider = new MaCoderCompletionItemProvider(apiClient);

        // Register for all languages
        const completionDisposable = languages.registerCompletionItemProvider(
            { pattern: '**' },
            completionProvider,
            '.', ' ', '(', '[', '{', '"', "'"
        );

        context.subscriptions.push(completionDisposable);
    }

    // Register the code edit tracker if enabled
    if (enableCodeEditLogging && codeEditTracker) {
        context.subscriptions.push({
            dispose: () => {
                codeEditTracker?.dispose();
            }
        });
    }
}

/**
 * This method is called when the extension is deactivated.
 */
export function deactivate() {
    console.log('MaCoder extension is now deactivated');
}
