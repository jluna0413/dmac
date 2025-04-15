"""
Chat Message Processor for DMac.

This module processes chat messages and handles special commands.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from utils.secure_logging import get_logger
from config.config import config
from chat.agent_mention_handler import agent_mention_handler
from chat.task_command_handler import task_command_handler
from agents.memory_manager import memory_manager

logger = get_logger('dmac.chat.message_processor')

class MessageProcessor:
    """Processor for chat messages."""
    
    def __init__(self):
        """Initialize the message processor."""
        pass
    
    async def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """Process a chat message.
        
        Args:
            message: The message to process
            user_id: The ID of the user who sent the message
            
        Returns:
            Processing result
        """
        # Initialize the result
        result = {
            'original_message': message,
            'processed_message': message,
            'is_task': False,
            'task_info': None,
            'agent_responses': [],
            'memories_created': []
        }
        
        # Check for task command
        is_task, task_info = await task_command_handler.process_message(message, user_id)
        
        if is_task:
            result['is_task'] = True
            result['task_info'] = task_info
            
            # Create a memory for the task
            if task_info:
                memory = await memory_manager.add_memory(
                    agent_id=task_info['agent_id'],
                    memory=f"User {user_id} created a task: {task_info['description']}",
                    context={
                        'task_id': task_info['task_id'],
                        'task_type': task_info['task_type'],
                        'model_name': task_info['model_name']
                    },
                    importance=3  # Medium-high importance
                )
                
                result['memories_created'].append(memory)
            
            return result
        
        # Check for agent mentions
        processed_message, agent_responses = await agent_mention_handler.process_message(message, user_id)
        
        result['processed_message'] = processed_message
        result['agent_responses'] = agent_responses
        
        # Create memories for agent mentions
        for response in agent_responses:
            memory = await memory_manager.add_memory(
                agent_id=response['agent_id'],
                memory=f"User {user_id} mentioned me in a message: {message}",
                context={
                    'task_id': response['task_id'],
                    'user_message': message
                },
                importance=2  # Medium importance
            )
            
            result['memories_created'].append(memory)
        
        return result

# Create a singleton instance
message_processor = MessageProcessor()
