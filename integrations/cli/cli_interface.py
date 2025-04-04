"""
CLI interface for DMac using Cline.
"""

import asyncio
import logging
import os
import shlex
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from config.config import config

logger = logging.getLogger('dmac.integrations.cli')


class CLIInterface:
    """CLI interface for DMac using Cline."""
    
    def __init__(self):
        """Initialize the CLI interface."""
        self.enabled = config.get('integrations.cli.enabled', True)
        self.engine = config.get('integrations.cli.engine', 'Cline')
        self.cline_path = config.get('integrations.cli.cline_path', '')
        self.process = None
        self.logger = logging.getLogger('dmac.integrations.cli')
    
    async def initialize(self) -> bool:
        """Initialize the CLI interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("CLI interface is disabled in the configuration")
            return False
        
        self.logger.info(f"Initializing CLI interface with engine: {self.engine}")
        
        try:
            if self.engine == 'Cline':
                return await self._initialize_cline()
            else:
                self.logger.error(f"Unknown CLI engine: {self.engine}")
                return False
        except Exception as e:
            self.logger.exception(f"Error initializing CLI interface: {e}")
            return False
    
    async def _initialize_cline(self) -> bool:
        """Initialize the Cline engine.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            # Check if Cline is installed
            if not self.cline_path:
                # Try to find Cline in the PATH
                try:
                    if sys.platform == 'win32':
                        result = subprocess.run(['where', 'cline'], capture_output=True, text=True, check=True)
                    else:
                        result = subprocess.run(['which', 'cline'], capture_output=True, text=True, check=True)
                    
                    self.cline_path = result.stdout.strip()
                except subprocess.CalledProcessError:
                    self.logger.error("Cline not found in PATH")
                    return False
            
            # Check if the Cline executable exists
            if not os.path.exists(self.cline_path):
                self.logger.error(f"Cline executable not found: {self.cline_path}")
                return False
            
            self.logger.info(f"Cline found at: {self.cline_path}")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing Cline: {e}")
            return False
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command using the CLI interface.
        
        Args:
            command: The command to execute.
            
        Returns:
            A dictionary containing the result of the command execution.
        """
        if not self.enabled:
            self.logger.warning("CLI interface is disabled")
            return {"error": "CLI interface is disabled"}
        
        self.logger.info(f"Executing command: {command}")
        
        try:
            if self.engine == 'Cline':
                return await self._execute_cline_command(command)
            else:
                self.logger.error(f"Unknown CLI engine: {self.engine}")
                return {"error": f"Unknown CLI engine: {self.engine}"}
        except Exception as e:
            self.logger.exception(f"Error executing command: {e}")
            return {"error": str(e)}
    
    async def _execute_cline_command(self, command: str) -> Dict[str, Any]:
        """Execute a command using Cline.
        
        Args:
            command: The command to execute.
            
        Returns:
            A dictionary containing the result of the command execution.
        """
        try:
            # Prepare the command
            cmd = [self.cline_path, 'execute', command]
            
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the command to complete
            stdout, stderr = await process.communicate()
            
            # Check the result
            if process.returncode != 0:
                self.logger.error(f"Command failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Command executed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
            }
        except Exception as e:
            self.logger.exception(f"Error executing Cline command: {e}")
            return {"error": str(e)}
    
    async def start_interactive_session(self) -> bool:
        """Start an interactive CLI session.
        
        Returns:
            True if the session was started successfully, False otherwise.
        """
        if not self.enabled:
            self.logger.warning("CLI interface is disabled")
            return False
        
        if self.process:
            self.logger.warning("Interactive session already running")
            return True
        
        self.logger.info("Starting interactive CLI session")
        
        try:
            if self.engine == 'Cline':
                return await self._start_cline_interactive_session()
            else:
                self.logger.error(f"Unknown CLI engine: {self.engine}")
                return False
        except Exception as e:
            self.logger.exception(f"Error starting interactive session: {e}")
            return False
    
    async def _start_cline_interactive_session(self) -> bool:
        """Start an interactive Cline session.
        
        Returns:
            True if the session was started successfully, False otherwise.
        """
        try:
            # Prepare the command
            cmd = [self.cline_path, 'interactive']
            
            # Start the process
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.logger.info("Interactive Cline session started")
            return True
        except Exception as e:
            self.logger.exception(f"Error starting interactive Cline session: {e}")
            return False
    
    async def send_to_interactive_session(self, command: str) -> Dict[str, Any]:
        """Send a command to the interactive CLI session.
        
        Args:
            command: The command to send.
            
        Returns:
            A dictionary containing the result of the command execution.
        """
        if not self.enabled:
            self.logger.warning("CLI interface is disabled")
            return {"error": "CLI interface is disabled"}
        
        if not self.process:
            self.logger.error("No interactive session running")
            return {"error": "No interactive session running"}
        
        self.logger.info(f"Sending command to interactive session: {command}")
        
        try:
            # Send the command to the process
            self.process.stdin.write(f"{command}\n".encode())
            await self.process.stdin.drain()
            
            # Read the output
            # This is a simplified implementation
            # In a real implementation, you would need to handle the output more carefully
            # and possibly implement a timeout
            output = await self.process.stdout.readline()
            
            return {
                "success": True,
                "output": output.decode(),
            }
        except Exception as e:
            self.logger.exception(f"Error sending command to interactive session: {e}")
            return {"error": str(e)}
    
    async def stop_interactive_session(self) -> None:
        """Stop the interactive CLI session."""
        if not self.process:
            return
        
        self.logger.info("Stopping interactive CLI session")
        
        try:
            # Send exit command
            self.process.stdin.write(b"exit\n")
            await self.process.stdin.drain()
            
            # Wait for the process to terminate
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.logger.warning("Interactive session did not terminate gracefully, killing it")
                self.process.kill()
                await self.process.wait()
            
            self.process = None
            self.logger.info("Interactive CLI session stopped")
        except Exception as e:
            self.logger.exception(f"Error stopping interactive session: {e}")
            # Force kill the process
            try:
                self.process.kill()
                await self.process.wait()
            except:
                pass
            
            self.process = None
    
    async def cleanup(self) -> None:
        """Clean up resources used by the CLI interface."""
        self.logger.info("Cleaning up CLI interface")
        
        # Stop interactive session
        await self.stop_interactive_session()
        
        self.logger.info("CLI interface cleaned up")
