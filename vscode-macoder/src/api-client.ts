import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import * as vscode from 'vscode';

/**
 * API client for communicating with the MaCoder server.
 */
export class MaCoderApiClient {
    private client: AxiosInstance;
    private baseUrl: string;
    private modelName: string;

    /**
     * Create a new MaCoderApiClient.
     * 
     * @param baseUrl The base URL of the MaCoder server
     * @param modelName The name of the model to use
     */
    constructor(baseUrl: string, modelName: string) {
        this.baseUrl = baseUrl;
        this.modelName = modelName;

        // Create axios client
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 30000, // 30 seconds
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        // Add request interceptor for logging
        this.client.interceptors.request.use((config) => {
            console.log(`MaCoder API request: ${config.method?.toUpperCase()} ${config.url}`);
            return config;
        });

        // Add response interceptor for logging
        this.client.interceptors.response.use(
            (response) => {
                console.log(`MaCoder API response: ${response.status} ${response.statusText}`);
                return response;
            },
            (error) => {
                console.error(`MaCoder API error: ${error.message}`);
                return Promise.reject(error);
            }
        );
    }

    /**
     * Set the model name.
     * 
     * @param modelName The name of the model to use
     */
    public setModelName(modelName: string): void {
        this.modelName = modelName;
    }

    /**
     * Search for code matching a query.
     * 
     * @param query The search query
     * @param maxResults The maximum number of results to return
     * @returns The search results
     */
    public async searchCode(query: string, maxResults: number = 10): Promise<any> {
        try {
            const response = await this.client.post('/api/macoder/search', {
                query,
                max_results: maxResults,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error searching code');
            return { success: false, error: 'Error searching code' };
        }
    }

    /**
     * Get the content of a file.
     * 
     * @param filePath The path to the file
     * @returns The file content
     */
    public async getFileContent(filePath: string): Promise<any> {
        try {
            const response = await this.client.post('/api/macoder/file', {
                file_path: filePath,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error getting file content');
            return { success: false, error: 'Error getting file content' };
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
        try {
            const response = await this.client.post('/api/macoder/generate', {
                prompt,
                language,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error generating code');
            return { success: false, error: 'Error generating code' };
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
        try {
            const response = await this.client.post('/api/macoder/complete', {
                code,
                cursor_position: cursorPosition,
                language,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error completing code');
            return { success: false, error: 'Error completing code' };
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
        try {
            const response = await this.client.post('/api/macoder/explain', {
                code,
                language,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error explaining code');
            return { success: false, error: 'Error explaining code' };
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
        try {
            const response = await this.client.post('/api/macoder/refactor', {
                code,
                instructions,
                language,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error refactoring code');
            return { success: false, error: 'Error refactoring code' };
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
        try {
            const response = await this.client.post('/api/macoder/bugs', {
                code,
                language,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error finding bugs');
            return { success: false, error: 'Error finding bugs' };
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
        try {
            const response = await this.client.post('/api/macoder/tests', {
                code,
                language,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error generating tests');
            return { success: false, error: 'Error generating tests' };
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
        try {
            const response = await this.client.post('/api/macoder/document', {
                code,
                language,
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error documenting code');
            return { success: false, error: 'Error documenting code' };
        }
    }

    /**
     * Get a summary of the project.
     * 
     * @returns The project summary
     */
    public async getProjectSummary(): Promise<any> {
        try {
            const response = await this.client.post('/api/macoder/summary', {
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error getting project summary');
            return { success: false, error: 'Error getting project summary' };
        }
    }

    /**
     * Refresh the code index.
     * 
     * @returns Success status
     */
    public async refreshIndex(): Promise<any> {
        try {
            const response = await this.client.post('/api/macoder/refresh', {
                model: this.modelName
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error refreshing index');
            return { success: false, error: 'Error refreshing index' };
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
        try {
            const response = await this.client.post('/api/macoder/benchmark', {
                task,
                models,
                ...data
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Error benchmarking models');
            return { success: false, error: 'Error benchmarking models' };
        }
    }

    /**
     * Handle API errors.
     * 
     * @param error The error object
     * @param defaultMessage The default error message
     */
    private handleError(error: any, defaultMessage: string): void {
        if (axios.isAxiosError(error)) {
            const errorMessage = error.response?.data?.error || error.message || defaultMessage;
            vscode.window.showErrorMessage(`MaCoder API Error: ${errorMessage}`);
        } else {
            vscode.window.showErrorMessage(`MaCoder API Error: ${defaultMessage}`);
        }
        console.error('MaCoder API Error:', error);
    }
}
