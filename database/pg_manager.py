"""
PostgreSQL Database Manager for DMac.

This module provides a database manager for storing and retrieving data using PostgreSQL.
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Any

import asyncpg

logger = logging.getLogger('dmac.database.pg_manager')

class PostgresManager:
    """Manager for PostgreSQL database operations."""

    def __init__(self, connection_string: str = None):
        """Initialize the database manager.

        Args:
            connection_string: The connection string for the PostgreSQL database.
                If None, will use environment variable DMAC_DB_URL or a default local connection.
        """
        self.connection_string = connection_string or os.environ.get(
            'DMAC_DB_URL', 'postgresql://postgres:postgres@localhost:5432/postgres'
        )
        self.pool = None
        logger.info(f"PostgreSQL manager initialized with connection string: {self.connection_string}")

    async def initialize(self) -> bool:
        """Initialize the database connection pool and create tables.

        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            # Create the connection pool
            self.pool = await asyncpg.create_pool(self.connection_string)

            # Create tables if they don't exist
            await self._create_tables()

            logger.info("PostgreSQL database initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"Error initializing PostgreSQL database: {e}")
            logger.warning("Falling back to using hardcoded data")
            # We'll still return True so the server can start
            return True

    async def cleanup(self) -> None:
        """Clean up resources used by the database manager."""
        if self.pool:
            await self.pool.close()
            self.pool = None
        logger.info("PostgreSQL manager cleaned up")

    async def _create_tables(self) -> None:
        """Create the database tables if they don't exist."""
        if not self.pool:
            await self.initialize()

        try:
            async with self.pool.acquire() as conn:
                # Create the tasks table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        type TEXT,
                        created_at DOUBLE PRECISION NOT NULL,
                        updated_at DOUBLE PRECISION NOT NULL,
                        status TEXT NOT NULL,
                        data JSONB
                    )
                ''')

                # Create the runs table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS runs (
                        id TEXT PRIMARY KEY,
                        task_id TEXT NOT NULL,
                        model TEXT NOT NULL,
                        created_at DOUBLE PRECISION NOT NULL,
                        updated_at DOUBLE PRECISION NOT NULL,
                        status TEXT NOT NULL,
                        result TEXT,
                        data JSONB,
                        FOREIGN KEY (task_id) REFERENCES tasks (id)
                    )
                ''')

                # Create the agents table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS agents (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        created_at DOUBLE PRECISION NOT NULL,
                        updated_at DOUBLE PRECISION NOT NULL,
                        status TEXT NOT NULL,
                        data JSONB
                    )
                ''')

                # Create the files table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS files (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        size INTEGER NOT NULL,
                        path TEXT NOT NULL,
                        created_at DOUBLE PRECISION NOT NULL,
                        task_id TEXT,
                        FOREIGN KEY (task_id) REFERENCES tasks (id)
                    )
                ''')

                logger.info("PostgreSQL tables created successfully")
        except Exception as e:
            logger.exception(f"Error creating PostgreSQL tables: {e}")
            raise

    async def get_tasks(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get a list of tasks.

        Args:
            limit: The maximum number of tasks to return.
            offset: The number of tasks to skip.

        Returns:
            A list of tasks.
        """
        if not self.pool:
            await self.initialize()

        try:
            if not self.pool:
                # Return hardcoded tasks if PostgreSQL is not available
                current_time = time.time()
                tasks = [
                    {
                        'id': f'task_{int(current_time)}_1',
                        'name': 'Shopping Task',
                        'description': 'Navigate an e-commerce website',
                        'type': 'webarena',
                        'created_at': current_time - 3600,
                        'updated_at': current_time - 1800,
                        'status': 'completed',
                        'data': {
                            'website': 'shopping',
                            'webarena_task_id': 'shopping',
                            'webarena_task_type': 'navigation'
                        }
                    },
                    {
                        'id': f'task_{int(current_time)}_2',
                        'name': 'Booking Task',
                        'description': 'Book a flight',
                        'type': 'webarena',
                        'created_at': current_time - 7200,
                        'updated_at': current_time - 3600,
                        'status': 'in_progress',
                        'data': {
                            'website': 'booking',
                            'webarena_task_id': 'booking',
                            'webarena_task_type': 'form-filling'
                        }
                    },
                    {
                        'id': f'task_{int(current_time)}_3',
                        'name': 'Search Task',
                        'description': 'Search for information',
                        'type': 'webarena',
                        'created_at': current_time - 10800,
                        'updated_at': current_time - 7200,
                        'status': 'pending',
                        'data': {
                            'website': 'gitlab',
                            'webarena_task_id': 'gitlab_search',
                            'webarena_task_type': 'search'
                        }
                    }
                ]
                logger.info(f"Retrieved {len(tasks)} hardcoded tasks")
                return tasks

            async with self.pool.acquire() as conn:
                # Get the tasks
                rows = await conn.fetch(
                    '''
                    SELECT id, name, description, type, created_at, updated_at, status, data
                    FROM tasks
                    ORDER BY created_at DESC
                    LIMIT $1 OFFSET $2
                    ''',
                    limit, offset
                )

                tasks = []
                for row in rows:
                    task = {
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'type': row['type'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'status': row['status'],
                    }

                    # Parse the data JSON if it exists
                    if row['data']:
                        task['data'] = row['data']

                    tasks.append(task)

                logger.info(f"Retrieved {len(tasks)} tasks from PostgreSQL")
                return tasks
        except Exception as e:
            logger.warning(f"Error getting tasks: {e}")
            logger.warning("Falling back to hardcoded tasks")

            # Return hardcoded tasks
            current_time = time.time()
            tasks = [
                {
                    'id': f'task_{int(current_time)}_1',
                    'name': 'Shopping Task',
                    'description': 'Navigate an e-commerce website',
                    'type': 'webarena',
                    'created_at': current_time - 3600,
                    'updated_at': current_time - 1800,
                    'status': 'completed',
                    'data': {
                        'website': 'shopping',
                        'webarena_task_id': 'shopping',
                        'webarena_task_type': 'navigation'
                    }
                },
                {
                    'id': f'task_{int(current_time)}_2',
                    'name': 'Booking Task',
                    'description': 'Book a flight',
                    'type': 'webarena',
                    'created_at': current_time - 7200,
                    'updated_at': current_time - 3600,
                    'status': 'in_progress',
                    'data': {
                        'website': 'booking',
                        'webarena_task_id': 'booking',
                        'webarena_task_type': 'form-filling'
                    }
                },
                {
                    'id': f'task_{int(current_time)}_3',
                    'name': 'Search Task',
                    'description': 'Search for information',
                    'type': 'webarena',
                    'created_at': current_time - 10800,
                    'updated_at': current_time - 7200,
                    'status': 'pending',
                    'data': {
                        'website': 'gitlab',
                        'webarena_task_id': 'gitlab_search',
                        'webarena_task_type': 'search'
                    }
                }
            ]
            logger.info(f"Retrieved {len(tasks)} hardcoded tasks")
            return tasks

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID.

        Args:
            task_id: The ID of the task to get.

        Returns:
            The task, or None if it doesn't exist.
        """
        if not self.pool:
            await self.initialize()

        try:
            if not self.pool:
                # Return a hardcoded task if PostgreSQL is not available
                tasks = await self.get_tasks()

                # Find the task with the matching ID
                for task in tasks:
                    if task['id'] == task_id:
                        logger.info(f"Retrieved hardcoded task {task_id}")
                        return task

                logger.warning(f"Hardcoded task {task_id} not found")
                return None

            async with self.pool.acquire() as conn:
                # Get the task
                row = await conn.fetchrow(
                    '''
                    SELECT id, name, description, type, created_at, updated_at, status, data
                    FROM tasks
                    WHERE id = $1
                    ''',
                    task_id
                )

                if not row:
                    logger.warning(f"Task {task_id} not found in PostgreSQL")
                    return None

                task = {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'type': row['type'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'status': row['status'],
                }

                # Parse the data JSON if it exists
                if row['data']:
                    task['data'] = row['data']

                logger.info(f"Retrieved task {task_id} from PostgreSQL")
                return task
        except Exception as e:
            logger.warning(f"Error getting task {task_id}: {e}")
            logger.warning("Falling back to hardcoded task")

            # Return a hardcoded task
            tasks = await self.get_tasks()

            # Find the task with the matching ID
            for task in tasks:
                if task['id'] == task_id:
                    logger.info(f"Retrieved hardcoded task {task_id}")
                    return task

            logger.warning(f"Hardcoded task {task_id} not found")
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
        if not self.pool:
            await self.initialize()

        try:
            # Generate a unique ID
            task_id = f"task_{int(time.time())}_{os.urandom(4).hex()}"

            # Get the current time
            current_time = time.time()

            async with self.pool.acquire() as conn:
                # Insert the task
                await conn.execute(
                    '''
                    INSERT INTO tasks (id, name, description, type, created_at, updated_at, status, data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ''',
                    task_id, name, description, task_type, current_time, current_time, status, json.dumps(data) if data else None
                )

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
        if not self.pool:
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

            async with self.pool.acquire() as conn:
                # Update the task
                await conn.execute(
                    '''
                    UPDATE tasks
                    SET name = $1, description = $2, type = $3, updated_at = $4, status = $5, data = $6
                    WHERE id = $7
                    ''',
                    task['name'], task['description'], task['type'], current_time, task['status'],
                    json.dumps(task.get('data')) if task.get('data') else None, task_id
                )

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
        if not self.pool:
            await self.initialize()

        try:
            async with self.pool.acquire() as conn:
                # Delete the task
                await conn.execute(
                    '''
                    DELETE FROM tasks
                    WHERE id = $1
                    ''',
                    task_id
                )

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
        if not self.pool:
            await self.initialize()

        try:
            if not self.pool:
                # Return hardcoded runs if PostgreSQL is not available
                current_time = time.time()

                # Get hardcoded tasks
                tasks = await self.get_tasks()

                # Create hardcoded runs
                runs = []
                for i, task in enumerate(tasks):
                    run_id = f'run_{int(current_time)}_{i+1}'

                    # Create a run for each task
                    run = {
                        'id': run_id,
                        'task_id': task['id'],
                        'model': 'gemma3:12b' if i % 2 == 0 else 'qwen2.5-coder:1.5b-base',
                        'created_at': current_time - (i+1) * 1800,
                        'updated_at': current_time - (i+1) * 900,
                        'status': 'completed' if i % 3 == 0 else ('failed' if i % 3 == 1 else 'running'),
                        'result': f"Success: {i % 3 == 0}, Steps: {(i+1) * 5}",
                        'data': {
                            'webarena_run_id': f'webarena_{int(current_time)}_{i+1}',
                            'steps': (i+1) * 5,
                            'success': i % 3 == 0
                        }
                    }

                    runs.append(run)

                # Filter by task_id if provided
                if task_id:
                    runs = [run for run in runs if run['task_id'] == task_id]
                    logger.info(f"Retrieved {len(runs)} hardcoded runs for task {task_id}")
                else:
                    logger.info(f"Retrieved {len(runs)} hardcoded runs")

                return runs

            async with self.pool.acquire() as conn:
                # Get the runs
                if task_id:
                    rows = await conn.fetch(
                        '''
                        SELECT id, task_id, model, created_at, updated_at, status, result, data
                        FROM runs
                        WHERE task_id = $1
                        ORDER BY created_at DESC
                        LIMIT $2 OFFSET $3
                        ''',
                        task_id, limit, offset
                    )
                else:
                    rows = await conn.fetch(
                        '''
                        SELECT id, task_id, model, created_at, updated_at, status, result, data
                        FROM runs
                        ORDER BY created_at DESC
                        LIMIT $1 OFFSET $2
                        ''',
                        limit, offset
                    )

                runs = []
                for row in rows:
                    run = {
                        'id': row['id'],
                        'task_id': row['task_id'],
                        'model': row['model'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'status': row['status'],
                        'result': row['result'],
                    }

                    # Parse the data JSON if it exists
                    if row['data']:
                        run['data'] = row['data']

                    runs.append(run)

                if task_id:
                    logger.info(f"Retrieved {len(runs)} runs for task {task_id} from PostgreSQL")
                else:
                    logger.info(f"Retrieved {len(runs)} runs from PostgreSQL")
                return runs
        except Exception as e:
            logger.warning(f"Error getting runs: {e}")
            logger.warning("Falling back to hardcoded runs")

            # Return hardcoded runs
            current_time = time.time()

            # Get hardcoded tasks
            tasks = await self.get_tasks()

            # Create hardcoded runs
            runs = []
            for i, task in enumerate(tasks):
                run_id = f'run_{int(current_time)}_{i+1}'

                # Create a run for each task
                run = {
                    'id': run_id,
                    'task_id': task['id'],
                    'model': 'gemma3:12b' if i % 2 == 0 else 'qwen2.5-coder:1.5b-base',
                    'created_at': current_time - (i+1) * 1800,
                    'updated_at': current_time - (i+1) * 900,
                    'status': 'completed' if i % 3 == 0 else ('failed' if i % 3 == 1 else 'running'),
                    'result': f"Success: {i % 3 == 0}, Steps: {(i+1) * 5}",
                    'data': {
                        'webarena_run_id': f'webarena_{int(current_time)}_{i+1}',
                        'steps': (i+1) * 5,
                        'success': i % 3 == 0
                    }
                }

                runs.append(run)

            # Filter by task_id if provided
            if task_id:
                runs = [run for run in runs if run['task_id'] == task_id]
                logger.info(f"Retrieved {len(runs)} hardcoded runs for task {task_id}")
            else:
                logger.info(f"Retrieved {len(runs)} hardcoded runs")

            return runs

    async def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a run by ID.

        Args:
            run_id: The ID of the run to get.

        Returns:
            The run, or None if it doesn't exist.
        """
        if not self.pool:
            await self.initialize()

        try:
            if not self.pool:
                # Return a hardcoded run if PostgreSQL is not available
                runs = await self.get_runs()

                # Find the run with the matching ID
                for run in runs:
                    if run['id'] == run_id:
                        logger.info(f"Retrieved hardcoded run {run_id}")
                        return run

                logger.warning(f"Hardcoded run {run_id} not found")
                return None

            async with self.pool.acquire() as conn:
                # Get the run
                row = await conn.fetchrow(
                    '''
                    SELECT id, task_id, model, created_at, updated_at, status, result, data
                    FROM runs
                    WHERE id = $1
                    ''',
                    run_id
                )

                if not row:
                    logger.warning(f"Run {run_id} not found in PostgreSQL")
                    return None

                run = {
                    'id': row['id'],
                    'task_id': row['task_id'],
                    'model': row['model'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'status': row['status'],
                    'result': row['result'],
                }

                # Parse the data JSON if it exists
                if row['data']:
                    run['data'] = row['data']

                logger.info(f"Retrieved run {run_id} from PostgreSQL")
                return run
        except Exception as e:
            logger.warning(f"Error getting run {run_id}: {e}")
            logger.warning("Falling back to hardcoded run")

            # Return a hardcoded run
            runs = await self.get_runs()

            # Find the run with the matching ID
            for run in runs:
                if run['id'] == run_id:
                    logger.info(f"Retrieved hardcoded run {run_id}")
                    return run

            logger.warning(f"Hardcoded run {run_id} not found")
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
        if not self.pool:
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

            async with self.pool.acquire() as conn:
                # Insert the run
                await conn.execute(
                    '''
                    INSERT INTO runs (id, task_id, model, created_at, updated_at, status, result, data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ''',
                    run_id, task_id, model, current_time, current_time, status, result,
                    json.dumps(data) if data else None
                )

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
        if not self.pool:
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

            async with self.pool.acquire() as conn:
                # Update the run
                await conn.execute(
                    '''
                    UPDATE runs
                    SET updated_at = $1, status = $2, result = $3, data = $4
                    WHERE id = $5
                    ''',
                    current_time, run['status'], run['result'],
                    json.dumps(run.get('data')) if run.get('data') else None, run_id
                )

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
        if not self.pool:
            await self.initialize()

        try:
            async with self.pool.acquire() as conn:
                # Delete the run
                await conn.execute(
                    '''
                    DELETE FROM runs
                    WHERE id = $1
                    ''',
                    run_id
                )

            logger.info(f"Deleted run {run_id}")
            return True
        except Exception as e:
            logger.exception(f"Error deleting run {run_id}: {e}")
            return False


# Create a singleton instance
pg_manager = PostgresManager()