"""
Dashboard Server for DMac.

This module provides a web server for the DMac dashboard.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.web import Request, Response, middleware

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors
from security.secure_api import setup_secure_api, setup_auth_routes
from webarena.webarena_api import setup_webarena_routes

logger = get_logger('dmac.dashboard.dashboard_server')


class DashboardServer:
    """Server for the DMac dashboard."""

    def __init__(self):
        """Initialize the dashboard server."""
        # Load configuration
        self.enabled = config.get('dashboard.enabled', True)
        self.host = config.get('dashboard.host', '0.0.0.0')
        self.port = config.get('dashboard.port', 8080)
        self.static_dir = Path(config.get('dashboard.static_dir', 'dashboard/static'))
        self.templates_dir = Path(config.get('dashboard.templates_dir', 'dashboard/templates'))

        # Create directories if they don't exist
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)

        # Initialize the application
        self.app = None
        self.runner = None
        self.site = None

        logger.info("Dashboard server initialized")

    async def start(self) -> bool:
        """Start the dashboard server.

        Returns:
            True if the server was started successfully, False otherwise.
        """
        if not self.enabled:
            logger.info("Dashboard server is disabled")
            return True

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

            # Set up API routes
            setup_secure_api(self.app)
            setup_auth_routes(self.app)
            setup_webarena_routes(self.app)

            # Set up dashboard routes
            self._setup_dashboard_routes()

            # Start the server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()

            logger.info(f"Dashboard server started on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            logger.exception(f"Error starting dashboard server: {e}")
            return False

    async def stop(self) -> None:
        """Stop the dashboard server."""
        if not self.enabled:
            logger.debug("Dashboard server is disabled")
            return

        logger.info("Stopping dashboard server")

        if self.site:
            await self.site.stop()
            self.site = None

        if self.runner:
            await self.runner.cleanup()
            self.runner = None

        self.app = None

        logger.info("Dashboard server stopped")

    def _setup_dashboard_routes(self) -> None:
        """Set up dashboard routes."""
        # Add the routes
        self.app.router.add_get('/', self._handle_index)
        self.app.router.add_get('/login', self._handle_login)
        self.app.router.add_get('/dashboard', self._handle_dashboard)
        self.app.router.add_get('/agents', self._handle_agents)
        self.app.router.add_get('/tasks', self._handle_tasks)
        self.app.router.add_get('/models', self._handle_models)
        self.app.router.add_get('/webarena', self._handle_webarena)
        self.app.router.add_get('/webarena/dashboard', self._handle_webarena_dashboard)
        self.app.router.add_get('/webarena/runs', self._handle_webarena_runs)
        self.app.router.add_get('/webarena/runs/{run_id}', self._handle_webarena_run_details)
        self.app.router.add_get('/webarena/visualizations', self._handle_webarena_visualizations)
        self.app.router.add_get('/settings', self._handle_settings)

        logger.info("Dashboard routes set up")

    @aiohttp_jinja2.template('index.html')
    async def _handle_index(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the index page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - AI Agent Swarm',
            'page': 'index',
        }

    @aiohttp_jinja2.template('login.html')
    async def _handle_login(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the login page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - Login',
            'page': 'login',
        }

    @aiohttp_jinja2.template('dashboard.html')
    async def _handle_dashboard(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the dashboard page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - Dashboard',
            'page': 'dashboard',
        }

    @aiohttp_jinja2.template('agents.html')
    async def _handle_agents(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the agents page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - Agents',
            'page': 'agents',
        }

    @aiohttp_jinja2.template('tasks.html')
    async def _handle_tasks(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the tasks page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - Tasks',
            'page': 'tasks',
        }

    @aiohttp_jinja2.template('models.html')
    async def _handle_models(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the models page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - Models',
            'page': 'models',
        }

    @aiohttp_jinja2.template('webarena.html')
    async def _handle_webarena(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the WebArena page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - WebArena',
            'page': 'webarena',
        }

    @aiohttp_jinja2.template('webarena_dashboard.html')
    async def _handle_webarena_dashboard(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the WebArena dashboard page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - WebArena Dashboard',
            'page': 'webarena_dashboard',
        }

    @aiohttp_jinja2.template('webarena_runs.html')
    async def _handle_webarena_runs(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the WebArena runs page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - WebArena Runs',
            'page': 'webarena_runs',
        }

    @aiohttp_jinja2.template('webarena_run_details.html')
    async def _handle_webarena_run_details(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the WebArena run details page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        run_id = request.match_info.get('run_id')

        return {
            'title': f'DMac - WebArena Run {run_id}',
            'page': 'webarena_run_details',
            'run_id': run_id,
        }

    @aiohttp_jinja2.template('webarena_visualizations.html')
    async def _handle_webarena_visualizations(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the WebArena visualizations page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - WebArena Visualizations',
            'page': 'webarena_visualizations',
        }

    @aiohttp_jinja2.template('settings.html')
    async def _handle_settings(self, request: Request) -> Dict[str, Any]:
        """Handle a request to the settings page.

        Args:
            request: The request to handle.

        Returns:
            A dictionary of template variables.
        """
        return {
            'title': 'DMac - Settings',
            'page': 'settings',
        }


# Create a singleton instance
dashboard_server = DashboardServer()
