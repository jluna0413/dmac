#!/usr/bin/env python3
"""
List registered agents.

This script lists all registered agents.
"""

import os
import sys
import json
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from task_system.task_manager import TaskManager

async def list_agents():
    """List all registered agents."""
    task_manager = TaskManager()
    agents = await task_manager.list_agents()
    print(json.dumps(agents, indent=2))

if __name__ == '__main__':
    asyncio.run(list_agents())
