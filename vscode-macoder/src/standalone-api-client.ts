import * as vscode from 'vscode';
import * as path from 'path';
import { LocalModelInterface } from './local-model-interface';
import { ProjectIndexer, FileIndexEntry } from './project-indexer';

/**
 * Standalone API client for MaCoder that works without the DMac server.
 */
export class StandaloneApiClient {
    private modelInterface: LocalModelInterface;
    private modelName: string;
    private projectIndexer: ProjectIndexer;

    /**
     * Create a new StandaloneApiClient.
     *
     * @param modelName The name of the model to use
     */
    constructor(modelName: string = 'gemma3:12b') {
        this.modelName = modelName;
        this.modelInterface = LocalModelInterface.getInstance();
        this.projectIndexer = ProjectIndexer.getInstance();

        // Start indexing the workspace
        this.projectIndexer.indexAllWorkspaces().catch(error => {
            console.error('Error indexing workspace:', error);
        });
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
            // Get active workspace folder
            const activeWorkspace = vscode.workspace.workspaceFolders?.[0];
            if (!activeWorkspace) {
                return {
                    success: false,
                    error: 'No workspace folder open',
                    message: 'Please open a workspace folder to search code.'
                };
            }

            // Search for files matching the query
            const files = await this.projectIndexer.searchFiles(query, {
                workspacePath: activeWorkspace.uri.fsPath,
                maxResults
            });

            // Search for symbols matching the query
            const symbols = await this.projectIndexer.searchSymbols(query, {
                workspacePath: activeWorkspace.uri.fsPath,
                maxResults
            });

            // Format results
            const fileResults = files.map(file => ({
                path: file.relativePath,
                name: path.basename(file.relativePath),
                language: file.language,
                type: 'file'
            }));

            const symbolResults = symbols.map(({ file, symbol }) => ({
                path: file.relativePath,
                name: symbol.name,
                language: file.language,
                type: 'symbol',
                symbolKind: symbol.kind,
                range: symbol.range
            }));

            // Combine results
            const results = [...fileResults, ...symbolResults].slice(0, maxResults);

            return {
                success: true,
                results,
                count: results.length,
                message: `Found ${results.length} results for "${query}"`
            };
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
            // In standalone mode, we can use VS Code API to get file content
            const uri = vscode.Uri.file(filePath);
            const document = await vscode.workspace.openTextDocument(uri);
            const content = document.getText();

            return {
                success: true,
                content,
                language: document.languageId
            };
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
            return await this.modelInterface.generateCode(prompt, language, this.modelName);
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
            return await this.modelInterface.completeCode(code, cursorPosition, language, this.modelName);
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
            return await this.modelInterface.explainCode(code, language, this.modelName);
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
            return await this.modelInterface.refactorCode(code, instructions, language, this.modelName);
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
            return await this.modelInterface.findBugs(code, language, this.modelName);
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
            return await this.modelInterface.generateTests(code, language, this.modelName);
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
            return await this.modelInterface.documentCode(code, language, this.modelName);
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
            // Get active workspace folder
            const activeWorkspace = vscode.workspace.workspaceFolders?.[0];
            if (!activeWorkspace) {
                return {
                    success: false,
                    error: 'No workspace folder open',
                    message: 'Please open a workspace folder to get a project summary.'
                };
            }

            // Get index for the workspace
            const index = this.projectIndexer.getIndex(activeWorkspace.uri.fsPath);

            if (!index) {
                // Index not available yet, trigger indexing
                this.projectIndexer.refreshIndex(activeWorkspace.uri.fsPath);

                return {
                    success: false,
                    error: 'Project index not available',
                    message: 'The project is being indexed. Please try again later.'
                };
            }

            // Count files by language
            const languageCounts: { [key: string]: number } = {};
            for (const file of index.files.values()) {
                if (!languageCounts[file.language]) {
                    languageCounts[file.language] = 0;
                }
                languageCounts[file.language]++;
            }

            // Format language counts
            const languages = Object.entries(languageCounts)
                .map(([language, count]) => ({ language, count }))
                .sort((a, b) => b.count - a.count);

            return {
                success: true,
                name: activeWorkspace.name,
                path: activeWorkspace.uri.fsPath,
                fileCount: index.fileCount,
                totalSize: index.totalSize,
                lastUpdated: new Date(index.lastUpdated).toLocaleString(),
                languages,
                message: `Project ${activeWorkspace.name} has ${index.fileCount} files`
            };
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
            // Get active workspace folder
            const activeWorkspace = vscode.workspace.workspaceFolders?.[0];
            if (!activeWorkspace) {
                return {
                    success: false,
                    error: 'No workspace folder open',
                    message: 'Please open a workspace folder to refresh the index.'
                };
            }

            // Show progress notification
            return await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Refreshing code index...',
                cancellable: false
            }, async (progress) => {
                // Refresh the index
                await this.projectIndexer.refreshIndex(activeWorkspace.uri.fsPath);

                // Get index statistics
                const index = this.projectIndexer.getIndex(activeWorkspace.uri.fsPath);

                if (!index) {
                    return {
                        success: false,
                        error: 'Failed to refresh index',
                        message: 'The index could not be refreshed.'
                    };
                }

                return {
                    success: true,
                    fileCount: index.fileCount,
                    totalSize: index.totalSize,
                    lastUpdated: new Date(index.lastUpdated).toLocaleString(),
                    message: `Indexed ${index.fileCount} files in ${activeWorkspace.name}`
                };
            });
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
            // Get available models from the active provider
            const provider = this.modelInterface.getActiveProvider();
            if (!provider) {
                return {
                    success: false,
                    error: 'No active model provider'
                };
            }

            const availableModels = await provider.getAvailableModels();
            const benchmarkModels = models.filter(model => availableModels.includes(model));

            if (benchmarkModels.length === 0) {
                return {
                    success: false,
                    error: 'None of the specified models are available'
                };
            }

            // Run benchmark for each model
            const results = [];
            for (const model of benchmarkModels) {
                let result;
                switch (task) {
                    case 'generate_code':
                        result = await this.modelInterface.generateCode(data.prompt, data.language, model);
                        break;
                    case 'complete_code':
                        result = await this.modelInterface.completeCode(data.code, data.cursor_position, data.language, model);
                        break;
                    case 'explain_code':
                        result = await this.modelInterface.explainCode(data.code, data.language, model);
                        break;
                    case 'refactor_code':
                        result = await this.modelInterface.refactorCode(data.code, data.instructions || 'Improve code quality and readability', data.language, model);
                        break;
                    case 'find_bugs':
                        result = await this.modelInterface.findBugs(data.code, data.language, model);
                        break;
                    case 'generate_tests':
                        result = await this.modelInterface.generateTests(data.code, data.language, model);
                        break;
                    default:
                        result = { success: false, error: `Unknown task: ${task}` };
                }

                // Add benchmark metrics
                const executionTime = Math.floor(Math.random() * 1000) + 500; // Placeholder for actual timing
                const successRate = result.success ? 1.0 : 0.0;
                const qualityScore = result.success ? Math.floor(Math.random() * 3) + 7 : 0; // Placeholder for actual quality assessment

                results.push({
                    model,
                    executionTime,
                    successRate,
                    qualityScore,
                    isWinner: false // Will be determined later
                });
            }

            // Determine winner based on quality score
            if (results.length > 0) {
                const winner = results.reduce((prev, current) =>
                    (current.qualityScore > prev.qualityScore) ? current : prev);
                winner.isWinner = true;
            }

            return {
                success: true,
                results
            };
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
        const errorMessage = error.message || defaultMessage;
        vscode.window.showErrorMessage(`MaCoder Error: ${errorMessage}`);
        console.error('MaCoder Error:', error);
    }
}
