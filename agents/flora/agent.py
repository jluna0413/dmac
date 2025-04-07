"""
Flora - Frontend Developer Agent

This agent specializes in frontend development, UI/UX design, and
creating responsive web interfaces.
"""

import os
import json
import logging
import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple

from utils.secure_logging import get_logger
from agents.base_agent import BaseAgent
from models.model_provider import OllamaModelProvider
from config.config import config

logger = get_logger('dmac.agents.flora')

class FloraAgent(BaseAgent):
    """Frontend Developer agent for DMac."""

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the frontend developer agent.

        Args:
            agent_id: Unique identifier for the agent. If not provided, a UUID will be generated.
            config: Configuration for the agent.
        """
        super().__init__(agent_id or "flora", "FrontendDeveloper", "Agent for frontend development and UI/UX design")

        # Default configuration
        self.default_config = {
            'model_name': 'gemma:7b',
            'temperature': 0.7,
            'component_templates_dir': os.path.join('data', 'component_templates'),
            'ui_output_dir': os.path.join('data', 'ui_components'),
            'design_history_dir': os.path.join('data', 'design_history'),
            'max_history_items': 100,
            'supported_frameworks': ['react', 'vue', 'angular', 'html_css']
        }

        # Merge default config with provided config
        self.config = {**self.default_config, **(config or {})}

        # Initialize the model provider
        self.model_provider = OllamaModelProvider(
            model_name=self.config['model_name'],
            temperature=self.config['temperature']
        )

        # Create directories if they don't exist
        os.makedirs(self.config['component_templates_dir'], exist_ok=True)
        os.makedirs(self.config['ui_output_dir'], exist_ok=True)
        os.makedirs(self.config['design_history_dir'], exist_ok=True)

        # Set up capabilities
        self.capabilities = [
            "component_creation",
            "ui_design",
            "css_styling",
            "responsive_design",
            "accessibility_review",
            "animation_creation",
            "design_system_implementation",
            "ui_prototyping"
        ]

        # Load component templates
        self.component_templates = self._load_component_templates()

        logger.info(f"Flora Frontend Developer agent initialized with {len(self.component_templates)} templates")

    def _load_component_templates(self) -> Dict[str, Any]:
        """Load component templates from the templates directory.

        Returns:
            Dictionary of component templates.
        """
        templates = {}
        template_dir = self.config['component_templates_dir']

        if not os.path.exists(template_dir):
            return templates

        for framework in self.config['supported_frameworks']:
            framework_dir = os.path.join(template_dir, framework)
            if not os.path.exists(framework_dir):
                continue

            templates[framework] = {}

            for filename in os.listdir(framework_dir):
                if os.path.isfile(os.path.join(framework_dir, filename)):
                    try:
                        with open(os.path.join(framework_dir, filename), 'r') as f:
                            template_content = f.read()
                            template_id = os.path.splitext(filename)[0]
                            templates[framework][template_id] = {
                                'filename': filename,
                                'content': template_content
                            }
                    except Exception as e:
                        logger.error(f"Error loading component template {filename}: {str(e)}")

        return templates

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message sent to the agent.

        Args:
            message: Message to process

        Returns:
            Response message
        """
        prompt = message.get('prompt', '')
        task_type = message.get('task_type', 'component_creation')

        if task_type == 'component_creation':
            framework = message.get('framework', 'react')
            result = await self.create_component(prompt, framework)
        elif task_type == 'ui_design':
            style = message.get('style', 'material')
            result = await self.design_ui(prompt, style)
        elif task_type == 'css_styling':
            result = await self.create_css(prompt)
        elif task_type == 'accessibility_review':
            code = message.get('code', '')
            result = await self.review_accessibility(code)
        else:
            result = await self.create_component(prompt)

        return {
            'success': True,
            'result': result,
            'agent_id': self.agent_id
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task assigned to the agent.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        task_type = task.get('type', '')
        task_data = task.get('data', {})

        if task_type == 'create_component':
            description = task_data.get('description', '')
            framework = task_data.get('framework', 'react')

            component = await self.create_component(description, framework)

            return {
                'success': True,
                'result': component,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }

        elif task_type == 'design_ui':
            description = task_data.get('description', '')
            style = task_data.get('style', 'material')

            ui_design = await self.design_ui(description, style)

            return {
                'success': True,
                'result': ui_design,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }

        elif task_type == 'create_css':
            description = task_data.get('description', '')

            css = await self.create_css(description)

            return {
                'success': True,
                'result': css,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }

        elif task_type == 'review_accessibility':
            code = task_data.get('code', '')

            review = await self.review_accessibility(code)

            return {
                'success': True,
                'result': review,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }

        else:
            return {
                'success': False,
                'error': f"Unknown task type: {task_type}",
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }

    async def create_component(self, description: str, framework: str = 'react') -> str:
        """Create a UI component based on the description.

        Args:
            description: Description of the component to create
            framework: Frontend framework to use (react, vue, angular)

        Returns:
            Component code with explanation
        """
        if framework not in self.config['supported_frameworks']:
            framework = 'react'  # Default to React if framework not supported

        system_prompt = f"""You are Flora, an expert frontend developer. Your task is to create a {framework} component based on the description provided.
Follow these guidelines:
1. Use modern {framework} best practices and patterns
2. Create clean, maintainable, and reusable code
3. Consider accessibility and responsive design
4. Include proper comments and documentation
5. Follow a component-based architecture"""

        user_prompt = f"""Create a {framework} component that meets the following requirements:
Description: {description}

Your response should include:
1. The complete component code with proper formatting
2. An explanation of the component's structure and functionality
3. Any props or inputs the component accepts
4. Usage examples
5. Considerations for accessibility and responsiveness"""

        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Extract the component code from the response
        component_code = self._extract_code_from_response(response, framework)

        # Save the component to a file
        if component_code:
            extension = self._get_file_extension(framework)
            filename = f"component_{self.agent_id}_{int(asyncio.get_event_loop().time())}{extension}"
            filepath = os.path.join(self.config['ui_output_dir'], filename)

            with open(filepath, 'w') as f:
                f.write(component_code)

            # Add the filepath to the response
            response += f"\n\nComponent saved to: {filepath}"

        # Save to history
        self._save_to_history('create_component', {
            'description': description,
            'framework': framework,
            'result': response,
            'component_path': filepath if component_code else None
        })

        return response

    async def design_ui(self, description: str, style: str = 'material') -> str:
        """Design a UI layout based on the description.

        Args:
            description: Description of the UI to design
            style: Design style (material, ios, custom, etc.)

        Returns:
            UI design with explanation and code
        """
        system_prompt = f"""You are Flora, an expert UI/UX designer and frontend developer. Your task is to design a UI layout in {style} style based on the description provided.
Follow these guidelines:
1. Apply {style} design principles and patterns
2. Create a clean, intuitive, and visually appealing layout
3. Consider user experience and interaction flow
4. Ensure the design is accessible and responsive
5. Provide both visual description and implementation code"""

        user_prompt = f"""Design a UI layout in {style} style that meets the following requirements:
Description: {description}

Your response should include:
1. A detailed description of the UI layout and components
2. The HTML and CSS code to implement the design
3. Explanation of design choices and user experience considerations
4. Responsive design approach for different screen sizes
5. Accessibility features incorporated into the design"""

        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Extract the HTML and CSS code from the response
        html_code = self._extract_code_from_response(response, 'html')
        css_code = self._extract_code_from_response(response, 'css')

        # Save the design to files
        if html_code and css_code:
            timestamp = int(asyncio.get_event_loop().time())
            html_filename = f"design_{self.agent_id}_{timestamp}.html"
            css_filename = f"design_{self.agent_id}_{timestamp}.css"

            html_filepath = os.path.join(self.config['ui_output_dir'], html_filename)
            css_filepath = os.path.join(self.config['ui_output_dir'], css_filename)

            with open(html_filepath, 'w') as f:
                f.write(html_code)

            with open(css_filepath, 'w') as f:
                f.write(css_code)

            # Add the filepaths to the response
            response += f"\n\nHTML saved to: {html_filepath}\nCSS saved to: {css_filepath}"

        # Save to history
        self._save_to_history('design_ui', {
            'description': description,
            'style': style,
            'result': response,
            'html_path': html_filepath if html_code else None,
            'css_path': css_filepath if css_code else None
        })

        return response

    async def create_css(self, description: str) -> str:
        """Create CSS styles based on the description.

        Args:
            description: Description of the styles to create

        Returns:
            CSS code with explanation
        """
        system_prompt = """You are Flora, an expert frontend developer specializing in CSS. Your task is to create CSS styles based on the description provided.
Follow these guidelines:
1. Use modern CSS best practices (Flexbox, Grid, CSS Variables)
2. Create clean, maintainable, and reusable styles
3. Consider browser compatibility and performance
4. Include proper comments and documentation
5. Implement responsive design principles"""

        user_prompt = f"""Create CSS styles that meet the following requirements:
Description: {description}

Your response should include:
1. The complete CSS code with proper formatting and comments
2. An explanation of the styling approach and techniques used
3. Any variables or custom properties defined
4. Browser compatibility considerations
5. Responsive design implementation details"""

        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Extract the CSS code from the response
        css_code = self._extract_code_from_response(response, 'css')

        # Save the CSS to a file
        if css_code:
            filename = f"styles_{self.agent_id}_{int(asyncio.get_event_loop().time())}.css"
            filepath = os.path.join(self.config['ui_output_dir'], filename)

            with open(filepath, 'w') as f:
                f.write(css_code)

            # Add the filepath to the response
            response += f"\n\nCSS saved to: {filepath}"

        # Save to history
        self._save_to_history('create_css', {
            'description': description,
            'result': response,
            'css_path': filepath if css_code else None
        })

        return response

    async def review_accessibility(self, code: str) -> str:
        """Review code for accessibility issues.

        Args:
            code: HTML/CSS/JS code to review

        Returns:
            Accessibility review with recommendations
        """
        system_prompt = """You are Flora, an expert frontend developer specializing in accessibility. Your task is to review the provided code for accessibility issues and provide recommendations.
Follow these guidelines:
1. Check for WCAG 2.1 compliance issues
2. Identify missing aria attributes or roles
3. Evaluate keyboard navigation and focus management
4. Check color contrast and text readability
5. Provide specific, actionable recommendations"""

        user_prompt = f"""Review the following code for accessibility issues:
```
{code}
```

Your review should include:
1. Identified accessibility issues with severity levels
2. Specific code locations where issues occur
3. Recommendations for fixing each issue
4. Code examples of the fixes
5. General accessibility best practices relevant to this code"""

        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Save to history
        self._save_to_history('review_accessibility', {
            'code_length': len(code),
            'result': response
        })

        return response

    def _extract_code_from_response(self, response: str, language: str) -> Optional[str]:
        """Extract code of a specific language from the model's response.

        Args:
            response: Full response from the model
            language: Language to extract (react, vue, html, css, etc.)

        Returns:
            Extracted code or None if not found
        """
        # Look for code blocks with the language
        import re

        # Try to find code blocks with ```language
        code_block_pattern = r'```(?:' + language + r'|' + language.lower() + r'|' + language.upper() + r')?\s*(.*?)```'
        code_blocks = re.findall(code_block_pattern, response, re.DOTALL)

        if code_blocks:
            # Return the largest code block (most likely the full component)
            return max(code_blocks, key=len).strip()

        return None

    def _get_file_extension(self, framework: str) -> str:
        """Get the appropriate file extension for a framework.

        Args:
            framework: Frontend framework

        Returns:
            File extension including the dot
        """
        extensions = {
            'react': '.jsx',
            'vue': '.vue',
            'angular': '.component.ts',

            'html_css': '.html',
            'html': '.html',
            'css': '.css',
            'js': '.js',
            'typescript': '.ts'
        }

        return extensions.get(framework.lower(), '.txt')

    def _save_to_history(self, action_type: str, data: Dict[str, Any]) -> None:
        """Save an action to the design history.

        Args:
            action_type: Type of action
            data: Data associated with the action
        """
        history_dir = self.config['design_history_dir']

        # Create a history entry
        history_entry = {
            'timestamp': asyncio.get_event_loop().time(),
            'agent_id': self.agent_id,
            'action_type': action_type,
            'data': data
        }

        # Generate a filename
        filename = f"{action_type}_{self.agent_id}_{int(history_entry['timestamp'])}.json"
        filepath = os.path.join(history_dir, filename)

        # Save the entry
        with open(filepath, 'w') as f:
            json.dump(history_entry, f, indent=2)

        # Cleanup old history if needed
        self._cleanup_history()

    def _cleanup_history(self) -> None:
        """Clean up old history entries if there are too many."""
        history_dir = self.config['design_history_dir']
        max_items = self.config['max_history_items']

        # Get all history files
        history_files = [
            os.path.join(history_dir, f)
            for f in os.listdir(history_dir)
            if f.endswith('.json')
        ]

        # Sort by modification time (oldest first)
        history_files.sort(key=lambda f: os.path.getmtime(f))

        # Remove oldest files if there are too many
        if len(history_files) > max_items:
            for file_to_remove in history_files[:len(history_files) - max_items]:
                try:
                    os.remove(file_to_remove)
                    logger.debug(f"Removed old history file: {file_to_remove}")
                except Exception as e:
                    logger.error(f"Error removing history file {file_to_remove}: {str(e)}")
