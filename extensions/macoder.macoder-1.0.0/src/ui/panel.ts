import * as vscode from 'vscode';
import { logger } from '../core/logger';
import { ContextEngine } from '../context-engine';
import { CodeGenerationStrategyEngine } from '../generation/strategy-engine';
import { PluginManager } from '../plugins/plugin-manager';
import { IncrementalLearner } from '../learning/incremental-learner';
import { DomainAdapter } from '../domain/domain-adapter';
import { TestGenerationEngine } from '../testing/test-generation-engine';
import { DebugAssistant } from '../debugging/debug-assistant';
import { ProviderManager } from '../model-providers/provider-manager';

/**
 * Main panel for MaCoder
 */
export class MainPanel {
  private static instance: MainPanel | undefined;

  private panel: vscode.WebviewPanel | undefined;
  private context: vscode.ExtensionContext;
  private contextEngine: ContextEngine;
  private strategyEngine: CodeGenerationStrategyEngine;
  private pluginManager: PluginManager;
  private incrementalLearner: IncrementalLearner;
  private domainAdapter: DomainAdapter;
  private testGenerationEngine: TestGenerationEngine;
  private debugAssistant: DebugAssistant;
  private providerManager: ProviderManager;

  private constructor(
    context: vscode.ExtensionContext,
    contextEngine: ContextEngine,
    strategyEngine: CodeGenerationStrategyEngine,
    pluginManager: PluginManager,
    incrementalLearner: IncrementalLearner,
    domainAdapter: DomainAdapter,
    testGenerationEngine: TestGenerationEngine,
    debugAssistant: DebugAssistant,
    providerManager: ProviderManager
  ) {
    this.context = context;
    this.contextEngine = contextEngine;
    this.strategyEngine = strategyEngine;
    this.pluginManager = pluginManager;
    this.incrementalLearner = incrementalLearner;
    this.domainAdapter = domainAdapter;
    this.testGenerationEngine = testGenerationEngine;
    this.debugAssistant = debugAssistant;
    this.providerManager = providerManager;

    logger.info('Main panel initialized');
  }

  /**
   * Gets the main panel instance
   */
  public static getInstance(
    context: vscode.ExtensionContext,
    contextEngine: ContextEngine,
    strategyEngine: CodeGenerationStrategyEngine,
    pluginManager: PluginManager,
    incrementalLearner: IncrementalLearner,
    domainAdapter: DomainAdapter,
    testGenerationEngine: TestGenerationEngine,
    debugAssistant: DebugAssistant,
    providerManager: ProviderManager
  ): MainPanel {
    if (!MainPanel.instance) {
      MainPanel.instance = new MainPanel(
        context,
        contextEngine,
        strategyEngine,
        pluginManager,
        incrementalLearner,
        domainAdapter,
        testGenerationEngine,
        debugAssistant,
        providerManager
      );
    }

    return MainPanel.instance;
  }

  /**
   * Shows the main panel
   */
  public show(): void {
    if (this.panel) {
      this.panel.reveal();
      return;
    }

    // Create panel
    this.panel = vscode.window.createWebviewPanel(
      'macoderPanel',
      'MaCoder',
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
          case 'generateCode':
            await this.handleGenerateCode(message.prompt, message.language, message.strategy);
            break;

          case 'generateTests':
            await this.handleGenerateTests(message.filePath, message.framework, message.options);
            break;

          case 'analyzeError':
            await this.handleAnalyzeError(message.errorMessage, message.stackTrace, message.code);
            break;

          case 'analyzePerformance':
            await this.handleAnalyzePerformance(message.code, message.language);
            break;

          case 'suggestImprovements':
            await this.handleSuggestImprovements(message.code, message.language);
            break;

          case 'detectDomain':
            await this.handleDetectDomain();
            break;

          case 'showLearningStats':
            await this.handleShowLearningStats();
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
        <title>MaCoder</title>
        <link href="${styleUri}" rel="stylesheet">
      </head>
      <body>
        <div class="container">
          <h1>MaCoder</h1>

          <div class="tabs">
            <div class="tab active" data-tab="code-generation">Code Generation</div>
            <div class="tab" data-tab="testing">Testing</div>
            <div class="tab" data-tab="debugging">Debugging</div>
            <div class="tab" data-tab="domain">Domain</div>
            <div class="tab" data-tab="learning">Learning</div>
          </div>

          <div class="tab-content active" id="code-generation">
            <h2>Code Generation</h2>

            <div class="form-group">
              <label for="code-prompt">Prompt</label>
              <textarea id="code-prompt" rows="5" placeholder="Describe the code you want to generate"></textarea>
            </div>

            <div class="form-group">
              <label for="code-language">Language</label>
              <select id="code-language">
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="csharp">C#</option>
                <option value="go">Go</option>
              </select>
            </div>

            <div class="form-group">
              <label for="code-strategy">Strategy</label>
              <select id="code-strategy">
                <option value="auto">Auto-select</option>
                <option value="direct">Direct Generation</option>
                <option value="divide-and-conquer">Divide and Conquer</option>
                <option value="test-driven">Test-Driven</option>
                <option value="example-based">Example-Based</option>
                <option value="iterative-refinement">Iterative Refinement</option>
              </select>
            </div>

            <button id="generate-code-button">Generate Code</button>
          </div>

          <div class="tab-content" id="testing">
            <h2>Testing</h2>

            <div class="form-group">
              <label for="test-file">File to Test</label>
              <input type="text" id="test-file" placeholder="Path to file" readonly>
              <button id="browse-file-button">Browse</button>
            </div>

            <div class="form-group">
              <label for="test-framework">Framework</label>
              <select id="test-framework">
                <option value="jest">Jest</option>
                <option value="mocha">Mocha</option>
                <option value="pytest">Pytest</option>
                <option value="junit">JUnit</option>
              </select>
            </div>

            <div class="form-group">
              <label for="test-coverage">Coverage</label>
              <select id="test-coverage">
                <option value="basic">Basic</option>
                <option value="full">Full</option>
              </select>
            </div>

            <div class="form-group">
              <label>Options</label>
              <div>
                <input type="checkbox" id="test-edge-cases" checked>
                <label for="test-edge-cases">Include Edge Cases</label>
              </div>
              <div>
                <input type="checkbox" id="test-mocks" checked>
                <label for="test-mocks">Include Mocks</label>
              </div>
            </div>

            <button id="generate-tests-button">Generate Tests</button>
          </div>

          <div class="tab-content" id="debugging">
            <h2>Debugging</h2>

            <div class="tabs">
              <div class="tab active" data-tab="error-analysis">Error Analysis</div>
              <div class="tab" data-tab="performance-analysis">Performance Analysis</div>
              <div class="tab" data-tab="code-improvements">Code Improvements</div>
            </div>

            <div class="tab-content active" id="error-analysis">
              <h3>Error Analysis</h3>

              <div class="form-group">
                <label for="error-message">Error Message</label>
                <textarea id="error-message" rows="3" placeholder="Paste the error message"></textarea>
              </div>

              <div class="form-group">
                <label for="stack-trace">Stack Trace (Optional)</label>
                <textarea id="stack-trace" rows="5" placeholder="Paste the stack trace"></textarea>
              </div>

              <div class="form-group">
                <label for="error-code">Code (Optional)</label>
                <textarea id="error-code" rows="5" placeholder="Paste the code that caused the error"></textarea>
              </div>

              <button id="analyze-error-button">Analyze Error</button>
            </div>

            <div class="tab-content" id="performance-analysis">
              <h3>Performance Analysis</h3>

              <div class="form-group">
                <label for="performance-code">Code to Analyze</label>
                <textarea id="performance-code" rows="10" placeholder="Paste the code to analyze for performance issues"></textarea>
              </div>

              <div class="form-group">
                <label for="performance-language">Language</label>
                <select id="performance-language">
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="python">Python</option>
                  <option value="java">Java</option>
                </select>
              </div>

              <button id="analyze-performance-button">Analyze Performance</button>
            </div>

            <div class="tab-content" id="code-improvements">
              <h3>Code Improvements</h3>

              <div class="form-group">
                <label for="improvement-code">Code to Improve</label>
                <textarea id="improvement-code" rows="10" placeholder="Paste the code to improve"></textarea>
              </div>

              <div class="form-group">
                <label for="improvement-language">Language</label>
                <select id="improvement-language">
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="python">Python</option>
                  <option value="java">Java</option>
                </select>
              </div>

              <button id="suggest-improvements-button">Suggest Improvements</button>
            </div>
          </div>

          <div class="tab-content" id="domain">
            <h2>Domain</h2>

            <p>Detect the domain and technology stack of your project to get more relevant suggestions.</p>

            <button id="detect-domain-button">Detect Domain</button>

            <div id="domain-result" class="result-container" style="display: none;">
              <h3>Domain Detection Result</h3>
              <div id="domain-result-content"></div>
            </div>
          </div>

          <div class="tab-content" id="learning">
            <h2>Learning</h2>

            <p>View learning statistics based on your feedback.</p>

            <button id="show-learning-stats-button">Show Learning Statistics</button>

            <div id="learning-stats-result" class="result-container" style="display: none;">
              <h3>Learning Statistics</h3>
              <div id="learning-stats-content"></div>
            </div>
          </div>
        </div>

        <script>
          (function() {
            // Initialize tabs
            const tabs = document.querySelectorAll('.tabs .tab');
            const tabContents = document.querySelectorAll('.tab-content');

            tabs.forEach(tab => {
              tab.addEventListener('click', () => {
                // Get parent tabs container
                const tabsContainer = tab.parentElement;

                // Get all tabs in this container
                const siblingTabs = tabsContainer.querySelectorAll('.tab');

                // Get the tab content container
                let tabContentContainer;
                if (tabsContainer.classList.contains('tabs')) {
                  // Main tabs
                  tabContentContainer = document.querySelector('.container');
                } else {
                  // Nested tabs
                  tabContentContainer = tabsContainer.nextElementSibling;
                  while (tabContentContainer && !tabContentContainer.classList.contains('tab-content')) {
                    tabContentContainer = tabContentContainer.nextElementSibling;
                  }
                  tabContentContainer = tabContentContainer.parentElement;
                }

                // Get all tab contents in this container
                const siblingTabContents = tabContentContainer.querySelectorAll('.tab-content');

                // Remove active class from all tabs and contents
                siblingTabs.forEach(t => t.classList.remove('active'));
                siblingTabContents.forEach(c => c.classList.remove('active'));

                // Add active class to clicked tab and corresponding content
                tab.classList.add('active');
                const tabId = tab.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
              });
            });

            // Initialize buttons
            document.getElementById('generate-code-button').addEventListener('click', () => {
              const prompt = document.getElementById('code-prompt').value;
              const language = document.getElementById('code-language').value;
              const strategy = document.getElementById('code-strategy').value;

              if (!prompt) {
                vscode.postMessage({
                  command: 'showError',
                  message: 'Please enter a prompt'
                });
                return;
              }

              vscode.postMessage({
                command: 'generateCode',
                prompt,
                language,
                strategy: strategy === 'auto' ? undefined : strategy
              });
            });

            document.getElementById('browse-file-button').addEventListener('click', () => {
              vscode.postMessage({
                command: 'browseFile'
              });
            });

            document.getElementById('generate-tests-button').addEventListener('click', () => {
              const filePath = document.getElementById('test-file').value;
              const framework = document.getElementById('test-framework').value;
              const coverage = document.getElementById('test-coverage').value;
              const includeEdgeCases = document.getElementById('test-edge-cases').checked;
              const includeMocks = document.getElementById('test-mocks').checked;

              if (!filePath) {
                vscode.postMessage({
                  command: 'showError',
                  message: 'Please select a file'
                });
                return;
              }

              vscode.postMessage({
                command: 'generateTests',
                filePath,
                framework,
                options: {
                  coverage,
                  includeEdgeCases,
                  includeMocks
                }
              });
            });

            document.getElementById('analyze-error-button').addEventListener('click', () => {
              const errorMessage = document.getElementById('error-message').value;
              const stackTrace = document.getElementById('stack-trace').value;
              const code = document.getElementById('error-code').value;

              if (!errorMessage) {
                vscode.postMessage({
                  command: 'showError',
                  message: 'Please enter an error message'
                });
                return;
              }

              vscode.postMessage({
                command: 'analyzeError',
                errorMessage,
                stackTrace,
                code
              });
            });

            document.getElementById('analyze-performance-button').addEventListener('click', () => {
              const code = document.getElementById('performance-code').value;
              const language = document.getElementById('performance-language').value;

              if (!code) {
                vscode.postMessage({
                  command: 'showError',
                  message: 'Please enter code to analyze'
                });
                return;
              }

              vscode.postMessage({
                command: 'analyzePerformance',
                code,
                language
              });
            });

            document.getElementById('suggest-improvements-button').addEventListener('click', () => {
              const code = document.getElementById('improvement-code').value;
              const language = document.getElementById('improvement-language').value;

              if (!code) {
                vscode.postMessage({
                  command: 'showError',
                  message: 'Please enter code to improve'
                });
                return;
              }

              vscode.postMessage({
                command: 'suggestImprovements',
                code,
                language
              });
            });

            document.getElementById('detect-domain-button').addEventListener('click', () => {
              vscode.postMessage({
                command: 'detectDomain'
              });
            });

            document.getElementById('show-learning-stats-button').addEventListener('click', () => {
              vscode.postMessage({
                command: 'showLearningStats'
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
   * Handles generate code request
   */
  private async handleGenerateCode(
    prompt: string,
    language: string,
    strategy?: string
  ): Promise<void> {
    try {
      // Generate code
      const code = await this.strategyEngine.generateCode(prompt, language, strategy);

      // Create a new document with the generated code
      const document = await vscode.workspace.openTextDocument({
        language,
        content: code
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Code generated successfully');
    } catch (error: any) {
      logger.error('Error generating code:', error);
      vscode.window.showErrorMessage(`Error generating code: ${error.message}`);
    }
  }

  /**
   * Handles generate tests request
   */
  private async handleGenerateTests(
    filePath: string,
    framework: string,
    options: any
  ): Promise<void> {
    try {
      // Get file URI
      const fileUri = vscode.Uri.file(filePath);

      // Create test file
      const testFileUri = await this.testGenerationEngine.createTestFile(
        fileUri,
        framework,
        options
      );

      // Show the test file
      const document = await vscode.workspace.openTextDocument(testFileUri);
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Tests generated successfully');
    } catch (error: any) {
      logger.error('Error generating tests:', error);
      vscode.window.showErrorMessage(`Error generating tests: ${error.message}`);
    }
  }

  /**
   * Handles analyze error request
   */
  private async handleAnalyzeError(
    errorMessage: string,
    stackTrace?: string,
    code?: string
  ): Promise<void> {
    try {
      // Analyze error
      const result = await this.debugAssistant.analyzeError(errorMessage, stackTrace, code);

      // Create a new document with the analysis
      const content = `# Error Analysis

## Error
\`\`\`
${errorMessage}
\`\`\`

${stackTrace ? `## Stack Trace
\`\`\`
${stackTrace}
\`\`\`

` : ''}
## Cause
${result.cause}

## Solution
${result.solution}

${result.documentation ? `## Documentation
${result.documentation}

` : ''}
${result.examples ? `## Examples
\`\`\`
${result.examples.join('\n\n')}
\`\`\`

` : ''}
${result.context ? `## Context
\`\`\`
${result.context}
\`\`\`
` : ''}`;

      const document = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Error analyzed successfully');
    } catch (error: any) {
      logger.error('Error analyzing error:', error);
      vscode.window.showErrorMessage(`Error analyzing error: ${error.message}`);
    }
  }

  /**
   * Handles analyze performance request
   */
  private async handleAnalyzePerformance(
    code: string,
    language: string
  ): Promise<void> {
    try {
      // Analyze performance
      const result = await this.debugAssistant.analyzePerformance(code, language);

      // Create a new document with the analysis
      const content = `# Performance Analysis

## Summary
${result.summary}

## Recommendations
${result.recommendations.map(r => `- ${r}`).join('\n')}

## Issues
${result.issues.map(issue => `
### ${issue.type} (${issue.severity})
${issue.description}

**Recommendation:** ${issue.recommendation}

${issue.code ? `\`\`\`
${issue.code}
\`\`\`` : ''}
`).join('\n')}`;

      const document = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Performance analyzed successfully');
    } catch (error: any) {
      logger.error('Error analyzing performance:', error);
      vscode.window.showErrorMessage(`Error analyzing performance: ${error.message}`);
    }
  }

  /**
   * Handles suggest improvements request
   */
  private async handleSuggestImprovements(
    code: string,
    language: string
  ): Promise<void> {
    try {
      // Suggest improvements
      const result = await this.debugAssistant.suggestImprovements(code, language);

      // Create a new document with the improvements
      const content = `# Code Improvements

## Summary
${result.summary}

## Improvements
${result.improvements.map(improvement => `
### ${improvement.type} (${improvement.severity})
${improvement.description}

**Recommendation:** ${improvement.recommendation}

**Before:**
\`\`\`
${improvement.before}
\`\`\`

**After:**
\`\`\`
${improvement.after}
\`\`\`
`).join('\n')}

## Improved Code
\`\`\`${language}
${result.improvedCode}
\`\`\``;

      const document = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Improvements suggested successfully');
    } catch (error: any) {
      logger.error('Error suggesting improvements:', error);
      vscode.window.showErrorMessage(`Error suggesting improvements: ${error.message}`);
    }
  }

  /**
   * Handles detect domain request
   */
  private async handleDetectDomain(): Promise<void> {
    try {
      // Detect domain
      const domainInfo = await this.domainAdapter.detectDomain();

      // Create a new document with the domain info
      const content = `# Domain Detection

## Domain Type
${domainInfo.type}

## Languages
${domainInfo.languages.map(l => `- ${l}`).join('\n')}

## Frameworks
${domainInfo.frameworks.map(f => `- ${f.name} (${f.type})`).join('\n')}

## Patterns
${domainInfo.patterns.map(p => `- ${p}`).join('\n')}

## Knowledge Base
${domainInfo.knowledgeBase.map(k => `- ${k}`).join('\n')}`;

      const document = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Domain detected successfully');
    } catch (error: any) {
      logger.error('Error detecting domain:', error);
      vscode.window.showErrorMessage(`Error detecting domain: ${error.message}`);
    }
  }

  /**
   * Handles show learning stats request
   */
  private async handleShowLearningStats(): Promise<void> {
    try {
      // Get learning stats
      const stats = this.incrementalLearner.getStats();

      // Create a new document with the stats
      const content = `# Learning Statistics

## Summary
- Total Feedback: ${stats.totalFeedback}
- Positive Feedback: ${stats.positiveFeedback}
- Negative Feedback: ${stats.negativeFeedback}
- Neutral Feedback: ${stats.neutralFeedback}

## Feedback by Language
${Object.entries(stats.feedbackByLanguage).map(([language, count]) => `- ${language}: ${count}`).join('\n')}

## Feedback by Strategy
${Object.entries(stats.feedbackByStrategy).map(([strategy, count]) => `- ${strategy}: ${count}`).join('\n')}

## Recent Feedback
${stats.recentFeedback.map(feedback => `
### ${new Date(feedback.timestamp).toLocaleString()}
- Type: ${feedback.type}
- Language: ${feedback.language || 'Unknown'}
- Strategy: ${feedback.strategy || 'Unknown'}
${feedback.comments ? `- Comments: ${feedback.comments}` : ''}
`).join('\n')}`;

      const document = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Learning statistics shown successfully');
    } catch (error: any) {
      logger.error('Error showing learning stats:', error);
      vscode.window.showErrorMessage(`Error showing learning stats: ${error.message}`);
    }
  }
}
