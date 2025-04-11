# MaCoder User Guide

MaCoder is an AI-powered coding assistant for VS Code that helps you generate code, tests, and improve your codebase.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Features](#features)
   - [Code Generation](#code-generation)
   - [Test Generation](#test-generation)
   - [Error Analysis](#error-analysis)
   - [Performance Analysis](#performance-analysis)
   - [Code Improvements](#code-improvements)
   - [Domain Detection](#domain-detection)
   - [Brainstorming Mode](#brainstorming-mode)
   - [Autonomous Mode](#autonomous-mode)
   - [Model Management](#model-management)
   - [DMac Integration](#dmac-integration)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

## Installation

1. Download the MaCoder extension from the VS Code Marketplace or install it from the VSIX file.
2. Install the required dependencies:
   - Ollama: Follow the installation instructions at [https://ollama.ai/](https://ollama.ai/)
   - (Optional) HuggingFace API key: Sign up at [https://huggingface.co/](https://huggingface.co/)

## Getting Started

1. Open VS Code.
2. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
3. Type "MaCoder: Open Panel" and press Enter.
4. The MaCoder panel will open, showing the available features.

## Features

### Code Generation

MaCoder can generate code based on your description. It uses different strategies to generate code for various tasks.

To generate code:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Generate Code" and press Enter.
3. Enter a description of the code you want to generate.
4. Select a language.
5. Select a strategy (or use Auto-select).
6. MaCoder will generate the code and open it in a new editor.

Available strategies:

- **Direct Generation**: Generates code directly from the task description. Suitable for simple tasks, small functions, and utility methods.
- **Divide and Conquer**: Breaks down complex tasks into smaller, manageable subtasks. Suitable for complex systems, multi-file projects, and large functions.
- **Test-Driven**: Generates tests first, then implements code to pass the tests. Suitable for well-defined requirements, algorithms, and data structures.
- **Example-Based**: Generates code based on provided examples. Suitable for similar tasks, variations of existing code, and pattern implementation.
- **Iterative Refinement**: Generates an initial solution and iteratively refines it. Suitable for optimization tasks, complex algorithms, and performance-critical code.

### Test Generation

MaCoder can generate tests for your code using various testing frameworks.

To generate tests:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Generate Tests" and press Enter.
3. Select a file to test.
4. Select a testing framework.
5. Configure the test options.
6. MaCoder will generate the tests and open them in a new editor.

Supported testing frameworks:

- **Jest**: For JavaScript/TypeScript
- **Mocha**: For JavaScript/TypeScript
- **Pytest**: For Python
- **JUnit**: For Java

### Error Analysis

MaCoder can analyze errors and provide solutions.

To analyze an error:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Analyze Error" and press Enter.
3. Enter the error message.
4. (Optional) Enter the stack trace.
5. (Optional) Enter the code that caused the error.
6. MaCoder will analyze the error and provide a solution.

### Performance Analysis

MaCoder can analyze the performance of your code and suggest improvements.

To analyze performance:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Analyze Performance" and press Enter.
3. Select a file to analyze.
4. MaCoder will analyze the performance and provide recommendations.

### Code Improvements

MaCoder can suggest improvements to your code.

To suggest improvements:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Suggest Improvements" and press Enter.
3. Select a file to improve.
4. MaCoder will suggest improvements and provide an improved version of the code.
5. You can choose to apply the improvements.

### Domain Detection

MaCoder can detect the domain and technology stack of your project to provide more relevant suggestions.

To detect the domain:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Detect Project Domain" and press Enter.
3. MaCoder will analyze your project and detect the domain.

### Brainstorming Mode

Brainstorming mode helps you generate ideas and solutions for complex problems.

To use brainstorming mode:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Open Brainstorming Mode" and press Enter.
3. Enter a topic to brainstorm.
4. MaCoder will generate ideas and solutions.

### Autonomous Mode

Autonomous mode allows MaCoder to work independently on complex tasks.

To use autonomous mode:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Start Autonomous Mode" and press Enter.
3. Enter a task for autonomous mode.
4. MaCoder will break down the task into subtasks and execute them.

### Model Management

MaCoder can use different models for code generation. You can browse and manage models using the Model Browser.

To open the Model Browser:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Open Model Browser" and press Enter.
3. Browse and select models.

### DMac Integration

MaCoder can integrate with DMac to use its ChromaDB instance and communicate with other DMac agents.

To configure DMac integration:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
2. Type "MaCoder: Configure DMac Integration" and press Enter.
3. Configure the integration options.

## Configuration

MaCoder can be configured using the VS Code settings. Open the settings by pressing `Ctrl+,` (Windows/Linux) or `Cmd+,` (Mac) and search for "MaCoder".

Available settings:

- **MaCoder: Log Level**: Log level for MaCoder (debug, info, warn, error).
- **MaCoder: Model Provider**: Model provider to use (ollama, huggingface).
- **MaCoder: Model ID**: Model ID to use.
- **MaCoder: Ollama Base URL**: Base URL for Ollama API.
- **MaCoder: HuggingFace API Key**: API key for HuggingFace.
- **MaCoder: DMac Integration: Enabled**: Enable DMac integration.
- **MaCoder: DMac Integration: ChromaDB URL**: URL for ChromaDB.
- **MaCoder: DMac Integration: Use Shared ChromaDB**: Use shared ChromaDB instance from DMac.
- **MaCoder: DMac Integration: Agent Communication Enabled**: Enable communication with other DMac agents.

## Troubleshooting

If you encounter issues with MaCoder, try the following:

1. Check the MaCoder output channel in VS Code for error messages.
2. Make sure Ollama is running if you're using the Ollama provider.
3. Check your HuggingFace API key if you're using the HuggingFace provider.
4. Restart VS Code.
5. Reinstall the extension.

## FAQ

### Q: How do I change the model?

A: You can change the model in the VS Code settings or using the Model Browser.

### Q: Can I use my own models?

A: Yes, you can use any model available in Ollama or HuggingFace.

### Q: How do I add a plugin?

A: Plugins can be added to the `plugins` directory in the extension folder.

### Q: How do I provide feedback?

A: After generating code, you will be prompted to provide feedback. This feedback is used to improve future code generation.

### Q: How do I use DMac integration?

A: Configure DMac integration in the settings and make sure DMac is running.
