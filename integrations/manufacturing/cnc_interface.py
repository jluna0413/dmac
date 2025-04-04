"""
CNC interface for DMac.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from config.config import config

logger = logging.getLogger('dmac.integrations.manufacturing.cnc')


class CNCInterface:
    """CNC interface for DMac."""
    
    def __init__(self):
        """Initialize the CNC interface."""
        self.enabled = config.get('integrations.manufacturing.cnc.enabled', False)
        self.controller_path = config.get('integrations.manufacturing.cnc.controller_path', '')
        self.logger = logging.getLogger('dmac.integrations.manufacturing.cnc')
    
    async def initialize(self) -> bool:
        """Initialize the CNC interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("CNC integration is disabled in the configuration")
            return False
        
        self.logger.info("Initializing CNC interface")
        
        try:
            # Check if the CNC controller is available
            if not self.controller_path:
                self.logger.warning("CNC controller path not configured")
                return False
            
            if not os.path.exists(self.controller_path):
                self.logger.warning(f"CNC controller not found: {self.controller_path}")
                return False
            
            self.logger.info(f"CNC controller found at: {self.controller_path}")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing CNC interface: {e}")
            return False
    
    async def generate_toolpath(self, model_file: str, output_file: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a CNC toolpath from a 3D model.
        
        Args:
            model_file: Path to the 3D model file.
            output_file: Path to save the toolpath file.
            parameters: Toolpath generation parameters.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("CNC integration is disabled")
            return {"error": "CNC integration is disabled"}
        
        self.logger.info(f"Generating CNC toolpath for model: {model_file}")
        
        try:
            # Check if the model file exists
            if not os.path.exists(model_file):
                self.logger.error(f"Model file not found: {model_file}")
                return {"error": f"Model file not found: {model_file}"}
            
            # Create a temporary file for the parameters
            params_file = None
            if parameters:
                with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                    params_file = temp_file.name
                    json.dump(parameters, temp_file)
            
            # Prepare the command
            cmd = [self.controller_path, 'generate-toolpath', model_file, output_file]
            
            # Add the parameters file if available
            if params_file:
                cmd.extend(['--params', params_file])
            
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the command to complete
            stdout, stderr = await process.communicate()
            
            # Clean up the temporary file
            if params_file:
                os.unlink(params_file)
            
            # Check the result
            if process.returncode != 0:
                self.logger.error(f"Toolpath generation failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Toolpath generation completed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_file": output_file,
            }
        except Exception as e:
            self.logger.exception(f"Error generating CNC toolpath: {e}")
            return {"error": str(e)}
    
    async def run_job(self, toolpath_file: str) -> Dict[str, Any]:
        """Run a CNC job.
        
        Args:
            toolpath_file: Path to the toolpath file.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("CNC integration is disabled")
            return {"error": "CNC integration is disabled"}
        
        self.logger.info(f"Running CNC job with toolpath: {toolpath_file}")
        
        try:
            # Check if the toolpath file exists
            if not os.path.exists(toolpath_file):
                self.logger.error(f"Toolpath file not found: {toolpath_file}")
                return {"error": f"Toolpath file not found: {toolpath_file}"}
            
            # Prepare the command
            cmd = [self.controller_path, 'run-job', toolpath_file]
            
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
                self.logger.error(f"CNC job failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"CNC job completed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
            }
        except Exception as e:
            self.logger.exception(f"Error running CNC job: {e}")
            return {"error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the CNC machine.
        
        Returns:
            A dictionary containing the status of the CNC machine.
        """
        if not self.enabled:
            self.logger.warning("CNC integration is disabled")
            return {"error": "CNC integration is disabled"}
        
        self.logger.info("Getting CNC machine status")
        
        try:
            # Prepare the command
            cmd = [self.controller_path, 'status']
            
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
                self.logger.error(f"Failed to get CNC status with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"CNC status: {output}")
            
            # Try to parse the output as JSON
            try:
                status = json.loads(output)
            except json.JSONDecodeError:
                status = {"raw_output": output}
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "status": status,
            }
        except Exception as e:
            self.logger.exception(f"Error getting CNC status: {e}")
            return {"error": str(e)}
    
    async def stop_job(self) -> Dict[str, Any]:
        """Stop the current CNC job.
        
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("CNC integration is disabled")
            return {"error": "CNC integration is disabled"}
        
        self.logger.info("Stopping CNC job")
        
        try:
            # Prepare the command
            cmd = [self.controller_path, 'stop-job']
            
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
                self.logger.error(f"Failed to stop CNC job with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"CNC job stopped: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
            }
        except Exception as e:
            self.logger.exception(f"Error stopping CNC job: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Clean up resources used by the CNC interface."""
        self.logger.info("Cleaning up CNC interface")
        
        # No specific cleanup needed for the CNC interface
        
        self.logger.info("CNC interface cleaned up")
