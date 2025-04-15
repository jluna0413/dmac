"""
Pull Ollama Models.

This script pulls the necessary Ollama models for the DMac application.
"""

import asyncio
import logging
import os
import sys
import requests
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('dmac.pull_models')

# Ollama API URL
OLLAMA_API_URL = "http://localhost:11434"

# Models to pull
MODELS_TO_PULL = [
    "llama2",
    "mistral",
    "gemma:2b"
]

def check_ollama_running() -> bool:
    """Check if Ollama is running.
    
    Returns:
        True if Ollama is running, False otherwise.
    """
    try:
        response = requests.get(OLLAMA_API_URL)
        return response.status_code == 200
    except Exception:
        return False

def list_available_models() -> List[str]:
    """List available Ollama models.
    
    Returns:
        A list of available model names.
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model.get('name') for model in models]
        else:
            logger.warning(f"Failed to list models: {response.status_code}")
            return []
    except Exception as e:
        logger.exception(f"Error listing models: {e}")
        return []

def pull_model(model_name: str) -> bool:
    """Pull an Ollama model.
    
    Args:
        model_name: The name of the model to pull.
        
    Returns:
        True if the model was pulled successfully, False otherwise.
    """
    try:
        logger.info(f"Pulling model: {model_name}")
        response = requests.post(
            f"{OLLAMA_API_URL}/api/pull",
            json={"name": model_name}
        )
        
        if response.status_code == 200:
            logger.info(f"Model {model_name} pulled successfully")
            return True
        else:
            logger.warning(f"Failed to pull model {model_name}: {response.status_code}")
            return False
    except Exception as e:
        logger.exception(f"Error pulling model {model_name}: {e}")
        return False

def main():
    """Main entry point."""
    logger.info("Starting Ollama model puller")
    
    # Check if Ollama is running
    if not check_ollama_running():
        logger.error("Ollama is not running. Please start Ollama and try again.")
        sys.exit(1)
    
    # List available models
    available_models = list_available_models()
    logger.info(f"Available models: {available_models}")
    
    # Pull models
    for model_name in MODELS_TO_PULL:
        if model_name in available_models:
            logger.info(f"Model {model_name} is already available")
        else:
            success = pull_model(model_name)
            if not success:
                logger.warning(f"Failed to pull model {model_name}")
    
    # List available models again
    available_models = list_available_models()
    logger.info(f"Available models after pulling: {available_models}")
    
    logger.info("Ollama model puller completed")

if __name__ == "__main__":
    main()
