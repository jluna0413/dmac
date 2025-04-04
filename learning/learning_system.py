"""
Learning System for DMac.

This module provides the learning system for learning from model interactions.
"""

import asyncio
import json
import logging
import os
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from config.config import config
from utils.secure_logging import get_logger

logger = get_logger('dmac.learning.learning_system')


class ModelType(Enum):
    """Enum for model types."""
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    LOCAL = "local"
    CUSTOM = "custom"


class LearningSystem:
    """System for learning from model interactions."""
    
    def __init__(self):
        """Initialize the learning system."""
        # Load configuration
        self.enabled = config.get('learning.enabled', True)
        self.data_dir = Path(config.get('learning.data_dir', 'data/learning'))
        self.max_examples = config.get('learning.max_examples', 10000)
        self.batch_size = config.get('learning.batch_size', 32)
        self.learning_rate = config.get('learning.learning_rate', 0.0001)
        
        # Create the data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize learning data
        self.examples = {}
        self.model_examples = {
            ModelType.GEMINI: set(),
            ModelType.DEEPSEEK: set(),
            ModelType.LOCAL: set(),
            ModelType.CUSTOM: set(),
        }
        
        # Initialize learning tasks
        self.learning_tasks = []
        self.is_learning = False
        
        logger.info("Learning system initialized")
    
    async def initialize(self) -> bool:
        """Initialize the learning system.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            logger.info("Learning system is disabled")
            return True
        
        try:
            # Load existing learning examples
            await self._load_examples()
            
            # Start the learning loop
            self.is_learning = True
            learning_task = asyncio.create_task(self._learning_loop())
            self.learning_tasks.append(learning_task)
            
            logger.info("Learning system initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing learning system: {e}")
            return False
    
    async def add_learning_example(self, prompt: str, response: str, model_type: ModelType, 
                                  system_prompt: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a learning example.
        
        Args:
            prompt: The prompt that was used.
            response: The response that was generated.
            model_type: The type of model that generated the response.
            system_prompt: An optional system prompt that was used.
            metadata: Optional metadata about the example.
            
        Returns:
            The ID of the new example.
        """
        if not self.enabled:
            logger.debug("Learning system is disabled, not adding example")
            return ""
        
        # Create a new example
        example_id = f"example_{int(time.time())}_{len(self.examples)}"
        
        example = {
            'id': example_id,
            'prompt': prompt,
            'response': response,
            'model_type': model_type.value,
            'system_prompt': system_prompt,
            'metadata': metadata or {},
            'created_at': time.time(),
            'used_for_learning': False,
        }
        
        # Add the example to the dictionary
        self.examples[example_id] = example
        
        # Add the example to the model-specific set
        self.model_examples[model_type].add(example_id)
        
        # Save the example to disk
        await self._save_example(example)
        
        logger.debug(f"Added learning example {example_id} from {model_type.value} model")
        return example_id
    
    async def get_learning_example(self, example_id: str) -> Optional[Dict[str, Any]]:
        """Get a learning example.
        
        Args:
            example_id: The ID of the example to get.
            
        Returns:
            The example, or None if it was not found.
        """
        if not self.enabled:
            logger.debug("Learning system is disabled")
            return None
        
        return self.examples.get(example_id)
    
    async def get_learning_examples(self, model_type: Optional[ModelType] = None, 
                                   limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get learning examples.
        
        Args:
            model_type: Optional model type to filter by.
            limit: Maximum number of examples to return.
            offset: Offset to start from.
            
        Returns:
            A list of examples.
        """
        if not self.enabled:
            logger.debug("Learning system is disabled")
            return []
        
        if model_type:
            # Get examples for the specified model type
            example_ids = list(self.model_examples[model_type])
            examples = [self.examples[example_id] for example_id in example_ids if example_id in self.examples]
        else:
            # Get all examples
            examples = list(self.examples.values())
        
        # Sort examples by creation time (newest first)
        examples.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply limit and offset
        examples = examples[offset:offset + limit]
        
        return examples
    
    async def delete_learning_example(self, example_id: str) -> bool:
        """Delete a learning example.
        
        Args:
            example_id: The ID of the example to delete.
            
        Returns:
            True if the example was deleted, False otherwise.
        """
        if not self.enabled:
            logger.debug("Learning system is disabled")
            return False
        
        if example_id not in self.examples:
            logger.warning(f"Learning example {example_id} not found")
            return False
        
        # Get the example
        example = self.examples[example_id]
        
        # Remove the example from the dictionary
        del self.examples[example_id]
        
        # Remove the example from the model-specific set
        model_type = ModelType(example['model_type'])
        if example_id in self.model_examples[model_type]:
            self.model_examples[model_type].remove(example_id)
        
        # Delete the example file
        example_path = self.data_dir / f"{example_id}.json"
        if example_path.exists():
            os.remove(example_path)
        
        logger.info(f"Deleted learning example {example_id}")
        return True
    
    async def cleanup(self) -> None:
        """Clean up resources used by the learning system."""
        if not self.enabled:
            logger.debug("Learning system is disabled")
            return
        
        logger.info("Cleaning up learning system")
        
        # Stop the learning loop
        self.is_learning = False
        
        # Cancel all learning tasks
        for task in self.learning_tasks:
            task.cancel()
        
        # Wait for all learning tasks to complete
        if self.learning_tasks:
            await asyncio.gather(*self.learning_tasks, return_exceptions=True)
        
        self.learning_tasks = []
        
        logger.info("Learning system cleaned up")
    
    async def _load_examples(self) -> None:
        """Load learning examples from disk."""
        if not self.data_dir.exists():
            logger.warning(f"Learning data directory {self.data_dir} does not exist")
            return
        
        # Clear existing examples
        self.examples = {}
        for model_type in self.model_examples:
            self.model_examples[model_type] = set()
        
        # Load examples from disk
        example_files = list(self.data_dir.glob("example_*.json"))
        
        for example_file in example_files:
            try:
                with open(example_file, 'r') as f:
                    example = json.load(f)
                
                example_id = example['id']
                
                # Add the example to the dictionary
                self.examples[example_id] = example
                
                # Add the example to the model-specific set
                model_type = ModelType(example['model_type'])
                self.model_examples[model_type].add(example_id)
            except Exception as e:
                logger.exception(f"Error loading learning example from {example_file}: {e}")
        
        logger.info(f"Loaded {len(self.examples)} learning examples")
    
    async def _save_example(self, example: Dict[str, Any]) -> None:
        """Save a learning example to disk.
        
        Args:
            example: The example to save.
        """
        example_id = example['id']
        example_path = self.data_dir / f"{example_id}.json"
        
        try:
            with open(example_path, 'w') as f:
                json.dump(example, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving learning example {example_id}: {e}")
    
    async def _learning_loop(self) -> None:
        """Main learning loop."""
        while self.is_learning:
            try:
                # Check if there are enough examples to learn from
                if len(self.examples) < self.batch_size:
                    # Not enough examples, wait and try again
                    await asyncio.sleep(60)  # Wait for 1 minute
                    continue
                
                # Get examples that haven't been used for learning yet
                unused_examples = [
                    example for example in self.examples.values()
                    if not example['used_for_learning']
                ]
                
                if len(unused_examples) < self.batch_size:
                    # Not enough unused examples, wait and try again
                    await asyncio.sleep(60)  # Wait for 1 minute
                    continue
                
                # Select a batch of examples
                batch = unused_examples[:self.batch_size]
                
                # Learn from the batch
                await self._learn_from_batch(batch)
                
                # Mark the examples as used for learning
                for example in batch:
                    example['used_for_learning'] = True
                    await self._save_example(example)
                
                # Wait before processing the next batch
                await asyncio.sleep(10)  # Wait for 10 seconds
            except asyncio.CancelledError:
                logger.info("Learning loop cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in learning loop: {e}")
                await asyncio.sleep(60)  # Wait for 1 minute before trying again
    
    async def _learn_from_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Learn from a batch of examples.
        
        Args:
            batch: The batch of examples to learn from.
        """
        # This is a placeholder for the actual learning implementation
        # In a real implementation, this would use a machine learning framework
        # to learn from the examples
        
        logger.info(f"Learning from batch of {len(batch)} examples")
        
        # Simulate learning by waiting for a short time
        await asyncio.sleep(1)
        
        logger.info(f"Finished learning from batch of {len(batch)} examples")


# Create a singleton instance
learning_system = LearningSystem()
