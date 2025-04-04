"""
Base Agent for DMac.

This module provides the base agent class for all agents in the system.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Awaitable

from config.config import config
from utils.secure_logging import get_logger
from agents.swarm_manager import swarm_manager

logger = get_logger('dmac.agents.base_agent')


class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, agent_type: str = "base", model_name: Optional[str] = None):
        """Initialize the base agent.
        
        Args:
            name: The name of the agent.
            agent_type: The type of the agent.
            model_name: The name of the model to use for the agent.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.agent_type = agent_type
        self.model_name = model_name
        self.created_at = time.time()
        self.updated_at = time.time()
        self.is_active = False
        self.message_queue = asyncio.Queue()
        self.message_handlers = {}
        self.task_queue = asyncio.Queue()
        self.current_task = None
        self.task_history = []
        
        # Register with the swarm manager
        asyncio.create_task(swarm_manager.register_agent(self.id, self))
        
        logger.info(f"Initialized {agent_type} agent '{name}' with ID {self.id}")
    
    async def start(self) -> None:
        """Start the agent."""
        if self.is_active:
            logger.warning(f"Agent {self.id} is already active")
            return
        
        self.is_active = True
        
        # Start the message processing loop
        asyncio.create_task(self._process_messages())
        
        # Start the task processing loop
        asyncio.create_task(self._process_tasks())
        
        logger.info(f"Started agent {self.id}")
    
    async def stop(self) -> None:
        """Stop the agent."""
        if not self.is_active:
            logger.warning(f"Agent {self.id} is already inactive")
            return
        
        self.is_active = False
        
        # Unregister from the swarm manager
        await swarm_manager.unregister_agent(self.id)
        
        logger.info(f"Stopped agent {self.id}")
    
    async def receive_message(self, message: Dict[str, Any]) -> None:
        """Receive a message from another agent or the system.
        
        Args:
            message: The message to receive.
        """
        if not self.is_active:
            logger.warning(f"Agent {self.id} is inactive and cannot receive messages")
            return
        
        # Add the message to the queue
        await self.message_queue.put(message)
        
        logger.debug(f"Agent {self.id} received message: {message}")
    
    async def send_message(self, recipient_id: str, message_type: str, content: Any) -> bool:
        """Send a message to another agent.
        
        Args:
            recipient_id: The ID of the agent to send the message to.
            message_type: The type of the message.
            content: The content of the message.
            
        Returns:
            True if the message was sent, False otherwise.
        """
        if not self.is_active:
            logger.warning(f"Agent {self.id} is inactive and cannot send messages")
            return False
        
        # Get the recipient agent
        recipient = await swarm_manager.get_agent(recipient_id)
        
        if not recipient:
            logger.warning(f"Agent {self.id} could not send message to unknown agent {recipient_id}")
            return False
        
        # Create the message
        message = {
            'id': str(uuid.uuid4()),
            'sender_id': self.id,
            'sender_name': self.name,
            'sender_type': self.agent_type,
            'recipient_id': recipient_id,
            'message_type': message_type,
            'content': content,
            'timestamp': time.time(),
        }
        
        # Send the message to the recipient
        await recipient.receive_message(message)
        
        logger.debug(f"Agent {self.id} sent message to agent {recipient_id}: {message}")
        return True
    
    async def broadcast_message(self, swarm_id: str, message_type: str, content: Any) -> bool:
        """Broadcast a message to all agents in a swarm.
        
        Args:
            swarm_id: The ID of the swarm to broadcast to.
            message_type: The type of the message.
            content: The content of the message.
            
        Returns:
            True if the message was broadcast, False otherwise.
        """
        if not self.is_active:
            logger.warning(f"Agent {self.id} is inactive and cannot broadcast messages")
            return False
        
        # Create the message
        message = {
            'id': str(uuid.uuid4()),
            'sender_id': self.id,
            'sender_name': self.name,
            'sender_type': self.agent_type,
            'swarm_id': swarm_id,
            'message_type': message_type,
            'content': content,
            'timestamp': time.time(),
        }
        
        # Broadcast the message to the swarm
        result = await swarm_manager.broadcast_to_swarm(swarm_id, message)
        
        if result:
            logger.debug(f"Agent {self.id} broadcast message to swarm {swarm_id}: {message}")
        else:
            logger.warning(f"Agent {self.id} failed to broadcast message to swarm {swarm_id}")
        
        return result
    
    async def register_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Register a handler for a specific message type.
        
        Args:
            message_type: The type of message to handle.
            handler: The handler function to call when a message of this type is received.
        """
        self.message_handlers[message_type] = handler
        
        logger.debug(f"Agent {self.id} registered handler for message type '{message_type}'")
    
    async def unregister_message_handler(self, message_type: str) -> None:
        """Unregister a handler for a specific message type.
        
        Args:
            message_type: The type of message to stop handling.
        """
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
            
            logger.debug(f"Agent {self.id} unregistered handler for message type '{message_type}'")
    
    async def add_task(self, task: Dict[str, Any]) -> None:
        """Add a task to the agent's task queue.
        
        Args:
            task: The task to add.
        """
        if not self.is_active:
            logger.warning(f"Agent {self.id} is inactive and cannot accept tasks")
            return
        
        # Add the task to the queue
        await self.task_queue.put(task)
        
        logger.debug(f"Agent {self.id} added task: {task}")
    
    async def _process_messages(self) -> None:
        """Process messages from the message queue."""
        while self.is_active:
            try:
                # Get a message from the queue
                message = await self.message_queue.get()
                
                # Process the message
                await self._handle_message(message)
                
                # Mark the message as processed
                self.message_queue.task_done()
            except asyncio.CancelledError:
                logger.info(f"Agent {self.id} message processing loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error processing message for agent {self.id}: {e}")
    
    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle a message.
        
        Args:
            message: The message to handle.
        """
        message_type = message.get('message_type')
        
        if not message_type:
            logger.warning(f"Agent {self.id} received message with no type: {message}")
            return
        
        # Check if there is a handler for this message type
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](message)
            except Exception as e:
                logger.error(f"Error handling message of type '{message_type}' for agent {self.id}: {e}")
        else:
            logger.warning(f"Agent {self.id} has no handler for message type '{message_type}'")
    
    async def _process_tasks(self) -> None:
        """Process tasks from the task queue."""
        while self.is_active:
            try:
                # Get a task from the queue
                task = await self.task_queue.get()
                
                # Set the current task
                self.current_task = task
                
                # Process the task
                await self._handle_task(task)
                
                # Add the task to the history
                self.task_history.append(task)
                
                # Clear the current task
                self.current_task = None
                
                # Mark the task as processed
                self.task_queue.task_done()
            except asyncio.CancelledError:
                logger.info(f"Agent {self.id} task processing loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error processing task for agent {self.id}: {e}")
    
    async def _handle_task(self, task: Dict[str, Any]) -> None:
        """Handle a task.
        
        Args:
            task: The task to handle.
        """
        # This method should be overridden by subclasses
        logger.warning(f"Agent {self.id} has no task handler")
    
    async def get_info(self) -> Dict[str, Any]:
        """Get information about the agent.
        
        Returns:
            A dictionary containing information about the agent.
        """
        return {
            'id': self.id,
            'name': self.name,
            'type': self.agent_type,
            'model_name': self.model_name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'message_queue_size': self.message_queue.qsize(),
            'task_queue_size': self.task_queue.qsize(),
            'current_task': self.current_task,
            'task_history_size': len(self.task_history),
        }
    
    async def join_swarm(self, swarm_id: str) -> bool:
        """Join a swarm.
        
        Args:
            swarm_id: The ID of the swarm to join.
            
        Returns:
            True if the agent joined the swarm, False otherwise.
        """
        result = await swarm_manager.add_agent_to_swarm(self.id, swarm_id)
        
        if result:
            logger.info(f"Agent {self.id} joined swarm {swarm_id}")
        else:
            logger.warning(f"Agent {self.id} failed to join swarm {swarm_id}")
        
        return result
    
    async def leave_swarm(self, swarm_id: str) -> bool:
        """Leave a swarm.
        
        Args:
            swarm_id: The ID of the swarm to leave.
            
        Returns:
            True if the agent left the swarm, False otherwise.
        """
        result = await swarm_manager.remove_agent_from_swarm(self.id, swarm_id)
        
        if result:
            logger.info(f"Agent {self.id} left swarm {swarm_id}")
        else:
            logger.warning(f"Agent {self.id} failed to leave swarm {swarm_id}")
        
        return result
    
    async def get_swarms(self) -> List[Dict[str, Any]]:
        """Get information about all swarms that the agent is a member of.
        
        Returns:
            A list of dictionaries containing information about all swarms that the agent is a member of.
        """
        return await swarm_manager.get_agent_swarms(self.id)
