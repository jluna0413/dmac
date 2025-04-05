"""
Web Search API for DMac.

This module provides API endpoints for web search functionality.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any

from aiohttp import web
from aiohttp.web import Request, Response

from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors
from security.secure_api import require_role
from integrations.web_search import web_search, SearchCache

logger = get_logger('dmac.integrations.web_search_api')


@require_role('user')
async def handle_web_search(request: Request) -> Response:
    """Handle a request to search the web.

    Args:
        request: The request to handle.

    Returns:
        A response containing the search results.
    """
    try:
        # Parse the request body
        body = await request.json()

        # Get the search query
        query = body.get('query')
        num_results = body.get('num_results', 5)
        engine = body.get('engine')  # Optional search engine

        if not query:
            return web.json_response({'error': 'Missing query parameter'}, status=400)

        # Search the web
        results = await web_search.search(query, num_results, engine)

        # Return the results
        return web.json_response({'results': results})
    except Exception as e:
        logger.exception(f"Error searching the web: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_page_content(request: Request) -> Response:
    """Handle a request to get the content of a web page.

    Args:
        request: The request to handle.

    Returns:
        A response containing the page content.
    """
    try:
        # Parse the request body
        body = await request.json()

        # Get the URL
        url = body.get('url')

        if not url:
            return web.json_response({'error': 'Missing url parameter'}, status=400)

        # Get the page content
        content = await web_search.get_page_content(url)

        # Return the content
        return web.json_response({'content': content})
    except Exception as e:
        logger.exception(f"Error getting page content: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_search_and_summarize(request: Request) -> Response:
    """Handle a request to search the web and summarize the results.

    Args:
        request: The request to handle.

    Returns:
        A response containing the summary.
    """
    try:
        # Parse the request body
        body = await request.json()

        # Get the search query
        query = body.get('query')
        num_results = body.get('num_results', 3)
        engine = body.get('engine')  # Optional search engine

        if not query:
            return web.json_response({'error': 'Missing query parameter'}, status=400)

        # Search and summarize
        summary = await web_search.search_and_summarize(query, num_results, engine)

        # Return the summary
        return web.json_response({'summary': summary})
    except Exception as e:
        logger.exception(f"Error searching and summarizing: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_clear_cache(request: Request) -> Response:
    """Handle a request to clear the search cache.

    Args:
        request: The request to handle.

    Returns:
        A response indicating success or failure.
    """
    try:
        # Clear the cache
        web_search.cache = SearchCache()

        # Return success
        return web.json_response({'success': True})
    except Exception as e:
        logger.exception(f"Error clearing search cache: {e}")
        return web.json_response({'error': str(e)}, status=500)


def setup_web_search_routes(app: web.Application) -> None:
    """Set up web search API routes.

    Args:
        app: The application to set up routes for.
    """
    # Add the routes
    app.router.add_post('/api/web-search/search', handle_web_search)
    app.router.add_post('/api/web-search/get-page-content', handle_get_page_content)
    app.router.add_post('/api/web-search/search-and-summarize', handle_search_and_summarize)
    app.router.add_post('/api/web-search/clear-cache', handle_clear_cache)

    logger.info("Web search API routes set up")
