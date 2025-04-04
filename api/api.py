"""
API Module for DMac.

This module provides the main API for the DMac system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from aiohttp import web
from aiohttp.web import Request, Response

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors
from security.secure_api import setup_secure_api, setup_auth_routes
from api.agent_api import setup_agent_routes
from api.task_api import setup_task_routes
from api.model_api import setup_model_routes
from api.webarena_api import setup_webarena_routes
from api.webarena_agent_api import setup_webarena_agent_routes
from api.system_api import setup_system_routes

logger = get_logger('dmac.api.api')


class APIServer:
    """Server for the DMac API."""
    
    def __init__(self):
        """Initialize the API server."""
        # Load configuration
        self.enabled = config.get('api.enabled', True)
        self.host = config.get('api.host', '0.0.0.0')
        self.port = config.get('api.port', 8000)
        
        # Initialize the application
        self.app = None
        self.runner = None
        self.site = None
        
        logger.info("API server initialized")
    
    async def start(self) -> bool:
        """Start the API server.
        
        Returns:
            True if the server was started successfully, False otherwise.
        """
        if not self.enabled:
            logger.info("API server is disabled")
            return True
        
        try:
            # Create the application
            self.app = web.Application()
            
            # Set up security
            setup_secure_api(self.app)
            
            # Set up routes
            setup_auth_routes(self.app)
            setup_agent_routes(self.app)
            setup_task_routes(self.app)
            setup_model_routes(self.app)
            setup_webarena_routes(self.app)
            setup_webarena_agent_routes(self.app)
            setup_system_routes(self.app)
            
            # Start the server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"API server started on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            logger.exception(f"Error starting API server: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the API server."""
        if not self.enabled:
            logger.debug("API server is disabled")
            return
        
        logger.info("Stopping API server")
        
        if self.site:
            await self.site.stop()
            self.site = None
        
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
        
        self.app = None
        
        logger.info("API server stopped")


# Create a singleton instance
api_server = APIServer()
