"""
Learning Manager for DMac.

This module provides the learning manager for coordinating learning components.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any

from config.config import config
from utils.secure_logging import get_logger
from learning.learning_system import learning_system, ModelType
from learning.reinforcement_learning import reinforcement_learning
from learning.transfer_learning import transfer_learning

logger = get_logger('dmac.learning.learning_manager')


class LearningManager:
    """Manager for coordinating learning components."""
    
    def __init__(self):
        """Initialize the learning manager."""
        # Load configuration
        self.enabled = config.get('learning.enabled', True)
        
        # Initialize learning components
        self.learning_system = learning_system
        self.reinforcement_learning = reinforcement_learning
        self.transfer_learning = transfer_learning
        
        logger.info("Learning manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the learning manager.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            logger.info("Learning manager is disabled")
            return True
        
        try:
            # Initialize the learning system
            if not await self.learning_system.initialize():
                logger.error("Failed to initialize learning system")
                return False
            
            # Initialize the reinforcement learning system
            if not await self.reinforcement_learning.initialize():
                logger.warning("Failed to initialize reinforcement learning system")
                # Continue anyway, as this is not critical
            
            # Initialize the transfer learning system
            if not await self.transfer_learning.initialize():
                logger.warning("Failed to initialize transfer learning system")
                # Continue anyway, as this is not critical
            
            logger.info("Learning manager initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing learning manager: {e}")
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
            logger.debug("Learning manager is disabled, not adding example")
            return ""
        
        return await self.learning_system.add_learning_example(
            prompt=prompt,
            response=response,
            model_type=model_type,
            system_prompt=system_prompt,
            metadata=metadata
        )
    
    async def add_reinforcement_episode(self, states: List[Dict[str, Any]], actions: List[Dict[str, Any]], 
                                       rewards: List[float], model_type: ModelType) -> str:
        """Add an episode for reinforcement learning.
        
        Args:
            states: The states in the episode.
            actions: The actions taken in the episode.
            rewards: The rewards received in the episode.
            model_type: The type of model that generated the actions.
            
        Returns:
            The ID of the new episode.
        """
        if not self.enabled:
            logger.debug("Learning manager is disabled, not adding episode")
            return ""
        
        return await self.reinforcement_learning.add_episode(
            states=states,
            actions=actions,
            rewards=rewards,
            model_type=model_type
        )
    
    async def add_transfer_pair(self, source_example_id: str, target_example_id: str) -> str:
        """Add a transfer learning pair.
        
        Args:
            source_example_id: The ID of the source example.
            target_example_id: The ID of the target example.
            
        Returns:
            The ID of the new transfer pair.
        """
        if not self.enabled:
            logger.debug("Learning manager is disabled, not adding transfer pair")
            return ""
        
        return await self.transfer_learning.add_transfer_pair(
            source_example_id=source_example_id,
            target_example_id=target_example_id
        )
    
    async def get_action(self, state: Dict[str, Any], model_type: ModelType) -> Dict[str, Any]:
        """Get an action for a state using the learned policy.
        
        Args:
            state: The current state.
            model_type: The type of model to use.
            
        Returns:
            The action to take.
        """
        if not self.enabled:
            logger.debug("Learning manager is disabled")
            return {}
        
        return await self.reinforcement_learning.get_action(
            state=state,
            model_type=model_type
        )
    
    async def update_policy(self, state: Dict[str, Any], action: Dict[str, Any], 
                           reward: float, model_type: ModelType) -> None:
        """Update the policy based on a state-action-reward tuple.
        
        Args:
            state: The state.
            action: The action taken.
            reward: The reward received.
            model_type: The type of model.
        """
        if not self.enabled:
            logger.debug("Learning manager is disabled")
            return
        
        await self.reinforcement_learning.update_policy(
            state=state,
            action=action,
            reward=reward,
            model_type=model_type
        )
    
    async def get_transfer_result(self, source_model_type: str, target_model_type: str) -> Optional[Dict[str, Any]]:
        """Get a transfer learning result.
        
        Args:
            source_model_type: The source model type.
            target_model_type: The target model type.
            
        Returns:
            The result, or None if it was not found.
        """
        if not self.enabled:
            logger.debug("Learning manager is disabled")
            return None
        
        return await self.transfer_learning.get_transfer_result(
            source_model_type=source_model_type,
            target_model_type=target_model_type
        )
    
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
            logger.debug("Learning manager is disabled")
            return []
        
        return await self.learning_system.get_learning_examples(
            model_type=model_type,
            limit=limit,
            offset=offset
        )
    
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
            logger.debug("Learning manager is disabled")
            return []
        
        return await self.transfer_learning.get_transfer_pairs(
            source_model_type=source_model_type,
            target_model_type=target_model_type,
            limit=limit,
            offset=offset
        )
    
    async def cleanup(self) -> None:
        """Clean up resources used by the learning manager."""
        if not self.enabled:
            logger.debug("Learning manager is disabled")
            return
        
        logger.info("Cleaning up learning manager")
        
        # Clean up the learning system
        await self.learning_system.cleanup()
        
        # Clean up the reinforcement learning system
        await self.reinforcement_learning.cleanup()
        
        # Clean up the transfer learning system
        await self.transfer_learning.cleanup()
        
        logger.info("Learning manager cleaned up")


# Create a singleton instance
learning_manager = LearningManager()
