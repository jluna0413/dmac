"""
Run WebArena experiments with Ollama models.

This script runs WebArena experiments using locally hosted Ollama models.
"""

import os
import json
import asyncio
import argparse
from typing import List, Dict, Any

from models.webarena_ollama import WebArenaRunner


async def run_experiments(config_file: str, output_dir: str) -> None:
    """Run WebArena experiments with Ollama models.
    
    Args:
        config_file: Path to the configuration file.
        output_dir: Directory to save results to.
    """
    # Load the configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Create a runner
    runner = WebArenaRunner(output_dir=output_dir)
    
    # Add agents from the configuration
    for agent_config in config.get("agents", []):
        agent_name = agent_config.get("name")
        model_name = agent_config.get("model")
        
        if agent_name and model_name:
            runner.add_agent(agent_name, model_name)
            print(f"Added agent {agent_name} with model {model_name}")
    
    # Get the tasks from the configuration
    tasks = config.get("tasks", [])
    
    if not tasks:
        print("No tasks found in the configuration")
        return
    
    print(f"Loaded {len(tasks)} tasks from the configuration")
    
    # Run experiments with each agent
    for agent_name in runner.agents:
        print(f"Running experiments with agent {agent_name}...")
        results = await runner.run_experiment(tasks, agent_name)
        print(f"Agent {agent_name} completed {len(results)} tasks")
    
    print(f"All experiments completed. Results saved to {output_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run WebArena experiments with Ollama models")
    parser.add_argument("--config", type=str, default="webarena_config.json", help="Path to the configuration file")
    parser.add_argument("--output", type=str, default="webarena_results", help="Directory to save results to")
    
    args = parser.parse_args()
    
    # Create the output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Run the experiments
    asyncio.run(run_experiments(args.config, args.output))


if __name__ == "__main__":
    main()
