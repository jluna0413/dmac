"""
Coding agent for DMac.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union

from config.config import config
from core.swarm.agent import BaseAgent, AgentState
from models.model_manager import ModelManager, ModelType

logger = logging.getLogger('dmac.agents.coding')


class CodingAgent(BaseAgent):
    """Coding agent for DMac."""
    
    def __init__(self, agent_id: str, name: str, model_manager: ModelManager):
        """Initialize the coding agent.
        
        Args:
            agent_id: The ID of the agent.
            name: The name of the agent.
            model_manager: The model manager.
        """
        super().__init__(agent_id, 'coding', name)
        self.model_manager = model_manager
        self.capabilities = [
            'code_generation',
            'code_review',
            'code_explanation',
            'debugging',
            'refactoring',
        ]
        self.logger = logging.getLogger(f'dmac.agents.coding.{agent_id}')
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a coding task.
        
        Args:
            task: The task to process.
            
        Returns:
            The result of processing the task.
        """
        self.logger.info(f"Processing coding task: {task.get('task_id', 'unknown')}")
        
        # Update agent state
        self.state = AgentState.BUSY
        self.last_active = time.time()
        self.tasks.append(task)
        
        try:
            # Extract task details
            prompt = task.get('prompt', '')
            task_type = task.get('type', 'code_generation')
            
            # Generate a response based on the task type
            if task_type == 'code_generation':
                response = await self._generate_code(prompt)
            elif task_type == 'code_review':
                response = await self._review_code(prompt)
            elif task_type == 'code_explanation':
                response = await self._explain_code(prompt)
            elif task_type == 'debugging':
                response = await self._debug_code(prompt)
            elif task_type == 'refactoring':
                response = await self._refactor_code(prompt)
            else:
                response = await self._generate_code(prompt)
            
            result = {
                'success': True,
                'message': f"Coding task processed by {self.name}",
                'data': {
                    'response': response,
                },
            }
            
            # Update agent state
            self.state = AgentState.IDLE
            self.last_active = time.time()
            
            return result
        except Exception as e:
            self.logger.exception(f"Error processing coding task: {e}")
            
            # Update agent state
            self.state = AgentState.ERROR
            self.last_active = time.time()
            
            return {
                'success': False,
                'message': f"Error processing coding task: {str(e)}",
                'data': {},
            }
    
    async def _generate_code(self, prompt: str) -> str:
        """Generate code based on a prompt.
        
        Args:
            prompt: The prompt.
            
        Returns:
            The generated code.
        """
        # Enhance the prompt for code generation
        enhanced_prompt = f"""
        Generate code based on the following requirements:
        
        {prompt}
        
        Please provide clean, well-documented code with appropriate comments.
        Include error handling and follow best practices.
        """
        
        # Use the model manager to generate the code
        response = await self.model_manager.generate_text(enhanced_prompt)
        
        return response
    
    async def _review_code(self, prompt: str) -> str:
        """Review code.
        
        Args:
            prompt: The prompt containing the code to review.
            
        Returns:
            The code review.
        """
        # Enhance the prompt for code review
        enhanced_prompt = f"""
        Review the following code:
        
        {prompt}
        
        Please provide a detailed code review, including:
        1. Potential bugs or issues
        2. Performance considerations
        3. Code style and readability
        4. Security concerns
        5. Suggestions for improvement
        """
        
        # Use the model manager to generate the review
        response = await self.model_manager.generate_text(enhanced_prompt)
        
        return response
    
    async def _explain_code(self, prompt: str) -> str:
        """Explain code.
        
        Args:
            prompt: The prompt containing the code to explain.
            
        Returns:
            The code explanation.
        """
        # Enhance the prompt for code explanation
        enhanced_prompt = f"""
        Explain the following code:
        
        {prompt}
        
        Please provide a detailed explanation, including:
        1. What the code does
        2. How it works
        3. Key algorithms or data structures used
        4. Any notable patterns or techniques
        """
        
        # Use the model manager to generate the explanation
        response = await self.model_manager.generate_text(enhanced_prompt)
        
        return response
    
    async def _debug_code(self, prompt: str) -> str:
        """Debug code.
        
        Args:
            prompt: The prompt containing the code to debug.
            
        Returns:
            The debugging results.
        """
        # Enhance the prompt for debugging
        enhanced_prompt = f"""
        Debug the following code:
        
        {prompt}
        
        Please identify and fix any bugs or issues, explaining:
        1. What the bugs are
        2. Why they occur
        3. How to fix them
        4. The corrected code
        """
        
        # Use the model manager to generate the debugging results
        response = await self.model_manager.generate_text(enhanced_prompt)
        
        return response
    
    async def _refactor_code(self, prompt: str) -> str:
        """Refactor code.
        
        Args:
            prompt: The prompt containing the code to refactor.
            
        Returns:
            The refactored code.
        """
        # Enhance the prompt for refactoring
        enhanced_prompt = f"""
        Refactor the following code:
        
        {prompt}
        
        Please improve the code by:
        1. Reducing complexity
        2. Improving readability
        3. Enhancing performance
        4. Following best practices
        5. Applying appropriate design patterns
        
        Provide the refactored code and explain the changes made.
        """
        
        # Use the model manager to generate the refactored code
        response = await self.model_manager.generate_text(enhanced_prompt)
        
        return response
