"""
WebArena API for DMac.

This module provides API endpoints for WebArena integration.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any

from aiohttp import web
from aiohttp.web import Request, Response

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors
from security.secure_api import require_role
from webarena.webarena_manager import webarena_manager
from webarena.ollama_integration import webarena_ollama_integration

logger = get_logger('dmac.webarena.webarena_api')


@require_role('user')
async def handle_list_tasks(request: Request) -> Response:
    """Handle a request to list WebArena tasks.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the list of tasks.
    """
    try:
        # Get the available tasks
        tasks = await webarena_manager.get_available_tasks()
        
        # Return the tasks
        return web.json_response({'tasks': tasks})
    except Exception as e:
        logger.exception(f"Error listing WebArena tasks: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_list_models(request: Request) -> Response:
    """Handle a request to list WebArena models.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the list of models.
    """
    try:
        # Get the available models
        models = await webarena_ollama_integration.get_available_models()
        
        # Return the models
        return web.json_response({'models': models})
    except Exception as e:
        logger.exception(f"Error listing WebArena models: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_run_experiment(request: Request) -> Response:
    """Handle a request to run a WebArena experiment.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the run information.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Get the experiment parameters
        task_name = body.get('task_name')
        model_name = body.get('model_name')
        num_episodes = body.get('num_episodes', 1)
        timeout = body.get('timeout')
        
        # Validate the parameters
        if not task_name:
            return web.json_response({'error': 'Missing task_name parameter'}, status=400)
        
        if not model_name:
            return web.json_response({'error': 'Missing model_name parameter'}, status=400)
        
        # Run the experiment
        run_id, run_info = await webarena_manager.run_experiment(
            task_name=task_name,
            model_name=model_name,
            num_episodes=num_episodes,
            timeout=timeout
        )
        
        # Return the run information
        return web.json_response({'run_id': run_id, 'run_info': run_info})
    except Exception as e:
        logger.exception(f"Error running WebArena experiment: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_run_status(request: Request) -> Response:
    """Handle a request to get the status of a WebArena run.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the run status.
    """
    try:
        # Get the run ID from the URL
        run_id = request.match_info.get('run_id')
        
        if not run_id:
            return web.json_response({'error': 'Missing run_id parameter'}, status=400)
        
        # Get the run status
        run_status = await webarena_manager.get_run_status(run_id)
        
        # Return the run status
        return web.json_response({'run_status': run_status})
    except Exception as e:
        logger.exception(f"Error getting WebArena run status: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_stop_run(request: Request) -> Response:
    """Handle a request to stop a WebArena run.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response indicating whether the run was stopped.
    """
    try:
        # Get the run ID from the URL
        run_id = request.match_info.get('run_id')
        
        if not run_id:
            return web.json_response({'error': 'Missing run_id parameter'}, status=400)
        
        # Stop the run
        success = await webarena_manager.stop_run(run_id)
        
        # Return the result
        return web.json_response({'success': success})
    except Exception as e:
        logger.exception(f"Error stopping WebArena run: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_run_results(request: Request) -> Response:
    """Handle a request to get the results of a WebArena run.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the run results.
    """
    try:
        # Get the run ID from the URL
        run_id = request.match_info.get('run_id')
        
        if not run_id:
            return web.json_response({'error': 'Missing run_id parameter'}, status=400)
        
        # Get the run results
        results = await webarena_manager.get_run_results(run_id)
        
        # Return the results
        return web.json_response({'results': results})
    except Exception as e:
        logger.exception(f"Error getting WebArena run results: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_list_runs(request: Request) -> Response:
    """Handle a request to list WebArena runs.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the list of runs.
    """
    try:
        # Get the status parameter from the query string
        status = request.query.get('status')
        
        # List the runs
        runs = await webarena_manager.list_runs(status)
        
        # Return the runs
        return web.json_response({'runs': runs})
    except Exception as e:
        logger.exception(f"Error listing WebArena runs: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_update_model_config(request: Request) -> Response:
    """Handle a request to update a WebArena model configuration.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response indicating whether the configuration was updated.
    """
    try:
        # Get the model name from the URL
        model_name = request.match_info.get('model_name')
        
        if not model_name:
            return web.json_response({'error': 'Missing model_name parameter'}, status=400)
        
        # Parse the request body
        body = await request.json()
        
        # Get the configuration parameters
        system_prompt = body.get('system_prompt')
        
        # Update the model configuration
        success = await webarena_ollama_integration.update_model_config(
            model_name=model_name,
            system_prompt=system_prompt
        )
        
        # Return the result
        return web.json_response({'success': success})
    except Exception as e:
        logger.exception(f"Error updating WebArena model configuration: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_model_config(request: Request) -> Response:
    """Handle a request to get a WebArena model configuration.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the model configuration.
    """
    try:
        # Get the model name from the URL
        model_name = request.match_info.get('model_name')
        
        if not model_name:
            return web.json_response({'error': 'Missing model_name parameter'}, status=400)
        
        # Get the model configuration
        config = await webarena_ollama_integration.get_model_config(model_name)
        
        if not config:
            return web.json_response({'error': f"Model configuration for '{model_name}' not found"}, status=404)
        
        # Return the configuration
        return web.json_response({'config': config})
    except Exception as e:
        logger.exception(f"Error getting WebArena model configuration: {e}")
        return web.json_response({'error': str(e)}, status=500)


def setup_webarena_routes(app: web.Application) -> None:
    """Set up WebArena API routes.
    
    Args:
        app: The application to set up routes for.
    """
    # Add the routes
    app.router.add_get('/api/webarena/tasks', handle_list_tasks)
    app.router.add_get('/api/webarena/models', handle_list_models)
    app.router.add_post('/api/webarena/runs', handle_run_experiment)
    app.router.add_get('/api/webarena/runs', handle_list_runs)
    app.router.add_get('/api/webarena/runs/{run_id}', handle_get_run_status)
    app.router.add_delete('/api/webarena/runs/{run_id}', handle_stop_run)
    app.router.add_get('/api/webarena/runs/{run_id}/results', handle_get_run_results)
    app.router.add_get('/api/webarena/models/{model_name}/config', handle_get_model_config)
    app.router.add_put('/api/webarena/models/{model_name}/config', handle_update_model_config)
    
    logger.info("WebArena API routes set up")
