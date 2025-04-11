# MaCoder Developer Guide

This guide provides information for developers who want to extend or modify the MaCoder extension.

## Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [UI Components](#ui-components)
5. [Integration Components](#integration-components)
6. [Plugin System](#plugin-system)
7. [Building and Packaging](#building-and-packaging)
8. [Testing](#testing)
9. [Contributing](#contributing)

## Architecture

MaCoder is built as a VS Code extension using TypeScript. It follows a modular architecture with the following main components:

- **Core Components**: Provide the core functionality of the extension.
- **UI Components**: Provide the user interface for interacting with the extension.
- **Integration Components**: Provide integration with external systems like DMac.
- **Plugin System**: Allows extending the functionality of the extension.

## Project Structure

The project is structured as follows:

```
macoder.macoder-1.0.0/
├── .vscode/             # VS Code configuration
├── dist/                # Compiled output
├── media/               # Media files (CSS, images, etc.)
├── plugins/             # Plugins
├── src/                 # Source code
│   ├── core/            # Core components
│   ├── context-engine/  # Context engine
│   ├── debugging/       # Debugging components
│   ├── dmac-integration/# DMac integration
│   ├── domain/          # Domain adapter
│   ├── generation/      # Code generation
│   ├── learning/        # Incremental learning
│   ├── model-providers/ # Model providers
│   ├── plugins/         # Plugin system
│   ├── testing/         # Test generation
│   ├── ui/              # UI components
│   └── extension.ts     # Extension entry point
├── .eslintrc.json       # ESLint configuration
├── .gitignore           # Git ignore file
├── .vscodeignore        # VS Code ignore file
├── CHANGELOG.md         # Changelog
├── DEVELOPER_GUIDE.md   # Developer guide
├── LICENSE              # License
├── package.json         # Package configuration
├── README.md            # Readme
├── tsconfig.json        # TypeScript configuration
├── USER_GUIDE.md        # User guide
└── webpack.config.js    # Webpack configuration
```

## Core Components

### Logger

The logger provides logging functionality for the extension. It supports different log levels (debug, info, warn, error) and logs to the VS Code output channel.

```typescript
import { logger } from './core/logger';

logger.debug('Debug message');
logger.info('Info message');
logger.warn('Warning message');
logger.error('Error message');
```

### Context Engine

The context engine provides context information for code generation. It analyzes the workspace, project, directory, and file context to provide relevant information for code generation.

```typescript
import { ContextEngine } from './context-engine';

const contextEngine = new ContextEngine();
await contextEngine.initialize();

const contexts = await contextEngine.getAllContexts();
```

### Code Generation Strategy Engine

The code generation strategy engine provides different strategies for code generation. It selects the best strategy for a task and generates code using that strategy.

```typescript
import { CodeGenerationStrategyEngine } from './generation/strategy-engine';

const strategyEngine = new CodeGenerationStrategyEngine();
const code = await strategyEngine.generateCode('Generate a function that sorts an array of objects by a property', 'javascript');
```

### Plugin Manager

The plugin manager provides functionality for discovering and managing plugins. It loads plugins from the plugins directory and provides access to them.

```typescript
import { PluginManager } from './plugins/plugin-manager';

const pluginManager = new PluginManager(context);
await pluginManager.discoverPlugins(pluginsPath);

const plugins = pluginManager.getPlugins();
```

### Incremental Learner

The incremental learner provides functionality for learning from user feedback. It stores feedback and uses it to improve future code generation.

```typescript
import { IncrementalLearner, FeedbackType } from './learning/incremental-learner';

const incrementalLearner = new IncrementalLearner(context);
incrementalLearner.addFeedback('Generate a function that sorts an array of objects by a property', code, FeedbackType.POSITIVE, { language: 'javascript' });

const stats = incrementalLearner.getStats();
```

### Domain Adapter

The domain adapter provides functionality for detecting the domain and technology stack of a project. It analyzes the project and provides information about the domain, languages, frameworks, patterns, and knowledge base.

```typescript
import { DomainAdapter } from './domain/domain-adapter';

const domainAdapter = new DomainAdapter(context);
const domainInfo = await domainAdapter.detectDomain();
```

### Test Generation Engine

The test generation engine provides functionality for generating tests for code. It supports different testing frameworks and generates tests based on the code and options.

```typescript
import { TestGenerationEngine } from './testing/test-generation-engine';

const testGenerationEngine = new TestGenerationEngine();
const testFileUri = await testGenerationEngine.createTestFile(fileUri, 'jest', { coverage: 'full', includeEdgeCases: true, includeMocks: true });
```

### Debug Assistant

The debug assistant provides functionality for analyzing errors, performance, and suggesting improvements. It analyzes code and provides recommendations.

```typescript
import { DebugAssistant } from './debugging/debug-assistant';

const debugAssistant = new DebugAssistant();
const errorAnalysis = await debugAssistant.analyzeError(errorMessage, stackTrace, code);
const performanceAnalysis = await debugAssistant.analyzePerformance(code, language);
const improvements = await debugAssistant.suggestImprovements(code, language);
```

### Provider Manager

The provider manager provides functionality for managing model providers. It registers providers, lists models, and generates code using the active provider.

```typescript
import { ProviderManager } from './model-providers/provider-manager';
import { OllamaProvider } from './model-providers/ollama-provider';
import { HuggingFaceProvider } from './model-providers/huggingface-provider';

const providerManager = new ProviderManager();
providerManager.registerProvider(new OllamaProvider({ baseUrl: 'http://localhost:11434' }));
providerManager.registerProvider(new HuggingFaceProvider({ apiKey: 'your-api-key' }));

await providerManager.setActiveProvider('ollama', 'codellama:7b');
const models = await providerManager.listAllModels();
const code = await providerManager.generateCode('Generate a function that sorts an array of objects by a property');
```

## UI Components

### Main Panel

The main panel provides the main user interface for the extension. It shows the available features and allows the user to interact with them.

```typescript
import { MainPanel } from './ui/panel';

const panel = MainPanel.getInstance(context, contextEngine, strategyEngine, pluginManager, incrementalLearner, domainAdapter, testGenerationEngine, debugAssistant, providerManager);
panel.show();
```

### Model Browser

The model browser provides functionality for browsing and managing models. It shows the available models and allows the user to select the active model.

```typescript
import { ModelBrowser } from './ui/model-browser';

const modelBrowser = ModelBrowser.getInstance(context, providerManager);
await modelBrowser.show();
```

### Brainstorming Mode

Brainstorming mode provides functionality for generating ideas and solutions for complex problems. It shows a user interface for entering a topic and generates ideas.

```typescript
import { BrainstormingMode } from './ui/brainstorming';

const brainstormingMode = BrainstormingMode.getInstance(context, contextEngine, providerManager, domainAdapter);
await brainstormingMode.show();
```

### Autonomous Mode

Autonomous mode provides functionality for working independently on complex tasks. It shows a user interface for entering a task and executes it autonomously.

```typescript
import { AutonomousMode } from './ui/autonomous';

const autonomousMode = AutonomousMode.getInstance(context, contextEngine, strategyEngine, providerManager, domainAdapter, testGenerationEngine, debugAssistant);
await autonomousMode.show();
```

### Commands

The commands module provides functionality for registering and handling commands. It registers all the commands and provides handlers for them.

```typescript
import { Commands } from './ui/commands';

const commands = new Commands(context, contextEngine, strategyEngine, pluginManager, incrementalLearner, domainAdapter, testGenerationEngine, debugAssistant, providerManager, dmacConfigManager);
commands.registerCommands();
```

## Integration Components

### DMac Config Manager

The DMac config manager provides functionality for managing DMac integration configuration. It stores and retrieves configuration for DMac integration.

```typescript
import { DMacConfigManager } from './dmac-integration/config';

const dmacConfigManager = new DMacConfigManager(context);
const config = dmacConfigManager.getConfig();
await dmacConfigManager.updateConfig({ enabled: true, chromaDbUrl: 'http://localhost:8000' });
```

### ChromaDB Client

The ChromaDB client provides functionality for interacting with ChromaDB. It stores and retrieves embeddings from ChromaDB.

```typescript
import { ChromaClient } from './dmac-integration/chroma-client';

const chromaClient = new ChromaClient(dmacConfigManager);
await chromaClient.storeEmbedding('collection', 'id', [0.1, 0.2, 0.3], { metadata: 'value' });
const embeddings = await chromaClient.getEmbeddings('collection', ['id']);
```

### Agent Communication

The agent communication module provides functionality for communicating with other DMac agents. It sends and receives messages from other agents.

```typescript
import { AgentCommunication } from './dmac-integration/agent-communication';

const agentCommunication = new AgentCommunication(dmacConfigManager);
const messageProcessingDisposable = agentCommunication.startMessageProcessing();
await agentCommunication.sendMessage('agent', 'message');
```

## Plugin System

The plugin system allows extending the functionality of the extension. Plugins are loaded from the plugins directory and can provide additional functionality.

To create a plugin, create a directory in the plugins directory with the following structure:

```
plugin-name/
├── package.json
└── index.js
```

The package.json file should have the following structure:

```json
{
  "name": "plugin-name",
  "displayName": "Plugin Name",
  "description": "Plugin description",
  "version": "1.0.0",
  "main": "index.js",
  "author": "Author",
  "license": "MIT",
  "engines": {
    "vscode": "^1.60.0"
  }
}
```

The index.js file should export a Plugin class with the following structure:

```javascript
class Plugin {
  constructor() {
    this.id = 'plugin-id';
    this.name = 'Plugin Name';
    this.description = 'Plugin description';
    this.version = '1.0.0';
  }
  
  activate(context) {
    // Activate the plugin
  }
  
  deactivate() {
    // Deactivate the plugin
  }
}

exports.Plugin = Plugin;
```

## Building and Packaging

To build the extension, run the following commands:

```bash
npm install
npm run compile
```

To package the extension, run the following command:

```bash
npm run package
```

This will create a VSIX file in the dist directory that can be installed in VS Code.

## Testing

To run the tests, run the following command:

```bash
npm test
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a branch for your changes.
3. Make your changes.
4. Run the tests.
5. Submit a pull request.
