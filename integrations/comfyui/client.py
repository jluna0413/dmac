"""
ComfyUI Client

This module provides a client for interacting with ComfyUI for workflow visualization and execution.
"""

import logging
import json
import os
import asyncio
import aiohttp
import base64
from typing import Dict, List, Any, Optional, Tuple, Union

# Set up logging
logger = logging.getLogger('dmac.integrations.comfyui')

class ComfyUIClient:
    """Client for interacting with ComfyUI."""
    
    def __init__(self, base_url: str = "http://localhost:8188"):
        """
        Initialize the ComfyUI client.
        
        Args:
            base_url: Base URL for the ComfyUI server
        """
        self.base_url = base_url
        self.session = None
        self.connected = False
        self.client_id = None
        
        logger.info(f"ComfyUI client initialized with base URL: {base_url}")
    
    async def connect(self) -> bool:
        """
        Connect to the ComfyUI server.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.session = aiohttp.ClientSession()
            
            # Get a client ID
            async with self.session.get(f"{self.base_url}/prompt") as response:
                if response.status == 200:
                    data = await response.json()
                    self.client_id = data.get('client_id')
                    if self.client_id:
                        self.connected = True
                        logger.info(f"Connected to ComfyUI server with client ID: {self.client_id}")
                        return True
            
            logger.warning("Failed to connect to ComfyUI server")
            return False
        
        except Exception as e:
            logger.error(f"Error connecting to ComfyUI server: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the ComfyUI server."""
        if self.session:
            await self.session.close()
            self.session = None
            self.connected = False
            self.client_id = None
            logger.info("Disconnected from ComfyUI server")
    
    async def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """
        Get available workflow templates.
        
        Returns:
            List of workflow templates
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to ComfyUI server")
            return []
        
        try:
            # Get workflow templates
            async with self.session.get(f"{self.base_url}/workflow_templates") as response:
                if response.status == 200:
                    data = await response.json()
                    templates = data.get('templates', [])
                    logger.info(f"Retrieved {len(templates)} workflow templates")
                    return templates
                else:
                    logger.warning(f"Failed to get workflow templates: {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Error getting workflow templates: {str(e)}")
            return []
    
    async def load_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """
        Load a workflow into ComfyUI.
        
        Args:
            workflow_data: Workflow data to load
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to ComfyUI server")
            return False
        
        try:
            # Load the workflow
            async with self.session.post(
                f"{self.base_url}/prompt",
                json={
                    'client_id': self.client_id,
                    'prompt': workflow_data
                }
            ) as response:
                if response.status == 200:
                    logger.info("Loaded workflow into ComfyUI")
                    return True
                else:
                    logger.warning(f"Failed to load workflow: {response.status}")
                    return False
        
        except Exception as e:
            logger.error(f"Error loading workflow: {str(e)}")
            return False
    
    async def execute_workflow(self, workflow_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Execute a workflow in ComfyUI.
        
        Args:
            workflow_data: Workflow data to execute (optional, uses currently loaded workflow if not provided)
            
        Returns:
            Prompt ID if successful, None otherwise
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to ComfyUI server")
            return None
        
        try:
            # Load the workflow if provided
            if workflow_data:
                success = await self.load_workflow(workflow_data)
                if not success:
                    return None
            
            # Execute the workflow
            async with self.session.post(
                f"{self.base_url}/queue",
                json={
                    'client_id': self.client_id,
                    'prompt': None  # Use the currently loaded workflow
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    prompt_id = data.get('prompt_id')
                    logger.info(f"Executed workflow with prompt ID: {prompt_id}")
                    return prompt_id
                else:
                    logger.warning(f"Failed to execute workflow: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return None
    
    async def get_workflow_status(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution.
        
        Args:
            prompt_id: ID of the prompt to check
            
        Returns:
            Status information
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to ComfyUI server")
            return {'status': 'error', 'error': 'Not connected to ComfyUI server'}
        
        try:
            # Get the status
            async with self.session.get(f"{self.base_url}/history/{prompt_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Retrieved status for prompt ID: {prompt_id}")
                    return data
                else:
                    logger.warning(f"Failed to get status for prompt ID {prompt_id}: {response.status}")
                    return {'status': 'error', 'error': f"Failed to get status: {response.status}"}
        
        except Exception as e:
            logger.error(f"Error getting status for prompt ID {prompt_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def wait_for_workflow_completion(self, prompt_id: str, timeout: float = 60.0) -> Dict[str, Any]:
        """
        Wait for a workflow execution to complete.
        
        Args:
            prompt_id: ID of the prompt to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            Result information
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to ComfyUI server")
            return {'status': 'error', 'error': 'Not connected to ComfyUI server'}
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < timeout:
                # Get the status
                status = await self.get_workflow_status(prompt_id)
                
                # Check if the workflow has completed
                if status.get('status') == 'complete':
                    logger.info(f"Workflow completed for prompt ID: {prompt_id}")
                    return status
                
                # Check if the workflow has failed
                if status.get('status') == 'error':
                    logger.warning(f"Workflow failed for prompt ID: {prompt_id}")
                    return status
                
                # Wait before checking again
                await asyncio.sleep(1.0)
            
            logger.warning(f"Timeout waiting for workflow completion for prompt ID: {prompt_id}")
            return {'status': 'timeout', 'error': 'Timeout waiting for workflow completion'}
        
        except Exception as e:
            logger.error(f"Error waiting for workflow completion for prompt ID {prompt_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_workflow_result(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get the result of a workflow execution.
        
        Args:
            prompt_id: ID of the prompt to get the result for
            
        Returns:
            Result information
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to ComfyUI server")
            return {'status': 'error', 'error': 'Not connected to ComfyUI server'}
        
        try:
            # Get the result
            async with self.session.get(f"{self.base_url}/history/{prompt_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Retrieved result for prompt ID: {prompt_id}")
                    return data
                else:
                    logger.warning(f"Failed to get result for prompt ID {prompt_id}: {response.status}")
                    return {'status': 'error', 'error': f"Failed to get result: {response.status}"}
        
        except Exception as e:
            logger.error(f"Error getting result for prompt ID {prompt_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_image(self, filename: str) -> Optional[bytes]:
        """
        Get an image from ComfyUI.
        
        Args:
            filename: Name of the image file
            
        Returns:
            Image data if successful, None otherwise
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to ComfyUI server")
            return None
        
        try:
            # Get the image
            async with self.session.get(f"{self.base_url}/view/{filename}") as response:
                if response.status == 200:
                    image_data = await response.read()
                    logger.info(f"Retrieved image: {filename}")
                    return image_data
                else:
                    logger.warning(f"Failed to get image {filename}: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error getting image {filename}: {str(e)}")
            return None
    
    async def create_agent_visualization_workflow(self, agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a workflow for visualizing agents.
        
        Args:
            agents: List of agent information
            
        Returns:
            Workflow data
        """
        # This is a simplified example - in a real implementation, this would create a more complex workflow
        workflow = {
            "nodes": [],
            "connections": []
        }
        
        # Add a text node for each agent
        node_id = 1
        for agent in agents:
            agent_node = {
                "id": node_id,
                "type": "TextNode",
                "pos": [node_id * 200, 200],
                "inputs": {
                    "text": agent.get('name', 'Unknown Agent')
                }
            }
            workflow["nodes"].append(agent_node)
            node_id += 1
        
        return workflow
