# MaCoder User Guide

## Introduction

Welcome to MaCoder, an advanced AI-powered coding assistant for VS Code. MaCoder is designed to enhance your coding experience with intelligent code generation, testing, debugging, and more. This document provides comprehensive information on how to use MaCoder effectively.

## Getting Started

After installing MaCoder, you'll see a welcome message with a brief introduction. To get started:

1. Open the MaCoder panel by running the command `MaCoder: Open Panel` from the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS)
2. Explore the different tabs in the panel to discover MaCoder's features
3. Try generating some code by clicking on the "Generate Code" button or running the command `MaCoder: Generate Code`

## Main Features

### Code Generation

MaCoder can generate code based on natural language descriptions. It uses different strategies depending on the task to produce high-quality code.

#### How to Use Code Generation

1. Run the command `MaCoder: Generate Code` from the Command Palette or click the "Generate Code" button in the MaCoder panel
2. Enter a description of the code you want to generate (e.g., "Generate a function that sorts an array of objects by a property")
3. Select the programming language
4. MaCoder will analyze your task and suggest an appropriate generation strategy
5. You can accept the suggested strategy or choose a different one
6. MaCoder will generate the code and open it in a new editor
7. You can provide feedback on the generated code by clicking "Accept", "Modify", or "Reject"

### Testing

MaCoder can generate tests for your code using various testing frameworks.

#### How to Generate Tests

1. Open the file you want to generate tests for
2. Run the command `MaCoder: Generate Tests` from the Command Palette or click the "Generate Tests" button in the MaCoder panel
3. Select the testing framework (e.g., Jest, Mocha, Pytest)
4. Select the coverage level (basic or full)
5. Choose whether to include edge cases and mocks
6. MaCoder will generate tests and create a test file
7. The test file will be opened in the editor

### Debugging

MaCoder provides powerful debugging capabilities to help you identify and fix issues in your code.

#### Analyzing Errors

1. Run the command `MaCoder: Analyze Error` from the Command Palette or click the "Analyze Error" button in the MaCoder panel
2. Enter the error message
3. Optionally, enter the stack trace
4. MaCoder will analyze the error and provide:
   - The cause of the error
   - A solution
   - Related documentation
   - Examples
   - Code context (if available)

### Performance Analysis

MaCoder can analyze your code for performance issues and suggest improvements.

#### How to Analyze Performance

1. Open the file you want to analyze
2. Run the command `MaCoder: Analyze Performance` from the Command Palette or click the "Analyze Performance" button in the MaCoder panel
3. MaCoder will analyze the code and identify potential performance issues
4. The results will be displayed in a new document with:
   - A summary of performance issues
   - Recommendations for improvement
   - Detailed information about each issue

### Code Improvements

MaCoder can suggest improvements to your code to enhance its quality, maintainability, and security.

#### How to Get Code Improvement Suggestions

1. Open the file you want to improve
2. Run the command `MaCoder: Suggest Improvements` from the Command Palette or click the "Suggest Improvements" button in the MaCoder panel
3. MaCoder will analyze the code and suggest improvements
4. The results will be displayed in a new document with:
   - A summary of issues
   - Detailed information about each issue
   - Suggested fixes
5. You can apply the improvements by clicking "Apply Improvements" or view the improved code by clicking "Show Improved Code"

### Domain Detection

MaCoder can detect the domain and technology stack of your project to provide more relevant suggestions.

#### How to Detect Domain

1. Run the command `MaCoder: Detect Project Domain` from the Command Palette or click the "Detect Domain" button in the MaCoder panel
2. MaCoder will analyze your project and identify:
   - The domain type (e.g., web, data science, mobile)
   - Frameworks used
   - Languages used
   - Patterns used
3. The results will be displayed in a new document with detailed information about the domain and knowledge base

### Brainstorming Mode

MaCoder's Brainstorming Mode helps you generate ideas and solutions for complex problems.

#### How to Use Brainstorming Mode

1. Run the command `MaCoder: Open Brainstorming Mode` from the Command Palette or click the "Open Brainstorming" button in the MaCoder panel
2. Enter a topic to brainstorm (e.g., "How to implement a caching system for API responses")
3. MaCoder will generate ideas and present them in a structured format
4. The results will include:
   - Context information
   - Multiple ideas with descriptions
   - Pros and cons for each idea

### Autonomous Mode

MaCoder's Autonomous Mode allows it to work independently on complex tasks.

#### How to Use Autonomous Mode

1. Run the command `MaCoder: Start Autonomous Mode` from the Command Palette or click the "Start Autonomous Mode" button in the MaCoder panel
2. Enter a task for autonomous mode (e.g., "Implement a user authentication system with login and registration")
3. MaCoder will break down the task into subtasks and work on them autonomously
4. You'll see progress updates as MaCoder works
5. When complete, MaCoder will present a summary of the work done and the generated files

## Model Management

MaCoder supports multiple AI models from different providers. You can browse, download, and manage these models using the Model Browser.

### Opening the Model Browser

Run the command `MaCoder: Open Model Browser` from the Command Palette or click the "Open Model Browser" button in the MaCoder panel.

### Browsing Models

The Model Browser has two tabs:
- **Browse Models**: Browse and search for available models
- **Installed Models**: View models that are already installed

You can:
- Search for models by name, description, or tags
- Filter models by provider
- Sort models by popularity or date
- Download models with a single click

### Supported Model Providers

- **Ollama**: Run large language models locally
- **HuggingFace**: Access models from HuggingFace Hub
- **LocalAI**: Run AI models locally with LocalAI

## Configuration

MaCoder can be configured through VS Code settings.

### General Settings

- **Log Level**: Set the log level for MaCoder (debug, info, warn, error)
- **Model Provider**: Select the model provider to use (ollama, huggingface)
- **Model ID**: Specify the model ID to use

### Ollama Settings

- **Ollama Base URL**: Set the base URL for the Ollama API (default: http://localhost:11434)

### HuggingFace Settings

- **HuggingFace API Key**: Set your HuggingFace API key

### DMac Integration Settings

- **Enabled**: Enable or disable DMac integration
- **ChromaDB URL**: Set the URL for ChromaDB (default: http://localhost:8000)
- **Use Shared ChromaDB**: Use the shared ChromaDB instance from DMac
- **Agent Communication Enabled**: Enable or disable communication with other DMac agents

### How to Access Settings

1. Open VS Code settings (`Ctrl+,` or `Cmd+,` on macOS)
2. Search for "MaCoder"
3. Adjust the settings as needed

## DMac Integration

MaCoder can integrate with the DMac ecosystem for enhanced capabilities.

### Features

- **Shared ChromaDB**: Use the shared ChromaDB instance from DMac for context storage
- **Agent Communication**: Communicate with other DMac agents
- **Unified Context**: Share context between MaCoder and other DMac components

### Configuring DMac Integration

1. Run the command `MaCoder: Configure DMac Integration` from the Command Palette
2. Enable or disable DMac integration
3. Configure ChromaDB settings
4. Enable or disable agent communication

## Troubleshooting

### Common Issues

#### MaCoder Panel Doesn't Open

- Make sure MaCoder is installed correctly
- Try reloading VS Code (`Ctrl+R` or `Cmd+R` on macOS)
- Check the VS Code output panel for errors (View > Output, then select "MaCoder" from the dropdown)

#### Code Generation Fails

- Check if the selected model provider is available
- For Ollama, make sure the Ollama service is running
- For HuggingFace, check if your API key is valid
- Try a different model or provider

#### Model Download Fails

- Check your internet connection
- Make sure you have sufficient disk space
- For Ollama models, ensure Ollama is running
- For HuggingFace models, verify your API key

### Logs

MaCoder logs information to the VS Code output panel. To view logs:

1. Open the Output panel (View > Output or `Ctrl+Shift+U`)
2. Select "MaCoder" from the dropdown menu

You can adjust the log level in MaCoder settings to see more or less detailed logs.
