"""
Feedback API for DMac

This module provides API endpoints for the feedback system.
"""

import logging
import json
import os
from datetime import datetime
from aiohttp import web
from pathlib import Path

# Set up logging
logger = logging.getLogger('dmac.feedback_api')

# Create feedback directory if it doesn't exist
FEEDBACK_DIR = Path('data/feedback')
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

async def submit_feedback(request):
    """
    API endpoint to submit feedback on model responses.
    
    Args:
        request (web.Request): The request object.
        
    Returns:
        web.Response: JSON response indicating success or failure.
    """
    try:
        # Parse request data
        data = await request.json()
        
        # Validate required fields
        if 'messageId' not in data:
            return web.json_response({
                'success': False,
                'error': 'Message ID is required'
            }, status=400)
        
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        # Save feedback to file
        feedback_file = FEEDBACK_DIR / f"{data['messageId']}.json"
        with open(feedback_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Log feedback
        logger.info(f"Feedback received for message {data['messageId']}: {'positive' if data.get('isPositive') else 'negative'}")
        
        # Return success response
        return web.json_response({
            'success': True,
            'message': 'Feedback submitted successfully'
        })
    except Exception as e:
        logger.error(f"Error in submit_feedback endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def get_feedback_stats(request):
    """
    API endpoint to get feedback statistics.
    
    Args:
        request (web.Request): The request object.
        
    Returns:
        web.Response: JSON response with feedback statistics.
    """
    try:
        # Get all feedback files
        feedback_files = list(FEEDBACK_DIR.glob('*.json'))
        
        # Parse feedback data
        feedback_data = []
        for file in feedback_files:
            try:
                with open(file, 'r') as f:
                    feedback = json.load(f)
                    feedback_data.append(feedback)
            except Exception as e:
                logger.error(f"Error parsing feedback file {file}: {str(e)}")
        
        # Calculate statistics
        total_feedback = len(feedback_data)
        positive_feedback = sum(1 for f in feedback_data if f.get('isPositive', False))
        negative_feedback = total_feedback - positive_feedback
        
        # Count categories
        category_counts = {}
        for feedback in feedback_data:
            for category in feedback.get('categories', []):
                if category not in category_counts:
                    category_counts[category] = 0
                category_counts[category] += 1
        
        # Return statistics
        return web.json_response({
            'success': True,
            'stats': {
                'total': total_feedback,
                'positive': positive_feedback,
                'negative': negative_feedback,
                'categories': category_counts
            }
        })
    except Exception as e:
        logger.error(f"Error in get_feedback_stats endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

def setup_routes(app):
    """
    Set up the feedback API routes.
    
    Args:
        app (web.Application): The aiohttp application.
    """
    app.router.add_post('/api/feedback/submit', submit_feedback)
    app.router.add_get('/api/feedback/stats', get_feedback_stats)
