import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { logger } from './core/logger';
import { ContextEngine } from './context-engine';
import { CodeGenerationStrategyEngine } from './generation/strategy-engine';
import { PluginManager } from './plugins/plugin-manager';
import { IncrementalLearner } from './learning/incremental-learner';
import { DomainAdapter } from './domain/domain-adapter';
import { TestGenerationEngine } from './testing/test-generation-engine';
import { DebugAssistant } from './debugging/debug-assistant';
import { ProviderManager } from './model-providers/provider-manager';
import { OllamaProvider } from './model-providers/ollama-provider';
import { HuggingFaceProvider } from './model-providers/huggingface-provider';
import { DMacConfigManager } from './dmac-integration/config';
import { ChromaClient } from './dmac-integration/chroma-client';
import { AgentCommunication } from './dmac-integration/agent-communication';
import { Commands } from './ui/commands';

// Global instances
let contextEngine: ContextEngine | undefined;
let strategyEngine: CodeGenerationStrategyEngine | undefined;
let pluginManager: PluginManager | undefined;
let incrementalLearner: IncrementalLearner | undefined;
let domainAdapter: DomainAdapter | undefined;
let testGenerationEngine: TestGenerationEngine | undefined;
let debugAssistant: DebugAssistant | undefined;
let providerManager: ProviderManager | undefined;
let dmacConfigManager: DMacConfigManager | undefined;
let chromaClient: ChromaClient | undefined;
let agentCommunication: AgentCommunication | undefined;
let commands: Commands | undefined;

// Activation function
export async function activate(context: vscode.ExtensionContext) {
  try {
    // Initialize logger
    logger.initialize(context);
    logger.info('MaCoder extension is now active!');

    // Create storage directory if it doesn't exist
    const storageDir = context.globalStorageUri.fsPath;
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }

    // Initialize context engine
    contextEngine = new ContextEngine();
    await contextEngine.initialize();

    // Initialize strategy engine
    strategyEngine = new CodeGenerationStrategyEngine();

    // Initialize plugin manager
    pluginManager = new PluginManager(context);

    // Discover plugins
    const pluginsPath = path.join(context.extensionPath, 'plugins');
    await pluginManager.discoverPlugins(pluginsPath);

    // Initialize incremental learner
    incrementalLearner = new IncrementalLearner(context);

    // Initialize domain adapter
    domainAdapter = new DomainAdapter(context);

    // Initialize test generation engine
    testGenerationEngine = new TestGenerationEngine();

    // Initialize debug assistant
    debugAssistant = new DebugAssistant();

    // Initialize provider manager
    providerManager = new ProviderManager();

    // Register providers
    const config = vscode.workspace.getConfiguration('macoder');

    // Register Ollama provider
    const ollamaBaseUrl = config.get<string>('ollamaBaseUrl', 'http://localhost:11434');
    providerManager.registerProvider(new OllamaProvider({ baseUrl: ollamaBaseUrl }));

    // Register HuggingFace provider
    const huggingfaceApiKey = config.get<string>('huggingfaceApiKey', '');
    if (huggingfaceApiKey) {
      providerManager.registerProvider(new HuggingFaceProvider({ apiKey: huggingfaceApiKey }));
    }

    // Initialize DMac integration
    dmacConfigManager = new DMacConfigManager(context);

    // Initialize ChromaDB client
    chromaClient = new ChromaClient(dmacConfigManager);

    // Initialize agent communication
    agentCommunication = new AgentCommunication(dmacConfigManager);

    // Start message processing
    const messageProcessingDisposable = agentCommunication.startMessageProcessing();
    context.subscriptions.push(messageProcessingDisposable);

    // Initialize commands
    commands = new Commands(
      context,
      contextEngine,
      strategyEngine,
      pluginManager,
      incrementalLearner,
      domainAdapter,
      testGenerationEngine,
      debugAssistant,
      providerManager,
      dmacConfigManager
    );

    // Register commands
    commands.registerCommands();

    // Set active provider
    const modelProvider = config.get<string>('modelProvider', 'ollama');
    const modelId = config.get<string>('modelId', 'codellama:7b');

    try {
      await providerManager.setActiveProvider(modelProvider, modelId);
      logger.info(`Active provider set to ${modelProvider} with model ${modelId}`);
    } catch (error: any) {
      logger.warn(`Error setting active provider: ${error.message}`);
    }

    // Show welcome message on first install
    const firstInstall = context.globalState.get('firstInstall', true);
    if (firstInstall) {
      vscode.window.showInformationMessage(
        'MaCoder has been installed! Use the MaCoder panel or commands to get started.'
      );
      context.globalState.update('firstInstall', false);
    }

    logger.info('MaCoder extension activated successfully');
  } catch (error: any) {
    logger.error('Error activating MaCoder extension:', error);
    vscode.window.showErrorMessage(`Error activating MaCoder extension: ${error.message}`);
  }
}

// Deactivation function
export async function deactivate() {
  try {
    // Dispose context engine
    if (contextEngine) {
      contextEngine.dispose();
    }

    // Dispose plugin manager
    if (pluginManager) {
      pluginManager.dispose();
    }

    // Dispose provider manager
    if (providerManager) {
      await providerManager.dispose();
    }

    logger.info('MaCoder extension is now deactivated!');
  } catch (error: any) {
    logger.error('Error deactivating MaCoder extension:', error);
  }
}

// Global instance getters
export function getContextEngine(): ContextEngine {
  if (!contextEngine) {
    throw new Error('Context engine not initialized');
  }

  return contextEngine;
}

export function getStrategyEngine(): CodeGenerationStrategyEngine {
  if (!strategyEngine) {
    throw new Error('Strategy engine not initialized');
  }

  return strategyEngine;
}

export function getPluginManager(): PluginManager {
  if (!pluginManager) {
    throw new Error('Plugin manager not initialized');
  }

  return pluginManager;
}

export function getIncrementalLearner(): IncrementalLearner {
  if (!incrementalLearner) {
    throw new Error('Incremental learner not initialized');
  }

  return incrementalLearner;
}

export function getDomainAdapter(): DomainAdapter {
  if (!domainAdapter) {
    throw new Error('Domain adapter not initialized');
  }

  return domainAdapter;
}

export function getTestGenerationEngine(): TestGenerationEngine {
  if (!testGenerationEngine) {
    throw new Error('Test generation engine not initialized');
  }

  return testGenerationEngine;
}

export function getDebugAssistant(): DebugAssistant {
  if (!debugAssistant) {
    throw new Error('Debug assistant not initialized');
  }

  return debugAssistant;
}

export function getProviderManager(): ProviderManager {
  if (!providerManager) {
    throw new Error('Provider manager not initialized');
  }

  return providerManager;
}

export function getDMacConfigManager(): DMacConfigManager {
  if (!dmacConfigManager) {
    throw new Error('DMac config manager not initialized');
  }

  return dmacConfigManager;
}

export function getChromaClient(): ChromaClient {
  if (!chromaClient) {
    throw new Error('ChromaDB client not initialized');
  }

  return chromaClient;
}

export function getAgentCommunication(): AgentCommunication {
  if (!agentCommunication) {
    throw new Error('Agent communication not initialized');
  }

  return agentCommunication;
}
