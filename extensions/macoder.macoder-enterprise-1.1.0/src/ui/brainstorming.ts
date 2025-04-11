import * as vscode from 'vscode';
import { logger } from '../core/logger';
import { ContextEngine } from '../context-engine';
import { ProviderManager } from '../model-providers/provider-manager';
import { DomainAdapter } from '../domain/domain-adapter';

/**
 * Brainstorming mode for generating ideas
 */
export class BrainstormingMode {
  private static instance: BrainstormingMode | undefined;

  private panel: vscode.WebviewPanel | undefined;
  private context: vscode.ExtensionContext;
  private contextEngine: ContextEngine;
  private providerManager: ProviderManager;
  private domainAdapter: DomainAdapter;

  private constructor(
    context: vscode.ExtensionContext,
    contextEngine: ContextEngine,
    providerManager: ProviderManager,
    domainAdapter: DomainAdapter
  ) {
    this.context = context;
    this.contextEngine = contextEngine;
    this.providerManager = providerManager;
    this.domainAdapter = domainAdapter;

    logger.info('Brainstorming mode initialized');
  }

  /**
   * Gets the brainstorming mode instance
   */
  public static getInstance(
    context: vscode.ExtensionContext,
    contextEngine: ContextEngine,
    providerManager: ProviderManager,
    domainAdapter: DomainAdapter
  ): BrainstormingMode {
    if (!BrainstormingMode.instance) {
      BrainstormingMode.instance = new BrainstormingMode(
        context,
        contextEngine,
        providerManager,
        domainAdapter
      );
    }

    return BrainstormingMode.instance;
  }

  /**
   * Shows the brainstorming mode
   */
  public async show(): Promise<void> {
    if (this.panel) {
      this.panel.reveal();
      return;
    }

    // Create panel
    this.panel = vscode.window.createWebviewPanel(
      'macoderBrainstorming',
      'MaCoder Brainstorming',
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
          case 'brainstorm':
            await this.handleBrainstorm(message.topic);
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
        <title>MaCoder Brainstorming</title>
        <link href="${styleUri}" rel="stylesheet">
      </head>
      <body>
        <div class="container">
          <h1>MaCoder Brainstorming</h1>

          <p>Brainstorming mode helps you generate ideas and solutions for complex problems.</p>

          <div class="form-group">
            <label for="brainstorm-topic">Topic</label>
            <textarea id="brainstorm-topic" rows="5" placeholder="Enter a topic to brainstorm"></textarea>
          </div>

          <button id="brainstorm-button">Brainstorm</button>

          <div id="brainstorm-result" class="result-container" style="display: none;">
            <h2>Brainstorming Results</h2>
            <div id="brainstorm-result-content"></div>
          </div>
        </div>

        <script>
          (function() {
            // Initialize brainstorm button
            document.getElementById('brainstorm-button').addEventListener('click', () => {
              const topic = document.getElementById('brainstorm-topic').value;

              if (!topic) {
                vscode.postMessage({
                  command: 'showError',
                  message: 'Please enter a topic'
                });
                return;
              }

              // Show loading indicator
              const resultContainer = document.getElementById('brainstorm-result');
              resultContainer.style.display = 'block';

              const resultContent = document.getElementById('brainstorm-result-content');
              resultContent.innerHTML = '<div class="spinner"></div><p>Brainstorming...</p>';

              vscode.postMessage({
                command: 'brainstorm',
                topic
              });
            });

            // Initialize vscode API
            const vscode = acquireVsCodeApi();
          })();
        </script>
      </body>
      </html>
    `;
  }

  /**
   * Handles brainstorm request
   */
  private async handleBrainstorm(topic: string): Promise<void> {
    try {
      // Get context
      const contexts = await this.contextEngine.getAllContexts();
      const contextText = contexts.map(context => context.content).join('\n\n');

      // Get domain info
      const domainInfo = await this.domainAdapter.detectDomain();

      // Generate prompt
      const prompt = `
        I need to brainstorm ideas for the following topic:

        ${topic}

        Context information:
        ${contextText.substring(0, 1000)}

        Domain: ${domainInfo.type}
        Languages: ${domainInfo.languages.join(', ')}
        Frameworks: ${domainInfo.frameworks.map(f => f.name).join(', ')}

        Please generate 5 different ideas or approaches for this topic. For each idea, provide:
        1. A title
        2. A description
        3. Pros and cons
        4. Implementation considerations

        Format the response as markdown.
      `;

      // Generate ideas
      const ideas = await this.providerManager.generateCode(prompt);

      // Update webview
      if (this.panel) {
        this.panel.webview.postMessage({
          command: 'brainstormResult',
          result: ideas
        });
      }

      // Create a new document with the ideas
      const document = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content: `# Brainstorming: ${topic}\n\n${ideas}`
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Brainstorming completed successfully');
    } catch (error: any) {
      logger.error('Error brainstorming:', error);
      vscode.window.showErrorMessage(`Error brainstorming: ${error.message}`);

      // Update webview with error
      if (this.panel) {
        this.panel.webview.postMessage({
          command: 'brainstormError',
          error: error.message
        });
      }
    }
  }
}
