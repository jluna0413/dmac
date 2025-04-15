"""
Test script for WebArena integration.

This script tests the WebArena integration by creating a WebArena agent,
running an experiment, and checking the results.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import config
from utils.secure_logging import setup_logging, get_logger
from agents.agent_manager import agent_manager
from webarena.webarena_manager import webarena_manager
from webarena.ollama_integration import webarena_ollama_integration

logger = get_logger('dmac.tests.test_webarena_integration')


async def test_webarena_integration():
    """Test the WebArena integration."""
    # Set up logging
    setup_logging()
    
    logger.info("Testing WebArena integration")
    
    try:
        # Initialize components
        logger.info("Initializing components")
        
        # Initialize WebArena manager
        logger.info("Initializing WebArena manager")
        await webarena_manager.initialize()
        
        # Initialize WebArena Ollama integration
        logger.info("Initializing WebArena Ollama integration")
        await webarena_ollama_integration.initialize()
        
        # Initialize agent manager
        logger.info("Initializing agent manager")
        await agent_manager.initialize()
        
        # Check if WebArena is installed
        if not webarena_manager._is_webarena_installed():
            logger.warning("WebArena is not installed")
            return
        
        # Get available tasks
        logger.info("Getting available tasks")
        tasks = await webarena_manager.get_available_tasks()
        logger.info(f"Available tasks: {json.dumps(tasks, indent=2)}")
        
        # Get available models
        logger.info("Getting available models")
        models = await webarena_ollama_integration.get_available_models()
        logger.info(f"Available models: {json.dumps(models, indent=2)}")
        
        # Create a WebArena agent
        logger.info("Creating WebArena agent")
        agent = await agent_manager.create_agent(agent_type="webarena", name="Test WebArena Agent")
        logger.info(f"Created agent: {agent.agent_id} ({agent.name})")
        
        # Send a help message to the agent
        logger.info("Sending help message to agent")
        response = await agent_manager.send_message(agent.agent_id, {"type": "help"})
        logger.info(f"Help response: {json.dumps(response, indent=2)}")
        
        # List agents
        logger.info("Listing agents")
        agents = await agent_manager.list_agents(agent_type="webarena")
        logger.info(f"Agents: {json.dumps(agents, indent=2)}")
        
        # Clean up
        logger.info("Cleaning up")
        await agent_manager.delete_agent(agent.agent_id)
        await webarena_manager.cleanup()
        await agent_manager.cleanup()
        
        logger.info("WebArena integration test completed successfully")
    except Exception as e:
        logger.exception(f"Error testing WebArena integration: {e}")


if __name__ == "__main__":
    asyncio.run(test_webarena_integration())
