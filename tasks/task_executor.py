"""
Task Executor for DMac.

This module provides functionality for executing tasks with different models.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
import uuid

from database import db_manager
from integrations import ollama_client, web_scraper
from tasks.task_types import get_task_by_id, get_all_tasks

logger = logging.getLogger('dmac.tasks.task_executor')

class TaskExecutor:
    """Executor for running tasks with different models."""
    
    def __init__(self):
        """Initialize the task executor."""
        logger.info("Task executor initialized")
    
    async def execute_task(self, task_id: str, model: str) -> Dict[str, Any]:
        """Execute a task with a specific model.
        
        Args:
            task_id: The ID of the task to execute.
            model: The model to use for execution.
            
        Returns:
            A dictionary containing the task results.
        """
        # Get the task
        task = get_task_by_id(task_id)
        
        if not task:
            logger.warning(f"Task {task_id} not found")
            return {
                'task_id': task_id,
                'model': model,
                'error': f"Task {task_id} not found",
                'timestamp': time.time()
            }
        
        logger.info(f"Executing task {task_id} with model {model}")
        
        # Execute the task based on its type
        if task['type'] == 'web_scraping':
            return await self._execute_web_scraping_task(task, model)
        elif task['type'] == 'text_analysis':
            return await self._execute_text_analysis_task(task, model)
        elif task['type'] == 'code_generation':
            return await self._execute_code_generation_task(task, model)
        elif task['type'] == 'reasoning':
            return await self._execute_reasoning_task(task, model)
        elif task['type'] == 'conversation':
            return await self._execute_conversation_task(task, model)
        else:
            logger.warning(f"Unknown task type: {task['type']}")
            return {
                'task_id': task_id,
                'model': model,
                'error': f"Unknown task type: {task['type']}",
                'timestamp': time.time()
            }
    
    async def execute_all_tasks_with_model(self, model: str) -> List[Dict[str, Any]]:
        """Execute all tasks with a specific model.
        
        Args:
            model: The model to use for execution.
            
        Returns:
            A list of dictionaries containing the task results.
        """
        logger.info(f"Executing all tasks with model {model}")
        
        results = []
        tasks = get_all_tasks()
        
        for task in tasks:
            try:
                result = await self.execute_task(task['id'], model)
                results.append(result)
                
                # Store the result in the database
                run_id = await self._store_run_result(task['id'], model, result)
                
                if run_id:
                    logger.info(f"Stored run result for task {task['id']} with model {model}, run ID: {run_id}")
                else:
                    logger.warning(f"Failed to store run result for task {task['id']} with model {model}")
                
                # Add a short delay to avoid rate limiting
                await asyncio.sleep(2)
            except Exception as e:
                logger.exception(f"Error executing task {task['id']} with model {model}: {e}")
                results.append({
                    'task_id': task['id'],
                    'model': model,
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        logger.info(f"Executed {len(results)} tasks with model {model}")
        return results
    
    async def execute_task_with_all_models(self, task_id: str, models: List[str]) -> List[Dict[str, Any]]:
        """Execute a task with all specified models.
        
        Args:
            task_id: The ID of the task to execute.
            models: The list of models to use for execution.
            
        Returns:
            A list of dictionaries containing the task results.
        """
        logger.info(f"Executing task {task_id} with {len(models)} models")
        
        results = []
        
        for model in models:
            try:
                result = await self.execute_task(task_id, model)
                results.append(result)
                
                # Store the result in the database
                run_id = await self._store_run_result(task_id, model, result)
                
                if run_id:
                    logger.info(f"Stored run result for task {task_id} with model {model}, run ID: {run_id}")
                else:
                    logger.warning(f"Failed to store run result for task {task_id} with model {model}")
                
                # Add a short delay to avoid rate limiting
                await asyncio.sleep(2)
            except Exception as e:
                logger.exception(f"Error executing task {task_id} with model {model}: {e}")
                results.append({
                    'task_id': task_id,
                    'model': model,
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        logger.info(f"Executed task {task_id} with {len(models)} models")
        return results
    
    async def _execute_web_scraping_task(self, task: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Execute a web scraping task.
        
        Args:
            task: The task to execute.
            model: The model to use for execution.
            
        Returns:
            A dictionary containing the task results.
        """
        logger.info(f"Executing web scraping task {task['id']} with model {model}")
        
        # Get the URL to scrape
        url = task.get('url')
        
        if not url:
            logger.warning(f"No URL specified for web scraping task {task['id']}")
            return {
                'task_id': task['id'],
                'model': model,
                'error': "No URL specified",
                'timestamp': time.time()
            }
        
        # Scrape and summarize the URL
        result = await web_scraper.scrape_and_summarize(url, model)
        
        # Add task metadata
        result['task_id'] = task['id']
        result['task_name'] = task['name']
        result['task_type'] = task['type']
        
        logger.info(f"Completed web scraping task {task['id']} with model {model}")
        return result
    
    async def _execute_text_analysis_task(self, task: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Execute a text analysis task.
        
        Args:
            task: The task to execute.
            model: The model to use for execution.
            
        Returns:
            A dictionary containing the task results.
        """
        logger.info(f"Executing text analysis task {task['id']} with model {model}")
        
        # For now, return a mock result
        # In a real implementation, we would load the data and analyze it
        
        return {
            'task_id': task['id'],
            'task_name': task['name'],
            'task_type': task['type'],
            'model': model,
            'result': f"Mock result for text analysis task {task['id']} with model {model}",
            'timestamp': time.time()
        }
    
    async def _execute_code_generation_task(self, task: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Execute a code generation task.
        
        Args:
            task: The task to execute.
            model: The model to use for execution.
            
        Returns:
            A dictionary containing the task results.
        """
        logger.info(f"Executing code generation task {task['id']} with model {model}")
        
        # For now, return a mock result
        # In a real implementation, we would generate code based on the task
        
        return {
            'task_id': task['id'],
            'task_name': task['name'],
            'task_type': task['type'],
            'model': model,
            'result': f"Mock result for code generation task {task['id']} with model {model}",
            'timestamp': time.time()
        }
    
    async def _execute_reasoning_task(self, task: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Execute a reasoning task.
        
        Args:
            task: The task to execute.
            model: The model to use for execution.
            
        Returns:
            A dictionary containing the task results.
        """
        logger.info(f"Executing reasoning task {task['id']} with model {model}")
        
        # For now, return a mock result
        # In a real implementation, we would solve reasoning problems
        
        return {
            'task_id': task['id'],
            'task_name': task['name'],
            'task_type': task['type'],
            'model': model,
            'result': f"Mock result for reasoning task {task['id']} with model {model}",
            'timestamp': time.time()
        }
    
    async def _execute_conversation_task(self, task: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Execute a conversation task.
        
        Args:
            task: The task to execute.
            model: The model to use for execution.
            
        Returns:
            A dictionary containing the task results.
        """
        logger.info(f"Executing conversation task {task['id']} with model {model}")
        
        # For now, return a mock result
        # In a real implementation, we would simulate conversations
        
        return {
            'task_id': task['id'],
            'task_name': task['name'],
            'task_type': task['type'],
            'model': model,
            'result': f"Mock result for conversation task {task['id']} with model {model}",
            'timestamp': time.time()
        }
    
    async def _store_run_result(self, task_id: str, model: str, result: Dict[str, Any]) -> Optional[str]:
        """Store a run result in the database.
        
        Args:
            task_id: The ID of the task.
            model: The model used for execution.
            result: The task result.
            
        Returns:
            The ID of the run, or None if storage failed.
        """
        try:
            # Check if the task exists in the database
            db_task = await db_manager.get_task(task_id)
            
            # If the task doesn't exist, create it
            if not db_task:
                task = get_task_by_id(task_id)
                
                if not task:
                    logger.warning(f"Task {task_id} not found")
                    return None
                
                # Create the task in the database
                db_task_id = await db_manager.create_task(
                    name=task['name'],
                    description=task['description'],
                    task_type=task['type'],
                    status='completed',
                    data=task
                )
                
                if not db_task_id:
                    logger.warning(f"Failed to create task {task_id} in database")
                    return None
                
                # Use the new task ID
                task_id = db_task_id
            else:
                # Use the existing task ID
                task_id = db_task['id']
            
            # Create a run in the database
            run_id = await db_manager.create_run(
                task_id=task_id,
                model=model,
                status='completed',
                result=json.dumps(result) if isinstance(result, dict) else str(result),
                data=result
            )
            
            return run_id
        except Exception as e:
            logger.exception(f"Error storing run result: {e}")
            return None


# Create a singleton instance
task_executor = TaskExecutor()
