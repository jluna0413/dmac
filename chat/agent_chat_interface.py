"""
Agent Chat Interface for DMac.

This module provides a direct chat interface for interacting with agents.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from utils.secure_logging import get_logger
from config.config import config
from agents.agent_factory import agent_factory
from agents.personalities import get_agent_personality
from models.model_provider import model_provider_factory
from task_system.task_manager import TaskManager

logger = get_logger('dmac.chat.agent_chat_interface')

class AgentChatInterface:
    """Interface for chatting directly with agents."""
    
    def __init__(self):
        """Initialize the agent chat interface."""
        self.task_manager = TaskManager()
        self.chat_history_dir = config.get('chat.history_dir', os.path.join('data', 'chat_history'))
        
        # Create the chat history directory if it doesn't exist
        os.makedirs(self.chat_history_dir, exist_ok=True)
    
    async def send_message(self, 
                          agent_id: str, 
                          message: str, 
                          user_id: str,
                          model_name: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to an agent.
        
        Args:
            agent_id: The agent ID
            message: The message to send
            user_id: The ID of the user sending the message
            model_name: Optional model name to use
            
        Returns:
            The agent's response
        """
        # Get the agent
        agent = await self.task_manager.get_agent(agent_id)
        
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Get the agent's personality
        personality = get_agent_personality(agent_id)
        
        # Determine the task type
        task_type = self._get_task_type_for_agent(agent_id)
        
        # Create a task for the agent
        task = await self.task_manager.create_task(
            task_type=task_type,
            description=f"Direct chat message from user {user_id}: {message}",
            data={
                'message': message,
                'user_id': user_id,
                'model_name': model_name,
                'is_direct_chat': True
            },
            priority=3,  # Medium priority
            agent_id=agent_id
        )
        
        # Save the message to the chat history
        await self._save_message(agent_id, user_id, message, 'user')
        
        # Create the initial response
        response = {
            'agent_id': agent_id,
            'name': personality.get('name', agent_id),
            'role': personality.get('role', f"{agent_id} agent"),
            'avatar': personality.get('avatar', f"{agent_id}_avatar.png"),
            'color': personality.get('color', '#2196F3'),
            'task_id': task['task_id'],
            'message': f"I'm processing your message. I'll respond shortly.",
            'timestamp': time.time()
        }
        
        # In a real implementation, we would wait for the task to complete
        # For now, we'll simulate a response
        
        # Get the model provider
        model_provider = model_provider_factory.create_default_provider(
            model_name=model_name or agent.get('metadata', {}).get('model_name')
        )
        
        # Generate a response
        system_prompt = self._get_system_prompt_for_agent(agent_id, personality)
        user_prompt = f"User: {message}\n\nRespond as {personality.get('name', agent_id)}, {personality.get('role', 'an AI assistant')}."
        
        try:
            agent_message = await model_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            # Update the response
            response['message'] = agent_message
            
            # Save the response to the chat history
            await self._save_message(agent_id, user_id, agent_message, 'agent')
            
            # Update the task with the result
            await self.task_manager.update_task(
                task_id=task['task_id'],
                status='completed',
                result={'message': agent_message}
            )
            
        except Exception as e:
            logger.error(f"Error generating response from agent {agent_id}: {str(e)}")
            
            # Update the response with an error message
            response['message'] = f"I'm sorry, I encountered an error while processing your message: {str(e)}"
            
            # Update the task with the error
            await self.task_manager.update_task(
                task_id=task['task_id'],
                status='failed',
                error=str(e)
            )
        
        return response
    
    async def get_chat_history(self, agent_id: str, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the chat history for an agent and user.
        
        Args:
            agent_id: The agent ID
            user_id: The user ID
            limit: Maximum number of messages to return
            
        Returns:
            List of chat messages
        """
        # Get the chat history file path
        history_file = os.path.join(self.chat_history_dir, f"{agent_id}_{user_id}.json")
        
        # Check if the file exists
        if not os.path.exists(history_file):
            return []
        
        # Load the chat history
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Sort by timestamp (newest first) and limit
            history.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            return history[:limit]
        except Exception as e:
            logger.error(f"Error loading chat history for agent {agent_id} and user {user_id}: {str(e)}")
            return []
    
    async def _save_message(self, agent_id: str, user_id: str, message: str, sender: str) -> None:
        """Save a message to the chat history.
        
        Args:
            agent_id: The agent ID
            user_id: The user ID
            message: The message
            sender: The sender ('user' or 'agent')
        """
        # Get the chat history file path
        history_file = os.path.join(self.chat_history_dir, f"{agent_id}_{user_id}.json")
        
        # Create the message
        chat_message = {
            'agent_id': agent_id,
            'user_id': user_id,
            'message': message,
            'sender': sender,
            'timestamp': time.time()
        }
        
        # Load existing history or create a new one
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading chat history for agent {agent_id} and user {user_id}: {str(e)}")
                history = []
        else:
            history = []
        
        # Add the message to the history
        history.append(chat_message)
        
        # Save the history
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving chat history for agent {agent_id} and user {user_id}: {str(e)}")
    
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
    
    def _get_system_prompt_for_agent(self, agent_id: str, personality: Dict[str, Any]) -> str:
        """Get the system prompt for an agent.
        
        Args:
            agent_id: The agent ID
            personality: The agent's personality
            
        Returns:
            The system prompt
        """
        name = personality.get('name', agent_id)
        role = personality.get('role', f"{agent_id} agent")
        traits = personality.get('personality_traits', [])
        speech_pattern = personality.get('speech_pattern', {})
        
        system_prompt = f"""You are {name}, {role}. 

Personality traits: {', '.join(traits)}

Speech pattern:
- Tone: {speech_pattern.get('tone', 'Professional')}
- Pacing: {speech_pattern.get('pacing', 'Moderate')}
- Vocabulary: {speech_pattern.get('vocabulary', 'Technical')}
- Quirks: {speech_pattern.get('quirks', 'None')}

Respond to the user's message in a way that reflects your personality and expertise.
Be helpful, accurate, and engaging.
"""
        
        # Add agent-specific instructions
        if agent_id == 'codey':
            system_prompt += """
As a code specialist, focus on providing clean, efficient, and well-documented code.
Explain your code clearly and highlight any important considerations or potential issues.
"""
        elif agent_id == 'perry':
            system_prompt += """
As a prompt engineer, focus on crafting effective prompts that elicit the desired responses.
Explain your prompt design choices and suggest improvements or alternatives.
"""
        elif agent_id == 'shelly':
            system_prompt += """
As a shell/command-line specialist, focus on providing accurate and efficient commands.
Explain what each command does and any potential risks or side effects.
Consider platform-specific differences (Windows, macOS, Linux) when relevant.
"""
        elif agent_id == 'flora':
            system_prompt += """
As a frontend developer, focus on creating clean, responsive, and accessible UI components.
Explain your design choices and consider cross-browser compatibility and performance.
"""
        
        return system_prompt

# Create a singleton instance
agent_chat_interface = AgentChatInterface()
