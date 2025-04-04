# DMac AI Agent Swarm for VS Code

This extension integrates the DMac AI Agent Swarm directly into VS Code, allowing you to leverage AI agents for coding, research, and task automation without leaving your development environment.

## Features

### AI-Powered Code Assistance
- **Generate Code**: Describe what you want to build, and DMac will generate the code for you.
- **Explain Code**: Select code and get a detailed explanation of how it works.
- **Optimize Code**: Improve the performance and readability of your code with AI suggestions.
- **Debug Code**: Identify and fix issues in your code with AI-powered debugging.

### AI Agent Swarm
- **Create and Manage Agents**: Create specialized AI agents for different tasks.
- **Task Automation**: Assign tasks to agents and monitor their progress.
- **Collaborative Problem Solving**: Use multiple agents to solve complex problems.

### Chat Interface
- **Integrated Chat**: Chat with AI models directly within VS Code.
- **Context-Aware Responses**: The AI understands your project context for more relevant assistance.
- **Multiple Models**: Choose from various AI models based on your needs.

## Requirements

- VS Code 1.60.0 or higher
- DMac server running locally or remotely

## Extension Settings

This extension contributes the following settings:

* `dmac.serverUrl`: URL of the DMac server (default: "http://localhost:8080")
* `dmac.defaultModel`: Default AI model to use (default: "gemma3:12b")
* `dmac.enableAutoSuggestions`: Enable automatic code suggestions (default: true)

## Getting Started

1. Install the extension from the VS Code Marketplace
2. Make sure the DMac server is running
3. Configure the server URL in the extension settings if needed
4. Use the DMac commands from the command palette (Ctrl+Shift+P) or the DMac sidebar

## Commands

- `DMac: Start AI Agent`: Create a new AI agent
- `DMac: Open Chat Interface`: Open the chat interface to interact with AI models
- `DMac: Generate Code`: Generate code based on a description
- `DMac: Explain Selected Code`: Get an explanation of the selected code
- `DMac: Optimize Selected Code`: Get suggestions to optimize the selected code
- `DMac: Debug Selected Code`: Identify and fix issues in the selected code

## Known Issues

- The extension requires a running DMac server to function properly.
- Some features may be limited based on the capabilities of the selected AI model.

## Release Notes

### 0.1.0

- Initial release of DMac VS Code extension
- Basic integration with DMac server
- Code generation, explanation, optimization, and debugging
- Chat interface
- Agent management

## About DMac

DMac is an AI agent swarm platform that allows you to create, manage, and deploy AI agents for various tasks. It leverages multiple AI models and provides a unified interface for interacting with them.

For more information, visit [DMac GitHub Repository](https://github.com/jluna0413/dmac).
