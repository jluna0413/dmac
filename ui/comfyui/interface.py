"""
ComfyUI interface for DMac.
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp
from aiohttp import web

from config.config import config

logger = logging.getLogger('dmac.ui.comfyui')


class ComfyUIInterface:
    """ComfyUI interface for DMac."""
    
    def __init__(self):
        """Initialize the ComfyUI interface."""
        self.enabled = config.get('ui.comfyui.enabled', True)
        self.port = config.get('ui.comfyui.port', 8081)
        self.host = config.get('ui.comfyui.host', 'localhost')
        self.comfyui_path = config.get('ui.comfyui.path', '')
        self.process = None
        self.logger = logging.getLogger('dmac.ui.comfyui')
    
    async def initialize(self) -> bool:
        """Initialize the ComfyUI interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("ComfyUI interface is disabled in the configuration")
            return False
        
        self.logger.info("Initializing ComfyUI interface")
        
        try:
            # Check if ComfyUI is installed
            if not self.comfyui_path:
                # Try to find ComfyUI in common locations
                common_paths = []
                
                if sys.platform == 'win32':
                    common_paths = [
                        r"C:\ComfyUI",
                        r"C:\Program Files\ComfyUI",
                        r"C:\Users\Public\ComfyUI",
                    ]
                elif sys.platform == 'darwin':  # macOS
                    common_paths = [
                        "/Applications/ComfyUI",
                        os.path.expanduser("~/ComfyUI"),
                    ]
                else:  # Linux
                    common_paths = [
                        "/opt/ComfyUI",
                        os.path.expanduser("~/ComfyUI"),
                    ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        self.comfyui_path = path
                        break
            
            # If ComfyUI is not found, we'll create a simulated version
            if not self.comfyui_path:
                self.logger.warning("ComfyUI not found, using simulated version")
                self.comfyui_path = "simulated"
            
            self.logger.info(f"ComfyUI found at: {self.comfyui_path}")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing ComfyUI interface: {e}")
            return False
    
    async def start_server(self) -> bool:
        """Start the ComfyUI server.
        
        Returns:
            True if the server was started successfully, False otherwise.
        """
        if not self.enabled:
            self.logger.warning("ComfyUI interface is disabled")
            return False
        
        if self.process:
            self.logger.warning("ComfyUI server is already running")
            return True
        
        self.logger.info(f"Starting ComfyUI server on {self.host}:{self.port}")
        
        try:
            if self.comfyui_path == "simulated":
                # Start a simulated ComfyUI server
                return await self._start_simulated_server()
            else:
                # Start the actual ComfyUI server
                return await self._start_real_server()
        except Exception as e:
            self.logger.exception(f"Error starting ComfyUI server: {e}")
            return False
    
    async def _start_real_server(self) -> bool:
        """Start the real ComfyUI server.
        
        Returns:
            True if the server was started successfully, False otherwise.
        """
        try:
            # Check if the main script exists
            main_script = os.path.join(self.comfyui_path, "main.py")
            if not os.path.exists(main_script):
                self.logger.error(f"ComfyUI main script not found: {main_script}")
                return False
            
            # Prepare the command
            cmd = [sys.executable, main_script, "--port", str(self.port), "--host", self.host]
            
            # Start the process
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.comfyui_path
            )
            
            # Wait for the server to start
            await asyncio.sleep(5)
            
            # Check if the server is running
            if self.process.returncode is not None:
                self.logger.error(f"ComfyUI server failed to start with exit code {self.process.returncode}")
                return False
            
            self.logger.info(f"ComfyUI server started on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.exception(f"Error starting real ComfyUI server: {e}")
            return False
    
    async def _start_simulated_server(self) -> bool:
        """Start a simulated ComfyUI server.
        
        Returns:
            True if the server was started successfully, False otherwise.
        """
        try:
            # Create a simple web server to simulate ComfyUI
            app = web.Application()
            app.router.add_get('/', self._handle_simulated_index)
            app.router.add_get('/api/queue', self._handle_simulated_queue)
            app.router.add_post('/api/prompt', self._handle_simulated_prompt)
            
            # Start the server
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            
            # Store the runner and site for cleanup
            self._simulated_runner = runner
            self._simulated_site = site
            
            self.logger.info(f"Simulated ComfyUI server started on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.exception(f"Error starting simulated ComfyUI server: {e}")
            return False
    
    async def _handle_simulated_index(self, request: web.Request) -> web.Response:
        """Handle the index page request for the simulated ComfyUI server.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulated ComfyUI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        h1 {
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .info {
            margin-top: 20px;
            padding: 10px;
            background-color: #e8f4f8;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Simulated ComfyUI</h1>
        <p>This is a simulated version of ComfyUI for testing purposes.</p>
        
        <div class="info">
            <p>The real ComfyUI was not found on your system. This is a simplified simulation that provides the basic API endpoints for integration testing.</p>
            <p>To use the real ComfyUI, please install it and configure the path in the DMac configuration.</p>
        </div>
    </div>
</body>
</html>
"""
        return web.Response(text=html, content_type='text/html')
    
    async def _handle_simulated_queue(self, request: web.Request) -> web.Response:
        """Handle the queue API request for the simulated ComfyUI server.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        # Return an empty queue
        return web.json_response({
            "queue_running": [],
            "queue_pending": []
        })
    
    async def _handle_simulated_prompt(self, request: web.Request) -> web.Response:
        """Handle the prompt API request for the simulated ComfyUI server.
        
        Args:
            request: The HTTP request.
            
        Returns:
            The HTTP response.
        """
        # Parse the prompt data
        data = await request.json()
        
        # Generate a simulated prompt ID
        prompt_id = f"simulated-{int(time.time())}"
        
        # Return a success response
        return web.json_response({
            "prompt_id": prompt_id,
            "number": 1,
            "node_errors": {}
        })
    
    async def stop_server(self) -> None:
        """Stop the ComfyUI server."""
        self.logger.info("Stopping ComfyUI server")
        
        try:
            if self.comfyui_path == "simulated":
                # Stop the simulated server
                if hasattr(self, '_simulated_site'):
                    await self._simulated_site.stop()
                    self._simulated_site = None
                
                if hasattr(self, '_simulated_runner'):
                    await self._simulated_runner.cleanup()
                    self._simulated_runner = None
            else:
                # Stop the real server
                if self.process:
                    # Try to terminate the process gracefully
                    self.process.terminate()
                    
                    try:
                        # Wait for the process to terminate
                        await asyncio.wait_for(self.process.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        # If the process doesn't terminate, kill it
                        self.logger.warning("ComfyUI server did not terminate gracefully, killing it")
                        self.process.kill()
                        await self.process.wait()
                    
                    self.process = None
            
            self.logger.info("ComfyUI server stopped")
        except Exception as e:
            self.logger.exception(f"Error stopping ComfyUI server: {e}")
    
    async def create_visualization(self, data: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Create a visualization using ComfyUI.
        
        Args:
            data: Data to visualize.
            description: Description of the visualization to create.
            
        Returns:
            A dictionary containing the result of the operation.
        """
        if not self.enabled:
            self.logger.warning("ComfyUI interface is disabled")
            return {"error": "ComfyUI interface is disabled"}
        
        self.logger.info(f"Creating visualization from description: {description}")
        
        try:
            # Check if the server is running
            if not self.process and self.comfyui_path != "simulated":
                self.logger.warning("ComfyUI server is not running")
                return {"error": "ComfyUI server is not running"}
            
            # Create a simple workflow based on the description
            workflow = self._create_workflow(data, description)
            
            # Send the workflow to the ComfyUI API
            async with aiohttp.ClientSession() as session:
                async with session.post(f"http://{self.host}:{self.port}/api/prompt", json=workflow) as response:
                    if response.status != 200:
                        self.logger.error(f"Error sending workflow to ComfyUI: {await response.text()}")
                        return {"error": f"Error sending workflow to ComfyUI: {await response.text()}"}
                    
                    result = await response.json()
                    
                    # In a real implementation, you would wait for the workflow to complete
                    # and retrieve the generated images
                    
                    return {
                        "success": True,
                        "prompt_id": result.get("prompt_id"),
                        "visualization_id": f"viz_{int(time.time())}",
                        "url": f"http://{self.host}:{self.port}/view?prompt={result.get('prompt_id')}",
                    }
        except Exception as e:
            self.logger.exception(f"Error creating visualization: {e}")
            return {"error": str(e)}
    
    def _create_workflow(self, data: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Create a ComfyUI workflow based on data and description.
        
        Args:
            data: Data to visualize.
            description: Description of the visualization to create.
            
        Returns:
            A ComfyUI workflow.
        """
        # This is a simplified implementation
        # In a real implementation, you would create a more sophisticated workflow
        # based on the data and description
        
        # For now, we'll create a simple text-to-image workflow
        return {
            "prompt": {
                "1": {
                    "inputs": {
                        "text": description,
                        "clip": ["5", 0]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "2": {
                    "inputs": {
                        "text": "bad, ugly, blurry",
                        "clip": ["5", 0]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "3": {
                    "inputs": {
                        "seed": 123456789,
                        "steps": 20,
                        "cfg": 7.5,
                        "sampler_name": "euler_ancestral",
                        "scheduler": "normal",
                        "denoise": 1.0,
                        "model": ["4", 0],
                        "positive": ["1", 0],
                        "negative": ["2", 0],
                        "latent_image": ["6", 0]
                    },
                    "class_type": "KSampler"
                },
                "4": {
                    "inputs": {
                        "ckpt_name": "sd_xl_base_1.0.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "5": {
                    "inputs": {
                        "stop_at_clip_layer": -1,
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPSetLastLayer"
                },
                "6": {
                    "inputs": {
                        "width": 1024,
                        "height": 1024,
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage"
                },
                "7": {
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    },
                    "class_type": "VAEDecode"
                },
                "8": {
                    "inputs": {
                        "filename_prefix": "visualization",
                        "images": ["7", 0]
                    },
                    "class_type": "SaveImage"
                }
            }
        }
    
    async def cleanup(self) -> None:
        """Clean up resources used by the ComfyUI interface."""
        self.logger.info("Cleaning up ComfyUI interface")
        
        # Stop the server
        await self.stop_server()
        
        self.logger.info("ComfyUI interface cleaned up")
