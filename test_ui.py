"""
Test script for the DMac UI components.

This script tests the UI components of the DMac system:
- SwarmUI dashboard
- ComfyUI interface
- OpenCanvas workflow
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from ui.ui_manager import UIManager
from ui.swarmui.dashboard import SwarmUIDashboard
from ui.comfyui.interface import ComfyUIInterface
from ui.opencanvas.workflow import OpenCanvasWorkflow
from ui.dashboard.dashboard import Dashboard


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('test_ui')


async def test_swarmui_dashboard():
    """Test the SwarmUI dashboard."""
    logger.info("Testing SwarmUI dashboard")

    # Initialize the SwarmUI dashboard
    dashboard = SwarmUIDashboard()
    if not await dashboard.initialize():
        logger.error("Failed to initialize SwarmUI dashboard")
        return False

    try:
        # Start the server
        logger.info("Starting SwarmUI dashboard server")
        if not await dashboard.start_server():
            logger.error("Failed to start SwarmUI dashboard server")
            return False

        # Update agent status
        logger.info("Updating agent status")
        dashboard.update_agent_status('agent1', {
            'name': 'Coding Agent',
            'state': 'IDLE',
            'type': 'coding',
            'last_active': time.time(),
        })

        dashboard.update_agent_status('agent2', {
            'name': 'Design Agent',
            'state': 'BUSY',
            'type': 'design',
            'last_active': time.time(),
        })

        # Update task status
        logger.info("Updating task status")
        dashboard.update_task_status('task1', {
            'prompt': 'Generate a Python function to calculate factorial',
            'status': 'completed',
            'created_at': time.time() - 3600,
            'updated_at': time.time() - 3500,
            'agent_assignments': ['agent1'],
        })

        dashboard.update_task_status('task2', {
            'prompt': 'Design a 3D model of a gear',
            'status': 'running',
            'created_at': time.time() - 1800,
            'updated_at': time.time() - 1700,
            'agent_assignments': ['agent2'],
        })

        # Wait for a moment to allow the server to run
        logger.info("Waiting for 2 seconds...")
        await asyncio.sleep(2)

        logger.info("SwarmUI dashboard test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing SwarmUI dashboard: {e}")
        return False
    finally:
        # Stop the server
        await dashboard.stop_server()

        # Clean up
        await dashboard.cleanup()


async def test_comfyui_interface():
    """Test the ComfyUI interface."""
    logger.info("Testing ComfyUI interface")

    # Initialize the ComfyUI interface
    comfyui = ComfyUIInterface()
    if not await comfyui.initialize():
        logger.error("Failed to initialize ComfyUI interface")
        return False

    try:
        # Start the server
        logger.info("Starting ComfyUI server")
        if not await comfyui.start_server():
            logger.error("Failed to start ComfyUI server")
            return False

        # Create a visualization
        logger.info("Creating visualization")
        visualization = await comfyui.create_visualization(
            {'type': 'image', 'data': {'width': 512, 'height': 512}},
            'A beautiful sunset over mountains with a lake in the foreground'
        )

        logger.info(f"Visualization created: {visualization}")

        # Wait for a moment to allow the server to run
        logger.info("Waiting for 2 seconds...")
        await asyncio.sleep(2)

        logger.info("ComfyUI interface test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing ComfyUI interface: {e}")
        return False
    finally:
        # Stop the server
        await comfyui.stop_server()

        # Clean up
        await comfyui.cleanup()


async def test_opencanvas_workflow():
    """Test the OpenCanvas workflow."""
    logger.info("Testing OpenCanvas workflow")

    # Initialize the OpenCanvas workflow
    opencanvas = OpenCanvasWorkflow()
    if not await opencanvas.initialize():
        logger.error("Failed to initialize OpenCanvas workflow")
        return False

    try:
        # Start the server
        logger.info("Starting OpenCanvas workflow server")
        if not await opencanvas.start_server():
            logger.error("Failed to start OpenCanvas workflow server")
            return False

        # Create a workflow
        logger.info("Creating workflow")
        workflow = await opencanvas.create_workflow(
            'Test Workflow',
            'A test workflow for DMac'
        )

        logger.info(f"Workflow created: {workflow}")

        # Wait for a moment to allow the server to run
        logger.info("Waiting for 2 seconds...")
        await asyncio.sleep(2)

        logger.info("OpenCanvas workflow test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing OpenCanvas workflow: {e}")
        return False
    finally:
        # Stop the server
        await opencanvas.stop_server()

        # Clean up
        await opencanvas.cleanup()


async def test_main_dashboard():
    """Test the main dashboard."""
    logger.info("Testing main dashboard")

    # Initialize the main dashboard
    dashboard = Dashboard()
    if not await dashboard.initialize():
        logger.error("Failed to initialize main dashboard")
        return False

    try:
        # Start the server
        logger.info("Starting main dashboard server")
        if not await dashboard.start_server():
            logger.error("Failed to start main dashboard server")
            return False

        # Update component status
        logger.info("Updating component status")
        dashboard.update_component_status({
            'swarmui': {
                'enabled': True,
                'initialized': True,
                'running': True,
                'url': 'http://localhost:8080',
                'port': 8080,
                'host': 'localhost',
            },
            'comfyui': {
                'enabled': True,
                'initialized': True,
                'running': True,
                'url': 'http://localhost:8081',
                'port': 8081,
                'host': 'localhost',
            },
            'opencanvas': {
                'enabled': True,
                'initialized': True,
                'running': True,
                'url': 'http://localhost:8082',
                'port': 8082,
                'host': 'localhost',
            },
        })

        # Update agent status
        logger.info("Updating agent status")
        dashboard.update_agent_status('agent1', {
            'name': 'Coding Agent',
            'agent_type': 'coding',
            'state': 'IDLE',
            'last_active': time.time(),
        })

        dashboard.update_agent_status('agent2', {
            'name': 'Design Agent',
            'agent_type': 'design',
            'state': 'BUSY',
            'last_active': time.time(),
        })

        # Update task status
        logger.info("Updating task status")
        dashboard.update_task_status('task1', {
            'prompt': 'Generate a Python function to calculate factorial',
            'status': 'completed',
            'created_at': time.time() - 3600,
            'updated_at': time.time() - 3500,
        })

        dashboard.update_task_status('task2', {
            'prompt': 'Design a 3D model of a gear',
            'status': 'running',
            'created_at': time.time() - 1800,
            'updated_at': time.time() - 1700,
        })

        # Update model status
        logger.info("Updating model status")
        dashboard.update_model_status('gemini', {
            'type': 'external',
            'usage_count': 42,
            'last_used': time.time() - 1200,
        })

        dashboard.update_model_status('local', {
            'type': 'local',
            'usage_count': 123,
            'last_used': time.time() - 600,
        })

        # Wait for a moment to allow the server to run
        logger.info("Waiting for 2 seconds...")
        await asyncio.sleep(2)

        logger.info("Main dashboard test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing main dashboard: {e}")
        return False
    finally:
        # Stop the server
        await dashboard.stop_server()

        # Clean up
        await dashboard.cleanup()


async def test_ui_manager():
    """Test the UI manager."""
    logger.info("Testing UI manager")

    # Initialize the UI manager
    ui_manager = UIManager()
    if not await ui_manager.initialize():
        logger.error("Failed to initialize UI manager")
        return False

    try:
        # Start the servers
        logger.info("Starting UI servers")
        if not await ui_manager.start_servers():
            logger.error("Failed to start UI servers")
            return False

        # Update agent status
        logger.info("Updating agent status")
        ui_manager.update_agent_status('agent1', {
            'name': 'Coding Agent',
            'agent_type': 'coding',
            'state': 'IDLE',
            'last_active': time.time(),
        })

        # Update task status
        logger.info("Updating task status")
        ui_manager.update_task_status('task1', {
            'prompt': 'Generate a Python function to calculate factorial',
            'status': 'completed',
            'created_at': time.time() - 3600,
            'updated_at': time.time() - 3500,
        })

        # Update model status
        logger.info("Updating model status")
        ui_manager.update_model_status('gemini', {
            'type': 'external',
            'usage_count': 42,
            'last_used': time.time() - 1200,
        })

        # Open the dashboard
        logger.info("Opening dashboard")
        ui_manager.open_dashboard()

        # Wait for a moment to allow the servers to run
        logger.info("Waiting for 5 seconds...")
        await asyncio.sleep(5)

        logger.info("UI manager test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing UI manager: {e}")
        return False
    finally:
        # Stop the servers
        await ui_manager.stop_servers()

        # Clean up
        await ui_manager.cleanup()


async def main():
    """Main entry point for the test script."""
    logger.info("Starting UI tests")

    # Test SwarmUI dashboard
    swarmui_success = await test_swarmui_dashboard()
    logger.info(f"SwarmUI dashboard test {'succeeded' if swarmui_success else 'failed'}")

    # Test ComfyUI interface
    comfyui_success = await test_comfyui_interface()
    logger.info(f"ComfyUI interface test {'succeeded' if comfyui_success else 'failed'}")

    # Test OpenCanvas workflow
    opencanvas_success = await test_opencanvas_workflow()
    logger.info(f"OpenCanvas workflow test {'succeeded' if opencanvas_success else 'failed'}")

    # Test main dashboard
    dashboard_success = await test_main_dashboard()
    logger.info(f"Main dashboard test {'succeeded' if dashboard_success else 'failed'}")

    # Test UI manager
    ui_manager_success = await test_ui_manager()
    logger.info(f"UI manager test {'succeeded' if ui_manager_success else 'failed'}")

    # Overall result
    overall_success = (
        swarmui_success and
        comfyui_success and
        opencanvas_success and
        dashboard_success and
        ui_manager_success
    )

    logger.info(f"UI tests {'succeeded' if overall_success else 'failed'}")


if __name__ == '__main__':
    asyncio.run(main())
