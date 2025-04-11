"""
WebArena Ollama Integration for DMac.

This module provides integration between WebArena and Ollama models.
"""

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors, ModelError
from models.ollama_manager import ollama_manager

logger = get_logger('dmac.webarena.ollama_integration')


class WebArenaOllamaIntegration:
    """Integration between WebArena and Ollama models."""
    
    def __init__(self):
        """Initialize the WebArena Ollama integration."""
        # Load configuration
        self.enabled = config.get('webarena.ollama.enabled', True)
        self.webarena_dir = Path(config.get('webarena.dir', 'external/webarena'))
        self.models_dir = self.webarena_dir / 'models' / 'ollama'
        self.default_system_prompt = config.get('webarena.ollama.default_system_prompt', 
            "You are a helpful AI assistant that controls a web browser to help users with their tasks. "
            "You will be given a task to complete, and you should generate the actions to take in the browser. "
            "You can see the current state of the browser, and you should generate the next action to take. "
            "The available actions are: click, type, press, scroll, and select."
        )
        
        # Create directories if they don't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info("WebArena Ollama integration initialized")
    
    async def initialize(self) -> bool:
        """Initialize the WebArena Ollama integration.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            logger.info("WebArena Ollama integration is disabled")
            return True
        
        try:
            # Check if Ollama is available
            if not await self._is_ollama_available():
                logger.warning("Ollama is not available")
                return False
            
            # Create the Ollama model configuration
            await self._create_model_config()
            
            logger.info("WebArena Ollama integration initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing WebArena Ollama integration: {e}")
            return False
    
    @handle_async_errors(default_message="Error getting available Ollama models")
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get the available Ollama models for WebArena.
        
        Returns:
            A list of dictionaries containing model information.
        """
        if not self.enabled:
            logger.warning("WebArena Ollama integration is disabled")
            return []
        
        # Check if Ollama is available
        if not await self._is_ollama_available():
            logger.warning("Ollama is not available")
            return []
        
        try:
            # Get the available models from Ollama
            models = await ollama_manager.list_models()
            
            # Filter and format the models
            webarena_models = []
            for model in models:
                model_name = model.get('name')
                if model_name:
                    webarena_models.append({
                        'name': model_name,
                        'description': f"Ollama model: {model_name}",
                        'type': 'ollama',
                    })
            
            # Sort by name
            webarena_models.sort(key=lambda x: x['name'])
            
            return webarena_models
        except Exception as e:
            logger.exception(f"Error getting available Ollama models: {e}")
            return []
    
    @handle_async_errors(default_message="Error updating model configuration")
    async def update_model_config(self, model_name: str, system_prompt: Optional[str] = None) -> bool:
        """Update the configuration for an Ollama model.
        
        Args:
            model_name: The name of the model to update.
            system_prompt: Optional system prompt for the model.
            
        Returns:
            True if the configuration was updated successfully, False otherwise.
        """
        if not self.enabled:
            logger.warning("WebArena Ollama integration is disabled")
            raise ModelError("WebArena Ollama integration is disabled")
        
        # Check if Ollama is available
        if not await self._is_ollama_available():
            logger.warning("Ollama is not available")
            raise ModelError("Ollama is not available")
        
        # Check if the model exists
        model = await ollama_manager.get_model(model_name)
        if not model:
            logger.warning(f"Ollama model '{model_name}' not found")
            raise ModelError(f"Ollama model '{model_name}' not found")
        
        # Create the model configuration
        config_path = self.models_dir / f"{model_name}.json"
        
        try:
            # Create the configuration
            config = {
                'name': model_name,
                'type': 'ollama',
                'system_prompt': system_prompt or self.default_system_prompt,
                'updated_at': time.time(),
            }
            
            # Save the configuration
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Updated configuration for Ollama model '{model_name}'")
            return True
        except Exception as e:
            logger.exception(f"Error updating configuration for Ollama model '{model_name}': {e}")
            raise ModelError(f"Error updating configuration for Ollama model '{model_name}': {e}")
    
    @handle_async_errors(default_message="Error getting model configuration")
    async def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get the configuration for an Ollama model.
        
        Args:
            model_name: The name of the model to get the configuration for.
            
        Returns:
            A dictionary containing the model configuration, or None if the model was not found.
        """
        if not self.enabled:
            logger.warning("WebArena Ollama integration is disabled")
            raise ModelError("WebArena Ollama integration is disabled")
        
        # Check if the model configuration exists
        config_path = self.models_dir / f"{model_name}.json"
        
        if not config_path.exists():
            logger.warning(f"Configuration for Ollama model '{model_name}' not found")
            return None
        
        try:
            # Load the configuration
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            return config
        except Exception as e:
            logger.exception(f"Error getting configuration for Ollama model '{model_name}': {e}")
            raise ModelError(f"Error getting configuration for Ollama model '{model_name}': {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources used by the WebArena Ollama integration."""
        if not self.enabled:
            logger.debug("WebArena Ollama integration is disabled")
            return
        
        logger.info("Cleaning up WebArena Ollama integration")
        
        # No specific cleanup needed
        
        logger.info("WebArena Ollama integration cleaned up")
    
    async def _is_ollama_available(self) -> bool:
        """Check if Ollama is available.
        
        Returns:
            True if Ollama is available, False otherwise.
        """
        try:
            # Try to list models
            models = await ollama_manager.list_models()
            return len(models) > 0
        except Exception:
            return False
    
    async def _create_model_config(self) -> None:
        """Create the Ollama model configuration for WebArena."""
        # Get the available models
        models = await self.get_available_models()
        
        # Create a configuration for each model
        for model in models:
            model_name = model['name']
            
            # Check if the configuration already exists
            config_path = self.models_dir / f"{model_name}.json"
            
            if not config_path.exists():
                # Create the configuration
                await self.update_model_config(model_name)


# Create a singleton instance
webarena_ollama_integration = WebArenaOllamaIntegration()
