"""
Task Agent for DMac.

This module provides the task agent class for handling specific tasks.
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

logger = get_logger('dmac.agents.task_agent')


class TaskAgent(BaseAgent):
    """Agent for handling specific tasks."""
    
    def __init__(self, name: str, model_name: Optional[str] = None):
        """Initialize the task agent.
        
        Args:
            name: The name of the agent.
            model_name: The name of the model to use for the agent.
        """
        super().__init__(name, agent_type="task", model_name=model_name)
        
        # Initialize the model manager
        self.model_manager = ModelManager()
        
        # Set the default model if none is provided
        if not self.model_name:
            self.model_name = config.get('models.default_model', 'gemma3:12b')
        
        # Task-specific attributes
        self.task_results = {}
        self.task_status = {}
        
        # Register message handlers
        asyncio.create_task(self.register_message_handler('task_request', self._handle_task_request))
        asyncio.create_task(self.register_message_handler('task_status_request', self._handle_task_status_request))
        asyncio.create_task(self.register_message_handler('task_result_request', self._handle_task_result_request))
        
        logger.info(f"Initialized task agent '{name}' with model '{self.model_name}'")
    
    async def _handle_task(self, task: Dict[str, Any]) -> None:
        """Handle a task.
        
        Args:
            task: The task to handle.
        """
        task_id = task.get('id')
        task_type = task.get('type')
        task_prompt = task.get('prompt')
        task_params = task.get('params', {})
        
        if not task_id:
            logger.warning(f"Agent {self.id} received task with no ID")
            return
        
        if not task_type:
            logger.warning(f"Agent {self.id} received task with no type: {task}")
            return
        
        if not task_prompt:
            logger.warning(f"Agent {self.id} received task with no prompt: {task}")
            return
        
        logger.info(f"Agent {self.id} handling task {task_id} of type '{task_type}'")
        
        # Update task status
        self.task_status[task_id] = 'processing'
        
        try:
            # Process the task based on its type
            if task_type == 'generate':
                result = await self._handle_generate_task(task_prompt, task_params)
            elif task_type == 'analyze':
                result = await self._handle_analyze_task(task_prompt, task_params)
            elif task_type == 'search':
                result = await self._handle_search_task(task_prompt, task_params)
            else:
                logger.warning(f"Agent {self.id} received unknown task type '{task_type}'")
                result = {'error': f"Unknown task type '{task_type}'"}
                self.task_status[task_id] = 'failed'
                return
            
            # Store the task result
            self.task_results[task_id] = result
            
            # Update task status
            self.task_status[task_id] = 'completed'
            
            logger.info(f"Agent {self.id} completed task {task_id}")
            
            # Notify the task requester if specified
            if 'requester_id' in task:
                await self.send_message(
                    task['requester_id'],
                    'task_completed',
                    {
                        'task_id': task_id,
                        'result': result,
                    }
                )
        except Exception as e:
            logger.error(f"Error handling task {task_id} for agent {self.id}: {e}")
            
            # Update task status
            self.task_status[task_id] = 'failed'
            
            # Store the error as the task result
            self.task_results[task_id] = {'error': str(e)}
            
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
    
    async def _handle_generate_task(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a generate task.
        
        Args:
            prompt: The prompt to generate from.
            params: Additional parameters for the generation.
            
        Returns:
            The generation result.
        """
        # Get the system prompt if provided
        system_prompt = params.get('system_prompt')
        
        # Generate a response using the model manager
        response = await self.model_manager.generate(
            prompt=prompt,
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        return {
            'response': response,
            'model': self.model_name,
            'timestamp': time.time(),
        }
    
    async def _handle_analyze_task(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an analyze task.
        
        Args:
            prompt: The prompt to analyze.
            params: Additional parameters for the analysis.
            
        Returns:
            The analysis result.
        """
        # Get the system prompt for analysis
        system_prompt = params.get('system_prompt', "You are an expert analyst. Analyze the following text and provide insights.")
        
        # Generate an analysis using the model manager
        response = await self.model_manager.generate(
            prompt=prompt,
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        # Parse the response as JSON if possible
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            analysis = {'text': response}
        
        return {
            'analysis': analysis,
            'model': self.model_name,
            'timestamp': time.time(),
        }
    
    async def _handle_search_task(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a search task.
        
        Args:
            prompt: The prompt to search for.
            params: Additional parameters for the search.
            
        Returns:
            The search result.
        """
        # This is a placeholder for a real search implementation
        # In a real implementation, this would use a search engine or database
        
        # Generate a search response using the model manager
        system_prompt = "You are a search engine. Provide relevant information for the following query."
        
        response = await self.model_manager.generate(
            prompt=prompt,
            model=self.model_name,
            system_prompt=system_prompt
        )
        
        return {
            'results': [
                {
                    'title': 'Search Result 1',
                    'content': response,
                    'relevance': 0.95,
                }
            ],
            'model': self.model_name,
            'timestamp': time.time(),
        }
    
    async def _handle_task_request(self, message: Dict[str, Any]) -> None:
        """Handle a task request message.
        
        Args:
            message: The message containing the task request.
        """
        content = message.get('content', {})
        task = content.get('task')
        
        if not task:
            logger.warning(f"Agent {self.id} received task request with no task: {message}")
            
            # Send an error response
            await self.send_message(
                message['sender_id'],
                'task_request_error',
                {
                    'error': 'No task provided',
                    'original_message': message,
                }
            )
            return
        
        # Add the requester ID to the task
        task['requester_id'] = message['sender_id']
        
        # Add the task to the queue
        await self.add_task(task)
        
        # Send an acknowledgement
        await self.send_message(
            message['sender_id'],
            'task_request_ack',
            {
                'task_id': task.get('id'),
                'message': f"Task received and queued for processing",
            }
        )
    
    async def _handle_task_status_request(self, message: Dict[str, Any]) -> None:
        """Handle a task status request message.
        
        Args:
            message: The message containing the task status request.
        """
        content = message.get('content', {})
        task_id = content.get('task_id')
        
        if not task_id:
            logger.warning(f"Agent {self.id} received task status request with no task ID: {message}")
            
            # Send an error response
            await self.send_message(
                message['sender_id'],
                'task_status_error',
                {
                    'error': 'No task ID provided',
                    'original_message': message,
                }
            )
            return
        
        # Get the task status
        status = self.task_status.get(task_id, 'unknown')
        
        # Send the status response
        await self.send_message(
            message['sender_id'],
            'task_status_response',
            {
                'task_id': task_id,
                'status': status,
            }
        )
    
    async def _handle_task_result_request(self, message: Dict[str, Any]) -> None:
        """Handle a task result request message.
        
        Args:
            message: The message containing the task result request.
        """
        content = message.get('content', {})
        task_id = content.get('task_id')
        
        if not task_id:
            logger.warning(f"Agent {self.id} received task result request with no task ID: {message}")
            
            # Send an error response
            await self.send_message(
                message['sender_id'],
                'task_result_error',
                {
                    'error': 'No task ID provided',
                    'original_message': message,
                }
            )
            return
        
        # Get the task result
        result = self.task_results.get(task_id)
        
        if result is None:
            # Send an error response
            await self.send_message(
                message['sender_id'],
                'task_result_error',
                {
                    'error': f"No result found for task ID '{task_id}'",
                    'task_id': task_id,
                }
            )
            return
        
        # Send the result response
        await self.send_message(
            message['sender_id'],
            'task_result_response',
            {
                'task_id': task_id,
                'result': result,
            }
        )
    
    async def get_info(self) -> Dict[str, Any]:
        """Get information about the agent.
        
        Returns:
            A dictionary containing information about the agent.
        """
        info = await super().get_info()
        
        # Add task agent specific information
        info.update({
            'task_count': len(self.task_results),
            'completed_tasks': sum(1 for status in self.task_status.values() if status == 'completed'),
            'failed_tasks': sum(1 for status in self.task_status.values() if status == 'failed'),
            'processing_tasks': sum(1 for status in self.task_status.values() if status == 'processing'),
        })
        
        return info
