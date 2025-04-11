# MaCoder Developer Guide

## Introduction

This guide is intended for developers who want to contribute to MaCoder or extend its functionality. It provides information about the architecture, building from source, testing, and extending MaCoder with plugins.

## Architecture

MaCoder is built with a modular architecture that consists of several key components:

### Core Components

1. **Context Engine**: Provides multi-level context awareness for code understanding
2. **Code Generation Strategy Engine**: Selects optimal code generation strategies based on task characteristics
3. **Plugin Manager**: Manages plugins that extend MaCoder's functionality
4. **Incremental Learning System**: Learns from user feedback to improve over time
5. **Domain Adapter**: Adapts to the specific domain and technology stack of the project
6. **Test Generation Engine**: Generates tests for code with different frameworks and coverage levels
7. **Debug Assistant**: Analyzes errors, performance issues, and suggests code improvements
8. **Model Provider Manager**: Manages different model providers and models

### UI Components

1. **Main Panel**: The central interface for MaCoder
2. **Model Browser**: Interface for browsing and managing models
3. **Brainstorming Mode**: Interface for brainstorming ideas
4. **Autonomous Mode**: Interface for autonomous coding

### Integration Components

1. **DMac Config Manager**: Manages DMac integration configuration
2. **ChromaDB Client**: Interacts with ChromaDB for context storage
3. **Agent Communication**: Communicates with other DMac agents

## Building from Source

### Prerequisites

- Node.js 14.x or higher
- npm 6.x or higher
- VS Code 1.60.0 or higher

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/jluna0413/dmac.git
   cd dmac/extensions/macoder.macoder-1.0.0
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the extension:
   ```
   npm run compile
   ```

### Development Workflow

1. Make changes to the source code
2. Build the extension:
   ```
   npm run compile
   ```
3. Press F5 in VS Code to launch a new window with the extension loaded
4. Test your changes
5. Repeat

### Packaging

To package the extension for distribution:

```
npm run package
```

This will create a `.vsix` file that can be installed in VS Code.

## Testing

### Running Tests

To run tests:

```
npm test
```

### Writing Tests

Tests are located in the `src/test` directory. MaCoder uses Mocha for testing.

Example test:

```typescript
import * as assert from 'assert';
import * as vscode from 'vscode';
import * as myExtension from '../../extension';

suite('Extension Test Suite', () => {
  vscode.window.showInformationMessage('Start all tests.');

  test('Sample test', () => {
    assert.strictEqual(-1, [1, 2, 3].indexOf(5));
    assert.strictEqual(0, [1, 2, 3].indexOf(1));
  });
});
```

## Extending MaCoder

### Plugin System

MaCoder has a plugin system that allows you to extend its functionality. Plugins are loaded from the `plugins` directory.

### Creating a Plugin

A plugin is a JavaScript or TypeScript module that exports a `activate` function. The `activate` function is called when the plugin is loaded.

Example plugin:

```typescript
import * as vscode from 'vscode';
import { Plugin } from '../plugin-interface';

export class MyPlugin implements Plugin {
  id = 'my-plugin';
  name = 'My Plugin';
  description = 'A sample plugin for MaCoder';
  version = '1.0.0';
  
  activate(context: vscode.ExtensionContext): void {
    // Register commands, create UI, etc.
    console.log('My plugin activated');
  }
  
  deactivate(): void {
    // Clean up resources
    console.log('My plugin deactivated');
  }
}
```

### Plugin Interface

Plugins must implement the `Plugin` interface:

```typescript
export interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  
  activate(context: vscode.ExtensionContext): void;
  deactivate(): void;
}
```

### Plugin Discovery

Plugins are discovered by the `PluginManager` when the extension is activated. The `PluginManager` looks for plugins in the `plugins` directory.

## Contributing

### Code Style

MaCoder follows the [TypeScript Style Guide](https://github.com/microsoft/TypeScript/wiki/Coding-guidelines).

### Pull Requests

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Run tests
5. Submit a pull request

### Issues

If you find a bug or have a feature request, please [open an issue](https://github.com/jluna0413/dmac/issues) on GitHub.

## Documentation

### Updating Documentation

Documentation is written in Markdown and located in the `docs` directory. To update the documentation:

1. Edit the relevant Markdown files
2. Submit a pull request

### Building Documentation

Documentation is built using [Docsify](https://docsify.js.org/). To build the documentation:

1. Install Docsify:
   ```
   npm install -g docsify-cli
   ```

2. Preview the documentation:
   ```
   docsify serve docs
   ```

## Release Process

### Versioning

MaCoder follows [Semantic Versioning](https://semver.org/). Version numbers are in the format `MAJOR.MINOR.PATCH`:

- `MAJOR` version when you make incompatible API changes
- `MINOR` version when you add functionality in a backwards compatible manner
- `PATCH` version when you make backwards compatible bug fixes

### Creating a Release

1. Update the version number in `package.json`
2. Update the `CHANGELOG.md` file
3. Commit the changes
4. Create a tag for the version:
   ```
   git tag v1.0.0
   ```
5. Push the tag:
   ```
   git push origin v1.0.0
   ```
6. Create a release on GitHub
7. Upload the `.vsix` file to the release

## Support

If you need help with development, please [open an issue](https://github.com/jluna0413/dmac/issues) on GitHub.
