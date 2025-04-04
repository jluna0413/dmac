"""
Transfer Learning for DMac.

This module provides transfer learning capabilities for the learning system.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from config.config import config
from utils.secure_logging import get_logger
from learning.learning_system import learning_system, ModelType

logger = get_logger('dmac.learning.transfer_learning')


class TransferLearning:
    """Transfer learning for the learning system."""
    
    def __init__(self):
        """Initialize the transfer learning system."""
        # Load configuration
        self.enabled = config.get('learning.transfer.enabled', True)
        self.data_dir = Path(config.get('learning.transfer.data_dir', 'data/transfer'))
        self.source_model = config.get('learning.transfer.source_model', 'gemini-1.5-pro')
        self.target_model = config.get('learning.transfer.target_model', 'deepseek-coder:6.7b')
        self.batch_size = config.get('learning.transfer.batch_size', 32)
        self.learning_rate = config.get('learning.transfer.learning_rate', 0.0001)
        self.epochs = config.get('learning.transfer.epochs', 10)
        
        # Create the data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize transfer learning data
        self.transfer_pairs = {}
        self.transfer_results = {}
        
        # Initialize learning tasks
        self.learning_tasks = []
        self.is_learning = False
        
        logger.info("Transfer learning system initialized")
    
    async def initialize(self) -> bool:
        """Initialize the transfer learning system.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            logger.info("Transfer learning system is disabled")
            return True
        
        try:
            # Load existing transfer pairs and results
            await self._load_transfer_pairs()
            await self._load_transfer_results()
            
            # Start the learning loop
            self.is_learning = True
            learning_task = asyncio.create_task(self._learning_loop())
            self.learning_tasks.append(learning_task)
            
            logger.info("Transfer learning system initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing transfer learning system: {e}")
            return False
    
    async def add_transfer_pair(self, source_example_id: str, target_example_id: str) -> str:
        """Add a transfer learning pair.
        
        Args:
            source_example_id: The ID of the source example.
            target_example_id: The ID of the target example.
            
        Returns:
            The ID of the new transfer pair.
        """
        if not self.enabled:
            logger.debug("Transfer learning system is disabled, not adding transfer pair")
            return ""
        
        # Get the source and target examples
        source_example = await learning_system.get_learning_example(source_example_id)
        target_example = await learning_system.get_learning_example(target_example_id)
        
        if not source_example:
            logger.warning(f"Source example {source_example_id} not found")
            return ""
        
        if not target_example:
            logger.warning(f"Target example {target_example_id} not found")
            return ""
        
        # Create a new transfer pair
        pair_id = f"pair_{int(time.time())}_{len(self.transfer_pairs)}"
        
        pair = {
            'id': pair_id,
            'source_example_id': source_example_id,
            'target_example_id': target_example_id,
            'source_model_type': source_example['model_type'],
            'target_model_type': target_example['model_type'],
            'created_at': time.time(),
            'used_for_learning': False,
        }
        
        # Add the pair to the dictionary
        self.transfer_pairs[pair_id] = pair
        
        # Save the pair to disk
        await self._save_transfer_pair(pair)
        
        logger.debug(f"Added transfer pair {pair_id} from {source_example['model_type']} to {target_example['model_type']}")
        return pair_id
    
    async def get_transfer_pair(self, pair_id: str) -> Optional[Dict[str, Any]]:
        """Get a transfer pair.
        
        Args:
            pair_id: The ID of the pair to get.
            
        Returns:
            The pair, or None if it was not found.
        """
        if not self.enabled:
            logger.debug("Transfer learning system is disabled")
            return None
        
        return self.transfer_pairs.get(pair_id)
    
    async def get_transfer_pairs(self, source_model_type: Optional[str] = None, 
                               target_model_type: Optional[str] = None, 
                               limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transfer pairs.
        
        Args:
            source_model_type: Optional source model type to filter by.
            target_model_type: Optional target model type to filter by.
            limit: Maximum number of pairs to return.
            offset: Offset to start from.
            
        Returns:
            A list of pairs.
        """
        if not self.enabled:
            logger.debug("Transfer learning system is disabled")
            return []
        
        # Filter pairs by model types
        pairs = []
        for pair in self.transfer_pairs.values():
            if source_model_type and pair['source_model_type'] != source_model_type:
                continue
            
            if target_model_type and pair['target_model_type'] != target_model_type:
                continue
            
            pairs.append(pair)
        
        # Sort pairs by creation time (newest first)
        pairs.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply limit and offset
        pairs = pairs[offset:offset + limit]
        
        return pairs
    
    async def delete_transfer_pair(self, pair_id: str) -> bool:
        """Delete a transfer pair.
        
        Args:
            pair_id: The ID of the pair to delete.
            
        Returns:
            True if the pair was deleted, False otherwise.
        """
        if not self.enabled:
            logger.debug("Transfer learning system is disabled")
            return False
        
        if pair_id not in self.transfer_pairs:
            logger.warning(f"Transfer pair {pair_id} not found")
            return False
        
        # Remove the pair from the dictionary
        del self.transfer_pairs[pair_id]
        
        # Delete the pair file
        pair_path = self.data_dir / f"{pair_id}.json"
        if pair_path.exists():
            os.remove(pair_path)
        
        logger.info(f"Deleted transfer pair {pair_id}")
        return True
    
    async def get_transfer_result(self, source_model_type: str, target_model_type: str) -> Optional[Dict[str, Any]]:
        """Get a transfer learning result.
        
        Args:
            source_model_type: The source model type.
            target_model_type: The target model type.
            
        Returns:
            The result, or None if it was not found.
        """
        if not self.enabled:
            logger.debug("Transfer learning system is disabled")
            return None
        
        result_key = f"{source_model_type}_{target_model_type}"
        return self.transfer_results.get(result_key)
    
    async def cleanup(self) -> None:
        """Clean up resources used by the transfer learning system."""
        if not self.enabled:
            logger.debug("Transfer learning system is disabled")
            return
        
        logger.info("Cleaning up transfer learning system")
        
        # Stop the learning loop
        self.is_learning = False
        
        # Cancel all learning tasks
        for task in self.learning_tasks:
            task.cancel()
        
        # Wait for all learning tasks to complete
        if self.learning_tasks:
            await asyncio.gather(*self.learning_tasks, return_exceptions=True)
        
        self.learning_tasks = []
        
        logger.info("Transfer learning system cleaned up")
    
    async def _load_transfer_pairs(self) -> None:
        """Load transfer pairs from disk."""
        if not self.data_dir.exists():
            logger.warning(f"Transfer learning data directory {self.data_dir} does not exist")
            return
        
        # Clear existing pairs
        self.transfer_pairs = {}
        
        # Load pairs from disk
        pair_files = list(self.data_dir.glob("pair_*.json"))
        
        for pair_file in pair_files:
            try:
                with open(pair_file, 'r') as f:
                    pair = json.load(f)
                
                pair_id = pair['id']
                
                # Add the pair to the dictionary
                self.transfer_pairs[pair_id] = pair
            except Exception as e:
                logger.exception(f"Error loading transfer pair from {pair_file}: {e}")
        
        logger.info(f"Loaded {len(self.transfer_pairs)} transfer pairs")
    
    async def _save_transfer_pair(self, pair: Dict[str, Any]) -> None:
        """Save a transfer pair to disk.
        
        Args:
            pair: The pair to save.
        """
        pair_id = pair['id']
        pair_path = self.data_dir / f"{pair_id}.json"
        
        try:
            with open(pair_path, 'w') as f:
                json.dump(pair, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving transfer pair {pair_id}: {e}")
    
    async def _load_transfer_results(self) -> None:
        """Load transfer results from disk."""
        if not self.data_dir.exists():
            logger.warning(f"Transfer learning data directory {self.data_dir} does not exist")
            return
        
        # Clear existing results
        self.transfer_results = {}
        
        # Load results from disk
        result_files = list(self.data_dir.glob("result_*.json"))
        
        for result_file in result_files:
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                
                source_model_type = result['source_model_type']
                target_model_type = result['target_model_type']
                result_key = f"{source_model_type}_{target_model_type}"
                
                # Add the result to the dictionary
                self.transfer_results[result_key] = result
            except Exception as e:
                logger.exception(f"Error loading transfer result from {result_file}: {e}")
        
        logger.info(f"Loaded {len(self.transfer_results)} transfer results")
    
    async def _save_transfer_result(self, result: Dict[str, Any]) -> None:
        """Save a transfer result to disk.
        
        Args:
            result: The result to save.
        """
        source_model_type = result['source_model_type']
        target_model_type = result['target_model_type']
        result_path = self.data_dir / f"result_{source_model_type}_{target_model_type}.json"
        
        try:
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving transfer result: {e}")
    
    async def _learning_loop(self) -> None:
        """Main transfer learning loop."""
        while self.is_learning:
            try:
                # Check if there are enough pairs to learn from
                if len(self.transfer_pairs) < self.batch_size:
                    # Not enough pairs, wait and try again
                    await asyncio.sleep(60)  # Wait for 1 minute
                    continue
                
                # Get pairs that haven't been used for learning yet
                unused_pairs = [
                    pair for pair in self.transfer_pairs.values()
                    if not pair['used_for_learning']
                ]
                
                if len(unused_pairs) < self.batch_size:
                    # Not enough unused pairs, wait and try again
                    await asyncio.sleep(60)  # Wait for 1 minute
                    continue
                
                # Group pairs by source and target model types
                pairs_by_models = {}
                for pair in unused_pairs:
                    source_model_type = pair['source_model_type']
                    target_model_type = pair['target_model_type']
                    key = f"{source_model_type}_{target_model_type}"
                    
                    if key not in pairs_by_models:
                        pairs_by_models[key] = []
                    
                    pairs_by_models[key].append(pair)
                
                # Learn from pairs for each model type combination
                for key, pairs in pairs_by_models.items():
                    if len(pairs) < self.batch_size:
                        continue
                    
                    # Select a batch of pairs
                    batch = pairs[:self.batch_size]
                    
                    # Learn from the batch
                    await self._learn_from_batch(batch)
                    
                    # Mark the pairs as used for learning
                    for pair in batch:
                        pair['used_for_learning'] = True
                        await self._save_transfer_pair(pair)
                
                # Wait before processing the next batch
                await asyncio.sleep(10)  # Wait for 10 seconds
            except asyncio.CancelledError:
                logger.info("Transfer learning loop cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in transfer learning loop: {e}")
                await asyncio.sleep(60)  # Wait for 1 minute before trying again
    
    async def _learn_from_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Learn from a batch of transfer pairs.
        
        Args:
            batch: The batch of pairs to learn from.
        """
        # This is a placeholder for the actual transfer learning implementation
        # In a real implementation, this would use a transfer learning algorithm
        # to transfer knowledge from the source model to the target model
        
        if not batch:
            return
        
        source_model_type = batch[0]['source_model_type']
        target_model_type = batch[0]['target_model_type']
        
        logger.info(f"Learning from batch of {len(batch)} pairs from {source_model_type} to {target_model_type}")
        
        # Get the examples for each pair
        source_examples = []
        target_examples = []
        
        for pair in batch:
            source_example_id = pair['source_example_id']
            target_example_id = pair['target_example_id']
            
            source_example = await learning_system.get_learning_example(source_example_id)
            target_example = await learning_system.get_learning_example(target_example_id)
            
            if source_example and target_example:
                source_examples.append(source_example)
                target_examples.append(target_example)
        
        if not source_examples or not target_examples:
            logger.warning("No valid examples found for transfer learning")
            return
        
        # Create a transfer learning result
        result = {
            'source_model_type': source_model_type,
            'target_model_type': target_model_type,
            'num_pairs': len(source_examples),
            'loss': 0.0,  # Placeholder for the actual loss
            'accuracy': 0.0,  # Placeholder for the actual accuracy
            'created_at': time.time(),
        }
        
        # Add the result to the dictionary
        result_key = f"{source_model_type}_{target_model_type}"
        self.transfer_results[result_key] = result
        
        # Save the result to disk
        await self._save_transfer_result(result)
        
        logger.info(f"Finished learning from batch of {len(batch)} pairs from {source_model_type} to {target_model_type}")


# Create a singleton instance
transfer_learning = TransferLearning()
