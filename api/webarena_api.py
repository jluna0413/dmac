"""
WebArena API Integration for DMac.

This module provides API endpoints for interacting with WebArena agents.
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
from agents.agent_manager import agent_manager
from agents.webarena_agent_factory import webarena_agent_factory

logger = get_logger('dmac.api.webarena_api')


@require_role('user')
async def handle_create_webarena_agent(request: Request) -> Response:
    """Handle a request to create a WebArena agent.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the created agent information.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Get the agent parameters
        name = body.get('name')
        
        # Create the agent
        agent = await agent_manager.create_agent(agent_type='webarena', name=name)
        
        # Return the agent information
        return web.json_response({
            'agent_id': agent.agent_id,
            'name': agent.name,
            'type': agent.agent_type,
        })
    except Exception as e:
        logger.exception(f"Error creating WebArena agent: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_list_webarena_agents(request: Request) -> Response:
    """Handle a request to list WebArena agents.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the list of agents.
    """
    try:
        # List the agents
        agents = await agent_manager.list_agents(agent_type='webarena')
        
        # Return the agents
        return web.json_response({'agents': agents})
    except Exception as e:
        logger.exception(f"Error listing WebArena agents: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_webarena_agent(request: Request) -> Response:
    """Handle a request to get a WebArena agent.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the agent information.
    """
    try:
        # Get the agent ID from the URL
        agent_id = request.match_info.get('agent_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Get the agent
        agent = await agent_manager.get_agent(agent_id)
        
        if not agent:
            return web.json_response({'error': f"Agent {agent_id} not found"}, status=404)
        
        if agent.agent_type != 'webarena':
            return web.json_response({'error': f"Agent {agent_id} is not a WebArena agent"}, status=400)
        
        # Return the agent information
        return web.json_response({
            'agent_id': agent.agent_id,
            'name': agent.name,
            'type': agent.agent_type,
            'current_run_id': agent.current_run_id,
            'current_task': agent.current_task,
            'current_model': agent.current_model,
        })
    except Exception as e:
        logger.exception(f"Error getting WebArena agent: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_delete_webarena_agent(request: Request) -> Response:
    """Handle a request to delete a WebArena agent.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response indicating whether the agent was deleted.
    """
    try:
        # Get the agent ID from the URL
        agent_id = request.match_info.get('agent_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Delete the agent
        success = await agent_manager.delete_agent(agent_id)
        
        if not success:
            return web.json_response({'error': f"Agent {agent_id} not found"}, status=404)
        
        # Return success
        return web.json_response({'success': True})
    except Exception as e:
        logger.exception(f"Error deleting WebArena agent: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_send_message_to_webarena_agent(request: Request) -> Response:
    """Handle a request to send a message to a WebArena agent.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the agent's response.
    """
    try:
        # Get the agent ID from the URL
        agent_id = request.match_info.get('agent_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Parse the request body
        body = await request.json()
        
        # Get the message
        message = body.get('message')
        
        if not message:
            return web.json_response({'error': 'Missing message parameter'}, status=400)
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response({'response': response})
    except Exception as e:
        logger.exception(f"Error sending message to WebArena agent: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_run_webarena_experiment(request: Request) -> Response:
    """Handle a request to run a WebArena experiment.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the run information.
    """
    try:
        # Get the agent ID from the URL
        agent_id = request.match_info.get('agent_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
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
        
        # Create the message
        message = {
            'type': 'run_experiment',
            'task_name': task_name,
            'model_name': model_name,
            'num_episodes': num_episodes,
            'timeout': timeout,
        }
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error running WebArena experiment: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_webarena_run_status(request: Request) -> Response:
    """Handle a request to get the status of a WebArena run.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the run status.
    """
    try:
        # Get the agent ID and run ID from the URL
        agent_id = request.match_info.get('agent_id')
        run_id = request.match_info.get('run_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Create the message
        message = {
            'type': 'get_run_status',
            'run_id': run_id,
        }
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error getting WebArena run status: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_stop_webarena_run(request: Request) -> Response:
    """Handle a request to stop a WebArena run.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response indicating whether the run was stopped.
    """
    try:
        # Get the agent ID and run ID from the URL
        agent_id = request.match_info.get('agent_id')
        run_id = request.match_info.get('run_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Create the message
        message = {
            'type': 'stop_run',
            'run_id': run_id,
        }
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error stopping WebArena run: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_webarena_run_results(request: Request) -> Response:
    """Handle a request to get the results of a WebArena run.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the run results.
    """
    try:
        # Get the agent ID and run ID from the URL
        agent_id = request.match_info.get('agent_id')
        run_id = request.match_info.get('run_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Create the message
        message = {
            'type': 'get_run_results',
            'run_id': run_id,
        }
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error getting WebArena run results: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_list_webarena_runs(request: Request) -> Response:
    """Handle a request to list WebArena runs.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the list of runs.
    """
    try:
        # Get the agent ID from the URL
        agent_id = request.match_info.get('agent_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Get the status parameter from the query string
        status = request.query.get('status')
        
        # Create the message
        message = {
            'type': 'list_runs',
            'status': status,
        }
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error listing WebArena runs: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_available_webarena_tasks(request: Request) -> Response:
    """Handle a request to get the available WebArena tasks.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the list of tasks.
    """
    try:
        # Get the agent ID from the URL
        agent_id = request.match_info.get('agent_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Create the message
        message = {
            'type': 'get_available_tasks',
        }
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error getting available WebArena tasks: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_get_available_webarena_models(request: Request) -> Response:
    """Handle a request to get the available WebArena models.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the list of models.
    """
    try:
        # Get the agent ID from the URL
        agent_id = request.match_info.get('agent_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Create the message
        message = {
            'type': 'get_available_models',
        }
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error getting available WebArena models: {e}")
        return web.json_response({'error': str(e)}, status=500)


@require_role('user')
async def handle_generate_webarena_visualization(request: Request) -> Response:
    """Handle a request to generate a WebArena visualization.
    
    Args:
        request: The request to handle.
        
    Returns:
        A response containing the visualization path.
    """
    try:
        # Get the agent ID from the URL
        agent_id = request.match_info.get('agent_id')
        
        if not agent_id:
            return web.json_response({'error': 'Missing agent_id parameter'}, status=400)
        
        # Parse the request body
        body = await request.json()
        
        # Get the visualization parameters
        visualization_type = body.get('visualization_type')
        run_ids = body.get('run_ids', [])
        task_name = body.get('task_name')
        model_names = body.get('model_names', [])
        
        if not visualization_type:
            return web.json_response({'error': 'Missing visualization_type parameter'}, status=400)
        
        # Create the message
        message = {
            'type': 'generate_visualization',
            'visualization_type': visualization_type,
            'run_ids': run_ids,
            'task_name': task_name,
            'model_names': model_names,
        }
        
        # Send the message to the agent
        response = await agent_manager.send_message(agent_id, message)
        
        # Return the response
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error generating WebArena visualization: {e}")
        return web.json_response({'error': str(e)}, status=500)


def setup_webarena_agent_routes(app: web.Application) -> None:
    """Set up WebArena agent API routes.
    
    Args:
        app: The application to set up routes for.
    """
    # Add the routes
    app.router.add_post('/api/agents/webarena', handle_create_webarena_agent)
    app.router.add_get('/api/agents/webarena', handle_list_webarena_agents)
    app.router.add_get('/api/agents/webarena/{agent_id}', handle_get_webarena_agent)
    app.router.add_delete('/api/agents/webarena/{agent_id}', handle_delete_webarena_agent)
    app.router.add_post('/api/agents/webarena/{agent_id}/message', handle_send_message_to_webarena_agent)
    app.router.add_post('/api/agents/webarena/{agent_id}/runs', handle_run_webarena_experiment)
    app.router.add_get('/api/agents/webarena/{agent_id}/runs', handle_list_webarena_runs)
    app.router.add_get('/api/agents/webarena/{agent_id}/runs/{run_id}', handle_get_webarena_run_status)
    app.router.add_delete('/api/agents/webarena/{agent_id}/runs/{run_id}', handle_stop_webarena_run)
    app.router.add_get('/api/agents/webarena/{agent_id}/runs/{run_id}/results', handle_get_webarena_run_results)
    app.router.add_get('/api/agents/webarena/{agent_id}/tasks', handle_get_available_webarena_tasks)
    app.router.add_get('/api/agents/webarena/{agent_id}/models', handle_get_available_webarena_models)
    app.router.add_post('/api/agents/webarena/{agent_id}/visualizations', handle_generate_webarena_visualization)
    
    logger.info("WebArena agent API routes set up")
