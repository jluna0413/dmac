# AI Agents

DMac features a swarm of specialized AI agents, each designed to excel at specific tasks. This guide will introduce you to the main agents and explain how to work with them effectively.

## Overview of DMac Agents

DMac's agent system is built around the concept of specialized expertise. Rather than having a single AI try to handle all tasks, DMac distributes work among specialized agents that excel in their domains.

### Core Agents

DMac includes several core agents that handle common tasks:

1. **MaCoder** - Native Code Assistant (VS Code Extension)
2. **Cody** - Native Code Assistant (Local)
3. **Perry** - Project Manager
4. **Shelly** - Shell Command Expert
5. **Flora** - Documentation Specialist

Let's explore each agent in detail.

## MaCoder - Native Code Assistant

![MaCoder](../assets/macoder-architecture.svg)

MaCoder is a native code assistant with code completion functionality, inspired by Augment Code but running on models within the DMac ecosystem without external dependencies.

### Capabilities

- **Code Understanding**: Real-time indexing and analysis of your codebase
- **Code Generation**: Create new code based on natural language descriptions
- **Code Completion**: Context-aware suggestions as you type
- **Code Explanation**: Get detailed explanations of existing code
- **Code Refactoring**: Improve code quality with AI-guided refactoring
- **Bug Finding**: Identify potential issues in your code
- **Test Generation**: Automatically create tests for your code
- **Project Analysis**: Get insights into your codebase structure
- **Model Benchmarking**: Compare performance across different models

### How to Use MaCoder

You can interact with MaCoder in several ways:

1. **VS Code Extension**: Use the MaCoder VS Code extension for the best experience
   ```
   Install the MaCoder VS Code extension and access all features directly in your editor
   ```

2. **Direct Addressing**: Use "@MaCoder" at the beginning of your message
   ```
   @MaCoder Please help me understand this code snippet
   ```

3. **Code-Related Keywords**: MaCoder automatically responds to messages about code understanding, generation, and improvement
   ```
   Can you explain how this algorithm works?
   ```

### Best Practices

- Use the VS Code extension for the best experience
- Provide context about your project and requirements
- Be specific about what you want to achieve
- For complex changes, use the Next Edit feature for step-by-step guidance

## Cody - Native Code Assistant

![Cody](../assets/cody-avatar.png)

Cody is a native code assistant with code completion, vision capabilities, and reinforcement learning integration. Unlike MaCoder, Cody operates locally within the DMac ecosystem, listening for tasks from the main orchestrating agent powered by OpenManus RL.

### Capabilities

- **Code Generation**: Create new code based on natural language descriptions
- **Code Completion**: Context-aware suggestions as you type
- **Code Explanation**: Get detailed explanations of existing code
- **Code Refactoring**: Improve code quality with AI-guided refactoring
- **Bug Finding**: Identify potential issues in your code
- **Test Generation**: Automatically create tests for your code
- **Project Analysis**: Get insights into your codebase structure
- **Vision Code Understanding**: Analyze code from images or screenshots
- **Reinforcement Learning**: Learn from experience to improve over time

### DeepClaude Integration

Cody uses the DeepClaude approach, which combines DeepSeek R1 for reasoning with Claude 3.7 Sonnet for generation. This hybrid approach works by:

1. Using DeepSeek R1 to generate reasoning about a coding problem
2. Extracting this reasoning and passing it to Claude 3.7 Sonnet
3. Using Claude 3.7 Sonnet to generate the final code based on the reasoning

This approach leverages the strengths of both models to produce higher-quality code with better explanations.

### How to Use Cody

You can interact with Cody in several ways:

1. **Direct Addressing**: Use "@Cody" at the beginning of your message
   ```
   @Cody Please help me write a Python function to parse JSON data
   ```

2. **Code-Related Keywords**: Cody automatically responds to messages containing code-related terms
   ```
   Can you explain how this algorithm works?
   ```

3. **Code Blocks**: Share code by using triple backticks in the chat
   ```
   ```python
   def my_function():
       # This function needs explanation
       return json.loads(data)
   ```
   ```

4. **Image Upload**: Share screenshots of code for analysis
   ```
   @Cody What does this code do? [image attachment]
   ```

### Agent Dashboard

Cody has a dedicated dashboard that provides:

- Live agent data and status
- Benchmark comparisons across different models
- Performance metrics and task completion status
- Multi-modal chat interface (text, voice, file, canvas)
- Agent configuration options

To access the dashboard, click the "Details" button on Cody's agent card on the Agents page.

### Best Practices

- Be specific about programming languages and frameworks
- Provide context about your project when asking for help
- Share relevant code snippets to get more accurate assistance
- Use the vision capabilities for complex code screenshots
- Take advantage of the multi-modal chat interface for different input methods

## Perry - Project Manager

![Perry](../assets/perry-avatar.png)

Perry specializes in project management, prompt engineering, and task coordination.

### Capabilities

- **Prompt Creation**: Design effective prompts for AI models
- **Prompt Optimization**: Refine prompts for better results
- **Prompt Analysis**: Analyze why certain prompts work better than others
- **Prompt Benchmarking**: Test and compare different prompts
- **Chain of Thought Design**: Create step-by-step reasoning processes

### How to Use Perry

1. **Direct Addressing**: Use "@Perry" at the beginning of your message
   ```
   @Perry I need help creating a prompt for generating product descriptions
   ```

2. **Project Management Keywords**: Perry responds to messages about planning, organization, and management
   ```
   Can you help me break down this project into manageable tasks?
   ```

3. **Prompt Engineering Requests**: Ask for help with creating or improving prompts
   ```
   How can I improve this prompt to get more creative responses?
   ```

### Best Practices

- Clearly define your goals when asking for prompt assistance
- Provide examples of desired outputs when possible
- Share context about your target audience or use case
- Be specific about the tone, style, or format you want

## Shelly - Shell Command Expert

![Shelly](../assets/shelly-avatar.png)

Shelly specializes in command-line interfaces, shell scripting, and system operations.

### Capabilities

- **Command Generation**: Create shell commands for specific tasks
- **Script Creation**: Write shell scripts for automation
- **Command Explanation**: Explain what commands do and how they work
- **System Diagnostics**: Help diagnose system issues
- **File Operations**: Assist with file management tasks
- **Process Management**: Help with managing system processes
- **Text Processing**: Create commands for text manipulation
- **System Monitoring**: Assist with monitoring system resources

### How to Use Shelly

1. **Direct Addressing**: Use "@Shelly" at the beginning of your message
   ```
   @Shelly How do I find all files modified in the last 24 hours?
   ```

2. **Command-Related Keywords**: Shelly responds to messages about commands, terminals, or shells
   ```
   What's the command to compress a directory in Linux?
   ```

3. **Script Requests**: Ask for help with shell scripts
   ```
   Can you write a bash script to backup my project files daily?
   ```

### Best Practices

- Specify your operating system (Windows, macOS, Linux)
- Mention which shell you're using (Bash, PowerShell, Zsh, etc.)
- Provide context about your environment when relevant
- Be clear about security or permission requirements

## Flora - Documentation Specialist

![Flora](../assets/flora-avatar.png)

Flora specializes in documentation, UI design, and content creation.

### Capabilities

- **Component Creation**: Design UI components
- **UI Design**: Create user interface layouts
- **CSS Styling**: Write CSS for styling web applications
- **Responsive Design**: Create designs that work on different screen sizes
- **Accessibility Review**: Ensure designs are accessible
- **Animation Creation**: Design UI animations
- **Design System Implementation**: Implement consistent design systems
- **UI Prototyping**: Create interactive prototypes

### How to Use Flora

1. **Direct Addressing**: Use "@Flora" at the beginning of your message
   ```
   @Flora Can you help me design a navigation menu for my web app?
   ```

2. **Documentation Keywords**: Flora responds to messages about documentation, design, or content
   ```
   How should I structure the documentation for my API?
   ```

3. **Design Requests**: Ask for help with UI/UX design
   ```
   What's the best way to design a form for mobile users?
   ```

### Best Practices

- Provide visual references or examples when possible
- Specify target platforms or devices
- Mention any brand guidelines or design constraints
- Be clear about the purpose and audience of the documentation or design

## Other Specialized Agents

DMac includes several other specialized agents for specific tasks:

- **UI Agent**: Handles interactive UI and virtual agent tasks
- **IoT Agent**: Manages Internet of Things integrations
- **LangChain Agent**: Interacts with the LangChain evaluation framework
- **Research Agent**: Conducts deep research on complex topics
- **Benchmark Agent**: Runs performance comparisons between different models

These agents can be accessed in the same way as the core agents, by using the "@" symbol followed by the agent name.

## Agent Collaboration

One of DMac's key features is the ability for agents to collaborate on complex tasks. When you present a problem that requires multiple areas of expertise, DMac will automatically coordinate the appropriate agents to work together.

For example, if you ask for help building a web application, Codey might handle the code generation, Flora could design the UI, and Perry might help with project planning.

To initiate collaboration, simply describe your complex task in the chat, and DMac will handle the coordination behind the scenes.

## Next Steps

Now that you're familiar with DMac's AI agents, you can:

- Learn more about [MaCoder](MaCoder.md) and its capabilities
- Explore the available [Tools and Features](Tools-and-Features.md)
- Learn about [Model Management](Model-Management.md)
- Discover [Advanced Usage](Advanced-Usage.md) techniques
