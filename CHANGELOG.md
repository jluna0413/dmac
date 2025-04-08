# Changelog

All notable changes to the DMac project will be documented in this file.

## [1.4.0] - 2025-04-09

### Added
- **Cody Agent**: Implemented native code assistant with DeepClaude integration
  - Added code generation, completion, and explanation capabilities
  - Implemented code refactoring and bug finding
  - Added reinforcement learning integration with OpenManus RL
  - Implemented vision capabilities for code understanding

- **DeepClaude Integration**: Implemented hybrid approach combining DeepSeek R1 and Claude 3.7
  - Created flexible DeepClaude module for use by any agent
  - Implemented reasoning extraction and refinement
  - Added caching for improved performance
  - Created comprehensive documentation

- **Agent Dashboard**: Created detailed dashboard for agent monitoring and interaction
  - Implemented live agent data display
  - Added benchmark visualization with model comparison
  - Created performance metrics visualization
  - Implemented multi-modal chat interface (text, voice, file, canvas)
  - Added agent configuration interface

### Changed
- **Agent System**: Updated agent factory to include Cody
- **API Layer**: Added new API endpoints for Cody and agent dashboards
- **Model Manager**: Enhanced to support the DeepClaude approach
- **UI**: Updated agents page to link to agent dashboards

### Fixed
- Improved model integration with better error handling
- Enhanced agent configuration with more detailed options
- Fixed styling issues in the agent interface

## [1.3.0] - 2025-04-08

### Added
- **MaCoder**: Implemented native code assistant with code completion functionality
  - Added code indexing and analysis
  - Implemented code generation, completion, and explanation
  - Added refactoring, bug finding, and test generation
  - Implemented project analysis and benchmarking
  - Created VS Code extension for MaCoder
  - Added API endpoints for all MaCoder functionality

- **LangChain Integration**: Replaced WebArena with LangChain for agent evaluation and benchmarking
  - Implemented agent evaluation framework
  - Added benchmarking capabilities
  - Created visualization tools for evaluation results

- **Documentation**: Enhanced project documentation
  - Updated wiki with MaCoder and LangChain information
  - Created comprehensive MaCoder documentation
  - Added detailed implementation roadmap
  - Updated agent documentation

### Changed
- **Agent System**: Updated agent factory to include MaCoder
- **API Layer**: Modified API routes to include MaCoder endpoints
- **Configuration**: Enhanced agent configuration with MaCoder settings
- **Documentation**: Replaced WebArena references with LangChain

### Removed
- **WebArena Integration**: Removed WebArena due to lack of active development and compatibility issues
  - Removed WebArena API endpoints
  - Removed WebArena agent
  - Removed WebArena configuration
  - Removed WebArena documentation

### Fixed
- Resolved issues with Python symbol extraction
- Fixed code completion caching
- Addressed performance issues with large codebases

## [1.2.3] - 2025-04-06

### Added
- Comprehensive project documentation
- Detailed developer roadmap
- Model provider dropdown menu in chat interface
- Model capabilities display in right sidebar
- Tool buttons above chat input
- Labeled pills for tools instead of icon buttons
- Current model display in sidebar

### Changed
- Redesigned chat interface with three-column layout
- Improved chat input area to be more compact and streamlined
- Moved tools from right sidebar to above chat input
- Repurposed right sidebar to display model information
- Enhanced model details display with more accurate information
- Updated styling to match Google's Material Design

### Fixed
- Chat input no longer floats over content
- Input container properly positioned at bottom of chat area
- Improved responsive design for different screen sizes
- Added proper dark mode support

## [1.2.2] - 2025-04-05

### Added
- Hot word detection for automatic mode activation
  - Web search hot words (search, look up, find, etc.)
  - Deep thinking hot words (think, ponder, analyze, etc.)
  - Deep research hot words (research, brainstorm, investigate, etc.)
- Toast notifications for mode activation
- Visual indicators for active modes

## [1.2.1] - 2025-04-05

### Added
- Enhanced web search functionality for the chat interface
  - Multiple search engine support (DuckDuckGo and Google)
  - Search result caching for improved performance
  - Source attribution with direct links to original content
  - Enhanced query detection for better automatic searching
  - Clear cache functionality for refreshing search results

## [1.2.0] - 2025-04-05

### Added
- Web search functionality for the chat interface
  - Real-time information retrieval using web scraping
  - Automatic detection of queries that need current information
  - Integration with DuckDuckGo for privacy-friendly searches
  - Visual indicators for when web search is being used
- Enhanced chat API with web search capabilities
- Research button in chat interface to explicitly enable web search

### Changed
- Updated server to run on port 1302 for network accessibility
- Improved authentication system with auto-generated logins for development
- Enhanced error handling in the chat interface

### Fixed
- Fixed login issues with development accounts
- Improved error handling for Ollama model integration

## [1.1.0] - 2024-07-10

### Added
- Modern UI with Google Material Design
- Consistent brand identity with DMac logo
- Light/dark mode toggle for better user experience
- Enhanced task creation with file upload support (documents, code, media)
- Streamlit integration for WebArena visualization
- Comprehensive settings page with configuration options

### Changed
- Replaced Zeno with open-source visualization tools
- Updated WebArena dashboard to use Streamlit
- Improved models page to display dynamic data from Ollama
- Enhanced error handling throughout the application
- Updated model names to match exact Ollama versions
- Improved task creation interface with Material Design

### Removed
- All references to Zeno from the project
- Placeholder data in favor of dynamic data
- Redundant code and dependencies

### Fixed
- Task creation modal UI issues
- Model loading in WebArena dashboard
- VS Code type checking errors
- Navigation issues in the dashboard
- 404 errors when accessing certain pages

## [1.0.0] - 2024-06-15

### Added
- Initial release of DMac
- Core orchestration layer
- Specialized agents (Coding, Manufacturing, Design, UI, WebArena)
- External tool integrations
- User interfaces (SwarmUI, ComfyUI, WebArena Dashboard)
- AI models & services integration
- Enhanced learning system
- Comprehensive security measures
- WebArena integration
