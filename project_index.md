# DMac Project Index

## Overview

DMac is a modular, locally hosted AI ecosystem that coordinates a swarm of specialized agents to perform a wide range of tasks including software engineering, manufacturing automation, and creative design. The system leverages local LLMs through Ollama and incorporates continuous learning.

## Project Structure

### Core Components

- **app.py**: Main application entry point
- **run_server.py**: Server initialization and configuration
- **main.py**: Core application logic

### Agents

The agents directory contains specialized AI agents for different tasks:

- **agents/base_agent.py**: Base class for all agents
- **agents/agent_manager.py**: Manages agent lifecycle and communication

#### Specialized Agents

- **agents/coding/**: Code generation and software development agents
- **agents/design/**: UI/UX and creative design agents
- **agents/flora/**: Frontend development agent
- **agents/iot/**: Internet of Things integration agents
- **agents/macoder/**: Native code assistant agent
- **agents/manufacturing/**: Manufacturing automation agents
- **agents/mccoder/**: Microcontroller code generation agent
- **agents/perry/**: Project management agent
- **agents/qa/**: Quality assurance and testing agent
- **agents/researcher/**: Deep research agent
- **agents/shelly/**: User interaction agent
- **agents/ui/**: User interface agent
- **agents/writer/**: Content creation agent

### Dashboard

The dashboard provides a web-based interface for interacting with the system:

- **dashboard/dashboard_server.py**: Main dashboard server
- **dashboard/templates/**: HTML templates for the web interface
- **dashboard/static/**: Static assets (CSS, JavaScript, images)

#### Key Templates

- **dashboard/templates/base.html**: Base template for all pages
- **dashboard/templates/chat.html**: Chat interface
- **dashboard/templates/dashboard.html**: Main dashboard
- **dashboard/templates/models.html**: Model management
- **dashboard/templates/tasks.html**: Task management
- **dashboard/templates/webarena.html**: WebArena integration

#### Static Assets

- **dashboard/static/css/**: Stylesheets
- **dashboard/static/js/**: JavaScript files
- **dashboard/static/img/**: Images and icons
- **dashboard/static/js/unified-input.js**: Main chat interface logic

### Integrations

The integrations directory contains connectors to external services and tools:

- **integrations/ollama_client.py**: Client for Ollama LLM service
- **integrations/voice_interaction.py**: Voice input/output functionality
- **integrations/webarena_client.py**: Client for WebArena benchmarking
- **integrations/web_scraper.py**: Web scraping functionality
- **integrations/web_search.py**: Web search functionality
- **integrations/web_search_api.py**: API for web search

### Database

The database directory contains database management code:

- **database/db_manager.py**: Database initialization and management
- **database/models.py**: Database models

### Security

The security directory contains authentication and authorization code:

- **security/auth_manager.py**: Authentication management
- **security/encryption.py**: Encryption utilities

### Learning System

The learning system directory contains code for continuous learning:

- **learning/learning_manager.py**: Learning system management
- **learning/reinforcement_learning.py**: Reinforcement learning implementation

### WebArena

The WebArena directory contains code for benchmarking and evaluation:

- **webarena/webarena_manager.py**: WebArena integration management
- **webarena/visualization.py**: Visualization tools for WebArena results

### Utils

The utils directory contains utility functions and helpers:

- **utils/hot_reload.py**: Hot reload functionality for development
- **utils/secure_logging.py**: Secure logging utilities

### Documentation

The docs directory contains project documentation:

- **docs/architecture.md**: System architecture documentation
- **docs/hot_words.md**: Hot word functionality documentation
- **docs/installation.md**: Installation instructions
- **docs/learning_system.md**: Learning system documentation
- **docs/security_system.md**: Security system documentation
- **docs/web_search.md**: Web search functionality documentation

## Key Features

1. **Multi-Agent System**: Coordinated agents for specialized tasks
2. **Local LLM Integration**: Ollama integration for local model execution
3. **Web Search**: Real-time information retrieval from the web
4. **Hot Word Detection**: Natural language triggers for different modes
5. **WebArena Integration**: Benchmarking and evaluation tools
6. **Learning System**: Continuous improvement through reinforcement learning
7. **Security**: Authentication and authorization system
8. **Dashboard**: Web-based interface for system interaction

## Development Status

The project is currently in active development with the following components implemented:

- Basic application framework
- Dashboard server with authentication
- Web search functionality with multiple engines
- Hot word detection for natural language triggers
- Ollama integration for local LLM execution

The following components are planned for future development:

- Specialized agent implementation
- Agent orchestration layer
- Learning system implementation
- Manufacturing automation integration
- Creative design tools integration
- Voice interface implementation
- Workflow visualization tools

## Getting Started

To run the project:

1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python run_server.py`
3. Access the dashboard: http://localhost:1302

## Next Steps

Based on the project plan, the next steps are:

1. Implement the core agent framework
2. Develop specialized agents (Cody, Perry, Shelly, Flora)
3. Implement the agent orchestration layer
4. Develop the learning system
5. Enhance the user interface
6. Implement voice interface
7. Integrate manufacturing and design tools
