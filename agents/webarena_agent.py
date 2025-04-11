"""
WebArena Agent for DMac.

This module provides an agent that can interact with WebArena.
"""

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors, AgentError
from agents.base_agent import BaseAgent
from webarena.webarena_manager import webarena_manager
from webarena.ollama_integration import webarena_ollama_integration
from webarena.visualization import webarena_visualization

logger = get_logger('dmac.agents.webarena_agent')


class WebArenaAgent(BaseAgent):
    """Agent for interacting with WebArena."""
    
    def __init__(self, agent_id: str, name: str):
        """Initialize the WebArena agent.
        
        Args:
            agent_id: The ID of the agent.
            name: The name of the agent.
        """
        super().__init__(agent_id, name)
        self.agent_id = agent_id
        
        # Load configuration
        self.default_model = config.get('agents.webarena.default_model', 'llama2')
        self.default_task = config.get('agents.webarena.default_task', 'shopping')
        self.default_num_episodes = config.get('agents.webarena.default_num_episodes', 1)
        self.default_timeout = config.get('agents.webarena.default_timeout', 3600)
        
        # Initialize state
        self.current_run_id = None
        self.current_task = None
        self.current_model = None
        
        logger.info(f"WebArena agent {agent_id} ({name}) initialized")
    
    async def initialize(self) -> bool:
        """Initialize the WebArena agent.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            # Check if WebArena is available
            if not await self._is_webarena_available():
                logger.warning(f"WebArena is not available for agent {self.agent_id}")
                return False
            
            logger.info(f"WebArena agent {self.agent_id} initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing WebArena agent {self.agent_id}: {e}")
            return False
    
    @handle_async_errors(default_message="Error processing message")
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message.
        
        Args:
            message: The message to process.
            
        Returns:
            The response message.
        """
        # Get the message type
        message_type = message.get('type', 'unknown')
        
        # Process the message based on its type
        if message_type == 'run_experiment':
            return await self._handle_run_experiment(message)
        elif message_type == 'get_run_status':
            return await self._handle_get_run_status(message)
        elif message_type == 'stop_run':
            return await self._handle_stop_run(message)
        elif message_type == 'get_run_results':
            return await self._handle_get_run_results(message)
        elif message_type == 'list_runs':
            return await self._handle_list_runs(message)
        elif message_type == 'get_available_tasks':
            return await self._handle_get_available_tasks(message)
        elif message_type == 'get_available_models':
            return await self._handle_get_available_models(message)
        elif message_type == 'generate_visualization':
            return await self._handle_generate_visualization(message)
        elif message_type == 'help':
            return await self._handle_help(message)
        else:
            return {
                'type': 'error',
                'error': f"Unknown message type: {message_type}",
                'help': "Try sending a message with type 'help' to see available commands.",
            }
    
    async def cleanup(self) -> None:
        """Clean up resources used by the WebArena agent."""
        logger.info(f"Cleaning up WebArena agent {self.agent_id}")
        
        # Stop any active run
        if self.current_run_id:
            try:
                await webarena_manager.stop_run(self.current_run_id)
                self.current_run_id = None
                self.current_task = None
                self.current_model = None
            except Exception as e:
                logger.exception(f"Error stopping run {self.current_run_id}: {e}")
        
        logger.info(f"WebArena agent {self.agent_id} cleaned up")
    
    async def _is_webarena_available(self) -> bool:
        """Check if WebArena is available.
        
        Returns:
            True if WebArena is available, False otherwise.
        """
        try:
            # Check if the WebArena manager is initialized
            if not webarena_manager.enabled:
                return False
            
            # Check if WebArena is installed
            if not webarena_manager._is_webarena_installed():
                return False
            
            return True
        except Exception:
            return False
    
    async def _handle_run_experiment(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a run_experiment message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        # Get the message parameters
        task_name = message.get('task_name', self.default_task)
        model_name = message.get('model_name', self.default_model)
        num_episodes = message.get('num_episodes', self.default_num_episodes)
        timeout = message.get('timeout', self.default_timeout)
        
        # Run the experiment
        try:
            run_id, run_info = await webarena_manager.run_experiment(
                task_name=task_name,
                model_name=model_name,
                num_episodes=num_episodes,
                timeout=timeout
            )
            
            # Store the current run information
            self.current_run_id = run_id
            self.current_task = task_name
            self.current_model = model_name
            
            return {
                'type': 'run_experiment_response',
                'success': True,
                'run_id': run_id,
                'run_info': run_info,
                'message': f"Started WebArena run {run_id} for task '{task_name}' with model '{model_name}'",
            }
        except Exception as e:
            logger.exception(f"Error running WebArena experiment: {e}")
            return {
                'type': 'run_experiment_response',
                'success': False,
                'error': str(e),
                'message': f"Error running WebArena experiment: {e}",
            }
    
    async def _handle_get_run_status(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a get_run_status message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        # Get the message parameters
        run_id = message.get('run_id', self.current_run_id)
        
        if not run_id:
            return {
                'type': 'get_run_status_response',
                'success': False,
                'error': "No run ID specified and no current run",
                'message': "Please specify a run ID or start a run first.",
            }
        
        # Get the run status
        try:
            run_status = await webarena_manager.get_run_status(run_id)
            
            return {
                'type': 'get_run_status_response',
                'success': True,
                'run_id': run_id,
                'run_status': run_status,
                'message': f"Status of WebArena run {run_id}: {run_status['status']}",
            }
        except Exception as e:
            logger.exception(f"Error getting WebArena run status: {e}")
            return {
                'type': 'get_run_status_response',
                'success': False,
                'error': str(e),
                'message': f"Error getting WebArena run status: {e}",
            }
    
    async def _handle_stop_run(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a stop_run message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        # Get the message parameters
        run_id = message.get('run_id', self.current_run_id)
        
        if not run_id:
            return {
                'type': 'stop_run_response',
                'success': False,
                'error': "No run ID specified and no current run",
                'message': "Please specify a run ID or start a run first.",
            }
        
        # Stop the run
        try:
            success = await webarena_manager.stop_run(run_id)
            
            # Clear the current run if it was stopped
            if success and run_id == self.current_run_id:
                self.current_run_id = None
                self.current_task = None
                self.current_model = None
            
            return {
                'type': 'stop_run_response',
                'success': success,
                'run_id': run_id,
                'message': f"WebArena run {run_id} stopped successfully" if success else f"Failed to stop WebArena run {run_id}",
            }
        except Exception as e:
            logger.exception(f"Error stopping WebArena run: {e}")
            return {
                'type': 'stop_run_response',
                'success': False,
                'error': str(e),
                'message': f"Error stopping WebArena run: {e}",
            }
    
    async def _handle_get_run_results(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a get_run_results message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        # Get the message parameters
        run_id = message.get('run_id', self.current_run_id)
        
        if not run_id:
            return {
                'type': 'get_run_results_response',
                'success': False,
                'error': "No run ID specified and no current run",
                'message': "Please specify a run ID or start a run first.",
            }
        
        # Get the run results
        try:
            results = await webarena_manager.get_run_results(run_id)
            
            if results is None:
                return {
                    'type': 'get_run_results_response',
                    'success': False,
                    'run_id': run_id,
                    'error': "Run is not completed",
                    'message': f"WebArena run {run_id} is not completed yet.",
                }
            
            return {
                'type': 'get_run_results_response',
                'success': True,
                'run_id': run_id,
                'results': results,
                'message': f"Results for WebArena run {run_id}",
            }
        except Exception as e:
            logger.exception(f"Error getting WebArena run results: {e}")
            return {
                'type': 'get_run_results_response',
                'success': False,
                'error': str(e),
                'message': f"Error getting WebArena run results: {e}",
            }
    
    async def _handle_list_runs(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a list_runs message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        # Get the message parameters
        status = message.get('status')
        
        # List the runs
        try:
            runs = await webarena_manager.list_runs(status)
            
            return {
                'type': 'list_runs_response',
                'success': True,
                'runs': runs,
                'message': f"Listed {len(runs)} WebArena runs" + (f" with status '{status}'" if status else ""),
            }
        except Exception as e:
            logger.exception(f"Error listing WebArena runs: {e}")
            return {
                'type': 'list_runs_response',
                'success': False,
                'error': str(e),
                'message': f"Error listing WebArena runs: {e}",
            }
    
    async def _handle_get_available_tasks(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a get_available_tasks message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        # Get the available tasks
        try:
            tasks = await webarena_manager.get_available_tasks()
            
            return {
                'type': 'get_available_tasks_response',
                'success': True,
                'tasks': tasks,
                'message': f"Listed {len(tasks)} available WebArena tasks",
            }
        except Exception as e:
            logger.exception(f"Error getting available WebArena tasks: {e}")
            return {
                'type': 'get_available_tasks_response',
                'success': False,
                'error': str(e),
                'message': f"Error getting available WebArena tasks: {e}",
            }
    
    async def _handle_get_available_models(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a get_available_models message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        # Get the available models
        try:
            models = await webarena_ollama_integration.get_available_models()
            
            return {
                'type': 'get_available_models_response',
                'success': True,
                'models': models,
                'message': f"Listed {len(models)} available WebArena models",
            }
        except Exception as e:
            logger.exception(f"Error getting available WebArena models: {e}")
            return {
                'type': 'get_available_models_response',
                'success': False,
                'error': str(e),
                'message': f"Error getting available WebArena models: {e}",
            }
    
    async def _handle_generate_visualization(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a generate_visualization message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        # Get the message parameters
        visualization_type = message.get('visualization_type')
        run_ids = message.get('run_ids', [])
        task_name = message.get('task_name')
        model_names = message.get('model_names', [])
        
        if not visualization_type:
            return {
                'type': 'generate_visualization_response',
                'success': False,
                'error': "No visualization type specified",
                'message': "Please specify a visualization type.",
            }
        
        # Generate the visualization
        try:
            visualization_path = None
            
            if visualization_type == 'success_rate':
                if not run_ids:
                    return {
                        'type': 'generate_visualization_response',
                        'success': False,
                        'error': "No run IDs specified",
                        'message': "Please specify run IDs for the success rate visualization.",
                    }
                
                visualization_path = await webarena_visualization.generate_success_rate_visualization(run_ids)
            elif visualization_type == 'completion_time':
                if not run_ids:
                    return {
                        'type': 'generate_visualization_response',
                        'success': False,
                        'error': "No run IDs specified",
                        'message': "Please specify run IDs for the completion time visualization.",
                    }
                
                visualization_path = await webarena_visualization.generate_completion_time_visualization(run_ids)
                visualization_path = await webarena_visualization.generate_completion_time_visualization(run_ids)
            elif visualization_type == 'action_count':
                if not run_ids:
                    return {
                        'type': 'generate_visualization_response',
                        'success': False,
                        'error': "No run IDs specified",
                        'message': "Please specify run IDs for the action count visualization.",
                    }
                
                visualization_path = await webarena_visualization.generate_action_count_visualization(run_ids)
            elif visualization_type == 'model_comparison':
                if not task_name:
                    return {
                        'type': 'generate_visualization_response',
                        'success': False,
                        'error': "No task name specified",
                        'message': "Please specify a task name for the model comparison visualization.",
                    }
                
                if not model_names:
                    return {
                        'type': 'generate_visualization_response',
                        'success': False,
                        'error': "No model names specified",
                        'message': "Please specify model names for the model comparison visualization.",
                    }
                
                visualization_path = await webarena_visualization.generate_model_comparison_visualization(task_name, model_names)
            else:
                return {
                    'type': 'generate_visualization_response',
                    'success': False,
                    'error': f"Unknown visualization type: {visualization_type}",
                    'message': "Please specify a valid visualization type.",
                }
            
            if not visualization_path:
                return {
                    'type': 'generate_visualization_response',
                    'success': False,
                    'error': "Failed to generate visualization",
                    'message': "Failed to generate visualization.",
                }
            
            return {
                'type': 'generate_visualization_response',
                'success': True,
                'visualization_path': visualization_path,
                'message': f"Generated {visualization_type} visualization",
            }
        except Exception as e:
            logger.exception(f"Error generating visualization: {e}")
            return {
                'type': 'generate_visualization_response',
                'success': False,
                'error': str(e),
                'message': f"Error generating visualization: {e}",
            }
    
    async def _handle_help(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a help message.
        
        Args:
            message: The message to handle.
            
        Returns:
            The response message.
        """
        return {
            'type': 'help_response',
            'success': True,
            'commands': [
                {
                    'type': 'run_experiment',
                    'description': 'Run a WebArena experiment',
                    'parameters': {
                        'task_name': 'The name of the task to run',
                        'model_name': 'The name of the model to use',
                        'num_episodes': 'The number of episodes to run',
                        'timeout': 'The timeout for the experiment in seconds',
                    },
                },
                {
                    'type': 'get_run_status',
                    'description': 'Get the status of a WebArena run',
                    'parameters': {
                        'run_id': 'The ID of the run to get the status of',
                    },
                },
                {
                    'type': 'stop_run',
                    'description': 'Stop a WebArena run',
                    'parameters': {
                        'run_id': 'The ID of the run to stop',
                    },
                },
                {
                    'type': 'get_run_results',
                    'description': 'Get the results of a WebArena run',
                    'parameters': {
                        'run_id': 'The ID of the run to get the results of',
                    },
                },
                {
                    'type': 'list_runs',
                    'description': 'List WebArena runs',
                    'parameters': {
                        'status': 'Optional status to filter runs by',
                    },
                },
                {
                    'type': 'get_available_tasks',
                    'description': 'Get the available WebArena tasks',
                    'parameters': {},
                },
                {
                    'type': 'get_available_models',
                    'description': 'Get the available WebArena models',
                    'parameters': {},
                },
                {
                    'type': 'generate_visualization',
                    'description': 'Generate a visualization',
                    'parameters': {
                        'visualization_type': 'The type of visualization to generate (success_rate, completion_time, action_count, model_comparison)',
                        'run_ids': 'The IDs of the runs to include in the visualization (for success_rate, completion_time, action_count)',
                        'task_name': 'The name of the task to compare models on (for model_comparison)',
                        'model_names': 'The names of the models to compare (for model_comparison)',
                    },
                },
                {
                    'type': 'help',
                    'description': 'Get help information',
                    'parameters': {},
                },
            ],
            'message': "Available WebArena agent commands",
        }
