# Change Log

All notable changes to the "MaCoder" extension will be documented in this file.

## [0.3.0-alpha] - 2025-01-15

### Added
- Local project indexing system for standalone mode
  - Automatic workspace scanning and indexing
  - File watching to keep index up-to-date
  - Command to manually refresh the index
  - Search functionality using the local index
- Multiple model providers support
  - Added LM Studio as an alternative to Ollama
  - Command to switch between providers
  - Configuration options for different providers
- Autonomous mode
  - Task-based autonomous coding assistance
  - UI panel for managing autonomous tasks
  - Task parsing and execution system
  - Subtask management and tracking
- Brainstorming and roadmap generation
  - Brainstorming sessions for organizing ideas
  - AI-powered idea generation
  - Roadmap creation from brainstorming sessions
  - Task dependency tracking and status management
- Deep reasoning capabilities
  - Problem analysis from multiple angles
  - Structured reasoning with observations, thoughts, actions, and conclusions
  - AI-powered reasoning chain generation
  - Manual and automatic reasoning modes
- Code verification
  - Syntax verification for multiple languages
  - Style verification for coding standards
  - Integration with VS Code's Problems panel
  - Support for selected code or entire files
- Enhanced context awareness
  - Code edit logging for better context
  - Edit session management
  - Automatic tracking of code changes
  - Integration with the API client for improved suggestions
- Sandbox testing and debugging
  - Code execution in isolated environment
  - Support for multiple programming languages
  - Test case creation and management
  - Execution result analysis with output and error reporting

### Changed
- Updated documentation to reflect new features
- Improved error handling for all new features
- Enhanced standalone mode capabilities

### Fixed
- Various stability issues in standalone mode
- Edge cases in the hybrid API client

## [0.2.0] - 2025-01-01

### Added
- Standalone mode with local LLM support
- Laminar integration for tracing and evaluation
- Mode switching capability
- Improved error handling and fallback mechanisms

## [0.1.0] - 2024-12-15

### Added
- Initial release of MaCoder for Visual Studio Code
- Basic chat functionality
- Next edit guidance
- Code completions
- Instructions for code modification
