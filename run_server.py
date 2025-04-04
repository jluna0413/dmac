"""
DMac Server Runner.

This script starts a simplified server for testing the DMac WebArena dashboard.
"""

import argparse
import logging
import os
import sys
import json
import time
import asyncio
from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web

from database import db_manager
from integrations import ollama_client, webarena_client, web_scraper, voice_interaction
from tasks import task_executor, get_all_tasks, get_task_by_id
from api.web_research_api import setup_routes as setup_web_research_routes
from api.opencanvas_api import setup_routes as setup_opencanvas_routes

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('dmac.run_server')

class SimpleDashboardServer:
    """Simple server for the DMac dashboard."""

    def __init__(self):
        """Initialize the dashboard server."""
        # Configuration
        self.host = '0.0.0.0'
        self.port = 8080
        self.static_dir = Path('dashboard/static')
        self.templates_dir = Path('dashboard/templates')

        # Create directories if they don't exist
        os.makedirs(self.static_dir, exist_ok=True)

        # Initialize the application
        self.app = None
        self.runner = None
        self.site = None

        logger.info("Dashboard server initialized")

    async def start(self):
        """Start the dashboard server."""
        try:
            # Create the application
            self.app = web.Application()

            # Set up Jinja2 templates
            aiohttp_jinja2.setup(
                self.app,
                loader=jinja2.FileSystemLoader(str(self.templates_dir))
            )

            # Set up static routes
            self.app.router.add_static('/static', str(self.static_dir))

            # Initialize the database and integrations
            await db_manager.initialize()
            await ollama_client.initialize()
            await webarena_client.initialize()

            # Set up dashboard routes
            self._setup_dashboard_routes()

            # Set up API routes
            self._setup_api_routes()

            # Start the server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()

            logger.info(f"Dashboard server started on http://{self.host}:{self.port}")
            logger.info(f"WebArena dashboard available at http://{self.host}:{self.port}/webarena/dashboard")

            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.exception(f"Error starting dashboard server: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the dashboard server."""
        logger.info("Stopping dashboard server")

        if self.site:
            await self.site.stop()
            self.site = None

        if self.runner:
            await self.runner.cleanup()
            self.runner = None

        self.app = None

        # Clean up the database and integrations
        await db_manager.cleanup()
        await ollama_client.cleanup()
        await webarena_client.cleanup()

        logger.info("Dashboard server stopped")

    def _setup_dashboard_routes(self):
        """Set up dashboard routes."""
        # Add the routes
        self.app.router.add_get('/', self._handle_index)
        self.app.router.add_get('/login', self._handle_login)
        self.app.router.add_get('/direct-login', self._handle_direct_login)
        self.app.router.add_get('/register', self._handle_register)
        self.app.router.add_get('/forgot-password', self._handle_forgot_password)
        self.app.router.add_get('/dashboard', self._handle_dashboard)
        self.app.router.add_get('/agents', self._handle_agents)
        self.app.router.add_get('/tasks', self._handle_tasks)
        self.app.router.add_get('/models', self._handle_models)
        self.app.router.add_get('/webarena', self._handle_webarena)
        self.app.router.add_get('/webarena/dashboard', self._handle_webarena_dashboard)
        self.app.router.add_get('/webarena/runs', self._handle_webarena_runs)
        self.app.router.add_get('/webarena/runs/{run_id}', self._handle_webarena_run_details)
        self.app.router.add_get('/webarena/visualizations', self._handle_webarena_visualizations)
        self.app.router.add_get('/settings', self._handle_settings)
        self.app.router.add_get('/task-runner', self._handle_task_runner)
        self.app.router.add_get('/chat', self._handle_chat)

        logger.info("Dashboard routes set up")

    def _setup_api_routes(self):
        """Set up API routes."""
        # Add mock API routes for testing
        self.app.router.add_get('/api/webarena/tasks', self._handle_api_tasks)
        self.app.router.add_get('/api/webarena/models', self._handle_api_models)
        self.app.router.add_get('/api/webarena/runs', self._handle_api_runs)
        self.app.router.add_post('/api/webarena/runs', self._handle_api_create_run)
        self.app.router.add_get('/api/agents/webarena', self._handle_api_agents)
        self.app.router.add_post('/api/agents/webarena', self._handle_api_create_agent)
        self.app.router.add_get('/api/ollama/models', self._handle_api_ollama_models)

        # Add new task API routes
        self.app.router.add_get('/api/tasks/all', self._handle_api_all_tasks)
        self.app.router.add_post('/api/tasks/execute', self._handle_api_execute_task)
        self.app.router.add_post('/api/tasks/execute_all', self._handle_api_execute_all_tasks)

        # Add voice interaction API routes
        self.app.router.add_post('/api/voice/process', self._handle_api_voice_process)
        self.app.router.add_post('/api/voice/speech-to-text', self._handle_api_speech_to_text)
        self.app.router.add_post('/api/voice/text-to-speech', self._handle_api_text_to_speech)

        # Add chat API routes
        self.app.router.add_post('/api/chat/message', self._handle_api_chat_message)

        # Add web research API routes
        setup_web_research_routes(self.app)

        # Add OpenCanvas API routes
        setup_opencanvas_routes(self.app)

        logger.info("API routes set up")

    @aiohttp_jinja2.template('index.html')
    async def _handle_index(self, request):
        """Handle a request to the index page."""
        return {
            'title': 'DMac - AI Agent Swarm',
            'page': 'index',
        }

    @aiohttp_jinja2.template('login.html')
    async def _handle_login(self, request):
        """Handle a request to the login page."""
        return {
            'title': 'DMac - Login',
            'page': 'login',
        }

    @aiohttp_jinja2.template('direct_login.html')
    async def _handle_direct_login(self, request):
        """Handle a request to the direct login page."""
        return {
            'title': 'DMac - Direct Login',
            'page': 'direct_login',
        }

    @aiohttp_jinja2.template('dashboard.html')
    async def _handle_dashboard(self, request):
        """Handle a request to the dashboard page."""
        return {
            'title': 'DMac - Dashboard',
            'page': 'dashboard',
        }

    @aiohttp_jinja2.template('agents.html')
    async def _handle_agents(self, request):
        """Handle a request to the agents page."""
        return {
            'title': 'DMac - Agents',
            'page': 'agents',
        }

    @aiohttp_jinja2.template('tasks.html')
    async def _handle_tasks(self, request):
        """Handle a request to the tasks page."""
        return {
            'title': 'DMac - Tasks',
            'page': 'tasks',
        }

    @aiohttp_jinja2.template('models.html')
    async def _handle_models(self, request):
        """Handle a request to the models page."""
        return {
            'title': 'DMac - Models',
            'page': 'models',
        }

    @aiohttp_jinja2.template('webarena.html')
    async def _handle_webarena(self, request):
        """Handle a request to the WebArena page."""
        return {
            'title': 'DMac - WebArena',
            'page': 'webarena',
        }

    @aiohttp_jinja2.template('webarena_dashboard.html')
    async def _handle_webarena_dashboard(self, request):
        """Handle a request to the WebArena dashboard page."""
        return {
            'title': 'DMac - WebArena Dashboard',
            'page': 'webarena_dashboard',
        }

    @aiohttp_jinja2.template('webarena_runs.html')
    async def _handle_webarena_runs(self, request):
        """Handle a request to the WebArena runs page."""
        return {
            'title': 'DMac - WebArena Runs',
            'page': 'webarena_runs',
        }

    @aiohttp_jinja2.template('webarena_run_details.html')
    async def _handle_webarena_run_details(self, request):
        """Handle a request to the WebArena run details page."""
        run_id = request.match_info.get('run_id')
        return {
            'title': f'DMac - WebArena Run {run_id}',
            'page': 'webarena_run_details',
            'run_id': run_id,
        }

    @aiohttp_jinja2.template('webarena_visualizations.html')
    async def _handle_webarena_visualizations(self, request):
        """Handle a request to the WebArena visualizations page."""
        return {
            'title': 'DMac - WebArena Visualizations',
            'page': 'webarena_visualizations',
        }

    @aiohttp_jinja2.template('settings.html')
    async def _handle_settings(self, request):
        """Handle a request to the settings page."""
        return {
            'title': 'DMac - Settings',
            'page': 'settings',
        }

    @aiohttp_jinja2.template('task_runner.html')
    async def _handle_task_runner(self, request):
        """Handle a request to the task runner page."""
        return {
            'title': 'DMac - Task Runner',
            'page': 'task_runner',
        }

    @aiohttp_jinja2.template('chat.html')
    async def _handle_chat(self, request):
        """Handle a request to the chat page."""
        return {
            'title': 'DMac - Chat',
            'page': 'chat',
        }

    @aiohttp_jinja2.template('register.html')
    async def _handle_register(self, request):
        """Handle a request to the registration page."""
        return {
            'title': 'DMac - Register',
        }

    @aiohttp_jinja2.template('forgot-password.html')
    async def _handle_forgot_password(self, request):
        """Handle a request to the forgot password page."""
        return {
            'title': 'DMac - Forgot Password',
        }

    async def _handle_api_tasks(self, request):
        """Handle a request to the tasks API."""
        # Get tasks from the database
        tasks = await db_manager.get_tasks()

        # If there are no tasks, add some default WebArena tasks
        if not tasks:
            # Get WebArena tasks
            webarena_tasks = await webarena_client.get_tasks()

            # Create tasks in the database
            for task in webarena_tasks[:5]:  # Limit to 5 tasks for now
                await db_manager.create_task(
                    name=task['name'],
                    description=task['description'],
                    task_type='webarena',
                    status='pending',
                    data={
                        'website': task['website'],
                        'webarena_task_id': task['id'],
                        'webarena_task_type': task['type']
                    }
                )

            # Get the tasks again
            tasks = await db_manager.get_tasks()

        # Format the tasks for the API response
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                'id': task['id'],
                'name': task['name'],
                'description': task['description'],
                'type': task['type'],
                'status': task['status'],
                'created_at': task['created_at'],
                'updated_at': task['updated_at']
            })

        return web.json_response({
            'tasks': formatted_tasks
        })

    async def _handle_api_models(self, request):
        """Handle a request to the models API."""
        # Return mock models
        return web.json_response({
            'models': [
                {'name': 'llama2', 'description': 'Ollama model: llama2', 'type': 'ollama'},
                {'name': 'mistral', 'description': 'Ollama model: mistral', 'type': 'ollama'},
                {'name': 'gemma:2b', 'description': 'Ollama model: gemma:2b', 'type': 'ollama'},
            ]
        })

    async def _handle_api_runs(self, request):
        """Handle a request to the runs API."""
        # Get runs from the database
        runs = await db_manager.get_runs()

        # If there are no runs, get WebArena results
        if not runs:
            # Get WebArena results
            webarena_results = await webarena_client.get_results()

            # Create runs in the database
            for result in webarena_results[:5]:  # Limit to 5 results for now
                # Get the task ID
                tasks = await db_manager.get_tasks()
                task_id = None

                for task in tasks:
                    if task.get('data', {}).get('webarena_task_id') == result.get('task_id'):
                        task_id = task['id']
                        break

                if task_id:
                    # Create a run
                    await db_manager.create_run(
                        task_id=task_id,
                        model=result.get('model', 'unknown'),
                        status='completed' if result.get('success') else 'failed',
                        result=f"Success: {result.get('success')}, Steps: {result.get('steps')}",
                        data=result
                    )

            # Get the runs again
            runs = await db_manager.get_runs()

        # Format the runs for the API response
        formatted_runs = []
        for run in runs:
            # Get the task name
            task = await db_manager.get_task(run['task_id'])
            task_name = task['name'] if task else 'Unknown Task'

            formatted_runs.append({
                'id': run['id'],
                'task_id': run['task_id'],
                'task_name': task_name,
                'model_name': run['model'],
                'status': run['status'],
                'created_at': run['created_at'],
                'updated_at': run['updated_at'],
                'result': run['result']
            })

        return web.json_response({
            'runs': formatted_runs
        })

    async def _handle_api_create_run(self, request):
        """Handle a request to create a run."""
        # Parse the request body
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Get the run parameters
        task_id = body.get('task_id')
        model_name = body.get('model_name')

        if not task_id or not model_name:
            return web.json_response({
                'success': False,
                'error': 'Missing task_id or model_name'
            }, status=400)

        # Get the task
        task = await db_manager.get_task(task_id)
        if not task:
            return web.json_response({
                'success': False,
                'error': f'Task {task_id} not found'
            }, status=404)

        # Get the WebArena task ID
        webarena_task_id = task.get('data', {}).get('webarena_task_id')
        if not webarena_task_id:
            return web.json_response({
                'success': False,
                'error': f'Task {task_id} is not a WebArena task'
            }, status=400)

        # Run the WebArena task
        run_id = await webarena_client.run_task(webarena_task_id, model_name)
        if not run_id:
            return web.json_response({
                'success': False,
                'error': f'Failed to run WebArena task {webarena_task_id} with model {model_name}'
            }, status=500)

        # Create a run in the database
        db_run_id = await db_manager.create_run(
            task_id=task_id,
            model=model_name,
            status='running',
            data={
                'webarena_run_id': run_id
            }
        )

        if not db_run_id:
            return web.json_response({
                'success': False,
                'error': f'Failed to create run in database'
            }, status=500)

        return web.json_response({
            'success': True,
            'run_id': db_run_id,
            'message': f'Started WebArena run for task {task["name"]} with model {model_name}',
        })

    async def _handle_api_agents(self, request):
        """Handle a request to the agents API."""
        # Return mock agents
        return web.json_response({
            'agents': [
                {'id': 'agent_1', 'name': 'WebArena Agent 1', 'type': 'webarena', 'current_run_id': 'run_2'},
                {'id': 'agent_2', 'name': 'WebArena Agent 2', 'type': 'webarena', 'current_run_id': None},
            ]
        })

    async def _handle_api_create_agent(self, request):
        """Handle a request to create an agent."""
        # Parse the request body
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Get the agent name
        name = body.get('name', 'New WebArena Agent')

        # Return a mock agent
        return web.json_response({
            'agent_id': f'agent_{int(asyncio.get_event_loop().time())}',
            'name': name,
            'type': 'webarena',
        })

    async def _handle_api_ollama_models(self, request):
        """Handle a request to get Ollama models."""
        # Get models from Ollama
        models = await ollama_client.get_models()

        # Add API models
        models.append({
            'name': 'gemini-pro',
            'size': 'N/A',
            'status': 'Available',
            'source': 'api'
        })

        return web.json_response({
            'success': True,
            'models': models
        })

    async def _handle_api_all_tasks(self, request):
        """Handle a request to get all available tasks."""
        # Get all tasks
        tasks = get_all_tasks()

        return web.json_response({
            'success': True,
            'tasks': tasks
        })

    async def _handle_api_execute_task(self, request):
        """Handle a request to execute a task."""
        # Parse the request body
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Get the task parameters
        task_id = body.get('task_id')
        model = body.get('model')

        if not task_id or not model:
            return web.json_response({
                'success': False,
                'error': 'Missing task_id or model'
            }, status=400)

        # Execute the task
        try:
            result = await task_executor.execute_task(task_id, model)

            # Store the result in the database
            run_id = await task_executor._store_run_result(task_id, model, result)

            if run_id:
                logger.info(f"Stored run result for task {task_id} with model {model}, run ID: {run_id}")
            else:
                logger.warning(f"Failed to store run result for task {task_id} with model {model}")

            return web.json_response({
                'success': True,
                'run_id': run_id,
                'result': result
            })
        except Exception as e:
            logger.exception(f"Error executing task {task_id} with model {model}: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def _handle_api_execute_all_tasks(self, request):
        """Handle a request to execute all tasks with a model."""
        # Parse the request body
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Get the model parameter
        model = body.get('model')

        if not model:
            return web.json_response({
                'success': False,
                'error': 'Missing model'
            }, status=400)

        # Execute all tasks with the model
        try:
            # Start a background task to execute all tasks
            asyncio.create_task(task_executor.execute_all_tasks_with_model(model))

            return web.json_response({
                'success': True,
                'message': f"Started executing all tasks with model {model}"
            })
        except Exception as e:
            logger.exception(f"Error executing all tasks with model {model}: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def _handle_api_voice_process(self, request):
        """Handle a request to process voice input."""
        # Parse the request body
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Get the parameters
        text = body.get('text')
        model = body.get('model')

        if not text or not model:
            return web.json_response({
                'success': False,
                'error': 'Missing text or model'
            }, status=400)

        try:
            # Generate a response using the model
            result = await ollama_client.generate(model, text)

            if 'error' in result:
                return web.json_response({
                    'success': False,
                    'error': result['error']
                }, status=500)

            response_text = result.get('text', "I'm sorry, I couldn't generate a response.")

            return web.json_response({
                'success': True,
                'response': response_text,
                'model': model
            })
        except Exception as e:
            logger.exception(f"Error processing voice input: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def _handle_api_speech_to_text(self, request):
        """Handle a request to convert speech to text."""
        # Parse the request body
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Get the parameters
        audio_file = body.get('audio_file')
        timeout = body.get('timeout', 5)

        try:
            # Convert speech to text
            result = await voice_interaction.speech_to_text(audio_file, timeout)

            return web.json_response(result)
        except Exception as e:
            logger.exception(f"Error converting speech to text: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def _handle_api_text_to_speech(self, request):
        """Handle a request to convert text to speech."""
        # Parse the request body
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Get the parameters
        text = body.get('text')
        output_file = body.get('output_file')

        if not text:
            return web.json_response({
                'success': False,
                'error': 'Missing text'
            }, status=400)

        try:
            # Convert text to speech
            result = await voice_interaction.text_to_speech(text, output_file)

            return web.json_response(result)
        except Exception as e:
            logger.exception(f"Error converting text to speech: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def _handle_api_chat_message(self, request):
        """Handle a request to process a chat message."""
        # Parse the request body
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Get the parameters
        message = body.get('message', '')
        model = body.get('model')
        files = body.get('files', [])
        deep_research = body.get('deep_research', False)
        deep_thinking = body.get('deep_thinking', False)
        instructions = body.get('instructions', {})

        if not model:
            return web.json_response({
                'success': False,
                'error': 'Missing model'
            }, status=400)

        try:
            # Prepare the prompt
            prompt = message

            # Add file content to the prompt if any
            if files and len(files) > 0:
                prompt += "\n\nI'm also sending you the following files:\n"

                for file in files:
                    file_name = file.get('name', 'unnamed_file')
                    file_type = file.get('type', 'unknown')
                    file_content = file.get('content', '')

                    prompt += f"\n--- File: {file_name} (Type: {file_type}) ---\n"

                    # For text files, include the content directly
                    if file_type.startswith('text/') or file_type.endswith('/json') or file_type.endswith('/xml'):
                        prompt += f"\n{file_content}\n"
                    else:
                        prompt += "\n[Binary file content not included]\n"

                    prompt += "\n--- End of file ---\n"

            # Perform web research if requested
            web_research_results = None
            if deep_research or instructions.get('use_web_search', False):
                from utils.web_research import WebResearch
                web_researcher = WebResearch()

                # Research the topic
                success, research_data = await asyncio.to_thread(
                    web_researcher.research_topic,
                    message,
                    max_sources=3
                )

                if success:
                    web_research_results = research_data

                    # Add research results to the prompt
                    prompt += "\n\n--- Web Research Results ---\n"
                    prompt += "I've conducted research on your query and found the following information:\n"

                    for i, source in enumerate(research_data.get('sources', []), 1):
                        prompt += f"\nSource {i}: {source.get('title', 'Untitled')}\n"
                        prompt += f"URL: {source.get('url', '')}\n"

                        # Add a snippet of the content
                        content = source.get('content', '')
                        if content:
                            # Limit content length to avoid token limits
                            max_content_length = 1000
                            if len(content) > max_content_length:
                                content = content[:max_content_length] + "..."
                            prompt += f"Content: {content}\n"

                    prompt += "\n--- End of Web Research Results ---\n"
                    prompt += "\nPlease use this research to provide an accurate and up-to-date response.\n"

            # Add instructions for deep thinking
            if deep_thinking:
                prompt = "Please think deeply about this problem and provide a detailed, step-by-step solution: " + prompt

            # Add anti-hallucination instructions
            if instructions.get('prevent_hallucinations', False):
                prompt += "\n\n--- Important Instructions ---\n"
                prompt += "1. Only provide information that you are confident is accurate.\n"
                prompt += "2. If you're unsure about something, explicitly state your uncertainty.\n"
                prompt += "3. Do not make up facts or information.\n"
                prompt += "4. If you don't know the answer, say so clearly.\n"
                prompt += "5. Base your response on verifiable information only.\n"
                prompt += "--- End of Instructions ---\n"

            # Generate a response using the model
            result = await ollama_client.generate(model, prompt)

            if 'error' in result:
                return web.json_response({
                    'success': False,
                    'error': result['error']
                }, status=500)

            response_text = result.get('text', "I'm sorry, I couldn't generate a response.")

            # Prepare the response data
            response_data = {
                'success': True,
                'response': response_text,
                'model': model
            }

            # Include research metadata if available
            if web_research_results:
                response_data['research_metadata'] = {
                    'sources_count': len(web_research_results.get('sources', [])),
                    'query': web_research_results.get('query', ''),
                    'sources': [{
                        'title': s.get('title', 'Untitled'),
                        'url': s.get('url', '')
                    } for s in web_research_results.get('sources', [])]
                }

            return web.json_response(response_data)
        except Exception as e:
            logger.exception(f"Error processing chat message: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

async def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the DMac dashboard server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the server on')
    args = parser.parse_args()

    # Create and start the server
    server = SimpleDashboardServer()
    server.port = args.port
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
