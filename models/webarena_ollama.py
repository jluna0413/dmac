"""
WebArena integration with Ollama models.

This module provides integration between WebArena and Ollama models,
allowing WebArena to use locally hosted models through Ollama.
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union

from models.model_manager import ModelManager
from utils.secure_logging import get_logger

logger = get_logger('dmac.models.webarena_ollama')


class WebArenaOllamaAgent:
    """WebArena agent that uses Ollama models."""
    
    def __init__(self, model_name: str = "gemma3:12b", api_url: str = "http://localhost:11434"):
        """Initialize the WebArena Ollama agent.
        
        Args:
            model_name: The name of the Ollama model to use.
            api_url: The URL of the Ollama API.
        """
        self.model_name = model_name
        self.api_url = api_url
        self.model_manager = ModelManager()
        self.session_history = []
        
        logger.info(f"Initialized WebArena Ollama agent with model: {model_name}")
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response to a prompt using the Ollama model.
        
        Args:
            prompt: The prompt to generate a response for.
            system_prompt: An optional system prompt to provide context.
            
        Returns:
            The generated response.
        """
        try:
            # Add the prompt to the session history
            self.session_history.append({"role": "user", "content": prompt})
            
            # Generate a response using the model manager
            response = await self.model_manager.generate(
                prompt=prompt,
                model=self.model_name,
                system_prompt=system_prompt
            )
            
            # Add the response to the session history
            self.session_history.append({"role": "assistant", "content": response})
            
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {e}"
    
    async def process_webarena_action(self, observation: str, task: str) -> str:
        """Process a WebArena observation and generate an action.
        
        Args:
            observation: The observation from WebArena (usually a screenshot and text).
            task: The task to perform.
            
        Returns:
            The action to take (click, type, go_back, etc.).
        """
        # Create a prompt that includes the task and observation
        prompt = f"""
Task: {task}

Current Observation:
{observation}

Based on the observation, what action should I take next? Choose from:
1. `click [element]` - Click on an element
2. `type [text]` - Type text into a field
3. `go_back` - Go back to the previous page

Your response should be a single action in the format specified above.
"""
        
        # Generate a response
        response = await self.generate_response(prompt)
        
        # Extract the action from the response
        action_lines = [line for line in response.split('\n') if '`click' in line or '`type' in line or '`go_back' in line]
        
        if action_lines:
            return action_lines[0]
        else:
            logger.warning(f"No valid action found in response: {response}")
            return "`click [unknown]`"
    
    def reset(self) -> None:
        """Reset the agent's session history."""
        self.session_history = []
        logger.info("Reset WebArena Ollama agent session history")


class WebArenaRunner:
    """Runner for WebArena experiments using Ollama models."""
    
    def __init__(self, output_dir: str = "webarena_results"):
        """Initialize the WebArena runner.
        
        Args:
            output_dir: The directory to save results to.
        """
        self.output_dir = output_dir
        self.agents = {}
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized WebArena runner with output directory: {output_dir}")
    
    def add_agent(self, agent_name: str, model_name: str) -> None:
        """Add an agent to the runner.
        
        Args:
            agent_name: The name of the agent.
            model_name: The name of the Ollama model to use.
        """
        self.agents[agent_name] = WebArenaOllamaAgent(model_name=model_name)
        logger.info(f"Added agent {agent_name} with model {model_name}")
    
    async def run_experiment(self, tasks: List[Dict[str, Any]], agent_name: str) -> Dict[str, Any]:
        """Run an experiment with a specific agent.
        
        Args:
            tasks: The tasks to run.
            agent_name: The name of the agent to use.
            
        Returns:
            The results of the experiment.
        """
        if agent_name not in self.agents:
            logger.error(f"Agent {agent_name} not found")
            return {"error": f"Agent {agent_name} not found"}
        
        agent = self.agents[agent_name]
        results = {}
        
        for i, task in enumerate(tasks):
            task_id = task.get("id", f"task_{i}")
            task_description = task.get("description", "")
            task_site = task.get("site", "")
            
            logger.info(f"Running task {task_id} with agent {agent_name}")
            
            # Reset the agent for each task
            agent.reset()
            
            # Initialize the task result
            task_result = {
                "id": task_id,
                "description": task_description,
                "site": task_site,
                "success": False,
                "messages": []
            }
            
            # Simulate the task (in a real implementation, this would interact with WebArena)
            # For now, we'll just generate some sample interactions
            initial_observation = f"You are on the {task_site} site. The page shows [simulated content]."
            
            # Add the initial observation to the messages
            task_result["messages"].append({
                "user": initial_observation,
                "image": f"simulated_image_{i}_0.png"
            })
            
            # Generate the first action
            action = await agent.process_webarena_action(initial_observation, task_description)
            
            # Add the action to the messages
            task_result["messages"].append({
                "assistant": action
            })
            
            # Simulate a few more interactions
            for j in range(3):
                # Simulate the next observation based on the action
                next_observation = f"After {action}, you now see [simulated response content]."
                
                # Add the observation to the messages
                task_result["messages"].append({
                    "user": next_observation,
                    "image": f"simulated_image_{i}_{j+1}.png"
                })
                
                # Generate the next action
                action = await agent.process_webarena_action(next_observation, task_description)
                
                # Add the action to the messages
                task_result["messages"].append({
                    "assistant": action
                })
            
            # Simulate task success (in a real implementation, this would be determined by WebArena)
            task_result["success"] = True if random.random() > 0.3 else False
            
            # Add the task result to the results
            results[task_id] = task_result
            
            logger.info(f"Completed task {task_id} with success: {task_result['success']}")
        
        # Save the results
        self._save_results(results, agent_name)
        
        return results
    
    def _save_results(self, results: Dict[str, Any], agent_name: str) -> None:
        """Save the results of an experiment.
        
        Args:
            results: The results to save.
            agent_name: The name of the agent used.
        """
        # Create a filename for the results
        filename = f"{agent_name.replace(':', '_')}_results.json"
        file_path = os.path.join(self.output_dir, filename)
        
        # Save the results to a JSON file
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved results to {file_path}")


# Add this import at the top of the file
import random

# Example usage
async def main():
    """Example usage of the WebArena Ollama integration."""
    # Create a runner
    runner = WebArenaRunner()
    
    # Add agents with different models
    runner.add_agent("gemma3", "gemma3:12b")
    runner.add_agent("llama3", "llama3:8b")
    
    # Define some tasks
    tasks = [
        {
            "id": "task_1",
            "description": "Find the cheapest laptop on the shopping site",
            "site": "shopping"
        },
        {
            "id": "task_2",
            "description": "Search for posts about artificial intelligence on Reddit",
            "site": "reddit"
        },
        {
            "id": "task_3",
            "description": "Find directions from New York to Boston",
            "site": "mapping"
        }
    ]
    
    # Run experiments with each agent
    for agent_name in runner.agents:
        results = await runner.run_experiment(tasks, agent_name)
        print(f"Agent {agent_name} completed {len(results)} tasks")


if __name__ == "__main__":
    asyncio.run(main())
