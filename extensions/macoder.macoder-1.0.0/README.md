# MaCoder

Advanced AI-powered coding assistant for VS Code.

## Features

- **Intelligent Code Generation**: Generate high-quality code from natural language descriptions using multiple strategies
- **Automated Testing**: Generate tests for your code with various testing frameworks
- **Advanced Debugging**: Analyze errors and get detailed solutions
- **Performance Analysis**: Identify performance issues in your code
- **Code Improvements**: Get suggestions to improve code quality, maintainability, and security
- **Domain Detection**: Automatically detect your project's domain and technology stack
- **Brainstorming Mode**: Generate ideas and solutions for complex problems
- **Autonomous Mode**: Let MaCoder work independently on complex tasks
- **Model Management**: Browse, download, and manage AI models from different providers
- **DMac Integration**: Seamlessly integrate with the DMac ecosystem

## Getting Started

1. Open the MaCoder panel by running the command `MaCoder: Open Panel` from the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS)
2. Explore the different tabs in the panel to discover MaCoder's features
3. Try generating some code by clicking on the "Generate Code" button or running the command `MaCoder: Generate Code`

## Requirements

- VS Code 1.60.0 or higher
- For local model support: Ollama or LocalAI installed

## Extension Settings

This extension contributes the following settings:

* `macoder.logLevel`: Set the log level for MaCoder (debug, info, warn, error)
* `macoder.modelProvider`: Select the model provider to use (ollama, huggingface)
* `macoder.modelId`: Specify the model ID to use
* `macoder.ollamaBaseUrl`: Set the base URL for the Ollama API
* `macoder.huggingfaceApiKey`: Set your HuggingFace API key
* `macoder.dmacIntegration.enabled`: Enable or disable DMac integration
* `macoder.dmacIntegration.chromaDbUrl`: Set the URL for ChromaDB
* `macoder.dmacIntegration.useSharedChromaDb`: Use shared ChromaDB instance from DMac
* `macoder.dmacIntegration.agentCommunicationEnabled`: Enable communication with other DMac agents

## Known Issues

- Some features may require specific model providers or models to be installed
- Performance may vary depending on the hardware and models used

## Release Notes

### 1.0.0

Initial release of MaCoder with the following features:
- Code generation with multiple strategies
- Test generation for various frameworks
- Error analysis and debugging
- Performance analysis
- Code improvement suggestions
- Domain detection
- Brainstorming mode
- Autonomous mode
- Model management
- DMac integration
