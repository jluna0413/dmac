# DMac Project Documentation

## Project Overview

DMac (Dynamic Multi-Agent Collaboration) is an AI agent swarm platform that enables multiple AI agents to collaborate on complex tasks. The system provides a unified interface for interacting with various AI models, both cloud-based and local, and includes tools for web search, deep thinking, file analysis, and more.

## System Architecture

### Core Components

1. **Dashboard Server**: Flask-based web server that provides the user interface and API endpoints
2. **Agent System**: Framework for creating and managing AI agents with different specializations
3. **Model Integration**: Connectors for various AI models (Ollama, API services like Gemini, OpenAI)
4. **Tool Integration**: Web search, file processing, deep thinking, and other capabilities
5. **Database**: SQLite database for storing conversations, user preferences, and agent data

### Key Files and Directories

- `run_server.py`: Main entry point for starting the application
- `dashboard/`: Contains the web interface and API endpoints
  - `templates/`: HTML templates for the web interface
  - `static/`: CSS, JavaScript, and other static assets
  - `routes/`: API and page routing
- `agents/`: Agent definitions and orchestration logic
- `integrations/`: Connectors for external services and models
  - `ollama_client.py`: Client for connecting to local Ollama models
  - `web_search.py`: Web search functionality
- `database/`: Database models and management

## Features

### Current Features

1. **Chat Interface**:
   - Clean, modern UI inspired by Google's Material Design
   - Support for text input, voice input, and file uploads
   - Tools for web search, deep thinking, and more
   - Hot word detection for automatically activating tools

2. **Model Management**:
   - Support for multiple model providers (API services and local models)
   - Dynamic model selection via dropdown menus
   - Model capability display showing available features

3. **Agent System**:
   - Support for specialized agents (Cody, Perry, Shelly, Flora)
   - Agent task assignment and collaboration
   - Agent memory and context management

4. **Tools and Integrations**:
   - Web search with multiple search engines
   - File upload and analysis
   - Deep thinking mode for complex problems
   - Open Canvas for visual thinking

### Planned Features

1. **Enhanced Agent Capabilities**:
   - Reinforcement learning with OpenManus-RL and DeepSeek-RL
   - Agent benchmarking and leaderboards
   - Agent-specific optimized models

2. **Advanced UI**:
   - Voice interaction throughout the interface
   - User avatar uploads
   - Mobile view simulation
   - SwarmUI and ComfyUI for visualizing agent orchestration

3. **Security and Authentication**:
   - Multi-provider authentication (Google, GitHub, Apple ID, OpenID)
   - 2-factor authentication
   - Role-based access control

4. **Developer Tools**:
   - MaCoder code assistant agent
   - Code completion functionality
   - Integration with development environments

## User Guide

### Getting Started

1. **Installation**:
   ```bash
   # Clone the repository
   git clone https://github.com/username/dmac.git
   cd dmac
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start the server
   python run_server.py
   ```

2. **Accessing the Dashboard**:
   - Open a web browser and navigate to `http://localhost:1302`
   - Default login credentials: Auto-generated for development

3. **Using the Chat Interface**:
   - Select a model from the dropdown menu
   - Type a message or use voice input
   - Upload files for analysis
   - Use tools like web search and deep thinking

### Advanced Usage

1. **Working with Agents**:
   - Use '@' command to call specific agents
   - Use '# Task' command to create tasks
   - Specify models with ':' (e.g., '# Task: gemini-pro')

2. **Using Tools**:
   - Web Search: Activated with keywords like 'search', 'look up'
   - Deep Thinking: Activated with keywords like 'think', 'ponder'
   - Deep Research: Activated with keywords like 'research', 'brain store'

3. **Model Selection**:
   - API Service Providers: Gemini, OpenAI, DeepSeek, HuggingFace, OpenRouter
   - Local Model Providers: Ollama, LM Studio

## Developer Guide

### Setting Up the Development Environment

1. **Prerequisites**:
   - Python 3.8+
   - Node.js and npm (for frontend development)
   - Ollama (for local model support)
   - Docker (optional, for containerization)

2. **Development Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/username/dmac.git
   cd dmac
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start the server in development mode
   python run_server.py --debug
   ```

3. **Code Structure**:
   - Follow the existing directory structure
   - Use PEP 8 style guide for Python code
   - Use ESLint for JavaScript code

### Adding New Features

1. **Adding a New Agent**:
   - Create a new agent class in `agents/`
   - Register the agent in `agents/__init__.py`
   - Add the agent to the UI in `dashboard/templates/agents.html`

2. **Adding a New Model Provider**:
   - Create a new client in `integrations/`
   - Add the provider to the model selection dropdown
   - Implement the necessary API endpoints

3. **Adding a New Tool**:
   - Create a new tool module in `integrations/`
   - Add the tool to the UI in `dashboard/templates/chat.html`
   - Implement the necessary API endpoints

### Testing

1. **Running Tests**:
   ```bash
   # Run all tests
   pytest
   
   # Run specific tests
   pytest tests/test_agents.py
   ```

2. **Test Coverage**:
   ```bash
   # Generate coverage report
   pytest --cov=dmac
   ```

## API Reference

### Chat API

- `POST /api/chat`: Send a message to the AI
  - Request: `{ "message": "Hello", "model": "gemini-pro", "thinking": false, "research": false }`
  - Response: `{ "response": "Hi there!", "thinking": false, "research": false }`

### Model API

- `GET /api/ollama/models`: Get available Ollama models
  - Response: `{ "models": [{"name": "llama3:8b"}, {"name": "gemma3:12b"}] }`

### Agent API

- `POST /api/agents/assign`: Assign a task to an agent
  - Request: `{ "agent": "cody", "task": "Write a function to calculate Fibonacci numbers", "model": "gemini-pro" }`
  - Response: `{ "task_id": "123", "status": "assigned" }`

## Troubleshooting

### Common Issues

1. **Server Won't Start**:
   - Check if the port is already in use
   - Verify that all dependencies are installed
   - Check the logs for error messages

2. **Models Not Loading**:
   - Verify that Ollama is running
   - Check the Ollama API endpoint configuration
   - Ensure the models are installed in Ollama

3. **UI Issues**:
   - Clear browser cache
   - Check browser console for JavaScript errors
   - Verify that all static files are being served correctly

### Getting Help

- Open an issue on GitHub
- Check the FAQ in the wiki
- Join the community Discord server

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Developed by [Your Name]
- Built with Flask, Python, JavaScript, and various open-source libraries
- Uses models from Ollama, Gemini, and other providers
