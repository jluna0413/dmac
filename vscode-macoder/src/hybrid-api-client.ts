import * as vscode from 'vscode';
import { MaCoderApiClient } from './api-client';
import { StandaloneApiClient } from './standalone-api-client';

/**
 * Hybrid API client for MaCoder that can work with or without the DMac server.
 * It automatically switches between server mode and standalone mode based on availability.
 */
export class HybridApiClient {
    private dmacClient: MaCoderApiClient;
    private standaloneClient: StandaloneApiClient;
    private preferStandalone: boolean;
    private isDmacAvailable: boolean = false;
    private activeClient: 'dmac' | 'standalone' = 'standalone';
    private modelName: string;
    private modeChangeListeners: Array<() => void> = [];

    /**
     * Create a new HybridApiClient.
     *
     * @param serverUrl The base URL of the DMac server
     * @param modelName The name of the model to use
     * @param preferStandalone Whether to prefer standalone mode even if DMac is available
     */
    constructor(serverUrl: string, modelName: string, preferStandalone: boolean = false) {
        this.modelName = modelName;
        this.preferStandalone = preferStandalone;

        // Create both clients
        this.dmacClient = new MaCoderApiClient(serverUrl, modelName);
        this.standaloneClient = new StandaloneApiClient(modelName);

        // Initialize with standalone client as default
        this.activeClient = 'standalone';

        // Check DMac availability
        this.checkDmacAvailability(serverUrl);
    }

    /**
     * Check if DMac server is available
     *
     * @param serverUrl The base URL of the DMac server
     */
    private async checkDmacAvailability(serverUrl: string): Promise<void> {
        try {
            // Store previous state
            const previousMode = this.activeClient;
            const previousAvailability = this.isDmacAvailable;

            // Try to connect to DMac server
            const result = await this.dmacClient.getProjectSummary();
            this.isDmacAvailable = result.success || (result.error && result.error.includes('not found'));

            // Set active client based on availability and preference
            if (this.isDmacAvailable && !this.preferStandalone) {
                this.activeClient = 'dmac';
                console.log('DMac server is available, using DMac client');
            } else {
                this.activeClient = 'standalone';
                console.log('Using standalone client' + (this.isDmacAvailable ? ' (by preference)' : ' (DMac unavailable)'));
            }

            // Notify listeners if mode or availability changed
            if (previousMode !== this.activeClient || previousAvailability !== this.isDmacAvailable) {
                this.notifyModeChangeListeners();
            }
        } catch (error) {
            // Store previous state
            const previousMode = this.activeClient;
            const previousAvailability = this.isDmacAvailable;

            this.isDmacAvailable = false;
            this.activeClient = 'standalone';
            console.log('DMac server is not available, using standalone client');

            // Notify listeners if mode or availability changed
            if (previousMode !== this.activeClient || previousAvailability !== this.isDmacAvailable) {
                this.notifyModeChangeListeners();
            }
        }
    }

    /**
     * Set the model name.
     *
     * @param modelName The name of the model to use
     */
    public setModelName(modelName: string): void {
        this.modelName = modelName;
        this.dmacClient.setModelName(modelName);
        this.standaloneClient.setModelName(modelName);
    }

    /**
     * Set the preferred mode.
     *
     * @param preferStandalone Whether to prefer standalone mode even if DMac is available
     */
    public setPreferredMode(preferStandalone: boolean): void {
        this.preferStandalone = preferStandalone;

        // Store previous mode
        const previousMode = this.activeClient;

        // Update active client based on new preference
        if (this.isDmacAvailable && !this.preferStandalone) {
            this.activeClient = 'dmac';
            console.log('Switched to DMac client');
        } else {
            this.activeClient = 'standalone';
            console.log('Switched to standalone client');
        }

        // Notify listeners if mode changed
        if (previousMode !== this.activeClient) {
            this.notifyModeChangeListeners();
        }
    }

    /**
     * Register a listener for mode changes.
     *
     * @param listener The listener function to call when mode changes
     */
    public onModeChange(listener: () => void): void {
        this.modeChangeListeners.push(listener);
    }

    /**
     * Notify all mode change listeners.
     */
    private notifyModeChangeListeners(): void {
        for (const listener of this.modeChangeListeners) {
            try {
                listener();
            } catch (error) {
                console.error('Error in mode change listener:', error);
            }
        }
    }

    /**
     * Get the current mode.
     *
     * @returns The current mode ('dmac' or 'standalone')
     */
    public getCurrentMode(): 'dmac' | 'standalone' {
        return this.activeClient;
    }

    /**
     * Check if DMac is available.
     *
     * @returns Whether DMac is available
     */
    public isDmacServerAvailable(): boolean {
        return this.isDmacAvailable;
    }

    /**
     * Search for code matching a query.
     *
     * @param query The search query
     * @param maxResults The maximum number of results to return
     * @returns The search results
     */
    public async searchCode(query: string, maxResults: number = 10): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.searchCode(query, maxResults);
        } else {
            return this.standaloneClient.searchCode(query, maxResults);
        }
    }

    /**
     * Get the content of a file.
     *
     * @param filePath The path to the file
     * @returns The file content
     */
    public async getFileContent(filePath: string): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.getFileContent(filePath);
        } else {
            return this.standaloneClient.getFileContent(filePath);
        }
    }

    /**
     * Generate code based on a prompt.
     *
     * @param prompt The prompt for code generation
     * @param language The programming language
     * @returns The generated code
     */
    public async generateCode(prompt: string, language?: string): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.generateCode(prompt, language);
        } else {
            return this.standaloneClient.generateCode(prompt, language);
        }
    }

    /**
     * Complete code at a specific position.
     *
     * @param code The existing code
     * @param cursorPosition The position of the cursor in the code
     * @param language The programming language
     * @returns The completion suggestion
     */
    public async completeCode(code: string, cursorPosition: number, language?: string): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.completeCode(code, cursorPosition, language);
        } else {
            return this.standaloneClient.completeCode(code, cursorPosition, language);
        }
    }

    /**
     * Explain what code does.
     *
     * @param code The code to explain
     * @param language The programming language
     * @returns The explanation of the code
     */
    public async explainCode(code: string, language?: string): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.explainCode(code, language);
        } else {
            return this.standaloneClient.explainCode(code, language);
        }
    }

    /**
     * Refactor code according to instructions.
     *
     * @param code The code to refactor
     * @param instructions The instructions for refactoring
     * @param language The programming language
     * @returns The refactored code
     */
    public async refactorCode(code: string, instructions: string, language?: string): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.refactorCode(code, instructions, language);
        } else {
            return this.standaloneClient.refactorCode(code, instructions, language);
        }
    }

    /**
     * Find potential bugs in code.
     *
     * @param code The code to analyze
     * @param language The programming language
     * @returns The list of potential bugs
     */
    public async findBugs(code: string, language?: string): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.findBugs(code, language);
        } else {
            return this.standaloneClient.findBugs(code, language);
        }
    }

    /**
     * Generate unit tests for code.
     *
     * @param code The code to test
     * @param language The programming language
     * @returns The generated tests
     */
    public async generateTests(code: string, language?: string): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.generateTests(code, language);
        } else {
            return this.standaloneClient.generateTests(code, language);
        }
    }

    /**
     * Add documentation to code.
     *
     * @param code The code to document
     * @param language The programming language
     * @returns The documented code
     */
    public async documentCode(code: string, language?: string): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.documentCode(code, language);
        } else {
            return this.standaloneClient.documentCode(code, language);
        }
    }

    /**
     * Get a summary of the project.
     *
     * @returns The project summary
     */
    public async getProjectSummary(): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.getProjectSummary();
        } else {
            return this.standaloneClient.getProjectSummary();
        }
    }

    /**
     * Refresh the code index.
     *
     * @returns Success status
     */
    public async refreshIndex(): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.refreshIndex();
        } else {
            return this.standaloneClient.refreshIndex();
        }
    }

    /**
     * Benchmark models.
     *
     * @param task The task to benchmark
     * @param models The models to benchmark
     * @param data Additional data for the task
     * @returns The benchmark results
     */
    public async benchmarkModels(task: string, models: string[], data: any = {}): Promise<any> {
        if (this.activeClient === 'dmac') {
            return this.dmacClient.benchmarkModels(task, models, data);
        } else {
            return this.standaloneClient.benchmarkModels(task, models, data);
        }
    }
}
