import * as vscode from 'vscode';
import { HybridApiClient } from './hybrid-api-client';
import { generateId } from './utils';

/**
 * Task status enum
 */
export enum TaskStatus {
    Pending = 'pending',
    InProgress = 'in_progress',
    Completed = 'completed',
    Failed = 'failed',
    Cancelled = 'cancelled'
}

/**
 * Task interface
 */
export interface Task {
    id: string;
    description: string;
    status: TaskStatus;
    createdAt: number;
    startedAt?: number;
    completedAt?: number;
    error?: string;
    result?: any;
    subtasks?: Task[];
    parentId?: string;
}

/**
 * Autonomous mode manager
 */
export class AutonomousMode {
    private static instance: AutonomousMode;
    private apiClient: HybridApiClient;
    private tasks: Map<string, Task> = new Map();
    private activeTaskId: string | null = null;
    private isRunning: boolean = false;
    private statusBarItem: vscode.StatusBarItem;
    private outputChannel: vscode.OutputChannel;
    private _onTaskUpdated: vscode.EventEmitter<Task> = new vscode.EventEmitter<Task>();
    
    /**
     * Event that fires when a task is updated
     */
    public readonly onTaskUpdated: vscode.Event<Task> = this._onTaskUpdated.event;

    /**
     * Create a new AutonomousMode
     * 
     * @param apiClient The API client
     */
    private constructor(apiClient: HybridApiClient) {
        this.apiClient = apiClient;
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        this.statusBarItem.text = '$(sync) MaCoder: Idle';
        this.statusBarItem.tooltip = 'MaCoder Autonomous Mode';
        this.statusBarItem.command = 'macoder.toggleAutonomousMode';
        this.outputChannel = vscode.window.createOutputChannel('MaCoder Autonomous Mode');
        
        // Update status bar
        this.updateStatusBar();
    }

    /**
     * Get the singleton instance
     * 
     * @param apiClient The API client
     */
    public static getInstance(apiClient: HybridApiClient): AutonomousMode {
        if (!AutonomousMode.instance) {
            AutonomousMode.instance = new AutonomousMode(apiClient);
        }
        return AutonomousMode.instance;
    }

    /**
     * Start autonomous mode
     */
    public start(): void {
        if (this.isRunning) {
            return;
        }
        
        this.isRunning = true;
        this.statusBarItem.show();
        this.updateStatusBar();
        
        this.log('Autonomous mode started');
    }

    /**
     * Stop autonomous mode
     */
    public stop(): void {
        if (!this.isRunning) {
            return;
        }
        
        this.isRunning = false;
        this.updateStatusBar();
        
        // Cancel active task if any
        if (this.activeTaskId) {
            this.cancelTask(this.activeTaskId);
        }
        
        this.log('Autonomous mode stopped');
    }

    /**
     * Toggle autonomous mode
     */
    public toggle(): void {
        if (this.isRunning) {
            this.stop();
        } else {
            this.start();
        }
    }

    /**
     * Check if autonomous mode is running
     */
    public isActive(): boolean {
        return this.isRunning;
    }

    /**
     * Create a new task
     * 
     * @param description The task description
     * @param parentId The parent task ID
     */
    public createTask(description: string, parentId?: string): Task {
        const taskId = generateId();
        const task: Task = {
            id: taskId,
            description,
            status: TaskStatus.Pending,
            createdAt: Date.now(),
            parentId
        };
        
        this.tasks.set(taskId, task);
        
        // If it's a subtask, add it to the parent
        if (parentId) {
            const parentTask = this.tasks.get(parentId);
            if (parentTask) {
                if (!parentTask.subtasks) {
                    parentTask.subtasks = [];
                }
                parentTask.subtasks.push(task);
                this._onTaskUpdated.fire(parentTask);
            }
        }
        
        this._onTaskUpdated.fire(task);
        this.log(`Task created: ${description} (${taskId})`);
        
        return task;
    }

    /**
     * Start a task
     * 
     * @param taskId The task ID
     */
    public startTask(taskId: string): boolean {
        const task = this.tasks.get(taskId);
        if (!task) {
            return false;
        }
        
        // Check if another task is already active
        if (this.activeTaskId && this.activeTaskId !== taskId) {
            this.log(`Cannot start task ${taskId} because task ${this.activeTaskId} is already active`);
            return false;
        }
        
        // Update task status
        task.status = TaskStatus.InProgress;
        task.startedAt = Date.now();
        this.activeTaskId = taskId;
        
        this._onTaskUpdated.fire(task);
        this.updateStatusBar();
        this.log(`Task started: ${task.description} (${taskId})`);
        
        return true;
    }

    /**
     * Complete a task
     * 
     * @param taskId The task ID
     * @param result The task result
     */
    public completeTask(taskId: string, result?: any): boolean {
        const task = this.tasks.get(taskId);
        if (!task) {
            return false;
        }
        
        // Update task status
        task.status = TaskStatus.Completed;
        task.completedAt = Date.now();
        task.result = result;
        
        // Clear active task if this is the active one
        if (this.activeTaskId === taskId) {
            this.activeTaskId = null;
        }
        
        this._onTaskUpdated.fire(task);
        this.updateStatusBar();
        this.log(`Task completed: ${task.description} (${taskId})`);
        
        return true;
    }

    /**
     * Fail a task
     * 
     * @param taskId The task ID
     * @param error The error message
     */
    public failTask(taskId: string, error: string): boolean {
        const task = this.tasks.get(taskId);
        if (!task) {
            return false;
        }
        
        // Update task status
        task.status = TaskStatus.Failed;
        task.completedAt = Date.now();
        task.error = error;
        
        // Clear active task if this is the active one
        if (this.activeTaskId === taskId) {
            this.activeTaskId = null;
        }
        
        this._onTaskUpdated.fire(task);
        this.updateStatusBar();
        this.log(`Task failed: ${task.description} (${taskId}): ${error}`);
        
        return true;
    }

    /**
     * Cancel a task
     * 
     * @param taskId The task ID
     */
    public cancelTask(taskId: string): boolean {
        const task = this.tasks.get(taskId);
        if (!task) {
            return false;
        }
        
        // Update task status
        task.status = TaskStatus.Cancelled;
        task.completedAt = Date.now();
        
        // Clear active task if this is the active one
        if (this.activeTaskId === taskId) {
            this.activeTaskId = null;
        }
        
        this._onTaskUpdated.fire(task);
        this.updateStatusBar();
        this.log(`Task cancelled: ${task.description} (${taskId})`);
        
        return true;
    }

    /**
     * Get a task by ID
     * 
     * @param taskId The task ID
     */
    public getTask(taskId: string): Task | undefined {
        return this.tasks.get(taskId);
    }

    /**
     * Get all tasks
     */
    public getAllTasks(): Task[] {
        return Array.from(this.tasks.values());
    }

    /**
     * Get root tasks (tasks without a parent)
     */
    public getRootTasks(): Task[] {
        return Array.from(this.tasks.values()).filter(task => !task.parentId);
    }

    /**
     * Get active task
     */
    public getActiveTask(): Task | undefined {
        if (!this.activeTaskId) {
            return undefined;
        }
        
        return this.tasks.get(this.activeTaskId);
    }

    /**
     * Execute a task
     * 
     * @param description The task description
     */
    public async executeTask(description: string): Promise<any> {
        // Create the task
        const task = this.createTask(description);
        
        // Start the task
        if (!this.startTask(task.id)) {
            return {
                success: false,
                error: 'Failed to start task'
            };
        }
        
        try {
            // Parse the task description
            const parsedTask = await this.parseTask(description);
            
            // Create subtasks
            const subtasks = parsedTask.subtasks || [];
            for (const subtaskDescription of subtasks) {
                this.createTask(subtaskDescription, task.id);
            }
            
            // Execute the task
            const result = await this.executeTaskImpl(parsedTask);
            
            // Complete the task
            this.completeTask(task.id, result);
            
            return {
                success: true,
                result
            };
        } catch (error) {
            // Fail the task
            this.failTask(task.id, error instanceof Error ? error.message : String(error));
            
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }

    /**
     * Parse a task description
     * 
     * @param description The task description
     */
    private async parseTask(description: string): Promise<any> {
        // Use the API client to parse the task
        const response = await this.apiClient.generateCode(
            `Parse the following task description into a structured JSON object with 'type', 'details', and 'subtasks' fields:
            
            "${description}"
            
            The 'type' should be one of: 'code_generation', 'code_explanation', 'code_refactoring', 'bug_finding', 'test_generation', 'documentation'.
            The 'details' should contain relevant information for the task.
            The 'subtasks' should be an array of smaller tasks that need to be completed.
            
            Return only the JSON object without any explanation or markdown formatting.`,
            'json'
        );
        
        if (!response.success) {
            throw new Error('Failed to parse task');
        }
        
        try {
            // Extract JSON from the response
            const jsonMatch = response.code.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                throw new Error('No JSON found in response');
            }
            
            const parsedTask = JSON.parse(jsonMatch[0]);
            
            // Validate the parsed task
            if (!parsedTask.type) {
                throw new Error('Task type is required');
            }
            
            return parsedTask;
        } catch (error) {
            throw new Error(`Failed to parse task: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Execute a task implementation
     * 
     * @param parsedTask The parsed task
     */
    private async executeTaskImpl(parsedTask: any): Promise<any> {
        const taskType = parsedTask.type;
        const details = parsedTask.details || {};
        
        switch (taskType) {
            case 'code_generation':
                return this.executeCodeGeneration(details);
            case 'code_explanation':
                return this.executeCodeExplanation(details);
            case 'code_refactoring':
                return this.executeCodeRefactoring(details);
            case 'bug_finding':
                return this.executeBugFinding(details);
            case 'test_generation':
                return this.executeTestGeneration(details);
            case 'documentation':
                return this.executeDocumentation(details);
            default:
                throw new Error(`Unknown task type: ${taskType}`);
        }
    }

    /**
     * Execute code generation task
     * 
     * @param details The task details
     */
    private async executeCodeGeneration(details: any): Promise<any> {
        const prompt = details.prompt || details.description;
        const language = details.language;
        
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            throw new Error('No active editor');
        }
        
        // Generate code
        const response = await this.apiClient.generateCode(prompt, language);
        
        if (!response.success) {
            throw new Error(`Failed to generate code: ${response.error}`);
        }
        
        // Insert the generated code
        await editor.edit(editBuilder => {
            if (editor.selection.isEmpty) {
                editBuilder.insert(editor.selection.active, response.code);
            } else {
                editBuilder.replace(editor.selection, response.code);
            }
        });
        
        return {
            code: response.code,
            message: 'Code generated successfully'
        };
    }

    /**
     * Execute code explanation task
     * 
     * @param details The task details
     */
    private async executeCodeExplanation(details: any): Promise<any> {
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            throw new Error('No active editor');
        }
        
        // Get the selected code
        const selection = editor.selection;
        const code = editor.document.getText(selection);
        
        if (!code) {
            throw new Error('No code selected');
        }
        
        // Get the language ID
        const language = editor.document.languageId;
        
        // Explain code
        const response = await this.apiClient.explainCode(code, language);
        
        if (!response.success) {
            throw new Error(`Failed to explain code: ${response.error}`);
        }
        
        // Show the explanation
        this.outputChannel.clear();
        this.outputChannel.appendLine('# Code Explanation\n');
        this.outputChannel.appendLine(response.explanation);
        this.outputChannel.show();
        
        return {
            explanation: response.explanation,
            message: 'Code explained successfully'
        };
    }

    /**
     * Execute code refactoring task
     * 
     * @param details The task details
     */
    private async executeCodeRefactoring(details: any): Promise<any> {
        const instructions = details.instructions || details.description;
        
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            throw new Error('No active editor');
        }
        
        // Get the selected code
        const selection = editor.selection;
        const code = editor.document.getText(selection);
        
        if (!code) {
            throw new Error('No code selected');
        }
        
        // Get the language ID
        const language = editor.document.languageId;
        
        // Refactor code
        const response = await this.apiClient.refactorCode(code, instructions, language);
        
        if (!response.success) {
            throw new Error(`Failed to refactor code: ${response.error}`);
        }
        
        // Replace the selected code
        await editor.edit(editBuilder => {
            editBuilder.replace(selection, response.code);
        });
        
        return {
            code: response.code,
            message: 'Code refactored successfully'
        };
    }

    /**
     * Execute bug finding task
     * 
     * @param details The task details
     */
    private async executeBugFinding(details: any): Promise<any> {
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            throw new Error('No active editor');
        }
        
        // Get the selected code
        const selection = editor.selection;
        const code = editor.document.getText(selection);
        
        if (!code) {
            throw new Error('No code selected');
        }
        
        // Get the language ID
        const language = editor.document.languageId;
        
        // Find bugs
        const response = await this.apiClient.findBugs(code, language);
        
        if (!response.success) {
            throw new Error(`Failed to find bugs: ${response.error}`);
        }
        
        // Show the bugs
        this.outputChannel.clear();
        this.outputChannel.appendLine('# Bug Analysis\n');
        
        if (response.bugs && response.bugs.length > 0) {
            this.outputChannel.appendLine(`Found ${response.bugs.length} issues:\n`);
            
            for (let i = 0; i < response.bugs.length; i++) {
                const bug = response.bugs[i];
                this.outputChannel.appendLine(`## Issue ${i + 1}: ${bug.title}`);
                this.outputChannel.appendLine(`Severity: ${bug.severity}`);
                this.outputChannel.appendLine(`Location: ${bug.location}`);
                this.outputChannel.appendLine(`\n${bug.description}\n`);
            }
            
            this.outputChannel.appendLine('## Fixed Code\n');
            this.outputChannel.appendLine('```');
            this.outputChannel.appendLine(response.fixedCode);
            this.outputChannel.appendLine('```');
        } else {
            this.outputChannel.appendLine('No issues found in the code.');
        }
        
        this.outputChannel.show();
        
        return {
            bugs: response.bugs,
            fixedCode: response.fixedCode,
            message: `Found ${response.bugs ? response.bugs.length : 0} issues in the code`
        };
    }

    /**
     * Execute test generation task
     * 
     * @param details The task details
     */
    private async executeTestGeneration(details: any): Promise<any> {
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            throw new Error('No active editor');
        }
        
        // Get the selected code
        const selection = editor.selection;
        const code = editor.document.getText(selection);
        
        if (!code) {
            throw new Error('No code selected');
        }
        
        // Get the language ID
        const language = editor.document.languageId;
        
        // Generate tests
        const response = await this.apiClient.generateTests(code, language);
        
        if (!response.success) {
            throw new Error(`Failed to generate tests: ${response.error}`);
        }
        
        // Create a new file for the tests
        const currentFile = editor.document.fileName;
        const testFile = this.getTestFileName(currentFile);
        
        // Create the test file
        const testDocument = await vscode.workspace.openTextDocument(vscode.Uri.file(testFile));
        const testEditor = await vscode.window.showTextDocument(testDocument);
        
        // Insert the tests
        await testEditor.edit(editBuilder => {
            const start = new vscode.Position(0, 0);
            const end = testDocument.lineAt(testDocument.lineCount - 1).range.end;
            editBuilder.replace(new vscode.Range(start, end), response.tests);
        });
        
        return {
            tests: response.tests,
            testFile,
            message: 'Tests generated successfully'
        };
    }

    /**
     * Execute documentation task
     * 
     * @param details The task details
     */
    private async executeDocumentation(details: any): Promise<any> {
        // Get the active editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            throw new Error('No active editor');
        }
        
        // Get the selected code
        const selection = editor.selection;
        const code = editor.document.getText(selection);
        
        if (!code) {
            throw new Error('No code selected');
        }
        
        // Get the language ID
        const language = editor.document.languageId;
        
        // Document code
        const response = await this.apiClient.documentCode(code, language);
        
        if (!response.success) {
            throw new Error(`Failed to document code: ${response.error}`);
        }
        
        // Replace the selected code
        await editor.edit(editBuilder => {
            editBuilder.replace(selection, response.code);
        });
        
        return {
            code: response.code,
            message: 'Code documented successfully'
        };
    }

    /**
     * Get the test file name for a source file
     * 
     * @param sourceFile The source file
     */
    private getTestFileName(sourceFile: string): string {
        const path = require('path');
        const fs = require('fs');
        
        const dirname = path.dirname(sourceFile);
        const basename = path.basename(sourceFile);
        const extname = path.extname(sourceFile);
        const filename = basename.substring(0, basename.length - extname.length);
        
        // Check if there's a test directory
        const testDir = path.join(dirname, 'tests');
        if (fs.existsSync(testDir) && fs.statSync(testDir).isDirectory()) {
            return path.join(testDir, `test_${filename}${extname}`);
        }
        
        // Check if there's a __tests__ directory
        const testsDir = path.join(dirname, '__tests__');
        if (fs.existsSync(testsDir) && fs.statSync(testsDir).isDirectory()) {
            return path.join(testsDir, `${filename}.test${extname}`);
        }
        
        // Default to same directory with test_ prefix
        return path.join(dirname, `test_${filename}${extname}`);
    }

    /**
     * Update the status bar
     */
    private updateStatusBar(): void {
        if (!this.isRunning) {
            this.statusBarItem.text = '$(sync) MaCoder: Idle';
            this.statusBarItem.tooltip = 'MaCoder Autonomous Mode (Idle)';
            return;
        }
        
        const activeTask = this.getActiveTask();
        if (activeTask) {
            this.statusBarItem.text = `$(sync~spin) MaCoder: ${activeTask.description}`;
            this.statusBarItem.tooltip = `MaCoder Autonomous Mode (Active: ${activeTask.description})`;
        } else {
            this.statusBarItem.text = '$(sync) MaCoder: Ready';
            this.statusBarItem.tooltip = 'MaCoder Autonomous Mode (Ready)';
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
     * Dispose the autonomous mode
     */
    public dispose(): void {
        this.statusBarItem.dispose();
        this.outputChannel.dispose();
        this._onTaskUpdated.dispose();
    }
}
