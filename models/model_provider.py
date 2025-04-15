"""
Model Provider for DMac.

This module provides a unified interface for interacting with different LLM providers.
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple

from utils.secure_logging import get_logger
from config.config import config

logger = get_logger('dmac.models.model_provider')

class BaseModelProvider:
    """Base class for model providers."""
    
    def __init__(self, model_name: str, temperature: float = 0.7):
        """Initialize the model provider.
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation
        """
        self.model_name = model_name
        self.temperature = temperature
    
    async def generate(self, 
                      system_prompt: Optional[str] = None, 
                      user_prompt: str = "",
                      max_tokens: Optional[int] = None) -> str:
        """Generate text from the model.
        
        Args:
            system_prompt: Optional system prompt
            user_prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    async def generate_with_details(self,
                                  system_prompt: Optional[str] = None,
                                  user_prompt: str = "",
                                  max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Generate text from the model with additional details.
        
        Args:
            system_prompt: Optional system prompt
            user_prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dictionary with generated text and additional details
        """
        raise NotImplementedError("Subclasses must implement generate_with_details()")

class OllamaModelProvider(BaseModelProvider):
    """Model provider for Ollama."""
    
    def __init__(self, model_name: str, temperature: float = 0.7):
        """Initialize the Ollama model provider.
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation
        """
        super().__init__(model_name, temperature)
        self.api_base = config.get('models.ollama.api_base', 'http://localhost:11434')
    
    async def generate(self, 
                      system_prompt: Optional[str] = None, 
                      user_prompt: str = "",
                      max_tokens: Optional[int] = None) -> str:
        """Generate text from the model.
        
        Args:
            system_prompt: Optional system prompt
            user_prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text
        """
        result = await self.generate_with_details(system_prompt, user_prompt, max_tokens)
        return result.get('response', '')
    
    async def generate_with_details(self,
                                  system_prompt: Optional[str] = None,
                                  user_prompt: str = "",
                                  max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Generate text from the model with additional details.
        
        Args:
            system_prompt: Optional system prompt
            user_prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dictionary with generated text and additional details
        """
        # Prepare the request
        url = f"{self.api_base}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": user_prompt,
            "temperature": self.temperature,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error from Ollama API: {error_text}")
                        return {
                            "response": f"Error: {error_text}",
                            "success": False,
                            "error": error_text
                        }
                    
                    result = await response.json()
                    
                    return {
                        "response": result.get('response', ''),
                        "success": True,
                        "model": self.model_name,
                        "tokens": result.get('eval_count', 0) + result.get('prompt_eval_count', 0),
                        "prompt_tokens": result.get('prompt_eval_count', 0),
                        "completion_tokens": result.get('eval_count', 0),
                        "total_duration": result.get('total_duration', 0),
                        "load_duration": result.get('load_duration', 0),
                        "prompt_eval_duration": result.get('prompt_eval_duration', 0),
                        "eval_duration": result.get('eval_duration', 0)
                    }
                    
        except Exception as e:
            logger.error(f"Error generating from Ollama: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def stream_generate(self,
                            system_prompt: Optional[str] = None,
                            user_prompt: str = "",
                            max_tokens: Optional[int] = None):
        """Stream generated text from the model.
        
        Args:
            system_prompt: Optional system prompt
            user_prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            
        Yields:
            Generated text chunks
        """
        # Prepare the request
        url = f"{self.api_base}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": user_prompt,
            "temperature": self.temperature,
            "stream": True
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error from Ollama API: {error_text}")
                        yield f"Error: {error_text}"
                        return
                    
                    # Process the streaming response
                    async for line in response.content:
                        if not line:
                            continue
                            
                        try:
                            chunk = json.loads(line)
                            if 'response' in chunk:
                                yield chunk['response']
                        except json.JSONDecodeError:
                            logger.error(f"Error decoding JSON from Ollama: {line}")
                            continue
                    
        except Exception as e:
            logger.error(f"Error streaming from Ollama: {str(e)}")
            yield f"Error: {str(e)}"

class ModelProviderFactory:
    """Factory for creating model providers."""
    
    @staticmethod
    def create_provider(provider_type: str, model_name: str, temperature: float = 0.7) -> BaseModelProvider:
        """Create a model provider of the specified type.
        
        Args:
            provider_type: Type of provider (ollama, openai, etc.)
            model_name: Name of the model to use
            temperature: Temperature for generation
            
        Returns:
            Model provider instance
        """
        if provider_type == 'ollama':
            return OllamaModelProvider(model_name, temperature)
        else:
            logger.warning(f"Unsupported provider type: {provider_type}, falling back to Ollama")
            return OllamaModelProvider(model_name, temperature)
    
    @staticmethod
    def create_default_provider(model_name: Optional[str] = None, temperature: float = 0.7) -> BaseModelProvider:
        """Create a default model provider.
        
        Args:
            model_name: Name of the model to use (defaults to config value)
            temperature: Temperature for generation
            
        Returns:
            Model provider instance
        """
        provider_type = config.get('models.default_provider', 'ollama')
        default_model = config.get('models.default_model', 'gemma:7b')
        
        return ModelProviderFactory.create_provider(
            provider_type=provider_type,
            model_name=model_name or default_model,
            temperature=temperature
        )

# Create a singleton instance
model_provider_factory = ModelProviderFactory()
