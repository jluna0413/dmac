"""
Shelly - Shell/Command Line Specialist Agent

This agent specializes in shell scripting, command-line operations, and
system administration tasks.
"""

import os
import json
import logging
import asyncio
import subprocess
import shlex
from typing import Dict, Any, List, Optional, Tuple

from utils.secure_logging import get_logger
from agents.base_agent import BaseAgent
from models.model_provider import OllamaModelProvider
from config.config import config

logger = get_logger('dmac.agents.shelly')

class ShellyAgent(BaseAgent):
    """Shell/Command Line Specialist agent for DMac."""
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the shell specialist agent.
        
        Args:
            agent_id: Unique identifier for the agent. If not provided, a UUID will be generated.
            config: Configuration for the agent.
        """
        super().__init__(agent_id or "shelly", "ShellSpecialist", "Agent for shell scripting and command-line operations")
        
        # Default configuration
        self.default_config = {
            'model_name': 'gemma:7b',
            'temperature': 0.2,
            'script_templates_dir': os.path.join('data', 'script_templates'),
            'script_output_dir': os.path.join('data', 'scripts'),
            'command_history_dir': os.path.join('data', 'command_history'),
            'max_history_items': 100,
            'max_execution_time': 30,  # seconds
            'allowed_commands': ['ls', 'dir', 'find', 'grep', 'cat', 'head', 'tail', 'echo', 'ps'],
            'disallowed_commands': ['rm', 'del', 'rmdir', 'format', 'shutdown', 'reboot'],
            'sandbox_enabled': True
        }
        
        # Merge default config with provided config
        self.config = {**self.default_config, **(config or {})}
        
        # Initialize the model provider
        self.model_provider = OllamaModelProvider(
            model_name=self.config['model_name'],
            temperature=self.config['temperature']
        )
        
        # Create directories if they don't exist
        os.makedirs(self.config['script_templates_dir'], exist_ok=True)
        os.makedirs(self.config['script_output_dir'], exist_ok=True)
        os.makedirs(self.config['command_history_dir'], exist_ok=True)
        
        # Set up capabilities
        self.capabilities = [
            "command_generation",
            "script_creation",
            "command_explanation",
            "system_diagnostics",
            "file_operations",
            "process_management",
            "text_processing",
            "system_monitoring"
        ]
        
        # Load script templates
        self.script_templates = self._load_script_templates()
        
        logger.info(f"Shelly Shell Specialist agent initialized with {len(self.script_templates)} templates")
    
    def _load_script_templates(self) -> Dict[str, Any]:
        """Load script templates from the templates directory.
        
        Returns:
            Dictionary of script templates.
        """
        templates = {}
        template_dir = self.config['script_templates_dir']
        
        if not os.path.exists(template_dir):
            return templates
        
        for filename in os.listdir(template_dir):
            if filename.endswith('.sh') or filename.endswith('.bat') or filename.endswith('.ps1'):
                try:
                    with open(os.path.join(template_dir, filename), 'r') as f:
                        template_content = f.read()
                        template_id = os.path.splitext(filename)[0]
                        templates[template_id] = {
                            'filename': filename,
                            'content': template_content
                        }
                except Exception as e:
                    logger.error(f"Error loading script template {filename}: {str(e)}")
        
        return templates
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message sent to the agent.
        
        Args:
            message: Message to process
            
        Returns:
            Response message
        """
        prompt = message.get('prompt', '')
        task_type = message.get('task_type', 'command_generation')
        
        if task_type == 'command_generation':
            result = await self.generate_command(prompt)
        elif task_type == 'script_creation':
            result = await self.create_script(prompt)
        elif task_type == 'command_explanation':
            result = await self.explain_command(prompt)
        elif task_type == 'system_diagnostics':
            result = await self.diagnose_system(prompt)
        else:
            result = await self.generate_command(prompt)
        
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
        
        if task_type == 'generate_command':
            description = task_data.get('description', '')
            platform = task_data.get('platform', self._detect_platform())
            
            command = await self.generate_command(description, platform)
            
            return {
                'success': True,
                'result': command,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'create_script':
            description = task_data.get('description', '')
            platform = task_data.get('platform', self._detect_platform())
            script_type = task_data.get('script_type', 'bash')
            
            script = await self.create_script(description, platform, script_type)
            
            return {
                'success': True,
                'result': script,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'explain_command':
            command = task_data.get('command', '')
            
            explanation = await self.explain_command(command)
            
            return {
                'success': True,
                'result': explanation,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'execute_command':
            command = task_data.get('command', '')
            
            # Validate the command for safety
            is_safe, reason = self._validate_command_safety(command)
            
            if not is_safe:
                return {
                    'success': False,
                    'error': f"Command execution rejected: {reason}",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            
            # Execute the command
            success, output = await self._execute_command(command)
            
            return {
                'success': success,
                'result': output,
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
    
    async def generate_command(self, description: str, platform: str = None) -> str:
        """Generate a shell command based on the description.
        
        Args:
            description: Description of what the command should do
            platform: Target platform (linux, windows, macos)
            
        Returns:
            Generated command with explanation
        """
        if platform is None:
            platform = self._detect_platform()
        
        system_prompt = f"""You are Shelly, an expert in shell scripting and command-line operations. Your task is to generate a command for {platform} based on the description provided.
Follow these guidelines:
1. Be precise and efficient in your command generation
2. Consider platform-specific syntax and tools
3. Prioritize safety and avoid destructive operations
4. Use proper quoting and escaping
5. Consider error handling where appropriate"""
        
        user_prompt = f"""Generate a command for {platform} that accomplishes the following:
Description: {description}

Your response should include:
1. The exact command to run
2. A brief explanation of how the command works
3. Any potential issues or limitations to be aware of
4. Alternative approaches if relevant"""
        
        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Save to history
        self._save_to_history('generate_command', {
            'description': description,
            'platform': platform,
            'result': response
        })
        
        return response
    
    async def create_script(self, description: str, platform: str = None, script_type: str = 'bash') -> str:
        """Create a shell script based on the description.
        
        Args:
            description: Description of what the script should do
            platform: Target platform (linux, windows, macos)
            script_type: Type of script (bash, powershell, batch)
            
        Returns:
            Generated script with explanation
        """
        if platform is None:
            platform = self._detect_platform()
        
        # Determine script type based on platform if not specified
        if script_type == 'auto':
            if platform == 'windows':
                script_type = 'powershell'
            else:
                script_type = 'bash'
        
        system_prompt = f"""You are Shelly, an expert in shell scripting and command-line operations. Your task is to create a {script_type} script for {platform} based on the description provided.
Follow these guidelines:
1. Include proper shebang line and comments
2. Structure the script with clear sections and error handling
3. Use platform-appropriate commands and syntax
4. Include input validation and error checking
5. Add helpful comments explaining complex operations"""
        
        user_prompt = f"""Create a {script_type} script for {platform} that accomplishes the following:
Description: {description}

Your response should include:
1. The complete script with proper formatting and comments
2. Instructions for running the script
3. An explanation of how the script works
4. Any dependencies or requirements"""
        
        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Extract the script from the response
        script_content = self._extract_script_from_response(response, script_type)
        
        # Save the script to a file
        if script_content:
            extension = self._get_script_extension(script_type)
            filename = f"script_{self.agent_id}_{int(asyncio.get_event_loop().time())}{extension}"
            filepath = os.path.join(self.config['script_output_dir'], filename)
            
            with open(filepath, 'w') as f:
                f.write(script_content)
            
            # Add the filepath to the response
            response += f"\n\nScript saved to: {filepath}"
        
        # Save to history
        self._save_to_history('create_script', {
            'description': description,
            'platform': platform,
            'script_type': script_type,
            'result': response,
            'script_path': filepath if script_content else None
        })
        
        return response
    
    async def explain_command(self, command: str) -> str:
        """Explain a shell command in detail.
        
        Args:
            command: Command to explain
            
        Returns:
            Detailed explanation of the command
        """
        system_prompt = """You are Shelly, an expert in shell scripting and command-line operations. Your task is to explain the provided command in detail.
Follow these guidelines:
1. Break down each part of the command
2. Explain the purpose of each flag and argument
3. Describe what the command does and its expected output
4. Highlight any potential issues or edge cases
5. Suggest improvements or alternatives if appropriate"""
        
        user_prompt = f"""Explain the following command in detail:
Command: {command}

Your explanation should include:
1. A breakdown of each component of the command
2. The purpose and function of each flag and argument
3. What the command does and its expected output
4. Any potential issues, limitations, or security concerns
5. Suggestions for improvements or alternatives"""
        
        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Save to history
        self._save_to_history('explain_command', {
            'command': command,
            'result': response
        })
        
        return response
    
    async def diagnose_system(self, description: str) -> str:
        """Generate diagnostic commands for system issues.
        
        Args:
            description: Description of the system issue
            
        Returns:
            Diagnostic steps and commands
        """
        platform = self._detect_platform()
        
        system_prompt = f"""You are Shelly, an expert in shell scripting and system diagnostics. Your task is to provide diagnostic steps for a {platform} system based on the issue description.
Follow these guidelines:
1. Suggest specific commands to diagnose the issue
2. Provide a step-by-step troubleshooting approach
3. Explain what each command checks and what to look for in the output
4. Consider common causes for the described symptoms
5. Include both basic and advanced diagnostic techniques"""
        
        user_prompt = f"""Provide diagnostic steps for the following system issue on {platform}:
Issue Description: {description}

Your response should include:
1. A step-by-step diagnostic approach
2. Specific commands to run at each step
3. What to look for in the command output
4. Possible causes and solutions
5. Advanced troubleshooting if initial steps don't resolve the issue"""
        
        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Save to history
        self._save_to_history('diagnose_system', {
            'description': description,
            'platform': platform,
            'result': response
        })
        
        return response
    
    def _detect_platform(self) -> str:
        """Detect the current operating system platform.
        
        Returns:
            Platform name (linux, windows, macos)
        """
        import platform
        system = platform.system().lower()
        
        if system == 'darwin':
            return 'macos'
        elif system == 'windows':
            return 'windows'
        else:
            return 'linux'
    
    def _extract_script_from_response(self, response: str, script_type: str) -> Optional[str]:
        """Extract the script content from the model's response.
        
        Args:
            response: Full response from the model
            script_type: Type of script to extract
            
        Returns:
            Extracted script content or None if not found
        """
        # Look for code blocks with the script
        import re
        
        # Try to find code blocks with ```
        code_block_pattern = r'```(?:\w*\n)?(.*?)```'
        code_blocks = re.findall(code_block_pattern, response, re.DOTALL)
        
        if code_blocks:
            # Return the largest code block (most likely the full script)
            return max(code_blocks, key=len).strip()
        
        return None
    
    def _get_script_extension(self, script_type: str) -> str:
        """Get the appropriate file extension for a script type.
        
        Args:
            script_type: Type of script
            
        Returns:
            File extension including the dot
        """
        extensions = {
            'bash': '.sh',
            'shell': '.sh',
            'powershell': '.ps1',
            'batch': '.bat',
            'cmd': '.bat',
            'python': '.py'
        }
        
        return extensions.get(script_type.lower(), '.txt')
    
    def _validate_command_safety(self, command: str) -> Tuple[bool, str]:
        """Validate if a command is safe to execute.
        
        Args:
            command: Command to validate
            
        Returns:
            Tuple of (is_safe, reason)
        """
        # Split the command to get the base command
        try:
            parts = shlex.split(command)
            base_command = parts[0]
        except Exception:
            return False, "Could not parse command"
        
        # Check against disallowed commands
        for disallowed in self.config['disallowed_commands']:
            if base_command == disallowed or command.startswith(disallowed + ' '):
                return False, f"Command '{disallowed}' is not allowed for security reasons"
        
        # If sandbox is enabled, check against allowed commands
        if self.config['sandbox_enabled']:
            if base_command not in self.config['allowed_commands']:
                return False, f"Command '{base_command}' is not in the allowed list when sandbox is enabled"
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            'rm -rf', 'rmdir /s', 'del /f', 'format', '> /dev/null', '2>&1', 
            '>/dev/null', 'mkfs', 'dd if=', 'wget', 'curl', '| sh', '|sh',
            'eval', 'exec', ';rm', '; rm', '`rm', '$(rm'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"Command contains potentially dangerous pattern: '{pattern}'"
        
        return True, "Command appears safe"
    
    async def _execute_command(self, command: str) -> Tuple[bool, str]:
        """Execute a shell command safely.
        
        Args:
            command: Command to execute
            
        Returns:
            Tuple of (success, output)
        """
        try:
            # Create a subprocess with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the process to complete with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config['max_execution_time']
                )
            except asyncio.TimeoutError:
                # Kill the process if it times out
                process.kill()
                return False, f"Command execution timed out after {self.config['max_execution_time']} seconds"
            
            # Decode the output
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')
            
            # Check the return code
            if process.returncode != 0:
                return False, f"Command failed with exit code {process.returncode}:\n{stderr_str}"
            
            # Return the combined output
            output = stdout_str
            if stderr_str:
                output += f"\nSTDERR:\n{stderr_str}"
            
            return True, output
            
        except Exception as e:
            return False, f"Error executing command: {str(e)}"
    
    def _save_to_history(self, action_type: str, data: Dict[str, Any]) -> None:
        """Save an action to the command history.
        
        Args:
            action_type: Type of action
            data: Data associated with the action
        """
        history_dir = self.config['command_history_dir']
        
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
        history_dir = self.config['command_history_dir']
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
