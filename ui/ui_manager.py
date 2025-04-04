"""
UI manager for DMac.
"""

import logging
from typing import Any, Dict

from config.config import config
from ui.swarmui.dashboard import SwarmUIDashboard
from ui.comfyui.interface import ComfyUIInterface
from ui.opencanvas.workflow import OpenCanvasWorkflow
from ui.dashboard.dashboard import Dashboard

logger = logging.getLogger('dmac.ui')


class UIManager:
    """Manager for all UI components in DMac."""

    def __init__(self):
        """Initialize the UI manager."""
        self.swarmui_dashboard = SwarmUIDashboard()
        self.comfyui_interface = ComfyUIInterface()
        self.opencanvas_workflow = OpenCanvasWorkflow()
        self.main_dashboard = Dashboard()

        # Status tracking
        self.component_status = {
            'swarmui': {
                'enabled': config.get('ui.swarmui.enabled', True),
                'initialized': False,
                'running': False,
                'url': None,
                'port': config.get('ui.swarmui.port', 8080),
                'host': config.get('ui.swarmui.host', 'localhost'),
            },
            'comfyui': {
                'enabled': config.get('ui.comfyui.enabled', True),
                'initialized': False,
                'running': False,
                'url': None,
                'port': config.get('ui.comfyui.port', 8081),
                'host': config.get('ui.comfyui.host', 'localhost'),
            },
            'opencanvas': {
                'enabled': config.get('ui.opencanvas.enabled', True),
                'initialized': False,
                'running': False,
                'url': None,
                'port': config.get('ui.opencanvas.port', 8082),
                'host': config.get('ui.opencanvas.host', 'localhost'),
            },
        }

        # Main dashboard port
        self.dashboard_port = config.get('ui.dashboard.port', 8079)
        self.dashboard_host = config.get('ui.dashboard.host', 'localhost')
        self.dashboard_url = f"http://{self.dashboard_host}:{self.dashboard_port}"
        self.dashboard_running = False

        self.logger = logging.getLogger('dmac.ui')

    async def initialize(self) -> bool:
        """Initialize all UI components.

        Returns:
            True if all enabled UI components were initialized successfully, False otherwise.
        """
        self.logger.info("Initializing UI components")

        # Initialize SwarmUI dashboard
        swarmui_success = await self.swarmui_dashboard.initialize()
        self.component_status['swarmui']['initialized'] = swarmui_success
        self.logger.info(f"SwarmUI dashboard initialization {'succeeded' if swarmui_success else 'failed'}")

        # Initialize ComfyUI interface
        comfyui_success = await self.comfyui_interface.initialize()
        self.component_status['comfyui']['initialized'] = comfyui_success
        self.logger.info(f"ComfyUI interface initialization {'succeeded' if comfyui_success else 'failed'}")

        # Initialize OpenCanvas workflow
        opencanvas_success = await self.opencanvas_workflow.initialize()
        self.component_status['opencanvas']['initialized'] = opencanvas_success
        self.logger.info(f"OpenCanvas workflow initialization {'succeeded' if opencanvas_success else 'failed'}")

        # Initialize the main dashboard
        await self._initialize_dashboard()

        # Check if all enabled UI components were initialized successfully
        all_success = True

        if self.component_status['swarmui']['enabled'] and not swarmui_success:
            all_success = False

        if self.component_status['comfyui']['enabled'] and not comfyui_success:
            all_success = False

        if self.component_status['opencanvas']['enabled'] and not opencanvas_success:
            all_success = False

        self.logger.info(f"UI components initialization {'succeeded' if all_success else 'failed'}")
        return all_success

    async def _initialize_dashboard(self) -> bool:
        """Initialize the main dashboard.

        Returns:
            True if the dashboard was initialized successfully, False otherwise.
        """
        self.logger.info("Initializing main dashboard")

        # Initialize the main dashboard
        dashboard_success = await self.main_dashboard.initialize()

        if dashboard_success:
            self.logger.info("Main dashboard initialized")
        else:
            self.logger.error("Failed to initialize main dashboard")

        return dashboard_success

    async def start_servers(self) -> bool:
        """Start all UI servers.

        Returns:
            True if all enabled UI servers were started successfully, False otherwise.
        """
        self.logger.info("Starting UI servers")

        # Start SwarmUI server
        swarmui_success = await self.swarmui_dashboard.start_server()
        self.component_status['swarmui']['running'] = swarmui_success
        if swarmui_success:
            host = self.component_status['swarmui']['host']
            port = self.component_status['swarmui']['port']
            self.component_status['swarmui']['url'] = f"http://{host}:{port}"
        self.logger.info(f"SwarmUI server start {'succeeded' if swarmui_success else 'failed'}")

        # Start ComfyUI server
        comfyui_success = await self.comfyui_interface.start_server()
        self.component_status['comfyui']['running'] = comfyui_success
        if comfyui_success:
            host = self.component_status['comfyui']['host']
            port = self.component_status['comfyui']['port']
            self.component_status['comfyui']['url'] = f"http://{host}:{port}"
        self.logger.info(f"ComfyUI server start {'succeeded' if comfyui_success else 'failed'}")

        # Start OpenCanvas server
        opencanvas_success = await self.opencanvas_workflow.start_server()
        self.component_status['opencanvas']['running'] = opencanvas_success
        if opencanvas_success:
            host = self.component_status['opencanvas']['host']
            port = self.component_status['opencanvas']['port']
            self.component_status['opencanvas']['url'] = f"http://{host}:{port}"
        self.logger.info(f"OpenCanvas server start {'succeeded' if opencanvas_success else 'failed'}")

        # Start the main dashboard
        await self._start_dashboard()

        # Check if all enabled UI servers were started successfully
        all_success = True

        if self.component_status['swarmui']['enabled'] and not swarmui_success:
            all_success = False

        if self.component_status['comfyui']['enabled'] and not comfyui_success:
            all_success = False

        if self.component_status['opencanvas']['enabled'] and not opencanvas_success:
            all_success = False

        self.logger.info(f"UI servers start {'succeeded' if all_success else 'failed'}")
        return all_success

    async def _start_dashboard(self) -> bool:
        """Start the main dashboard server.

        Returns:
            True if the dashboard server was started successfully, False otherwise.
        """
        self.logger.info("Starting main dashboard server")

        # Start the main dashboard server
        dashboard_success = await self.main_dashboard.start_server()

        if dashboard_success:
            self.dashboard_running = True
            self.dashboard_url = f"http://{self.dashboard_host}:{self.dashboard_port}"
            self.logger.info(f"Main dashboard server started at {self.dashboard_url}")

            # Update the component status in the dashboard
            self.main_dashboard.update_component_status(self.component_status)
        else:
            self.logger.error("Failed to start main dashboard server")

        return dashboard_success

    async def stop_servers(self) -> None:
        """Stop all UI servers."""
        self.logger.info("Stopping UI servers")

        # Stop the main dashboard
        await self._stop_dashboard()

        # Stop SwarmUI server
        await self.swarmui_dashboard.stop_server()
        self.component_status['swarmui']['running'] = False
        self.component_status['swarmui']['url'] = None

        # Stop ComfyUI server
        await self.comfyui_interface.stop_server()
        self.component_status['comfyui']['running'] = False
        self.component_status['comfyui']['url'] = None

        # Stop OpenCanvas server
        await self.opencanvas_workflow.stop_server()
        self.component_status['opencanvas']['running'] = False
        self.component_status['opencanvas']['url'] = None

        self.logger.info("UI servers stopped")

    async def _stop_dashboard(self) -> None:
        """Stop the main dashboard server."""
        self.logger.info("Stopping main dashboard server")

        # Stop the main dashboard server
        await self.main_dashboard.stop_server()

        self.dashboard_running = False
        self.logger.info("Main dashboard server stopped")

    async def cleanup(self) -> None:
        """Clean up all UI components."""
        self.logger.info("Cleaning up UI components")

        # Stop all servers
        await self.stop_servers()

        # Clean up SwarmUI dashboard
        await self.swarmui_dashboard.cleanup()
        self.component_status['swarmui']['initialized'] = False

        # Clean up ComfyUI interface
        await self.comfyui_interface.cleanup()
        self.component_status['comfyui']['initialized'] = False

        # Clean up OpenCanvas workflow
        await self.opencanvas_workflow.cleanup()
        self.component_status['opencanvas']['initialized'] = False

        # Clean up main dashboard
        await self.main_dashboard.cleanup()

        self.logger.info("UI components cleaned up")

    def get_component_status(self, component_name: str = None) -> Dict[str, Any]:
        """Get the status of a UI component or all components.

        Args:
            component_name: The name of the component to get the status of.
                If None, returns the status of all components.

        Returns:
            The status of the component(s).
        """
        if component_name is not None:
            if component_name in self.component_status:
                return self.component_status[component_name]
            else:
                return None
        else:
            return self.component_status

    def get_dashboard_status(self) -> Dict[str, Any]:
        """Get the status of the main dashboard.

        Returns:
            The status of the main dashboard.
        """
        return {
            'running': self.dashboard_running,
            'url': self.dashboard_url,
            'port': self.dashboard_port,
            'host': self.dashboard_host,
        }

    def open_dashboard(self) -> bool:
        """Open the main dashboard in a web browser.

        Returns:
            True if the dashboard was opened successfully, False otherwise.
        """
        if not self.dashboard_running:
            self.logger.warning("Cannot open dashboard: not running")
            return False

        try:
            # Open the dashboard in a web browser
            import webbrowser
            webbrowser.open(self.dashboard_url)
            self.logger.info(f"Opening dashboard at {self.dashboard_url}")
            return True
        except Exception as e:
            self.logger.exception(f"Error opening dashboard: {e}")
            return False

    def open_component(self, component_name: str) -> bool:
        """Open a UI component in a web browser.

        Args:
            component_name: The name of the component to open.

        Returns:
            True if the component was opened successfully, False otherwise.
        """
        if component_name not in self.component_status:
            self.logger.warning(f"Cannot open component: {component_name} not found")
            return False

        if not self.component_status[component_name]['running']:
            self.logger.warning(f"Cannot open component: {component_name} not running")
            return False

        url = self.component_status[component_name]['url']
        if not url:
            self.logger.warning(f"Cannot open component: {component_name} has no URL")
            return False

        try:
            # Open the component in a web browser
            import webbrowser
            webbrowser.open(url)
            self.logger.info(f"Opening {component_name} at {url}")
            return True
        except Exception as e:
            self.logger.exception(f"Error opening {component_name}: {e}")
            return False

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

    def get_main_dashboard(self) -> Dashboard:
        """Get the main dashboard.

        Returns:
            The main dashboard.
        """
        return self.main_dashboard

    def update_agent_status(self, agent_id: str, status: Dict[str, Any]) -> None:
        """Update the status of an agent.

        Args:
            agent_id: The ID of the agent.
            status: The status of the agent.
        """
        if self.dashboard_running:
            self.main_dashboard.update_agent_status(agent_id, status)

    def update_task_status(self, task_id: str, status: Dict[str, Any]) -> None:
        """Update the status of a task.

        Args:
            task_id: The ID of the task.
            status: The status of the task.
        """
        if self.dashboard_running:
            self.main_dashboard.update_task_status(task_id, status)

    def update_model_status(self, model_name: str, status: Dict[str, Any]) -> None:
        """Update the status of a model.

        Args:
            model_name: The name of the model.
            status: The status of the model.
        """
        if self.dashboard_running:
            self.main_dashboard.update_model_status(model_name, status)
