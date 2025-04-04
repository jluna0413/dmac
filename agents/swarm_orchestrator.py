"""
Swarm Orchestrator for DMac.

This module provides the orchestrator for managing agent swarms.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Set, Tuple, Any

from config.config import config
from utils.secure_logging import get_logger
from agents.swarm_manager import swarm_manager
from agents.agent_factory import agent_factory

logger = get_logger('dmac.agents.swarm_orchestrator')


class SwarmOrchestrator:
    """Orchestrator for managing agent swarms."""
    
    def __init__(self):
        """Initialize the swarm orchestrator."""
        self.swarm_templates = {}
        self.swarm_instances = {}
        
        # Load configuration
        self.max_swarms = config.get('swarm.max_swarms', 10)
        
        logger.info("Swarm orchestrator initialized")
    
    async def create_swarm_template(self, name: str, description: str, agent_specs: List[Dict[str, Any]]) -> str:
        """Create a swarm template.
        
        Args:
            name: The name of the template.
            description: A description of the template.
            agent_specs: A list of agent specifications.
            
        Returns:
            The ID of the new template.
        """
        template_id = str(uuid.uuid4())
        
        self.swarm_templates[template_id] = {
            'id': template_id,
            'name': name,
            'description': description,
            'agent_specs': agent_specs,
            'created_at': time.time(),
        }
        
        logger.info(f"Created swarm template {template_id} with name '{name}'")
        return template_id
    
    async def delete_swarm_template(self, template_id: str) -> bool:
        """Delete a swarm template.
        
        Args:
            template_id: The ID of the template to delete.
            
        Returns:
            True if the template was deleted, False otherwise.
        """
        if template_id not in self.swarm_templates:
            logger.warning(f"Swarm template {template_id} not found")
            return False
        
        # Delete the template
        del self.swarm_templates[template_id]
        
        logger.info(f"Deleted swarm template {template_id}")
        return True
    
    async def instantiate_swarm(self, template_id: str, name: str, description: str = "") -> Optional[str]:
        """Instantiate a swarm from a template.
        
        Args:
            template_id: The ID of the template to instantiate.
            name: The name of the new swarm.
            description: A description of the new swarm.
            
        Returns:
            The ID of the new swarm, or None if the template was not found or the maximum number of swarms has been reached.
        """
        if template_id not in self.swarm_templates:
            logger.warning(f"Swarm template {template_id} not found")
            return None
        
        if len(self.swarm_instances) >= self.max_swarms:
            logger.warning(f"Maximum number of swarms ({self.max_swarms}) reached")
            return None
        
        # Create a new swarm
        swarm_id = await swarm_manager.create_swarm(name, description)
        
        # Create agents according to the template
        template = self.swarm_templates[template_id]
        agent_ids = []
        
        for agent_spec in template['agent_specs']:
            agent_type = agent_spec.get('type')
            agent_name = agent_spec.get('name')
            
            if not agent_type or not agent_name:
                logger.warning(f"Invalid agent specification in template {template_id}: {agent_spec}")
                continue
            
            # Create the agent
            agent = await agent_factory.create_agent(agent_type, agent_name, **agent_spec.get('params', {}))
            
            if not agent:
                logger.warning(f"Failed to create agent of type '{agent_type}' with name '{agent_name}'")
                continue
            
            # Start the agent
            await agent.start()
            
            # Add the agent to the swarm
            await swarm_manager.add_agent_to_swarm(agent.id, swarm_id)
            
            agent_ids.append(agent.id)
        
        # Store the swarm instance
        self.swarm_instances[swarm_id] = {
            'id': swarm_id,
            'template_id': template_id,
            'name': name,
            'description': description,
            'agent_ids': agent_ids,
            'created_at': time.time(),
        }
        
        logger.info(f"Instantiated swarm {swarm_id} from template {template_id} with {len(agent_ids)} agents")
        return swarm_id
    
    async def destroy_swarm(self, swarm_id: str) -> bool:
        """Destroy a swarm.
        
        Args:
            swarm_id: The ID of the swarm to destroy.
            
        Returns:
            True if the swarm was destroyed, False otherwise.
        """
        if swarm_id not in self.swarm_instances:
            logger.warning(f"Swarm instance {swarm_id} not found")
            return False
        
        # Get the swarm instance
        instance = self.swarm_instances[swarm_id]
        
        # Stop all agents in the swarm
        for agent_id in instance['agent_ids']:
            agent = await swarm_manager.get_agent(agent_id)
            if agent:
                await agent.stop()
        
        # Delete the swarm
        await swarm_manager.delete_swarm(swarm_id)
        
        # Delete the swarm instance
        del self.swarm_instances[swarm_id]
        
        logger.info(f"Destroyed swarm {swarm_id}")
        return True
    
    async def get_swarm_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a swarm template.
        
        Args:
            template_id: The ID of the template to get information about.
            
        Returns:
            A dictionary containing information about the template, or None if the template was not found.
        """
        if template_id not in self.swarm_templates:
            logger.warning(f"Swarm template {template_id} not found")
            return None
        
        return self.swarm_templates[template_id].copy()
    
    async def get_swarm_templates(self) -> List[Dict[str, Any]]:
        """Get information about all swarm templates.
        
        Returns:
            A list of dictionaries containing information about all swarm templates.
        """
        return [template.copy() for template in self.swarm_templates.values()]
    
    async def get_swarm_instance(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a swarm instance.
        
        Args:
            swarm_id: The ID of the swarm instance to get information about.
            
        Returns:
            A dictionary containing information about the swarm instance, or None if the instance was not found.
        """
        if swarm_id not in self.swarm_instances:
            logger.warning(f"Swarm instance {swarm_id} not found")
            return None
        
        instance = self.swarm_instances[swarm_id].copy()
        
        # Get additional information from the swarm manager
        swarm_info = await swarm_manager.get_swarm(swarm_id)
        
        if swarm_info:
            instance.update({
                'agents': swarm_info['agents'],
                'tasks': swarm_info['tasks'],
                'updated_at': swarm_info['updated_at'],
            })
        
        return instance
    
    async def get_swarm_instances(self) -> List[Dict[str, Any]]:
        """Get information about all swarm instances.
        
        Returns:
            A list of dictionaries containing information about all swarm instances.
        """
        instances = []
        
        for swarm_id in self.swarm_instances:
            instance = await self.get_swarm_instance(swarm_id)
            if instance:
                instances.append(instance)
        
        return instances
    
    async def add_agent_to_swarm(self, agent_type: str, agent_name: str, swarm_id: str, **kwargs) -> Optional[str]:
        """Add a new agent to a swarm.
        
        Args:
            agent_type: The type of agent to add.
            agent_name: The name of the agent.
            swarm_id: The ID of the swarm to add the agent to.
            **kwargs: Additional arguments to pass to the agent constructor.
            
        Returns:
            The ID of the new agent, or None if the swarm was not found or the agent could not be created.
        """
        if swarm_id not in self.swarm_instances:
            logger.warning(f"Swarm instance {swarm_id} not found")
            return None
        
        # Create the agent
        agent = await agent_factory.create_agent(agent_type, agent_name, **kwargs)
        
        if not agent:
            logger.warning(f"Failed to create agent of type '{agent_type}' with name '{agent_name}'")
            return None
        
        # Start the agent
        await agent.start()
        
        # Add the agent to the swarm
        await swarm_manager.add_agent_to_swarm(agent.id, swarm_id)
        
        # Add the agent to the swarm instance
        self.swarm_instances[swarm_id]['agent_ids'].append(agent.id)
        
        logger.info(f"Added agent {agent.id} of type '{agent_type}' to swarm {swarm_id}")
        return agent.id
    
    async def remove_agent_from_swarm(self, agent_id: str, swarm_id: str) -> bool:
        """Remove an agent from a swarm.
        
        Args:
            agent_id: The ID of the agent to remove.
            swarm_id: The ID of the swarm to remove the agent from.
            
        Returns:
            True if the agent was removed, False otherwise.
        """
        if swarm_id not in self.swarm_instances:
            logger.warning(f"Swarm instance {swarm_id} not found")
            return False
        
        # Remove the agent from the swarm
        result = await swarm_manager.remove_agent_from_swarm(agent_id, swarm_id)
        
        if not result:
            logger.warning(f"Failed to remove agent {agent_id} from swarm {swarm_id}")
            return False
        
        # Remove the agent from the swarm instance
        if agent_id in self.swarm_instances[swarm_id]['agent_ids']:
            self.swarm_instances[swarm_id]['agent_ids'].remove(agent_id)
        
        # Stop the agent
        agent = await swarm_manager.get_agent(agent_id)
        if agent:
            await agent.stop()
        
        logger.info(f"Removed agent {agent_id} from swarm {swarm_id}")
        return True
    
    async def assign_task_to_swarm(self, task: Dict[str, Any], swarm_id: str) -> bool:
        """Assign a task to a swarm.
        
        Args:
            task: The task to assign.
            swarm_id: The ID of the swarm to assign the task to.
            
        Returns:
            True if the task was assigned, False otherwise.
        """
        if swarm_id not in self.swarm_instances:
            logger.warning(f"Swarm instance {swarm_id} not found")
            return False
        
        # Add the task to the swarm
        result = await swarm_manager.add_task_to_swarm(task['id'], swarm_id)
        
        if not result:
            logger.warning(f"Failed to add task {task['id']} to swarm {swarm_id}")
            return False
        
        # Get all agents in the swarm
        agents = await swarm_manager.get_swarm_agents(swarm_id)
        
        if not agents:
            logger.warning(f"No agents in swarm {swarm_id}")
            return False
        
        # Assign the task to all agents in the swarm
        for agent_id, agent in agents.items():
            await agent.add_task(task)
        
        logger.info(f"Assigned task {task['id']} to swarm {swarm_id} with {len(agents)} agents")
        return True
    
    async def cleanup(self) -> None:
        """Clean up resources used by the swarm orchestrator."""
        logger.info("Cleaning up swarm orchestrator")
        
        # Destroy all swarm instances
        swarm_ids = list(self.swarm_instances.keys())
        for swarm_id in swarm_ids:
            await self.destroy_swarm(swarm_id)
        
        # Clean up the swarm manager
        await swarm_manager.cleanup()
        
        logger.info("Swarm orchestrator cleaned up")


# Create a singleton instance
swarm_orchestrator = SwarmOrchestrator()
