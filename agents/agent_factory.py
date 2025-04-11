"""
Agent Factory for DMac.

This module provides a factory for creating agents.
"""

from typing import Optional

from utils.secure_logging import get_logger
from agents.base_agent import BaseAgent
from agents.task_agent import TaskAgent
from agents.assistant_agent import AssistantAgent
from agents.tool_agent import ToolAgent
from agents.perry import PerryAgent
from agents.shelly import ShellyAgent
from agents.flora import FloraAgent

logger = get_logger('dmac.agents.agent_factory')

# Import Codey if available
try:
    from agents.coding import CodingAgent
except ImportError:
    logger.warning("CodingAgent not available")
    CodingAgent = None


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
        elif agent_type == 'perry':
            return PerryAgent(name, **kwargs)
        elif agent_type == 'shelly':
            return ShellyAgent(name, **kwargs)
        elif agent_type == 'flora':
            return FloraAgent(name, **kwargs)
        elif agent_type == 'codey' and CodingAgent is not None:
            # Cast to BaseAgent to satisfy type checker
            return CodingAgent(name, **kwargs) # type: ignore
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

    @staticmethod
    async def create_perry_agent(name: str = "perry", model_name: Optional[str] = None) -> PerryAgent:
        """Create a Perry (Prompt Engineer) agent.

        Args:
            name: The name of the agent.
            model_name: The name of the model to use for the agent.

        Returns:
            The created Perry agent.
        """
        config = {}
        if model_name:
            config['model_name'] = model_name
        return PerryAgent(name, config=config)

    @staticmethod
    async def create_shelly_agent(name: str = "shelly", model_name: Optional[str] = None) -> ShellyAgent:
        """Create a Shelly (Shell/Command Line Specialist) agent.

        Args:
            name: The name of the agent.
            model_name: The name of the model to use for the agent.

        Returns:
            The created Shelly agent.
        """
        config = {}
        if model_name:
            config['model_name'] = model_name
        return ShellyAgent(name, config=config)

    @staticmethod
    async def create_flora_agent(name: str = "flora", model_name: Optional[str] = None) -> FloraAgent:
        """Create a Flora (Frontend Developer) agent.

        Args:
            name: The name of the agent.
            model_name: The name of the model to use for the agent.

        Returns:
            The created Flora agent.
        """
        config = {}
        if model_name:
            config['model_name'] = model_name
        return FloraAgent(name, config=config)

    @staticmethod
    async def create_codey_agent(name: str = "codey", model_name: Optional[str] = None) -> Optional[BaseAgent]:
        """Create a Codey (Code Curator) agent.

        Args:
            name: The name of the agent.
            model_name: The name of the model to use for the agent.

        Returns:
            The created Codey agent, or None if CodingAgent is not available.
        """
        if CodingAgent is None:
            logger.warning("CodingAgent not available")
            return None

        # CodingAgent might have different parameters, adjust as needed
        if model_name:
            return CodingAgent(name, model_name=model_name) # type: ignore
        else:
            return CodingAgent(name) # type: ignore


# Create a singleton instance
agent_factory = AgentFactory()
