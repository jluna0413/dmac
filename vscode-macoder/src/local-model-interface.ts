import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

/**
 * Interface for model providers
 */
export interface ModelProvider {
    /**
     * Get the name of the provider
     */
    getName(): string;

    /**
     * Get available models
     */
    getAvailableModels(): Promise<string[]>;

    /**
     * Generate a completion
     *
     * @param prompt The prompt to complete
     * @param options Additional options
     */
    generateCompletion(prompt: string, options?: any): Promise<string>;

    /**
     * Check if the provider is available
     */
    isAvailable(): Promise<boolean>;
}

/**
 * Ollama model provider
 */
export class OllamaProvider implements ModelProvider {
    private client: AxiosInstance;
    private baseUrl: string;
    private availableModels: string[] = [];

    /**
     * Create a new OllamaProvider
     *
     * @param baseUrl The base URL of the Ollama server
     */
    constructor(baseUrl: string = 'http://localhost:11434') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 60000, // 60 seconds
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
    }

    /**
     * Get the name of the provider
     */
    public getName(): string {
        return 'Ollama';
    }

    /**
     * Get available models
     */
    public async getAvailableModels(): Promise<string[]> {
        try {
            const response = await this.client.get('/api/tags');
            this.availableModels = response.data.models.map((model: any) => model.name);
            return this.availableModels;
        } catch (error) {
            console.error('Error getting available models:', error);
            return [];
        }
    }

    /**
     * Generate a completion
     *
     * @param prompt The prompt to complete
     * @param options Additional options
     */
    public async generateCompletion(prompt: string, options: any = {}): Promise<string> {
        try {
            const model = options.model || 'gemma3:12b';
            const temperature = options.temperature || 0.7;
            const maxTokens = options.maxTokens || 2048;

            const response = await this.client.post('/api/generate', {
                model,
                prompt,
                temperature,
                max_tokens: maxTokens,
                stream: false
            });

            return response.data.response;
        } catch (error) {
            console.error('Error generating completion:', error);
            throw new Error('Failed to generate completion');
        }
    }

    /**
     * Check if the provider is available
     */
    public async isAvailable(): Promise<boolean> {
        try {
            await this.client.get('/api/tags');
            return true;
        } catch (error) {
            return false;
        }
    }
}

/**
 * LM Studio model provider
 */
export class LMStudioProvider implements ModelProvider {
    private client: AxiosInstance;
    private baseUrl: string;
    private availableModels: string[] = [];

    /**
     * Create a new LMStudioProvider
     *
     * @param baseUrl The base URL of the LM Studio server
     */
    constructor(baseUrl: string = 'http://localhost:1234') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 60000, // 60 seconds
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
    }

    /**
     * Get the name of the provider
     */
    public getName(): string {
        return 'LM Studio';
    }

    /**
     * Get available models
     */
    public async getAvailableModels(): Promise<string[]> {
        try {
            // LM Studio doesn't have an API to list models
            // Return a default model
            this.availableModels = ['default'];
            return this.availableModels;
        } catch (error) {
            console.error('Error getting available models:', error);
            return [];
        }
    }

    /**
     * Generate a completion
     *
     * @param prompt The prompt to complete
     * @param options Additional options
     */
    public async generateCompletion(prompt: string, options: any = {}): Promise<string> {
        try {
            const temperature = options.temperature || 0.7;
            const maxTokens = options.maxTokens || 2048;

            // LM Studio uses OpenAI-compatible API
            const response = await this.client.post('/v1/completions', {
                prompt,
                temperature,
                max_tokens: maxTokens,
                stream: false
            });

            // Extract the completion from the response
            if (response.data.choices && response.data.choices.length > 0) {
                return response.data.choices[0].text;
            }

            throw new Error('No completion in response');
        } catch (error) {
            console.error('Error generating completion:', error);
            throw new Error('Failed to generate completion');
        }
    }

    /**
     * Check if the provider is available
     */
    public async isAvailable(): Promise<boolean> {
        try {
            // Try to access the models endpoint
            await this.client.get('/v1/models');
            return true;
        } catch (error) {
            return false;
        }
    }
}

/**
 * Local model interface for MaCoder
 */
export class LocalModelInterface {
    private static instance: LocalModelInterface;
    private providers: Map<string, ModelProvider> = new Map();
    private activeProvider: ModelProvider | null = null;
    private cacheDir: string;

    /**
     * Create a new LocalModelInterface
     */
    private constructor() {
        // Create cache directory
        this.cacheDir = path.join(os.homedir(), '.macoder', 'cache');
        if (!fs.existsSync(this.cacheDir)) {
            fs.mkdirSync(this.cacheDir, { recursive: true });
        }

        // Initialize providers
        this.initializeProviders();
    }

    /**
     * Get the singleton instance
     */
    public static getInstance(): LocalModelInterface {
        if (!LocalModelInterface.instance) {
            LocalModelInterface.instance = new LocalModelInterface();
        }
        return LocalModelInterface.instance;
    }

    /**
     * Initialize model providers
     */
    private async initializeProviders(): Promise<void> {
        // Get configuration
        const config = vscode.workspace.getConfiguration('macoder');
        const preferredProvider = config.get<string>('localModelProvider') || 'ollama';
        const ollamaUrl = config.get<string>('ollamaUrl') || 'http://localhost:11434';
        const lmStudioUrl = config.get<string>('lmStudioUrl') || 'http://localhost:1234';

        // Add Ollama provider
        const ollamaProvider = new OllamaProvider(ollamaUrl);
        this.providers.set('ollama', ollamaProvider);

        // Add LM Studio provider
        const lmStudioProvider = new LMStudioProvider(lmStudioUrl);
        this.providers.set('lmstudio', lmStudioProvider);

        // Try to set active provider based on preference
        let providerSet = false;

        if (preferredProvider === 'ollama') {
            if (await ollamaProvider.isAvailable()) {
                this.activeProvider = ollamaProvider;
                console.log('Using Ollama as active provider');
                providerSet = true;
            }
        } else if (preferredProvider === 'lmstudio') {
            if (await lmStudioProvider.isAvailable()) {
                this.activeProvider = lmStudioProvider;
                console.log('Using LM Studio as active provider');
                providerSet = true;
            }
        }

        // If preferred provider is not available, try others
        if (!providerSet) {
            if (await ollamaProvider.isAvailable()) {
                this.activeProvider = ollamaProvider;
                console.log('Using Ollama as active provider (fallback)');
                providerSet = true;
            } else if (await lmStudioProvider.isAvailable()) {
                this.activeProvider = lmStudioProvider;
                console.log('Using LM Studio as active provider (fallback)');
                providerSet = true;
            } else {
                console.log('No model providers available');
            }
        }
    }

    /**
     * Get available providers
     */
    public getProviders(): Map<string, ModelProvider> {
        return this.providers;
    }

    /**
     * Get active provider
     */
    public getActiveProvider(): ModelProvider | null {
        return this.activeProvider;
    }

    /**
     * Set active provider
     *
     * @param providerName The name of the provider to set as active
     */
    public setActiveProvider(providerName: string): boolean {
        const provider = this.providers.get(providerName);
        if (provider) {
            this.activeProvider = provider;
            return true;
        }
        return false;
    }

    /**
     * Restart with a specific provider
     *
     * @param providerName The name of the provider to use
     */
    public async restartWithProvider(providerName: string): Promise<boolean> {
        const provider = this.providers.get(providerName);
        if (!provider) {
            return false;
        }

        // Check if provider is available
        if (await provider.isAvailable()) {
            this.activeProvider = provider;
            console.log(`Switched to ${providerName} provider`);
            return true;
        } else {
            console.log(`Provider ${providerName} is not available`);
            return false;
        }
    }

    /**
     * Generate code based on a prompt
     *
     * @param prompt The prompt for code generation
     * @param language The programming language
     * @param model The model to use
     * @returns The generated code
     */
    public async generateCode(prompt: string, language?: string, model?: string): Promise<any> {
        if (!this.activeProvider) {
            throw new Error('No active model provider');
        }

        try {
            // Create a more specific prompt for code generation
            const enhancedPrompt = this.createCodeGenerationPrompt(prompt, language);

            // Generate completion
            const completion = await this.activeProvider.generateCompletion(enhancedPrompt, {
                model: model || 'gemma3:12b',
                temperature: 0.2, // Lower temperature for code generation
                maxTokens: 2048
            });

            // Extract code from completion
            const code = this.extractCodeFromCompletion(completion, language);

            return {
                success: true,
                code,
                model: model || 'gemma3:12b'
            };
        } catch (error) {
            console.error('Error generating code:', error);
            return {
                success: false,
                error: 'Failed to generate code'
            };
        }
    }

    /**
     * Complete code at a specific position
     *
     * @param code The existing code
     * @param cursorPosition The position of the cursor in the code
     * @param language The programming language
     * @param model The model to use
     * @returns The completion suggestion
     */
    public async completeCode(code: string, cursorPosition: number, language?: string, model?: string): Promise<any> {
        if (!this.activeProvider) {
            throw new Error('No active model provider');
        }

        try {
            // Split code at cursor position
            const beforeCursor = code.substring(0, cursorPosition);
            const afterCursor = code.substring(cursorPosition);

            // Create prompt for code completion
            const prompt = this.createCodeCompletionPrompt(beforeCursor, afterCursor, language);

            // Generate completion
            const completion = await this.activeProvider.generateCompletion(prompt, {
                model: model || 'gemma3:12b',
                temperature: 0.1, // Very low temperature for completions
                maxTokens: 512
            });

            // Extract completion
            const suggestion = this.extractCompletionSuggestion(completion);

            return {
                success: true,
                suggestion,
                model: model || 'gemma3:12b'
            };
        } catch (error) {
            console.error('Error completing code:', error);
            return {
                success: false,
                error: 'Failed to complete code'
            };
        }
    }

    /**
     * Explain what code does
     *
     * @param code The code to explain
     * @param language The programming language
     * @param model The model to use
     * @returns The explanation of the code
     */
    public async explainCode(code: string, language?: string, model?: string): Promise<any> {
        if (!this.activeProvider) {
            throw new Error('No active model provider');
        }

        try {
            // Create prompt for code explanation
            const prompt = this.createCodeExplanationPrompt(code, language);

            // Generate explanation
            const explanation = await this.activeProvider.generateCompletion(prompt, {
                model: model || 'gemma3:12b',
                temperature: 0.7,
                maxTokens: 2048
            });

            return {
                success: true,
                explanation,
                model: model || 'gemma3:12b'
            };
        } catch (error) {
            console.error('Error explaining code:', error);
            return {
                success: false,
                error: 'Failed to explain code'
            };
        }
    }

    /**
     * Refactor code according to instructions
     *
     * @param code The code to refactor
     * @param instructions The instructions for refactoring
     * @param language The programming language
     * @param model The model to use
     * @returns The refactored code
     */
    public async refactorCode(code: string, instructions: string, language?: string, model?: string): Promise<any> {
        if (!this.activeProvider) {
            throw new Error('No active model provider');
        }

        try {
            // Create prompt for code refactoring
            const prompt = this.createCodeRefactoringPrompt(code, instructions, language);

            // Generate refactored code
            const completion = await this.activeProvider.generateCompletion(prompt, {
                model: model || 'gemma3:12b',
                temperature: 0.3,
                maxTokens: 4096
            });

            // Extract code from completion
            const refactoredCode = this.extractCodeFromCompletion(completion, language);

            return {
                success: true,
                code: refactoredCode,
                model: model || 'gemma3:12b'
            };
        } catch (error) {
            console.error('Error refactoring code:', error);
            return {
                success: false,
                error: 'Failed to refactor code'
            };
        }
    }

    /**
     * Find potential bugs in code
     *
     * @param code The code to analyze
     * @param language The programming language
     * @param model The model to use
     * @returns The list of potential bugs
     */
    public async findBugs(code: string, language?: string, model?: string): Promise<any> {
        if (!this.activeProvider) {
            throw new Error('No active model provider');
        }

        try {
            // Create prompt for bug finding
            const prompt = this.createBugFindingPrompt(code, language);

            // Generate bug analysis
            const analysis = await this.activeProvider.generateCompletion(prompt, {
                model: model || 'gemma3:12b',
                temperature: 0.3,
                maxTokens: 2048
            });

            // Parse bugs from analysis
            const { bugs, fixedCode } = this.parseBugsFromAnalysis(analysis, code);

            return {
                success: true,
                bugs,
                fixedCode,
                model: model || 'gemma3:12b'
            };
        } catch (error) {
            console.error('Error finding bugs:', error);
            return {
                success: false,
                error: 'Failed to find bugs'
            };
        }
    }

    /**
     * Generate unit tests for code
     *
     * @param code The code to test
     * @param language The programming language
     * @param model The model to use
     * @returns The generated tests
     */
    public async generateTests(code: string, language?: string, model?: string): Promise<any> {
        if (!this.activeProvider) {
            throw new Error('No active model provider');
        }

        try {
            // Create prompt for test generation
            const prompt = this.createTestGenerationPrompt(code, language);

            // Generate tests
            const completion = await this.activeProvider.generateCompletion(prompt, {
                model: model || 'gemma3:12b',
                temperature: 0.3,
                maxTokens: 4096
            });

            // Extract tests from completion
            const tests = this.extractCodeFromCompletion(completion, language);

            return {
                success: true,
                tests,
                model: model || 'gemma3:12b'
            };
        } catch (error) {
            console.error('Error generating tests:', error);
            return {
                success: false,
                error: 'Failed to generate tests'
            };
        }
    }

    /**
     * Add documentation to code
     *
     * @param code The code to document
     * @param language The programming language
     * @param model The model to use
     * @returns The documented code
     */
    public async documentCode(code: string, language?: string, model?: string): Promise<any> {
        if (!this.activeProvider) {
            throw new Error('No active model provider');
        }

        try {
            // Create prompt for documentation
            const prompt = this.createDocumentationPrompt(code, language);

            // Generate documented code
            const completion = await this.activeProvider.generateCompletion(prompt, {
                model: model || 'gemma3:12b',
                temperature: 0.3,
                maxTokens: 4096
            });

            // Extract code from completion
            const documentedCode = this.extractCodeFromCompletion(completion, language);

            return {
                success: true,
                code: documentedCode,
                model: model || 'gemma3:12b'
            };
        } catch (error) {
            console.error('Error documenting code:', error);
            return {
                success: false,
                error: 'Failed to document code'
            };
        }
    }

    /**
     * Create a prompt for code generation
     *
     * @param prompt The user prompt
     * @param language The programming language
     * @returns The enhanced prompt
     */
    private createCodeGenerationPrompt(prompt: string, language?: string): string {
        const langSpecific = language ? `in ${language}` : '';
        return `You are an expert programmer. Generate high-quality, efficient, and well-documented code ${langSpecific} based on the following request:

${prompt}

Provide only the code without any explanations or markdown formatting. Make sure the code is complete, correct, and follows best practices.`;
    }

    /**
     * Create a prompt for code completion
     *
     * @param beforeCursor The code before the cursor
     * @param afterCursor The code after the cursor
     * @param language The programming language
     * @returns The prompt
     */
    private createCodeCompletionPrompt(beforeCursor: string, afterCursor: string, language?: string): string {
        const langSpecific = language ? `The code is written in ${language}.` : '';
        return `You are an expert programmer. ${langSpecific} Complete the following code snippet. The cursor position is marked with [CURSOR].

${beforeCursor}[CURSOR]${afterCursor}

Provide only the completion at the cursor position without any explanations or markdown formatting. Do not repeat the existing code.`;
    }

    /**
     * Create a prompt for code explanation
     *
     * @param code The code to explain
     * @param language The programming language
     * @returns The prompt
     */
    private createCodeExplanationPrompt(code: string, language?: string): string {
        const langSpecific = language ? `This is ${language} code.` : '';
        return `You are an expert programmer. ${langSpecific} Explain the following code in detail:

\`\`\`
${code}
\`\`\`

Provide a comprehensive explanation including:
1. What the code does at a high level
2. How it works step by step
3. Any important patterns or techniques used
4. Potential issues or improvements

Format your response in markdown.`;
    }

    /**
     * Create a prompt for code refactoring
     *
     * @param code The code to refactor
     * @param instructions The refactoring instructions
     * @param language The programming language
     * @returns The prompt
     */
    private createCodeRefactoringPrompt(code: string, instructions: string, language?: string): string {
        const langSpecific = language ? `This is ${language} code.` : '';
        return `You are an expert programmer. ${langSpecific} Refactor the following code according to these instructions:

INSTRUCTIONS:
${instructions}

CODE:
\`\`\`
${code}
\`\`\`

Provide only the refactored code without any explanations or markdown formatting. Make sure the refactored code is complete, correct, and follows best practices.`;
    }

    /**
     * Create a prompt for bug finding
     *
     * @param code The code to analyze
     * @param language The programming language
     * @returns The prompt
     */
    private createBugFindingPrompt(code: string, language?: string): string {
        const langSpecific = language ? `This is ${language} code.` : '';
        return `You are an expert programmer and code reviewer. ${langSpecific} Analyze the following code for bugs, errors, and potential issues:

\`\`\`
${code}
\`\`\`

First, list all bugs and issues you find in a structured format with the following for each issue:
1. Title: A short description of the issue
2. Description: A detailed explanation of the problem
3. Location: Where in the code the issue occurs
4. Severity: How serious the issue is (Critical, High, Medium, Low)

Then, provide a fixed version of the entire code that addresses all the issues you identified.

Format your response as follows:

BUGS:
[List of bugs in the format described above]

FIXED CODE:
\`\`\`
[The complete fixed code]
\`\`\``;
    }

    /**
     * Create a prompt for test generation
     *
     * @param code The code to test
     * @param language The programming language
     * @returns The prompt
     */
    private createTestGenerationPrompt(code: string, language?: string): string {
        const langSpecific = language ? `This is ${language} code.` : '';
        let testFramework = '';

        if (language) {
            switch (language.toLowerCase()) {
                case 'javascript':
                    testFramework = 'Jest';
                    break;
                case 'typescript':
                    testFramework = 'Jest';
                    break;
                case 'python':
                    testFramework = 'pytest';
                    break;
                case 'java':
                    testFramework = 'JUnit';
                    break;
                case 'csharp':
                    testFramework = 'NUnit or MSTest';
                    break;
                default:
                    testFramework = 'a standard testing framework';
            }
        }

        return `You are an expert programmer and test engineer. ${langSpecific} Generate comprehensive unit tests for the following code using ${testFramework}:

\`\`\`
${code}
\`\`\`

Create tests that:
1. Cover all functions and methods
2. Test both normal and edge cases
3. Verify error handling
4. Achieve high code coverage

Provide only the test code without any explanations or markdown formatting. Make sure the tests are complete, correct, and follow best practices.`;
    }

    /**
     * Create a prompt for documentation
     *
     * @param code The code to document
     * @param language The programming language
     * @returns The prompt
     */
    private createDocumentationPrompt(code: string, language?: string): string {
        const langSpecific = language ? `This is ${language} code.` : '';
        let docStyle = '';

        if (language) {
            switch (language.toLowerCase()) {
                case 'javascript':
                case 'typescript':
                    docStyle = 'JSDoc';
                    break;
                case 'python':
                    docStyle = 'docstrings (Google style)';
                    break;
                case 'java':
                    docStyle = 'Javadoc';
                    break;
                case 'csharp':
                    docStyle = 'XML documentation comments';
                    break;
                default:
                    docStyle = 'standard documentation comments';
            }
        }

        return `You are an expert programmer and technical writer. ${langSpecific} Add comprehensive documentation to the following code using ${docStyle}:

\`\`\`
${code}
\`\`\`

Add documentation that:
1. Describes the purpose of each function, class, and method
2. Documents parameters, return values, and exceptions
3. Provides usage examples where appropriate
4. Explains complex logic or algorithms

Provide only the documented code without any explanations or markdown formatting. Make sure the documentation is clear, accurate, and follows best practices.`;
    }

    /**
     * Extract code from a completion
     *
     * @param completion The completion text
     * @param language The programming language
     * @returns The extracted code
     */
    private extractCodeFromCompletion(completion: string, language?: string): string {
        // Try to extract code from markdown code blocks
        const codeBlockRegex = /```(?:\w+)?\s*\n([\s\S]*?)```/g;
        const matches = [...completion.matchAll(codeBlockRegex)];

        if (matches.length > 0) {
            // Return the largest code block (most likely the main code)
            return matches.reduce((longest, match) =>
                match[1].length > longest.length ? match[1] : longest, '');
        }

        // If no code blocks found, return the raw completion
        return completion;
    }

    /**
     * Extract completion suggestion
     *
     * @param completion The completion text
     * @returns The extracted suggestion
     */
    private extractCompletionSuggestion(completion: string): string {
        // Remove any markdown formatting or explanations
        return completion.trim();
    }

    /**
     * Parse bugs from analysis
     *
     * @param analysis The bug analysis text
     * @param originalCode The original code
     * @returns The parsed bugs and fixed code
     */
    private parseBugsFromAnalysis(analysis: string, originalCode: string): { bugs: any[], fixedCode: string } {
        const bugs: any[] = [];
        let fixedCode = '';

        // Extract bugs section
        const bugsMatch = analysis.match(/BUGS:\s*([\s\S]*?)(?:FIXED CODE:|$)/i);
        if (bugsMatch && bugsMatch[1]) {
            const bugsText = bugsMatch[1].trim();

            // Simple parsing for bug entries (this could be improved)
            const bugEntries = bugsText.split(/(?:\d+\.\s+|\n\n+)/).filter(entry => entry.trim().length > 0);

            for (const entry of bugEntries) {
                const titleMatch = entry.match(/Title:\s*(.*?)(?:\n|$)/i);
                const descriptionMatch = entry.match(/Description:\s*(.*?)(?:\n(?!Description:|Location:|Severity:)|$)/is);
                const locationMatch = entry.match(/Location:\s*(.*?)(?:\n|$)/i);
                const severityMatch = entry.match(/Severity:\s*(.*?)(?:\n|$)/i);

                if (titleMatch) {
                    bugs.push({
                        title: titleMatch[1].trim(),
                        description: descriptionMatch ? descriptionMatch[1].trim() : '',
                        location: locationMatch ? locationMatch[1].trim() : '',
                        severity: severityMatch ? severityMatch[1].trim() : 'Medium'
                    });
                }
            }
        }

        // Extract fixed code
        const fixedCodeMatch = analysis.match(/FIXED CODE:\s*```(?:\w+)?\s*\n([\s\S]*?)```/i);
        if (fixedCodeMatch && fixedCodeMatch[1]) {
            fixedCode = fixedCodeMatch[1].trim();
        } else {
            // If no fixed code section found, use original code
            fixedCode = originalCode;
        }

        return { bugs, fixedCode };
    }
}
