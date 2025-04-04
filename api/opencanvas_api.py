"""
OpenCanvas API for DMac

This module provides API endpoints for interacting with Langchain's OpenCanvas.
"""

import logging
import json
import os
import tempfile
import webbrowser
from pathlib import Path
from aiohttp import web
from typing import Dict, Any, List, Optional

# Set up logging
logger = logging.getLogger('dmac.opencanvas_api')

# OpenCanvas configuration
OPENCANVAS_URL = "http://localhost:3000"  # Default OpenCanvas URL

class OpenCanvasManager:
    """Manager for OpenCanvas interactions."""
    
    def __init__(self, base_url: str = OPENCANVAS_URL):
        """
        Initialize the OpenCanvas manager.
        
        Args:
            base_url: Base URL for OpenCanvas
        """
        self.base_url = base_url
        self.temp_dir = Path(tempfile.gettempdir()) / "dmac_opencanvas"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"OpenCanvas manager initialized with base URL: {base_url}")
    
    def open_canvas(self, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Open OpenCanvas with the current conversation history.
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            URL to the OpenCanvas interface
        """
        # Create a unique ID for this session
        import uuid
        session_id = str(uuid.uuid4())
        
        # Save conversation history to a temporary file if provided
        if conversation_history:
            conversation_file = self.temp_dir / f"conversation_{session_id}.json"
            with open(conversation_file, 'w') as f:
                json.dump(conversation_history, f)
            
            # In a real implementation, we would pass this file to OpenCanvas
            # For now, we'll just open the base URL
        
        # Construct the OpenCanvas URL
        # In a real implementation, this would include parameters to load the conversation
        canvas_url = f"{self.base_url}?session={session_id}"
        
        logger.info(f"Opening OpenCanvas with URL: {canvas_url}")
        
        return canvas_url

async def open_opencanvas(request):
    """
    API endpoint to open the OpenCanvas interface.
    
    Args:
        request (web.Request): The request object.
        
    Returns:
        web.Response: JSON response with the OpenCanvas URL.
    """
    try:
        # Parse request data
        data = await request.json()
        conversation_history = data.get('current_conversation', [])
        
        # Get OpenCanvas manager
        opencanvas_manager = OpenCanvasManager()
        
        # Open OpenCanvas
        canvas_url = opencanvas_manager.open_canvas(conversation_history)
        
        # Try to open the URL in the browser
        try:
            webbrowser.open(canvas_url)
            browser_opened = True
        except Exception as e:
            logger.error(f"Error opening browser: {str(e)}")
            browser_opened = False
        
        return web.json_response({
            'success': True,
            'url': canvas_url,
            'browser_opened': browser_opened
        })
    except Exception as e:
        logger.error(f"Error in open_opencanvas endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

def setup_routes(app):
    """
    Set up the OpenCanvas API routes.
    
    Args:
        app (web.Application): The aiohttp application.
    """
    app.router.add_post('/api/opencanvas/open', open_opencanvas)
