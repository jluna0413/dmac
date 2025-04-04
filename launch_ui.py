"""
Launch the DMac UI.
"""

import asyncio
import logging
import os
import ssl
import sys
import time
from pathlib import Path

# Fix SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Disable SSL verification for httpx
os.environ['SSL_CERT_FILE'] = ''

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from ui.ui_manager import UIManager
from models.model_manager import ModelManager
from core.swarm.orchestrator import Orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('launch_ui')


async def main():
    """Main entry point for the script."""
    logger.info("Starting DMac UI")

    # Initialize the UI manager
    ui_manager = UIManager()
    if not await ui_manager.initialize():
        logger.error("Failed to initialize UI manager")
        return

    try:
        # Start the UI servers
        logger.info("Starting UI servers")
        if not await ui_manager.start_servers():
            logger.error("Failed to start UI servers")
            return

        # Initialize the model manager
        logger.info("Initializing model manager")
        model_manager = ModelManager()
        if not await model_manager.initialize():
            logger.warning("Failed to initialize model manager, continuing without it")

        # Initialize the orchestrator
        logger.info("Initializing orchestrator")
        orchestrator = Orchestrator(model_manager)
        if not await orchestrator.initialize():
            logger.warning("Failed to initialize orchestrator, continuing without it")

        # Add some sample data to the dashboard
        logger.info("Adding sample data to the dashboard")

        # Add sample agents
        ui_manager.update_agent_status('agent1', {
            'name': 'Coding Agent',
            'agent_type': 'coding',
            'state': 'IDLE',
            'last_active': time.time(),
        })

        ui_manager.update_agent_status('agent2', {
            'name': 'Design Agent',
            'agent_type': 'design',
            'state': 'BUSY',
            'last_active': time.time(),
        })

        ui_manager.update_agent_status('agent3', {
            'name': 'Manufacturing Agent',
            'agent_type': 'manufacturing',
            'state': 'IDLE',
            'last_active': time.time(),
        })

        # Add sample tasks
        ui_manager.update_task_status('task1', {
            'prompt': 'Generate a Python function to calculate factorial',
            'status': 'completed',
            'created_at': time.time() - 3600,
            'updated_at': time.time() - 3500,
        })

        ui_manager.update_task_status('task2', {
            'prompt': 'Design a 3D model of a gear',
            'status': 'running',
            'created_at': time.time() - 1800,
            'updated_at': time.time() - 1700,
        })

        ui_manager.update_task_status('task3', {
            'prompt': 'Create a manufacturing plan for a simple bracket',
            'status': 'planning',
            'created_at': time.time() - 900,
            'updated_at': time.time() - 800,
        })

        # Add sample models
        ui_manager.update_model_status('gemini', {
            'type': 'external',
            'usage_count': 42,
            'last_used': time.time() - 1200,
        })

        ui_manager.update_model_status('deepseek', {
            'type': 'local',
            'usage_count': 78,
            'last_used': time.time() - 900,
        })

        ui_manager.update_model_status('local', {
            'type': 'local',
            'usage_count': 123,
            'last_used': time.time() - 600,
        })

        # Open the dashboard
        logger.info("Opening dashboard")
        ui_manager.open_dashboard()

        # Keep the script running
        logger.info("UI is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping DMac UI")
    except Exception as e:
        logger.exception(f"Error running DMac UI: {e}")
    finally:
        # Stop the UI servers
        logger.info("Stopping UI servers")
        await ui_manager.stop_servers()

        # Clean up
        logger.info("Cleaning up")
        await ui_manager.cleanup()

        logger.info("DMac UI stopped")


if __name__ == "__main__":
    asyncio.run(main())
