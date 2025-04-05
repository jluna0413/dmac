# DMac: a Multi-Agent AI Swarm

DMac is a modular, locally hosted AI ecosystem that coordinates a swarm of specialized agents to perform a wide range of tasks including software engineering, manufacturing automation, creative design, and more.

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow)
![Python](https://img.shields.io/badge/Python-3.9+-blue)

## Features

- **Software Engineering & "Vibe Coding"**: Code generation, real-time debugging, and iterative refinement using voice (STT) and text commands.
- **Manufacturing Automation**: 3D printing, CNC machining, and laser engraving integrated with automated packaging design.
- **Creative Design & Content Creation**: 3D modeling, video content production, and packaging visualization.
- **Interactive UI & Virtual Agents**: Real-time dashboards (SwarmUI, ComfyUI), visual workflow building (LangChain OpenCanvas), and lifelike agent interaction (Unreal Engine 5 Metahumans).
- **WebArena Integration**: Evaluate your agents in the WebArena environment, a benchmark for web agents with comprehensive open-source visualization and analysis tools.
- **Real-time Web Search**: Chat interface with web scraping capabilities to retrieve up-to-date information from the internet using DuckDuckGo.
- **Home Automation & IoT** (Optional): Control of smart devices and industrial machinery as part of an integrated manufacturing process.

## Architecture

DMac is built on top of OpenManus-RL, which provides the reinforcement learning framework for agent training and coordination. The system consists of the following components:

- **Core Orchestration Layer**: Coordinates all specialized agents and manages task execution.
- **Specialized Agents**: Coding, Manufacturing, Design, UI, WebArena, and IoT agents that perform specific tasks.
- **External Tool Integrations**: Voice interface, CLI interface, design tools, WebArena benchmark, and manufacturing controllers.
- **User Interfaces**: SwarmUI, ComfyUI, WebArena Dashboard, and LangChain OpenCanvas for monitoring and control.
- **AI Models & Services**: DeepClaude framework, Gemini 2.5 pro API, Ollama models, and DeepSeek-RL 0.324.
- **Enhanced Learning System**: Continuous learning from all model interactions with feedback mechanisms to improve response quality over time.
- **Comprehensive Security**: Secure credential management, input validation, rate limiting, encryption, and authentication to protect the system and data.
- **WebArena Integration**: Benchmark environment for evaluating web agents with open-source visualization and analysis tools using Streamlit.

## Installation

**Important**: DMac requires Ollama as a core dependency for managing local LLMs. DMac prioritizes using local models and only uses external services strategically when needed.

For detailed installation instructions, see [docs/installation.md](docs/installation.md).

### Backend Installation

1. Install Ollama from [ollama.com/download](https://ollama.com/download)
2. Clone the repository:
   ```
   git clone https://github.com/yourusername/dmac.git
   cd dmac
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure the system:
   ```
   # Edit the configuration file
   nano config/config.yaml
   ```

5. Run the backend application:
   ```
   python main.py
   ```

### Web UI Installation

The web UI is built into the Python backend and doesn't require separate installation. It's automatically served when you run the backend application.

## Usage

### Backend Usage

DMac can be used in interactive mode or with a single prompt:

```
# Interactive mode
python main.py

# Single prompt
python main.py --prompt "Generate a Python function to sort a list of integers"
```

### Web UI Usage

The web UI provides a modern Material Design interface for interacting with the DMac system:

1. **Login**: Use the provided test accounts or auto-generate a login for testing
   - Admin: admin@dmac.ai (any password works for testing)
   - User: user@dmac.ai (any password works for testing)
   - Developer: dev@dmac.ai (any password works for testing)

2. **Dashboard**: Access the main dashboard with tabs for Agents, Tasks, Models, and Analytics

3. **Chat**: Interact with the AI agent swarm through the chat interface
   - Use the Research button to enable web search for real-time information
   - Ask questions about current events, latest versions, or any topic requiring up-to-date information
   - See visual indicators when web search is being used

4. **WebArena**: Run experiments and evaluate models in the WebArena environment

### WebArena Integration

The WebArena integration allows you to evaluate your agents in the WebArena environment using open-source visualization tools:

```
# Start the DMac application with the dashboard
python run_server.py

# Or use the batch script
run_dmac_server.bat

# Access the WebArena dashboard at
http://localhost:1302/webarena/dashboard
```

From the WebArena dashboard, you can:

- Create and manage WebArena agents
- Run experiments with different models and tasks
- View the results of experiments
- Generate visualizations and analyze performance using Streamlit
- Compare different models including Ollama models like Gemma3:12b

## Configuration

DMac can be configured by editing the `config/config.yaml` file. The configuration includes settings for:

- Orchestration parameters
- Agent settings
- Model configurations
- Integration settings
- UI configurations

## Learning System

DMac features an enhanced learning system that allows the AI models to improve over time:

- **Continuous Learning**: The system learns from all interactions with all models, not just Gemini 2.5 Pro.
- **Feedback Mechanism**: Users can provide feedback on responses, which is used to improve future responses.
- **Training Process**: DeepSeek-RL is periodically trained on the collected learning data to improve its capabilities.
- **Model Evaluation**: The system regularly evaluates model performance to track improvements.
- **Adaptive Switching**: The system intelligently switches between models based on usage caps and performance metrics.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Recent Updates

### Version 1.2.0 (April 5, 2025)
- Added web search functionality to the chat interface
- Implemented real-time information retrieval using web scraping
- Added automatic detection of queries that need current information
- Integrated with DuckDuckGo for privacy-friendly searches
- Improved authentication system with auto-generated logins for development
- Enhanced error handling in the chat interface

### Version 1.1.0 (July 10, 2024)
- Added modern UI with Google Material Design
- Implemented consistent brand identity with DMac logo
- Added light/dark mode toggle for better user experience
- Enhanced task creation with file upload support
- Integrated Streamlit for WebArena visualization
- Replaced Zeno with open-source visualization tools

### Version 0.2.0
- Added Flutter app for improved UI/UX
- Implemented user authentication system
- Added dashboard with Agents, Tasks, Models, and Analytics views
- Integrated WebArena experiments and visualization
- Added reinforcement learning with OpenManus-RL and DeepSeek-RL
- Integrated Langchain and Open Deep Research
- Improved security and user management

## Acknowledgements

- OpenManus-RL team for the reinforcement learning framework
- All the open-source projects that made this possible
