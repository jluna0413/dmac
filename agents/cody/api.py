"""
API endpoints for the Cody agent.

This module provides API endpoints for interacting with the Cody agent,
including getting agent details, benchmarks, and performance metrics.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional

from aiohttp import web
from aiohttp.web import Request, Response

from utils.secure_logging import get_logger
from agents.cody.agent import CodyAgent
from config.config import config

logger = get_logger('dmac.agents.cody.api')

# Cache for agent details
_agent_details_cache = {}
_agent_details_cache_time = 0
_CACHE_EXPIRY = 60  # seconds

async def get_agent_details(request: Request) -> Response:
    """
    API endpoint to get Cody agent details.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with agent details
    """
    try:
        # Check if we have a cached response that's still valid
        global _agent_details_cache, _agent_details_cache_time
        current_time = time.time()
        
        if _agent_details_cache and (current_time - _agent_details_cache_time) < _CACHE_EXPIRY:
            return web.json_response(_agent_details_cache)
        
        # Get agent configuration
        agent_config = config.get('agents.cody', {})
        
        # Get agent data file
        agent_data_path = os.path.join('data', 'agents', 'cody.json')
        agent_data = {}
        
        if os.path.exists(agent_data_path):
            try:
                with open(agent_data_path, 'r') as f:
                    agent_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading agent data: {e}")
        
        # Combine configuration and data
        agent_details = {
            'id': 'cody',
            'name': 'Cody',
            'type': 'code_assistant',
            'status': 'active',
            'description': 'Native Code Assistant with code completion, vision capabilities, and reinforcement learning integration',
            'model': agent_config.get('model_name', 'GandalfBaum/deepseek_r1-claude3.7:latest'),
            'capabilities': agent_config.get('capabilities', [
                'code_search',
                'code_generation',
                'code_completion',
                'code_explanation',
                'code_refactoring',
                'bug_finding',
                'test_generation',
                'code_documentation',
                'project_analysis',
                'vision_code_understanding',
                'reinforcement_learning'
            ]),
            'configuration': {
                'temperature': agent_config.get('temperature', 0.2),
                'max_context_length': agent_config.get('max_context_length', 16384),
                'vision_enabled': agent_config.get('vision_enabled', True),
                'rl_enabled': agent_config.get('rl_enabled', True),
                'rl_model': agent_config.get('rl_model', 'openManus'),
                'code_completion_enabled': agent_config.get('code_completion_enabled', True)
            },
            'metadata': agent_data.get('metadata', {}),
            'created_at': agent_data.get('created_at', '2025-04-08T12:00:00Z'),
            'updated_at': agent_data.get('updated_at', '2025-04-08T12:00:00Z')
        }
        
        # Add performance metrics
        agent_details['performance'] = {
            'tasks_completed': 42,  # This would come from a database in a real implementation
            'success_rate': '94%',
            'average_response_time': '180ms',
            'memory_usage': '1.4 GB'
        }
        
        # Cache the response
        _agent_details_cache = agent_details
        _agent_details_cache_time = current_time
        
        return web.json_response(agent_details)
    except Exception as e:
        logger.exception(f"Error getting agent details: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def get_agent_benchmarks(request: Request) -> Response:
    """
    API endpoint to get Cody agent benchmarks.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with agent benchmarks
    """
    try:
        # Parse request data
        data = await request.json() if request.body_exists else {}
        category = data.get('category', 'all')
        limit = int(data.get('limit', 10))
        
        # Get benchmark data
        # In a real implementation, this would come from a database
        benchmarks = [
            {
                'id': 'benchmark_1',
                'category': 'code_generation',
                'task': 'Generate a function to parse JSON',
                'timestamp': '2025-04-07T10:00:00Z',
                'models': [
                    {
                        'name': 'GandalfBaum/deepseek_r1-claude3.7:latest',
                        'accuracy': 0.95,
                        'latency': 210,
                        'tokens_per_second': 42.5,
                        'code_quality': 0.92,
                        'execution_time': 0.8
                    },
                    {
                        'name': 'gemma3:12b',
                        'accuracy': 0.88,
                        'latency': 180,
                        'tokens_per_second': 38.2,
                        'code_quality': 0.85,
                        'execution_time': 0.9
                    },
                    {
                        'name': 'qwen2.5-coder:1.5b-base',
                        'accuracy': 0.82,
                        'latency': 120,
                        'tokens_per_second': 52.1,
                        'code_quality': 0.78,
                        'execution_time': 1.1
                    }
                ]
            },
            {
                'id': 'benchmark_2',
                'category': 'code_explanation',
                'task': 'Explain a complex algorithm',
                'timestamp': '2025-04-07T11:30:00Z',
                'models': [
                    {
                        'name': 'GandalfBaum/deepseek_r1-claude3.7:latest',
                        'accuracy': 0.97,
                        'latency': 250,
                        'tokens_per_second': 38.1,
                        'code_quality': 'N/A',
                        'execution_time': 'N/A'
                    },
                    {
                        'name': 'gemma3:12b',
                        'accuracy': 0.91,
                        'latency': 220,
                        'tokens_per_second': 35.5,
                        'code_quality': 'N/A',
                        'execution_time': 'N/A'
                    },
                    {
                        'name': 'qwen2.5-coder:1.5b-base',
                        'accuracy': 0.84,
                        'latency': 150,
                        'tokens_per_second': 48.2,
                        'code_quality': 'N/A',
                        'execution_time': 'N/A'
                    }
                ]
            },
            {
                'id': 'benchmark_3',
                'category': 'code_completion',
                'task': 'Complete function implementation',
                'timestamp': '2025-04-07T14:15:00Z',
                'models': [
                    {
                        'name': 'GandalfBaum/deepseek_r1-claude3.7:latest',
                        'accuracy': 0.94,
                        'latency': 180,
                        'tokens_per_second': 45.2,
                        'code_quality': 0.90,
                        'execution_time': 0.7
                    },
                    {
                        'name': 'gemma3:12b',
                        'accuracy': 0.89,
                        'latency': 160,
                        'tokens_per_second': 40.8,
                        'code_quality': 0.86,
                        'execution_time': 0.8
                    },
                    {
                        'name': 'qwen2.5-coder:1.5b-base',
                        'accuracy': 0.81,
                        'latency': 110,
                        'tokens_per_second': 55.3,
                        'code_quality': 0.75,
                        'execution_time': 1.0
                    }
                ]
            }
        ]
        
        # Filter by category if specified
        if category != 'all':
            benchmarks = [b for b in benchmarks if b['category'] == category]
        
        # Limit the number of results
        benchmarks = benchmarks[:limit]
        
        return web.json_response({
            'success': True,
            'benchmarks': benchmarks
        })
    except Exception as e:
        logger.exception(f"Error getting agent benchmarks: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def get_agent_performance(request: Request) -> Response:
    """
    API endpoint to get Cody agent performance metrics.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with agent performance metrics
    """
    try:
        # Parse request data
        data = await request.json() if request.body_exists else {}
        period = data.get('period', 'week')  # day, week, month, year
        
        # Get performance data
        # In a real implementation, this would come from a database
        
        # Generate some sample data based on the period
        if period == 'day':
            intervals = 24  # hours
            interval_name = 'hour'
        elif period == 'week':
            intervals = 7  # days
            interval_name = 'day'
        elif period == 'month':
            intervals = 30  # days
            interval_name = 'day'
        else:  # year
            intervals = 12  # months
            interval_name = 'month'
        
        # Generate sample data
        performance_data = []
        for i in range(intervals):
            performance_data.append({
                'interval': i + 1,
                'interval_name': f"{interval_name} {i + 1}",
                'tasks_completed': 10 + i * 2,
                'success_rate': 85 + (i % 3) * 5,
                'average_response_time': 200 - i * 2,
                'memory_usage': 1.0 + (i % 5) * 0.1
            })
        
        # Task completion status
        task_status = {
            'completed': 42,
            'in_progress': 5,
            'failed': 3,
            'pending': 8
        }
        
        # Task categories
        task_categories = {
            'code_generation': 18,
            'code_completion': 12,
            'code_explanation': 8,
            'code_refactoring': 6,
            'bug_finding': 4,
            'test_generation': 3,
            'other': 7
        }
        
        return web.json_response({
            'success': True,
            'period': period,
            'performance_data': performance_data,
            'task_status': task_status,
            'task_categories': task_categories
        })
    except Exception as e:
        logger.exception(f"Error getting agent performance: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

async def send_message_to_agent(request: Request) -> Response:
    """
    API endpoint to send a message to the Cody agent.
    
    Args:
        request: HTTP request
        
    Returns:
        JSON response with agent response
    """
    try:
        # Parse request data
        data = await request.json()
        message = data.get('message', '')
        input_type = data.get('type', 'text')  # text, voice, file, canvas
        
        if not message and input_type == 'text':
            return web.json_response({
                'success': False,
                'error': 'Message is required for text input'
            }, status=400)
        
        # Create a unique agent ID
        import uuid
        agent_id = str(uuid.uuid4())
        
        # Create agent
        agent_config = config.get('agents.cody', {})
        agent = CodyAgent(agent_id, 'Cody', agent_config)
        
        # Process message
        if input_type == 'text':
            response = await agent.process_message({
                'content': message,
                'action': 'chat'
            })
        elif input_type == 'voice':
            # In a real implementation, this would process voice input
            response = {
                'success': True,
                'content': 'Voice input processing is not implemented yet.',
                'agent_id': agent_id,
                'agent_name': 'Cody'
            }
        elif input_type == 'file':
            # In a real implementation, this would process file input
            response = {
                'success': True,
                'content': 'File input processing is not implemented yet.',
                'agent_id': agent_id,
                'agent_name': 'Cody'
            }
        elif input_type == 'canvas':
            # In a real implementation, this would process canvas input
            response = {
                'success': True,
                'content': 'Canvas input processing is not implemented yet.',
                'agent_id': agent_id,
                'agent_name': 'Cody'
            }
        else:
            return web.json_response({
                'success': False,
                'error': f"Unknown input type: {input_type}"
            }, status=400)
        
        return web.json_response(response)
    except Exception as e:
        logger.exception(f"Error sending message to agent: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

def setup_routes(app: web.Application) -> None:
    """
    Set up the Cody API routes.
    
    Args:
        app: The aiohttp application
    """
    app.router.add_get('/api/agents/cody', get_agent_details)
    app.router.add_post('/api/agents/cody/benchmarks', get_agent_benchmarks)
    app.router.add_post('/api/agents/cody/performance', get_agent_performance)
    app.router.add_post('/api/agents/cody/message', send_message_to_agent)
    
    logger.info("Cody API routes set up")
