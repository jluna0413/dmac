"""
Base agent class for DMac.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger('dmac.agent')


class AgentState(Enum):
    """Enum representing the state of an agent."""
    IDLE = auto()
    INITIALIZING = auto()
    RUNNING = auto()
    WAITING = auto()
    ERROR = auto()
    FINISHED = auto()


class BaseAgent(ABC):
    """Base class for all agents in the DMac system."""
    
    def __init__(self, agent_id: Optional[str] = None, name: str = "BaseAgent", 
                 description: str = "Base agent for DMac"):
        """Initialize the agent.
        
        Args:
            agent_id: Unique identifier for the agent. If not provided, a UUID will be generated.
            name: Name of the agent.
            description: Description of the agent.
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.state = AgentState.IDLE
        self.max_steps = 10
        self.current_step = 0
        self.history = []
        self.tools = {}
        self.logger = logging.getLogger(f'dmac.agent.{self.name.lower()}')
    
    async def initialize(self) -> bool:
        """Initialize the agent.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        self.state = AgentState.INITIALIZING
        try:
            success = await self._initialize()
            self.state = AgentState.IDLE if success else AgentState.ERROR
            return success
        except Exception as e:
            self.logger.exception(f"Error initializing agent: {e}")
            self.state = AgentState.ERROR
            return False
    
    @abstractmethod
    async def _initialize(self) -> bool:
        """Initialize the agent implementation.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        pass
    
    async def process(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Process input data and return a result.
        
        Args:
            input_data: Input data to process. Can be a string or a dictionary.
            
        Returns:
            A dictionary containing the result of the processing.
        """
        if self.state == AgentState.ERROR:
            self.logger.error("Cannot process input: agent is in ERROR state")
            return {"error": "Agent is in ERROR state"}
        
        self.state = AgentState.RUNNING
        self.current_step = 0
        
        try:
            # Convert string input to dictionary if necessary
            if isinstance(input_data, str):
                input_data = {"prompt": input_data}
            
            # Add input to history
            self.history.append({"role": "user", "content": input_data})
            
            # Process the input
            result = await self._process(input_data)
            
            # Add result to history
            self.history.append({"role": "agent", "content": result})
            
            self.state = AgentState.IDLE
            return result
        except Exception as e:
            self.logger.exception(f"Error processing input: {e}")
            self.state = AgentState.ERROR
            return {"error": str(e)}
    
    @abstractmethod
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return a result.
        
        Args:
            input_data: Input data to process.
            
        Returns:
            A dictionary containing the result of the processing.
        """
        pass
    
    async def step(self) -> Dict[str, Any]:
        """Execute a single step of the agent's processing.
        
        Returns:
            A dictionary containing the result of the step.
        """
        if self.state != AgentState.RUNNING:
            self.logger.error(f"Cannot execute step: agent is not in RUNNING state (current state: {self.state})")
            return {"error": f"Agent is not in RUNNING state (current state: {self.state})"}
        
        try:
            result = await self._step()
            
            # Check if we've reached the maximum number of steps
            self.current_step += 1
            if self.current_step >= self.max_steps:
                self.logger.warning(f"Reached maximum number of steps ({self.max_steps})")
                self.state = AgentState.FINISHED
            
            return result
        except Exception as e:
            self.logger.exception(f"Error executing step: {e}")
            self.state = AgentState.ERROR
            return {"error": str(e)}
    
    @abstractmethod
    async def _step(self) -> Dict[str, Any]:
        """Execute a single step of the agent's processing.
        
        Returns:
            A dictionary containing the result of the step.
        """
        pass
    
    async def cleanup(self) -> None:
        """Clean up resources used by the agent."""
        try:
            await self._cleanup()
        except Exception as e:
            self.logger.exception(f"Error cleaning up agent: {e}")
    
    @abstractmethod
    async def _cleanup(self) -> None:
        """Clean up resources used by the agent implementation."""
        pass
    
    def register_tool(self, tool_name: str, tool_function: callable) -> None:
        """Register a tool that the agent can use.
        
        Args:
            tool_name: Name of the tool.
            tool_function: Function that implements the tool.
        """
        self.tools[tool_name] = tool_function
        self.logger.debug(f"Registered tool: {tool_name}")
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a registered tool.
        
        Args:
            tool_name: Name of the tool to use.
            **kwargs: Arguments to pass to the tool.
            
        Returns:
            The result of the tool execution.
            
        Raises:
            ValueError: If the tool is not registered.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not registered: {tool_name}")
        
        self.logger.debug(f"Using tool: {tool_name}")
        return await self.tools[tool_name](**kwargs)
    
    def is_stuck(self) -> bool:
        """Check if the agent is stuck in a loop.
        
        Returns:
            True if the agent is stuck, False otherwise.
        """
        # TODO: Implement stuck detection logic
        return False
    
    def handle_stuck_state(self) -> None:
        """Handle the case where the agent is stuck in a loop."""
        self.logger.warning("Agent appears to be stuck in a loop")
        # TODO: Implement stuck handling logic
