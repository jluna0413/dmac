"""
Chat API for DMac.

This module provides API endpoints for chat functionality.
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any

from aiohttp import web
from aiohttp.web import Request, Response

from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors
from security.secure_api import require_role
from integrations.ollama_client import ollama_client
from integrations.web_search import web_search

logger = get_logger('dmac.agents.chat_api')


@require_role('user')
async def handle_chat(request: Request) -> Response:
    """Handle a chat request.

    Args:
        request: The request to handle.

    Returns:
        A response containing the chat response.
    """
    try:
        # Parse the request body
        body = await request.json()

        # Get the chat parameters
        message = body.get('message')
        model = body.get('model', 'gemma3:12b')  # Default to Gemma 3 12B
        use_web_search = body.get('use_web_search', False)
        search_engine = body.get('search_engine')  # Optional search engine

        if not message:
            return web.json_response({'error': 'Missing message parameter'}, status=400)

        # Check if the message requires web search
        needs_web_search = use_web_search or _should_use_web_search(message)

        # Initialize variables
        web_search_results = ""
        search_query = ""

        # If web search is needed, perform the search
        if needs_web_search:
            # Extract the search query
            search_query = _extract_search_query(message)

            # Perform the search
            logger.info(f"Performing web search for query: {search_query} using engine: {search_engine if search_engine else 'default'}")
            web_search_results = await web_search.search_and_summarize(search_query, engine=search_engine)

        # Prepare the messages for the model
        messages = []

        # Add system message
        system_message = "You are a helpful AI assistant that provides accurate and up-to-date information."

        if needs_web_search:
            system_message += " You have access to real-time information from the web. Use this information to provide the most accurate and current response possible. Always cite your sources."

        messages.append({
            "role": "system",
            "content": system_message
        })

        # Add user message with web search results if available
        user_content = message
        if web_search_results:
            user_content += f"\n\nHere is some real-time information from the web that may help you answer:\n\n{web_search_results}"

        messages.append({
            "role": "user",
            "content": user_content
        })

        # Get the response from the model
        logger.info(f"Getting response from model {model}")
        # Use the Ollama client to get a response
        try:
            response = await ollama_client.chat(model, messages)
        except Exception as e:
            logger.error(f"Error from Ollama client: {e}")
            # Fallback response
            response = {
                'response': f"I'm sorry, I couldn't get a response from the model. Error: {str(e)}",
                'model': model,
                'messages': messages
            }

        # Check for errors
        if 'error' in response:
            logger.error(f"Error getting response from model: {response['error']}")
            return web.json_response({'error': response['error']}, status=500)

        # Return the response
        return web.json_response({
            'response': response.get('response', ''),
            'model': model,
            'used_web_search': needs_web_search,
            'search_engine': search_engine if needs_web_search and search_engine else None,
            'search_query': search_query if needs_web_search else None
        })
    except Exception as e:
        logger.exception(f"Error handling chat request: {e}")
        return web.json_response({'error': str(e)}, status=500)


def _should_use_web_search(message: str) -> bool:
    """Determine if a message should use web search.

    Args:
        message: The message to check.

    Returns:
        True if the message should use web search, False otherwise.
    """
    # Keywords that indicate a need for current information
    current_info_keywords = [
        'current', 'latest', 'recent', 'today', 'now', 'update',
        'news', 'version', 'release', 'weather', 'price',
        'stock', 'market', 'election', 'score', 'game',
        'what is the', 'how to', 'who is', 'where is',
        'best', 'top', 'trending', 'popular', 'review',
        'comparison', 'vs', 'versus', 'difference between',
        'how many', 'when was', 'where can I', 'why does'
    ]

    # Check if any of the keywords are in the message
    message_lower = message.lower()
    for keyword in current_info_keywords:
        if keyword in message_lower:
            return True

    # Check for questions about dates or times
    date_time_patterns = [
        r'what (day|date|time|year) is it',
        r'what is the (date|time|year)',
        r'current (date|time|year)',
        r'today\'s (date|day)',
        r'what is today',
        r'when (is|was|will)',
        r'(date|time) of',
        r'how long (ago|until)',
        r'(yesterday|tomorrow)'
    ]

    for pattern in date_time_patterns:
        if re.search(pattern, message_lower):
            return True

    return False


def _extract_search_query(message: str) -> str:
    """Extract a search query from a message.

    Args:
        message: The message to extract from.

    Returns:
        The extracted search query.
    """
    # If the message is short, use it as is
    if len(message.split()) <= 10:
        return message

    # Try to extract a question
    question_patterns = [
        r'what is (.*?)\?',
        r'who is (.*?)\?',
        r'where is (.*?)\?',
        r'when is (.*?)\?',
        r'why is (.*?)\?',
        r'how (to|do|does|can|could) (.*?)\?',
        r'which (is|are) (.*?)\?',
        r'can (.*?)\?',
        r'will (.*?)\?',
        r'should (.*?)\?',
        r'is (.*?)\?',
        r'are (.*?)\?'
    ]

    for pattern in question_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(0)

    # If no question found, use the first sentence
    sentences = message.split('.')
    if sentences:
        return sentences[0]

    # Fallback to the original message
    return message


def setup_chat_routes(app: web.Application) -> None:
    """Set up chat API routes.

    Args:
        app: The application to set up routes for.
    """
    # Add the routes
    app.router.add_post('/api/chat', handle_chat)

    logger.info("Chat API routes set up")
