"""
Integration manager for DMac.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from config.config import config
from integrations.voice.voice_interface import VoiceInterface
from integrations.cli.cli_interface import CLIInterface
from integrations.design.blender_interface import BlenderInterface
from integrations.design.ue5_interface import UE5Interface
from integrations.manufacturing.printing_interface import PrintingInterface
from integrations.manufacturing.cnc_interface import CNCInterface
from integrations.manufacturing.laser_interface import LaserInterface
from integrations.manufacturing.packaging_interface import PackagingInterface

logger = logging.getLogger('dmac.integrations')


class IntegrationManager:
    """Manager for all integrations in DMac."""
    
    def __init__(self):
        """Initialize the integration manager."""
        self.voice_interface = VoiceInterface()
        self.cli_interface = CLIInterface()
        self.blender_interface = BlenderInterface()
        self.ue5_interface = UE5Interface()
        self.printing_interface = PrintingInterface()
        self.cnc_interface = CNCInterface()
        self.laser_interface = LaserInterface()
        self.packaging_interface = PackagingInterface()
        
        self.logger = logging.getLogger('dmac.integrations')
    
    async def initialize(self) -> bool:
        """Initialize all integrations.
        
        Returns:
            True if all enabled integrations were initialized successfully, False otherwise.
        """
        self.logger.info("Initializing integrations")
        
        # Initialize voice interface
        voice_success = await self.voice_interface.initialize()
        self.logger.info(f"Voice interface initialization {'succeeded' if voice_success else 'failed'}")
        
        # Initialize CLI interface
        cli_success = await self.cli_interface.initialize()
        self.logger.info(f"CLI interface initialization {'succeeded' if cli_success else 'failed'}")
        
        # Initialize design tools
        blender_success = await self.blender_interface.initialize()
        self.logger.info(f"Blender interface initialization {'succeeded' if blender_success else 'failed'}")
        
        ue5_success = await self.ue5_interface.initialize()
        self.logger.info(f"UE5 interface initialization {'succeeded' if ue5_success else 'failed'}")
        
        # Initialize manufacturing controllers
        printing_success = await self.printing_interface.initialize()
        self.logger.info(f"3D printing interface initialization {'succeeded' if printing_success else 'failed'}")
        
        cnc_success = await self.cnc_interface.initialize()
        self.logger.info(f"CNC interface initialization {'succeeded' if cnc_success else 'failed'}")
        
        laser_success = await self.laser_interface.initialize()
        self.logger.info(f"Laser interface initialization {'succeeded' if laser_success else 'failed'}")
        
        packaging_success = await self.packaging_interface.initialize()
        self.logger.info(f"Packaging interface initialization {'succeeded' if packaging_success else 'failed'}")
        
        # Check if all enabled integrations were initialized successfully
        all_success = True
        
        if config.get('integrations.voice.enabled', True) and not voice_success:
            all_success = False
        
        if config.get('integrations.cli.enabled', True) and not cli_success:
            all_success = False
        
        if config.get('integrations.design.enabled', True):
            if not blender_success:
                all_success = False
            
            # UE5 is optional, so we don't fail if it's not available
        
        if config.get('integrations.manufacturing.enabled', True):
            if not printing_success:
                all_success = False
            
            # CNC, laser, and packaging are optional, so we don't fail if they're not available
        
        self.logger.info(f"Integrations initialization {'succeeded' if all_success else 'failed'}")
        return all_success
    
    async def cleanup(self) -> None:
        """Clean up all integrations."""
        self.logger.info("Cleaning up integrations")
        
        # Clean up voice interface
        await self.voice_interface.cleanup()
        
        # Clean up CLI interface
        await self.cli_interface.cleanup()
        
        # Clean up design tools
        await self.blender_interface.cleanup()
        await self.ue5_interface.cleanup()
        
        # Clean up manufacturing controllers
        await self.printing_interface.cleanup()
        await self.cnc_interface.cleanup()
        await self.laser_interface.cleanup()
        await self.packaging_interface.cleanup()
        
        self.logger.info("Integrations cleaned up")
    
    def get_voice_interface(self) -> VoiceInterface:
        """Get the voice interface.
        
        Returns:
            The voice interface.
        """
        return self.voice_interface
    
    def get_cli_interface(self) -> CLIInterface:
        """Get the CLI interface.
        
        Returns:
            The CLI interface.
        """
        return self.cli_interface
    
    def get_blender_interface(self) -> BlenderInterface:
        """Get the Blender interface.
        
        Returns:
            The Blender interface.
        """
        return self.blender_interface
    
    def get_ue5_interface(self) -> UE5Interface:
        """Get the UE5 interface.
        
        Returns:
            The UE5 interface.
        """
        return self.ue5_interface
    
    def get_printing_interface(self) -> PrintingInterface:
        """Get the 3D printing interface.
        
        Returns:
            The 3D printing interface.
        """
        return self.printing_interface
    
    def get_cnc_interface(self) -> CNCInterface:
        """Get the CNC interface.
        
        Returns:
            The CNC interface.
        """
        return self.cnc_interface
    
    def get_laser_interface(self) -> LaserInterface:
        """Get the laser interface.
        
        Returns:
            The laser interface.
        """
        return self.laser_interface
    
    def get_packaging_interface(self) -> PackagingInterface:
        """Get the packaging interface.
        
        Returns:
            The packaging interface.
        """
        return self.packaging_interface
