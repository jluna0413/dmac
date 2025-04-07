#!/usr/bin/env python3
"""
Register agents with the DMac task system.

This script registers the agents with the task system so they can be assigned tasks.
"""

import os
import sys
import asyncio
import argparse
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.agent_factory import agent_factory
from agents.personalities import get_agent_personality
from utils.secure_logging import get_logger
from task_system.task_manager import TaskManager

logger = get_logger('dmac.scripts.register_agents')

async def register_agents(
    agent_ids: List[str],
    model_name: Optional[str] = None,
    force: bool = False
) -> None:
    """Register agents with the task system.
    
    Args:
        agent_ids: List of agent IDs to register
        model_name: Optional model name to use for all agents
        force: Whether to force re-registration of existing agents
    """
    # Initialize the task manager
    task_manager = TaskManager()
    
    # Register each agent
    for agent_id in agent_ids:
        try:
            # Check if agent is already registered
            existing_agent = await task_manager.get_agent(agent_id)
            if existing_agent and not force:
                logger.info(f"Agent {agent_id} is already registered")
                continue
            
            # Create the agent
            agent = None
            if agent_id == 'codey':
                agent = await agent_factory.create_codey_agent(agent_id, model_name)
            elif agent_id == 'perry':
                agent = await agent_factory.create_perry_agent(agent_id, model_name)
            elif agent_id == 'shelly':
                agent = await agent_factory.create_shelly_agent(agent_id, model_name)
            elif agent_id == 'flora':
                agent = await agent_factory.create_flora_agent(agent_id, model_name)
            else:
                # Try generic creation
                agent = await agent_factory.create_agent(agent_id, agent_id, model_name=model_name)
            
            if not agent:
                logger.error(f"Failed to create agent {agent_id}")
                continue
            
            # Get agent personality
            personality = get_agent_personality(agent_id)
            
            # Register the agent
            await task_manager.register_agent(
                agent_id=agent_id,
                name=personality.get('name', agent_id),
                description=personality.get('role', f"{agent_id} agent"),
                capabilities=agent.capabilities if hasattr(agent, 'capabilities') else [],
                metadata={
                    'personality': personality,
                    'model_name': model_name or agent.model_name if hasattr(agent, 'model_name') else 'default'
                }
            )
            
            logger.info(f"Agent {agent_id} registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering agent {agent_id}: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Register agents with the DMac task system')
    parser.add_argument('--agents', nargs='+', default=['codey', 'perry', 'shelly', 'flora'],
                        help='Agent IDs to register')
    parser.add_argument('--model', help='Model name to use for all agents')
    parser.add_argument('--force', action='store_true', help='Force re-registration of existing agents')
    
    args = parser.parse_args()
    
    # Register the agents
    asyncio.run(register_agents(
        agent_ids=args.agents,
        model_name=args.model,
        force=args.force
    ))

if __name__ == '__main__':
    main()
