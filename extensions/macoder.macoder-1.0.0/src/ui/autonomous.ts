import * as vscode from 'vscode';
import { logger } from '../core/logger';
import { ContextEngine } from '../context-engine';
import { CodeGenerationStrategyEngine } from '../generation/strategy-engine';
import { ProviderManager } from '../model-providers/provider-manager';
import { DomainAdapter } from '../domain/domain-adapter';
import { TestGenerationEngine } from '../testing/test-generation-engine';
import { DebugAssistant } from '../debugging/debug-assistant';

/**
 * Autonomous mode for working independently on complex tasks
 */
export class AutonomousMode {
  private static instance: AutonomousMode | undefined;

  private panel: vscode.WebviewPanel | undefined;
  private context: vscode.ExtensionContext;
  private contextEngine: ContextEngine;
  private strategyEngine: CodeGenerationStrategyEngine;
  private providerManager: ProviderManager;
  private domainAdapter: DomainAdapter;
  private testGenerationEngine: TestGenerationEngine;
  private debugAssistant: DebugAssistant;

  private isRunning: boolean = false;
  private currentTask: string = '';
  private subtasks: string[] = [];
  private completedSubtasks: string[] = [];
  private currentSubtask: string = '';
  private logs: string[] = [];

  private constructor(
    context: vscode.ExtensionContext,
    contextEngine: ContextEngine,
    strategyEngine: CodeGenerationStrategyEngine,
    providerManager: ProviderManager,
    domainAdapter: DomainAdapter,
    testGenerationEngine: TestGenerationEngine,
    debugAssistant: DebugAssistant
  ) {
    this.context = context;
    this.contextEngine = contextEngine;
    this.strategyEngine = strategyEngine;
    this.providerManager = providerManager;
    this.domainAdapter = domainAdapter;
    this.testGenerationEngine = testGenerationEngine;
    this.debugAssistant = debugAssistant;

    logger.info('Autonomous mode initialized');
  }

  /**
   * Gets the autonomous mode instance
   */
  public static getInstance(
    context: vscode.ExtensionContext,
    contextEngine: ContextEngine,
    strategyEngine: CodeGenerationStrategyEngine,
    providerManager: ProviderManager,
    domainAdapter: DomainAdapter,
    testGenerationEngine: TestGenerationEngine,
    debugAssistant: DebugAssistant
  ): AutonomousMode {
    if (!AutonomousMode.instance) {
      AutonomousMode.instance = new AutonomousMode(
        context,
        contextEngine,
        strategyEngine,
        providerManager,
        domainAdapter,
        testGenerationEngine,
        debugAssistant
      );
    }

    return AutonomousMode.instance;
  }

  /**
   * Shows the autonomous mode
   */
  public async show(): Promise<void> {
    if (this.panel) {
      this.panel.reveal();
      return;
    }

    // Create panel
    this.panel = vscode.window.createWebviewPanel(
      'macoderAutonomous',
      'MaCoder Autonomous Mode',
      vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [
          vscode.Uri.joinPath(this.context.extensionUri, 'media')
        ]
      }
    );

    // Set HTML content
    this.updateContent();

    // Handle messages from the webview
    this.panel.webview.onDidReceiveMessage(
      async message => {
        switch (message.command) {
          case 'startTask':
            await this.handleStartTask(message.task);
            break;

          case 'stopTask':
            await this.handleStopTask();
            break;
        }
      },
      undefined,
      this.context.subscriptions
    );

    // Handle panel disposal
    this.panel.onDidDispose(
      () => {
        this.panel = undefined;
      },
      null,
      this.context.subscriptions
    );
  }

  /**
   * Updates the panel content
   */
  private updateContent(): void {
    if (!this.panel) {
      return;
    }

    // Get style URI
    const styleUri = this.panel.webview.asWebviewUri(
      vscode.Uri.joinPath(this.context.extensionUri, 'media', 'style.css')
    );

    // Set HTML content
    this.panel.webview.html = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaCoder Autonomous Mode</title>
        <link href="${styleUri}" rel="stylesheet">
        <style>
          .progress-container {
            width: 100%;
            background-color: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            margin-bottom: 10px;
          }

          .progress-bar {
            height: 20px;
            background-color: var(--vscode-progressBar-background);
            border-radius: 4px;
            width: 0%;
            transition: width 0.3s;
          }

          .log-container {
            background-color: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 10px;
            height: 200px;
            overflow-y: auto;
            font-family: monospace;
            margin-bottom: 10px;
          }

          .log-entry {
            margin: 0;
            padding: 2px 0;
          }

          .subtask {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
          }

          .subtask-status {
            margin-right: 10px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .subtask-status.pending {
            background-color: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
          }

          .subtask-status.in-progress {
            background-color: var(--vscode-progressBar-background);
          }

          .subtask-status.completed {
            background-color: var(--vscode-terminal-ansiGreen);
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>MaCoder Autonomous Mode</h1>

          <p>Autonomous mode allows MaCoder to work independently on complex tasks.</p>

          <div class="form-group">
            <label for="autonomous-task">Task</label>
            <textarea id="autonomous-task" rows="5" placeholder="Enter a task for autonomous mode" ${this.isRunning ? 'disabled' : ''}></textarea>
          </div>

          ${this.isRunning ? `
            <div class="panel">
              <div class="panel-header">
                <h2>Task: ${this.currentTask}</h2>
              </div>
              <div class="panel-body">
                <h3>Progress</h3>
                <div class="progress-container">
                  <div class="progress-bar" style="width: ${this.getProgressPercentage()}%"></div>
                </div>
                <p>${this.completedSubtasks.length} of ${this.subtasks.length} subtasks completed</p>

                <h3>Current Subtask</h3>
                <p>${this.currentSubtask || 'Planning...'}</p>

                <h3>Subtasks</h3>
                <div class="subtasks-container">
                  ${this.subtasks.map(subtask => `
                    <div class="subtask">
                      <div class="subtask-status ${this.getSubtaskStatus(subtask)}"></div>
                      <div class="subtask-text">${subtask}</div>
                    </div>
                  `).join('')}
                </div>

                <h3>Logs</h3>
                <div class="log-container">
                  ${this.logs.map(log => `<p class="log-entry">${log}</p>`).join('')}
                </div>

                <button id="stop-task-button">Stop Task</button>
              </div>
            </div>
          ` : `
            <button id="start-task-button">Start Task</button>
          `}
        </div>

        <script>
          (function() {
            // Initialize buttons
            ${this.isRunning ? `
              document.getElementById('stop-task-button').addEventListener('click', () => {
                vscode.postMessage({
                  command: 'stopTask'
                });
              });
            ` : `
              document.getElementById('start-task-button').addEventListener('click', () => {
                const task = document.getElementById('autonomous-task').value;

                if (!task) {
                  vscode.postMessage({
                    command: 'showError',
                    message: 'Please enter a task'
                  });
                  return;
                }

                vscode.postMessage({
                  command: 'startTask',
                  task
                });
              });
            `}

            // Initialize vscode API
            const vscode = acquireVsCodeApi();
          })();
        </script>
      </body>
      </html>
    `;
  }

  /**
   * Gets the progress percentage
   */
  private getProgressPercentage(): number {
    if (this.subtasks.length === 0) {
      return 0;
    }

    return Math.round((this.completedSubtasks.length / this.subtasks.length) * 100);
  }

  /**
   * Gets the status of a subtask
   */
  private getSubtaskStatus(subtask: string): string {
    if (this.completedSubtasks.includes(subtask)) {
      return 'completed';
    } else if (this.currentSubtask === subtask) {
      return 'in-progress';
    } else {
      return 'pending';
    }
  }

  /**
   * Handles start task request
   */
  private async handleStartTask(task: string): Promise<void> {
    try {
      // Check if already running
      if (this.isRunning) {
        vscode.window.showErrorMessage('A task is already running');
        return;
      }

      // Set task
      this.currentTask = task;
      this.isRunning = true;
      this.subtasks = [];
      this.completedSubtasks = [];
      this.currentSubtask = '';
      this.logs = [];

      // Update content
      this.updateContent();

      // Log start
      this.addLog(`Starting task: ${task}`);

      // Plan task
      await this.planTask();

      // Execute subtasks
      for (const subtask of this.subtasks) {
        // Set current subtask
        this.currentSubtask = subtask;

        // Update content
        this.updateContent();

        // Log subtask
        this.addLog(`Executing subtask: ${subtask}`);

        // Execute subtask
        await this.executeSubtask(subtask);

        // Mark subtask as completed
        this.completedSubtasks.push(subtask);

        // Update content
        this.updateContent();
      }

      // Log completion
      this.addLog('Task completed successfully');

      // Reset current subtask
      this.currentSubtask = '';

      // Update content
      this.updateContent();

      // Show success message
      vscode.window.showInformationMessage('Task completed successfully');
    } catch (error: any) {
      logger.error('Error executing task:', error);

      // Log error
      this.addLog(`Error: ${error.message}`);

      // Update content
      this.updateContent();

      // Show error message
      vscode.window.showErrorMessage(`Error executing task: ${error.message}`);
    } finally {
      // Reset running state
      this.isRunning = false;

      // Update content
      this.updateContent();
    }
  }

  /**
   * Handles stop task request
   */
  private async handleStopTask(): Promise<void> {
    try {
      // Check if running
      if (!this.isRunning) {
        vscode.window.showErrorMessage('No task is running');
        return;
      }

      // Log stop
      this.addLog('Task stopped by user');

      // Reset running state
      this.isRunning = false;

      // Update content
      this.updateContent();

      // Show message
      vscode.window.showInformationMessage('Task stopped');
    } catch (error: any) {
      logger.error('Error stopping task:', error);
      vscode.window.showErrorMessage(`Error stopping task: ${error.message}`);
    }
  }

  /**
   * Plans a task
   */
  private async planTask(): Promise<void> {
    try {
      // Log planning
      this.addLog('Planning task...');

      // Get context
      const contexts = await this.contextEngine.getAllContexts();
      const contextText = contexts.map(context => context.content).join('\n\n');

      // Get domain info
      const domainInfo = await this.domainAdapter.detectDomain();

      // Generate prompt
      const prompt = `
        I need to break down the following task into subtasks:

        ${this.currentTask}

        Context information:
        ${contextText.substring(0, 1000)}

        Domain: ${domainInfo.type}
        Languages: ${domainInfo.languages.join(', ')}
        Frameworks: ${domainInfo.frameworks.map(f => f.name).join(', ')}

        Please break down this task into 5-10 subtasks. Each subtask should be a specific, actionable item.

        Format the response as a list of subtasks, one per line, with no numbering or bullets.
      `;

      // Generate subtasks
      const subtasksText = await this.providerManager.generateCode(prompt);

      // Parse subtasks
      this.subtasks = subtasksText
        .split('\n')
        .map(line => line.trim())
        .filter(line => line && !line.startsWith('#') && !line.startsWith('-') && !line.startsWith('*'));

      // Log subtasks
      this.addLog(`Task broken down into ${this.subtasks.length} subtasks`);

      // Update content
      this.updateContent();
    } catch (error: any) {
      logger.error('Error planning task:', error);
      throw new Error(`Error planning task: ${error.message}`);
    }
  }

  /**
   * Executes a subtask
   */
  private async executeSubtask(subtask: string): Promise<void> {
    try {
      // Get context
      const contexts = await this.contextEngine.getAllContexts();
      const contextText = contexts.map(context => context.content).join('\n\n');

      // Generate prompt
      const prompt = `
        I need to execute the following subtask:

        ${subtask}

        This is part of the larger task:

        ${this.currentTask}

        Context information:
        ${contextText.substring(0, 1000)}

        Please generate the code needed to complete this subtask.
      `;

      // Generate code
      const code = await this.providerManager.generateCode(prompt);

      // Create a new document with the generated code
      const document = await vscode.workspace.openTextDocument({
        content: code
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Log completion
      this.addLog(`Generated code for subtask: ${subtask}`);

      // Simulate delay for demo purposes
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (error: any) {
      logger.error(`Error executing subtask: ${subtask}`, error);
      throw new Error(`Error executing subtask: ${error.message}`);
    }
  }

  /**
   * Adds a log entry
   */
  private addLog(message: string): void {
    const timestamp = new Date().toLocaleTimeString();
    this.logs.push(`[${timestamp}] ${message}`);

    // Keep only the last 100 logs
    if (this.logs.length > 100) {
      this.logs = this.logs.slice(-100);
    }

    // Log to output channel
    logger.info(`[Autonomous] ${message}`);
  }
}
