#!/usr/bin/env python3
"""
Assign tasks to agents.

This script creates and assigns tasks to agents based on their capabilities.
"""

import os
import sys
import json
import asyncio
import argparse
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.secure_logging import get_logger
from config.config import config
from task_system.task_manager import TaskManager

logger = get_logger('dmac.scripts.assign_tasks')

async def create_task(
    task_type: str,
    description: str,
    data: Dict[str, Any],
    priority: int = 1,
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a task and assign it to an agent.
    
    Args:
        task_type: Type of task
        description: Description of the task
        data: Task data
        priority: Task priority (1-5, with 5 being highest)
        agent_id: Optional agent ID to assign the task to
        
    Returns:
        Created task
    """
    # Initialize the task manager
    task_manager = TaskManager()
    
    # If no agent ID is provided, use task routing to find the appropriate agent
    if not agent_id:
        agent_id = config.get(f'task_routing.{task_type}')
        
        if not agent_id:
            # Find an agent with the capability
            agents = await task_manager.list_agents()
            for agent in agents:
                if 'capabilities' in agent and task_type in agent['capabilities']:
                    agent_id = agent['agent_id']
                    break
    
    if not agent_id:
        raise ValueError(f"No agent found for task type: {task_type}")
    
    # Create the task
    task = await task_manager.create_task(
        task_type=task_type,
        description=description,
        data=data,
        priority=priority,
        agent_id=agent_id
    )
    
    logger.info(f"Created task {task['task_id']} of type {task_type} and assigned to agent {agent_id}")
    
    return task

async def list_tasks(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List tasks.
    
    Args:
        status: Optional status to filter tasks
        
    Returns:
        List of tasks
    """
    # Initialize the task manager
    task_manager = TaskManager()
    
    # List tasks
    tasks = await task_manager.list_tasks(status=status)
    
    return tasks

async def get_task_result(task_id: str) -> Dict[str, Any]:
    """Get the result of a task.
    
    Args:
        task_id: Task ID
        
    Returns:
        Task result
    """
    # Initialize the task manager
    task_manager = TaskManager()
    
    # Get the task
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise ValueError(f"Task not found: {task_id}")
    
    return task

async def main_async(args):
    """Main async entry point."""
    # List tasks
    if args.list:
        tasks = await list_tasks(status=args.status)
        
        if not tasks:
            print("No tasks found")
            return
        
        print(f"Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"  Task ID: {task['task_id']}")
            print(f"  Type: {task['task_type']}")
            print(f"  Description: {task['description']}")
            print(f"  Status: {task['status']}")
            print(f"  Agent: {task['agent_id']}")
            print(f"  Created: {task['created_at']}")
            print(f"  Updated: {task['updated_at']}")
            print()
    
    # Get task result
    elif args.get:
        try:
            task = await get_task_result(args.get)
            
            print(f"Task ID: {task['task_id']}")
            print(f"Type: {task['task_type']}")
            print(f"Description: {task['description']}")
            print(f"Status: {task['status']}")
            print(f"Agent: {task['agent_id']}")
            print(f"Created: {task['created_at']}")
            print(f"Updated: {task['updated_at']}")
            print()
            
            if 'result' in task:
                print("Result:")
                print(json.dumps(task['result'], indent=2))
            else:
                print("No result yet")
        except ValueError as e:
            print(f"Error: {str(e)}")
    
    # Create task
    elif args.create:
        # Parse task data
        data = {}
        if args.data:
            for item in args.data:
                key, value = item.split('=', 1)
                data[key] = value
        
        try:
            task = await create_task(
                task_type=args.type,
                description=args.description,
                data=data,
                priority=args.priority,
                agent_id=args.agent
            )
            
            print(f"Created task {task['task_id']} of type {args.type} and assigned to agent {task['agent_id']}")
        except ValueError as e:
            print(f"Error: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Assign tasks to agents')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Create task parser
    create_parser = subparsers.add_parser('create', help='Create a task')
    create_parser.add_argument('--type', required=True, help='Task type')
    create_parser.add_argument('--description', required=True, help='Task description')
    create_parser.add_argument('--data', nargs='+', help='Task data in the format key=value')
    create_parser.add_argument('--priority', type=int, default=1, help='Task priority (1-5, with 5 being highest)')
    create_parser.add_argument('--agent', help='Agent ID to assign the task to')
    
    # List tasks parser
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--status', help='Filter tasks by status')
    
    # Get task result parser
    get_parser = subparsers.add_parser('get', help='Get task result')
    get_parser.add_argument('task_id', help='Task ID')
    
    args = parser.parse_args()
    
    # Set flags based on command
    if args.command == 'create':
        args.create = True
        args.list = False
        args.get = False
    elif args.command == 'list':
        args.create = False
        args.list = True
        args.get = False
    elif args.command == 'get':
        args.create = False
        args.list = False
        args.get = args.task_id
    else:
        parser.print_help()
        return
    
    # Run the async main function
    asyncio.run(main_async(args))

if __name__ == '__main__':
    main()
