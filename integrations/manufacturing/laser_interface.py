"""
Laser engraving interface for DMac.
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

logger = logging.getLogger('dmac.integrations.manufacturing.laser')


class LaserInterface:
    """Laser engraving interface for DMac."""
    
    def __init__(self):
        """Initialize the laser engraving interface."""
        self.enabled = config.get('integrations.manufacturing.laser.enabled', False)
        self.controller_path = config.get('integrations.manufacturing.laser.controller_path', '')
        self.logger = logging.getLogger('dmac.integrations.manufacturing.laser')
    
    async def initialize(self) -> bool:
        """Initialize the laser engraving interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("Laser engraving integration is disabled in the configuration")
            return False
        
        self.logger.info("Initializing laser engraving interface")
        
        try:
            # Check if the laser controller is available
            if not self.controller_path:
                self.logger.warning("Laser controller path not configured")
                return False
            
            if not os.path.exists(self.controller_path):
                self.logger.warning(f"Laser controller not found: {self.controller_path}")
                return False
            
            self.logger.info(f"Laser controller found at: {self.controller_path}")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing laser engraving interface: {e}")
            return False
    
    async def generate_laser_path(self, design_file: str, output_file: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a laser cutting/engraving path from a design.
        
        Args:
            design_file: Path to the design file.
            output_file: Path to save the laser path file.
            parameters: Path generation parameters.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Laser engraving integration is disabled")
            return {"error": "Laser engraving integration is disabled"}
        
        self.logger.info(f"Generating laser path for design: {design_file}")
        
        try:
            # Check if the design file exists
            if not os.path.exists(design_file):
                self.logger.error(f"Design file not found: {design_file}")
                return {"error": f"Design file not found: {design_file}"}
            
            # Create a temporary file for the parameters
            params_file = None
            if parameters:
                with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                    params_file = temp_file.name
                    json.dump(parameters, temp_file)
            
            # Prepare the command
            cmd = [self.controller_path, 'generate-path', design_file, output_file]
            
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
                self.logger.error(f"Laser path generation failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Laser path generation completed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_file": output_file,
            }
        except Exception as e:
            self.logger.exception(f"Error generating laser path: {e}")
            return {"error": str(e)}
    
    async def run_job(self, path_file: str) -> Dict[str, Any]:
        """Run a laser engraving job.
        
        Args:
            path_file: Path to the laser path file.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Laser engraving integration is disabled")
            return {"error": "Laser engraving integration is disabled"}
        
        self.logger.info(f"Running laser job with path: {path_file}")
        
        try:
            # Check if the path file exists
            if not os.path.exists(path_file):
                self.logger.error(f"Path file not found: {path_file}")
                return {"error": f"Path file not found: {path_file}"}
            
            # Prepare the command
            cmd = [self.controller_path, 'run-job', path_file]
            
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
                self.logger.error(f"Laser job failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Laser job completed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
            }
        except Exception as e:
            self.logger.exception(f"Error running laser job: {e}")
            return {"error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the laser engraver.
        
        Returns:
            A dictionary containing the status of the laser engraver.
        """
        if not self.enabled:
            self.logger.warning("Laser engraving integration is disabled")
            return {"error": "Laser engraving integration is disabled"}
        
        self.logger.info("Getting laser engraver status")
        
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
                self.logger.error(f"Failed to get laser status with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Laser status: {output}")
            
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
            self.logger.exception(f"Error getting laser status: {e}")
            return {"error": str(e)}
    
    async def stop_job(self) -> Dict[str, Any]:
        """Stop the current laser engraving job.
        
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Laser engraving integration is disabled")
            return {"error": "Laser engraving integration is disabled"}
        
        self.logger.info("Stopping laser job")
        
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
                self.logger.error(f"Failed to stop laser job with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Laser job stopped: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
            }
        except Exception as e:
            self.logger.exception(f"Error stopping laser job: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Clean up resources used by the laser engraving interface."""
        self.logger.info("Cleaning up laser engraving interface")
        
        # No specific cleanup needed for the laser engraving interface
        
        self.logger.info("Laser engraving interface cleaned up")
