"""
WebArena Agent Factory for DMac.

This module provides a factory for creating WebArena agents.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors, AgentError
from agents.agent_factory import AgentFactory
from agents.webarena_agent import WebArenaAgent

logger = get_logger('dmac.agents.webarena_agent_factory')


class WebArenaAgentFactory(AgentFactory):
    """Factory for creating WebArena agents."""
    
    def __init__(self):
        """Initialize the WebArena agent factory."""
        super().__init__(agent_type="webarena")
        
        # Load configuration
        self.max_agents = config.get('agents.webarena.max_agents', 10)
        
        # Initialize agent tracking
        self.agents = {}
        
        logger.info("WebArena agent factory initialized")
    
    @handle_async_errors(default_message="Error creating WebArena agent")
    async def create_agent(self, name: Optional[str] = None, **kwargs) -> WebArenaAgent:
        """Create a new WebArena agent.
        
        Args:
            name: Optional name for the agent.
            **kwargs: Additional arguments for the agent.
            
        Returns:
            The created agent.
            
        Raises:
            AgentError: If the agent could not be created.
        """
        # Check if we've reached the maximum number of agents
        if len(self.agents) >= self.max_agents:
            logger.warning(f"Maximum number of WebArena agents reached: {self.max_agents}")
            raise AgentError(f"Maximum number of WebArena agents reached: {self.max_agents}")
        
        # Generate an agent ID
        agent_id = str(uuid.uuid4())
        
        # Set the agent name
        if not name:
            name = f"WebArena Agent {len(self.agents) + 1}"
        
        # Create the agent
        agent = WebArenaAgent(agent_id, name)
        
        # Initialize the agent
        success = await agent.initialize()
        
        if not success:
            logger.warning(f"Failed to initialize WebArena agent {agent_id}")
            raise AgentError(f"Failed to initialize WebArena agent {agent_id}")
        
        # Store the agent
        self.agents[agent_id] = agent
        
        logger.info(f"Created WebArena agent {agent_id} ({name})")
        return agent
    
    @handle_async_errors(default_message="Error getting WebArena agent")
    async def get_agent(self, agent_id: str) -> Optional[WebArenaAgent]:
        """Get a WebArena agent by ID.
        
        Args:
            agent_id: The ID of the agent to get.
            
        Returns:
            The agent, or None if not found.
        """
        return self.agents.get(agent_id)
    
    @handle_async_errors(default_message="Error listing WebArena agents")
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all WebArena agents.
        
        Returns:
            A list of dictionaries containing agent information.
        """
        return [
            {
                'id': agent_id,
                'name': agent.name,
                'type': agent.agent_type,
                'current_run_id': agent.current_run_id,
                'current_task': agent.current_task,
                'current_model': agent.current_model,
            }
            for agent_id, agent in self.agents.items()
        ]
    
    @handle_async_errors(default_message="Error deleting WebArena agent")
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete a WebArena agent.
        
        Args:
            agent_id: The ID of the agent to delete.
            
        Returns:
            True if the agent was deleted, False otherwise.
        """
        # Check if the agent exists
        agent = self.agents.get(agent_id)
        
        if not agent:
            logger.warning(f"WebArena agent {agent_id} not found")
            return False
        
        # Clean up the agent
        await agent.cleanup()
        
        # Remove the agent from the dictionary
        del self.agents[agent_id]
        
        logger.info(f"Deleted WebArena agent {agent_id}")
        return True
    
    async def cleanup(self) -> None:
        """Clean up resources used by the WebArena agent factory."""
        logger.info("Cleaning up WebArena agent factory")
        
        # Clean up all agents
        for agent_id, agent in list(self.agents.items()):
            try:
                await agent.cleanup()
            except Exception as e:
                logger.exception(f"Error cleaning up WebArena agent {agent_id}: {e}")
        
        # Clear the agents dictionary
        self.agents.clear()
        
        logger.info("WebArena agent factory cleaned up")


# Create a singleton instance
webarena_agent_factory = WebArenaAgentFactory()
