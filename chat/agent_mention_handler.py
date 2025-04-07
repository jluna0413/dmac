"""
Agent Mention Handler for DMac.

This module handles the "@" command to call specific agents in the chat interface.
"""

import re
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from utils.secure_logging import get_logger
from config.config import config
from agents.agent_factory import agent_factory
from agents.personalities import get_agent_personality
from task_system.task_manager import TaskManager

logger = get_logger('dmac.chat.agent_mention_handler')

class AgentMentionHandler:
    """Handler for agent mentions in chat messages."""
    
    def __init__(self):
        """Initialize the agent mention handler."""
        self.task_manager = TaskManager()
        self.mention_pattern = r'@(\w+)'
        
        # Map of aliases to agent IDs
        self.agent_aliases = {
            # Agent IDs
            'codey': 'codey',
            'perry': 'perry',
            'shelly': 'shelly',
            'flora': 'flora',
            
            # Job titles
            'coder': 'codey',
            'developer': 'codey',
            'programmer': 'codey',
            'promptengineer': 'perry',
            'prompter': 'perry',
            'shell': 'shelly',
            'commandline': 'shelly',
            'terminal': 'shelly',
            'frontend': 'flora',
            'ui': 'flora',
            'ux': 'flora',
            
            # Specialties
            'code': 'codey',
            'coding': 'codey',
            'programming': 'codey',
            'prompt': 'perry',
            'prompting': 'perry',
            'command': 'shelly',
            'bash': 'shelly',
            'powershell': 'shelly',
            'design': 'flora',
            'css': 'flora',
            'html': 'flora'
        }
    
    async def process_message(self, message: str, user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Process a message for agent mentions.
        
        Args:
            message: The message to process
            user_id: The ID of the user who sent the message
            
        Returns:
            Tuple of (processed message, list of agent responses)
        """
        # Find all mentions in the message
        mentions = re.findall(self.mention_pattern, message)
        
        if not mentions:
            return message, []
        
        # Process each mention
        agent_responses = []
        for mention in mentions:
            # Normalize the mention (lowercase, remove spaces)
            normalized_mention = mention.lower().replace(' ', '')
            
            # Get the agent ID from the mention
            agent_id = self.agent_aliases.get(normalized_mention)
            
            if not agent_id:
                # Try to find a partial match
                for alias, aid in self.agent_aliases.items():
                    if normalized_mention in alias:
                        agent_id = aid
                        break
            
            if agent_id:
                # Get the agent
                agent = await self.task_manager.get_agent(agent_id)
                
                if agent:
                    # Extract the message for the agent (everything after the mention)
                    agent_message = self._extract_agent_message(message, mention)
                    
                    # Create a task for the agent
                    task_type = self._get_task_type_for_agent(agent_id)
                    
                    task = await self.task_manager.create_task(
                        task_type=task_type,
                        description=f"Message from user {user_id}: {agent_message}",
                        data={'message': agent_message, 'user_id': user_id},
                        priority=3,  # Medium priority
                        agent_id=agent_id
                    )
                    
                    # Add the agent response
                    personality = get_agent_personality(agent_id)
                    agent_responses.append({
                        'agent_id': agent_id,
                        'name': personality.get('name', agent_id),
                        'role': personality.get('role', f"{agent_id} agent"),
                        'avatar': personality.get('avatar', f"{agent_id}_avatar.png"),
                        'color': personality.get('color', '#2196F3'),
                        'task_id': task['task_id'],
                        'message': f"I'm processing your request: '{agent_message}'. I'll get back to you shortly."
                    })
        
        return message, agent_responses
    
    def _extract_agent_message(self, message: str, mention: str) -> str:
        """Extract the message for an agent from the full message.
        
        Args:
            message: The full message
            mention: The mention text
            
        Returns:
            The message for the agent
        """
        # Find the mention in the message
        mention_pattern = f"@{mention}"
        mention_index = message.find(mention_pattern)
        
        if mention_index == -1:
            return message
        
        # Extract everything after the mention
        start_index = mention_index + len(mention_pattern)
        
        # Find the next mention, if any
        next_mention_index = message.find('@', start_index)
        
        if next_mention_index == -1:
            # No next mention, extract until the end
            agent_message = message[start_index:].strip()
        else:
            # Extract until the next mention
            agent_message = message[start_index:next_mention_index].strip()
        
        return agent_message
    
    def _get_task_type_for_agent(self, agent_id: str) -> str:
        """Get the appropriate task type for an agent.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            The task type
        """
        task_types = {
            'codey': 'code_generation',
            'perry': 'prompt_creation',
            'shelly': 'command_generation',
            'flora': 'component_creation'
        }
        
        return task_types.get(agent_id, 'general_task')

# Create a singleton instance
agent_mention_handler = AgentMentionHandler()
