"""
McCoder Agent - Agent interface for the McCoder Code Intelligence System

This module provides an agent interface for the McCoder code intelligence system,
allowing it to be used as part of the DMac agent swarm.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple

from agents.base_agent import BaseAgent
from agents.mccoder.core import McCoder
from integrations.ollama_client import OllamaClient

# Set up logging
logger = logging.getLogger('dmac.mccoder.agent')

class McCoderAgent(BaseAgent):
    """
    Agent for code intelligence tasks using the McCoder system.
    """
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any] = None):
        """
        Initialize the McCoder agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            config: Configuration for the agent
        """
        super().__init__(agent_id, name, agent_type="code_assistant", config=config)
        
        # Default configuration
        self.default_config = {
            'project_root': os.getcwd(),
            'model_name': 'gemma3:12b',
            'max_context_length': 8192,
            'temperature': 0.7,
        }
        
        # Merge default config with provided config
        self.config = {**self.default_config, **(config or {})}
        
        # Initialize the model provider
        self.model_provider = OllamaModelProvider(
            model_name=self.config['model_name'],
            temperature=self.config['temperature']
        )
        
        # Initialize the McCoder instance
        self.mccoder = McCoder(
            project_root=self.config['project_root'],
            model_provider=self.model_provider
        )
        
        # Set up capabilities
        self.capabilities = [
            "code_search",
            "code_generation",
            "code_explanation",
            "code_refactoring",
            "bug_finding",
            "test_generation",
            "code_documentation",
            "project_analysis"
        ]
    
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
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'search_code':
                # Search for code
                query = data.get('query', content)
                results = self.mccoder.search_code(query)
                return {
                    'success': True,
                    'content': f"Found {len(results)} results for '{query}'",
                    'data': {'results': results},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'generate_code':
                # Generate code
                prompt = data.get('prompt', content)
                language = data.get('language')
                context = data.get('context')
                
                code = await self.model_provider.generate(
                    f"Generate {language or 'code'} for the following task:\n\n{prompt}" +
                    (f"\n\nContext:\n{context}" if context else "")
                )
                
                return {
                    'success': True,
                    'content': "Here's the generated code:",
                    'data': {'code': code},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'explain_code':
                # Explain code
                code = data.get('code', content)
                language = data.get('language')
                
                explanation = await self.model_provider.generate(
                    f"Explain the following {language or 'code'} in detail:\n\n```\n{code}\n```"
                )
                
                return {
                    'success': True,
                    'content': explanation,
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'refactor_code':
                # Refactor code
                code = data.get('code', '')
                instructions = data.get('instructions', content)
                language = data.get('language')
                
                prompt = f"Refactor the following {language or 'code'} according to these instructions:\n\n"
                prompt += f"Instructions: {instructions}\n\n"
                prompt += f"Code:\n```\n{code}\n```\n\n"
                prompt += "Please provide only the refactored code without explanations."
                
                refactored_code = await self.model_provider.generate(prompt)
                
                return {
                    'success': True,
                    'content': "Here's the refactored code:",
                    'data': {'refactored_code': refactored_code},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'find_bugs':
                # Find bugs in code
                code = data.get('code', content)
                language = data.get('language')
                
                prompt = f"Find potential bugs in the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
                prompt += "Format your response as a JSON array of objects with 'line', 'description', and 'severity' fields."
                
                response = await self.model_provider.generate(prompt)
                
                # Try to parse JSON from the response
                bugs = []
                try:
                    # Extract JSON array from the response
                    import re
                    json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
                    if json_match:
                        bugs = json.loads(json_match.group(0))
                except Exception as e:
                    logger.error(f"Error parsing bug report: {str(e)}")
                
                return {
                    'success': True,
                    'content': f"Found {len(bugs)} potential issues in the code.",
                    'data': {'bugs': bugs, 'raw_response': response},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'generate_tests':
                # Generate tests for code
                code = data.get('code', content)
                language = data.get('language')
                
                prompt = f"Generate unit tests for the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
                prompt += "Please provide comprehensive tests that cover all functionality."
                
                tests = await self.model_provider.generate(prompt)
                
                return {
                    'success': True,
                    'content': "Here are the generated tests:",
                    'data': {'tests': tests},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'document_code':
                # Document code
                code = data.get('code', content)
                language = data.get('language')
                
                prompt = f"Add comprehensive documentation to the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
                prompt += "Please include docstrings, comments, and type hints where appropriate."
                
                documented_code = await self.model_provider.generate(prompt)
                
                return {
                    'success': True,
                    'content': "Here's the documented code:",
                    'data': {'documented_code': documented_code},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'project_summary':
                # Get project summary
                summary = self.mccoder.get_project_summary()
                
                return {
                    'success': True,
                    'content': f"Project summary for {summary['project_root']}",
                    'data': {'summary': summary},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'refresh_index':
                # Refresh the code index
                self.mccoder.refresh_index()
                
                return {
                    'success': True,
                    'content': "Code index refreshed successfully.",
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            else:
                # Unknown action
                return {
                    'success': False,
                    'content': f"Unknown action: {action}",
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'success': False,
                'content': f"Error processing message: {str(e)}",
                'agent_id': self.agent_id,
                'agent_name': self.name
            }
    
    async def _handle_chat(self, content: str) -> str:
        """
        Handle a general chat message.
        
        Args:
            content: Message content
            
        Returns:
            Response text
        """
        # Analyze the message to determine the intent
        if any(keyword in content.lower() for keyword in ['search', 'find', 'look for']):
            # Search intent
            query = content.split('search for')[-1].split('find')[-1].split('look for')[-1].strip()
            results = self.mccoder.search_code(query)
            
            if results:
                response = f"I found {len(results)} results for '{query}':\n\n"
                for i, result in enumerate(results[:5], 1):
                    file_path = result.get('file', '')
                    if 'symbol' in result:
                        response += f"{i}. Symbol: {result['symbol']} ({result['type']}) in {file_path}\n"
                    else:
                        response += f"{i}. File: {file_path}\n"
                        if 'matches' in result:
                            for match in result['matches'][:2]:
                                response += f"   Line {match['line']}: {match['content']}\n"
                
                if len(results) > 5:
                    response += f"\nAnd {len(results) - 5} more results."
                
                return response
            else:
                return f"I couldn't find any code matching '{query}'. Try a different search term."
        
        elif any(keyword in content.lower() for keyword in ['generate', 'create', 'write']):
            # Code generation intent
            prompt = content
            
            # Try to detect the language
            language = None
            for lang in ['python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust']:
                if lang in content.lower():
                    language = lang
                    break
            
            code = await self.model_provider.generate(
                f"Generate {language or 'code'} for the following task:\n\n{prompt}"
            )
            
            return f"Here's the code I generated:\n\n```\n{code}\n```"
        
        elif any(keyword in content.lower() for keyword in ['explain', 'understand', 'what does']):
            # Code explanation intent
            # Check if there's code in the message (between backticks)
            import re
            code_match = re.search(r'```(.*?)```', content, re.DOTALL)
            
            if code_match:
                code = code_match.group(1).strip()
                explanation = await self.model_provider.generate(
                    f"Explain the following code in detail:\n\n```\n{code}\n```"
                )
                return explanation
            else:
                return "I'd be happy to explain code for you. Please include the code between triple backticks (```code```) so I can analyze it properly."
        
        else:
            # General chat
            prompt = f"You are McCoder, a code intelligence agent. Respond to the following message:\n\n{content}"
            response = await self.model_provider.generate(prompt)
            return response
    
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
        
        if task_type == 'code_analysis':
            # Analyze code
            code = task_data.get('code', '')
            language = task_data.get('language')
            
            prompt = f"Analyze the following {language or 'code'} and provide a detailed report:\n\n```\n{code}\n```\n\n"
            prompt += "Include information about code quality, potential issues, and suggestions for improvement."
            
            analysis = await self.model_provider.generate(prompt)
            
            return {
                'success': True,
                'result': analysis,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'code_review':
            # Review code changes
            code_before = task_data.get('code_before', '')
            code_after = task_data.get('code_after', '')
            language = task_data.get('language')
            
            prompt = f"Review the following code changes in {language or 'code'}:\n\n"
            prompt += f"Before:\n```\n{code_before}\n```\n\n"
            prompt += f"After:\n```\n{code_after}\n```\n\n"
            prompt += "Provide a detailed review of the changes, including potential issues and suggestions."
            
            review = await self.model_provider.generate(prompt)
            
            return {
                'success': True,
                'result': review,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'code_generation':
            # Generate code based on specifications
            specifications = task_data.get('specifications', '')
            language = task_data.get('language')
            
            prompt = f"Generate {language or 'code'} based on the following specifications:\n\n{specifications}"
            
            code = await self.model_provider.generate(prompt)
            
            return {
                'success': True,
                'result': code,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        else:
            # Unknown task type
            return {
                'success': False,
                'result': f"Unknown task type: {task_type}",
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the agent.
        
        Returns:
            Agent status
        """
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'type': 'code_assistant',
            'status': 'active',
            'capabilities': self.capabilities,
            'project_root': self.config['project_root'],
            'model_name': self.config['model_name'],
            'file_count': len(self.mccoder.file_index),
            'symbol_count': len(self.mccoder.symbol_index)
        }
    
    def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the agent configuration.
        
        Args:
            config: New configuration
            
        Returns:
            Updated configuration
        """
        # Update configuration
        self.config.update(config)
        
        # Update model provider if model name changed
        if 'model_name' in config:
            self.model_provider = OllamaModelProvider(
                model_name=self.config['model_name'],
                temperature=self.config['temperature']
            )
            self.mccoder.model_provider = self.model_provider
        
        # Update project root if changed
        if 'project_root' in config:
            self.mccoder = McCoder(
                project_root=self.config['project_root'],
                model_provider=self.model_provider
            )
        
        return self.config

class OllamaModelProvider:
    """Model provider using Ollama for LLM capabilities."""
    
    def __init__(self, model_name: str = "gemma3:12b", temperature: float = 0.7):
        """
        Initialize the Ollama model provider.
        
        Args:
            model_name: Name of the Ollama model to use
            temperature: Temperature for generation
        """
        self.model_name = model_name
        self.temperature = temperature
        self.ollama_client = OllamaClient()
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text using the Ollama model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        try:
            result = await self.ollama_client.generate(
                self.model_name, 
                prompt,
                temperature=self.temperature
            )
            
            if 'error' in result:
                logger.error(f"Error generating text: {result['error']}")
                return f"Error: {result['error']}"
            
            return result.get('text', "")
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: {str(e)}"
