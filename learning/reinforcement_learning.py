"""
Reinforcement Learning for DMac.

This module provides reinforcement learning capabilities for the learning system.
"""

import asyncio
import json
import logging
import os
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from config.config import config
from utils.secure_logging import get_logger
from learning.learning_system import learning_system, ModelType

logger = get_logger('dmac.learning.reinforcement_learning')


class ReinforcementLearning:
    """Reinforcement learning for the learning system."""
    
    def __init__(self):
        """Initialize the reinforcement learning system."""
        # Load configuration
        self.enabled = config.get('learning.reinforcement.enabled', True)
        self.data_dir = Path(config.get('learning.reinforcement.data_dir', 'data/reinforcement'))
        self.model_name = config.get('learning.reinforcement.model_name', 'deepseek-rl:latest')
        self.learning_rate = config.get('learning.reinforcement.learning_rate', 0.001)
        self.discount_factor = config.get('learning.reinforcement.discount_factor', 0.99)
        self.exploration_rate = config.get('learning.reinforcement.exploration_rate', 0.1)
        self.batch_size = config.get('learning.reinforcement.batch_size', 32)
        
        # Create the data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize reinforcement learning data
        self.episodes = {}
        self.rewards = {}
        self.policies = {}
        
        # Initialize learning tasks
        self.learning_tasks = []
        self.is_learning = False
        
        logger.info("Reinforcement learning system initialized")
    
    async def initialize(self) -> bool:
        """Initialize the reinforcement learning system.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            logger.info("Reinforcement learning system is disabled")
            return True
        
        try:
            # Load existing episodes and policies
            await self._load_episodes()
            await self._load_policies()
            
            # Start the learning loop
            self.is_learning = True
            learning_task = asyncio.create_task(self._learning_loop())
            self.learning_tasks.append(learning_task)
            
            logger.info("Reinforcement learning system initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing reinforcement learning system: {e}")
            return False
    
    async def add_episode(self, states: List[Dict[str, Any]], actions: List[Dict[str, Any]], 
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
            logger.debug("Reinforcement learning system is disabled, not adding episode")
            return ""
        
        if len(states) != len(actions) + 1 or len(actions) != len(rewards):
            logger.warning("Invalid episode: states, actions, and rewards have inconsistent lengths")
            return ""
        
        # Create a new episode
        episode_id = f"episode_{int(time.time())}_{len(self.episodes)}"
        
        episode = {
            'id': episode_id,
            'states': states,
            'actions': actions,
            'rewards': rewards,
            'model_type': model_type.value,
            'created_at': time.time(),
            'used_for_learning': False,
        }
        
        # Add the episode to the dictionary
        self.episodes[episode_id] = episode
        
        # Save the episode to disk
        await self._save_episode(episode)
        
        logger.debug(f"Added episode {episode_id} from {model_type.value} model")
        return episode_id
    
    async def get_action(self, state: Dict[str, Any], model_type: ModelType) -> Dict[str, Any]:
        """Get an action for a state using the learned policy.
        
        Args:
            state: The current state.
            model_type: The type of model to use.
            
        Returns:
            The action to take.
        """
        if not self.enabled:
            logger.debug("Reinforcement learning system is disabled")
            return {}
        
        # Get the policy for the model type
        policy = self.policies.get(model_type.value, {})
        
        # Convert the state to a string for lookup
        state_str = json.dumps(state, sort_keys=True)
        
        # Check if we have a policy for this state
        if state_str in policy:
            # Get the action from the policy
            action = policy[state_str]
            
            # Exploration: sometimes choose a random action
            if random.random() < self.exploration_rate:
                # This is a placeholder for generating a random action
                # In a real implementation, this would generate a valid random action
                action = {'type': 'random', 'value': random.random()}
        else:
            # No policy for this state, use a default action
            # This is a placeholder for generating a default action
            # In a real implementation, this would generate a valid default action
            action = {'type': 'default', 'value': 0.5}
        
        return action
    
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
            logger.debug("Reinforcement learning system is disabled")
            return
        
        # Get the policy for the model type
        if model_type.value not in self.policies:
            self.policies[model_type.value] = {}
        
        policy = self.policies[model_type.value]
        
        # Convert the state to a string for lookup
        state_str = json.dumps(state, sort_keys=True)
        
        # Update the policy for this state
        policy[state_str] = action
        
        # Save the policy to disk
        await self._save_policy(model_type.value)
        
        logger.debug(f"Updated policy for {model_type.value} model")
    
    async def cleanup(self) -> None:
        """Clean up resources used by the reinforcement learning system."""
        if not self.enabled:
            logger.debug("Reinforcement learning system is disabled")
            return
        
        logger.info("Cleaning up reinforcement learning system")
        
        # Stop the learning loop
        self.is_learning = False
        
        # Cancel all learning tasks
        for task in self.learning_tasks:
            task.cancel()
        
        # Wait for all learning tasks to complete
        if self.learning_tasks:
            await asyncio.gather(*self.learning_tasks, return_exceptions=True)
        
        self.learning_tasks = []
        
        logger.info("Reinforcement learning system cleaned up")
    
    async def _load_episodes(self) -> None:
        """Load episodes from disk."""
        if not self.data_dir.exists():
            logger.warning(f"Reinforcement learning data directory {self.data_dir} does not exist")
            return
        
        # Clear existing episodes
        self.episodes = {}
        
        # Load episodes from disk
        episode_files = list(self.data_dir.glob("episode_*.json"))
        
        for episode_file in episode_files:
            try:
                with open(episode_file, 'r') as f:
                    episode = json.load(f)
                
                episode_id = episode['id']
                
                # Add the episode to the dictionary
                self.episodes[episode_id] = episode
            except Exception as e:
                logger.exception(f"Error loading episode from {episode_file}: {e}")
        
        logger.info(f"Loaded {len(self.episodes)} episodes")
    
    async def _save_episode(self, episode: Dict[str, Any]) -> None:
        """Save an episode to disk.
        
        Args:
            episode: The episode to save.
        """
        episode_id = episode['id']
        episode_path = self.data_dir / f"{episode_id}.json"
        
        try:
            with open(episode_path, 'w') as f:
                json.dump(episode, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving episode {episode_id}: {e}")
    
    async def _load_policies(self) -> None:
        """Load policies from disk."""
        if not self.data_dir.exists():
            logger.warning(f"Reinforcement learning data directory {self.data_dir} does not exist")
            return
        
        # Clear existing policies
        self.policies = {}
        
        # Load policies from disk
        policy_files = list(self.data_dir.glob("policy_*.json"))
        
        for policy_file in policy_files:
            try:
                with open(policy_file, 'r') as f:
                    policy_data = json.load(f)
                
                model_type = policy_data['model_type']
                policy = policy_data['policy']
                
                # Add the policy to the dictionary
                self.policies[model_type] = policy
            except Exception as e:
                logger.exception(f"Error loading policy from {policy_file}: {e}")
        
        logger.info(f"Loaded policies for {len(self.policies)} model types")
    
    async def _save_policy(self, model_type: str) -> None:
        """Save a policy to disk.
        
        Args:
            model_type: The model type of the policy to save.
        """
        if model_type not in self.policies:
            logger.warning(f"No policy found for model type {model_type}")
            return
        
        policy = self.policies[model_type]
        policy_path = self.data_dir / f"policy_{model_type}.json"
        
        try:
            policy_data = {
                'model_type': model_type,
                'policy': policy,
                'updated_at': time.time(),
            }
            
            with open(policy_path, 'w') as f:
                json.dump(policy_data, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving policy for model type {model_type}: {e}")
    
    async def _learning_loop(self) -> None:
        """Main reinforcement learning loop."""
        while self.is_learning:
            try:
                # Check if there are enough episodes to learn from
                if len(self.episodes) < self.batch_size:
                    # Not enough episodes, wait and try again
                    await asyncio.sleep(60)  # Wait for 1 minute
                    continue
                
                # Get episodes that haven't been used for learning yet
                unused_episodes = [
                    episode for episode in self.episodes.values()
                    if not episode['used_for_learning']
                ]
                
                if len(unused_episodes) < self.batch_size:
                    # Not enough unused episodes, wait and try again
                    await asyncio.sleep(60)  # Wait for 1 minute
                    continue
                
                # Select a batch of episodes
                batch = unused_episodes[:self.batch_size]
                
                # Learn from the batch
                await self._learn_from_batch(batch)
                
                # Mark the episodes as used for learning
                for episode in batch:
                    episode['used_for_learning'] = True
                    await self._save_episode(episode)
                
                # Wait before processing the next batch
                await asyncio.sleep(10)  # Wait for 10 seconds
            except asyncio.CancelledError:
                logger.info("Reinforcement learning loop cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in reinforcement learning loop: {e}")
                await asyncio.sleep(60)  # Wait for 1 minute before trying again
    
    async def _learn_from_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Learn from a batch of episodes.
        
        Args:
            batch: The batch of episodes to learn from.
        """
        # This is a placeholder for the actual reinforcement learning implementation
        # In a real implementation, this would use a reinforcement learning algorithm
        # such as Q-learning or policy gradients to learn from the episodes
        
        logger.info(f"Learning from batch of {len(batch)} episodes")
        
        # Group episodes by model type
        episodes_by_model = {}
        for episode in batch:
            model_type = episode['model_type']
            if model_type not in episodes_by_model:
                episodes_by_model[model_type] = []
            episodes_by_model[model_type].append(episode)
        
        # Learn from episodes for each model type
        for model_type, episodes in episodes_by_model.items():
            # Get the policy for this model type
            if model_type not in self.policies:
                self.policies[model_type] = {}
            
            policy = self.policies[model_type]
            
            # Update the policy based on the episodes
            for episode in episodes:
                states = episode['states']
                actions = episode['actions']
                rewards = episode['rewards']
                
                # Calculate discounted rewards
                discounted_rewards = []
                cumulative_reward = 0
                for reward in reversed(rewards):
                    cumulative_reward = reward + self.discount_factor * cumulative_reward
                    discounted_rewards.insert(0, cumulative_reward)
                
                # Update the policy for each state-action pair
                for i in range(len(actions)):
                    state = states[i]
                    action = actions[i]
                    discounted_reward = discounted_rewards[i]
                    
                    # Convert the state to a string for lookup
                    state_str = json.dumps(state, sort_keys=True)
                    
                    # Update the policy for this state
                    policy[state_str] = action
            
            # Save the updated policy
            await self._save_policy(model_type)
        
        logger.info(f"Finished learning from batch of {len(batch)} episodes")


# Create a singleton instance
reinforcement_learning = ReinforcementLearning()
