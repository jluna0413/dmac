"""
Assistant Agent for DMac.

This module provides the assistant agent class for handling user interactions.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Callable, Awaitable

from config.config import config
from utils.secure_logging import get_logger
from agents.base_agent import BaseAgent
from models.model_manager import ModelManager

logger = get_logger('dmac.agents.assistant_agent')


class AssistantAgent(BaseAgent):
    """Agent for handling user interactions."""
    
    def __init__(self, name: str, model_name: Optional[str] = None):
        """Initialize the assistant agent.
        
        Args:
            name: The name of the agent.
            model_name: The name of the model to use for the agent.
        """
        super().__init__(name, agent_type="assistant", model_name=model_name)
        
        # Initialize the model manager
        self.model_manager = ModelManager()
        
        # Set the default model if none is provided
        if not self.model_name:
            self.model_name = config.get('models.default_model', 'gemma3:12b')
        
        # Assistant-specific attributes
        self.conversations = {}
        self.user_preferences = {}
        self.tool_registry = {}
        
        # Register message handlers
        asyncio.create_task(self.register_message_handler('user_message', self._handle_user_message))
        asyncio.create_task(self.register_message_handler('tool_response', self._handle_tool_response))
        asyncio.create_task(self.register_message_handler('task_completed', self._handle_task_completed))
        
        logger.info(f"Initialized assistant agent '{name}' with model '{self.model_name}'")
    
    async def _handle_task(self, task: Dict[str, Any]) -> None:
        """Handle a task.
        
        Args:
            task: The task to handle.
        """
        task_id = task.get('id')
        task_type = task.get('type')
        
        if not task_id:
            logger.warning(f"Agent {self.id} received task with no ID")
            return
        
        if not task_type:
            logger.warning(f"Agent {self.id} received task with no type: {task}")
            return
        
        logger.info(f"Agent {self.id} handling task {task_id} of type '{task_type}'")
        
        try:
            # Process the task based on its type
            if task_type == 'conversation':
                await self._handle_conversation_task(task)
            elif task_type == 'user_preference':
                await self._handle_user_preference_task(task)
            elif task_type == 'tool_registration':
                await self._handle_tool_registration_task(task)
            else:
                logger.warning(f"Agent {self.id} received unknown task type '{task_type}'")
                return
            
            logger.info(f"Agent {self.id} completed task {task_id}")
            
            # Notify the task requester if specified
            if 'requester_id' in task:
                await self.send_message(
                    task['requester_id'],
                    'task_completed',
                    {
                        'task_id': task_id,
                        'message': f"Task {task_id} completed successfully",
                    }
                )
        except Exception as e:
            logger.error(f"Error handling task {task_id} for agent {self.id}: {e}")
            
            # Notify the task requester if specified
            if 'requester_id' in task:
                await self.send_message(
                    task['requester_id'],
                    'task_failed',
                    {
                        'task_id': task_id,
                        'error': str(e),
                    }
                )
    
    async def _handle_conversation_task(self, task: Dict[str, Any]) -> None:
        """Handle a conversation task.
        
        Args:
            task: The conversation task to handle.
        """
        conversation_id = task.get('conversation_id')
        user_id = task.get('user_id')
        message = task.get('message')
        
        if not conversation_id:
            logger.warning(f"Agent {self.id} received conversation task with no conversation ID: {task}")
            return
        
        if not user_id:
            logger.warning(f"Agent {self.id} received conversation task with no user ID: {task}")
            return
        
        if not message:
            logger.warning(f"Agent {self.id} received conversation task with no message: {task}")
            return
        
        # Create a new conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                'id': conversation_id,
                'user_id': user_id,
                'messages': [],
                'created_at': time.time(),
                'updated_at': time.time(),
            }
        
        # Add the user message to the conversation
        self.conversations[conversation_id]['messages'].append({
            'role': 'user',
            'content': message,
            'timestamp': time.time(),
        })
        
        # Update the conversation timestamp
        self.conversations[conversation_id]['updated_at'] = time.time()
        
        # Generate a response
        response = await self._generate_response(conversation_id)
        
        # Add the assistant message to the conversation
        self.conversations[conversation_id]['messages'].append({
            'role': 'assistant',
            'content': response,
            'timestamp': time.time(),
        })
        
        # Update the conversation timestamp
        self.conversations[conversation_id]['updated_at'] = time.time()
        
        # Send the response to the user
        if 'requester_id' in task:
            await self.send_message(
                task['requester_id'],
                'conversation_response',
                {
                    'conversation_id': conversation_id,
                    'response': response,
                }
            )
    
    async def _handle_user_preference_task(self, task: Dict[str, Any]) -> None:
        """Handle a user preference task.
        
        Args:
            task: The user preference task to handle.
        """
        user_id = task.get('user_id')
        preferences = task.get('preferences')
        
        if not user_id:
            logger.warning(f"Agent {self.id} received user preference task with no user ID: {task}")
            return
        
        if not preferences:
            logger.warning(f"Agent {self.id} received user preference task with no preferences: {task}")
            return
        
        # Create or update user preferences
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        # Update the preferences
        self.user_preferences[user_id].update(preferences)
        
        logger.info(f"Agent {self.id} updated preferences for user {user_id}")
    
    async def _handle_tool_registration_task(self, task: Dict[str, Any]) -> None:
        """Handle a tool registration task.
        
        Args:
            task: The tool registration task to handle.
        """
        tool_id = task.get('tool_id')
        tool_name = task.get('tool_name')
        tool_description = task.get('tool_description')
        tool_agent_id = task.get('tool_agent_id')
        
        if not tool_id:
            logger.warning(f"Agent {self.id} received tool registration task with no tool ID: {task}")
            return
        
        if not tool_name:
            logger.warning(f"Agent {self.id} received tool registration task with no tool name: {task}")
            return
        
        if not tool_description:
            logger.warning(f"Agent {self.id} received tool registration task with no tool description: {task}")
            return
        
        if not tool_agent_id:
            logger.warning(f"Agent {self.id} received tool registration task with no tool agent ID: {task}")
            return
        
        # Register the tool
        self.tool_registry[tool_id] = {
            'id': tool_id,
            'name': tool_name,
            'description': tool_description,
            'agent_id': tool_agent_id,
            'registered_at': time.time(),
        }
        
        logger.info(f"Agent {self.id} registered tool {tool_id} ({tool_name})")
    
    async def _handle_user_message(self, message: Dict[str, Any]) -> None:
        """Handle a user message.
        
        Args:
            message: The user message to handle.
        """
        content = message.get('content', {})
        user_id = content.get('user_id')
        conversation_id = content.get('conversation_id')
        text = content.get('text')
        
        if not user_id:
            logger.warning(f"Agent {self.id} received user message with no user ID: {message}")
            return
        
        if not conversation_id:
            logger.warning(f"Agent {self.id} received user message with no conversation ID: {message}")
            return
        
        if not text:
            logger.warning(f"Agent {self.id} received user message with no text: {message}")
            return
        
        # Create a conversation task
        task = {
            'id': f"task_{time.time()}_{conversation_id}",
            'type': 'conversation',
            'conversation_id': conversation_id,
            'user_id': user_id,
            'message': text,
            'requester_id': message['sender_id'],
        }
        
        # Add the task to the queue
        await self.add_task(task)
    
    async def _handle_tool_response(self, message: Dict[str, Any]) -> None:
        """Handle a tool response message.
        
        Args:
            message: The tool response message to handle.
        """
        content = message.get('content', {})
        conversation_id = content.get('conversation_id')
        tool_id = content.get('tool_id')
        response = content.get('response')
        
        if not conversation_id:
            logger.warning(f"Agent {self.id} received tool response with no conversation ID: {message}")
            return
        
        if not tool_id:
            logger.warning(f"Agent {self.id} received tool response with no tool ID: {message}")
            return
        
        if not response:
            logger.warning(f"Agent {self.id} received tool response with no response: {message}")
            return
        
        # Check if the conversation exists
        if conversation_id not in self.conversations:
            logger.warning(f"Agent {self.id} received tool response for unknown conversation {conversation_id}")
            return
        
        # Add the tool response to the conversation
        self.conversations[conversation_id]['messages'].append({
            'role': 'tool',
            'tool_id': tool_id,
            'content': response,
            'timestamp': time.time(),
        })
        
        # Update the conversation timestamp
        self.conversations[conversation_id]['updated_at'] = time.time()
        
        # Generate a response that incorporates the tool response
        response = await self._generate_response(conversation_id)
        
        # Add the assistant message to the conversation
        self.conversations[conversation_id]['messages'].append({
            'role': 'assistant',
            'content': response,
            'timestamp': time.time(),
        })
        
        # Update the conversation timestamp
        self.conversations[conversation_id]['updated_at'] = time.time()
        
        # Send the response to the user
        user_id = self.conversations[conversation_id]['user_id']
        
        await self.send_message(
            message['sender_id'],
            'conversation_response',
            {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'response': response,
            }
        )
    
    async def _handle_task_completed(self, message: Dict[str, Any]) -> None:
        """Handle a task completed message.
        
        Args:
            message: The task completed message to handle.
        """
        content = message.get('content', {})
        task_id = content.get('task_id')
        result = content.get('result')
        
        if not task_id:
            logger.warning(f"Agent {self.id} received task completed message with no task ID: {message}")
            return
        
        if not result:
            logger.warning(f"Agent {self.id} received task completed message with no result: {message}")
            return
        
        # Process the task result
        # This is a placeholder for task result processing
        logger.info(f"Agent {self.id} received task completion for task {task_id}")
    
    async def _generate_response(self, conversation_id: str) -> str:
        """Generate a response for a conversation.
        
        Args:
            conversation_id: The ID of the conversation to generate a response for.
            
        Returns:
            The generated response.
        """
        if conversation_id not in self.conversations:
            logger.warning(f"Agent {self.id} tried to generate a response for unknown conversation {conversation_id}")
            return "I'm sorry, but I couldn't find that conversation."
        
        # Get the conversation history
        conversation = self.conversations[conversation_id]
        messages = conversation['messages']
        
        # Create a prompt from the conversation history
        prompt = ""
        for message in messages[-10:]:  # Use the last 10 messages for context
            role = message['role']
            content = message['content']
            
            if role == 'user':
                prompt += f"User: {content}\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n"
            elif role == 'tool':
                prompt += f"Tool ({message.get('tool_id', 'unknown')}): {content}\n"
        
        prompt += "Assistant: "
        
        # Get user preferences if available
        user_id = conversation['user_id']
        user_preferences = self.user_preferences.get(user_id, {})
        
        # Create a system prompt based on user preferences
        system_prompt = "You are a helpful assistant."
        
        if 'style' in user_preferences:
            system_prompt += f" Your communication style is {user_preferences['style']}."
        
        if 'expertise' in user_preferences:
            system_prompt += f" You have expertise in {user_preferences['expertise']}."
        
        if 'language' in user_preferences:
            system_prompt += f" You communicate in {user_preferences['language']}."
        
        # Generate a response using the model manager
        response = await self.model_manager.generate(
            prompt=prompt,
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        return response
    
    async def get_info(self) -> Dict[str, Any]:
        """Get information about the agent.
        
        Returns:
            A dictionary containing information about the agent.
        """
        info = await super().get_info()
        
        # Add assistant agent specific information
        info.update({
            'conversation_count': len(self.conversations),
            'user_count': len(self.user_preferences),
            'tool_count': len(self.tool_registry),
        })
        
        return info
