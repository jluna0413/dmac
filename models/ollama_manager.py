"""
Ollama Manager for DMac.

This module provides integration with Ollama for local model management.
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any

from config.config import config
from utils.secure_logging import get_logger

logger = get_logger('dmac.models.ollama_manager')


class OllamaManager:
    """Manager for Ollama models."""
    
    def __init__(self):
        """Initialize the Ollama manager."""
        self.api_url = config.get('models.ollama.api_url', 'http://localhost:11434')
        self.models_dir = config.get('models.ollama.models_dir', 'models/ollama')
        self.session = None
        self.models_cache = {}
        self.models_cache_time = 0
        self.cache_ttl = 300  # 5 minutes
        
        # Create the models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info(f"Initialized Ollama manager with API URL: {self.api_url}")
    
    async def start(self) -> None:
        """Start the Ollama manager."""
        if self.session is not None:
            logger.warning("Ollama manager is already started")
            return
        
        self.session = aiohttp.ClientSession()
        
        logger.info("Started Ollama manager")
    
    async def stop(self) -> None:
        """Stop the Ollama manager."""
        if self.session is None:
            logger.warning("Ollama manager is not started")
            return
        
        await self.session.close()
        self.session = None
        
        logger.info("Stopped Ollama manager")
    
    async def list_models(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """List all available models.
        
        Args:
            force_refresh: Whether to force a refresh of the models cache.
            
        Returns:
            A list of dictionaries containing information about available models.
        """
        # Check if we need to refresh the cache
        current_time = time.time()
        if force_refresh or self.session is None or current_time - self.models_cache_time > self.cache_ttl:
            await self._refresh_models_cache()
        
        return list(self.models_cache.values())
    
    async def get_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model.
        
        Args:
            model_name: The name of the model to get information about.
            
        Returns:
            A dictionary containing information about the model, or None if the model was not found.
        """
        # Check if we need to refresh the cache
        current_time = time.time()
        if self.session is None or current_time - self.models_cache_time > self.cache_ttl:
            await self._refresh_models_cache()
        
        return self.models_cache.get(model_name)
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama.
        
        Args:
            model_name: The name of the model to pull.
            
        Returns:
            True if the model was pulled successfully, False otherwise.
        """
        if self.session is None:
            logger.warning("Ollama manager is not started")
            return False
        
        try:
            url = f"{self.api_url}/api/pull"
            data = {"name": model_name}
            
            async with self.session.post(url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error pulling model {model_name}: {error_text}")
                    return False
                
                # The pull operation is asynchronous, so we need to wait for it to complete
                # We'll poll the API to check if the model is available
                for _ in range(60):  # Wait for up to 60 seconds
                    if await self._is_model_available(model_name):
                        break
                    await asyncio.sleep(1)
                
                # Refresh the models cache
                await self._refresh_models_cache()
                
                logger.info(f"Pulled model {model_name}")
                return True
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model from Ollama.
        
        Args:
            model_name: The name of the model to delete.
            
        Returns:
            True if the model was deleted successfully, False otherwise.
        """
        if self.session is None:
            logger.warning("Ollama manager is not started")
            return False
        
        try:
            url = f"{self.api_url}/api/delete"
            data = {"name": model_name}
            
            async with self.session.delete(url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error deleting model {model_name}: {error_text}")
                    return False
                
                # Refresh the models cache
                await self._refresh_models_cache()
                
                logger.info(f"Deleted model {model_name}")
                return True
        except Exception as e:
            logger.error(f"Error deleting model {model_name}: {e}")
            return False
    
    async def generate(self, prompt: str, model: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate a response using a model.
        
        Args:
            prompt: The prompt to generate from.
            model: The name of the model to use.
            system_prompt: An optional system prompt to provide context.
            **kwargs: Additional parameters for the generation.
            
        Returns:
            The generated response.
        """
        if self.session is None:
            logger.warning("Ollama manager is not started")
            return "Error: Ollama manager is not started"
        
        try:
            url = f"{self.api_url}/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
            }
            
            if system_prompt:
                data["system"] = system_prompt
            
            # Add any additional parameters
            data.update(kwargs)
            
            async with self.session.post(url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error generating response with model {model}: {error_text}")
                    return f"Error: {error_text}"
                
                # Parse the response
                response_text = await response.text()
                
                # The response is a series of JSON objects, one per line
                # We need to concatenate the 'response' field from each object
                result = ""
                for line in response_text.strip().split('\n'):
                    try:
                        data = json.loads(line)
                        result += data.get('response', '')
                    except json.JSONDecodeError:
                        logger.warning(f"Error parsing response line: {line}")
                
                return result
        except Exception as e:
            logger.error(f"Error generating response with model {model}: {e}")
            return f"Error: {e}"
    
    async def chat(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
        """Generate a chat response using a model.
        
        Args:
            messages: A list of message dictionaries with 'role' and 'content' fields.
            model: The name of the model to use.
            **kwargs: Additional parameters for the generation.
            
        Returns:
            The generated response.
        """
        if self.session is None:
            logger.warning("Ollama manager is not started")
            return "Error: Ollama manager is not started"
        
        try:
            url = f"{self.api_url}/api/chat"
            data = {
                "model": model,
                "messages": messages,
            }
            
            # Add any additional parameters
            data.update(kwargs)
            
            async with self.session.post(url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error generating chat response with model {model}: {error_text}")
                    return f"Error: {error_text}"
                
                # Parse the response
                response_json = await response.json()
                
                return response_json.get('message', {}).get('content', '')
        except Exception as e:
            logger.error(f"Error generating chat response with model {model}: {e}")
            return f"Error: {e}"
    
    async def embeddings(self, text: str, model: str) -> List[float]:
        """Generate embeddings for a text using a model.
        
        Args:
            text: The text to generate embeddings for.
            model: The name of the model to use.
            
        Returns:
            A list of embedding values.
        """
        if self.session is None:
            logger.warning("Ollama manager is not started")
            return []
        
        try:
            url = f"{self.api_url}/api/embeddings"
            data = {
                "model": model,
                "prompt": text,
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error generating embeddings with model {model}: {error_text}")
                    return []
                
                # Parse the response
                response_json = await response.json()
                
                return response_json.get('embedding', [])
        except Exception as e:
            logger.error(f"Error generating embeddings with model {model}: {e}")
            return []
    
    async def _refresh_models_cache(self) -> None:
        """Refresh the models cache."""
        if self.session is None:
            logger.warning("Ollama manager is not started")
            return
        
        try:
            url = f"{self.api_url}/api/tags"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error listing models: {error_text}")
                    return
                
                # Parse the response
                response_json = await response.json()
                models = response_json.get('models', [])
                
                # Update the cache
                self.models_cache = {}
                for model in models:
                    model_name = model.get('name')
                    if model_name:
                        self.models_cache[model_name] = model
                
                self.models_cache_time = time.time()
                
                logger.debug(f"Refreshed models cache with {len(self.models_cache)} models")
        except Exception as e:
            logger.error(f"Error refreshing models cache: {e}")
    
    async def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available.
        
        Args:
            model_name: The name of the model to check.
            
        Returns:
            True if the model is available, False otherwise.
        """
        if self.session is None:
            logger.warning("Ollama manager is not started")
            return False
        
        try:
            url = f"{self.api_url}/api/tags"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return False
                
                # Parse the response
                response_json = await response.json()
                models = response_json.get('models', [])
                
                # Check if the model is in the list
                for model in models:
                    if model.get('name') == model_name:
                        return True
                
                return False
        except Exception:
            return False


# Create a singleton instance
ollama_manager = OllamaManager()
