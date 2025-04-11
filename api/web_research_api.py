"""
Web Research API for DMac

This module provides API endpoints for web research functionality.
"""

import logging
import json
from aiohttp import web
from utils.web_research import WebResearch

# Set up logging
logger = logging.getLogger('dmac.web_research_api')

# Create web research instance
web_research = WebResearch()

async def search_web(request):
    """
    API endpoint to search the web.
    
    Args:
        request (web.Request): The request object.
        
    Returns:
        web.Response: JSON response with search results.
    """
    try:
        # Parse request data
        data = await request.json()
        query = data.get('query', '')
        num_results = int(data.get('num_results', 5))
        
        if not query:
            return web.json_response({
                'success': False,
                'error': 'Query parameter is required'
            }, status=400)
        
        # Search the web
        success, results = web_research.search_web(query, num_results=num_results)
        
        if success:
            return web.json_response({
                'success': True,
                'results': results
            })
        else:
            return web.json_response({
                'success': False,
                'error': results  # Error message
            }, status=500)
    except Exception as e:
        logger.error(f"Error in search_web endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def research_topic(request):
    """
    API endpoint to research a topic.
    
    Args:
        request (web.Request): The request object.
        
    Returns:
        web.Response: JSON response with research data.
    """
    try:
        # Parse request data
        data = await request.json()
        query = data.get('query', '')
        max_sources = int(data.get('max_sources', 3))
        max_depth = int(data.get('max_depth', 1))
        
        if not query:
            return web.json_response({
                'success': False,
                'error': 'Query parameter is required'
            }, status=400)
        
        # Research the topic
        success, research_data = web_research.research_topic(
            query, 
            max_sources=max_sources,
            max_depth=max_depth
        )
        
        if success:
            return web.json_response({
                'success': True,
                'research_data': research_data
            })
        else:
            return web.json_response({
                'success': False,
                'error': research_data  # Error message
            }, status=500)
    except Exception as e:
        logger.error(f"Error in research_topic endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def scrape_site(request):
    """
    API endpoint to scrape a specific website.
    
    Args:
        request (web.Request): The request object.
        
    Returns:
        web.Response: JSON response with scraped data.
    """
    try:
        # Parse request data
        data = await request.json()
        url = data.get('url', '')
        max_articles = int(data.get('max_articles', 5))
        
        if not url:
            return web.json_response({
                'success': False,
                'error': 'URL parameter is required'
            }, status=400)
        
        # Scrape the site
        success, site_data = web_research.scrape_specific_site(url, max_articles=max_articles)
        
        if success:
            return web.json_response({
                'success': True,
                'site_data': site_data
            })
        else:
            return web.json_response({
                'success': False,
                'error': site_data  # Error message
            }, status=500)
    except Exception as e:
        logger.error(f"Error in scrape_site endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

def setup_routes(app):
    """
    Set up the web research API routes.
    
    Args:
        app (web.Application): The aiohttp application.
    """
    app.router.add_post('/api/web/search', search_web)
    app.router.add_post('/api/web/research', research_topic)
    app.router.add_post('/api/web/scrape', scrape_site)
