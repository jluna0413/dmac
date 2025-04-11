import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { generateId } from './utils';

/**
 * Sandbox execution result interface
 */
export interface SandboxResult {
    success: boolean;
    output: string;
    error?: string;
    executionTime?: number;
}

/**
 * Sandbox test interface
 */
export interface SandboxTest {
    id: string;
    name: string;
    code: string;
    language: string;
    result?: SandboxResult;
    createdAt: number;
}

/**
 * Code sandbox interface
 */
export interface CodeSandbox {
    /**
     * Execute code in the sandbox
     *
     * @param code The code to execute
     * @param language The language of the code
     */
    executeCode(code: string, language: string): Promise<SandboxResult>;

    /**
     * Create a test
     *
     * @param name The test name
     * @param code The test code
     * @param language The test language
     */
    createTest(name: string, code: string, language: string): SandboxTest;

    /**
     * Run a test
     *
     * @param testId The test ID
     */
    runTest(testId: string): Promise<SandboxResult>;

    /**
     * Get a test by ID
     *
     * @param testId The test ID
     */
    getTest(testId: string): SandboxTest | undefined;

    /**
     * Get all tests
     */
    getAllTests(): SandboxTest[];

    /**
     * Delete a test
     *
     * @param testId The test ID
     */
    deleteTest(testId: string): boolean;
}

/**
 * Local code sandbox
 */
export class LocalCodeSandbox implements CodeSandbox {
    private static instance: LocalCodeSandbox;
    private tests: Map<string, SandboxTest> = new Map();
    private sandboxDir: string;
    private outputChannel: vscode.OutputChannel;
    private _onTestCreated: vscode.EventEmitter<SandboxTest> = new vscode.EventEmitter<SandboxTest>();
    private _onTestRun: vscode.EventEmitter<SandboxTest> = new vscode.EventEmitter<SandboxTest>();
    private _onTestDeleted: vscode.EventEmitter<string> = new vscode.EventEmitter<string>();

    /**
     * Event that fires when a test is created
     */
    public readonly onTestCreated: vscode.Event<SandboxTest> = this._onTestCreated.event;

    /**
     * Event that fires when a test is run
     */
    public readonly onTestRun: vscode.Event<SandboxTest> = this._onTestRun.event;

    /**
     * Event that fires when a test is deleted
     */
    public readonly onTestDeleted: vscode.Event<string> = this._onTestDeleted.event;

    /**
     * Create a new LocalCodeSandbox
     *
     * @param sandboxDir The sandbox directory
     */
    private constructor(sandboxDir: string) {
        this.sandboxDir = sandboxDir;
        this.outputChannel = vscode.window.createOutputChannel('MaCoder Sandbox');

        // Create sandbox directory if it doesn't exist
        if (!fs.existsSync(this.sandboxDir)) {
            fs.mkdirSync(this.sandboxDir, { recursive: true });
        }

        // Load existing tests
        this.loadTests();

        this.log('Code sandbox initialized');
    }

    /**
     * Get the singleton instance
     *
     * @param context The extension context
     */
    public static getInstance(context: vscode.ExtensionContext): LocalCodeSandbox {
        if (!LocalCodeSandbox.instance) {
            const sandboxDir = path.join(context.globalStoragePath, 'sandbox');
            LocalCodeSandbox.instance = new LocalCodeSandbox(sandboxDir);
        }
        return LocalCodeSandbox.instance;
    }

    /**
     * Execute code in the sandbox
     *
     * @param code The code to execute
     * @param language The language of the code
     */
    public async executeCode(code: string, language: string): Promise<SandboxResult> {
        try {
            // Create a temporary file for the code
            const tempDir = path.join(this.sandboxDir, 'temp');
            if (!fs.existsSync(tempDir)) {
                fs.mkdirSync(tempDir, { recursive: true });
            }

            // Get file extension for language
            const extension = this.getFileExtension(language);
            if (!extension) {
                return {
                    success: false,
                    output: '',
                    error: `Unsupported language: ${language}`
                };
            }

            // Create the file
            const tempFile = path.join(tempDir, `code_${Date.now()}${extension}`);
            fs.writeFileSync(tempFile, code, 'utf8');

            // Execute the code
            const startTime = Date.now();
            const result = await this.executeFile(tempFile, language);
            const executionTime = Date.now() - startTime;

            // Clean up
            try {
                fs.unlinkSync(tempFile);
            } catch (error) {
                this.log(`Error deleting temp file: ${error instanceof Error ? error.message : String(error)}`);
            }

            return {
                ...result,
                executionTime
            };
        } catch (error) {
            return {
                success: false,
                output: '',
                error: `Execution failed: ${error instanceof Error ? error.message : String(error)}`
            };
        }
    }

    /**
     * Create a test
     *
     * @param name The test name
     * @param code The test code
     * @param language The test language
     */
    public createTest(name: string, code: string, language: string): SandboxTest {
        const testId = generateId();
        const test: SandboxTest = {
            id: testId,
            name,
            code,
            language,
            createdAt: Date.now()
        };

        this.tests.set(testId, test);
        this.saveTests();

        this._onTestCreated.fire(test);
        this.log(`Created test: ${name} (${testId})`);

        return test;
    }

    /**
     * Run a test
     *
     * @param testId The test ID
     */
    public async runTest(testId: string): Promise<SandboxResult> {
        const test = this.tests.get(testId);
        if (!test) {
            return {
                success: false,
                output: '',
                error: 'Test not found'
            };
        }

        this.log(`Running test: ${test.name} (${testId})`);

        // Execute the code
        const result = await this.executeCode(test.code, test.language);

        // Update the test with the result
        test.result = result;
        this.saveTests();

        this._onTestRun.fire(test);

        return result;
    }

    /**
     * Get a test by ID
     *
     * @param testId The test ID
     */
    public getTest(testId: string): SandboxTest | undefined {
        return this.tests.get(testId);
    }

    /**
     * Get all tests
     */
    public getAllTests(): SandboxTest[] {
        return Array.from(this.tests.values());
    }

    /**
     * Delete a test
     *
     * @param testId The test ID
     */
    public deleteTest(testId: string): boolean {
        const test = this.tests.get(testId);
        if (!test) {
            return false;
        }

        this.tests.delete(testId);
        this.saveTests();

        this._onTestDeleted.fire(testId);
        this.log(`Deleted test: ${test.name} (${testId})`);

        return true;
    }

    /**
     * Execute a file
     *
     * @param filePath The file path
     * @param language The language
     */
    private async executeFile(filePath: string, language: string): Promise<SandboxResult> {
        try {
            // Get the command for the language
            const command = this.getExecutionCommand(filePath, language);
            if (!command) {
                return {
                    success: false,
                    output: '',
                    error: `Unsupported language: ${language}`
                };
            }

            // Execute the command
            const { exec } = require('child_process');

            return new Promise((resolve) => {
                exec(command, { timeout: 5000 }, (error: any, stdout: string, stderr: string) => {
                    if (error) {
                        resolve({
                            success: false,
                            output: stdout,
                            error: stderr || error.message
                        });
                    } else {
                        resolve({
                            success: true,
                            output: stdout,
                            error: stderr
                        });
                    }
                });
            });
        } catch (error) {
            return {
                success: false,
                output: '',
                error: `Execution failed: ${error instanceof Error ? error.message : String(error)}`
            };
        }
    }

    /**
     * Get the file extension for a language
     *
     * @param language The language
     */
    private getFileExtension(language: string): string | null {
        const languageLower = language.toLowerCase();

        switch (languageLower) {
            case 'javascript':
            case 'js':
                return '.js';
            case 'typescript':
            case 'ts':
                return '.ts';
            case 'python':
            case 'py':
                return '.py';
            case 'java':
                return '.java';
            case 'c':
                return '.c';
            case 'cpp':
            case 'c++':
                return '.cpp';
            case 'csharp':
            case 'c#':
                return '.cs';
            case 'go':
                return '.go';
            case 'ruby':
            case 'rb':
                return '.rb';
            case 'php':
                return '.php';
            case 'rust':
            case 'rs':
                return '.rs';
            case 'shell':
            case 'bash':
            case 'sh':
                return '.sh';
            case 'powershell':
            case 'ps1':
                return '.ps1';
            default:
                return null;
        }
    }

    /**
     * Get the execution command for a language
     *
     * @param filePath The file path
     * @param language The language
     */
    private getExecutionCommand(filePath: string, language: string): string | null {
        const languageLower = language.toLowerCase();
        const isWindows = os.platform() === 'win32';

        switch (languageLower) {
            case 'javascript':
            case 'js':
                return `node "${filePath}"`;
            case 'typescript':
            case 'ts':
                return `ts-node "${filePath}"`;
            case 'python':
            case 'py':
                return `python "${filePath}"`;
            case 'java':
                // Compile and run Java
                const javaClassName = path.basename(filePath, '.java');
                const javaDir = path.dirname(filePath);
                return `javac "${filePath}" && java -cp "${javaDir}" ${javaClassName}`;
            case 'c':
                // Compile and run C
                const cOutput = path.join(path.dirname(filePath), 'output');
                return `gcc "${filePath}" -o "${cOutput}" && "${cOutput}"`;
            case 'cpp':
            case 'c++':
                // Compile and run C++
                const cppOutput = path.join(path.dirname(filePath), 'output');
                return `g++ "${filePath}" -o "${cppOutput}" && "${cppOutput}"`;
            case 'csharp':
            case 'c#':
                return `dotnet run "${filePath}"`;
            case 'go':
                return `go run "${filePath}"`;
            case 'ruby':
            case 'rb':
                return `ruby "${filePath}"`;
            case 'php':
                return `php "${filePath}"`;
            case 'rust':
            case 'rs':
                return `rustc "${filePath}" -o "${path.join(path.dirname(filePath), 'output')}" && "${path.join(path.dirname(filePath), 'output')}"`;
            case 'shell':
            case 'bash':
            case 'sh':
                return isWindows ? `bash "${filePath}"` : `bash "${filePath}"`;
            case 'powershell':
            case 'ps1':
                return isWindows ? `powershell -ExecutionPolicy Bypass -File "${filePath}"` : `pwsh -File "${filePath}"`;
            default:
                return null;
        }
    }

    /**
     * Load tests from file
     */
    private loadTests(): void {
        const testsPath = path.join(this.sandboxDir, 'tests.json');

        if (fs.existsSync(testsPath)) {
            try {
                const testsJson = fs.readFileSync(testsPath, 'utf8');
                const tests = JSON.parse(testsJson) as SandboxTest[];

                // Convert to map
                this.tests = new Map(tests.map(test => [test.id, test]));

                this.log(`Loaded ${this.tests.size} tests from file`);
            } catch (error) {
                this.log(`Error loading tests: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    }

    /**
     * Save tests to file
     */
    private saveTests(): void {
        const testsPath = path.join(this.sandboxDir, 'tests.json');

        try {
            const tests = Array.from(this.tests.values());
            const testsJson = JSON.stringify(tests, null, 2);
            fs.writeFileSync(testsPath, testsJson, 'utf8');
        } catch (error) {
            this.log(`Error saving tests: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Log a message to the output channel
     *
     * @param message The message to log
     */
    private log(message: string): void {
        const timestamp = new Date().toISOString();
        this.outputChannel.appendLine(`[${timestamp}] ${message}`);
    }

    /**
     * Dispose the sandbox
     */
    public dispose(): void {
        this.outputChannel.dispose();
        this._onTestCreated.dispose();
        this._onTestRun.dispose();
        this._onTestDeleted.dispose();
    }
}
