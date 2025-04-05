# Changelog

All notable changes to the DMac project will be documented in this file.

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
