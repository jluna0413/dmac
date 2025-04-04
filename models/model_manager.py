"""
Model manager for DMac.

This module manages the AI models used by DMac, including:
- Switching between Gemini 2.5 Pro and local LLMs based on usage caps
- Ensuring DeepSeek-RL learns from Gemini interactions
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import ollama manager
from models.ollama_manager import ollama_manager

from config.config import config
from config.credentials import credentials
from models.model_types import ModelType

# Import after ModelType to avoid circular imports
from models.learning_system import LearningSystem

logger = logging.getLogger('dmac.models')


class ModelManager:
    """Manager for AI models used by DMac."""

    def __init__(self):
        """Initialize the model manager."""
        # Get Gemini API key from credentials (more secure than config)
        self.gemini_api_key = credentials.get('models.gemini.api_key', '')
        self.gemini_api_url = config.get('models.gemini.api_url', 'http://gemini.google.com')
        self.gemini_usage: Dict[str, int] = self._load_gemini_usage()
        # Set the usage cap with a default of 1000 requests
        self.gemini_usage_cap = 1000

        self.deepseek_model_name: str = str(config.get('models.deepseek.model_name', 'GandalfBaum/deepseek_r1-claude3.7'))
        self.deepseek_learning_enabled = config.get('models.deepseek.learning_enabled', True)

        self.local_model_name: str = str(config.get('models.local.model_name', 'gemma3:12b'))

        self.logger = logging.getLogger('dmac.models')

        # Use the Ollama manager
        self.ollama_manager = ollama_manager

        # Cache for model responses
        self.response_cache = {}

        # Initialize the learning system
        self.learning_system = LearningSystem()

    async def initialize(self) -> bool:
        """Initialize the model manager.

        Returns:
            True if initialization was successful, False otherwise.
        """
        self.logger.info("Initializing model manager")

        # Start the Ollama manager
        try:
            await self.ollama_manager.start()
            self.logger.info("Ollama manager started")
        except Exception as e:
            self.logger.error(f"Failed to start Ollama manager: {e}")
            self.logger.error("Ollama is required for DMac to function properly.")
            self.logger.error("Please ensure Ollama is installed and running.")
            self.logger.error("Installation instructions: https://ollama.com/download")
            return False

        # Check if the required models are available
        try:
            models = await self._get_available_models()
            model_names = [model.get('name') for model in models]

            if self.deepseek_model_name not in model_names:
                self.logger.warning(f"DeepSeek model '{self.deepseek_model_name}' not found. Attempting to pull it.")
                await self._pull_model(self.deepseek_model_name)

            if self.local_model_name not in model_names:
                self.logger.warning(f"Local model '{self.local_model_name}' not found. Attempting to pull it.")
                await self._pull_model(self.local_model_name)

            self.logger.info("Required models are available")
        except Exception as e:
            self.logger.exception(f"Error checking available models: {e}")
            return False

        # Initialize the learning system
        try:
            if await self.learning_system.initialize():
                self.logger.info("Learning system initialized")
            else:
                self.logger.warning("Learning system initialization failed")
        except Exception as e:
            self.logger.exception(f"Error initializing learning system: {e}")

        self.logger.info("Model manager initialized")
        return True

    async def _get_available_models(self) -> List[Dict[str, Any]]:
        """Get a list of available models.

        Returns:
            A list of dictionaries containing information about available models.
        """
        try:
            # Use the Ollama manager to get available models
            return await self.ollama_manager.list_models()
        except Exception as e:
            self.logger.exception(f"Error getting available models: {e}")
            return []

    async def _pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama.

        Args:
            model_name: Name of the model to pull.

        Returns:
            True if the model was pulled successfully, False otherwise.
        """
        return await self.ollama_manager.pull_model(model_name)

    def _load_gemini_usage(self) -> Dict[str, int]:
        """Load Gemini usage data from a file.

        Returns:
            A dictionary containing Gemini usage data.
        """
        usage_path = Path('models/gemini_usage.json')

        if not usage_path.exists():
            return {
                'total_requests': 0,
                'daily_requests': 0,
                'last_reset': int(time.time()),
            }

        try:
            with open(usage_path, 'r') as f:
                usage = json.load(f)

            # Reset daily usage if it's been more than a day
            last_reset = usage.get('last_reset', 0)
            if time.time() - last_reset > 86400:  # 24 hours in seconds
                usage['daily_requests'] = 0
                usage['last_reset'] = int(time.time())
                self._save_gemini_usage(usage)

            return usage
        except Exception as e:
            self.logger.exception(f"Error loading Gemini usage data: {e}")
            return {
                'total_requests': 0,
                'daily_requests': 0,
                'last_reset': int(time.time()),
            }

    def _save_gemini_usage(self, usage: Dict[str, int]) -> None:
        """Save Gemini usage data to a file.

        Args:
            usage: A dictionary containing Gemini usage data.
        """
        usage_path = Path('models/gemini_usage.json')

        try:
            # Create the directory if it doesn't exist
            usage_path.parent.mkdir(parents=True, exist_ok=True)

            with open(usage_path, 'w') as f:
                json.dump(usage, f)
        except Exception as e:
            self.logger.exception(f"Error saving Gemini usage data: {e}")

    def _update_gemini_usage(self) -> None:
        """Update Gemini usage data."""
        self.gemini_usage['total_requests'] += 1
        self.gemini_usage['daily_requests'] += 1
        self._save_gemini_usage(self.gemini_usage)

    def _should_use_gemini(self) -> bool:
        """Check if Gemini should be used based on usage caps.

        Returns:
            True if Gemini should be used, False otherwise.
        """
        # Check if Gemini API key is available
        if not self.gemini_api_key:
            self.logger.warning("Gemini API key not available")
            return False

        # Check if we've reached the usage cap
        if self.gemini_usage['daily_requests'] >= self.gemini_usage_cap:
            self.logger.warning(f"Gemini daily usage cap reached ({self.gemini_usage_cap} requests)")
            return False

        return True

    # Learning data methods have been moved to the LearningSystem class

    async def generate_text(self, prompt: str, model_type: Optional[ModelType] = None) -> str:
        """Generate text using an AI model.

        Args:
            prompt: The prompt to generate text from.
            model_type: The type of model to use. If not provided, the best available model will be used.

        Returns:
            The generated text.
        """
        # Check if we have a cached response
        cache_key = f"{prompt}_{model_type.value if model_type else 'auto'}"
        if cache_key in self.response_cache:
            self.logger.info(f"Using cached response for prompt: {prompt[:50]}...")
            return self.response_cache[cache_key]

        # Determine which model to use
        if model_type is None:
            if self._should_use_gemini():
                model_type = ModelType.GEMINI
            else:
                model_type = ModelType.LOCAL

        # Generate text using the selected model
        if model_type == ModelType.GEMINI:
            response = await self._generate_with_gemini(prompt)

            # Save for learning
            await self.learning_system.save_learning_example(prompt, response, model_type)
        elif model_type == ModelType.DEEPSEEK:
            response = await self._generate_with_deepseek(prompt)
            # Save for learning
            await self.learning_system.save_learning_example(prompt, response, model_type)
        else:  # ModelType.LOCAL
            response = await self._generate_with_local(prompt)
            # Save for learning
            await self.learning_system.save_learning_example(prompt, response, model_type)

        # Cache the response
        self.response_cache[cache_key] = response

        return response

    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate text using Gemini.

        Args:
            prompt: The prompt to generate text from.

        Returns:
            The generated text.
        """
        self.logger.info(f"Generating text with Gemini: {prompt[:50]}...")

        # Update usage statistics
        self._update_gemini_usage()

        try:
            # In a real implementation, you would use the Gemini API
            # For now, we'll simulate a response

            # TODO: Implement actual Gemini API call
            # Example:
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         f"{self.gemini_api_url}/v1/models/gemini-pro:generateContent",
            #         headers={"Authorization": f"Bearer {self.gemini_api_key}"},
            #         json={"contents": [{"parts": [{"text": prompt}]}]}
            #     )
            #     data = response.json()
            #     return data["candidates"][0]["content"]["parts"][0]["text"]

            # Check if we have a valid API key
            if not self.gemini_api_key:
                self.logger.warning("No Gemini API key provided in credentials")
                self.logger.info("To use Gemini, add your API key to config/credentials.json or set the DMAC_MODELS_GEMINI_API_KEY environment variable")
                self.logger.info("Falling back to local model")
                return await self._generate_with_local(prompt)

            # Simulate some processing time
            await asyncio.sleep(2)

            # Simulated response
            return f"Gemini response to: {prompt[:50]}...\n\nThis is a simulated response from Gemini 2.5 Pro."
        except Exception as e:
            self.logger.exception(f"Error generating text with Gemini: {e}")
            # Fall back to local model
            return await self._generate_with_local(prompt)

    async def _generate_with_deepseek(self, prompt: str) -> str:
        """Generate text using DeepSeek-RL.

        Args:
            prompt: The prompt to generate text from.

        Returns:
            The generated text.
        """
        self.logger.info(f"Generating text with DeepSeek: {prompt[:50]}...")

        try:
            # Use Ollama manager to generate text with DeepSeek
            response_text = await self.ollama_manager.generate(
                prompt=prompt,
                model=self.deepseek_model_name,
                temperature=0.7,
                top_p=0.9,
                max_tokens=1024
            )

            # Add to learning system
            if self.deepseek_learning_enabled:
                # This is a placeholder for the learning system integration
                # In a real implementation, this would add the example to the learning system
                pass

            return response_text
        except Exception as e:
            self.logger.exception(f"Error generating text with DeepSeek: {e}")
            # Fall back to local model
            return await self._generate_with_local(prompt)

    async def _generate_with_local(self, prompt: str) -> str:
        """Generate text using a local model.

        Args:
            prompt: The prompt to generate text from.

        Returns:
            The generated text.
        """
        self.logger.info(f"Generating text with local model: {prompt[:50]}...")

        try:
            # Use Ollama manager to generate text with the local model
            response_text = await self.ollama_manager.generate(
                prompt=prompt,
                model=self.local_model_name,
                temperature=0.7,
                top_p=0.9,
                max_tokens=1024
            )

            # Add to learning system
            # This is a placeholder for the learning system integration
            # In a real implementation, this would add the example to the learning system

            return response_text
        except Exception as e:
            self.logger.exception(f"Error generating text with local model: {e}")
            return f"Error generating text: {str(e)}"

    async def train_deepseek(self) -> bool:
        """Train DeepSeek-RL using the learning data.

        Returns:
            True if training was successful, False otherwise.
        """
        self.logger.info("Training DeepSeek-RL model")

        # Use the enhanced learning system to train the model
        return await self.learning_system.train_model()

    async def provide_feedback(self, prompt: str, response: str, feedback: str, rating: int) -> bool:
        """Provide feedback on a response.

        Args:
            prompt: The prompt that generated the response.
            response: The response to provide feedback on.
            feedback: The feedback text.
            rating: The rating (1-5).

        Returns:
            True if feedback was saved successfully, False otherwise.
        """
        self.logger.info(f"Providing feedback with rating {rating}")

        # Save the feedback using the learning system
        await self.learning_system.save_feedback(prompt, response, feedback, rating)

        # Apply the feedback to improve the model
        return await self.learning_system.apply_feedback()

    async def cleanup(self) -> None:
        """Clean up resources used by the model manager."""
        self.logger.info("Cleaning up model manager")

        # Save any unsaved data
        self._save_gemini_usage(self.gemini_usage)

        # Clean up the learning system
        try:
            await self.learning_system.cleanup()
            self.logger.info("Learning system cleaned up")
        except Exception as e:
            self.logger.exception(f"Error cleaning up learning system: {e}")

        # Clean up the Ollama manager
        try:
            await self.ollama_manager.stop()
            self.logger.info("Ollama manager stopped")
        except Exception as e:
            self.logger.exception(f"Error stopping Ollama manager: {e}")

        self.logger.info("Model manager cleaned up")
