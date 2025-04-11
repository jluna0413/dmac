"""
Technical Writer Agent - Agent for creating and managing documentation

This module provides an agent for creating, editing, and managing technical documentation,
including API docs, user guides, and other technical content.
"""

import logging
import json
import os
import re
import time
from typing import Dict, List, Any, Optional, Tuple
import asyncio

from agents.base_agent import BaseAgent
from integrations.ollama_client import OllamaClient

# Set up logging
logger = logging.getLogger('dmac.writer.agent')

class WriterAgent(BaseAgent):
    """
    Agent for creating and managing technical documentation.
    """
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any] = None):
        """
        Initialize the Writer agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            config: Configuration for the agent
        """
        super().__init__(agent_id, name, agent_type="writer", config=config)
        
        # Default configuration
        self.default_config = {
            'model_name': 'gemma3:12b',
            'temperature': 0.7,
            'default_format': 'markdown',
            'docs_directory': 'docs',
            'templates_directory': 'templates/docs',
            'max_context_length': 8192
        }
        
        # Merge default config with provided config
        self.config = {**self.default_config, **(config or {})}
        
        # Initialize the model provider
        self.model_provider = OllamaModelProvider(
            model_name=self.config['model_name'],
            temperature=self.config['temperature']
        )
        
        # Create docs directory if it doesn't exist
        os.makedirs(self.config['docs_directory'], exist_ok=True)
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.config['templates_directory'], exist_ok=True)
        
        # Set up capabilities
        self.capabilities = [
            "documentation_generation",
            "api_documentation",
            "user_guide_creation",
            "readme_generation",
            "code_documentation",
            "technical_writing",
            "content_editing"
        ]
        
        # Active writing tasks
        self.active_tasks = {}
        
        # Document templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """
        Load document templates from the templates directory.
        
        Returns:
            Dictionary of templates
        """
        templates = {}
        
        # Check if templates directory exists
        if not os.path.exists(self.config['templates_directory']):
            return templates
        
        # Load templates
        for filename in os.listdir(self.config['templates_directory']):
            if filename.endswith('.md') or filename.endswith('.txt'):
                template_name = os.path.splitext(filename)[0]
                template_path = os.path.join(self.config['templates_directory'], filename)
                
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        templates[template_name] = f.read()
                except Exception as e:
                    logger.error(f"Error loading template {template_name}: {str(e)}")
        
        # If no templates found, create default templates
        if not templates:
            # Create default README template
            readme_template = """# {project_name}

{project_description}

## Features

{features}

## Installation

{installation_instructions}

## Usage

{usage_examples}

## API Reference

{api_reference}

## Contributing

{contributing_guidelines}

## License

{license_information}
"""
            templates['readme'] = readme_template
            
            # Create default API documentation template
            api_doc_template = """# {api_name} API Documentation

{api_description}

## Base URL

{base_url}

## Authentication

{authentication_details}

## Endpoints

{endpoints}

## Error Codes

{error_codes}

## Rate Limiting

{rate_limiting}

## Examples

{examples}
"""
            templates['api_documentation'] = api_doc_template
            
            # Create default user guide template
            user_guide_template = """# {product_name} User Guide

{product_description}

## Getting Started

{getting_started}

## Features

{features}

## Tutorials

{tutorials}

## Troubleshooting

{troubleshooting}

## FAQ

{faq}
"""
            templates['user_guide'] = user_guide_template
            
            # Save default templates
            for template_name, template_content in templates.items():
                template_path = os.path.join(self.config['templates_directory'], f"{template_name}.md")
                
                try:
                    with open(template_path, 'w', encoding='utf-8') as f:
                        f.write(template_content)
                except Exception as e:
                    logger.error(f"Error saving template {template_name}: {str(e)}")
        
        return templates
    
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
            
            elif action == 'generate_documentation':
                # Generate documentation
                doc_type = data.get('doc_type', 'general')
                content_data = data.get('content_data', {})
                format = data.get('format', self.config['default_format'])
                
                # Generate the documentation
                documentation = await self._generate_documentation(doc_type, content_data, format)
                
                return {
                    'success': True,
                    'content': "Here's the generated documentation:",
                    'data': {'documentation': documentation},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'document_code':
                # Document code
                code = data.get('code', '')
                language = data.get('language', '')
                format = data.get('format', self.config['default_format'])
                
                if not code:
                    return {
                        'success': False,
                        'content': "Please provide code to document.",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                
                # Document the code
                documentation = await self._document_code(code, language, format)
                
                return {
                    'success': True,
                    'content': "Here's the code documentation:",
                    'data': {'documentation': documentation},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'create_readme':
                # Create a README file
                project_info = data.get('project_info', {})
                format = data.get('format', self.config['default_format'])
                
                if not project_info:
                    return {
                        'success': False,
                        'content': "Please provide project information to create a README.",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                
                # Create the README
                readme = await self._create_readme(project_info, format)
                
                return {
                    'success': True,
                    'content': "Here's the generated README:",
                    'data': {'readme': readme},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'edit_document':
                # Edit a document
                document = data.get('document', '')
                instructions = data.get('instructions', '')
                
                if not document:
                    return {
                        'success': False,
                        'content': "Please provide a document to edit.",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                
                if not instructions:
                    return {
                        'success': False,
                        'content': "Please provide editing instructions.",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                
                # Edit the document
                edited_document = await self._edit_document(document, instructions)
                
                return {
                    'success': True,
                    'content': "Here's the edited document:",
                    'data': {'edited_document': edited_document},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'save_document':
                # Save a document to disk
                document = data.get('document', '')
                filename = data.get('filename', '')
                
                if not document:
                    return {
                        'success': False,
                        'content': "Please provide a document to save.",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                
                if not filename:
                    return {
                        'success': False,
                        'content': "Please provide a filename.",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                
                # Save the document
                success = await self._save_document(document, filename)
                
                if success:
                    return {
                        'success': True,
                        'content': f"Document saved to {filename}",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                else:
                    return {
                        'success': False,
                        'content': f"Failed to save document to {filename}",
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
        if any(keyword in content.lower() for keyword in ['document', 'documentation', 'docs']):
            # Documentation intent
            if 'code' in content.lower() or 'function' in content.lower() or 'class' in content.lower():
                # Code documentation intent
                # Extract code if present
                code_match = re.search(r'```(.*?)```', content, re.DOTALL)
                
                if code_match:
                    code = code_match.group(1).strip()
                    language = ''
                    
                    # Try to detect language
                    language_match = re.match(r'```(\w+)', content)
                    if language_match:
                        language = language_match.group(1)
                    
                    # Document the code
                    documentation = await self._document_code(code, language, self.config['default_format'])
                    
                    return f"Here's the documentation for your code:\n\n{documentation}"
                else:
                    return "I'd be happy to document your code. Please share the code you'd like me to document, preferably enclosed in triple backticks (```code```)."
            
            elif 'readme' in content.lower() or 'project' in content.lower():
                # README generation intent
                return "I can help you create a README for your project. Please provide some information about your project, such as its name, description, features, and installation instructions."
            
            elif 'api' in content.lower():
                # API documentation intent
                return "I can help you create API documentation. Please provide details about your API, including endpoints, parameters, responses, and examples."
            
            else:
                # General documentation intent
                return "I can help you create various types of documentation. What specific type of documentation do you need? For example, I can create READMEs, API docs, user guides, or code documentation."
        
        elif any(keyword in content.lower() for keyword in ['edit', 'revise', 'improve']):
            # Document editing intent
            # Check if there's a document in the message
            doc_match = re.search(r'```(.*?)```', content, re.DOTALL)
            
            if doc_match:
                document = doc_match.group(1).strip()
                
                # Extract editing instructions
                instructions = content.replace(doc_match.group(0), '').strip()
                
                # Edit the document
                edited_document = await self._edit_document(document, instructions)
                
                return f"Here's the edited document:\n\n{edited_document}"
            else:
                return "I'd be happy to edit a document for you. Please share the document you'd like me to edit, preferably enclosed in triple backticks (```document```), along with your editing instructions."
        
        else:
            # General chat
            prompt = f"You are Doc Doug, a technical writing assistant. Respond to the following message:\n\n{content}"
            response = await self.model_provider.generate(prompt)
            return response
    
    async def _generate_documentation(self, doc_type: str, content_data: Dict[str, Any], format: str) -> str:
        """
        Generate documentation based on the provided data.
        
        Args:
            doc_type: Type of documentation to generate
            content_data: Data for the documentation
            format: Format of the documentation
            
        Returns:
            Generated documentation
        """
        # Check if we have a template for this doc type
        template = self.templates.get(doc_type)
        
        if template:
            # Use the template
            try:
                # Replace placeholders in the template
                documentation = template
                
                for key, value in content_data.items():
                    placeholder = f"{{{key}}}"
                    documentation = documentation.replace(placeholder, str(value))
                
                return documentation
            except Exception as e:
                logger.error(f"Error applying template for {doc_type}: {str(e)}")
                # Fall back to generation without template
        
        # Generate documentation without a template
        prompt = f"Generate {doc_type} documentation in {format} format based on the following information:\n\n"
        
        for key, value in content_data.items():
            prompt += f"{key}: {value}\n"
        
        prompt += f"\nCreate comprehensive, well-structured {doc_type} documentation that covers all the provided information."
        
        # Generate the documentation
        documentation = await self.model_provider.generate(prompt)
        
        return documentation
    
    async def _document_code(self, code: str, language: str, format: str) -> str:
        """
        Generate documentation for code.
        
        Args:
            code: Code to document
            language: Programming language of the code
            format: Format of the documentation
            
        Returns:
            Generated documentation
        """
        # Create a prompt for the model
        prompt = f"Document the following {language} code in {format} format:\n\n```{language}\n{code}\n```\n\n"
        prompt += "Include the following in your documentation:\n"
        prompt += "1. Overview of what the code does\n"
        prompt += "2. Description of functions, classes, and methods\n"
        prompt += "3. Parameters and return values\n"
        prompt += "4. Examples of usage\n"
        prompt += "5. Any dependencies or requirements\n\n"
        prompt += "Make the documentation comprehensive, clear, and following best practices for technical documentation."
        
        # Generate the documentation
        documentation = await self.model_provider.generate(prompt)
        
        return documentation
    
    async def _create_readme(self, project_info: Dict[str, Any], format: str) -> str:
        """
        Create a README file for a project.
        
        Args:
            project_info: Information about the project
            format: Format of the README
            
        Returns:
            Generated README
        """
        # Check if we have a README template
        template = self.templates.get('readme')
        
        if template:
            # Use the template
            try:
                # Replace placeholders in the template
                readme = template
                
                for key, value in project_info.items():
                    placeholder = f"{{{key}}}"
                    readme = readme.replace(placeholder, str(value))
                
                return readme
            except Exception as e:
                logger.error(f"Error applying README template: {str(e)}")
                # Fall back to generation without template
        
        # Generate README without a template
        prompt = f"Create a README file in {format} format for a project with the following information:\n\n"
        
        for key, value in project_info.items():
            prompt += f"{key}: {value}\n"
        
        prompt += "\nCreate a comprehensive, well-structured README that includes:\n"
        prompt += "1. Project name and description\n"
        prompt += "2. Features\n"
        prompt += "3. Installation instructions\n"
        prompt += "4. Usage examples\n"
        prompt += "5. API reference (if applicable)\n"
        prompt += "6. Contributing guidelines\n"
        prompt += "7. License information\n\n"
        prompt += "Follow best practices for README files and make it clear and informative."
        
        # Generate the README
        readme = await self.model_provider.generate(prompt)
        
        return readme
    
    async def _edit_document(self, document: str, instructions: str) -> str:
        """
        Edit a document based on instructions.
        
        Args:
            document: Document to edit
            instructions: Editing instructions
            
        Returns:
            Edited document
        """
        # Create a prompt for the model
        prompt = f"Edit the following document according to these instructions:\n\n"
        prompt += f"Instructions: {instructions}\n\n"
        prompt += f"Document:\n```\n{document}\n```\n\n"
        prompt += "Provide the edited document, maintaining the original format and structure unless the instructions specify otherwise."
        
        # Generate the edited document
        edited_document = await self.model_provider.generate(prompt)
        
        return edited_document
    
    async def _save_document(self, document: str, filename: str) -> bool:
        """
        Save a document to disk.
        
        Args:
            document: Document to save
            filename: Name of the file to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure the filename has an extension
            if not filename.endswith('.md') and not filename.endswith('.txt'):
                filename += '.md'
            
            # Create the full path
            file_path = os.path.join(self.config['docs_directory'], filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the document
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(document)
            
            logger.info(f"Document saved to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving document to {filename}: {str(e)}")
            return False
    
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
        
        if task_type == 'generate_documentation':
            # Generate documentation
            doc_type = task_data.get('doc_type', 'general')
            content_data = task_data.get('content_data', {})
            format = task_data.get('format', self.config['default_format'])
            
            # Generate the documentation
            documentation = await self._generate_documentation(doc_type, content_data, format)
            
            return {
                'success': True,
                'result': documentation,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'document_code':
            # Document code
            code = task_data.get('code', '')
            language = task_data.get('language', '')
            format = task_data.get('format', self.config['default_format'])
            
            if not code:
                return {
                    'success': False,
                    'result': "No code provided for documentation task",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            
            # Document the code
            documentation = await self._document_code(code, language, format)
            
            return {
                'success': True,
                'result': documentation,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'create_readme':
            # Create a README file
            project_info = task_data.get('project_info', {})
            format = task_data.get('format', self.config['default_format'])
            
            if not project_info:
                return {
                    'success': False,
                    'result': "No project information provided for README task",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            
            # Create the README
            readme = await self._create_readme(project_info, format)
            
            return {
                'success': True,
                'result': readme,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'edit_document':
            # Edit a document
            document = task_data.get('document', '')
            instructions = task_data.get('instructions', '')
            
            if not document:
                return {
                    'success': False,
                    'result': "No document provided for editing task",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            
            if not instructions:
                return {
                    'success': False,
                    'result': "No editing instructions provided",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            
            # Edit the document
            edited_document = await self._edit_document(document, instructions)
            
            return {
                'success': True,
                'result': edited_document,
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
            'type': 'writer',
            'status': 'active',
            'capabilities': self.capabilities,
            'model_name': self.config['model_name'],
            'active_tasks': len(self.active_tasks),
            'templates': list(self.templates.keys())
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
        
        # Create docs directory if it doesn't exist
        if 'docs_directory' in config:
            os.makedirs(self.config['docs_directory'], exist_ok=True)
        
        # Create templates directory if it doesn't exist
        if 'templates_directory' in config:
            os.makedirs(self.config['templates_directory'], exist_ok=True)
            # Reload templates
            self.templates = self._load_templates()
        
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
