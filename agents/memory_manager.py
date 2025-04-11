"""
Agent Memory Manager for DMac.

This module manages agent memories stored in the database.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from utils.secure_logging import get_logger
from config.config import config

logger = get_logger('dmac.agents.memory_manager')

class MemoryManager:
    """Manager for agent memories."""
    
    def __init__(self):
        """Initialize the memory manager."""
        self.memories_dir = config.get('agents.memories_dir', os.path.join('data', 'agent_memories'))
        self.max_memories = config.get('agents.max_memories', 1000)
        
        # Create the memories directory if it doesn't exist
        os.makedirs(self.memories_dir, exist_ok=True)
    
    async def add_memory(self, 
                        agent_id: str, 
                        memory: str, 
                        context: Optional[Dict[str, Any]] = None,
                        importance: int = 1) -> Dict[str, Any]:
        """Add a memory for an agent.
        
        Args:
            agent_id: The agent ID
            memory: The memory text
            context: Optional context for the memory
            importance: Importance of the memory (1-5, with 5 being highest)
            
        Returns:
            The created memory
        """
        # Create the memory
        memory_obj = {
            'agent_id': agent_id,
            'memory': memory,
            'context': context or {},
            'importance': importance,
            'created_at': time.time(),
            'last_accessed': time.time(),
            'access_count': 0
        }
        
        # Save the memory
        await self._save_memory(agent_id, memory_obj)
        
        # Clean up old memories if needed
        await self._cleanup_memories(agent_id)
        
        return memory_obj
    
    async def get_memories(self, 
                          agent_id: str, 
                          query: Optional[str] = None,
                          limit: int = 10,
                          min_importance: int = 1) -> List[Dict[str, Any]]:
        """Get memories for an agent.
        
        Args:
            agent_id: The agent ID
            query: Optional query to search for
            limit: Maximum number of memories to return
            min_importance: Minimum importance level
            
        Returns:
            List of memories
        """
        # Get the agent's memories directory
        agent_dir = os.path.join(self.memories_dir, agent_id)
        
        if not os.path.exists(agent_dir):
            return []
        
        # Load all memories
        memories = []
        for filename in os.listdir(agent_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(agent_dir, filename), 'r') as f:
                        memory = json.load(f)
                    
                    # Filter by importance
                    if memory.get('importance', 1) >= min_importance:
                        memories.append(memory)
                except Exception as e:
                    logger.error(f"Error loading memory {filename} for agent {agent_id}: {str(e)}")
        
        # Filter by query if provided
        if query:
            filtered_memories = []
            for memory in memories:
                if query.lower() in memory.get('memory', '').lower():
                    filtered_memories.append(memory)
                    
                    # Update access count and last accessed time
                    memory['access_count'] = memory.get('access_count', 0) + 1
                    memory['last_accessed'] = time.time()
                    
                    # Save the updated memory
                    await self._save_memory(agent_id, memory)
            
            memories = filtered_memories
        
        # Sort by importance (highest first) and last accessed (most recent first)
        memories.sort(key=lambda x: (x.get('importance', 1), x.get('last_accessed', 0)), reverse=True)
        
        # Limit the number of memories
        return memories[:limit]
    
    async def update_memory(self, 
                           agent_id: str, 
                           memory_id: str,
                           memory: Optional[str] = None,
                           context: Optional[Dict[str, Any]] = None,
                           importance: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Update a memory for an agent.
        
        Args:
            agent_id: The agent ID
            memory_id: The memory ID (filename without extension)
            memory: Optional new memory text
            context: Optional new context
            importance: Optional new importance
            
        Returns:
            The updated memory or None if not found
        """
        # Get the memory file path
        memory_file = os.path.join(self.memories_dir, agent_id, f"{memory_id}.json")
        
        # Check if the memory exists
        if not os.path.exists(memory_file):
            return None
        
        # Load the memory
        try:
            with open(memory_file, 'r') as f:
                memory_obj = json.load(f)
        except Exception as e:
            logger.error(f"Error loading memory {memory_id} for agent {agent_id}: {str(e)}")
            return None
        
        # Update the memory
        if memory is not None:
            memory_obj['memory'] = memory
        
        if context is not None:
            memory_obj['context'] = context
        
        if importance is not None:
            memory_obj['importance'] = importance
        
        memory_obj['last_accessed'] = time.time()
        
        # Save the updated memory
        await self._save_memory(agent_id, memory_obj)
        
        return memory_obj
    
    async def delete_memory(self, agent_id: str, memory_id: str) -> bool:
        """Delete a memory for an agent.
        
        Args:
            agent_id: The agent ID
            memory_id: The memory ID (filename without extension)
            
        Returns:
            True if the memory was deleted, False otherwise
        """
        # Get the memory file path
        memory_file = os.path.join(self.memories_dir, agent_id, f"{memory_id}.json")
        
        # Check if the memory exists
        if not os.path.exists(memory_file):
            return False
        
        # Delete the memory
        try:
            os.remove(memory_file)
            return True
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id} for agent {agent_id}: {str(e)}")
            return False
    
    async def _save_memory(self, agent_id: str, memory: Dict[str, Any]) -> None:
        """Save a memory to disk.
        
        Args:
            agent_id: The agent ID
            memory: The memory to save
        """
        # Get the agent's memories directory
        agent_dir = os.path.join(self.memories_dir, agent_id)
        
        # Create the directory if it doesn't exist
        os.makedirs(agent_dir, exist_ok=True)
        
        # Generate a filename based on the creation time and memory text
        memory_id = f"memory_{int(memory.get('created_at', time.time()))}_{hash(memory.get('memory', ''))}"
        
        # Save the memory
        memory_file = os.path.join(agent_dir, f"{memory_id}.json")
        
        try:
            with open(memory_file, 'w') as f:
                json.dump(memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory for agent {agent_id}: {str(e)}")
    
    async def _cleanup_memories(self, agent_id: str) -> None:
        """Clean up old memories for an agent.
        
        Args:
            agent_id: The agent ID
        """
        # Get the agent's memories directory
        agent_dir = os.path.join(self.memories_dir, agent_id)
        
        if not os.path.exists(agent_dir):
            return
        
        # Get all memory files
        memory_files = [
            os.path.join(agent_dir, f) 
            for f in os.listdir(agent_dir) 
            if f.endswith('.json')
        ]
        
        # Check if we need to clean up
        if len(memory_files) <= self.max_memories:
            return
        
        # Load all memories
        memories = []
        for memory_file in memory_files:
            try:
                with open(memory_file, 'r') as f:
                    memory = json.load(f)
                
                # Add the file path to the memory
                memory['file_path'] = memory_file
                memories.append(memory)
            except Exception as e:
                logger.error(f"Error loading memory {memory_file} for agent {agent_id}: {str(e)}")
        
        # Sort by importance (lowest first) and last accessed (oldest first)
        memories.sort(key=lambda x: (x.get('importance', 1), x.get('last_accessed', 0)))
        
        # Delete the oldest, least important memories
        num_to_delete = len(memories) - self.max_memories
        
        for i in range(num_to_delete):
            try:
                os.remove(memories[i]['file_path'])
            except Exception as e:
                logger.error(f"Error deleting memory {memories[i]['file_path']} for agent {agent_id}: {str(e)}")

# Create a singleton instance
memory_manager = MemoryManager()
