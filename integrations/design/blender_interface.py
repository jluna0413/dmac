"""
Blender interface for DMac.
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

logger = logging.getLogger('dmac.integrations.design.blender')


class BlenderInterface:
    """Blender interface for DMac."""
    
    def __init__(self):
        """Initialize the Blender interface."""
        self.enabled = config.get('integrations.design.enabled', True)
        self.blender_path = config.get('integrations.design.blender_path', '')
        self.scripts_dir = Path(__file__).parent / 'blender_scripts'
        self.logger = logging.getLogger('dmac.integrations.design.blender')
    
    async def initialize(self) -> bool:
        """Initialize the Blender interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("Design tools integration is disabled in the configuration")
            return False
        
        self.logger.info("Initializing Blender interface")
        
        try:
            # Check if Blender is installed
            if not self.blender_path:
                # Try to find Blender in common locations
                common_paths = []
                
                if sys.platform == 'win32':
                    common_paths = [
                        r"C:\Program Files\Blender Foundation\Blender 3.6",
                        r"C:\Program Files\Blender Foundation\Blender 3.5",
                        r"C:\Program Files\Blender Foundation\Blender 3.4",
                        r"C:\Program Files\Blender Foundation\Blender 3.3",
                        r"C:\Program Files\Blender Foundation\Blender 3.2",
                        r"C:\Program Files\Blender Foundation\Blender 3.1",
                        r"C:\Program Files\Blender Foundation\Blender 3.0",
                        r"C:\Program Files\Blender Foundation\Blender 2.93",
                    ]
                elif sys.platform == 'darwin':  # macOS
                    common_paths = [
                        "/Applications/Blender.app/Contents/MacOS/Blender",
                    ]
                else:  # Linux
                    common_paths = [
                        "/usr/bin/blender",
                        "/usr/local/bin/blender",
                    ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        if sys.platform == 'win32':
                            self.blender_path = os.path.join(path, "blender.exe")
                        else:
                            self.blender_path = path
                        break
                
                if not self.blender_path:
                    # Try to find Blender in PATH
                    try:
                        if sys.platform == 'win32':
                            result = subprocess.run(['where', 'blender'], capture_output=True, text=True, check=True)
                        else:
                            result = subprocess.run(['which', 'blender'], capture_output=True, text=True, check=True)
                        
                        self.blender_path = result.stdout.strip()
                    except subprocess.CalledProcessError:
                        self.logger.error("Blender not found in PATH")
                        return False
            
            # Check if the Blender executable exists
            if not os.path.exists(self.blender_path):
                self.logger.error(f"Blender executable not found: {self.blender_path}")
                return False
            
            # Create the scripts directory if it doesn't exist
            os.makedirs(self.scripts_dir, exist_ok=True)
            
            # Create the necessary Blender scripts
            await self._create_blender_scripts()
            
            self.logger.info(f"Blender found at: {self.blender_path}")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing Blender interface: {e}")
            return False
    
    async def _create_blender_scripts(self) -> None:
        """Create the necessary Blender scripts."""
        # Create a script for creating 3D models
        create_model_script = self.scripts_dir / 'create_model.py'
        with open(create_model_script, 'w') as f:
            f.write("""
import bpy
import sys
import json
import os

# Get the arguments
args = sys.argv[sys.argv.index('--') + 1:]
if len(args) < 2:
    print("Error: Not enough arguments")
    sys.exit(1)

# Parse the parameters
params_file = args[0]
output_file = args[1]

# Load the parameters
with open(params_file, 'r') as f:
    params = json.load(f)

# Clear the scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create a simple object based on the parameters
object_type = params.get('object_type', 'cube')
if object_type == 'cube':
    bpy.ops.mesh.primitive_cube_add(size=params.get('size', 2.0))
elif object_type == 'sphere':
    bpy.ops.mesh.primitive_uv_sphere_add(radius=params.get('radius', 1.0))
elif object_type == 'cylinder':
    bpy.ops.mesh.primitive_cylinder_add(radius=params.get('radius', 1.0), depth=params.get('depth', 2.0))
elif object_type == 'cone':
    bpy.ops.mesh.primitive_cone_add(radius1=params.get('radius', 1.0), depth=params.get('depth', 2.0))
elif object_type == 'torus':
    bpy.ops.mesh.primitive_torus_add(
        major_radius=params.get('major_radius', 1.0),
        minor_radius=params.get('minor_radius', 0.25)
    )
else:
    print(f"Error: Unknown object type: {object_type}")
    sys.exit(1)

# Set the object name
obj = bpy.context.active_object
obj.name = params.get('name', 'Object')

# Apply material if specified
if 'material' in params:
    mat = bpy.data.materials.new(name=params['material'].get('name', 'Material'))
    mat.use_nodes = True
    
    # Set the material color
    if 'color' in params['material']:
        color = params['material']['color']
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = [
            color[0], color[1], color[2], 1.0
        ]
    
    # Assign the material to the object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Save the model
bpy.ops.export_mesh.stl(filepath=output_file)

print(f"Model created and saved to: {output_file}")
""")
        
        # Create a script for rendering 3D models
        render_script = self.scripts_dir / 'render_model.py'
        with open(render_script, 'w') as f:
            f.write("""
import bpy
import sys
import json
import os

# Get the arguments
args = sys.argv[sys.argv.index('--') + 1:]
if len(args) < 3:
    print("Error: Not enough arguments")
    sys.exit(1)

# Parse the parameters
model_file = args[0]
params_file = args[1]
output_file = args[2]

# Load the parameters
with open(params_file, 'r') as f:
    params = json.load(f)

# Clear the scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import the model
if model_file.endswith('.stl'):
    bpy.ops.import_mesh.stl(filepath=model_file)
elif model_file.endswith('.obj'):
    bpy.ops.import_scene.obj(filepath=model_file)
elif model_file.endswith('.fbx'):
    bpy.ops.import_scene.fbx(filepath=model_file)
elif model_file.endswith('.glb') or model_file.endswith('.gltf'):
    bpy.ops.import_scene.gltf(filepath=model_file)
else:
    print(f"Error: Unsupported file format: {model_file}")
    sys.exit(1)

# Set up the camera
camera = bpy.data.objects['Camera']
camera.location = params.get('camera_location', [0, -10, 0])
camera.rotation_euler = params.get('camera_rotation', [1.5708, 0, 0])  # 90 degrees in radians

# Set up the lighting
light = bpy.data.objects['Light']
light.location = params.get('light_location', [4, -4, 5])
light.data.energy = params.get('light_energy', 1000)

# Set up the render settings
bpy.context.scene.render.resolution_x = params.get('resolution_x', 1920)
bpy.context.scene.render.resolution_y = params.get('resolution_y', 1080)
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = params.get('samples', 128)

# Render the image
bpy.context.scene.render.filepath = output_file
bpy.ops.render.render(write_still=True)

print(f"Model rendered and saved to: {output_file}")
""")
        
        # Create a script for creating animations
        animation_script = self.scripts_dir / 'create_animation.py'
        with open(animation_script, 'w') as f:
            f.write("""
import bpy
import sys
import json
import os
import math

# Get the arguments
args = sys.argv[sys.argv.index('--') + 1:]
if len(args) < 3:
    print("Error: Not enough arguments")
    sys.exit(1)

# Parse the parameters
model_file = args[0]
params_file = args[1]
output_file = args[2]

# Load the parameters
with open(params_file, 'r') as f:
    params = json.load(f)

# Clear the scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import the model
if model_file.endswith('.stl'):
    bpy.ops.import_mesh.stl(filepath=model_file)
elif model_file.endswith('.obj'):
    bpy.ops.import_scene.obj(filepath=model_file)
elif model_file.endswith('.fbx'):
    bpy.ops.import_scene.fbx(filepath=model_file)
elif model_file.endswith('.glb') or model_file.endswith('.gltf'):
    bpy.ops.import_scene.gltf(filepath=model_file)
else:
    print(f"Error: Unsupported file format: {model_file}")
    sys.exit(1)

# Get the object
obj = bpy.context.selected_objects[0]

# Set up the animation
animation_type = params.get('animation_type', 'rotate')
frames = params.get('frames', 60)
bpy.context.scene.frame_end = frames

if animation_type == 'rotate':
    # Create a rotation animation
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    
    obj.rotation_euler = (0, 0, 2 * math.pi)
    obj.keyframe_insert(data_path="rotation_euler", frame=frames)
elif animation_type == 'move':
    # Create a movement animation
    start_pos = params.get('start_position', [0, 0, 0])
    end_pos = params.get('end_position', [5, 0, 0])
    
    obj.location = start_pos
    obj.keyframe_insert(data_path="location", frame=1)
    
    obj.location = end_pos
    obj.keyframe_insert(data_path="location", frame=frames)
elif animation_type == 'scale':
    # Create a scaling animation
    start_scale = params.get('start_scale', [1, 1, 1])
    end_scale = params.get('end_scale', [2, 2, 2])
    
    obj.scale = start_scale
    obj.keyframe_insert(data_path="scale", frame=1)
    
    obj.scale = end_scale
    obj.keyframe_insert(data_path="scale", frame=frames)
else:
    print(f"Error: Unknown animation type: {animation_type}")
    sys.exit(1)

# Set up the camera
camera = bpy.data.objects['Camera']
camera.location = params.get('camera_location', [0, -10, 0])
camera.rotation_euler = params.get('camera_rotation', [1.5708, 0, 0])  # 90 degrees in radians

# Set up the lighting
light = bpy.data.objects['Light']
light.location = params.get('light_location', [4, -4, 5])
light.data.energy = params.get('light_energy', 1000)

# Set up the render settings
bpy.context.scene.render.resolution_x = params.get('resolution_x', 1920)
bpy.context.scene.render.resolution_y = params.get('resolution_y', 1080)
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = params.get('samples', 64)

# Set up the output format
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'

# Render the animation
bpy.context.scene.render.filepath = output_file
bpy.ops.render.render(animation=True)

print(f"Animation created and saved to: {output_file}")
""")
    
    async def create_3d_model(self, parameters: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Create a 3D model using Blender.
        
        Args:
            parameters: Parameters for creating the 3D model.
            output_file: Path to save the 3D model.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Design tools integration is disabled")
            return {"error": "Design tools integration is disabled"}
        
        self.logger.info(f"Creating 3D model with parameters: {parameters}")
        
        try:
            # Create a temporary file for the parameters
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_file_path = temp_file.name
                json.dump(parameters, temp_file)
            
            # Prepare the command
            script_path = self.scripts_dir / 'create_model.py'
            cmd = [
                self.blender_path,
                '--background',
                '--python', str(script_path),
                '--',
                temp_file_path,
                output_file
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
                self.logger.error(f"Blender command failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Blender command executed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_file": output_file,
            }
        except Exception as e:
            self.logger.exception(f"Error creating 3D model: {e}")
            return {"error": str(e)}
    
    async def render_3d_model(self, model_file: str, parameters: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Render a 3D model using Blender.
        
        Args:
            model_file: Path to the 3D model file.
            parameters: Parameters for rendering the 3D model.
            output_file: Path to save the rendered image.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Design tools integration is disabled")
            return {"error": "Design tools integration is disabled"}
        
        self.logger.info(f"Rendering 3D model: {model_file}")
        
        try:
            # Create a temporary file for the parameters
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_file_path = temp_file.name
                json.dump(parameters, temp_file)
            
            # Prepare the command
            script_path = self.scripts_dir / 'render_model.py'
            cmd = [
                self.blender_path,
                '--background',
                '--python', str(script_path),
                '--',
                model_file,
                temp_file_path,
                output_file
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
                self.logger.error(f"Blender command failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Blender command executed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_file": output_file,
            }
        except Exception as e:
            self.logger.exception(f"Error rendering 3D model: {e}")
            return {"error": str(e)}
    
    async def create_animation(self, model_file: str, parameters: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Create an animation using Blender.
        
        Args:
            model_file: Path to the 3D model file.
            parameters: Parameters for creating the animation.
            output_file: Path to save the animation.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("Design tools integration is disabled")
            return {"error": "Design tools integration is disabled"}
        
        self.logger.info(f"Creating animation for model: {model_file}")
        
        try:
            # Create a temporary file for the parameters
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_file_path = temp_file.name
                json.dump(parameters, temp_file)
            
            # Prepare the command
            script_path = self.scripts_dir / 'create_animation.py'
            cmd = [
                self.blender_path,
                '--background',
                '--python', str(script_path),
                '--',
                model_file,
                temp_file_path,
                output_file
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
                self.logger.error(f"Blender command failed with exit code {process.returncode}: {stderr.decode()}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
            
            # Parse the output
            output = stdout.decode()
            self.logger.info(f"Blender command executed successfully: {output}")
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": output,
                "stderr": stderr.decode(),
                "output_file": output_file,
            }
        except Exception as e:
            self.logger.exception(f"Error creating animation: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Clean up resources used by the Blender interface."""
        self.logger.info("Cleaning up Blender interface")
        
        # No specific cleanup needed for Blender
        
        self.logger.info("Blender interface cleaned up")
