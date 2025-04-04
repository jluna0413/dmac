"""
DMac Test Application.

This module provides a simplified entry point for testing the DMac application.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from config.config import config
from utils.secure_logging import setup_logging, get_logger

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('dmac.test_app')

async def main():
    """Main entry point for the test application."""
    logger.info("Starting DMac test application")
    
    # Print configuration
    logger.info("Configuration:")
    logger.info(f"Ollama API URL: {config.get('models.ollama.api_url')}")
    logger.info(f"Ollama Models: {config.get('models.ollama.models')}")
    logger.info(f"WebArena Enabled: {config.get('webarena.enabled')}")
    logger.info(f"WebArena Directory: {config.get('webarena.dir')}")
    
    # Create directories if they don't exist
    os.makedirs(config.get('webarena.dir'), exist_ok=True)
    os.makedirs(config.get('webarena.data_dir'), exist_ok=True)
    os.makedirs(os.path.join(config.get('webarena.data_dir'), 'results'), exist_ok=True)
    os.makedirs(os.path.join(config.get('webarena.data_dir'), 'logs'), exist_ok=True)
    os.makedirs(os.path.join(config.get('webarena.data_dir'), 'visualizations'), exist_ok=True)
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get(config.get('models.ollama.api_url'))
        logger.info(f"Ollama API response: {response.status_code}")
        
        # List available models
        models_response = requests.get(f"{config.get('models.ollama.api_url')}/api/tags")
        if models_response.status_code == 200:
            models = models_response.json().get('models', [])
            logger.info(f"Available Ollama models: {[model.get('name') for model in models]}")
        else:
            logger.warning(f"Failed to list Ollama models: {models_response.status_code}")
    except Exception as e:
        logger.exception(f"Error connecting to Ollama: {e}")
    
    logger.info("DMac test application completed")

if __name__ == "__main__":
    asyncio.run(main())
