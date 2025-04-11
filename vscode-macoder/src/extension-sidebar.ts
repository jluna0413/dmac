import * as vscode from 'vscode';
import { registerSidebarProviders } from './ui/sidebar';

/**
 * Basic API client for communicating with LLM providers
 */
class ApiClient {
    private modelProvider: string;
    private ollamaModel: string;
    private ollamaUrl: string;
    private openaiApiKey: string;
    private openaiModel: string;
    private geminiApiKey: string;
    private geminiModel: string;
    private temperature: number;
    private maxTokens: number;
    private contextSize: number;
    private outputChannel: vscode.OutputChannel;

    constructor() {
        // Initialize with default values
        this.modelProvider = 'ollama';
        this.ollamaModel = 'codellama';
        this.ollamaUrl = 'http://localhost:11434';
        this.openaiApiKey = '';
        this.openaiModel = 'gpt-3.5-turbo';
        this.geminiApiKey = '';
        this.geminiModel = 'gemini-pro';
        this.temperature = 0.7;
        this.maxTokens = 2048;
        this.contextSize = 4096;
        this.outputChannel = vscode.window.createOutputChannel('MaCoder');

        // Load settings
        this.loadSettings();

        // Listen for settings changes
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('macoder')) {
                this.loadSettings();
            }
        });
    }

    /**
     * Load settings from VS Code configuration
     */
    private loadSettings() {
        const config = vscode.workspace.getConfiguration('macoder');
        this.modelProvider = config.get('modelProvider', this.modelProvider);
        this.ollamaModel = config.get('ollamaModel', this.ollamaModel);
        this.ollamaUrl = config.get('ollamaUrl', this.ollamaUrl);
        this.openaiApiKey = config.get('openaiApiKey', this.openaiApiKey);
        this.openaiModel = config.get('openaiModel', this.openaiModel);
        this.geminiApiKey = config.get('geminiApiKey', this.geminiApiKey);
        this.geminiModel = config.get('geminiModel', this.geminiModel);
        this.temperature = config.get('temperature', this.temperature);
        this.maxTokens = config.get('maxTokens', this.maxTokens);
        this.contextSize = config.get('contextSize', this.contextSize);

        this.log(`Settings loaded: modelProvider=${this.modelProvider}, temperature=${this.temperature}`);
    }

    /**
     * Generate a completion
     * 
     * @param options The completion options
     */
    async generateCompletion(options: any): Promise<any> {
        const { prompt, systemPrompt } = options;
        
        this.log(`Generating completion: prompt=${prompt.substring(0, 50)}...`);
        
        // In a real implementation, this would call the appropriate LLM API
        // For now, we'll just return a mock response
        return {
            text: `Generated response for prompt: ${prompt}\nUsing model provider: ${this.modelProvider}\nModel: ${this.getCurrentModel()}\nSystem prompt: ${systemPrompt || 'None'}`,
            model: this.getCurrentModel(),
            provider: this.modelProvider,
            usage: {
                promptTokens: prompt.length,
                completionTokens: 100,
                totalTokens: prompt.length + 100
            }
        };
    }

    /**
     * Get the current model based on the provider
     */
    private getCurrentModel(): string {
        switch (this.modelProvider) {
            case 'ollama':
                return this.ollamaModel;
            case 'openai':
                return this.openaiModel;
            case 'gemini':
                return this.geminiModel;
            default:
                return 'unknown';
        }
    }

    /**
     * Log a message to the output channel
     * 
     * @param message The message to log
     */
    private log(message: string) {
        const timestamp = new Date().toISOString();
        this.outputChannel.appendLine(`[${timestamp}] ${message}`);
    }

    /**
     * Explain code
     * 
     * @param code The code to explain
     */
    async explainCode(code: string): Promise<string> {
        this.log(`Explaining code: ${code.substring(0, 50)}...`);
        
        // In a real implementation, this would call the appropriate LLM API
        // For now, we'll just return a mock response
        return `Explanation for code:\n${code}\n\nThis code appears to be a simple example.`;
    }

    /**
     * Refactor code
     * 
     * @param code The code to refactor
     * @param instructions The refactoring instructions
     */
    async refactorCode(code: string, instructions: string): Promise<string> {
        this.log(`Refactoring code with instructions: ${instructions}`);
        
        // In a real implementation, this would call the appropriate LLM API
        // For now, we'll just return a mock response
        return `Refactored code based on instructions: ${instructions}\n\n${code}\n// Refactored with improved structure`;
    }

    /**
     * Generate code
     * 
     * @param instructions The code generation instructions
     * @param language The programming language
     */
    async generateCode(instructions: string, language: string = 'javascript'): Promise<string> {
        this.log(`Generating ${language} code with instructions: ${instructions}`);
        
        // In a real implementation, this would call the appropriate LLM API
        // For now, we'll just return a mock response
        return `// Generated ${language} code based on: ${instructions}\nfunction example() {\n  console.log("Hello, world!");\n  // Implementation would go here\n}`;
    }
}

/**
 * Activate the extension
 * 
 * @param context The extension context
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('MaCoder extension is now active!');

    // Create API client
    const apiClient = new ApiClient();

    // Register sidebar providers
    registerSidebarProviders(context, apiClient);

    // Register commands
    const startChatCommand = vscode.commands.registerCommand('macoder.startChat', () => {
        // Focus the chat view
        vscode.commands.executeCommand('macoder.chat.focus');
    });

    const generateCodeCommand = vscode.commands.registerCommand('macoder.generateCode', async () => {
        // Focus the code generation view
        vscode.commands.executeCommand('macoder.codeGeneration.focus');
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

    const startBrainstormingCommand = vscode.commands.registerCommand('macoder.startBrainstorming', () => {
        // Focus the brainstorming view
        vscode.commands.executeCommand('macoder.brainstorming.focus');
    });

    const openSandboxCommand = vscode.commands.registerCommand('macoder.openSandbox', () => {
        // Focus the sandbox view
        vscode.commands.executeCommand('macoder.sandbox.focus');
    });

    const openSettingsCommand = vscode.commands.registerCommand('macoder.openSettings', () => {
        // Focus the settings view
        vscode.commands.executeCommand('macoder.settings.focus');
    });

    const showInfoCommand = vscode.commands.registerCommand('macoder.showInfo', () => {
        vscode.window.showInformationMessage('MaCoder VS Code Extension v0.4.0-alpha');
    });

    // Add commands to subscriptions
    context.subscriptions.push(
        startChatCommand,
        generateCodeCommand,
        explainCodeCommand,
        refactorCodeCommand,
        startBrainstormingCommand,
        openSandboxCommand,
        openSettingsCommand,
        showInfoCommand
    );
}

/**
 * Deactivate the extension
 */
export function deactivate() {}
