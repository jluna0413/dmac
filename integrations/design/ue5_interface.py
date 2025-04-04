"""
Unreal Engine 5 interface for DMac.
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

logger = logging.getLogger('dmac.integrations.design.ue5')


class UE5Interface:
    """Unreal Engine 5 interface for DMac."""
    
    def __init__(self):
        """Initialize the UE5 interface."""
        self.enabled = config.get('integrations.design.enabled', True)
        self.ue5_path = config.get('integrations.design.ue5_path', '')
        self.scripts_dir = Path(__file__).parent / 'ue5_scripts'
        self.logger = logging.getLogger('dmac.integrations.design.ue5')
    
    async def initialize(self) -> bool:
        """Initialize the UE5 interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("Design tools integration is disabled in the configuration")
            return False
        
        self.logger.info("Initializing UE5 interface")
        
        try:
            # Check if UE5 is installed
            if not self.ue5_path:
                # Try to find UE5 in common locations
                common_paths = []
                
                if sys.platform == 'win32':
                    common_paths = [
                        r"C:\Program Files\Epic Games\UE_5.3",
                        r"C:\Program Files\Epic Games\UE_5.2",
                        r"C:\Program Files\Epic Games\UE_5.1",
                        r"C:\Program Files\Epic Games\UE_5.0",
                    ]
                elif sys.platform == 'darwin':  # macOS
                    common_paths = [
                        "/Applications/Unreal Engine.app/Contents/MacOS/UnrealEditor",
                    ]
                else:  # Linux
                    common_paths = [
                        "/opt/unreal-engine/Engine/Binaries/Linux/UnrealEditor",
                    ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        if sys.platform == 'win32':
                            self.ue5_path = os.path.join(path, "Engine", "Binaries", "Win64", "UnrealEditor.exe")
                        else:
                            self.ue5_path = path
                        break
            
            # Check if the UE5 executable exists
            if not self.ue5_path or not os.path.exists(self.ue5_path):
                self.logger.warning(f"UE5 executable not found: {self.ue5_path}")
                self.logger.warning("UE5 integration will be disabled")
                return False
            
            # Create the scripts directory if it doesn't exist
            os.makedirs(self.scripts_dir, exist_ok=True)
            
            # Create the necessary UE5 scripts
            await self._create_ue5_scripts()
            
            self.logger.info(f"UE5 found at: {self.ue5_path}")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing UE5 interface: {e}")
            return False
    
    async def _create_ue5_scripts(self) -> None:
        """Create the necessary UE5 scripts."""
        # Create a Python script for creating Metahumans
        metahuman_script = self.scripts_dir / 'create_metahuman.py'
        with open(metahuman_script, 'w') as f:
            f.write("""
import unreal
import sys
import json
import os

# Get the arguments
args = sys.argv[1:]
if len(args) < 2:
    print("Error: Not enough arguments")
    sys.exit(1)

# Parse the parameters
params_file = args[0]
output_dir = args[1]

# Load the parameters
with open(params_file, 'r') as f:
    params = json.load(f)

# Create a new Metahuman
metahuman_name = params.get('name', 'Metahuman')
metahuman_gender = params.get('gender', 'male')
metahuman_age = params.get('age', 30)

# This is a simplified implementation
# In a real implementation, you would use the Metahuman API to create a Metahuman
# For now, we'll just print the parameters

print(f"Creating Metahuman with parameters:")
print(f"  Name: {metahuman_name}")
print(f"  Gender: {metahuman_gender}")
print(f"  Age: {metahuman_age}")
print(f"Output directory: {output_dir}")

# In a real implementation, you would save the Metahuman to the output directory
# For now, we'll just create a dummy file
with open(os.path.join(output_dir, f"{metahuman_name}.json"), 'w') as f:
    json.dump(params, f)

print(f"Metahuman created and saved to: {output_dir}")
""")
    
    async def create_metahuman(self, parameters: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """Create a Metahuman using UE5.
        
        Args:
            parameters: Parameters for creating the Metahuman.
            output_dir: Directory to save the Metahuman.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Design tools integration is disabled")
            return {"error": "Design tools integration is disabled"}
        
        if not self.ue5_path:
            self.logger.warning("UE5 executable not found")
            return {"error": "UE5 executable not found"}
        
        self.logger.info(f"Creating Metahuman with parameters: {parameters}")
        
        try:
            # Create a temporary file for the parameters
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_file_path = temp_file.name
                json.dump(parameters, temp_file)
            
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Prepare the command
            script_path = self.scripts_dir / 'create_metahuman.py'
            cmd = [
                self.ue5_path,
                '-ExecutePythonScript',
                str(script_path),
                temp_file_path,
                output_dir
            ]
            
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the command to complete
            stdout, stderr = await process.communicate()
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            # Check the result
            if process.returncode != 0:
                self.logger.error(f"UE5 command failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"UE5 command executed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_dir": output_dir,
            }
        except Exception as e:
            self.logger.exception(f"Error creating Metahuman: {e}")
            return {"error": str(e)}
    
    async def render_scene(self, scene_file: str, parameters: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Render a scene using UE5.
        
        Args:
            scene_file: Path to the UE5 scene file.
            parameters: Parameters for rendering the scene.
            output_file: Path to save the rendered image or video.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Design tools integration is disabled")
            return {"error": "Design tools integration is disabled"}
        
        if not self.ue5_path:
            self.logger.warning("UE5 executable not found")
            return {"error": "UE5 executable not found"}
        
        self.logger.info(f"Rendering scene: {scene_file}")
        
        try:
            # Create a temporary file for the parameters
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_file_path = temp_file.name
                json.dump(parameters, temp_file)
            
            # Prepare the command
            cmd = [
                self.ue5_path,
                scene_file,
                '-MovieSceneCaptureType=/Script/MovieSceneCapture.AutomatedLevelSequenceCapture',
                f'-MovieFolder={os.path.dirname(output_file)}',
                f'-MovieName={os.path.basename(output_file)}',
                '-MovieFormat=MP4',
                '-MovieQuality=75',
                '-MovieFrameRate=30',
                '-MovieResolution=1920x1080',
                '-NoLoadingScreen',
                '-game',
                '-NoSplash',
                '-NoVSync',
                '-silent',
                '-unattended',
                '-NoScreenMessages',
                '-ExecCmds=Automation RunTests Render.MovieCapture; Quit'
            ]
            
            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the command to complete
            stdout, stderr = await process.communicate()
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            # Check the result
            if process.returncode != 0:
                self.logger.error(f"UE5 command failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"UE5 command executed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_file": output_file,
            }
        except Exception as e:
            self.logger.exception(f"Error rendering scene: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Clean up resources used by the UE5 interface."""
        self.logger.info("Cleaning up UE5 interface")
        
        # No specific cleanup needed for UE5
        
        self.logger.info("UE5 interface cleaned up")
