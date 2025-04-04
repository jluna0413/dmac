"""
Agent Manager for DMac.

This module provides a manager for agent creation and interaction.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Type

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors, AgentError
from agents.agent_factory import AgentFactory
from agents.base_agent import BaseAgent
from agents.task_agent_factory import task_agent_factory
from agents.assistant_agent_factory import assistant_agent_factory
from agents.tool_agent_factory import tool_agent_factory
from agents.webarena_agent_factory import webarena_agent_factory

logger = get_logger('dmac.agents.agent_manager')


class AgentManager:
    """Manager for agent creation and interaction."""
    
    def __init__(self):
        """Initialize the agent manager."""
        # Load configuration
        self.enabled = config.get('agents.enabled', True)
        
        # Initialize agent factories
        self.agent_factories = {
            'task': task_agent_factory,
            'assistant': assistant_agent_factory,
            'tool': tool_agent_factory,
            'webarena': webarena_agent_factory,
        }
        
        # Initialize message queue
        self.message_queue = asyncio.Queue()
        
        # Initialize message processing task
        self.message_processor_task = None
        self.is_processing_messages = False
        
        logger.info("Agent manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the agent manager.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            logger.info("Agent manager is disabled")
            return True
        
        try:
            # Start the message processor
            self.is_processing_messages = True
            self.message_processor_task = asyncio.create_task(self._process_messages())
            
            logger.info("Agent manager initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing agent manager: {e}")
            return False
    
    @handle_async_errors(default_message="Error creating agent")
    async def create_agent(self, agent_type: str, name: Optional[str] = None, **kwargs) -> BaseAgent:
        """Create a new agent.
        
        Args:
            agent_type: The type of agent to create.
            name: Optional name for the agent.
            **kwargs: Additional arguments for the agent.
            
        Returns:
            The created agent.
            
        Raises:
            AgentError: If the agent could not be created.
        """
        if not self.enabled:
            logger.warning("Agent manager is disabled")
            raise AgentError("Agent manager is disabled")
        
        # Get the agent factory
        factory = self.agent_factories.get(agent_type)
        
        if not factory:
            logger.warning(f"Unknown agent type: {agent_type}")
            raise AgentError(f"Unknown agent type: {agent_type}")
        
        # Create the agent
        agent = await factory.create_agent(name=name, **kwargs)
        
        logger.info(f"Created {agent_type} agent {agent.agent_id} ({agent.name})")
        return agent
    
    @handle_async_errors(default_message="Error getting agent")
    async def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to get.
            
        Returns:
            The agent, or None if not found.
        """
        if not self.enabled:
            logger.warning("Agent manager is disabled")
            return None
        
        # Try each factory
        for factory in self.agent_factories.values():
            agent = await factory.get_agent(agent_id)
            if agent:
                return agent
        
        return None
    
    @handle_async_errors(default_message="Error listing agents")
    async def list_agents(self, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all agents.
        
        Args:
            agent_type: Optional type of agents to list.
            
        Returns:
            A list of dictionaries containing agent information.
        """
        if not self.enabled:
            logger.warning("Agent manager is disabled")
            return []
        
        agents = []
        
        # Get agents from each factory
        for factory_type, factory in self.agent_factories.items():
            if agent_type is None or factory_type == agent_type:
                factory_agents = await factory.list_agents()
                agents.extend(factory_agents)
        
        return agents
    
    @handle_async_errors(default_message="Error deleting agent")
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent.
        
        Args:
            agent_id: The ID of the agent to delete.
            
        Returns:
            True if the agent was deleted, False otherwise.
        """
        if not self.enabled:
            logger.warning("Agent manager is disabled")
            return False
        
        # Try each factory
        for factory in self.agent_factories.values():
            success = await factory.delete_agent(agent_id)
            if success:
                return True
        
        logger.warning(f"Agent {agent_id} not found")
        return False
    
    @handle_async_errors(default_message="Error sending message to agent")
    async def send_message(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to an agent.
        
        Args:
            agent_id: The ID of the agent to send the message to.
            message: The message to send.
            
        Returns:
            The response message.
            
        Raises:
            AgentError: If the message could not be sent.
        """
        if not self.enabled:
            logger.warning("Agent manager is disabled")
            raise AgentError("Agent manager is disabled")
        
        # Get the agent
        agent = await self.get_agent(agent_id)
        
        if not agent:
            logger.warning(f"Agent {agent_id} not found")
            raise AgentError(f"Agent {agent_id} not found")
        
        # Process the message
        response = await agent.process_message(message)
        
        return response
    
    @handle_async_errors(default_message="Error sending message to queue")
    async def send_message_to_queue(self, agent_id: str, message: Dict[str, Any], callback: Optional[callable] = None) -> str:
        """Send a message to the agent's message queue.
        
        Args:
            agent_id: The ID of the agent to send the message to.
            message: The message to send.
            callback: Optional callback function to call with the response.
            
        Returns:
            The message ID.
            
        Raises:
            AgentError: If the message could not be sent.
        """
        if not self.enabled:
            logger.warning("Agent manager is disabled")
            raise AgentError("Agent manager is disabled")
        
        # Generate a message ID
        message_id = str(uuid.uuid4())
        
        # Add the message to the queue
        await self.message_queue.put({
            'message_id': message_id,
            'agent_id': agent_id,
            'message': message,
            'callback': callback,
        })
        
        return message_id
    
    async def cleanup(self) -> None:
        """Clean up resources used by the agent manager."""
        if not self.enabled:
            logger.debug("Agent manager is disabled")
            return
        
        logger.info("Cleaning up agent manager")
        
        # Stop the message processor
        self.is_processing_messages = False
        
        if self.message_processor_task:
            self.message_processor_task.cancel()
            try:
                await self.message_processor_task
            except asyncio.CancelledError:
                pass
            self.message_processor_task = None
        
        # Clean up agent factories
        for factory_type, factory in self.agent_factories.items():
            try:
                logger.info(f"Cleaning up {factory_type} agent factory")
                await factory.cleanup()
            except Exception as e:
                logger.exception(f"Error cleaning up {factory_type} agent factory: {e}")
        
        logger.info("Agent manager cleaned up")
    
    async def _process_messages(self) -> None:
        """Process messages from the message queue."""
        while self.is_processing_messages:
            try:
                # Get a message from the queue
                message_info = await self.message_queue.get()
                
                # Extract message information
                message_id = message_info['message_id']
                agent_id = message_info['agent_id']
                message = message_info['message']
                callback = message_info['callback']
                
                try:
                    # Send the message to the agent
                    response = await self.send_message(agent_id, message)
                    
                    # Call the callback if provided
                    if callback:
                        try:
                            callback(message_id, response)
                        except Exception as e:
                            logger.exception(f"Error in message callback: {e}")
                except Exception as e:
                    logger.exception(f"Error processing message {message_id}: {e}")
                    
                    # Call the callback with an error response if provided
                    if callback:
                        try:
                            callback(message_id, {
                                'type': 'error',
                                'error': str(e),
                                'message': f"Error processing message: {e}",
                            })
                        except Exception as e:
                            logger.exception(f"Error in message callback: {e}")
                
                # Mark the message as done
                self.message_queue.task_done()
            except asyncio.CancelledError:
                logger.info("Message processor cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in message processor: {e}")
                await asyncio.sleep(1)  # Wait a bit before trying again


# Create a singleton instance
agent_manager = AgentManager()
