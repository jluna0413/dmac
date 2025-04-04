"""
Packaging interface for DMac using Cricut.
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

logger = logging.getLogger('dmac.integrations.manufacturing.packaging')


class PackagingInterface:
    """Packaging interface for DMac using Cricut."""
    
    def __init__(self):
        """Initialize the packaging interface."""
        self.enabled = config.get('integrations.manufacturing.packaging.enabled', False)
        self.cricut_path = config.get('integrations.manufacturing.packaging.cricut_path', '')
        self.logger = logging.getLogger('dmac.integrations.manufacturing.packaging')
    
    async def initialize(self) -> bool:
        """Initialize the packaging interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("Packaging integration is disabled in the configuration")
            return False
        
        self.logger.info("Initializing packaging interface")
        
        try:
            # Check if the Cricut software is available
            if not self.cricut_path:
                self.logger.warning("Cricut path not configured")
                return False
            
            if not os.path.exists(self.cricut_path):
                self.logger.warning(f"Cricut software not found: {self.cricut_path}")
                return False
            
            self.logger.info(f"Cricut software found at: {self.cricut_path}")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing packaging interface: {e}")
            return False
    
    async def create_packaging(self, design_file: str, output_file: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create packaging from a design.
        
        Args:
            design_file: Path to the design file.
            output_file: Path to save the packaging file.
            parameters: Packaging creation parameters.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Packaging integration is disabled")
            return {"error": "Packaging integration is disabled"}
        
        self.logger.info(f"Creating packaging from design: {design_file}")
        
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
            cmd = [self.cricut_path, 'create-packaging', design_file, output_file]
            
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
                self.logger.error(f"Packaging creation failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Packaging creation completed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_file": output_file,
            }
        except Exception as e:
            self.logger.exception(f"Error creating packaging: {e}")
            return {"error": str(e)}
    
    async def cut_packaging(self, packaging_file: str) -> Dict[str, Any]:
        """Cut packaging using Cricut.
        
        Args:
            packaging_file: Path to the packaging file.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Packaging integration is disabled")
            return {"error": "Packaging integration is disabled"}
        
        self.logger.info(f"Cutting packaging: {packaging_file}")
        
        try:
            # Check if the packaging file exists
            if not os.path.exists(packaging_file):
                self.logger.error(f"Packaging file not found: {packaging_file}")
                return {"error": f"Packaging file not found: {packaging_file}"}
            
            # Prepare the command
            cmd = [self.cricut_path, 'cut', packaging_file]
            
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
                self.logger.error(f"Packaging cutting failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Packaging cutting completed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
            }
        except Exception as e:
            self.logger.exception(f"Error cutting packaging: {e}")
            return {"error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the Cricut machine.
        
        Returns:
            A dictionary containing the status of the Cricut machine.
        """
        if not self.enabled:
            self.logger.warning("Packaging integration is disabled")
            return {"error": "Packaging integration is disabled"}
        
        self.logger.info("Getting Cricut machine status")
        
        try:
            # Prepare the command
            cmd = [self.cricut_path, 'status']
            
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
                self.logger.error(f"Failed to get Cricut status with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Cricut status: {output}")
            
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
            self.logger.exception(f"Error getting Cricut status: {e}")
            return {"error": str(e)}
    
    async def stop_job(self) -> Dict[str, Any]:
        """Stop the current Cricut job.
        
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Packaging integration is disabled")
            return {"error": "Packaging integration is disabled"}
        
        self.logger.info("Stopping Cricut job")
        
        try:
            # Prepare the command
            cmd = [self.cricut_path, 'stop-job']
            
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
                self.logger.error(f"Failed to stop Cricut job with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Cricut job stopped: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
            }
        except Exception as e:
            self.logger.exception(f"Error stopping Cricut job: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Clean up resources used by the packaging interface."""
        self.logger.info("Cleaning up packaging interface")
        
        # No specific cleanup needed for the packaging interface
        
        self.logger.info("Packaging interface cleaned up")
