"""
DMac Dashboard Test.

This module provides a simplified entry point for testing the DMac dashboard.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('dmac.test_dashboard')

class TestDashboardServer:
    """Test server for the DMac dashboard."""
    
    def __init__(self):
        """Initialize the test dashboard server."""
        # Configuration
        self.host = '0.0.0.0'
        self.port = 8080
        self.static_dir = Path('dashboard/static')
        self.templates_dir = Path('dashboard/templates')
        
        # Create directories if they don't exist
        os.makedirs(self.static_dir, exist_ok=True)
        
        # Initialize the application
        self.app = None
        self.runner = None
        self.site = None
        
        logger.info("Test dashboard server initialized")
    
    async def start(self):
        """Start the test dashboard server."""
        try:
            # Create the application
            self.app = web.Application()
            
            # Set up Jinja2 templates
            aiohttp_jinja2.setup(
                self.app,
                loader=jinja2.FileSystemLoader(str(self.templates_dir))
            )
            
            # Set up static routes
            self.app.router.add_static('/static', str(self.static_dir))
            
            # Set up dashboard routes
            self._setup_dashboard_routes()
            
            # Start the server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"Test dashboard server started on http://{self.host}:{self.port}")
            
            # Wait for Ctrl+C
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.exception(f"Error starting test dashboard server: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the test dashboard server."""
        logger.info("Stopping test dashboard server")
        
        if self.site:
            await self.site.stop()
            self.site = None
        
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
        
        self.app = None
        
        logger.info("Test dashboard server stopped")
    
    def _setup_dashboard_routes(self):
        """Set up dashboard routes."""
        # Add the routes
        self.app.router.add_get('/', self._handle_index)
        self.app.router.add_get('/login', self._handle_login)
        self.app.router.add_get('/dashboard', self._handle_dashboard)
        self.app.router.add_get('/webarena', self._handle_webarena)
        self.app.router.add_get('/webarena/dashboard', self._handle_webarena_dashboard)
        
        logger.info("Dashboard routes set up")
    
    @aiohttp_jinja2.template('index.html')
    async def _handle_index(self, request):
        """Handle a request to the index page."""
        return {
            'title': 'DMac - AI Agent Swarm',
            'page': 'index',
        }
    
    @aiohttp_jinja2.template('login.html')
    async def _handle_login(self, request):
        """Handle a request to the login page."""
        return {
            'title': 'DMac - Login',
            'page': 'login',
        }
    
    @aiohttp_jinja2.template('dashboard.html')
    async def _handle_dashboard(self, request):
        """Handle a request to the dashboard page."""
        return {
            'title': 'DMac - Dashboard',
            'page': 'dashboard',
        }
    
    @aiohttp_jinja2.template('webarena.html')
    async def _handle_webarena(self, request):
        """Handle a request to the WebArena page."""
        return {
            'title': 'DMac - WebArena',
            'page': 'webarena',
        }
    
    @aiohttp_jinja2.template('webarena_dashboard.html')
    async def _handle_webarena_dashboard(self, request):
        """Handle a request to the WebArena dashboard page."""
        return {
            'title': 'DMac - WebArena Dashboard',
            'page': 'webarena_dashboard',
        }

async def main():
    """Main entry point."""
    server = TestDashboardServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
