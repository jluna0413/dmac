"""
WebArena Manager for DMac.

This module provides integration with WebArena for agent evaluation.
"""

import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors, ProcessError
from models.ollama_manager import ollama_manager
from security.secure_process_ops import secure_process_ops

logger = get_logger('dmac.webarena.webarena_manager')


class WebArenaManager:
    """Manager for WebArena integration."""
    
    def __init__(self):
        """Initialize the WebArena manager."""
        # Load configuration
        self.enabled = config.get('webarena.enabled', True)
        self.webarena_dir = Path(config.get('webarena.dir', 'external/webarena'))
        self.data_dir = Path(config.get('webarena.data_dir', 'data/webarena'))
        self.results_dir = self.data_dir / 'results'
        self.logs_dir = self.data_dir / 'logs'
        self.max_concurrent_runs = config.get('webarena.max_concurrent_runs', 2)
        self.default_timeout = config.get('webarena.default_timeout', 3600)  # 1 hour
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize run tracking
        self.runs = {}
        self.active_runs = set()
        self.next_run_id = 1
        
        # Initialize run monitoring task
        self.monitor_task = None
        self.is_monitoring = False
        
        logger.info("WebArena manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the WebArena manager.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            logger.info("WebArena integration is disabled")
            return True
        
        try:
            # Check if WebArena is installed
            if not self._is_webarena_installed():
                logger.warning("WebArena is not installed")
                return False
            
            # Start the run monitoring task
            self.is_monitoring = True
            self.monitor_task = asyncio.create_task(self._monitor_runs())
            
            logger.info("WebArena manager initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing WebArena manager: {e}")
            return False
    
    @handle_async_errors(default_message="Error running WebArena experiment")
    async def run_experiment(self, task_name: str, model_name: str, 
                           num_episodes: int = 1, timeout: Optional[int] = None) -> Tuple[str, Dict[str, Any]]:
        """Run a WebArena experiment.
        
        Args:
            task_name: The name of the task to run.
            model_name: The name of the model to use.
            num_episodes: The number of episodes to run.
            timeout: Optional timeout for the experiment in seconds.
            
        Returns:
            A tuple of (run_id, run_info).
        """
        if not self.enabled:
            logger.warning("WebArena integration is disabled")
            raise ProcessError("WebArena integration is disabled")
        
        # Check if WebArena is installed
        if not self._is_webarena_installed():
            logger.warning("WebArena is not installed")
            raise ProcessError("WebArena is not installed")
        
        # Check if we've reached the maximum number of concurrent runs
        if len(self.active_runs) >= self.max_concurrent_runs:
            logger.warning(f"Maximum number of concurrent runs reached: {self.max_concurrent_runs}")
            raise ProcessError(f"Maximum number of concurrent runs reached: {self.max_concurrent_runs}")
        
        # Set the timeout
        if timeout is None:
            timeout = self.default_timeout
        
        # Generate a run ID
        run_id = f"run_{self.next_run_id}"
        self.next_run_id += 1
        
        # Create run directories
        run_dir = self.results_dir / run_id
        os.makedirs(run_dir, exist_ok=True)
        
        # Create the run configuration
        run_config = {
            'task_name': task_name,
            'model_name': model_name,
            'num_episodes': num_episodes,
            'timeout': timeout,
        }
        
        # Save the run configuration
        config_path = run_dir / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(run_config, f, indent=2)
        
        # Create the command
        command = self._create_command(run_id, task_name, model_name, num_episodes)
        
        # Start the run
        success, message, process_info = await secure_process_ops.run_process(
            command=command,
            cwd=str(self.webarena_dir),
            timeout=timeout
        )
        
        if not success:
            logger.error(f"Error starting WebArena run: {message}")
            raise ProcessError(f"Error starting WebArena run: {message}")
        
        # Store the run information
        run_info = {
            'id': run_id,
            'task_name': task_name,
            'model_name': model_name,
            'num_episodes': num_episodes,
            'timeout': timeout,
            'start_time': time.time(),
            'process_id': process_info['id'],
            'status': 'running',
            'results': None,
        }
        
        self.runs[run_id] = run_info
        self.active_runs.add(run_id)
        
        logger.info(f"Started WebArena run {run_id} for task '{task_name}' with model '{model_name}'")
        return run_id, run_info
    
    @handle_async_errors(default_message="Error getting WebArena run status")
    async def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """Get the status of a WebArena run.
        
        Args:
            run_id: The ID of the run to get the status of.
            
        Returns:
            A dictionary containing the run status.
        """
        if not self.enabled:
            logger.warning("WebArena integration is disabled")
            raise ProcessError("WebArena integration is disabled")
        
        # Check if the run exists
        if run_id not in self.runs:
            logger.warning(f"WebArena run {run_id} not found")
            raise ProcessError(f"WebArena run {run_id} not found")
        
        # Get the run information
        run_info = self.runs[run_id]
        
        # If the run is still active, get the process status
        if run_id in self.active_runs:
            process_id = run_info['process_id']
            success, message, process_info = await secure_process_ops.get_process_info(process_id)
            
            if success:
                # Update the run status based on the process status
                if process_info['completed']:
                    # Process has completed, update the run status
                    run_info['status'] = 'completed' if process_info['returncode'] == 0 else 'failed'
                    run_info['end_time'] = time.time()
                    run_info['duration'] = run_info['end_time'] - run_info['start_time']
                    run_info['returncode'] = process_info['returncode']
                    
                    # Parse the results
                    await self._parse_results(run_id)
                    
                    # Remove the run from active runs
                    self.active_runs.remove(run_id)
                else:
                    # Process is still running
                    run_info['status'] = 'running'
            else:
                # Error getting process info
                logger.warning(f"Error getting process info for WebArena run {run_id}: {message}")
                run_info['status'] = 'unknown'
        
        return run_info
    
    @handle_async_errors(default_message="Error stopping WebArena run")
    async def stop_run(self, run_id: str) -> bool:
        """Stop a WebArena run.
        
        Args:
            run_id: The ID of the run to stop.
            
        Returns:
            True if the run was stopped, False otherwise.
        """
        if not self.enabled:
            logger.warning("WebArena integration is disabled")
            raise ProcessError("WebArena integration is disabled")
        
        # Check if the run exists
        if run_id not in self.runs:
            logger.warning(f"WebArena run {run_id} not found")
            raise ProcessError(f"WebArena run {run_id} not found")
        
        # Check if the run is active
        if run_id not in self.active_runs:
            logger.warning(f"WebArena run {run_id} is not active")
            return False
        
        # Get the run information
        run_info = self.runs[run_id]
        process_id = run_info['process_id']
        
        # Stop the process
        success, message = await secure_process_ops.kill_process(process_id)
        
        if not success:
            logger.warning(f"Error stopping WebArena run {run_id}: {message}")
            return False
        
        # Update the run status
        run_info['status'] = 'stopped'
        run_info['end_time'] = time.time()
        run_info['duration'] = run_info['end_time'] - run_info['start_time']
        
        # Remove the run from active runs
        self.active_runs.remove(run_id)
        
        logger.info(f"Stopped WebArena run {run_id}")
        return True
    
    @handle_async_errors(default_message="Error getting WebArena run results")
    async def get_run_results(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the results of a WebArena run.
        
        Args:
            run_id: The ID of the run to get the results of.
            
        Returns:
            A dictionary containing the run results, or None if the run is not completed.
        """
        if not self.enabled:
            logger.warning("WebArena integration is disabled")
            raise ProcessError("WebArena integration is disabled")
        
        # Check if the run exists
        if run_id not in self.runs:
            logger.warning(f"WebArena run {run_id} not found")
            raise ProcessError(f"WebArena run {run_id} not found")
        
        # Get the run information
        run_info = self.runs[run_id]
        
        # Check if the run is completed
        if run_info['status'] != 'completed':
            logger.warning(f"WebArena run {run_id} is not completed")
            return None
        
        # Return the results
        return run_info['results']
    
    @handle_async_errors(default_message="Error listing WebArena runs")
    async def list_runs(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List WebArena runs.
        
        Args:
            status: Optional status to filter runs by.
            
        Returns:
            A list of dictionaries containing run information.
        """
        if not self.enabled:
            logger.warning("WebArena integration is disabled")
            return []
        
        # Get all runs
        runs = list(self.runs.values())
        
        # Filter by status if specified
        if status:
            runs = [run for run in runs if run['status'] == status]
        
        # Sort by start time (newest first)
        runs.sort(key=lambda x: x['start_time'], reverse=True)
        
        return runs
    
    @handle_async_errors(default_message="Error getting WebArena tasks")
    async def get_available_tasks(self) -> List[Dict[str, Any]]:
        """Get the available WebArena tasks.
        
        Returns:
            A list of dictionaries containing task information.
        """
        if not self.enabled:
            logger.warning("WebArena integration is disabled")
            return []
        
        # Check if WebArena is installed
        if not self._is_webarena_installed():
            logger.warning("WebArena is not installed")
            return []
        
        # Get the tasks from the WebArena configuration
        tasks_file = self.webarena_dir / 'config' / 'tasks.json'
        
        if not tasks_file.exists():
            logger.warning(f"WebArena tasks file not found: {tasks_file}")
            return []
        
        try:
            with open(tasks_file, 'r') as f:
                tasks_data = json.load(f)
            
            # Extract task information
            tasks = []
            for task_id, task_info in tasks_data.items():
                task = {
                    'id': task_id,
                    'name': task_info.get('name', task_id),
                    'description': task_info.get('description', ''),
                    'website': task_info.get('website', ''),
                    'difficulty': task_info.get('difficulty', 'unknown'),
                }
                tasks.append(task)
            
            # Sort by ID
            tasks.sort(key=lambda x: x['id'])
            
            return tasks
        except Exception as e:
            logger.exception(f"Error getting WebArena tasks: {e}")
            return []
    
    async def cleanup(self) -> None:
        """Clean up resources used by the WebArena manager."""
        if not self.enabled:
            logger.debug("WebArena integration is disabled")
            return
        
        logger.info("Cleaning up WebArena manager")
        
        # Stop the run monitoring task
        self.is_monitoring = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            self.monitor_task = None
        
        # Stop all active runs
        for run_id in list(self.active_runs):
            await self.stop_run(run_id)
        
        logger.info("WebArena manager cleaned up")
    
    def _is_webarena_installed(self) -> bool:
        """Check if WebArena is installed.
        
        Returns:
            True if WebArena is installed, False otherwise.
        """
        # Check if the WebArena directory exists
        if not self.webarena_dir.exists():
            return False
        
        # Check if the WebArena main script exists
        main_script = self.webarena_dir / 'run.py'
        if not main_script.exists():
            return False
        
        return True
    
    def _create_command(self, run_id: str, task_name: str, model_name: str, num_episodes: int) -> str:
        """Create the command to run a WebArena experiment.
        
        Args:
            run_id: The ID of the run.
            task_name: The name of the task to run.
            model_name: The name of the model to use.
            num_episodes: The number of episodes to run.
            
        Returns:
            The command to run.
        """
        # Create the results directory path
        results_dir = self.results_dir / run_id
        
        # Create the command
        command = f"python run.py --task {task_name} --model ollama --model_name {model_name} --num_episodes {num_episodes} --results_dir {results_dir} --log_dir {self.logs_dir}"
        
        return command
    
    async def _parse_results(self, run_id: str) -> None:
        """Parse the results of a WebArena run.
        
        Args:
            run_id: The ID of the run to parse the results of.
        """
        # Get the run information
        run_info = self.runs[run_id]
        
        # Get the results directory
        results_dir = self.results_dir / run_id
        
        # Check if the results file exists
        results_file = results_dir / 'results.json'
        
        if not results_file.exists():
            logger.warning(f"Results file not found for WebArena run {run_id}: {results_file}")
            run_info['results'] = {'error': 'Results file not found'}
            return
        
        try:
            # Parse the results file
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            # Store the results
            run_info['results'] = results
            
            logger.info(f"Parsed results for WebArena run {run_id}")
        except Exception as e:
            logger.exception(f"Error parsing results for WebArena run {run_id}: {e}")
            run_info['results'] = {'error': f"Error parsing results: {e}"}
    
    async def _monitor_runs(self) -> None:
        """Monitor WebArena runs for timeouts and completion."""
        while self.is_monitoring:
            try:
                # Check each active run
                for run_id in list(self.active_runs):
                    # Get the run status
                    await self.get_run_status(run_id)
                
                # Sleep for a short time
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info("WebArena run monitoring cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in WebArena run monitoring: {e}")
                await asyncio.sleep(30)  # Wait for 30 seconds before trying again


# Create a singleton instance
webarena_manager = WebArenaManager()
