# MaCoder for Visual Studio Code

MaCoder is a powerful AI coding assistant with code completion functionality, inspired by Augment Code. It can work in two modes:

1. **Integrated Mode**: Connected to the DMac server for enhanced capabilities
2. **Standalone Mode**: Works completely independently without any external dependencies

## Features

- **Chat**: Get answers about your code and codebase
- **Next Edit**: Step-by-step guidance for complex changes
- **Code Completions**: Context-aware code suggestions
- **Instructions**: Use natural language to modify code
- **Autonomous Mode**: Autonomous coding assistance for complex tasks
- **Project Indexing**: Local code indexing for better context awareness
- **Brainstorming**: Generate and organize ideas for your projects
- **Roadmap Generation**: Create project roadmaps from brainstorming sessions
- **Deep Reasoning**: Perform deep reasoning on complex problems
- **Code Verification**: Verify code syntax and style
- **Enhanced Context Awareness**: Track code edits for better context
- **Multiple Model Providers**: Support for Ollama and LM Studio

## Requirements

- Visual Studio Code 1.60.0 or higher
- For integrated mode: DMac server running on http://localhost:1302 (configurable)
- For standalone mode: Ollama or LM Studio installed locally

## Installation

1. Download the extension from the VS Code Marketplace
2. Install the extension in VS Code
3. Configure the extension settings (optional)

### For Standalone Mode

1. Install [Ollama](https://ollama.ai/) (recommended) or [LM Studio](https://lmstudio.ai/)
2. For Ollama, pull a model: `ollama pull gemma3:12b` (or another model of your choice)
3. Set `macoder.preferStandalone` to `true` in VS Code settings

## Usage

### Chat

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Start Chat`
3. Ask questions about your code or codebase

### Next Edit

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Next Edit`
3. Describe the changes you want to make
4. Follow the step-by-step guidance

### Code Completions

Code completions are automatically provided as you type. They are context-aware and understand your codebase.

### Code Generation

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Generate Code`
3. Describe the code you want to generate

### Code Explanation

1. Select the code you want to explain
2. Right-click and select `MaCoder: Explain Code` or use the Command Palette

### Code Refactoring

1. Select the code you want to refactor
2. Right-click and select `MaCoder: Refactor Code` or use the Command Palette
3. Describe how you want to refactor the code

### Switching Modes

MaCoder can operate in either integrated mode (with DMac server) or standalone mode:

1. Use the command palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Toggle Between DMac and Standalone Mode`
3. The current mode is displayed in the status bar: `MaCoder [dmac]` or `MaCoder [standalone]`

### Autonomous Mode

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Show Autonomous Mode Panel`
3. Click the Start button to activate autonomous mode
4. Enter a task description and click Execute Task
5. MaCoder will autonomously complete the task

### Project Indexing

MaCoder automatically indexes your project in standalone mode. To manually refresh the index:

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Refresh Code Index`

### Brainstorming

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Show Brainstorming Panel`
3. Create a new brainstorming session
4. Add ideas manually or generate them with AI
5. Create roadmaps from your brainstorming sessions

### Deep Reasoning

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Show Deep Reasoning Panel` or `MaCoder: Perform Deep Reasoning`
3. Enter a problem to reason about
4. MaCoder will analyze the problem from multiple angles
5. Review the observations, thoughts, actions, and conclusions

### Code Verification

1. Select the code you want to verify
2. Right-click and select `MaCoder: Verify Code` or use the Command Palette
3. MaCoder will check the code for syntax and style issues
4. Issues will be displayed in the Problems panel

### Enhanced Context Awareness

1. MaCoder automatically tracks your code edits to provide better context
2. You can manage edit sessions to organize related changes:
   - Use `MaCoder: Start New Edit Session` to start a new session
   - Use `MaCoder: End Current Edit Session` to end the current session
3. Edit sessions help MaCoder understand the context of your changes

### Sandbox Testing and Debugging

1. Open the Sandbox Panel with `MaCoder: Show Sandbox Panel`
2. Execute code directly in the sandbox or select code and use `MaCoder: Execute Code in Sandbox`
3. Create and save test cases for repeated testing
4. View execution results including output and errors

### Switching Model Providers

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Type `MaCoder: Switch Local Model Provider`
3. Select the provider you want to use (Ollama or LM Studio)

## Extension Settings

This extension contributes the following settings:

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

## Known Issues

### Integrated Mode
- Requires a running DMac server
- Some features may be limited if the DMac server is not fully configured

### Standalone Mode
- Requires a local LLM provider (Ollama or LM Studio)
- Performance depends on your local hardware
- Some advanced features may be limited compared to integrated mode

### Project Indexing
- Initial indexing may take time for large projects
- Some file types might not be properly indexed
- Memory usage increases with project size

### Autonomous Mode
- Complex tasks may not be completed successfully
- Task parsing may sometimes fail with ambiguous instructions
- Task execution might timeout for very large operations

### Brainstorming
- Generated ideas quality depends on the model used
- Roadmap generation may not capture all dependencies correctly
- Storage is local and not synchronized across devices

### Deep Reasoning
- Analysis quality depends on the model used
- Complex problems may require multiple reasoning chains
- Reasoning steps may sometimes be incomplete or imprecise

### Code Verification
- Verification quality depends on the model used
- Some language-specific issues may not be detected
- Line and column numbers may not always be accurate

### Enhanced Context Awareness
- Large edit sessions may impact performance
- Some complex refactorings may not be tracked accurately
- Edit sessions are stored locally and not synchronized across devices

### Sandbox Testing and Debugging
- Execution environment is limited to installed tools and languages
- Some languages may require additional setup
- Execution time is limited to prevent infinite loops
- Sandbox is isolated but not completely secure for malicious code

### General
- Code completions may be slow for large files
- Next Edit may not work well for complex changes

## Development Status

MaCoder is currently in alpha stage (v0.3.0-alpha) and is under active development. The extension is intended for personal local use only, not for public release, but will be enterprise-ready in the next iteration.

### Current Status

- ✅ Hybrid mode (DMac integration + standalone)
- ✅ Local project indexing
- ✅ Multiple model providers (Ollama, LM Studio)
- ✅ Autonomous mode
- ✅ Brainstorming and roadmap generation
- ✅ Deep reasoning capabilities
- ✅ Code verification
- ✅ Enhanced context awareness with code edit logging
- ✅ Sandbox testing and debugging
- ✅ Laminar integration for tracing and evaluation

### Future Roadmap

The following features are planned for future releases:

- 📅 Integration with more model providers (Gemini, OpenAI, OpenRouter, DeepSeek)
- 📅 Ability to search and pull models from Ollama repositories and Hugging Face
- 📅 Deep research and web search capabilities
- 📅 Enhanced UI/UX with better styling and error handling
- 📅 Full activity bar view implementation

## Release Notes

### 0.3.0-alpha (Upcoming)

- Added project indexing for standalone mode
- Added autonomous mode for complex tasks
- Added brainstorming and roadmap generation
- Added deep reasoning capabilities
- Added code verification for syntax and style
- Added enhanced context awareness with code edit logging
- Added sandbox testing and debugging
- Added support for LM Studio
- Added command to switch model providers

### 0.2.0

- Added standalone mode with local LLM support
- Added Laminar integration for tracing and evaluation
- Added mode switching capability
- Improved error handling and fallback mechanisms

### 0.1.0

- Initial release of MaCoder for Visual Studio Code

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This extension is licensed under the MIT License.
