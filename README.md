# DMac: a Multi-Agent AI Swarm

DMac is a modular, locally hosted AI ecosystem that coordinates a swarm of specialized agents to perform a wide range of tasks including software engineering, manufacturing automation, creative design, and more.

## Features

- **Software Engineering & "Vibe Coding"**: Code generation, real-time debugging, and iterative refinement using voice (STT) and text commands.
- **Manufacturing Automation**: 3D printing, CNC machining, and laser engraving integrated with automated packaging design.
- **Creative Design & Content Creation**: 3D modeling, video content production, and packaging visualization.
- **Interactive UI & Virtual Agents**: Real-time dashboards (SwarmUI, ComfyUI), visual workflow building (LangChain OpenCanvas), and lifelike agent interaction (Unreal Engine 5 Metahumans).
- **Home Automation & IoT** (Optional): Control of smart devices and industrial machinery as part of an integrated manufacturing process.

## Architecture

DMac is built on top of OpenManus-RL, which provides the reinforcement learning framework for agent training and coordination. The system consists of the following components:

- **Core Orchestration Layer**: Coordinates all specialized agents and manages task execution.
- **Specialized Agents**: Coding, Manufacturing, Design, UI, and IoT agents that perform specific tasks.
- **External Tool Integrations**: Voice interface, CLI interface, design tools, and manufacturing controllers.
- **User Interfaces**: SwarmUI, ComfyUI, and LangChain OpenCanvas for monitoring and control.
- **AI Models & Services**: DeepClaude framework, Gemini 2.5 pro API, and DeepSeek-RL 0.324.
- **Enhanced Learning System**: Continuous learning from all model interactions with feedback mechanisms to improve response quality over time.
- **Comprehensive Security**: Secure credential management, input validation, rate limiting, encryption, and authentication to protect the system and data.

## Installation

**Important**: DMac requires Ollama as a core dependency for managing local LLMs. DMac prioritizes using local models and only uses external services strategically when needed.

For detailed installation instructions, see [docs/installation.md](docs/installation.md).

1. Install Ollama from [ollama.com/download](https://ollama.com/download)
2. Clone the repository:
   ```
   git clone https://github.com/yourusername/dmac.git
   cd dmac
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the system:
   ```
   # Edit the configuration file
   nano config/config.yaml
   ```

4. Run the application:
   ```
   python main.py
   ```

## Usage

DMac can be used in interactive mode or with a single prompt:

```
# Interactive mode
python main.py

# Single prompt
python main.py --prompt "Generate a Python function to sort a list of integers"
```

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

## Acknowledgements

- OpenManus-RL team for the reinforcement learning framework
- All the open-source projects that made this possible
