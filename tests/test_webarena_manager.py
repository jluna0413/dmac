"""
Unit tests for the WebArena manager.
"""

import unittest
import asyncio
import os
import shutil
import tempfile
import json
from unittest.mock import patch, MagicMock, AsyncMock

from webarena.webarena_manager import WebArenaManager


class TestWebArenaManager(unittest.TestCase):
    """Test case for the WebArenaManager class."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary directory for the WebArena manager data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a WebArena manager with the temporary directory
        self.webarena_manager = WebArenaManager()
        self.webarena_manager.data_dir = os.path.join(self.temp_dir, 'webarena')
        self.webarena_manager.results_dir = os.path.join(self.webarena_manager.data_dir, 'results')
        self.webarena_manager.logs_dir = os.path.join(self.webarena_manager.data_dir, 'logs')
        
        # Create the directories
        os.makedirs(self.webarena_manager.data_dir, exist_ok=True)
        os.makedirs(self.webarena_manager.results_dir, exist_ok=True)
        os.makedirs(self.webarena_manager.logs_dir, exist_ok=True)
    
    def tearDown(self):
        """Tear down the test case."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    @patch('webarena.webarena_manager.secure_process_ops')
    async def async_test_run_experiment(self, mock_secure_process_ops):
        """Test the run_experiment method."""
        # Mock the run_process method
        mock_secure_process_ops.run_process = AsyncMock(return_value=(
            True,
            "Process started successfully",
            {
                'id': 1,
                'command': 'python run.py --task test_task --model ollama --model_name test_model --num_episodes 1 --results_dir results/run_1 --log_dir logs',
                'cwd': str(self.webarena_manager.webarena_dir),
                'start_time': 1234567890,
                'timeout': 3600,
            }
        ))
        
        # Mock the _is_webarena_installed method
        self.webarena_manager._is_webarena_installed = MagicMock(return_value=True)
        
        # Run an experiment
        run_id, run_info = await self.webarena_manager.run_experiment(
            task_name="test_task",
            model_name="test_model",
            num_episodes=1,
            timeout=3600
        )
        
        # Check that the run ID is correct
        self.assertEqual(run_id, "run_1")
        
        # Check that the run information is correct
        self.assertEqual(run_info['task_name'], "test_task")
        self.assertEqual(run_info['model_name'], "test_model")
        self.assertEqual(run_info['num_episodes'], 1)
        self.assertEqual(run_info['timeout'], 3600)
        self.assertEqual(run_info['process_id'], 1)
        self.assertEqual(run_info['status'], "running")
        
        # Check that the run was added to the runs dictionary
        self.assertIn(run_id, self.webarena_manager.runs)
        
        # Check that the run was added to the active runs set
        self.assertIn(run_id, self.webarena_manager.active_runs)
        
        # Check that the run_process method was called with the correct arguments
        mock_secure_process_ops.run_process.assert_called_once()
        args, kwargs = mock_secure_process_ops.run_process.call_args
        self.assertEqual(kwargs['cwd'], str(self.webarena_manager.webarena_dir))
        self.assertEqual(kwargs['timeout'], 3600)
        
        # Check that the command contains the correct arguments
        command = kwargs['command']
        self.assertIn("--task test_task", command)
        self.assertIn("--model ollama", command)
        self.assertIn("--model_name test_model", command)
        self.assertIn("--num_episodes 1", command)
    
    @patch('webarena.webarena_manager.secure_process_ops')
    async def async_test_get_run_status(self, mock_secure_process_ops):
        """Test the get_run_status method."""
        # Mock the get_process_info method
        mock_secure_process_ops.get_process_info = AsyncMock(return_value=(
            True,
            "Process information retrieved successfully",
            {
                'id': 1,
                'command': 'python run.py --task test_task --model ollama --model_name test_model --num_episodes 1 --results_dir results/run_1 --log_dir logs',
                'cwd': str(self.webarena_manager.webarena_dir),
                'start_time': 1234567890,
                'completed': False,
                'returncode': None,
                'stdout': [],
                'stderr': [],
            }
        ))
        
        # Create a run
        run_id = "run_1"
        self.webarena_manager.runs[run_id] = {
            'id': run_id,
            'task_name': "test_task",
            'model_name': "test_model",
            'num_episodes': 1,
            'timeout': 3600,
            'start_time': 1234567890,
            'process_id': 1,
            'status': "running",
            'results': None,
        }
        self.webarena_manager.active_runs.add(run_id)
        
        # Get the run status
        run_status = await self.webarena_manager.get_run_status(run_id)
        
        # Check that the run status is correct
        self.assertEqual(run_status['id'], run_id)
        self.assertEqual(run_status['task_name'], "test_task")
        self.assertEqual(run_status['model_name'], "test_model")
        self.assertEqual(run_status['num_episodes'], 1)
        self.assertEqual(run_status['timeout'], 3600)
        self.assertEqual(run_status['start_time'], 1234567890)
        self.assertEqual(run_status['process_id'], 1)
        self.assertEqual(run_status['status'], "running")
        
        # Check that the get_process_info method was called with the correct arguments
        mock_secure_process_ops.get_process_info.assert_called_once_with(1)
        
        # Now test with a completed process
        mock_secure_process_ops.get_process_info.reset_mock()
        mock_secure_process_ops.get_process_info = AsyncMock(return_value=(
            True,
            "Process information retrieved successfully",
            {
                'id': 1,
                'command': 'python run.py --task test_task --model ollama --model_name test_model --num_episodes 1 --results_dir results/run_1 --log_dir logs',
                'cwd': str(self.webarena_manager.webarena_dir),
                'start_time': 1234567890,
                'completed': True,
                'returncode': 0,
                'stdout': [],
                'stderr': [],
            }
        ))
        
        # Create a results file
        results_dir = os.path.join(self.webarena_manager.results_dir, run_id)
        os.makedirs(results_dir, exist_ok=True)
        results_file = os.path.join(results_dir, 'results.json')
        with open(results_file, 'w') as f:
            json.dump({
                'success_rate': 0.75,
                'completion_time': 120.5,
                'total_actions': 42,
            }, f)
        
        # Mock the _parse_results method
        self.webarena_manager._parse_results = AsyncMock()
        
        # Get the run status again
        run_status = await self.webarena_manager.get_run_status(run_id)
        
        # Check that the run status is updated
        self.assertEqual(run_status['status'], "completed")
        self.assertIn('end_time', run_status)
        self.assertIn('duration', run_status)
        self.assertEqual(run_status['returncode'], 0)
        
        # Check that the run was removed from the active runs set
        self.assertNotIn(run_id, self.webarena_manager.active_runs)
        
        # Check that the _parse_results method was called with the correct arguments
        self.webarena_manager._parse_results.assert_called_once_with(run_id)
    
    @patch('webarena.webarena_manager.secure_process_ops')
    async def async_test_stop_run(self, mock_secure_process_ops):
        """Test the stop_run method."""
        # Mock the kill_process method
        mock_secure_process_ops.kill_process = AsyncMock(return_value=(True, "Process killed successfully"))
        
        # Create a run
        run_id = "run_1"
        self.webarena_manager.runs[run_id] = {
            'id': run_id,
            'task_name': "test_task",
            'model_name': "test_model",
            'num_episodes': 1,
            'timeout': 3600,
            'start_time': 1234567890,
            'process_id': 1,
            'status': "running",
            'results': None,
        }
        self.webarena_manager.active_runs.add(run_id)
        
        # Stop the run
        success = await self.webarena_manager.stop_run(run_id)
        
        # Check that the stop was successful
        self.assertTrue(success)
        
        # Check that the run status was updated
        self.assertEqual(self.webarena_manager.runs[run_id]['status'], "stopped")
        self.assertIn('end_time', self.webarena_manager.runs[run_id])
        self.assertIn('duration', self.webarena_manager.runs[run_id])
        
        # Check that the run was removed from the active runs set
        self.assertNotIn(run_id, self.webarena_manager.active_runs)
        
        # Check that the kill_process method was called with the correct arguments
        mock_secure_process_ops.kill_process.assert_called_once_with(1)
    
    async def async_test_get_run_results(self):
        """Test the get_run_results method."""
        # Create a run
        run_id = "run_1"
        self.webarena_manager.runs[run_id] = {
            'id': run_id,
            'task_name': "test_task",
            'model_name': "test_model",
            'num_episodes': 1,
            'timeout': 3600,
            'start_time': 1234567890,
            'process_id': 1,
            'status': "completed",
            'results': {
                'success_rate': 0.75,
                'completion_time': 120.5,
                'total_actions': 42,
            },
        }
        
        # Get the run results
        results = await self.webarena_manager.get_run_results(run_id)
        
        # Check that the results are correct
        self.assertEqual(results['success_rate'], 0.75)
        self.assertEqual(results['completion_time'], 120.5)
        self.assertEqual(results['total_actions'], 42)
        
        # Test with a run that is not completed
        self.webarena_manager.runs[run_id]['status'] = "running"
        
        # Get the run results again
        results = await self.webarena_manager.get_run_results(run_id)
        
        # Check that the results are None
        self.assertIsNone(results)
    
    async def async_test_list_runs(self):
        """Test the list_runs method."""
        # Create some runs
        self.webarena_manager.runs = {
            "run_1": {
                'id': "run_1",
                'task_name': "test_task_1",
                'model_name': "test_model_1",
                'num_episodes': 1,
                'timeout': 3600,
                'start_time': 1234567890,
                'process_id': 1,
                'status': "completed",
                'results': {
                    'success_rate': 0.75,
                    'completion_time': 120.5,
                    'total_actions': 42,
                },
            },
            "run_2": {
                'id': "run_2",
                'task_name': "test_task_2",
                'model_name': "test_model_2",
                'num_episodes': 2,
                'timeout': 7200,
                'start_time': 1234567891,
                'process_id': 2,
                'status': "running",
                'results': None,
            },
            "run_3": {
                'id': "run_3",
                'task_name': "test_task_3",
                'model_name': "test_model_3",
                'num_episodes': 3,
                'timeout': 10800,
                'start_time': 1234567892,
                'process_id': 3,
                'status': "failed",
                'results': None,
            },
        }
        
        # List all runs
        runs = await self.webarena_manager.list_runs()
        
        # Check that all runs are returned
        self.assertEqual(len(runs), 3)
        
        # Check that the runs are sorted by start time (newest first)
        self.assertEqual(runs[0]['id'], "run_3")
        self.assertEqual(runs[1]['id'], "run_2")
        self.assertEqual(runs[2]['id'], "run_1")
        
        # List runs with a specific status
        runs = await self.webarena_manager.list_runs(status="running")
        
        # Check that only runs with the specified status are returned
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]['id'], "run_2")
    
    async def async_test_get_available_tasks(self):
        """Test the get_available_tasks method."""
        # Mock the _is_webarena_installed method
        self.webarena_manager._is_webarena_installed = MagicMock(return_value=True)
        
        # Create a tasks file
        tasks_dir = os.path.join(self.webarena_manager.webarena_dir, 'config')
        os.makedirs(tasks_dir, exist_ok=True)
        tasks_file = os.path.join(tasks_dir, 'tasks.json')
        with open(tasks_file, 'w') as f:
            json.dump({
                "task_1": {
                    "name": "Task 1",
                    "description": "This is task 1",
                    "website": "https://example.com/task1",
                    "difficulty": "easy",
                },
                "task_2": {
                    "name": "Task 2",
                    "description": "This is task 2",
                    "website": "https://example.com/task2",
                    "difficulty": "medium",
                },
                "task_3": {
                    "name": "Task 3",
                    "description": "This is task 3",
                    "website": "https://example.com/task3",
                    "difficulty": "hard",
                },
            }, f)
        
        # Get the available tasks
        tasks = await self.webarena_manager.get_available_tasks()
        
        # Check that the tasks are correct
        self.assertEqual(len(tasks), 3)
        
        # Check that the tasks are sorted by ID
        self.assertEqual(tasks[0]['id'], "task_1")
        self.assertEqual(tasks[1]['id'], "task_2")
        self.assertEqual(tasks[2]['id'], "task_3")
        
        # Check that the task information is correct
        self.assertEqual(tasks[0]['name'], "Task 1")
        self.assertEqual(tasks[0]['description'], "This is task 1")
        self.assertEqual(tasks[0]['website'], "https://example.com/task1")
        self.assertEqual(tasks[0]['difficulty'], "easy")
    
    async def async_test_cleanup(self):
        """Test the cleanup method."""
        # Create some active runs
        self.webarena_manager.active_runs = {"run_1", "run_2", "run_3"}
        
        # Mock the stop_run method
        self.webarena_manager.stop_run = AsyncMock(return_value=True)
        
        # Start the monitoring task
        self.webarena_manager.is_monitoring = True
        self.webarena_manager.monitor_task = asyncio.create_task(asyncio.sleep(3600))
        
        # Clean up
        await self.webarena_manager.cleanup()
        
        # Check that monitoring was stopped
        self.assertFalse(self.webarena_manager.is_monitoring)
        self.assertIsNone(self.webarena_manager.monitor_task)
        
        # Check that all active runs were stopped
        self.assertEqual(self.webarena_manager.stop_run.call_count, 3)
        self.webarena_manager.stop_run.assert_any_call("run_1")
        self.webarena_manager.stop_run.assert_any_call("run_2")
        self.webarena_manager.stop_run.assert_any_call("run_3")
    
    def test_run_experiment(self):
        """Test the run_experiment method."""
        asyncio.run(self.async_test_run_experiment())
    
    def test_get_run_status(self):
        """Test the get_run_status method."""
        asyncio.run(self.async_test_get_run_status())
    
    def test_stop_run(self):
        """Test the stop_run method."""
        asyncio.run(self.async_test_stop_run())
    
    def test_get_run_results(self):
        """Test the get_run_results method."""
        asyncio.run(self.async_test_get_run_results())
    
    def test_list_runs(self):
        """Test the list_runs method."""
        asyncio.run(self.async_test_list_runs())
    
    def test_get_available_tasks(self):
        """Test the get_available_tasks method."""
        asyncio.run(self.async_test_get_available_tasks())
    
    def test_cleanup(self):
        """Test the cleanup method."""
        asyncio.run(self.async_test_cleanup())


if __name__ == '__main__':
    unittest.main()
