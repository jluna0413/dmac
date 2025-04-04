"""
UI manager for DMac.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from config.config import config
from ui.swarmui.dashboard import SwarmUIDashboard
from ui.comfyui.interface import ComfyUIInterface
from ui.opencanvas.workflow import OpenCanvasWorkflow

logger = logging.getLogger('dmac.ui')


class UIManager:
    """Manager for all UI components in DMac."""
    
    def __init__(self):
        """Initialize the UI manager."""
        self.swarmui_dashboard = SwarmUIDashboard()
        self.comfyui_interface = ComfyUIInterface()
        self.opencanvas_workflow = OpenCanvasWorkflow()
        
        self.logger = logging.getLogger('dmac.ui')
    
    async def initialize(self) -> bool:
        """Initialize all UI components.
        
        Returns:
            True if all enabled UI components were initialized successfully, False otherwise.
        """
        self.logger.info("Initializing UI components")
        
        # Initialize SwarmUI dashboard
        swarmui_success = await self.swarmui_dashboard.initialize()
        self.logger.info(f"SwarmUI dashboard initialization {'succeeded' if swarmui_success else 'failed'}")
        
        # Initialize ComfyUI interface
        comfyui_success = await self.comfyui_interface.initialize()
        self.logger.info(f"ComfyUI interface initialization {'succeeded' if comfyui_success else 'failed'}")
        
        # Initialize OpenCanvas workflow
        opencanvas_success = await self.opencanvas_workflow.initialize()
        self.logger.info(f"OpenCanvas workflow initialization {'succeeded' if opencanvas_success else 'failed'}")
        
        # Check if all enabled UI components were initialized successfully
        all_success = True
        
        if config.get('ui.swarmui.enabled', True) and not swarmui_success:
            all_success = False
        
        if config.get('ui.comfyui.enabled', True) and not comfyui_success:
            all_success = False
        
        if config.get('ui.opencanvas.enabled', True) and not opencanvas_success:
            all_success = False
        
        self.logger.info(f"UI components initialization {'succeeded' if all_success else 'failed'}")
        return all_success
    
    async def start_servers(self) -> bool:
        """Start all UI servers.
        
        Returns:
            True if all enabled UI servers were started successfully, False otherwise.
        """
        self.logger.info("Starting UI servers")
        
        # Start SwarmUI server
        swarmui_success = await self.swarmui_dashboard.start_server()
        self.logger.info(f"SwarmUI server start {'succeeded' if swarmui_success else 'failed'}")
        
        # Start ComfyUI server
        comfyui_success = await self.comfyui_interface.start_server()
        self.logger.info(f"ComfyUI server start {'succeeded' if comfyui_success else 'failed'}")
        
        # Start OpenCanvas server
        opencanvas_success = await self.opencanvas_workflow.start_server()
        self.logger.info(f"OpenCanvas server start {'succeeded' if opencanvas_success else 'failed'}")
        
        # Check if all enabled UI servers were started successfully
        all_success = True
        
        if config.get('ui.swarmui.enabled', True) and not swarmui_success:
            all_success = False
        
        if config.get('ui.comfyui.enabled', True) and not comfyui_success:
            all_success = False
        
        if config.get('ui.opencanvas.enabled', True) and not opencanvas_success:
            all_success = False
        
        self.logger.info(f"UI servers start {'succeeded' if all_success else 'failed'}")
        return all_success
    
    async def stop_servers(self) -> None:
        """Stop all UI servers."""
        self.logger.info("Stopping UI servers")
        
        # Stop SwarmUI server
        await self.swarmui_dashboard.stop_server()
        
        # Stop ComfyUI server
        await self.comfyui_interface.stop_server()
        
        # Stop OpenCanvas server
        await self.opencanvas_workflow.stop_server()
        
        self.logger.info("UI servers stopped")
    
    async def cleanup(self) -> None:
        """Clean up all UI components."""
        self.logger.info("Cleaning up UI components")
        
        # Stop all servers
        await self.stop_servers()
        
        # Clean up SwarmUI dashboard
        await self.swarmui_dashboard.cleanup()
        
        # Clean up ComfyUI interface
        await self.comfyui_interface.cleanup()
        
        # Clean up OpenCanvas workflow
        await self.opencanvas_workflow.cleanup()
        
        self.logger.info("UI components cleaned up")
    
    def get_swarmui_dashboard(self) -> SwarmUIDashboard:
        """Get the SwarmUI dashboard.
        
        Returns:
            The SwarmUI dashboard.
        """
        return self.swarmui_dashboard
    
    def get_comfyui_interface(self) -> ComfyUIInterface:
        """Get the ComfyUI interface.
        
        Returns:
            The ComfyUI interface.
        """
        return self.comfyui_interface
    
    def get_opencanvas_workflow(self) -> OpenCanvasWorkflow:
        """Get the OpenCanvas workflow.
        
        Returns:
            The OpenCanvas workflow.
        """
        return self.opencanvas_workflow
