"""
Task Manager for DMac.

This module provides the task manager for handling tasks.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Awaitable

from config.config import config
from utils.secure_logging import get_logger
from agents.swarm_orchestrator import swarm_orchestrator

logger = get_logger('dmac.tasks.task_manager')


class TaskManager:
    """Manager for handling tasks."""
    
    def __init__(self):
        """Initialize the task manager."""
        self.tasks = {}
        self.task_queue = asyncio.Queue()
        self.task_handlers = {}
        self.is_running = False
        self.worker_tasks = []
        
        # Load configuration
        self.max_workers = config.get('tasks.max_workers', 5)
        self.max_queue_size = config.get('tasks.max_queue_size', 100)
        
        # Register default task handlers
        self._register_default_task_handlers()
        
        logger.info("Task manager initialized")
    
    def _register_default_task_handlers(self) -> None:
        """Register default task handlers."""
        self.task_handlers['generate'] = self._handle_generate_task
        self.task_handlers['analyze'] = self._handle_analyze_task
        self.task_handlers['search'] = self._handle_search_task
        self.task_handlers['swarm'] = self._handle_swarm_task
        self.task_handlers['tool'] = self._handle_tool_task
    
    async def start(self) -> None:
        """Start the task manager."""
        if self.is_running:
            logger.warning("Task manager is already running")
            return
        
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker())
            self.worker_tasks.append(worker)
        
        logger.info(f"Started task manager with {self.max_workers} workers")
    
    async def stop(self) -> None:
        """Stop the task manager."""
        if not self.is_running:
            logger.warning("Task manager is not running")
            return
        
        self.is_running = False
        
        # Cancel all worker tasks
        for worker in self.worker_tasks:
            worker.cancel()
        
        # Wait for all worker tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        self.worker_tasks = []
        
        logger.info("Stopped task manager")
    
    async def create_task(self, task_type: str, **kwargs) -> Optional[str]:
        """Create a new task.
        
        Args:
            task_type: The type of task to create.
            **kwargs: Additional arguments for the task.
            
        Returns:
            The ID of the new task, or None if the task could not be created.
        """
        if not self.is_running:
            logger.warning("Task manager is not running")
            return None
        
        if task_type not in self.task_handlers:
            logger.warning(f"Unsupported task type '{task_type}'")
            return None
        
        if self.task_queue.qsize() >= self.max_queue_size:
            logger.warning("Task queue is full")
            return None
        
        # Create a new task
        task_id = str(uuid.uuid4())
        
        task = {
            'id': task_id,
            'type': task_type,
            'status': 'pending',
            'created_at': time.time(),
            'updated_at': time.time(),
            'params': kwargs,
        }
        
        # Add the task to the dictionary
        self.tasks[task_id] = task
        
        # Add the task to the queue
        await self.task_queue.put(task)
        
        logger.info(f"Created task {task_id} of type '{task_type}'")
        return task_id
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a task.
        
        Args:
            task_id: The ID of the task to get information about.
            
        Returns:
            A dictionary containing information about the task, or None if the task was not found.
        """
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return None
        
        return self.tasks[task_id].copy()
    
    async def get_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get information about all tasks.
        
        Args:
            status: Optional status to filter tasks by.
            
        Returns:
            A list of dictionaries containing information about tasks.
        """
        if status:
            return [task.copy() for task in self.tasks.values() if task['status'] == status]
        else:
            return [task.copy() for task in self.tasks.values()]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            True if the task was cancelled, False otherwise.
        """
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return False
        
        # Check if the task can be cancelled
        task = self.tasks[task_id]
        
        if task['status'] not in ['pending', 'processing']:
            logger.warning(f"Task {task_id} cannot be cancelled (status: {task['status']})")
            return False
        
        # Update the task status
        task['status'] = 'cancelled'
        task['updated_at'] = time.time()
        
        logger.info(f"Cancelled task {task_id}")
        return True
    
    async def register_task_handler(self, task_type: str, handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]) -> None:
        """Register a handler for a specific task type.
        
        Args:
            task_type: The type of task to handle.
            handler: The handler function to call when a task of this type is processed.
        """
        self.task_handlers[task_type] = handler
        
        logger.info(f"Registered handler for task type '{task_type}'")
    
    async def unregister_task_handler(self, task_type: str) -> None:
        """Unregister a handler for a specific task type.
        
        Args:
            task_type: The type of task to stop handling.
        """
        if task_type in self.task_handlers:
            del self.task_handlers[task_type]
            
            logger.info(f"Unregistered handler for task type '{task_type}'")
    
    async def _worker(self) -> None:
        """Worker task for processing tasks from the queue."""
        while self.is_running:
            try:
                # Get a task from the queue
                task = await self.task_queue.get()
                
                # Process the task
                await self._process_task(task)
                
                # Mark the task as processed
                self.task_queue.task_done()
            except asyncio.CancelledError:
                logger.info("Worker task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in worker task: {e}")
    
    async def _process_task(self, task: Dict[str, Any]) -> None:
        """Process a task.
        
        Args:
            task: The task to process.
        """
        task_id = task['id']
        task_type = task['type']
        
        logger.info(f"Processing task {task_id} of type '{task_type}'")
        
        # Update the task status
        task['status'] = 'processing'
        task['updated_at'] = time.time()
        
        try:
            # Get the task handler
            handler = self.task_handlers.get(task_type)
            
            if not handler:
                logger.warning(f"No handler for task type '{task_type}'")
                task['status'] = 'failed'
                task['error'] = f"No handler for task type '{task_type}'"
                return
            
            # Call the task handler
            result = await handler(task)
            
            # Update the task with the result
            task['result'] = result
            task['status'] = 'completed'
            task['updated_at'] = time.time()
            
            logger.info(f"Completed task {task_id}")
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            
            # Update the task status
            task['status'] = 'failed'
            task['error'] = str(e)
            task['updated_at'] = time.time()
    
    async def _handle_generate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a generate task.
        
        Args:
            task: The task to handle.
            
        Returns:
            The task result.
        """
        params = task.get('params', {})
        prompt = params.get('prompt')
        model_name = params.get('model_name')
        
        if not prompt:
            raise ValueError("No prompt provided for generate task")
        
        # This is a placeholder for a real implementation
        # In a real implementation, this would use a model to generate a response
        
        return {
            'generated_text': f"Generated text for prompt: {prompt}",
            'model_name': model_name,
            'timestamp': time.time(),
        }
    
    async def _handle_analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an analyze task.
        
        Args:
            task: The task to handle.
            
        Returns:
            The task result.
        """
        params = task.get('params', {})
        text = params.get('text')
        analysis_type = params.get('analysis_type', 'sentiment')
        
        if not text:
            raise ValueError("No text provided for analyze task")
        
        # This is a placeholder for a real implementation
        # In a real implementation, this would use a model to analyze the text
        
        return {
            'analysis_type': analysis_type,
            'analysis': {
                'sentiment': 'positive',
                'confidence': 0.85,
            },
            'timestamp': time.time(),
        }
    
    async def _handle_search_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a search task.
        
        Args:
            task: The task to handle.
            
        Returns:
            The task result.
        """
        params = task.get('params', {})
        query = params.get('query')
        
        if not query:
            raise ValueError("No query provided for search task")
        
        # This is a placeholder for a real implementation
        # In a real implementation, this would use a search engine or database
        
        return {
            'query': query,
            'results': [
                {
                    'title': 'Search Result 1',
                    'url': 'https://example.com/result1',
                    'snippet': 'This is a snippet from the first search result...',
                },
                {
                    'title': 'Search Result 2',
                    'url': 'https://example.com/result2',
                    'snippet': 'This is a snippet from the second search result...',
                },
            ],
            'timestamp': time.time(),
        }
    
    async def _handle_swarm_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a swarm task.
        
        Args:
            task: The task to handle.
            
        Returns:
            The task result.
        """
        params = task.get('params', {})
        swarm_id = params.get('swarm_id')
        swarm_task = params.get('swarm_task')
        
        if not swarm_id:
            raise ValueError("No swarm ID provided for swarm task")
        
        if not swarm_task:
            raise ValueError("No swarm task provided for swarm task")
        
        # Assign the task to the swarm
        result = await swarm_orchestrator.assign_task_to_swarm(swarm_task, swarm_id)
        
        if not result:
            raise ValueError(f"Failed to assign task to swarm {swarm_id}")
        
        return {
            'swarm_id': swarm_id,
            'task_id': swarm_task['id'],
            'success': True,
            'timestamp': time.time(),
        }
    
    async def _handle_tool_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool task.
        
        Args:
            task: The task to handle.
            
        Returns:
            The task result.
        """
        params = task.get('params', {})
        tool_type = params.get('tool_type')
        operation = params.get('operation')
        operation_params = params.get('operation_params', {})
        
        if not tool_type:
            raise ValueError("No tool type provided for tool task")
        
        if not operation:
            raise ValueError("No operation provided for tool task")
        
        # This is a placeholder for a real implementation
        # In a real implementation, this would use a tool agent to perform the operation
        
        return {
            'tool_type': tool_type,
            'operation': operation,
            'result': {
                'success': True,
                'message': f"Performed {operation} operation with {tool_type} tool",
            },
            'timestamp': time.time(),
        }


# Create a singleton instance
task_manager = TaskManager()
