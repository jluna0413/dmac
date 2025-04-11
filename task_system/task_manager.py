"""
Task Manager for DMac.

This module provides functionality for managing tasks and agents.
"""

import os
import json
import time
import uuid
import logging
import asyncio
from typing import Dict, List, Any, Optional

from utils.secure_logging import get_logger
from config.config import config

logger = get_logger('dmac.task_system.task_manager')

class TaskManager:
    """Manager for tasks and agents."""
    
    def __init__(self):
        """Initialize the task manager."""
        # Load configuration
        self.config = {
            'tasks_dir': config.get('task_system.tasks_dir', os.path.join('data', 'tasks')),
            'agents_dir': config.get('task_system.agents_dir', os.path.join('data', 'agents')),
            'max_concurrent_tasks': config.get('task_system.max_concurrent_tasks', 10),
            'task_timeout': config.get('task_system.task_timeout', 3600),  # 1 hour
            'agent_timeout': config.get('task_system.agent_timeout', 60)  # 1 minute
        }
        
        # Create directories if they don't exist
        os.makedirs(self.config['tasks_dir'], exist_ok=True)
        os.makedirs(self.config['agents_dir'], exist_ok=True)
    
    async def create_task(self, 
                         task_type: str, 
                         description: str, 
                         data: Dict[str, Any],
                         priority: int = 1,
                         agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new task.
        
        Args:
            task_type: Type of task
            description: Description of the task
            data: Task data
            priority: Task priority (1-5, with 5 being highest)
            agent_id: Optional agent ID to assign the task to
            
        Returns:
            Created task
        """
        # Generate a task ID
        task_id = f"task_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Create the task
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'description': description,
            'data': data,
            'priority': priority,
            'status': 'pending',
            'agent_id': agent_id,
            'created_at': time.time(),
            'updated_at': time.time()
        }
        
        # Save the task
        await self._save_task(task)
        
        logger.info(f"Created task {task_id} of type {task_type}")
        
        # If an agent is assigned, notify the agent
        if agent_id:
            await self._notify_agent(agent_id, task_id)
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task or None if not found
        """
        # Get the task file path
        task_file = os.path.join(self.config['tasks_dir'], f"{task_id}.json")
        
        # Check if the task exists
        if not os.path.exists(task_file):
            return None
        
        # Load the task
        try:
            with open(task_file, 'r') as f:
                task = json.load(f)
            
            return task
        except Exception as e:
            logger.error(f"Error loading task {task_id}: {str(e)}")
            return None
    
    async def update_task(self, 
                         task_id: str, 
                         status: Optional[str] = None,
                         result: Optional[Any] = None,
                         error: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update a task.
        
        Args:
            task_id: Task ID
            status: New status
            result: Task result
            error: Error message
            
        Returns:
            Updated task or None if not found
        """
        # Get the task
        task = await self.get_task(task_id)
        
        if not task:
            return None
        
        # Update the task
        if status:
            task['status'] = status
        
        if result is not None:
            task['result'] = result
        
        if error:
            task['error'] = error
        
        task['updated_at'] = time.time()
        
        # Save the task
        await self._save_task(task)
        
        logger.info(f"Updated task {task_id} with status {status}")
        
        return task
    
    async def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks.
        
        Args:
            status: Optional status to filter tasks
            
        Returns:
            List of tasks
        """
        tasks = []
        
        # Get all task files
        for filename in os.listdir(self.config['tasks_dir']):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.config['tasks_dir'], filename), 'r') as f:
                        task = json.load(f)
                    
                    # Filter by status if provided
                    if status and task.get('status') != status:
                        continue
                    
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Error loading task {filename}: {str(e)}")
        
        # Sort tasks by priority (highest first) and creation time (oldest first)
        tasks.sort(key=lambda t: (-t.get('priority', 1), t.get('created_at', 0)))
        
        return tasks
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if the task was deleted, False otherwise
        """
        # Get the task file path
        task_file = os.path.join(self.config['tasks_dir'], f"{task_id}.json")
        
        # Check if the task exists
        if not os.path.exists(task_file):
            return False
        
        # Delete the task
        try:
            os.remove(task_file)
            logger.info(f"Deleted task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            return False
    
    async def register_agent(self, 
                            agent_id: str, 
                            name: str,
                            description: str,
                            capabilities: List[str],
                            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register an agent.
        
        Args:
            agent_id: Agent ID
            name: Agent name
            description: Agent description
            capabilities: Agent capabilities
            metadata: Additional metadata
            
        Returns:
            Registered agent
        """
        # Create the agent
        agent = {
            'agent_id': agent_id,
            'name': name,
            'description': description,
            'capabilities': capabilities,
            'status': 'active',
            'metadata': metadata or {},
            'registered_at': time.time(),
            'updated_at': time.time()
        }
        
        # Save the agent
        await self._save_agent(agent)
        
        logger.info(f"Registered agent {agent_id}")
        
        return agent
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent or None if not found
        """
        # Get the agent file path
        agent_file = os.path.join(self.config['agents_dir'], f"{agent_id}.json")
        
        # Check if the agent exists
        if not os.path.exists(agent_file):
            return None
        
        # Load the agent
        try:
            with open(agent_file, 'r') as f:
                agent = json.load(f)
            
            return agent
        except Exception as e:
            logger.error(f"Error loading agent {agent_id}: {str(e)}")
            return None
    
    async def update_agent(self, 
                          agent_id: str, 
                          status: Optional[str] = None,
                          capabilities: Optional[List[str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Update an agent.
        
        Args:
            agent_id: Agent ID
            status: New status
            capabilities: New capabilities
            metadata: New metadata
            
        Returns:
            Updated agent or None if not found
        """
        # Get the agent
        agent = await self.get_agent(agent_id)
        
        if not agent:
            return None
        
        # Update the agent
        if status:
            agent['status'] = status
        
        if capabilities:
            agent['capabilities'] = capabilities
        
        if metadata:
            if 'metadata' not in agent:
                agent['metadata'] = {}
            
            agent['metadata'].update(metadata)
        
        agent['updated_at'] = time.time()
        
        # Save the agent
        await self._save_agent(agent)
        
        logger.info(f"Updated agent {agent_id}")
        
        return agent
    
    async def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List agents.
        
        Args:
            status: Optional status to filter agents
            
        Returns:
            List of agents
        """
        agents = []
        
        # Get all agent files
        for filename in os.listdir(self.config['agents_dir']):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.config['agents_dir'], filename), 'r') as f:
                        agent = json.load(f)
                    
                    # Filter by status if provided
                    if status and agent.get('status') != status:
                        continue
                    
                    agents.append(agent)
                except Exception as e:
                    logger.error(f"Error loading agent {filename}: {str(e)}")
        
        return agents
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """Deregister an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if the agent was deregistered, False otherwise
        """
        # Get the agent
        agent = await self.get_agent(agent_id)
        
        if not agent:
            return False
        
        # Update the agent status
        agent['status'] = 'inactive'
        agent['updated_at'] = time.time()
        
        # Save the agent
        await self._save_agent(agent)
        
        logger.info(f"Deregistered agent {agent_id}")
        
        return True
    
    async def assign_task(self, task_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
        """Assign a task to an agent.
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
            
        Returns:
            Updated task or None if not found
        """
        # Get the task
        task = await self.get_task(task_id)
        
        if not task:
            return None
        
        # Get the agent
        agent = await self.get_agent(agent_id)
        
        if not agent:
            return None
        
        # Check if the agent is active
        if agent.get('status') != 'active':
            logger.warning(f"Agent {agent_id} is not active")
            return None
        
        # Update the task
        task['agent_id'] = agent_id
        task['updated_at'] = time.time()
        
        # Save the task
        await self._save_task(task)
        
        logger.info(f"Assigned task {task_id} to agent {agent_id}")
        
        # Notify the agent
        await self._notify_agent(agent_id, task_id)
        
        return task
    
    async def find_agent_for_task(self, task_type: str) -> Optional[str]:
        """Find an agent for a task.
        
        Args:
            task_type: Task type
            
        Returns:
            Agent ID or None if no suitable agent found
        """
        # Get all active agents
        agents = await self.list_agents(status='active')
        
        # Find an agent with the capability
        for agent in agents:
            if 'capabilities' in agent and task_type in agent['capabilities']:
                return agent['agent_id']
        
        # Try task routing
        agent_id = config.get(f'task_routing.{task_type}')
        
        if agent_id:
            # Check if the agent exists and is active
            agent = await self.get_agent(agent_id)
            
            if agent and agent.get('status') == 'active':
                return agent_id
        
        return None
    
    async def _save_task(self, task: Dict[str, Any]) -> None:
        """Save a task to disk.
        
        Args:
            task: Task to save
        """
        # Get the task file path
        task_file = os.path.join(self.config['tasks_dir'], f"{task['task_id']}.json")
        
        # Save the task
        try:
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving task {task['task_id']}: {str(e)}")
    
    async def _save_agent(self, agent: Dict[str, Any]) -> None:
        """Save an agent to disk.
        
        Args:
            agent: Agent to save
        """
        # Get the agent file path
        agent_file = os.path.join(self.config['agents_dir'], f"{agent['agent_id']}.json")
        
        # Save the agent
        try:
            with open(agent_file, 'w') as f:
                json.dump(agent, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving agent {agent['agent_id']}: {str(e)}")
    
    async def _notify_agent(self, agent_id: str, task_id: str) -> None:
        """Notify an agent about a task.
        
        Args:
            agent_id: Agent ID
            task_id: Task ID
        """
        # In a real implementation, this would send a message to the agent
        # For now, we'll just log it
        logger.info(f"Notified agent {agent_id} about task {task_id}")
        
        # TODO: Implement agent notification
