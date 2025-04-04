"""
Ollama integration for DMac.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
import ollama

from config.config import config

logger = logging.getLogger('dmac.models.ollama')


class OllamaIntegration:
    """Ollama integration for DMac."""
    
    def __init__(self):
        """Initialize the Ollama integration."""
        self.client = None
        self.api_url = config.get('models.ollama.api_url', 'http://localhost:11434')
        self.models_dir = Path(config.get('models.ollama.models_dir', 'models/ollama'))
        self.performance_data_file = self.models_dir / 'performance_data.json'
        self.model_usage_file = self.models_dir / 'model_usage.json'
        
        # Performance data
        self.performance_data = {}
        
        # Model usage data
        self.model_usage = {}
        
        # Logger
        self.logger = logging.getLogger('dmac.models.ollama')
    
    async def initialize(self) -> bool:
        """Initialize the Ollama integration.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        self.logger.info("Initializing Ollama integration")
        
        try:
            # Create the models directory if it doesn't exist
            os.makedirs(self.models_dir, exist_ok=True)
            
            # Initialize the Ollama client
            self.client = ollama.Client(host=self.api_url)
            self.logger.info("Ollama client initialized")
            
            # Load performance data
            await self._load_performance_data()
            
            # Load model usage data
            await self._load_model_usage()
            
            self.logger.info("Ollama integration initialized")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing Ollama integration: {e}")
            return False
    
    async def _load_performance_data(self) -> None:
        """Load performance data from file."""
        if os.path.exists(self.performance_data_file):
            try:
                with open(self.performance_data_file, 'r') as f:
                    self.performance_data = json.load(f)
                self.logger.info(f"Loaded performance data for {len(self.performance_data)} models")
            except Exception as e:
                self.logger.exception(f"Error loading performance data: {e}")
                self.performance_data = {}
        else:
            self.logger.info("No performance data file found, creating a new one")
            self.performance_data = {}
            await self._save_performance_data()
    
    async def _save_performance_data(self) -> None:
        """Save performance data to file."""
        try:
            with open(self.performance_data_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
            self.logger.info(f"Saved performance data for {len(self.performance_data)} models")
        except Exception as e:
            self.logger.exception(f"Error saving performance data: {e}")
    
    async def _load_model_usage(self) -> None:
        """Load model usage data from file."""
        if os.path.exists(self.model_usage_file):
            try:
                with open(self.model_usage_file, 'r') as f:
                    self.model_usage = json.load(f)
                self.logger.info(f"Loaded usage data for {len(self.model_usage)} models")
            except Exception as e:
                self.logger.exception(f"Error loading model usage data: {e}")
                self.model_usage = {}
        else:
            self.logger.info("No model usage file found, creating a new one")
            self.model_usage = {}
            await self._save_model_usage()
    
    async def _save_model_usage(self) -> None:
        """Save model usage data to file."""
        try:
            with open(self.model_usage_file, 'w') as f:
                json.dump(self.model_usage, f, indent=2)
            self.logger.info(f"Saved usage data for {len(self.model_usage)} models")
        except Exception as e:
            self.logger.exception(f"Error saving model usage data: {e}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get a list of available models.
        
        Returns:
            A list of available models with their details.
        """
        try:
            # Use the Ollama client to list models
            response = await asyncio.to_thread(self.client.list)
            
            # Extract model details
            models = []
            for model in response.get('models', []):
                model_name = model.get('name', '')
                if model_name:
                    # Get model details
                    model_details = {
                        'name': model_name,
                        'size': model.get('size', 0),
                        'modified_at': model.get('modified_at', ''),
                        'performance': self.performance_data.get(model_name, {}),
                        'usage': self.model_usage.get(model_name, {
                            'count': 0,
                            'last_used': None,
                            'total_tokens': 0,
                            'total_time': 0,
                        }),
                    }
                    models.append(model_details)
            
            return models
        except Exception as e:
            self.logger.exception(f"Error getting available models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama.
        
        Args:
            model_name: Name of the model to pull.
            
        Returns:
            True if the model was pulled successfully, False otherwise.
        """
        try:
            self.logger.info(f"Pulling model: {model_name}")
            await asyncio.to_thread(self.client.pull, model_name)
            self.logger.info(f"Model pulled successfully: {model_name}")
            
            # Initialize performance data for the model if it doesn't exist
            if model_name not in self.performance_data:
                self.performance_data[model_name] = {
                    'avg_tokens_per_second': 0,
                    'avg_response_time': 0,
                    'total_requests': 0,
                    'total_tokens': 0,
                    'total_time': 0,
                }
                await self._save_performance_data()
            
            # Initialize usage data for the model if it doesn't exist
            if model_name not in self.model_usage:
                self.model_usage[model_name] = {
                    'count': 0,
                    'last_used': None,
                    'total_tokens': 0,
                    'total_time': 0,
                }
                await self._save_model_usage()
            
            return True
        except Exception as e:
            self.logger.exception(f"Error pulling model {model_name}: {e}")
            return False
    
    async def generate(self, model_name: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate text using a model.
        
        Args:
            model_name: Name of the model to use.
            prompt: The prompt to generate text from.
            options: Options for the generation.
            
        Returns:
            The generated text and metadata.
        """
        if options is None:
            options = {}
        
        try:
            self.logger.info(f"Generating text with model {model_name}: {prompt[:50]}...")
            
            # Record start time
            start_time = time.time()
            
            # Generate text
            response = await asyncio.to_thread(
                self.client.generate,
                model=model_name,
                prompt=prompt,
                options=options
            )
            
            # Record end time
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Extract response text
            response_text = response.get('response', '')
            
            # Extract metadata
            metadata = {
                'model': model_name,
                'prompt': prompt,
                'response': response_text,
                'generation_time': generation_time,
                'total_duration': response.get('total_duration', 0),
                'load_duration': response.get('load_duration', 0),
                'prompt_eval_count': response.get('prompt_eval_count', 0),
                'prompt_eval_duration': response.get('prompt_eval_duration', 0),
                'eval_count': response.get('eval_count', 0),
                'eval_duration': response.get('eval_duration', 0),
            }
            
            # Update performance data
            await self._update_performance_data(model_name, metadata)
            
            # Update usage data
            await self._update_model_usage(model_name, metadata)
            
            return {
                'text': response_text,
                'metadata': metadata,
            }
        except Exception as e:
            self.logger.exception(f"Error generating text with model {model_name}: {e}")
            return {
                'text': f"Error generating text: {str(e)}",
                'metadata': {
                    'model': model_name,
                    'prompt': prompt,
                    'error': str(e),
                },
            }
    
    async def _update_performance_data(self, model_name: str, metadata: Dict[str, Any]) -> None:
        """Update performance data for a model.
        
        Args:
            model_name: Name of the model.
            metadata: Metadata from the generation.
        """
        if model_name not in self.performance_data:
            self.performance_data[model_name] = {
                'avg_tokens_per_second': 0,
                'avg_response_time': 0,
                'total_requests': 0,
                'total_tokens': 0,
                'total_time': 0,
            }
        
        # Extract data from metadata
        eval_count = metadata.get('eval_count', 0)
        generation_time = metadata.get('generation_time', 0)
        
        # Update performance data
        performance_data = self.performance_data[model_name]
        performance_data['total_requests'] += 1
        performance_data['total_tokens'] += eval_count
        performance_data['total_time'] += generation_time
        
        # Calculate averages
        if performance_data['total_time'] > 0:
            performance_data['avg_tokens_per_second'] = performance_data['total_tokens'] / performance_data['total_time']
        
        if performance_data['total_requests'] > 0:
            performance_data['avg_response_time'] = performance_data['total_time'] / performance_data['total_requests']
        
        # Save performance data
        await self._save_performance_data()
    
    async def _update_model_usage(self, model_name: str, metadata: Dict[str, Any]) -> None:
        """Update usage data for a model.
        
        Args:
            model_name: Name of the model.
            metadata: Metadata from the generation.
        """
        if model_name not in self.model_usage:
            self.model_usage[model_name] = {
                'count': 0,
                'last_used': None,
                'total_tokens': 0,
                'total_time': 0,
            }
        
        # Extract data from metadata
        eval_count = metadata.get('eval_count', 0)
        generation_time = metadata.get('generation_time', 0)
        
        # Update usage data
        usage_data = self.model_usage[model_name]
        usage_data['count'] += 1
        usage_data['last_used'] = time.time()
        usage_data['total_tokens'] += eval_count
        usage_data['total_time'] += generation_time
        
        # Save usage data
        await self._save_model_usage()
    
    async def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """Get performance data for a model.
        
        Args:
            model_name: Name of the model.
            
        Returns:
            Performance data for the model.
        """
        return self.performance_data.get(model_name, {})
    
    async def get_model_usage(self, model_name: str) -> Dict[str, Any]:
        """Get usage data for a model.
        
        Args:
            model_name: Name of the model.
            
        Returns:
            Usage data for the model.
        """
        return self.model_usage.get(model_name, {})
    
    async def get_all_model_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance data for all models.
        
        Returns:
            Performance data for all models.
        """
        return self.performance_data
    
    async def get_all_model_usage(self) -> Dict[str, Dict[str, Any]]:
        """Get usage data for all models.
        
        Returns:
            Usage data for all models.
        """
        return self.model_usage
    
    async def cleanup(self) -> None:
        """Clean up resources used by the Ollama integration."""
        self.logger.info("Cleaning up Ollama integration")
        
        # Save performance data
        await self._save_performance_data()
        
        # Save model usage data
        await self._save_model_usage()
        
        self.logger.info("Ollama integration cleaned up")
