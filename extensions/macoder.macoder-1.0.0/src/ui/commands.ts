import * as vscode from 'vscode';
import { logger } from '../core/logger';
import { ContextEngine } from '../context-engine';
import { CodeGenerationStrategyEngine } from '../generation/strategy-engine';
import { PluginManager } from '../plugins/plugin-manager';
import { IncrementalLearner, FeedbackType } from '../learning/incremental-learner';
import { DomainAdapter } from '../domain/domain-adapter';
import { TestGenerationEngine } from '../testing/test-generation-engine';
import { DebugAssistant } from '../debugging/debug-assistant';
import { ProviderManager } from '../model-providers/provider-manager';
import { DMacConfigManager } from '../dmac-integration/config';
import { MainPanel } from './panel';
import { ModelBrowser } from './model-browser';
import { BrainstormingMode } from './brainstorming';
import { AutonomousMode } from './autonomous';

/**
 * Commands module for registering and handling commands
 */
export class Commands {
  private context: vscode.ExtensionContext;
  private contextEngine: ContextEngine;
  private strategyEngine: CodeGenerationStrategyEngine;
  private pluginManager: PluginManager;
  private incrementalLearner: IncrementalLearner;
  private domainAdapter: DomainAdapter;
  private testGenerationEngine: TestGenerationEngine;
  private debugAssistant: DebugAssistant;
  private providerManager: ProviderManager;
  private dmacConfigManager: DMacConfigManager;

  constructor(
    context: vscode.ExtensionContext,
    contextEngine: ContextEngine,
    strategyEngine: CodeGenerationStrategyEngine,
    pluginManager: PluginManager,
    incrementalLearner: IncrementalLearner,
    domainAdapter: DomainAdapter,
    testGenerationEngine: TestGenerationEngine,
    debugAssistant: DebugAssistant,
    providerManager: ProviderManager,
    dmacConfigManager: DMacConfigManager
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
    this.dmacConfigManager = dmacConfigManager;

    logger.info('Commands module initialized');
  }

  /**
   * Registers all commands
   */
  public registerCommands(): void {
    // Register the openPanel command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.openPanel', this.openPanel.bind(this))
    );

    // Register the generateCode command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.generateCode', this.generateCode.bind(this))
    );

    // Register the generateTests command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.generateTests', this.generateTests.bind(this))
    );

    // Register the analyzeError command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.analyzeError', this.analyzeError.bind(this))
    );

    // Register the analyzePerformance command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.analyzePerformance', this.analyzePerformance.bind(this))
    );

    // Register the suggestImprovements command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.suggestImprovements', this.suggestImprovements.bind(this))
    );

    // Register the listStrategies command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.listStrategies', this.listStrategies.bind(this))
    );

    // Register the listPlugins command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.listPlugins', this.listPlugins.bind(this))
    );

    // Register the detectDomain command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.detectDomain', this.detectDomain.bind(this))
    );

    // Register the showLearningStats command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.showLearningStats', this.showLearningStats.bind(this))
    );

    // Register the openBrainstorming command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.openBrainstorming', this.openBrainstorming.bind(this))
    );

    // Register the startAutonomous command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.startAutonomous', this.startAutonomous.bind(this))
    );

    // Register the openModelBrowser command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.openModelBrowser', this.openModelBrowser.bind(this))
    );

    // Register the configureDMacIntegration command
    this.context.subscriptions.push(
      vscode.commands.registerCommand('macoder.configureDMacIntegration', this.configureDMacIntegration.bind(this))
    );

    logger.info('Commands registered');
  }

  /**
   * Opens the main panel
   */
  private async openPanel(): Promise<void> {
    try {
      // Get main panel instance
      const panel = MainPanel.getInstance(
        this.context,
        this.contextEngine,
        this.strategyEngine,
        this.pluginManager,
        this.incrementalLearner,
        this.domainAdapter,
        this.testGenerationEngine,
        this.debugAssistant,
        this.providerManager
      );

      // Show panel
      panel.show();
    } catch (error: any) {
      logger.error('Error opening panel:', error);
      vscode.window.showErrorMessage(`Error opening panel: ${error.message}`);
    }
  }

  /**
   * Generates code
   */
  private async generateCode(): Promise<void> {
    try {
      // Show input box
      const description = await vscode.window.showInputBox({
        prompt: 'Enter a description of the code you want to generate',
        placeHolder: 'Generate a function that sorts an array of objects by a property'
      });

      if (!description) {
        return;
      }

      // Show language quick pick
      const language = await vscode.window.showQuickPick(
        ['javascript', 'typescript', 'python', 'java', 'csharp', 'go'],
        {
          placeHolder: 'Select a language'
        }
      );

      if (!language) {
        return;
      }

      // Get strategies
      const strategies = this.strategyEngine.getStrategies();

      // Show strategy quick pick
      const strategy = await vscode.window.showQuickPick(
        [
          { label: 'Auto-select', description: 'Let MaCoder select the best strategy', value: undefined },
          ...strategies.map(s => ({ label: s.name, description: s.description, value: s.id }))
        ],
        {
          placeHolder: 'Select a strategy'
        }
      );

      if (!strategy) {
        return;
      }

      // Generate code
      const code = await this.strategyEngine.generateCode(description, language, strategy.value);

      // Create a new document with the generated code
      const document = await vscode.workspace.openTextDocument({
        language,
        content: code
      });

      // Show the document
      await vscode.window.showTextDocument(document);

      // Show success message
      vscode.window.showInformationMessage('Code generated successfully');

      // Add feedback
      const feedbackOptions = ['Positive', 'Neutral', 'Negative'];
      const feedback = await vscode.window.showQuickPick(feedbackOptions, {
        placeHolder: 'How would you rate the generated code?'
      });

      if (feedback) {
        let feedbackType: FeedbackType;

        switch (feedback) {
          case 'Positive':
            feedbackType = FeedbackType.POSITIVE;
            break;
          case 'Negative':
            feedbackType = FeedbackType.NEGATIVE;
            break;
          default:
            feedbackType = FeedbackType.NEUTRAL;
        }

        this.incrementalLearner.addFeedback(
          description,
          code,
          feedbackType,
          {
            language,
            strategy: strategy.value
          }
        );
      }
    } catch (error: any) {
      logger.error('Error generating code:', error);
      vscode.window.showErrorMessage(`Error generating code: ${error.message}`);
    }
  }

  /**
   * Generates tests
   */
  private async generateTests(): Promise<void> {
    try {
      // Show file picker
      const fileUris = await vscode.window.showOpenDialog({
        canSelectMany: false,
        openLabel: 'Select File to Test',
        filters: {
          'All Files': ['*']
        }
      });

      if (!fileUris || fileUris.length === 0) {
        return;
      }

      const fileUri = fileUris[0];

      // Get document
      const document = await vscode.workspace.openTextDocument(fileUri);

      // Get language
      const language = document.languageId;

      // Get frameworks for language
      const frameworks = this.testGenerationEngine.getFrameworksForLanguage(language);

      if (frameworks.length === 0) {
        vscode.window.showErrorMessage(`No test frameworks available for language: ${language}`);
        return;
      }

      // Show framework quick pick
      const framework = await vscode.window.showQuickPick(
        frameworks.map(f => ({ label: f.name, description: `Test framework for ${f.language}`, value: f.id })),
        {
          placeHolder: 'Select a test framework'
        }
      );

      if (!framework) {
        return;
      }

      // Show coverage quick pick
      const coverage = await vscode.window.showQuickPick(
        [
          { label: 'Basic', description: 'Basic test coverage', value: 'basic' },
          { label: 'Full', description: 'Full test coverage', value: 'full' }
        ],
        {
          placeHolder: 'Select coverage level'
        }
      );

      if (!coverage) {
        return;
      }

      // Show edge cases quick pick
      const includeEdgeCases = await vscode.window.showQuickPick(
        [
          { label: 'Yes', description: 'Include edge cases', value: true },
          { label: 'No', description: 'Do not include edge cases', value: false }
        ],
        {
          placeHolder: 'Include edge cases?'
        }
      );

      if (!includeEdgeCases) {
        return;
      }

      // Show mocks quick pick
      const includeMocks = await vscode.window.showQuickPick(
        [
          { label: 'Yes', description: 'Include mocks', value: true },
          { label: 'No', description: 'Do not include mocks', value: false }
        ],
        {
          placeHolder: 'Include mocks?'
        }
      );

      if (!includeMocks) {
        return;
      }

      // Create test file
      const testFileUri = await this.testGenerationEngine.createTestFile(
        fileUri,
        framework.value,
        {
          coverage: coverage.value as 'basic' | 'full',
          includeEdgeCases: includeEdgeCases.value,
          includeMocks: includeMocks.value
        }
      );

      // Show the test file
      const testDocument = await vscode.workspace.openTextDocument(testFileUri);
      await vscode.window.showTextDocument(testDocument);

      // Show success message
      vscode.window.showInformationMessage('Tests generated successfully');
    } catch (error: any) {
      logger.error('Error generating tests:', error);
      vscode.window.showErrorMessage(`Error generating tests: ${error.message}`);
    }
  }

  /**
   * Analyzes an error
   */
  private async analyzeError(): Promise<void> {
    try {
      // Show input box for error message
      const errorMessage = await vscode.window.showInputBox({
        prompt: 'Enter the error message',
        placeHolder: 'TypeError: Cannot read property \'x\' of undefined'
      });

      if (!errorMessage) {
        return;
      }

      // Show input box for stack trace
      const stackTrace = await vscode.window.showInputBox({
        prompt: 'Enter the stack trace (optional)',
        placeHolder: 'at Object.<anonymous> (/path/to/file.js:10:20)'
      });

      // Show input box for code
      const code = await vscode.window.showInputBox({
        prompt: 'Enter the code that caused the error (optional)',
        placeHolder: 'const result = obj.prop.value;'
      });

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
   * Analyzes performance
   */
  private async analyzePerformance(): Promise<void> {
    try {
      // Show file picker
      const fileUris = await vscode.window.showOpenDialog({
        canSelectMany: false,
        openLabel: 'Select File to Analyze',
        filters: {
          'All Files': ['*']
        }
      });

      if (!fileUris || fileUris.length === 0) {
        return;
      }

      const fileUri = fileUris[0];

      // Get document
      const document = await vscode.workspace.openTextDocument(fileUri);

      // Get language
      const language = document.languageId;

      // Get code
      const code = document.getText();

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

      const analysisDocument = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(analysisDocument);

      // Show success message
      vscode.window.showInformationMessage('Performance analyzed successfully');
    } catch (error: any) {
      logger.error('Error analyzing performance:', error);
      vscode.window.showErrorMessage(`Error analyzing performance: ${error.message}`);
    }
  }

  /**
   * Suggests improvements
   */
  private async suggestImprovements(): Promise<void> {
    try {
      // Show file picker
      const fileUris = await vscode.window.showOpenDialog({
        canSelectMany: false,
        openLabel: 'Select File to Improve',
        filters: {
          'All Files': ['*']
        }
      });

      if (!fileUris || fileUris.length === 0) {
        return;
      }

      const fileUri = fileUris[0];

      // Get document
      const document = await vscode.workspace.openTextDocument(fileUri);

      // Get language
      const language = document.languageId;

      // Get code
      const code = document.getText();

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

      const improvementsDocument = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(improvementsDocument);

      // Show success message
      vscode.window.showInformationMessage('Improvements suggested successfully');

      // Ask if user wants to apply improvements
      const apply = await vscode.window.showQuickPick(
        [
          { label: 'Yes', description: 'Apply improvements', value: true },
          { label: 'No', description: 'Do not apply improvements', value: false }
        ],
        {
          placeHolder: 'Apply improvements?'
        }
      );

      if (apply && apply.value) {
        // Create edit
        const edit = new vscode.WorkspaceEdit();
        edit.replace(fileUri, new vscode.Range(0, 0, document.lineCount, 0), result.improvedCode);

        // Apply edit
        await vscode.workspace.applyEdit(edit);

        // Show success message
        vscode.window.showInformationMessage('Improvements applied successfully');
      }
    } catch (error: any) {
      logger.error('Error suggesting improvements:', error);
      vscode.window.showErrorMessage(`Error suggesting improvements: ${error.message}`);
    }
  }

  /**
   * Lists strategies
   */
  private async listStrategies(): Promise<void> {
    try {
      // Get strategies
      const strategies = this.strategyEngine.getStrategies();

      // Create a new document with the strategies
      const content = `# Code Generation Strategies

${strategies.map(strategy => `
## ${strategy.name}
${strategy.description}

**Complexity:** ${strategy.complexity}

**Suitable For:**
${strategy.suitableFor.map(s => `- ${s}`).join('\n')}

**Not Suitable For:**
${strategy.notSuitableFor.map(s => `- ${s}`).join('\n')}
`).join('\n')}`;

      const document = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(document);
    } catch (error: any) {
      logger.error('Error listing strategies:', error);
      vscode.window.showErrorMessage(`Error listing strategies: ${error.message}`);
    }
  }

  /**
   * Lists plugins
   */
  private async listPlugins(): Promise<void> {
    try {
      // Get plugins
      const plugins = this.pluginManager.getPlugins();

      // Create a new document with the plugins
      const content = `# Installed Plugins

${plugins.map(plugin => `
## ${plugin.name}
${plugin.description}

**ID:** ${plugin.id}
**Version:** ${plugin.version}
`).join('\n')}`;

      const document = await vscode.workspace.openTextDocument({
        language: 'markdown',
        content
      });

      // Show the document
      await vscode.window.showTextDocument(document);
    } catch (error: any) {
      logger.error('Error listing plugins:', error);
      vscode.window.showErrorMessage(`Error listing plugins: ${error.message}`);
    }
  }

  /**
   * Detects domain
   */
  private async detectDomain(): Promise<void> {
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
   * Shows learning stats
   */
  private async showLearningStats(): Promise<void> {
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
    } catch (error: any) {
      logger.error('Error showing learning stats:', error);
      vscode.window.showErrorMessage(`Error showing learning stats: ${error.message}`);
    }
  }

  /**
   * Opens brainstorming mode
   */
  private async openBrainstorming(): Promise<void> {
    try {
      // Get brainstorming mode instance
      const brainstormingMode = BrainstormingMode.getInstance(
        this.context,
        this.contextEngine,
        this.providerManager,
        this.domainAdapter
      );

      // Show brainstorming mode
      await brainstormingMode.show();
    } catch (error: any) {
      logger.error('Error opening brainstorming mode:', error);
      vscode.window.showErrorMessage(`Error opening brainstorming mode: ${error.message}`);
    }
  }

  /**
   * Starts autonomous mode
   */
  private async startAutonomous(): Promise<void> {
    try {
      // Get autonomous mode instance
      const autonomousMode = AutonomousMode.getInstance(
        this.context,
        this.contextEngine,
        this.strategyEngine,
        this.providerManager,
        this.domainAdapter,
        this.testGenerationEngine,
        this.debugAssistant
      );

      // Show autonomous mode
      await autonomousMode.show();
    } catch (error: any) {
      logger.error('Error starting autonomous mode:', error);
      vscode.window.showErrorMessage(`Error starting autonomous mode: ${error.message}`);
    }
  }

  /**
   * Opens model browser
   */
  private async openModelBrowser(): Promise<void> {
    try {
      // Get model browser instance
      const modelBrowser = ModelBrowser.getInstance(
        this.context,
        this.providerManager
      );

      // Show model browser
      await modelBrowser.show();
    } catch (error: any) {
      logger.error('Error opening model browser:', error);
      vscode.window.showErrorMessage(`Error opening model browser: ${error.message}`);
    }
  }

  /**
   * Configures DMac integration
   */
  private async configureDMacIntegration(): Promise<void> {
    try {
      // Get current config
      const config = this.dmacConfigManager.getConfig();

      // Show enabled quick pick
      const enabled = await vscode.window.showQuickPick(
        [
          { label: 'Yes', description: 'Enable DMac integration', value: true },
          { label: 'No', description: 'Disable DMac integration', value: false }
        ],
        {
          placeHolder: 'Enable DMac integration?'
        }
      );

      if (!enabled) {
        return;
      }

      // Update config
      await this.dmacConfigManager.updateConfig({
        enabled: enabled.value
      });

      if (enabled.value) {
        // Show ChromaDB URL input box
        const chromaDbUrl = await vscode.window.showInputBox({
          prompt: 'Enter ChromaDB URL',
          placeHolder: 'http://localhost:8000',
          value: config.chromaDbUrl
        });

        if (!chromaDbUrl) {
          return;
        }

        // Show shared ChromaDB quick pick
        const useSharedChromaDb = await vscode.window.showQuickPick(
          [
            { label: 'Yes', description: 'Use shared ChromaDB instance from DMac', value: true },
            { label: 'No', description: 'Use separate ChromaDB instance', value: false }
          ],
          {
            placeHolder: 'Use shared ChromaDB instance from DMac?'
          }
        );

        if (!useSharedChromaDb) {
          return;
        }

        // Show agent communication quick pick
        const agentCommunicationEnabled = await vscode.window.showQuickPick(
          [
            { label: 'Yes', description: 'Enable communication with other DMac agents', value: true },
            { label: 'No', description: 'Disable communication with other DMac agents', value: false }
          ],
          {
            placeHolder: 'Enable communication with other DMac agents?'
          }
        );

        if (!agentCommunicationEnabled) {
          return;
        }

        // Update config
        await this.dmacConfigManager.updateConfig({
          chromaDbUrl,
          useSharedChromaDb: useSharedChromaDb.value,
          agentCommunicationEnabled: agentCommunicationEnabled.value
        });
      }

      // Show success message
      vscode.window.showInformationMessage('DMac integration configured successfully');
    } catch (error: any) {
      logger.error('Error configuring DMac integration:', error);
      vscode.window.showErrorMessage(`Error configuring DMac integration: ${error.message}`);
    }
  }
}
