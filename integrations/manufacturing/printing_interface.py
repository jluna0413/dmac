"""
3D printing interface for DMac using Klipper, OctoPrint, and Slic3r.
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

import httpx

from config.config import config

logger = logging.getLogger('dmac.integrations.manufacturing.printing')


class PrintingInterface:
    """3D printing interface for DMac using Klipper, OctoPrint, and Slic3r."""
    
    def __init__(self):
        """Initialize the 3D printing interface."""
        self.enabled = config.get('integrations.manufacturing.enabled', True)
        self.klipper_enabled = config.get('integrations.manufacturing.3d_printing.klipper_enabled', True)
        self.octoprint_url = config.get('integrations.manufacturing.3d_printing.octoprint_url', 'http://localhost:5000')
        self.octoprint_api_key = config.get('integrations.manufacturing.3d_printing.octoprint_api_key', '')
        self.slicer_path = config.get('integrations.manufacturing.3d_printing.slicer_path', '')
        self.logger = logging.getLogger('dmac.integrations.manufacturing.printing')
    
    async def initialize(self) -> bool:
        """Initialize the 3D printing interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("Manufacturing integration is disabled in the configuration")
            return False
        
        self.logger.info("Initializing 3D printing interface")
        
        try:
            # Check if Slic3r is installed
            if not self.slicer_path:
                # Try to find Slic3r in common locations
                common_paths = []
                
                if sys.platform == 'win32':
                    common_paths = [
                        r"C:\Program Files\Slic3r\slic3r.exe",
                        r"C:\Program Files\Slic3r\slic3r-console.exe",
                        r"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe",
                        r"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe",
                    ]
                elif sys.platform == 'darwin':  # macOS
                    common_paths = [
                        "/Applications/Slic3r.app/Contents/MacOS/slic3r",
                        "/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer",
                    ]
                else:  # Linux
                    common_paths = [
                        "/usr/bin/slic3r",
                        "/usr/local/bin/slic3r",
                        "/usr/bin/prusa-slicer",
                        "/usr/local/bin/prusa-slicer",
                    ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        self.slicer_path = path
                        break
                
                if not self.slicer_path:
                    # Try to find Slic3r in PATH
                    try:
                        if sys.platform == 'win32':
                            result = subprocess.run(['where', 'slic3r'], capture_output=True, text=True, check=True)
                        else:
                            result = subprocess.run(['which', 'slic3r'], capture_output=True, text=True, check=True)
                        
                        self.slicer_path = result.stdout.strip()
                    except subprocess.CalledProcessError:
                        try:
                            if sys.platform == 'win32':
                                result = subprocess.run(['where', 'prusa-slicer'], capture_output=True, text=True, check=True)
                            else:
                                result = subprocess.run(['which', 'prusa-slicer'], capture_output=True, text=True, check=True)
                            
                            self.slicer_path = result.stdout.strip()
                        except subprocess.CalledProcessError:
                            self.logger.warning("Slic3r not found in PATH")
            
            # Check if the slicer executable exists
            if not self.slicer_path or not os.path.exists(self.slicer_path):
                self.logger.warning(f"Slicer executable not found: {self.slicer_path}")
                self.logger.warning("Slicing functionality will be disabled")
            else:
                self.logger.info(f"Slicer found at: {self.slicer_path}")
            
            # Check if OctoPrint is available
            if self.octoprint_url:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{self.octoprint_url}/api/version", timeout=5.0)
                        if response.status_code == 200:
                            self.logger.info(f"OctoPrint found at: {self.octoprint_url}")
                        else:
                            self.logger.warning(f"OctoPrint returned status code {response.status_code}")
                            self.logger.warning("OctoPrint functionality will be limited")
                except Exception as e:
                    self.logger.warning(f"Error connecting to OctoPrint: {e}")
                    self.logger.warning("OctoPrint functionality will be limited")
            else:
                self.logger.warning("OctoPrint URL not configured")
                self.logger.warning("OctoPrint functionality will be disabled")
            
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing 3D printing interface: {e}")
            return False
    
    async def slice_model(self, model_file: str, output_file: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Slice a 3D model for printing.
        
        Args:
            model_file: Path to the 3D model file.
            output_file: Path to save the G-code file.
            parameters: Slicing parameters.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Manufacturing integration is disabled")
            return {"error": "Manufacturing integration is disabled"}
        
        if not self.slicer_path:
            self.logger.warning("Slicer not found")
            return {"error": "Slicer not found"}
        
        self.logger.info(f"Slicing model: {model_file}")
        
        try:
            # Check if the model file exists
            if not os.path.exists(model_file):
                self.logger.error(f"Model file not found: {model_file}")
                return {"error": f"Model file not found: {model_file}"}
            
            # Create a temporary file for the parameters
            config_file = None
            if parameters:
                with tempfile.NamedTemporaryFile(suffix='.ini', delete=False) as temp_file:
                    config_file = temp_file.name
                    
                    # Write the parameters to the config file
                    for key, value in parameters.items():
                        temp_file.write(f"{key} = {value}\n".encode())
            
            # Prepare the command
            cmd = [self.slicer_path, model_file, '--output', output_file]
            
            # Add the config file if available
            if config_file:
                cmd.extend(['--load', config_file])
            
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the command to complete
            stdout, stderr = await process.communicate()
            
            # Clean up the temporary file
            if config_file:
                os.unlink(config_file)
            
            # Check the result
            if process.returncode != 0:
                self.logger.error(f"Slicing failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Slicing completed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_file": output_file,
            }
        except Exception as e:
            self.logger.exception(f"Error slicing model: {e}")
            return {"error": str(e)}
    
    async def print_model(self, gcode_file: str) -> Dict[str, Any]:
        """Print a sliced 3D model.
        
        Args:
            gcode_file: Path to the G-code file.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Manufacturing integration is disabled")
            return {"error": "Manufacturing integration is disabled"}
        
        if not self.octoprint_url:
            self.logger.warning("OctoPrint URL not configured")
            return {"error": "OctoPrint URL not configured"}
        
        self.logger.info(f"Printing model: {gcode_file}")
        
        try:
            # Check if the G-code file exists
            if not os.path.exists(gcode_file):
                self.logger.error(f"G-code file not found: {gcode_file}")
                return {"error": f"G-code file not found: {gcode_file}"}
            
            # Upload the G-code file to OctoPrint
            async with httpx.AsyncClient() as client:
                # Set up the headers
                headers = {}
                if self.octoprint_api_key:
                    headers['X-Api-Key'] = self.octoprint_api_key
                
                # Upload the file
                with open(gcode_file, 'rb') as f:
                    files = {'file': (os.path.basename(gcode_file), f, 'application/octet-stream')}
                    response = await client.post(
                        f"{self.octoprint_url}/api/files/local",
                        headers=headers,
                        files=files,
                        data={'print': 'true'},  # Start printing immediately
                        timeout=60.0
                    )
                
                # Check the response
                if response.status_code != 201:
                    self.logger.error(f"Failed to upload G-code file: {response.text}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response": response.text,
                    }
                
                # Parse the response
                response_data = response.json()
                self.logger.info(f"G-code file uploaded successfully: {response_data}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response_data,
                    "job_id": response_data.get('files', {}).get('local', {}).get('name'),
                }
        except Exception as e:
            self.logger.exception(f"Error printing model: {e}")
            return {"error": str(e)}
    
    async def get_printer_status(self) -> Dict[str, Any]:
        """Get the status of the 3D printer.
        
        Returns:
            A dictionary containing the printer status.
        """
        if not self.enabled:
            self.logger.warning("Manufacturing integration is disabled")
            return {"error": "Manufacturing integration is disabled"}
        
        if not self.octoprint_url:
            self.logger.warning("OctoPrint URL not configured")
            return {"error": "OctoPrint URL not configured"}
        
        self.logger.info("Getting printer status")
        
        try:
            # Get the printer status from OctoPrint
            async with httpx.AsyncClient() as client:
                # Set up the headers
                headers = {}
                if self.octoprint_api_key:
                    headers['X-Api-Key'] = self.octoprint_api_key
                
                # Get the printer status
                response = await client.get(
                    f"{self.octoprint_url}/api/printer",
                    headers=headers,
                    timeout=10.0
                )
                
                # Check the response
                if response.status_code != 200:
                    self.logger.error(f"Failed to get printer status: {response.text}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response": response.text,
                    }
                
                # Parse the response
                response_data = response.json()
                self.logger.info(f"Printer status: {response_data}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response_data,
                    "state": response_data.get('state', {}).get('text'),
                    "temperature": response_data.get('temperature', {}),
                }
        except Exception as e:
            self.logger.exception(f"Error getting printer status: {e}")
            return {"error": str(e)}
    
    async def get_job_status(self) -> Dict[str, Any]:
        """Get the status of the current print job.
        
        Returns:
            A dictionary containing the job status.
        """
        if not self.enabled:
            self.logger.warning("Manufacturing integration is disabled")
            return {"error": "Manufacturing integration is disabled"}
        
        if not self.octoprint_url:
            self.logger.warning("OctoPrint URL not configured")
            return {"error": "OctoPrint URL not configured"}
        
        self.logger.info("Getting job status")
        
        try:
            # Get the job status from OctoPrint
            async with httpx.AsyncClient() as client:
                # Set up the headers
                headers = {}
                if self.octoprint_api_key:
                    headers['X-Api-Key'] = self.octoprint_api_key
                
                # Get the job status
                response = await client.get(
                    f"{self.octoprint_url}/api/job",
                    headers=headers,
                    timeout=10.0
                )
                
                # Check the response
                if response.status_code != 200:
                    self.logger.error(f"Failed to get job status: {response.text}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response": response.text,
                    }
                
                # Parse the response
                response_data = response.json()
                self.logger.info(f"Job status: {response_data}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response_data,
                    "state": response_data.get('state'),
                    "progress": response_data.get('progress', {}),
                    "job": response_data.get('job', {}),
                }
        except Exception as e:
            self.logger.exception(f"Error getting job status: {e}")
            return {"error": str(e)}
    
    async def cancel_job(self) -> Dict[str, Any]:
        """Cancel the current print job.
        
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Manufacturing integration is disabled")
            return {"error": "Manufacturing integration is disabled"}
        
        if not self.octoprint_url:
            self.logger.warning("OctoPrint URL not configured")
            return {"error": "OctoPrint URL not configured"}
        
        self.logger.info("Cancelling job")
        
        try:
            # Cancel the job in OctoPrint
            async with httpx.AsyncClient() as client:
                # Set up the headers
                headers = {}
                if self.octoprint_api_key:
                    headers['X-Api-Key'] = self.octoprint_api_key
                
                # Cancel the job
                response = await client.post(
                    f"{self.octoprint_url}/api/job",
                    headers=headers,
                    json={"command": "cancel"},
                    timeout=10.0
                )
                
                # Check the response
                if response.status_code != 204:
                    self.logger.error(f"Failed to cancel job: {response.text}")
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "response": response.text,
                    }
                
                self.logger.info("Job cancelled successfully")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                }
        except Exception as e:
            self.logger.exception(f"Error cancelling job: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Clean up resources used by the 3D printing interface."""
        self.logger.info("Cleaning up 3D printing interface")
        
        # No specific cleanup needed for the 3D printing interface
        
        self.logger.info("3D printing interface cleaned up")
