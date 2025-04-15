"""
Cody Agent - Native Code Assistant for DMac

This module provides the Cody agent implementation, which serves as a native code assistant
with code completion, vision capabilities, and reinforcement learning integration.
Cody listens for tasks from DMac, the main orchestrating agent powered by OpenManus RL.
"""

import time
import json
from typing import Dict, Any, Optional, List

from agents.base_agent import BaseAgent
from models.deepclaude import DeepClaudeModule
from utils.secure_logging import get_logger

logger = get_logger('dmac.agents.cody')

class CodyAgent(BaseAgent):
    """
    Cody is a native code assistant with advanced coding capabilities.

    Cody provides code completion, generation, explanation, and refactoring capabilities
    directly within the codebase. Unlike MaCoder, Cody is not a VS Code plugin but
    operates locally within the DMac ecosystem, listening for tasks from the main
    orchestrating agent.
    """

    def __init__(self, agent_id: str, name: str, config: Dict[str, Any] = None):
        """
        Initialize the Cody agent.

        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            config: Configuration for the agent
        """
        super().__init__(agent_id, name, "code_assistant")

        # Default configuration
        self.default_config = {
            'model_name': 'GandalfBaum/deepseek_r1-claude3.7:latest',  # Ideal for coding tasks
            'temperature': 0.2,
            'max_context_length': 16384,
            'vision_enabled': True,
            'rl_enabled': True,
            'rl_model': 'openManus',
            'code_completion_enabled': True,
        }

        # Merge default config with provided config
        self.config = {**self.default_config, **(config or {})}

        # Set up capabilities
        self.capabilities = [
            "code_search",
            "code_generation",
            "code_completion",
            "code_explanation",
            "code_refactoring",
            "bug_finding",
            "test_generation",
            "code_documentation",
            "project_analysis",
            "vision_code_understanding",
            "reinforcement_learning"
        ]

        # Initialize vision capabilities if enabled
        self.vision_enabled = self.config.get('vision_enabled', True)

        # Initialize reinforcement learning if enabled
        self.rl_enabled = self.config.get('rl_enabled', True)
        self.rl_model = self.config.get('rl_model', 'openManus')

        # Initialize code completion
        self.code_completion_enabled = self.config.get('code_completion_enabled', True)

        # Initialize DeepClaude module
        # DeepClaude combines DeepSeek R1 for reasoning with Claude 3.7 for generation
        # This hybrid approach provides better code generation and explanation capabilities
        deepclaude_config = {
            # Model used for reasoning (typically DeepSeek R1)
            'reasoning_model': self.config.get('reasoning_model', 'GandalfBaum/deepseek_r1-claude3.7:latest'),
            # Model used for final generation (typically Claude 3.7)
            'generation_model': self.config.get('generation_model', 'claude-3-7-sonnet'),
            # Temperature controls randomness in generation (lower = more deterministic)
            'temperature': self.config.get('temperature', 0.2),
            # Whether the reasoning model supports native reasoning capabilities
            'supports_native_reasoning': self.config.get('supports_native_reasoning', True),
            # Proxy settings for API calls
            'enable_proxy': self.config.get('enable_proxy', {'reasoning_model': False, 'generation_model': True})
        }
        self.deepclaude = DeepClaudeModule(deepclaude_config)

        # Initialize agent state
        self.current_tasks = {}
        self.context_cache = {}

        # Initialize RL experience tracking
        self.rl_experiences = []

        # Store agent ID and name for reference
        self._agent_id = agent_id
        self._name = name

        logger.info(f"Cody agent initialized with ID {agent_id}")

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message sent to the agent.

        Args:
            message: Message to process

        Returns:
            Response message
        """
        try:
            # Extract message content
            content = message.get('content', '')
            action = message.get('action', 'chat')
            data = message.get('data', {})

            # Process based on the action
            if action == 'chat':
                # General chat interaction
                response_text = await self._handle_chat(content)
                return {
                    'success': True,
                    'content': response_text,
                    'agent_id': self._agent_id,
                    'agent_name': self.name
                }

            elif action == 'vision_code':
                # Process code with vision capabilities
                result = await self._process_code_with_vision(data.get('task_id'), data.get('image_data'))
                return {
                    'success': True,
                    'content': f"Vision processing initiated for task {data.get('task_id')}",
                    'data': result,
                    'agent_id': self._agent_id,
                    'agent_name': self.name
                }

            elif action == 'generate_code':
                # Generate code
                result = await self._generate_code(data.get('prompt'), data.get('language'))
                return {
                    'success': True,
                    'content': "Code generation completed",
                    'data': result,
                    'agent_id': self._agent_id,
                    'agent_name': self.name
                }

            elif action == 'complete_code':
                # Complete code
                result = await self._complete_code(data.get('code'), data.get('cursor_position'), data.get('language'))
                return {
                    'success': True,
                    'content': "Code completion generated",
                    'data': result,
                    'agent_id': self._agent_id,
                    'agent_name': self.name
                }

            elif action == 'explain_code':
                # Explain code
                result = await self._explain_code(data.get('code'), data.get('language'))
                return {
                    'success': True,
                    'content': "Code explanation completed",
                    'data': result,
                    'agent_id': self._agent_id,
                    'agent_name': self.name
                }

            else:
                # Unknown action
                return {
                    'success': False,
                    'content': f"Unknown action: {action}",
                    'agent_id': self._agent_id,
                    'agent_name': self.name
                }

        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            return {
                'success': False,
                'content': f"Error: {str(e)}",
                'agent_id': self._agent_id,
                'agent_name': self.name
            }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to the agent.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        task_type = task.get('type', '')
        task_data = task.get('data', {})

        if task_type == 'vision_code_understanding':
            # Process code with vision capabilities
            result = await self._process_code_with_vision(task.get('task_id'), task_data.get('image_data'))

            return {
                'success': True,
                'result': result,
                'task_id': task.get('task_id'),
                'agent_id': self._agent_id
            }

        elif task_type == 'code_generation':
            # Generate code
            result = await self._generate_code(task_data.get('prompt'), task_data.get('language'))

            return {
                'success': True,
                'result': result,
                'task_id': task.get('task_id'),
                'agent_id': self._agent_id
            }

        elif task_type == 'code_completion':
            # Complete code
            result = await self._complete_code(
                task_data.get('code'),
                task_data.get('cursor_position'),
                task_data.get('language')
            )

            return {
                'success': True,
                'result': result,
                'task_id': task.get('task_id'),
                'agent_id': self._agent_id
            }

        elif task_type == 'code_explanation':
            # Explain code
            result = await self._explain_code(task_data.get('code'), task_data.get('language'))

            return {
                'success': True,
                'result': result,
                'task_id': task.get('task_id'),
                'agent_id': self._agent_id
            }

        else:
            # Unknown task type
            return {
                'success': False,
                'result': f"Unknown task type: {task_type}",
                'task_id': task.get('task_id'),
                'agent_id': self._agent_id
            }

    async def _handle_chat(self, content: str) -> str:
        """
        Handle a chat message.

        Args:
            content: Message content

        Returns:
            Response text
        """
        # Analyze the message to determine intent
        if any(keyword in content.lower() for keyword in ['complete', 'finish', 'autocomplete']):
            # Code completion intent
            return "I can help complete your code. Please share the code snippet you're working on."

        elif any(keyword in content.lower() for keyword in ['generate', 'create', 'write']):
            # Code generation intent
            return "I can generate code based on your requirements. What would you like me to create?"

        elif any(keyword in content.lower() for keyword in ['explain', 'understand', 'clarify']):
            # Code explanation intent
            return "I'd be happy to explain code. Please share the code you'd like me to explain."

        elif any(keyword in content.lower() for keyword in ['refactor', 'improve', 'optimize']):
            # Code refactoring intent
            return "I can help refactor your code for better performance and readability. Please share the code you'd like to improve."

        elif any(keyword in content.lower() for keyword in ['vision', 'image', 'screenshot']):
            # Vision code understanding intent
            return "I can analyze code from images or screenshots. Please share the image containing the code."

        else:
            # General chat
            return "I'm Cody, a native code assistant with code completion, vision capabilities, and reinforcement learning integration. I can help you write, understand, and improve your code. How can I assist you with your coding project today?"

    async def _process_code_with_vision(self, task_id: str, image_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Process code from images using vision capabilities.

        Args:
            task_id: ID of the task
            image_data: Image data containing code

        Returns:
            Vision processing result
        """
        logger.info(f"Processing code with vision for task {task_id}")

        # In a real implementation, this would involve:
        # 1. Processing the image to extract text/code
        # 2. Analyzing the extracted code
        # 3. Providing insights or suggestions
        # 4. Potentially generating improved code

        # For now, we'll return a simple result
        return {
            'task_id': task_id,
            'vision_enabled': self.vision_enabled,
            'status': 'processed',
            'extracted_code_length': 100 if image_data else 0,  # Placeholder
            'processing_time': time.time()
        }

    async def _generate_code(self, prompt: Optional[str] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate code based on a prompt using DeepClaude.

        Args:
            prompt: The prompt describing the code to generate
            language: The programming language

        Returns:
            Generated code result
        """
        logger.info(f"Generating code in {language or 'unspecified'} language using DeepClaude")

        if not prompt:
            return {
                'success': False,
                'error': 'Prompt is required for code generation',
                'language': language or 'python',
                'generated_code': ''
            }

        try:
            # Create system message based on language
            if language:
                system_message = f"You are an expert {language} programmer. Generate high-quality, efficient, and well-documented {language} code."
            else:
                system_message = "You are an expert programmer. Generate high-quality, efficient, and well-documented code."

            # Generate code using DeepClaude
            result = await self.deepclaude.generate_code(
                prompt=prompt,
                language=language,
                system_message=system_message
            )

            # Track RL experience
            await self._track_rl_experience('code_generation', {
                'prompt': prompt,
                'language': language,
                'success': result.get('success', False),
                'reasoning_used': bool(result.get('reasoning', ''))
            })

            # Format the result
            return {
                'success': result.get('success', False),
                'prompt': prompt,
                'language': language or 'python',
                'generated_code': result.get('content', ''),
                'reasoning': result.get('reasoning', ''),
                'generation_time': result.get('total_time', 0)
            }
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {
                'success': False,
                'error': str(e),
                'prompt': prompt,
                'language': language or 'python',
                'generated_code': ''
            }

    async def _complete_code(self, code: Optional[str] = None, cursor_position: Optional[int] = None,
                            language: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete code at a specific position using DeepClaude.

        Args:
            code: The code to complete
            cursor_position: The position of the cursor in the code
            language: The programming language

        Returns:
            Code completion result
        """
        logger.info(f"Completing code in {language or 'unspecified'} language using DeepClaude")

        if not code:
            return {
                'success': False,
                'error': 'Code is required for completion',
                'language': language or 'python',
                'completion': ''
            }

        try:
            # Extract the code before the cursor position
            code_before_cursor = code[:cursor_position] if cursor_position is not None else code

            # Create prompt for completion
            if language:
                prompt = f"Complete the following {language} code. Only provide the completion, not the entire code:\n\n```{language}\n{code_before_cursor}```"
                system_message = f"You are an expert {language} programmer. Complete the code with high-quality, efficient, and well-documented {language} code."
            else:
                prompt = f"Complete the following code. Only provide the completion, not the entire code:\n\n```\n{code_before_cursor}```"
                system_message = "You are an expert programmer. Complete the code with high-quality, efficient, and well-documented code."

            # Generate completion using DeepClaude
            result = await self.deepclaude.generate_with_reasoning(
                prompt=prompt,
                system_message=system_message
            )

            # Track RL experience
            await self._track_rl_experience('code_completion', {
                'code_length': len(code),
                'cursor_position': cursor_position,
                'language': language,
                'success': result.get('success', False),
                'reasoning_used': bool(result.get('reasoning', ''))
            })

            # Extract completion from the result
            completion = result.get('content', '')

            # Clean up the completion (remove code blocks, etc.)
            if '```' in completion:
                # Extract code from code blocks
                import re
                code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)```', completion)
                if code_blocks:
                    completion = code_blocks[0].strip()

            return {
                'success': result.get('success', False),
                'code_length': len(code),
                'cursor_position': cursor_position or 0,
                'language': language or 'python',
                'completion': completion,
                'reasoning': result.get('reasoning', ''),
                'completion_time': result.get('total_time', 0)
            }
        except Exception as e:
            logger.error(f"Error completing code: {e}")
            return {
                'success': False,
                'error': str(e),
                'code_length': len(code) if code else 0,
                'cursor_position': cursor_position or 0,
                'language': language or 'python',
                'completion': ''
            }

    async def _explain_code(self, code: Optional[str] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Explain what code does using DeepClaude.

        Args:
            code: The code to explain
            language: The programming language

        Returns:
            Code explanation result
        """
        logger.info(f"Explaining code in {language or 'unspecified'} language using DeepClaude")

        if not code:
            return {
                'success': False,
                'error': 'Code is required for explanation',
                'language': language or 'python',
                'explanation': ''
            }

        try:
            # Generate explanation using DeepClaude
            result = await self.deepclaude.explain_code(
                code=code,
                language=language
            )

            # Track RL experience
            await self._track_rl_experience('code_explanation', {
                'code_length': len(code),
                'language': language,
                'success': result.get('success', False),
                'reasoning_used': bool(result.get('reasoning', ''))
            })

            return {
                'success': result.get('success', False),
                'code_length': len(code),
                'language': language or 'python',
                'explanation': result.get('content', ''),
                'reasoning': result.get('reasoning', ''),
                'explanation_time': result.get('total_time', 0)
            }
        except Exception as e:
            logger.error(f"Error explaining code: {e}")
            return {
                'success': False,
                'error': str(e),
                'code_length': len(code) if code else 0,
                'language': language or 'python',
                'explanation': ''
            }

    async def _refactor_code(self, code: Optional[str] = None, instructions: Optional[str] = None,
                            language: Optional[str] = None) -> Dict[str, Any]:
        """
        Refactor code according to instructions using DeepClaude.

        Args:
            code: The code to refactor
            instructions: Instructions for refactoring
            language: The programming language

        Returns:
            Refactored code result
        """
        logger.info(f"Refactoring code in {language or 'unspecified'} language using DeepClaude")

        if not code:
            return {
                'success': False,
                'error': 'Code is required for refactoring',
                'language': language or 'python',
                'refactored_code': ''
            }

        if not instructions:
            instructions = 'Improve readability, efficiency, and maintainability'

        try:
            # Generate refactored code using DeepClaude
            result = await self.deepclaude.refactor_code(
                code=code,
                instructions=instructions,
                language=language
            )

            # Track RL experience
            await self._track_rl_experience('code_refactoring', {
                'code_length': len(code),
                'instructions': instructions,
                'language': language,
                'success': result.get('success', False),
                'reasoning_used': bool(result.get('reasoning', ''))
            })

            return {
                'success': result.get('success', False),
                'code_length': len(code),
                'instructions': instructions,
                'language': language or 'python',
                'refactored_code': result.get('content', ''),
                'reasoning': result.get('reasoning', ''),
                'refactoring_time': result.get('total_time', 0)
            }
        except Exception as e:
            logger.error(f"Error refactoring code: {e}")
            return {
                'success': False,
                'error': str(e),
                'code_length': len(code) if code else 0,
                'instructions': instructions,
                'language': language or 'python',
                'refactored_code': ''
            }

    async def _track_rl_experience(self, action_type: str, data: Dict[str, Any]) -> None:
        """
        Track reinforcement learning experience for OpenManus RL.

        This method captures agent experiences during code-related tasks and sends them
        to the OpenManus RL system for future learning and improvement. These experiences
        help the RL system understand which approaches work best for different coding tasks.

        The experiences are stored both locally (as a backup) and sent to the central
        OpenManus RL knowledge base, where they can be used to improve task dispatching
        and agent selection in the future.

        Args:
            action_type: Type of action (e.g., 'code_generation', 'code_completion')
            data: Data about the action and its outcome, including success/failure,
                  context information, and performance metrics
        """
        # Skip if RL is disabled for this agent
        if not self.rl_enabled:
            return

        # Create experience record with all necessary metadata
        experience = {
            'agent_id': self._agent_id,  # Unique identifier for this agent instance
            'agent_name': self._name,    # Human-readable name
            'action_type': action_type,  # Type of coding action performed
            'timestamp': time.time(),    # When the action occurred
            'data': data                 # Detailed information about the action and outcome
        }

        # Add to local experiences list for persistence across restarts
        self.rl_experiences.append(experience)

        # Send to OpenManus RL if available
        try:
            # In a real implementation, this would send the experience to OpenManus RL
            # For now, we'll just log it
            logger.debug(f"Sending RL experience to OpenManus RL: {action_type}")

            # TODO: Implement actual integration with OpenManus RL
            # The OpenManus RL system will use these experiences to:
            # 1. Improve model selection for different coding tasks
            # 2. Optimize prompting strategies
            # 3. Learn which approaches work best for different programming languages
            # 4. Adapt to user preferences over time
            # Example: await self.openmanus_client.send_experience(experience)

            # Save experiences to a local file for now (temporary solution)
            self._save_experiences_to_file()
        except Exception as e:
            logger.error(f"Error sending RL experience to OpenManus RL: {e}")

    def _save_experiences_to_file(self) -> None:
        """
        Save RL experiences to a local file.
        This is a temporary solution until OpenManus RL integration is implemented.
        """
        try:
            import os
            import json

            # Create directory if it doesn't exist
            os.makedirs('data/rl_experiences', exist_ok=True)

            # Save to file
            file_path = f'data/rl_experiences/{self._agent_id}_experiences.json'
            with open(file_path, 'w') as f:
                json.dump(self.rl_experiences, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving RL experiences to file: {e}")

    async def _find_bugs(self, code: Optional[str] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Find bugs in code.

        Args:
            code: The code to analyze
            language: The programming language

        Returns:
            Bug finding result
        """
        logger.info(f"Finding bugs in {language or 'unspecified'} language code")

        # In a real implementation, this would involve:
        # 1. Static code analysis
        # 2. Pattern matching for common bugs
        # 3. Semantic analysis

        # For now, we'll return a simple result
        return {
            'code_length': len(code) if code else 0,
            'language': language or 'python',
            'bugs_found': [
                {
                    'line': 3,
                    'description': 'Potential division by zero',
                    'severity': 'high'
                }
            ],
            'analysis_time': time.time()
        }