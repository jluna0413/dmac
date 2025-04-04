"""
Agent Factory for DMac.

This module provides a factory for creating agents.
"""

import logging
from typing import Dict, List, Optional, Any

from config.config import config
from utils.secure_logging import get_logger
from agents.base_agent import BaseAgent
from agents.task_agent import TaskAgent
from agents.assistant_agent import AssistantAgent
from agents.tool_agent import ToolAgent

logger = get_logger('dmac.agents.agent_factory')


class AgentFactory:
    """Factory for creating agents."""
    
    @staticmethod
    async def create_agent(agent_type: str, name: str, **kwargs) -> Optional[BaseAgent]:
        """Create an agent of the specified type.
        
        Args:
            agent_type: The type of agent to create.
            name: The name of the agent.
            **kwargs: Additional arguments to pass to the agent constructor.
            
        Returns:
            The created agent, or None if the agent type is not supported.
        """
        if agent_type == 'task':
            return TaskAgent(name, **kwargs)
        elif agent_type == 'assistant':
            return AssistantAgent(name, **kwargs)
        elif agent_type == 'tool':
            tool_type = kwargs.get('tool_type')
            if not tool_type:
                logger.warning(f"No tool type provided for tool agent '{name}'")
                return None
            return ToolAgent(name, tool_type, **kwargs)
        else:
            logger.warning(f"Unsupported agent type '{agent_type}'")
            return None
    
    @staticmethod
    async def create_task_agent(name: str, model_name: Optional[str] = None) -> TaskAgent:
        """Create a task agent.
        
        Args:
            name: The name of the agent.
            model_name: The name of the model to use for the agent.
            
        Returns:
            The created task agent.
        """
        return TaskAgent(name, model_name=model_name)
    
    @staticmethod
    async def create_assistant_agent(name: str, model_name: Optional[str] = None) -> AssistantAgent:
        """Create an assistant agent.
        
        Args:
            name: The name of the agent.
            model_name: The name of the model to use for the agent.
            
        Returns:
            The created assistant agent.
        """
        return AssistantAgent(name, model_name=model_name)
    
    @staticmethod
    async def create_tool_agent(name: str, tool_type: str, model_name: Optional[str] = None) -> Optional[ToolAgent]:
        """Create a tool agent.
        
        Args:
            name: The name of the agent.
            tool_type: The type of tool this agent handles.
            model_name: The name of the model to use for the agent.
            
        Returns:
            The created tool agent, or None if the tool type is not supported.
        """
        if not tool_type:
            logger.warning(f"No tool type provided for tool agent '{name}'")
            return None
        
        return ToolAgent(name, tool_type, model_name=model_name)


# Create a singleton instance
agent_factory = AgentFactory()
