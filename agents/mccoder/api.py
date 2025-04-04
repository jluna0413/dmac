"""
McCoder API - REST API for the McCoder Code Intelligence Agent

This module provides API endpoints for interacting with the McCoder agent.
"""

import logging
import json
import os
from aiohttp import web
from typing import Dict, Any, Optional

from agents.mccoder.core import McCoder
from integrations.ollama_client import OllamaClient

# Set up logging
logger = logging.getLogger('dmac.mccoder.api')

# Global McCoder instance
mccoder_instance = None

def get_mccoder_instance(project_root: Optional[str] = None, model_name: str = "gemma3:12b") -> McCoder:
    """
    Get or create the McCoder instance.
    
    Args:
        project_root: Root directory of the project to analyze
        model_name: Name of the model to use
        
    Returns:
        McCoder instance
    """
    global mccoder_instance
    
    if mccoder_instance is None:
        # Create a model provider using Ollama
        model_provider = OllamaModelProvider(model_name)
        
        # Create the McCoder instance
        mccoder_instance = McCoder(project_root, model_provider)
    
    return mccoder_instance

class OllamaModelProvider:
    """Model provider using Ollama for LLM capabilities."""
    
    def __init__(self, model_name: str = "gemma3:12b"):
        """
        Initialize the Ollama model provider.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        self.ollama_client = OllamaClient()
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text using the Ollama model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        try:
            result = await self.ollama_client.generate(self.model_name, prompt)
            
            if 'error' in result:
                logger.error(f"Error generating text: {result['error']}")
                return f"Error: {result['error']}"
            
            return result.get('text', "")
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: {str(e)}"

async def search_code(request):
    """
    API endpoint to search code.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with search results
    """
    try:
        # Parse request data
        data = await request.json()
        query = data.get('query', '')
        project_root = data.get('project_root')
        
        if not query:
            return web.json_response({
                'success': False,
                'error': 'Query parameter is required'
            }, status=400)
        
        # Get McCoder instance
        mccoder = get_mccoder_instance(project_root)
        
        # Search code
        results = mccoder.search_code(query)
        
        return web.json_response({
            'success': True,
            'results': results
        })
    except Exception as e:
        logger.error(f"Error in search_code endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def get_file_content(request):
    """
    API endpoint to get file content.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with file content
    """
    try:
        # Parse request data
        data = await request.json()
        file_path = data.get('file_path', '')
        project_root = data.get('project_root')
        
        if not file_path:
            return web.json_response({
                'success': False,
                'error': 'File path parameter is required'
            }, status=400)
        
        # Get McCoder instance
        mccoder = get_mccoder_instance(project_root)
        
        # Get file content
        content = mccoder.get_file_content(file_path)
        
        if content is None:
            return web.json_response({
                'success': False,
                'error': f'File not found: {file_path}'
            }, status=404)
        
        return web.json_response({
            'success': True,
            'content': content,
            'language': mccoder.file_index.get(file_path, {}).get('language', 'unknown')
        })
    except Exception as e:
        logger.error(f"Error in get_file_content endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def get_symbol_info(request):
    """
    API endpoint to get symbol information.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with symbol information
    """
    try:
        # Parse request data
        data = await request.json()
        symbol_name = data.get('symbol_name', '')
        project_root = data.get('project_root')
        
        if not symbol_name:
            return web.json_response({
                'success': False,
                'error': 'Symbol name parameter is required'
            }, status=400)
        
        # Get McCoder instance
        mccoder = get_mccoder_instance(project_root)
        
        # Get symbol information
        symbol_info = mccoder.get_symbol_info(symbol_name)
        
        if symbol_info is None:
            return web.json_response({
                'success': False,
                'error': f'Symbol not found: {symbol_name}'
            }, status=404)
        
        return web.json_response({
            'success': True,
            'symbol_info': symbol_info
        })
    except Exception as e:
        logger.error(f"Error in get_symbol_info endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def generate_code(request):
    """
    API endpoint to generate code.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with generated code
    """
    try:
        # Parse request data
        data = await request.json()
        prompt = data.get('prompt', '')
        language = data.get('language')
        context = data.get('context')
        project_root = data.get('project_root')
        model_name = data.get('model', 'gemma3:12b')
        
        if not prompt:
            return web.json_response({
                'success': False,
                'error': 'Prompt parameter is required'
            }, status=400)
        
        # Get McCoder instance with the specified model
        mccoder = get_mccoder_instance(project_root, model_name)
        
        # Generate code
        code = await mccoder.model_provider.generate(
            f"Generate {language or 'code'} for the following task:\n\n{prompt}" +
            (f"\n\nContext:\n{context}" if context else "")
        )
        
        return web.json_response({
            'success': True,
            'code': code
        })
    except Exception as e:
        logger.error(f"Error in generate_code endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def explain_code(request):
    """
    API endpoint to explain code.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with code explanation
    """
    try:
        # Parse request data
        data = await request.json()
        code = data.get('code', '')
        language = data.get('language')
        project_root = data.get('project_root')
        model_name = data.get('model', 'gemma3:12b')
        
        if not code:
            return web.json_response({
                'success': False,
                'error': 'Code parameter is required'
            }, status=400)
        
        # Get McCoder instance with the specified model
        mccoder = get_mccoder_instance(project_root, model_name)
        
        # Explain code
        explanation = await mccoder.model_provider.generate(
            f"Explain the following {language or 'code'} in detail:\n\n```\n{code}\n```"
        )
        
        return web.json_response({
            'success': True,
            'explanation': explanation
        })
    except Exception as e:
        logger.error(f"Error in explain_code endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def refactor_code(request):
    """
    API endpoint to refactor code.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with refactored code
    """
    try:
        # Parse request data
        data = await request.json()
        code = data.get('code', '')
        instructions = data.get('instructions', '')
        language = data.get('language')
        project_root = data.get('project_root')
        model_name = data.get('model', 'gemma3:12b')
        
        if not code:
            return web.json_response({
                'success': False,
                'error': 'Code parameter is required'
            }, status=400)
        
        if not instructions:
            return web.json_response({
                'success': False,
                'error': 'Instructions parameter is required'
            }, status=400)
        
        # Get McCoder instance with the specified model
        mccoder = get_mccoder_instance(project_root, model_name)
        
        # Refactor code
        prompt = f"Refactor the following {language or 'code'} according to these instructions:\n\n"
        prompt += f"Instructions: {instructions}\n\n"
        prompt += f"Code:\n```\n{code}\n```\n\n"
        prompt += "Please provide only the refactored code without explanations."
        
        refactored_code = await mccoder.model_provider.generate(prompt)
        
        return web.json_response({
            'success': True,
            'refactored_code': refactored_code
        })
    except Exception as e:
        logger.error(f"Error in refactor_code endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def find_bugs(request):
    """
    API endpoint to find bugs in code.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with bug report
    """
    try:
        # Parse request data
        data = await request.json()
        code = data.get('code', '')
        language = data.get('language')
        project_root = data.get('project_root')
        model_name = data.get('model', 'gemma3:12b')
        
        if not code:
            return web.json_response({
                'success': False,
                'error': 'Code parameter is required'
            }, status=400)
        
        # Get McCoder instance with the specified model
        mccoder = get_mccoder_instance(project_root, model_name)
        
        # Find bugs
        prompt = f"Find potential bugs in the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
        prompt += "Format your response as a JSON array of objects with 'line', 'description', and 'severity' fields."
        
        response = await mccoder.model_provider.generate(prompt)
        
        # Try to parse JSON from the response
        bugs = []
        try:
            # Extract JSON array from the response
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                bugs = json.loads(json_match.group(0))
        except Exception as e:
            logger.error(f"Error parsing bug report: {str(e)}")
            # If JSON parsing fails, return the raw response
            return web.json_response({
                'success': True,
                'raw_response': response,
                'bugs': []
            })
        
        return web.json_response({
            'success': True,
            'bugs': bugs
        })
    except Exception as e:
        logger.error(f"Error in find_bugs endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def generate_tests(request):
    """
    API endpoint to generate tests for code.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with generated tests
    """
    try:
        # Parse request data
        data = await request.json()
        code = data.get('code', '')
        language = data.get('language')
        project_root = data.get('project_root')
        model_name = data.get('model', 'gemma3:12b')
        
        if not code:
            return web.json_response({
                'success': False,
                'error': 'Code parameter is required'
            }, status=400)
        
        # Get McCoder instance with the specified model
        mccoder = get_mccoder_instance(project_root, model_name)
        
        # Generate tests
        prompt = f"Generate unit tests for the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
        prompt += "Please provide comprehensive tests that cover all functionality."
        
        tests = await mccoder.model_provider.generate(prompt)
        
        return web.json_response({
            'success': True,
            'tests': tests
        })
    except Exception as e:
        logger.error(f"Error in generate_tests endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def document_code(request):
    """
    API endpoint to document code.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with documented code
    """
    try:
        # Parse request data
        data = await request.json()
        code = data.get('code', '')
        language = data.get('language')
        project_root = data.get('project_root')
        model_name = data.get('model', 'gemma3:12b')
        
        if not code:
            return web.json_response({
                'success': False,
                'error': 'Code parameter is required'
            }, status=400)
        
        # Get McCoder instance with the specified model
        mccoder = get_mccoder_instance(project_root, model_name)
        
        # Document code
        prompt = f"Add comprehensive documentation to the following {language or 'code'}:\n\n```\n{code}\n```\n\n"
        prompt += "Please include docstrings, comments, and type hints where appropriate."
        
        documented_code = await mccoder.model_provider.generate(prompt)
        
        return web.json_response({
            'success': True,
            'documented_code': documented_code
        })
    except Exception as e:
        logger.error(f"Error in document_code endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def get_project_summary(request):
    """
    API endpoint to get project summary.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with project summary
    """
    try:
        # Parse request data
        data = await request.json()
        project_root = data.get('project_root')
        
        # Get McCoder instance
        mccoder = get_mccoder_instance(project_root)
        
        # Get project summary
        summary = mccoder.get_project_summary()
        
        return web.json_response({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        logger.error(f"Error in get_project_summary endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def refresh_index(request):
    """
    API endpoint to refresh the code index.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response indicating success
    """
    try:
        # Parse request data
        data = await request.json()
        project_root = data.get('project_root')
        
        # Get McCoder instance
        mccoder = get_mccoder_instance(project_root)
        
        # Refresh index
        mccoder.refresh_index()
        
        return web.json_response({
            'success': True,
            'message': 'Code index refreshed successfully'
        })
    except Exception as e:
        logger.error(f"Error in refresh_index endpoint: {str(e)}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

def setup_routes(app):
    """
    Set up the McCoder API routes.
    
    Args:
        app: The aiohttp application
    """
    app.router.add_post('/api/mccoder/search', search_code)
    app.router.add_post('/api/mccoder/file', get_file_content)
    app.router.add_post('/api/mccoder/symbol', get_symbol_info)
    app.router.add_post('/api/mccoder/generate', generate_code)
    app.router.add_post('/api/mccoder/explain', explain_code)
    app.router.add_post('/api/mccoder/refactor', refactor_code)
    app.router.add_post('/api/mccoder/bugs', find_bugs)
    app.router.add_post('/api/mccoder/tests', generate_tests)
    app.router.add_post('/api/mccoder/document', document_code)
    app.router.add_post('/api/mccoder/summary', get_project_summary)
    app.router.add_post('/api/mccoder/refresh', refresh_index)
