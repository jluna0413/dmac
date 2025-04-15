"""
SwarmUI Client

This module provides a client for interacting with SwarmUI for agent visualization.
"""

import logging
import json
import os
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logger = logging.getLogger('dmac.integrations.swarmui')

class SwarmUIClient:
    """Client for interacting with SwarmUI."""
    
    def __init__(self, base_url: str = "http://localhost:3030"):
        """
        Initialize the SwarmUI client.
        
        Args:
            base_url: Base URL for the SwarmUI server
        """
        self.base_url = base_url
        self.session = None
        self.connected = False
        
        logger.info(f"SwarmUI client initialized with base URL: {base_url}")
    
    async def connect(self) -> bool:
        """
        Connect to the SwarmUI server.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.session = aiohttp.ClientSession()
            
            # Check if the server is available
            async with self.session.get(f"{self.base_url}/api/status") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'ok':
                        self.connected = True
                        logger.info("Connected to SwarmUI server")
                        return True
            
            logger.warning("Failed to connect to SwarmUI server")
            return False
        
        except Exception as e:
            logger.error(f"Error connecting to SwarmUI server: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the SwarmUI server."""
        if self.session:
            await self.session.close()
            self.session = None
            self.connected = False
            logger.info("Disconnected from SwarmUI server")
    
    async def create_agent_node(self, agent_id: str, agent_name: str, agent_type: str, position: Optional[Dict[str, float]] = None) -> Optional[str]:
        """
        Create a node for an agent in the SwarmUI visualization.
        
        Args:
            agent_id: ID of the agent
            agent_name: Name of the agent
            agent_type: Type of the agent
            position: Position of the node (optional)
            
        Returns:
            Node ID if successful, None otherwise
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to SwarmUI server")
            return None
        
        try:
            # Prepare the node data
            node_data = {
                'id': agent_id,
                'label': agent_name,
                'type': agent_type,
                'data': {
                    'agent_id': agent_id,
                    'agent_type': agent_type
                }
            }
            
            if position:
                node_data['position'] = position
            
            # Create the node
            async with self.session.post(f"{self.base_url}/api/nodes", json=node_data) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    node_id = data.get('id')
                    logger.info(f"Created node for agent {agent_id} with node ID {node_id}")
                    return node_id
                else:
                    logger.warning(f"Failed to create node for agent {agent_id}: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error creating node for agent {agent_id}: {str(e)}")
            return None
    
    async def create_edge(self, source_id: str, target_id: str, edge_type: str = "default") -> Optional[str]:
        """
        Create an edge between two nodes in the SwarmUI visualization.
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            edge_type: Type of the edge
            
        Returns:
            Edge ID if successful, None otherwise
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to SwarmUI server")
            return None
        
        try:
            # Prepare the edge data
            edge_data = {
                'source': source_id,
                'target': target_id,
                'type': edge_type
            }
            
            # Create the edge
            async with self.session.post(f"{self.base_url}/api/edges", json=edge_data) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    edge_id = data.get('id')
                    logger.info(f"Created edge from {source_id} to {target_id} with edge ID {edge_id}")
                    return edge_id
                else:
                    logger.warning(f"Failed to create edge from {source_id} to {target_id}: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error creating edge from {source_id} to {target_id}: {str(e)}")
            return None
    
    async def update_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Update the status of an agent in the SwarmUI visualization.
        
        Args:
            agent_id: ID of the agent
            status: New status of the agent
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to SwarmUI server")
            return False
        
        try:
            # Prepare the update data
            update_data = {
                'data': {
                    'status': status
                }
            }
            
            # Update the node
            async with self.session.patch(f"{self.base_url}/api/nodes/{agent_id}", json=update_data) as response:
                if response.status == 200:
                    logger.info(f"Updated status of agent {agent_id} to {status}")
                    return True
                else:
                    logger.warning(f"Failed to update status of agent {agent_id}: {response.status}")
                    return False
        
        except Exception as e:
            logger.error(f"Error updating status of agent {agent_id}: {str(e)}")
            return False
    
    async def log_agent_activity(self, agent_id: str, activity: str) -> bool:
        """
        Log an activity for an agent in the SwarmUI visualization.
        
        Args:
            agent_id: ID of the agent
            activity: Activity to log
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to SwarmUI server")
            return False
        
        try:
            # Prepare the activity data
            activity_data = {
                'agent_id': agent_id,
                'activity': activity,
                'timestamp': int(asyncio.get_event_loop().time() * 1000)
            }
            
            # Log the activity
            async with self.session.post(f"{self.base_url}/api/activities", json=activity_data) as response:
                if response.status == 200 or response.status == 201:
                    logger.info(f"Logged activity for agent {agent_id}: {activity}")
                    return True
                else:
                    logger.warning(f"Failed to log activity for agent {agent_id}: {response.status}")
                    return False
        
        except Exception as e:
            logger.error(f"Error logging activity for agent {agent_id}: {str(e)}")
            return False
    
    async def clear_visualization(self) -> bool:
        """
        Clear the SwarmUI visualization.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.session:
            logger.warning("Not connected to SwarmUI server")
            return False
        
        try:
            # Clear the visualization
            async with self.session.delete(f"{self.base_url}/api/visualization") as response:
                if response.status == 200:
                    logger.info("Cleared SwarmUI visualization")
                    return True
                else:
                    logger.warning(f"Failed to clear SwarmUI visualization: {response.status}")
                    return False
        
        except Exception as e:
            logger.error(f"Error clearing SwarmUI visualization: {str(e)}")
            return False
    
    async def get_visualization_url(self) -> str:
        """
        Get the URL for the SwarmUI visualization.
        
        Returns:
            URL for the SwarmUI visualization
        """
        return f"{self.base_url}/visualization"
