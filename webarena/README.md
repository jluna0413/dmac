# WebArena Integration for DMac

This module provides integration with WebArena for agent evaluation.

## Overview

WebArena is a benchmark for evaluating web agents. It provides a standardized environment for testing and comparing the performance of different AI agents on web-based tasks.

The DMac WebArena integration allows you to:

1. Run experiments with different models and tasks
2. Visualize and analyze the results
3. Compare the performance of different models
4. Track progress over time

## Components

The WebArena integration consists of the following components:

- **WebArena Manager**: Manages WebArena experiments and runs
- **Ollama Integration**: Integrates WebArena with Ollama models
- **Open-Source Visualization**: Provides completely free and open-source visualization utilities for WebArena results
- **WebArena Agent**: An agent that can interact with WebArena
- **API**: Provides API endpoints for WebArena integration
- **Dashboard**: Provides a web interface for WebArena integration

## Usage

### Dashboard

The WebArena dashboard provides a user-friendly interface for managing and monitoring WebArena experiments. You can access it at:

```
http://localhost:8080/webarena/dashboard
```

From the dashboard, you can:

- Create and manage WebArena agents
- Run experiments with different models and tasks
- View the results of experiments
- Generate visualizations

### API

The WebArena API provides programmatic access to WebArena functionality. The main endpoints are:

- `/api/webarena/tasks`: List available tasks
- `/api/webarena/models`: List available models
- `/api/webarena/runs`: Run experiments and list runs
- `/api/webarena/runs/{run_id}`: Get run status and results
- `/api/agents/webarena`: Create and manage WebArena agents

### Open-Source Visualization

The WebArena integration includes completely free and open-source visualization tools that don't rely on any proprietary services. These tools use standard Python libraries like matplotlib, pandas, and plotly to create visualizations.

The visualization tools provide:

- **Success Rate Visualization**: Compare success rates across different models and tasks
- **Steps Distribution**: Analyze the distribution of steps taken by different models
- **Action Counts**: Compare the number of clicks, types, and other actions across models
- **Model Comparison**: Compare different models on the same task
- **Interactive Dashboards**: Create interactive dashboards with multiple visualizations

All visualizations can be generated through the dashboard or programmatically using the Python API.

### Agent

The WebArena agent provides a high-level interface for interacting with WebArena. You can use it to:

- Run experiments
- Get run status and results
- Generate visualizations

## Installation

To use the WebArena integration, you need to have WebArena installed. You can install it by following the instructions in the [WebArena repository](https://github.com/web-arena-x/webarena).

Once WebArena is installed, you need to configure the DMac WebArena integration by setting the following configuration options:

```json
{
  "webarena": {
    "enabled": true,
    "dir": "path/to/webarena",
    "data_dir": "data/webarena",
    "max_concurrent_runs": 2,
    "default_timeout": 3600,
    "ollama": {
      "enabled": true,
      "default_system_prompt": "You are a helpful AI assistant that controls a web browser..."
    },
    "visualization": {
      "enabled": true,
      "open_source": true,
      "tools": ["matplotlib", "pandas", "plotly"],
      "output_dir": "visualizations"
    }
  }
}
```

## Examples

### Running an Experiment

```python
from webarena.webarena_manager import webarena_manager

# Run an experiment
run_id, run_info = await webarena_manager.run_experiment(
    task_name="shopping",
    model_name="llama2",
    num_episodes=1,
    timeout=3600
)

# Get the run status
run_status = await webarena_manager.get_run_status(run_id)

# Get the run results
results = await webarena_manager.get_run_results(run_id)
```

### Using the WebArena Agent

```python
from agents.agent_manager import agent_manager

# Create a WebArena agent
agent = await agent_manager.create_agent(agent_type="webarena", name="My WebArena Agent")

# Run an experiment
response = await agent_manager.send_message(agent.agent_id, {
    "type": "run_experiment",
    "task_name": "shopping",
    "model_name": "llama2",
    "num_episodes": 1,
    "timeout": 3600
})

# Get the run status
response = await agent_manager.send_message(agent.agent_id, {
    "type": "get_run_status",
    "run_id": response["run_id"]
})

# Get the run results
response = await agent_manager.send_message(agent.agent_id, {
    "type": "get_run_results",
    "run_id": response["run_id"]
})
```

## Troubleshooting

If you encounter issues with the WebArena integration, check the following:

1. Make sure WebArena is installed and configured correctly
2. Check that Ollama is running and has the required models
3. Check the logs for error messages
4. Make sure the WebArena directory is set correctly in the configuration

If you continue to experience issues, please report them on the DMac issue tracker.
