"""
Database Manager for DMac.

This module provides a simple database manager for storing and retrieving data.
"""

import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger('dmac.database.db_manager')

class DatabaseManager:
    """Manager for database operations."""

    def __init__(self, db_path: str = "data/dmac.db"):
        """Initialize the database manager.

        Args:
            db_path: The path to the database file.
        """
        self.db_path = db_path
        self.connection = None
        logger.info(f"Database manager initialized with path: {db_path}")

    async def initialize(self) -> bool:
        """Initialize the database.

        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            # Connect to the database
            self.connection = await aiosqlite.connect(self.db_path)

            # Create tables if they don't exist
            await self._create_tables()

            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing database: {e}")
            return False

    async def cleanup(self) -> None:
        """Clean up resources used by the database manager."""
        if self.connection:
            await self.connection.close()
            self.connection = None
        logger.info("Database manager cleaned up")

    async def _create_tables(self) -> None:
        """Create the database tables if they don't exist."""
        if not self.connection:
            await self.initialize()

        try:
            # Create the tasks table
            await self.connection.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    status TEXT NOT NULL,
                    data TEXT
                )
            ''')

            # Create the runs table
            await self.connection.execute('''
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    data TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            ''')

            # Create the agents table
            await self.connection.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    status TEXT NOT NULL,
                    data TEXT
                )
            ''')

            # Create the files table
            await self.connection.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    task_id TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            ''')

            await self.connection.commit()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.exception(f"Error creating database tables: {e}")
            raise

    async def get_tasks(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get a list of tasks.

        Args:
            limit: The maximum number of tasks to return.
            offset: The number of tasks to skip.

        Returns:
            A list of tasks.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Get the tasks
            async with self.connection.execute(
                '''
                SELECT id, name, description, type, created_at, updated_at, status, data
                FROM tasks
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                ''',
                (limit, offset)
            ) as cursor:
                tasks = []
                async for row in cursor:
                    task = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'type': row[3],
                        'created_at': row[4],
                        'updated_at': row[5],
                        'status': row[6],
                    }

                    # Parse the data JSON if it exists
                    if row[7]:
                        try:
                            task['data'] = json.loads(row[7])
                        except json.JSONDecodeError:
                            logger.warning(f"Error decoding JSON data for task {row[0]}")

                    tasks.append(task)

                logger.info(f"Retrieved {len(tasks)} tasks")
                return tasks
        except Exception as e:
            logger.exception(f"Error getting tasks: {e}")
            return []

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID.

        Args:
            task_id: The ID of the task to get.

        Returns:
            The task, or None if it doesn't exist.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Get the task
            async with self.connection.execute(
                '''
                SELECT id, name, description, type, created_at, updated_at, status, data
                FROM tasks
                WHERE id = ?
                ''',
                (task_id,)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    logger.warning(f"Task {task_id} not found")
                    return None

                task = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'type': row[3],
                    'created_at': row[4],
                    'updated_at': row[5],
                    'status': row[6],
                }

                # Parse the data JSON if it exists
                if row[7]:
                    try:
                        task['data'] = json.loads(row[7])
                    except json.JSONDecodeError:
                        logger.warning(f"Error decoding JSON data for task {row[0]}")

                logger.info(f"Retrieved task {task_id}")
                return task
        except Exception as e:
            logger.exception(f"Error getting task {task_id}: {e}")
            return None

    async def create_task(self, name: str, description: str, task_type: str,
                        status: str = 'pending', data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a new task.

        Args:
            name: The name of the task.
            description: The description of the task.
            task_type: The type of the task.
            status: The status of the task.
            data: Additional data for the task.

        Returns:
            The ID of the new task, or None if creation failed.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Generate a unique ID
            task_id = f"task_{int(time.time())}_{os.urandom(4).hex()}"

            # Get the current time
            current_time = time.time()

            # Convert the data to JSON if it exists
            data_json = json.dumps(data) if data else None

            # Insert the task
            await self.connection.execute(
                '''
                INSERT INTO tasks (id, name, description, type, created_at, updated_at, status, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (task_id, name, description, task_type, current_time, current_time, status, data_json)
            )

            await self.connection.commit()
            logger.info(f"Created task {task_id}")
            return task_id
        except Exception as e:
            logger.exception(f"Error creating task: {e}")
            return None

    async def update_task(self, task_id: str, name: Optional[str] = None,
                        description: Optional[str] = None, task_type: Optional[str] = None,
                        status: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> bool:
        """Update a task.

        Args:
            task_id: The ID of the task to update.
            name: The new name of the task.
            description: The new description of the task.
            task_type: The new type of the task.
            status: The new status of the task.
            data: The new data for the task.

        Returns:
            True if the update was successful, False otherwise.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Get the current task
            task = await self.get_task(task_id)

            if not task:
                logger.warning(f"Task {task_id} not found for update")
                return False

            # Update the task fields
            if name is not None:
                task['name'] = name

            if description is not None:
                task['description'] = description

            if task_type is not None:
                task['type'] = task_type

            if status is not None:
                task['status'] = status

            if data is not None:
                task['data'] = data

            # Get the current time
            current_time = time.time()

            # Convert the data to JSON if it exists
            data_json = json.dumps(task.get('data')) if task.get('data') else None

            # Update the task
            await self.connection.execute(
                '''
                UPDATE tasks
                SET name = ?, description = ?, type = ?, updated_at = ?, status = ?, data = ?
                WHERE id = ?
                ''',
                (task['name'], task['description'], task['type'], current_time, task['status'], data_json, task_id)
            )

            await self.connection.commit()
            logger.info(f"Updated task {task_id}")
            return True
        except Exception as e:
            logger.exception(f"Error updating task {task_id}: {e}")
            return False

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if the deletion was successful, False otherwise.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Delete the task
            await self.connection.execute(
                '''
                DELETE FROM tasks
                WHERE id = ?
                ''',
                (task_id,)
            )

            await self.connection.commit()
            logger.info(f"Deleted task {task_id}")
            return True
        except Exception as e:
            logger.exception(f"Error deleting task {task_id}: {e}")
            return False

    async def get_runs(self, task_id: Optional[str] = None,
                     limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get a list of runs.

        Args:
            task_id: The ID of the task to get runs for, or None to get all runs.
            limit: The maximum number of runs to return.
            offset: The number of runs to skip.

        Returns:
            A list of runs.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Get the runs
            if task_id:
                async with self.connection.execute(
                    '''
                    SELECT id, task_id, model, created_at, updated_at, status, result, data
                    FROM runs
                    WHERE task_id = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    ''',
                    (task_id, limit, offset)
                ) as cursor:
                    runs = []
                    async for row in cursor:
                        run = {
                            'id': row[0],
                            'task_id': row[1],
                            'model': row[2],
                            'created_at': row[3],
                            'updated_at': row[4],
                            'status': row[5],
                            'result': row[6],
                        }

                        # Parse the data JSON if it exists
                        if row[7]:
                            try:
                                run['data'] = json.loads(row[7])
                            except json.JSONDecodeError:
                                logger.warning(f"Error decoding JSON data for run {row[0]}")

                        runs.append(run)

                    logger.info(f"Retrieved {len(runs)} runs for task {task_id}")
                    return runs
            else:
                async with self.connection.execute(
                    '''
                    SELECT id, task_id, model, created_at, updated_at, status, result, data
                    FROM runs
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    ''',
                    (limit, offset)
                ) as cursor:
                    runs = []
                    async for row in cursor:
                        run = {
                            'id': row[0],
                            'task_id': row[1],
                            'model': row[2],
                            'created_at': row[3],
                            'updated_at': row[4],
                            'status': row[5],
                            'result': row[6],
                        }

                        # Parse the data JSON if it exists
                        if row[7]:
                            try:
                                run['data'] = json.loads(row[7])
                            except json.JSONDecodeError:
                                logger.warning(f"Error decoding JSON data for run {row[0]}")

                        runs.append(run)

                    logger.info(f"Retrieved {len(runs)} runs")
                    return runs
        except Exception as e:
            logger.exception(f"Error getting runs: {e}")
            return []

    async def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a run by ID.

        Args:
            run_id: The ID of the run to get.

        Returns:
            The run, or None if it doesn't exist.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Get the run
            async with self.connection.execute(
                '''
                SELECT id, task_id, model, created_at, updated_at, status, result, data
                FROM runs
                WHERE id = ?
                ''',
                (run_id,)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    logger.warning(f"Run {run_id} not found")
                    return None

                run = {
                    'id': row[0],
                    'task_id': row[1],
                    'model': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'status': row[5],
                    'result': row[6],
                }

                # Parse the data JSON if it exists
                if row[7]:
                    try:
                        run['data'] = json.loads(row[7])
                    except json.JSONDecodeError:
                        logger.warning(f"Error decoding JSON data for run {row[0]}")

                logger.info(f"Retrieved run {run_id}")
                return run
        except Exception as e:
            logger.exception(f"Error getting run {run_id}: {e}")
            return None

    async def create_run(self, task_id: str, model: str, status: str = 'pending',
                       result: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a new run.

        Args:
            task_id: The ID of the task to create a run for.
            model: The model to use for the run.
            status: The status of the run.
            result: The result of the run.
            data: Additional data for the run.

        Returns:
            The ID of the new run, or None if creation failed.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Check if the task exists
            task = await self.get_task(task_id)

            if not task:
                logger.warning(f"Task {task_id} not found for run creation")
                return None

            # Generate a unique ID
            run_id = f"run_{int(time.time())}_{os.urandom(4).hex()}"

            # Get the current time
            current_time = time.time()

            # Convert the data to JSON if it exists
            data_json = json.dumps(data) if data else None

            # Insert the run
            await self.connection.execute(
                '''
                INSERT INTO runs (id, task_id, model, created_at, updated_at, status, result, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (run_id, task_id, model, current_time, current_time, status, result, data_json)
            )

            await self.connection.commit()
            logger.info(f"Created run {run_id} for task {task_id}")
            return run_id
        except Exception as e:
            logger.exception(f"Error creating run: {e}")
            return None

    async def update_run(self, run_id: str, status: Optional[str] = None,
                       result: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> bool:
        """Update a run.

        Args:
            run_id: The ID of the run to update.
            status: The new status of the run.
            result: The new result of the run.
            data: The new data for the run.

        Returns:
            True if the update was successful, False otherwise.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Get the current run
            run = await self.get_run(run_id)

            if not run:
                logger.warning(f"Run {run_id} not found for update")
                return False

            # Update the run fields
            if status is not None:
                run['status'] = status

            if result is not None:
                run['result'] = result

            if data is not None:
                run['data'] = data

            # Get the current time
            current_time = time.time()

            # Convert the data to JSON if it exists
            data_json = json.dumps(run.get('data')) if run.get('data') else None

            # Update the run
            await self.connection.execute(
                '''
                UPDATE runs
                SET updated_at = ?, status = ?, result = ?, data = ?
                WHERE id = ?
                ''',
                (current_time, run['status'], run['result'], data_json, run_id)
            )

            await self.connection.commit()
            logger.info(f"Updated run {run_id}")
            return True
        except Exception as e:
            logger.exception(f"Error updating run {run_id}: {e}")
            return False

    async def delete_run(self, run_id: str) -> bool:
        """Delete a run.

        Args:
            run_id: The ID of the run to delete.

        Returns:
            True if the deletion was successful, False otherwise.
        """
        if not self.connection:
            await self.initialize()

        try:
            # Delete the run
            await self.connection.execute(
                '''
                DELETE FROM runs
                WHERE id = ?
                ''',
                (run_id,)
            )

            await self.connection.commit()
            logger.info(f"Deleted run {run_id}")
            return True
        except Exception as e:
            logger.exception(f"Error deleting run {run_id}: {e}")
            return False


# Create a singleton instance
db_manager = DatabaseManager()
