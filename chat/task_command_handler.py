"""
Task Command Handler for DMac.

This module handles the "#Task" command to generate tasks in the chat interface.
"""

import re
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from utils.secure_logging import get_logger
from config.config import config
from task_system.task_manager import TaskManager

logger = get_logger('dmac.chat.task_command_handler')

class TaskCommandHandler:
    """Handler for task commands in chat messages."""
    
    def __init__(self):
        """Initialize the task command handler."""
        self.task_manager = TaskManager()
        self.task_pattern = r'#\s*Task\s*(?::?\s*([^\n]+))?\s*\n([\s\S]*)'
        self.model_pattern = r'#\s*Task\s*:\s*([^\s\n]+)\s*\n([\s\S]*)'
    
    async def process_message(self, message: str, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Process a message for task commands.
        
        Args:
            message: The message to process
            user_id: The ID of the user who sent the message
            
        Returns:
            Tuple of (is_task, task_info)
        """
        # Check if the message contains a task command
        task_match = re.search(self.task_pattern, message, re.IGNORECASE)
        
        if not task_match:
            return False, None
        
        # Check if a model was specified
        model_match = re.search(self.model_pattern, message, re.IGNORECASE)
        
        if model_match:
            # Extract the model name and task description
            model_name = model_match.group(1)
            task_description = model_match.group(2).strip()
        else:
            # No model specified, use the default
            model_name = config.get('models.default_model', 'gemma3:12b')
            
            # Extract the task description
            if task_match.group(1):
                # There's text after the colon
                task_description = task_match.group(1).strip() + "\n" + task_match.group(2).strip()
            else:
                # No text after the colon
                task_description = task_match.group(2).strip()
        
        # Determine the task type and agent based on the description
        task_type, agent_id = await self._determine_task_type(task_description)
        
        # Create the task
        task = await self.task_manager.create_task(
            task_type=task_type,
            description=task_description,
            data={
                'message': task_description,
                'user_id': user_id,
                'model_name': model_name
            },
            priority=2,  # High priority
            agent_id=agent_id
        )
        
        # Return the task info
        return True, {
            'task_id': task['task_id'],
            'task_type': task_type,
            'description': task_description,
            'agent_id': agent_id,
            'model_name': model_name
        }
    
    async def _determine_task_type(self, description: str) -> Tuple[str, str]:
        """Determine the task type and appropriate agent based on the description.
        
        Args:
            description: The task description
            
        Returns:
            Tuple of (task_type, agent_id)
        """
        # Define keywords for each task type
        task_keywords = {
            'code_generation': ['code', 'program', 'function', 'class', 'script', 'develop', 'implement', 'coding'],
            'prompt_creation': ['prompt', 'instruction', 'query', 'question', 'ask', 'generate text'],
            'command_generation': ['command', 'shell', 'terminal', 'bash', 'powershell', 'cmd', 'execute'],
            'component_creation': ['component', 'ui', 'interface', 'design', 'frontend', 'html', 'css', 'react']
        }
        
        # Count keyword matches for each task type
        matches = {}
        for task_type, keywords in task_keywords.items():
            count = 0
            for keyword in keywords:
                if keyword.lower() in description.lower():
                    count += 1
            matches[task_type] = count
        
        # Get the task type with the most matches
        if matches:
            task_type = max(matches.items(), key=lambda x: x[1])[0]
        else:
            # Default to code generation if no matches
            task_type = 'code_generation'
        
        # Map task types to agent IDs
        agent_map = {
            'code_generation': 'codey',
            'prompt_creation': 'perry',
            'command_generation': 'shelly',
            'component_creation': 'flora'
        }
        
        agent_id = agent_map.get(task_type, 'codey')
        
        return task_type, agent_id

# Create a singleton instance
task_command_handler = TaskCommandHandler()
