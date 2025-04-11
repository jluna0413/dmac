# MaCoder User Guide

This guide provides detailed instructions on how to use the MaCoder VS Code extension.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Modes of Operation](#modes-of-operation)
4. [Basic Features](#basic-features)
5. [Sidebar Interface](#sidebar-interface)
5. [Advanced Features](#advanced-features)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Installation

1. Download the extension from the VS Code Marketplace
2. Install the extension in VS Code
3. Configure the extension settings (optional)

### For Standalone Mode

1. Install [Ollama](https://ollama.ai/) (recommended) or [LM Studio](https://lmstudio.ai/)
2. For Ollama, pull a model: `ollama pull gemma3:12b` (or another model of your choice)
3. Set `macoder.preferStandalone` to `true` in VS Code settings

## Getting Started

After installing MaCoder, you can access its features through the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).

The most common commands are:

- `MaCoder: Start Chat`: Open the chat panel
- `MaCoder: Next Edit`: Get step-by-step guidance for complex changes
- `MaCoder: Generate Code`: Generate code from a description
- `MaCoder: Show Autonomous Mode Panel`: Open the autonomous mode panel
- `MaCoder: Show Brainstorming Panel`: Open the brainstorming panel

## Modes of Operation

MaCoder can operate in two modes:

### Integrated Mode

In integrated mode, MaCoder connects to the DMac server to leverage its advanced capabilities:

- Neural network of specialized agents
- Comprehensive code indexing and retrieval
- Enhanced context awareness
- Collaborative capabilities with other DMac agents

### Standalone Mode

In standalone mode, MaCoder works completely independently:

- Uses local LLM providers like Ollama or LM Studio
- All processing happens locally on your machine
- No external dependencies or internet connection required
- Full privacy with no data leaving your computer

### Switching Modes

To switch between modes:

1. Use the command palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Toggle Between DMac and Standalone Mode`
3. The current mode is displayed in the status bar: `MaCoder [dmac]` or `MaCoder [standalone]`

## Basic Features

### Chat

The chat feature allows you to ask questions about your code and codebase:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Start Chat`
3. Ask questions about your code or codebase

### Next Edit

Next Edit provides step-by-step guidance for complex changes:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Next Edit`
3. Describe the changes you want to make
4. Follow the step-by-step guidance

### Code Completions

Code completions are automatically provided as you type. They are context-aware and understand your codebase.

### Code Generation

Generate code from a description:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Generate Code`
3. Describe the code you want to generate

### Code Explanation

Get an explanation of selected code:

1. Select the code you want to explain
2. Right-click and select `MaCoder: Explain Code` or use the Command Palette

### Code Refactoring

Refactor selected code:

1. Select the code you want to refactor
2. Right-click and select `MaCoder: Refactor Code` or use the Command Palette
3. Describe how you want to refactor the code

## Sidebar Interface

MaCoder provides a full sidebar interface in the VS Code Activity Bar. Click on the MaCoder icon in the Activity Bar to access the sidebar.

### Chat View

The Chat view allows you to interact with MaCoder directly:

1. Type your message in the text area at the bottom
2. Press Enter or click the Send button
3. MaCoder will respond with helpful information

### Code Generation View

The Code Generation view helps you generate code based on your instructions:

1. Enter your instructions in the text area
2. Select the programming language from the dropdown
3. Click the "Generate Code" button
4. Review the generated code
5. Use the action buttons to insert the code, create a new file, or copy to clipboard

### Brainstorming View

The Brainstorming view helps you generate ideas and create development roadmaps:

1. Enter a topic in the "Topic" field
2. Optionally add context in the "Context" field
3. Click "Start Brainstorming"
4. Review the generated ideas
5. Click "Generate Roadmap" to create a development plan
6. Use "Export Roadmap" to save the roadmap as a Markdown file

### Sandbox View

The Sandbox view allows you to test code snippets without affecting your project files:

1. Select a programming language from the dropdown
2. Enter your code in the editor
3. Click "Run Code" to execute it
4. View the output in the output panel
5. Use "Save to File" to save your code
6. Use "Load from File" to load existing code

### Settings View

The Settings view allows you to configure MaCoder according to your preferences:

- Model Provider (Ollama, OpenAI, Gemini)
- Provider-specific settings (API keys, models, URLs)
- Generation settings (temperature, max tokens, context size)
- Feature toggles (project indexing, code verification, etc.)

## Advanced Features

### Autonomous Mode

Autonomous mode allows MaCoder to complete complex tasks autonomously:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Show Autonomous Mode Panel`
3. Click the Start button to activate autonomous mode
4. Enter a task description and click Execute Task
5. MaCoder will autonomously complete the task

Tasks can include:
- Code generation
- Code refactoring
- Bug finding
- Test generation
- Documentation

### Project Indexing

MaCoder automatically indexes your project in standalone mode for better context awareness. To manually refresh the index:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Refresh Code Index`

The index includes:
- File information
- Symbol information (functions, classes, methods, etc.)
- Relationships between files and symbols

### Brainstorming

The brainstorming feature helps you generate and organize ideas for your projects:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Show Brainstorming Panel`
3. Create a new brainstorming session
4. Add ideas manually or generate them with AI
5. Create roadmaps from your brainstorming sessions

### Roadmap Generation

Create project roadmaps from your brainstorming sessions:

1. Open a brainstorming session
2. Click the Create Roadmap button
3. Enter a title and description for the roadmap
4. MaCoder will generate a roadmap with tasks, priorities, and dependencies

### Deep Reasoning

The deep reasoning feature helps you analyze complex problems from multiple angles:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Show Deep Reasoning Panel` or `MaCoder: Perform Deep Reasoning`
3. Enter a problem to reason about
4. MaCoder will analyze the problem from multiple angles
5. Review the observations, thoughts, actions, and conclusions

You can also add your own reasoning steps manually:

1. Open a reasoning chain
2. Click the Add Step button
3. Enter the step content and select the step type
4. Click Add

### Code Verification

Verify code for syntax and style issues:

1. Select the code you want to verify (or don't select anything to verify the entire file)
2. Right-click and select `MaCoder: Verify Code` or use the Command Palette
3. MaCoder will check the code for syntax and style issues
4. Issues will be displayed in the Problems panel

### Enhanced Context Awareness

MaCoder tracks your code edits to provide better context for suggestions:

1. Code edits are automatically tracked as you work
2. You can organize related changes into sessions:
   - Open the Command Palette (`Ctrl+Shift+P`)
   - Type `MaCoder: Start New Edit Session` to start a new session
   - Enter a description for the session (e.g., "Implementing feature X")
   - When you're done, use `MaCoder: End Current Edit Session`
3. Edit sessions help MaCoder understand the context of your changes

### Sandbox Testing and Debugging

Test and debug your code in an isolated environment:

1. Open the Sandbox Panel:
   - Open the Command Palette (`Ctrl+Shift+P`)
   - Type `MaCoder: Show Sandbox Panel`
2. Execute code directly:
   - Enter your code in the Execute Code tab
   - Select the language
   - Click Execute
3. Execute selected code:
   - Select code in your editor
   - Right-click and select `MaCoder: Execute Code in Sandbox` or use the Command Palette
4. Create and manage test cases:
   - Click New Test in the Tests tab
   - Enter a name, code, and select a language
   - Run tests and view results

### Switching Model Providers

In standalone mode, you can switch between different model providers:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Switch Local Model Provider`
3. Select the provider you want to use (Ollama or LM Studio)

## Configuration

MaCoder can be configured through VS Code settings:

### General Settings

* `macoder.modelName`: The name of the model to use for code generation and completion
* `macoder.temperature`: The temperature to use for code generation and completion
* `macoder.maxContextLength`: The maximum context length to use for code generation and completion
* `macoder.benchmarkModels`: The models to use for benchmarking
* `macoder.enableCompletions`: Enable code completions
* `macoder.enableChat`: Enable chat
* `macoder.enableNextEdit`: Enable next edit
* `macoder.enableInstructions`: Enable instructions

### Mode Settings

* `macoder.serverUrl`: The URL of the DMac server (for integrated mode)
* `macoder.preferStandalone`: Whether to prefer standalone mode even if DMac is available
* `macoder.localModelProvider`: The local model provider to use in standalone mode (ollama or lmstudio)
* `macoder.ollamaUrl`: The URL of the Ollama server (default: http://localhost:11434)
* `macoder.lmStudioUrl`: The URL of the LM Studio server (default: http://localhost:1234)

### Brainstorming Settings

* `macoder.brainstorming`: Storage for brainstorming sessions and roadmaps

### Deep Reasoning Settings

* `macoder.deepReasoning`: Storage for deep reasoning chains

### Code Verification Settings

* `macoder.codeVerification`: Settings for code verification

### Context Awareness Settings

* `macoder.enableCodeEditLogging`: Enable code edit logging for enhanced context awareness

### Sandbox Settings

* `macoder.enableSandbox`: Enable sandbox for testing and debugging code

### Laminar Integration

* `macoder.laminar.enabled`: Enable Laminar integration for tracing and evaluation
* `macoder.laminar.projectApiKey`: The Laminar project API key
* `macoder.laminar.baseUrl`: The Laminar API base URL
* `macoder.laminar.selfHosted`: Use self-hosted Laminar instance

## Troubleshooting

### Integrated Mode Issues

- **DMac server not found**: Make sure the DMac server is running and accessible
- **Connection issues**: Check the server URL in the settings
- **Authentication issues**: Make sure you have the correct credentials

### Standalone Mode Issues

- **Ollama not found**: Make sure Ollama is installed and running
- **Model not available**: Run `ollama pull <model-name>` to download the model
- **Slow performance**: Try using a smaller model or adjust the settings

### Project Indexing Issues

- **Slow indexing**: For large projects, initial indexing may take time
- **High memory usage**: The index is kept in memory, so large projects may use more memory
- **Missing files**: Some files might be excluded by the indexing settings

### Autonomous Mode Issues

- **Task parsing failures**: Make sure your task descriptions are clear and specific
- **Task execution failures**: Complex tasks may not be completed successfully
- **Timeouts**: Very large operations might timeout

### Brainstorming Issues

- **Poor idea quality**: The quality of generated ideas depends on the model used
- **Storage issues**: Brainstorming data is stored locally and not synchronized across devices

### Deep Reasoning Issues

- **Analysis quality**: The quality of the reasoning depends on the model used
- **Complex problems**: Very complex problems may require multiple reasoning chains
- **Reasoning steps**: Steps may sometimes be incomplete or imprecise

### Code Verification Issues

- **Verification quality**: The quality of the verification depends on the model used
- **Language support**: Some languages may not be fully supported
- **Line and column numbers**: Line and column numbers may not always be accurate

### Enhanced Context Awareness Issues

- **Performance**: Large edit sessions may impact performance
- **Complex refactorings**: Some complex refactorings may not be tracked accurately
- **Storage**: Edit sessions are stored locally and not synchronized across devices

### Sandbox Testing and Debugging Issues

- **Environment limitations**: The sandbox is limited to tools and languages installed on your system
- **Setup requirements**: Some languages may require additional setup to work properly
- **Execution limits**: Execution time is limited to prevent infinite loops
- **Security**: The sandbox is isolated but not completely secure for malicious code

If you encounter any other issues, please report them on the [GitHub repository](https://github.com/jluna0413/dmac).
