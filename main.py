"""
DMac: a Multi-Agent AI Swarm Orchestrated by OpenManus-RL
Main entry point for the application.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from config.config import config
from core.swarm.orchestrator import Orchestrator
from core.openmanus_rl.integration import OpenManusRLIntegration
from models.model_manager import ModelManager
from integrations.integration_manager import IntegrationManager


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get('orchestration.logging_level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dmac.log')
    ]
)

logger = logging.getLogger('dmac')


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='DMac: a Multi-Agent AI Swarm')
    parser.add_argument('--config', type=str, help='Path to the configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--prompt', type=str, help='Initial prompt to process')
    return parser.parse_args()


async def main():
    """Main entry point for the application."""
    args = parse_args()

    # Set debug mode if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('Debug mode enabled')

    # Load custom configuration if provided
    if args.config:
        logger.info(f'Loading configuration from {args.config}')
        # TODO: Implement custom configuration loading

    try:
        # Initialize the model manager
        logger.info('Initializing model manager')
        model_manager = ModelManager()
        if not await model_manager.initialize():
            logger.error('Failed to initialize model manager')
            return

        # Initialize the integration manager
        logger.info('Initializing integration manager')
        integration_manager = IntegrationManager()
        if not await integration_manager.initialize():
            logger.warning('Some integrations failed to initialize')

        # Initialize OpenManus-RL integration
        logger.info('Initializing OpenManus-RL integration')
        openmanus_integration = OpenManusRLIntegration()
        await openmanus_integration.initialize()

        # Initialize the orchestrator with the model manager and integration manager
        logger.info('Initializing orchestrator')
        orchestrator = Orchestrator(openmanus_integration, model_manager, integration_manager)
        await orchestrator.initialize()

        # Process initial prompt if provided
        if args.prompt:
            logger.info(f'Processing initial prompt: {args.prompt}')
            result = await orchestrator.process(args.prompt)
            print(result)
        else:
            # Start interactive mode
            logger.info('Starting interactive mode')
            await interactive_mode(orchestrator)

    except KeyboardInterrupt:
        logger.info('Interrupted by user')
    except Exception as e:
        logger.exception(f'Error: {e}')
    finally:
        # Cleanup
        logger.info('Cleaning up')
        if 'orchestrator' in locals():
            await orchestrator.cleanup()
        if 'openmanus_integration' in locals():
            await openmanus_integration.cleanup()
        if 'integration_manager' in locals():
            await integration_manager.cleanup()
        if 'model_manager' in locals():
            await model_manager.cleanup()


async def interactive_mode(orchestrator):
    """Run the application in interactive mode."""
    print("DMac: a Multi-Agent AI Swarm")
    print("Type 'exit' or 'quit' to exit")

    while True:
        try:
            prompt = input("\nEnter your prompt: ")
            if prompt.lower() in ['exit', 'quit']:
                break

            if not prompt.strip():
                continue

            print("Processing your request...")
            result = await orchestrator.process(prompt)
            print(result)

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception(f'Error processing prompt: {e}')
            print(f'Error: {e}')


if __name__ == '__main__':
    asyncio.run(main())
