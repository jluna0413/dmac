"""
DMac Main Application.

This module provides the main entry point for the DMac application.
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

from config.config import config
from utils.secure_logging import setup_logging, get_logger
from utils.error_handling import install_global_exception_handler
from security.security_manager import security_manager
from models.model_manager import model_manager
from models.ollama_manager import ollama_manager
from webarena.webarena_manager import webarena_manager
from webarena.ollama_integration import webarena_ollama_integration
from dashboard.dashboard_server import dashboard_server
from agents.agent_manager import agent_manager
from tasks.task_manager import task_manager
from learning.learning_manager import learning_manager

logger = get_logger('dmac.app')


class DMacApplication:
    """Main DMac application."""
    
    def __init__(self):
        """Initialize the DMac application."""
        # Set up logging
        setup_logging()
        
        # Install global exception handler
        install_global_exception_handler()
        
        # Initialize components
        self.components = {
            'security_manager': security_manager,
            'model_manager': model_manager,
            'ollama_manager': ollama_manager,
            'webarena_manager': webarena_manager,
            'webarena_ollama_integration': webarena_ollama_integration,
            'dashboard_server': dashboard_server,
            'agent_manager': agent_manager,
            'task_manager': task_manager,
            'learning_manager': learning_manager,
        }
        
        # Initialize shutdown flag
        self.shutdown_event = asyncio.Event()
        
        logger.info("DMac application initialized")
    
    async def start(self):
        """Start the DMac application."""
        logger.info("Starting DMac application")
        
        try:
            # Start security manager
            logger.info("Starting security manager")
            await security_manager.initialize()
            
            # Start model manager
            logger.info("Starting model manager")
            await model_manager.initialize()
            
            # Start Ollama manager
            logger.info("Starting Ollama manager")
            await ollama_manager.initialize()
            
            # Start WebArena manager
            logger.info("Starting WebArena manager")
            await webarena_manager.initialize()
            
            # Start WebArena Ollama integration
            logger.info("Starting WebArena Ollama integration")
            await webarena_ollama_integration.initialize()
            
            # Start agent manager
            logger.info("Starting agent manager")
            await agent_manager.initialize()
            
            # Start task manager
            logger.info("Starting task manager")
            await task_manager.initialize()
            
            # Start learning manager
            logger.info("Starting learning manager")
            await learning_manager.initialize()
            
            # Start dashboard server
            logger.info("Starting dashboard server")
            await dashboard_server.start()
            
            logger.info("DMac application started")
            
            # Set up signal handlers
            self._setup_signal_handlers()
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
        except Exception as e:
            logger.exception(f"Error starting DMac application: {e}")
            await self.shutdown()
    
    async def shutdown(self):
        """Shut down the DMac application."""
        logger.info("Shutting down DMac application")
        
        # Shut down components in reverse order
        for name, component in reversed(list(self.components.items())):
            try:
                logger.info(f"Shutting down {name}")
                if hasattr(component, 'cleanup'):
                    await component.cleanup()
                elif hasattr(component, 'stop'):
                    await component.stop()
            except Exception as e:
                logger.exception(f"Error shutting down {name}: {e}")
        
        logger.info("DMac application shut down")
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self._handle_signal()))
    
    async def _handle_signal(self):
        """Handle termination signals."""
        logger.info("Received termination signal")
        self.shutdown_event.set()


async def main():
    """Main entry point for the DMac application."""
    app = DMacApplication()
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())
