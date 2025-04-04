"""
Swarm Manager for DMac.

This module provides the core functionality for managing agent swarms.
"""

import asyncio
import logging
import os
import time
import uuid
from typing import Dict, List, Optional, Set, Tuple, Any

from config.config import config
from utils.secure_logging import get_logger

logger = get_logger('dmac.agents.swarm_manager')


class SwarmManager:
    """Manager for agent swarms."""
    
    def __init__(self):
        """Initialize the swarm manager."""
        self.agents = {}  # Dictionary of agent_id -> agent
        self.swarms = {}  # Dictionary of swarm_id -> set of agent_ids
        self.agent_swarms = {}  # Dictionary of agent_id -> set of swarm_ids
        self.swarm_tasks = {}  # Dictionary of swarm_id -> set of task_ids
        self.task_swarms = {}  # Dictionary of task_id -> set of swarm_ids
        
        # Load configuration
        self.max_agents_per_swarm = config.get('swarm.max_agents_per_swarm', 10)
        self.max_swarms_per_agent = config.get('swarm.max_swarms_per_agent', 5)
        self.max_tasks_per_swarm = config.get('swarm.max_tasks_per_swarm', 20)
        
        logger.info("Swarm manager initialized")
    
    async def create_swarm(self, name: str, description: str = "", agent_ids: Optional[List[str]] = None) -> str:
        """Create a new swarm.
        
        Args:
            name: The name of the swarm.
            description: A description of the swarm.
            agent_ids: Optional list of agent IDs to add to the swarm.
            
        Returns:
            The ID of the new swarm.
        """
        swarm_id = str(uuid.uuid4())
        
        self.swarms[swarm_id] = {
            'id': swarm_id,
            'name': name,
            'description': description,
            'created_at': time.time(),
            'updated_at': time.time(),
            'agents': set(),
            'tasks': set(),
        }
        
        # Add agents to the swarm if provided
        if agent_ids:
            for agent_id in agent_ids:
                await self.add_agent_to_swarm(agent_id, swarm_id)
        
        logger.info(f"Created swarm {swarm_id} with name '{name}'")
        return swarm_id
    
    async def delete_swarm(self, swarm_id: str) -> bool:
        """Delete a swarm.
        
        Args:
            swarm_id: The ID of the swarm to delete.
            
        Returns:
            True if the swarm was deleted, False otherwise.
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return False
        
        # Remove all agents from the swarm
        agents_to_remove = list(self.swarms[swarm_id]['agents'])
        for agent_id in agents_to_remove:
            await self.remove_agent_from_swarm(agent_id, swarm_id)
        
        # Remove all tasks from the swarm
        tasks_to_remove = list(self.swarms[swarm_id]['tasks'])
        for task_id in tasks_to_remove:
            await self.remove_task_from_swarm(task_id, swarm_id)
        
        # Delete the swarm
        del self.swarms[swarm_id]
        
        logger.info(f"Deleted swarm {swarm_id}")
        return True
    
    async def add_agent_to_swarm(self, agent_id: str, swarm_id: str) -> bool:
        """Add an agent to a swarm.
        
        Args:
            agent_id: The ID of the agent to add.
            swarm_id: The ID of the swarm to add the agent to.
            
        Returns:
            True if the agent was added, False otherwise.
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return False
        
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        # Check if the agent is already in the swarm
        if agent_id in self.swarms[swarm_id]['agents']:
            logger.warning(f"Agent {agent_id} is already in swarm {swarm_id}")
            return True
        
        # Check if the swarm has reached its maximum number of agents
        if len(self.swarms[swarm_id]['agents']) >= self.max_agents_per_swarm:
            logger.warning(f"Swarm {swarm_id} has reached its maximum number of agents")
            return False
        
        # Check if the agent has reached its maximum number of swarms
        if agent_id in self.agent_swarms and len(self.agent_swarms[agent_id]) >= self.max_swarms_per_agent:
            logger.warning(f"Agent {agent_id} has reached its maximum number of swarms")
            return False
        
        # Add the agent to the swarm
        self.swarms[swarm_id]['agents'].add(agent_id)
        self.swarms[swarm_id]['updated_at'] = time.time()
        
        # Add the swarm to the agent's swarms
        if agent_id not in self.agent_swarms:
            self.agent_swarms[agent_id] = set()
        self.agent_swarms[agent_id].add(swarm_id)
        
        logger.info(f"Added agent {agent_id} to swarm {swarm_id}")
        return True
    
    async def remove_agent_from_swarm(self, agent_id: str, swarm_id: str) -> bool:
        """Remove an agent from a swarm.
        
        Args:
            agent_id: The ID of the agent to remove.
            swarm_id: The ID of the swarm to remove the agent from.
            
        Returns:
            True if the agent was removed, False otherwise.
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return False
        
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        # Check if the agent is in the swarm
        if agent_id not in self.swarms[swarm_id]['agents']:
            logger.warning(f"Agent {agent_id} is not in swarm {swarm_id}")
            return False
        
        # Remove the agent from the swarm
        self.swarms[swarm_id]['agents'].remove(agent_id)
        self.swarms[swarm_id]['updated_at'] = time.time()
        
        # Remove the swarm from the agent's swarms
        if agent_id in self.agent_swarms:
            self.agent_swarms[agent_id].remove(swarm_id)
            if not self.agent_swarms[agent_id]:
                del self.agent_swarms[agent_id]
        
        logger.info(f"Removed agent {agent_id} from swarm {swarm_id}")
        return True
    
    async def add_task_to_swarm(self, task_id: str, swarm_id: str) -> bool:
        """Add a task to a swarm.
        
        Args:
            task_id: The ID of the task to add.
            swarm_id: The ID of the swarm to add the task to.
            
        Returns:
            True if the task was added, False otherwise.
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return False
        
        # Check if the task is already in the swarm
        if task_id in self.swarms[swarm_id]['tasks']:
            logger.warning(f"Task {task_id} is already in swarm {swarm_id}")
            return True
        
        # Check if the swarm has reached its maximum number of tasks
        if len(self.swarms[swarm_id]['tasks']) >= self.max_tasks_per_swarm:
            logger.warning(f"Swarm {swarm_id} has reached its maximum number of tasks")
            return False
        
        # Add the task to the swarm
        self.swarms[swarm_id]['tasks'].add(task_id)
        self.swarms[swarm_id]['updated_at'] = time.time()
        
        # Add the swarm to the task's swarms
        if task_id not in self.task_swarms:
            self.task_swarms[task_id] = set()
        self.task_swarms[task_id].add(swarm_id)
        
        logger.info(f"Added task {task_id} to swarm {swarm_id}")
        return True
    
    async def remove_task_from_swarm(self, task_id: str, swarm_id: str) -> bool:
        """Remove a task from a swarm.
        
        Args:
            task_id: The ID of the task to remove.
            swarm_id: The ID of the swarm to remove the task from.
            
        Returns:
            True if the task was removed, False otherwise.
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return False
        
        # Check if the task is in the swarm
        if task_id not in self.swarms[swarm_id]['tasks']:
            logger.warning(f"Task {task_id} is not in swarm {swarm_id}")
            return False
        
        # Remove the task from the swarm
        self.swarms[swarm_id]['tasks'].remove(task_id)
        self.swarms[swarm_id]['updated_at'] = time.time()
        
        # Remove the swarm from the task's swarms
        if task_id in self.task_swarms:
            self.task_swarms[task_id].remove(swarm_id)
            if not self.task_swarms[task_id]:
                del self.task_swarms[task_id]
        
        logger.info(f"Removed task {task_id} from swarm {swarm_id}")
        return True
    
    async def get_swarm(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a swarm.
        
        Args:
            swarm_id: The ID of the swarm to get information about.
            
        Returns:
            A dictionary containing information about the swarm, or None if the swarm was not found.
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return None
        
        swarm_info = self.swarms[swarm_id].copy()
        swarm_info['agents'] = list(swarm_info['agents'])
        swarm_info['tasks'] = list(swarm_info['tasks'])
        
        return swarm_info
    
    async def get_swarms(self) -> List[Dict[str, Any]]:
        """Get information about all swarms.
        
        Returns:
            A list of dictionaries containing information about all swarms.
        """
        swarms_info = []
        
        for swarm_id in self.swarms:
            swarm_info = await self.get_swarm(swarm_id)
            if swarm_info:
                swarms_info.append(swarm_info)
        
        return swarms_info
    
    async def get_agent_swarms(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get information about all swarms that an agent is a member of.
        
        Args:
            agent_id: The ID of the agent to get swarms for.
            
        Returns:
            A list of dictionaries containing information about all swarms that the agent is a member of.
        """
        if agent_id not in self.agent_swarms:
            logger.warning(f"Agent {agent_id} is not a member of any swarms")
            return []
        
        swarms_info = []
        
        for swarm_id in self.agent_swarms[agent_id]:
            swarm_info = await self.get_swarm(swarm_id)
            if swarm_info:
                swarms_info.append(swarm_info)
        
        return swarms_info
    
    async def get_task_swarms(self, task_id: str) -> List[Dict[str, Any]]:
        """Get information about all swarms that a task is assigned to.
        
        Args:
            task_id: The ID of the task to get swarms for.
            
        Returns:
            A list of dictionaries containing information about all swarms that the task is assigned to.
        """
        if task_id not in self.task_swarms:
            logger.warning(f"Task {task_id} is not assigned to any swarms")
            return []
        
        swarms_info = []
        
        for swarm_id in self.task_swarms[task_id]:
            swarm_info = await self.get_swarm(swarm_id)
            if swarm_info:
                swarms_info.append(swarm_info)
        
        return swarms_info
    
    async def register_agent(self, agent_id: str, agent: Any) -> bool:
        """Register an agent with the swarm manager.
        
        Args:
            agent_id: The ID of the agent to register.
            agent: The agent object to register.
            
        Returns:
            True if the agent was registered, False otherwise.
        """
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} is already registered")
            return False
        
        self.agents[agent_id] = agent
        
        logger.info(f"Registered agent {agent_id}")
        return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the swarm manager.
        
        Args:
            agent_id: The ID of the agent to unregister.
            
        Returns:
            True if the agent was unregistered, False otherwise.
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} is not registered")
            return False
        
        # Remove the agent from all swarms
        if agent_id in self.agent_swarms:
            swarms_to_remove = list(self.agent_swarms[agent_id])
            for swarm_id in swarms_to_remove:
                await self.remove_agent_from_swarm(agent_id, swarm_id)
        
        # Unregister the agent
        del self.agents[agent_id]
        
        logger.info(f"Unregistered agent {agent_id}")
        return True
    
    async def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to get.
            
        Returns:
            The agent object, or None if the agent was not found.
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return None
        
        return self.agents[agent_id]
    
    async def get_agents(self) -> Dict[str, Any]:
        """Get all registered agents.
        
        Returns:
            A dictionary mapping agent IDs to agent objects.
        """
        return self.agents.copy()
    
    async def get_swarm_agents(self, swarm_id: str) -> Dict[str, Any]:
        """Get all agents in a swarm.
        
        Args:
            swarm_id: The ID of the swarm to get agents for.
            
        Returns:
            A dictionary mapping agent IDs to agent objects.
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return {}
        
        agents = {}
        
        for agent_id in self.swarms[swarm_id]['agents']:
            agent = await self.get_agent(agent_id)
            if agent:
                agents[agent_id] = agent
        
        return agents
    
    async def broadcast_to_swarm(self, swarm_id: str, message: Any) -> bool:
        """Broadcast a message to all agents in a swarm.
        
        Args:
            swarm_id: The ID of the swarm to broadcast to.
            message: The message to broadcast.
            
        Returns:
            True if the message was broadcast, False otherwise.
        """
        if swarm_id not in self.swarms:
            logger.warning(f"Swarm {swarm_id} not found")
            return False
        
        agents = await self.get_swarm_agents(swarm_id)
        
        if not agents:
            logger.warning(f"No agents in swarm {swarm_id}")
            return False
        
        # Broadcast the message to all agents
        for agent_id, agent in agents.items():
            try:
                await agent.receive_message(message)
            except Exception as e:
                logger.error(f"Error broadcasting message to agent {agent_id}: {e}")
        
        logger.info(f"Broadcast message to {len(agents)} agents in swarm {swarm_id}")
        return True
    
    async def cleanup(self) -> None:
        """Clean up resources used by the swarm manager."""
        logger.info("Cleaning up swarm manager")
        
        # Unregister all agents
        agents_to_unregister = list(self.agents.keys())
        for agent_id in agents_to_unregister:
            await self.unregister_agent(agent_id)
        
        # Delete all swarms
        swarms_to_delete = list(self.swarms.keys())
        for swarm_id in swarms_to_delete:
            await self.delete_swarm(swarm_id)
        
        logger.info("Swarm manager cleaned up")


# Create a singleton instance
swarm_manager = SwarmManager()
