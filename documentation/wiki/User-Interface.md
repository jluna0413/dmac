# DMac User Interface

DMac provides a modern, intuitive user interface that makes it easy to interact with AI agents and access various features. This guide will walk you through the main components of the DMac user interface.

## Dashboard

The Dashboard is the main landing page of DMac, providing an overview of the system status and quick access to key features.

![Dashboard](../assets/dashboard.png)

### Dashboard Components

1. **Navigation Menu**: Located on the left side of the screen, this menu allows you to navigate between different sections of DMac.

2. **Active Agents**: Displays the currently active AI agents, their status, and recent activities.

3. **Recent Tasks**: Shows recently completed or ongoing tasks, with status indicators and completion times.

4. **Model Status**: Provides information about available AI models, including their status and capabilities.

5. **Quick Actions**: Offers shortcuts to common actions like creating a new task, managing agents, or accessing settings.

## Chat Interface

The Chat Interface is where you'll spend most of your time interacting with DMac's AI agents.

![Chat Interface](../assets/chat-interface.png)

### Chat Components

1. **Message History**: Displays the conversation history between you and the AI agents.

2. **Input Field**: Located at the bottom of the screen, this is where you type your messages.

3. **Tool Buttons**: Located above the input field, these buttons allow you to activate specific tools:
   - **Web Search**: Activates web search functionality to retrieve up-to-date information
   - **Deep Thinking**: Enables the AI to think more deeply about complex problems
   - **Open Canvas**: Opens the visual thinking canvas for complex problem-solving

4. **Voice Input**: Click the microphone icon to use voice input instead of typing.

5. **File Upload**: Allows you to upload files for analysis or processing.

6. **Model Selector**: Dropdown menu to select which AI model to use for the conversation.

### Using the Chat Interface

1. **Basic Interaction**: Simply type your message in the input field and press Enter or click the Send button.

2. **Activating Tools**:
   - Click the tool buttons above the input field
   - Use hot words in your message (e.g., "search for...", "think about...", "research...")

3. **Addressing Specific Agents**:
   - Use the @ symbol followed by the agent name (e.g., "@Cody help me debug this code")
   - The system will automatically route your request to the appropriate agent

4. **File Analysis**:
   - Click the file upload button to upload files
   - The AI will analyze the content and respond accordingly

## Agent Management

The Agent Management interface allows you to view and manage the specialized AI agents in DMac.

![Agent Management](../assets/agent-management.png)

### Agent Management Components

1. **Agent List**: Displays all available agents with their status and capabilities.

2. **Agent Cards**: Visual cards for each agent showing:
   - Agent avatar and name
   - Specialty and description
   - Quick action buttons for chat and details

3. **Agent Controls**: Allows you to:
   - Activate/deactivate agents
   - Configure agent settings
   - View agent logs

## Agent Dashboard

Each agent has a dedicated dashboard that provides detailed information and interaction capabilities.

![Agent Dashboard](../assets/agent-dashboard.png)

### Agent Dashboard Components

1. **Agent Info Section**: Displays detailed information about the agent:
   - Name and description
   - Status and capabilities
   - Performance metrics (tasks completed, success rate, response time)

2. **Benchmarks Tab**: Shows how the agent performs with different models:
   - Model comparison chart (radar chart)
   - Benchmark results table
   - Performance metrics across different tasks

3. **Performance Tab**: Provides detailed metrics about the agent's performance:
   - Task completion status (completed, in progress, failed, pending)
   - Task categories distribution
   - Response time trend
   - Success rate trend

4. **Tasks Tab**: Lists recent tasks performed by the agent:
   - Task ID and type
   - Status and completion time
   - Duration and results

5. **Settings Tab**: Allows you to configure the agent:
   - Model selection
   - Temperature and other generation parameters
   - Vision and RL capabilities
   - Other agent-specific settings

6. **Multi-Modal Chat Interface**: Allows direct interaction with the agent:
   - Text input
   - Voice input
   - File upload
   - Canvas interaction

### Accessing the Agent Dashboard

To access an agent's dashboard:

1. Navigate to the Agents page
2. Find the agent card for the desired agent
3. Click the "Details" button on the agent card

Alternatively, you can access the dashboard directly via the URL: `/agent/<agent_id>`

## Settings

The Settings interface allows you to customize DMac according to your preferences.

![Settings](../assets/settings.png)

### Settings Components

1. **General Settings**: Basic configuration options like theme, language, and notification preferences.

2. **Model Settings**: Configure AI model preferences, including:
   - Default model selection
   - Temperature and other generation parameters
   - API keys for external services

3. **Agent Settings**: Configure agent-specific settings.

4. **LangChain Settings**: Configure the LangChain agent evaluation framework.

5. **Advanced Settings**: Advanced configuration options for power users.

## LangChain Evaluation Dashboard

The LangChain Evaluation Dashboard provides access to the LangChain agent evaluation framework, where you can benchmark and evaluate your agents.

![LangChain Dashboard](../assets/langchain-dashboard.png)

### LangChain Dashboard Components

1. **Evaluation Controls**: Create and run new agent evaluations.

2. **Results Viewer**: View the results of previous evaluations.

3. **Leaderboard**: Compare the performance of different agents and models.

4. **Visualization Tools**: Visualize evaluation results and agent performance.

## Navigation Tips

- **Keyboard Shortcuts**: DMac supports various keyboard shortcuts for quick navigation and actions. Press `?` to view the available shortcuts.

- **Search**: Use the search bar at the top of the screen to quickly find specific content or features.

- **Context Menus**: Right-click on various elements to access context-specific actions.

- **Responsive Design**: DMac's interface is responsive and works well on different screen sizes, from desktop to tablet.

## Next Steps

Now that you're familiar with the DMac user interface, you can:

- Learn about the specialized [AI Agents](AI-Agents.md)
- Explore the available [Tools and Features](Tools-and-Features.md)
- Discover how to use the [LangChain Integration](LangChain-Integration.md)
