"""
Secure Process Operations for DMac.

This module provides secure process operations for the DMac system.
"""

import asyncio
import logging
import os
import re
import signal
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from config.config import config
from utils.secure_logging import get_logger

logger = get_logger('dmac.security.secure_process_ops')


class SecureProcessOps:
    """Secure process operations for the DMac system."""
    
    def __init__(self):
        """Initialize the secure process operations."""
        # Load configuration
        self.enabled = config.get('security.process_ops.enabled', True)
        self.max_processes = config.get('security.process_ops.max_processes', 10)
        self.max_runtime = config.get('security.process_ops.max_runtime', 3600)  # 1 hour
        self.allowed_commands = set(config.get('security.process_ops.allowed_commands', [
            'python', 'pip', 'npm', 'node', 'git', 'ollama'
        ]))
        self.blocked_commands = set(config.get('security.process_ops.blocked_commands', [
            'rm', 'del', 'format', 'shutdown', 'reboot', 'halt', 'poweroff'
        ]))
        
        # Initialize process tracking
        self.processes = {}
        self.next_process_id = 1
        
        # Initialize process monitoring task
        self.monitor_task = None
        self.is_monitoring = False
        
        logger.info("Secure process operations initialized")
    
    async def start_monitoring(self) -> None:
        """Start monitoring processes."""
        if not self.enabled:
            logger.debug("Secure process operations are disabled")
            return
        
        if self.is_monitoring:
            logger.warning("Process monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_processes())
        
        logger.info("Started process monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring processes."""
        if not self.enabled:
            logger.debug("Secure process operations are disabled")
            return
        
        if not self.is_monitoring:
            logger.warning("Process monitoring is not running")
            return
        
        self.is_monitoring = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            self.monitor_task = None
        
        logger.info("Stopped process monitoring")
    
    async def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate a command.
        
        Args:
            command: The command to validate.
            
        Returns:
            A tuple of (valid, message).
        """
        if not self.enabled:
            logger.debug("Secure process operations are disabled")
            return True, "Secure process operations are disabled"
        
        # Check if the command is empty
        if not command:
            logger.warning("Empty command")
            return False, "Empty command"
        
        # Split the command into parts
        parts = command.split()
        
        # Get the base command (first part)
        base_command = parts[0]
        
        # Check if the base command is blocked
        for blocked in self.blocked_commands:
            if base_command.lower() == blocked.lower():
                logger.warning(f"Blocked command: {base_command}")
                return False, f"Command {base_command} is not allowed"
        
        # Check if the base command is allowed
        if self.allowed_commands:
            allowed = False
            for allowed_cmd in self.allowed_commands:
                if base_command.lower() == allowed_cmd.lower():
                    allowed = True
                    break
            
            if not allowed:
                logger.warning(f"Command not in allowed list: {base_command}")
                return False, f"Command {base_command} is not allowed"
        
        # Check for shell metacharacters
        shell_metacharacters = [';', '&', '|', '>', '<', '`', '$', '(', ')', '{', '}', '[', ']', '!', '*', '?', '~', '#']
        for char in shell_metacharacters:
            if char in command:
                logger.warning(f"Command contains shell metacharacter: {char}")
                return False, f"Command contains shell metacharacter: {char}"
        
        return True, "Command is valid"
    
    async def run_process(self, command: str, cwd: Optional[str] = None, 
                        timeout: Optional[int] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Run a process securely.
        
        Args:
            command: The command to run.
            cwd: Optional working directory for the command.
            timeout: Optional timeout for the command in seconds.
            
        Returns:
            A tuple of (success, message, process_info).
        """
        if not self.enabled:
            logger.debug("Secure process operations are disabled")
            return True, "Secure process operations are disabled", None
        
        # Validate the command
        valid, message = await self.validate_command(command)
        if not valid:
            return False, message, None
        
        # Check if we've reached the maximum number of processes
        if len(self.processes) >= self.max_processes:
            logger.warning(f"Maximum number of processes reached: {self.max_processes}")
            return False, f"Maximum number of processes reached: {self.max_processes}", None
        
        # Set the timeout
        if timeout is None:
            timeout = self.max_runtime
        else:
            timeout = min(timeout, self.max_runtime)
        
        try:
            # Create the process
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            # Generate a process ID
            process_id = self.next_process_id
            self.next_process_id += 1
            
            # Store the process information
            self.processes[process_id] = {
                'id': process_id,
                'command': command,
                'cwd': cwd,
                'process': process,
                'start_time': time.time(),
                'timeout': timeout,
                'stdout': [],
                'stderr': [],
                'returncode': None,
                'completed': False,
            }
            
            # Start reading the output
            asyncio.create_task(self._read_process_output(process_id))
            
            logger.info(f"Started process {process_id}: {command}")
            
            # Return the process information
            return True, "Process started successfully", {
                'id': process_id,
                'command': command,
                'cwd': cwd,
                'start_time': self.processes[process_id]['start_time'],
                'timeout': timeout,
            }
        except Exception as e:
            logger.exception(f"Error starting process: {e}")
            return False, f"Error starting process: {e}", None
    
    async def get_process_info(self, process_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Get information about a process.
        
        Args:
            process_id: The ID of the process.
            
        Returns:
            A tuple of (success, message, process_info).
        """
        if not self.enabled:
            logger.debug("Secure process operations are disabled")
            return True, "Secure process operations are disabled", None
        
        # Check if the process exists
        if process_id not in self.processes:
            logger.warning(f"Process {process_id} not found")
            return False, f"Process {process_id} not found", None
        
        # Get the process information
        process_info = self.processes[process_id]
        
        # Create a copy of the process information without the process object
        info = process_info.copy()
        del info['process']
        
        # Convert stdout and stderr to strings
        info['stdout'] = b''.join(info['stdout']).decode('utf-8', errors='replace')
        info['stderr'] = b''.join(info['stderr']).decode('utf-8', errors='replace')
        
        logger.debug(f"Got information for process {process_id}")
        return True, "Process information retrieved successfully", info
    
    async def kill_process(self, process_id: int) -> Tuple[bool, str]:
        """Kill a process.
        
        Args:
            process_id: The ID of the process to kill.
            
        Returns:
            A tuple of (success, message).
        """
        if not self.enabled:
            logger.debug("Secure process operations are disabled")
            return True, "Secure process operations are disabled"
        
        # Check if the process exists
        if process_id not in self.processes:
            logger.warning(f"Process {process_id} not found")
            return False, f"Process {process_id} not found"
        
        # Get the process information
        process_info = self.processes[process_id]
        
        # Check if the process is already completed
        if process_info['completed']:
            logger.warning(f"Process {process_id} is already completed")
            return False, f"Process {process_id} is already completed"
        
        try:
            # Kill the process
            process_info['process'].kill()
            
            # Wait for the process to exit
            await process_info['process'].wait()
            
            # Update the process information
            process_info['completed'] = True
            process_info['returncode'] = process_info['process'].returncode
            
            logger.info(f"Killed process {process_id}")
            return True, f"Process {process_id} killed successfully"
        except Exception as e:
            logger.exception(f"Error killing process {process_id}: {e}")
            return False, f"Error killing process {process_id}: {e}"
    
    async def list_processes(self) -> List[Dict[str, Any]]:
        """List all processes.
        
        Returns:
            A list of process information dictionaries.
        """
        if not self.enabled:
            logger.debug("Secure process operations are disabled")
            return []
        
        # Create a list of process information
        process_list = []
        
        for process_id, process_info in self.processes.items():
            # Create a copy of the process information without the process object
            info = process_info.copy()
            del info['process']
            
            # Convert stdout and stderr to strings
            info['stdout'] = b''.join(info['stdout']).decode('utf-8', errors='replace')
            info['stderr'] = b''.join(info['stderr']).decode('utf-8', errors='replace')
            
            process_list.append(info)
        
        logger.debug(f"Listed {len(process_list)} processes")
        return process_list
    
    async def cleanup(self) -> None:
        """Clean up resources used by the secure process operations."""
        if not self.enabled:
            logger.debug("Secure process operations are disabled")
            return
        
        logger.info("Cleaning up secure process operations")
        
        # Stop monitoring
        await self.stop_monitoring()
        
        # Kill all processes
        for process_id in list(self.processes.keys()):
            await self.kill_process(process_id)
        
        logger.info("Secure process operations cleaned up")
    
    async def _read_process_output(self, process_id: int) -> None:
        """Read the output of a process.
        
        Args:
            process_id: The ID of the process.
        """
        # Check if the process exists
        if process_id not in self.processes:
            logger.warning(f"Process {process_id} not found")
            return
        
        # Get the process information
        process_info = self.processes[process_id]
        process = process_info['process']
        
        try:
            # Read the output
            while True:
                # Read from stdout
                stdout_data = await process.stdout.read(1024)
                if stdout_data:
                    process_info['stdout'].append(stdout_data)
                
                # Read from stderr
                stderr_data = await process.stderr.read(1024)
                if stderr_data:
                    process_info['stderr'].append(stderr_data)
                
                # Check if the process has exited
                if process.returncode is not None:
                    # Update the process information
                    process_info['completed'] = True
                    process_info['returncode'] = process.returncode
                    
                    logger.info(f"Process {process_id} completed with return code {process.returncode}")
                    break
                
                # Check if we've reached the timeout
                if time.time() - process_info['start_time'] > process_info['timeout']:
                    # Kill the process
                    process.kill()
                    
                    # Wait for the process to exit
                    await process.wait()
                    
                    # Update the process information
                    process_info['completed'] = True
                    process_info['returncode'] = process.returncode
                    
                    logger.warning(f"Process {process_id} timed out after {process_info['timeout']} seconds")
                    break
                
                # Sleep for a short time
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.exception(f"Error reading output for process {process_id}: {e}")
            
            # Update the process information
            process_info['completed'] = True
            process_info['returncode'] = -1
    
    async def _monitor_processes(self) -> None:
        """Monitor processes for timeouts and cleanup."""
        while self.is_monitoring:
            try:
                # Check each process
                for process_id in list(self.processes.keys()):
                    # Get the process information
                    process_info = self.processes[process_id]
                    
                    # Skip completed processes
                    if process_info['completed']:
                        continue
                    
                    # Check if the process has timed out
                    if time.time() - process_info['start_time'] > process_info['timeout']:
                        # Kill the process
                        await self.kill_process(process_id)
                
                # Sleep for a short time
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.info("Process monitoring cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in process monitoring: {e}")
                await asyncio.sleep(5)  # Wait for 5 seconds before trying again


# Create a singleton instance
secure_process_ops = SecureProcessOps()
