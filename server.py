"""
DMac Server Application.

This module provides a Flask web server for the DMac application.
It handles HTTP requests and serves the web interface.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import asyncio
import logging
from pathlib import Path

# Import configuration and utility modules
from config.config import config
from utils.secure_logging import get_logger
# Remove error_handling import that doesn't exist
# from utils.error_handling import log_error, ErrorCategory, ErrorSeverity

# Import managers - uncomment as implementations are completed
# from database.db_manager import db_manager
# from models.model_manager import model_manager
# from agents.agent_manager import agent_manager
# from tasks.task_manager import task_manager
from langchain_integration.langchain_manager import langchain_manager
from langchain_integration.chat_integration import initialize_langchain, process_message, process_web_scraping

# Create Flask app
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# Set up logger
logger = logging.getLogger("dmac.server")

# Routes for pages
@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    """Render the dashboard page."""
    return render_template("dashboard.html")

@app.route("/agents")
def agents():
    """Render the agents page."""
    try:
        # For now, we will use static data until we implement the LangChain integration
        return render_template("agents.html")
    except Exception as e:
        logger.exception(f"Error rendering agents page: {e}")
        return f"Error: {str(e)}"  # Simple error handling for now

@app.route("/tasks")
def tasks():
    """Render the tasks page."""
    return render_template("tasks.html")

@app.route("/models")
def models():
    """Render the models page."""
    return render_template("models.html")

@app.route("/datasets")
def datasets():
    """Render the datasets page."""
    return render_template("datasets.html")

@app.route("/benchmarks")
def benchmarks():
    """Render the training and benchmarks page."""
    return render_template("benchmarks.html")

@app.route("/settings")
def settings():
    """Render the settings page."""
    return render_template("settings.html")

@app.route("/chat")
def chat():
    """Render the chat page."""
    agent_id = request.args.get("agent", "default")
    return render_template("chat.html", agent_id=agent_id)

@app.route("/agent/<agent_id>")
def agent_dashboard(agent_id):
    """Render the agent dashboard page."""
    try:
        # Get agent details
        agent = get_agent_details(agent_id)
        if not agent:
            return redirect(url_for('agents'))

        return render_template("agent_dashboard.html", agent=agent)
    except Exception as e:
        logger.exception(f"Error rendering agent dashboard page: {e}")
        return f"Error: {str(e)}"  # Simple error handling for now

@app.route("/onboarding")
def onboarding():
    """Render the onboarding page."""
    return render_template("onboarding.html")

# Helper functions
def get_agent_details(agent_id):
    """Get details for a specific agent."""
    # For now, return static data
    agents_data = {
        "cody": {
            "id": "cody",
            "name": "Cody",
            "specialty": "Code Assistant",
            "description": "Native Code Assistant with code completion, vision capabilities, and reinforcement learning integration",
            "status": "active",
            "capabilities": [
                "code_search",
                "code_generation",
                "code_completion",
                "code_explanation",
                "code_refactoring",
                "bug_finding",
                "test_generation",
                "code_documentation",
                "project_analysis",
                "vision_code_understanding",
                "reinforcement_learning"
            ],
            "performance": {
                "tasks_completed": 42,
                "success_rate": "94%",
                "average_response_time": "180ms",
                "memory_usage": "1.4 GB"
            },
            "configuration": {
                "model_name": "GandalfBaum/deepseek_r1-claude3.7:latest",
                "temperature": 0.2,
                "max_context_length": 16384,
                "vision_enabled": True,
                "rl_enabled": True,
                "rl_model": "openManus",
                "code_completion_enabled": True
            }
        },
        "perry": {
            "id": "perry",
            "name": "Perry",
            "specialty": "Project Manager",
            "description": "Perry helps manage projects, track tasks, and coordinate team activities to ensure successful project completion.",
            "status": "active",
            "capabilities": [
                "project_planning",
                "task_tracking",
                "team_coordination",
                "resource_allocation",
                "progress_reporting"
            ],
            "performance": {
                "tasks_completed": 35,
                "success_rate": "92%",
                "average_response_time": "210ms",
                "memory_usage": "1.2 GB"
            },
            "configuration": {
                "model_name": "gemma3:12b",
                "temperature": 0.3,
                "max_context_length": 8192,
                "vision_enabled": False,
                "rl_enabled": True,
                "rl_model": "openManus"
            }
        },
        "shelly": {
            "id": "shelly",
            "name": "Shelly",
            "specialty": "Shell Expert",
            "description": "Shelly is an expert in shell scripting, command-line tools, and system administration tasks.",
            "status": "active",
            "capabilities": [
                "command_generation",
                "script_creation",
                "command_explanation",
                "system_diagnostics",
                "file_operations"
            ],
            "performance": {
                "tasks_completed": 28,
                "success_rate": "89%",
                "average_response_time": "150ms",
                "memory_usage": "1.0 GB"
            },
            "configuration": {
                "model_name": "gemma3:12b",
                "temperature": 0.3,
                "max_context_length": 8192,
                "vision_enabled": False,
                "rl_enabled": True,
                "rl_model": "openManus"
            }
        }
    }

    return agents_data.get(agent_id)

# API routes
@app.route("/api/agents", methods=["GET"])
def get_agents():
    """Get all agents."""
    # For now, return static data
    agents = [
        {
            "id": "cody",
            "name": "Cody",
            "specialty": "Code Assistant",
            "description": "Cody is a specialized code assistant that helps with programming tasks, debugging, and code optimization."
        },
        {
            "id": "perry",
            "name": "Perry",
            "specialty": "Project Manager",
            "description": "Perry helps manage projects, track tasks, and coordinate team activities to ensure successful project completion."
        },
        {
            "id": "shelly",
            "name": "Shelly",
            "specialty": "Shell Expert",
            "description": "Shelly is an expert in shell scripting, command-line tools, and system administration tasks."
        },
        {
            "id": "flora",
            "name": "Flora",
            "specialty": "Data Scientist",
            "description": "Flora specializes in data analysis, visualization, and machine learning to extract insights from data."
        }
    ]
    return jsonify(agents)

# Agent API routes
@app.route("/api/agents/<agent_id>", methods=["GET"])
def api_get_agent_details(agent_id):
    """Get details for a specific agent."""
    agent = get_agent_details(agent_id)
    if not agent:
        return jsonify({"error": f"Agent {agent_id} not found"}), 404

    return jsonify(agent)

@app.route("/api/agents/<agent_id>/benchmarks", methods=["POST"])
def api_get_agent_benchmarks(agent_id):
    """Get benchmarks for a specific agent."""
    agent = get_agent_details(agent_id)
    if not agent:
        return jsonify({"error": f"Agent {agent_id} not found"}), 404

    # Parse request data
    data = request.json or {}
    category = data.get('category', 'all')
    limit = int(data.get('limit', 10))

    # For now, return static data
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

    return jsonify({
        'success': True,
        'benchmarks': benchmarks
    })

@app.route("/api/agents/<agent_id>/performance", methods=["POST"])
def api_get_agent_performance(agent_id):
    """Get performance metrics for a specific agent."""
    agent = get_agent_details(agent_id)
    if not agent:
        return jsonify({"error": f"Agent {agent_id} not found"}), 404

    # Parse request data
    data = request.json or {}
    period = data.get('period', 'week')  # day, week, month, year

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

    return jsonify({
        'success': True,
        'period': period,
        'performance_data': performance_data,
        'task_status': task_status,
        'task_categories': task_categories
    })

@app.route("/api/agents/<agent_id>/message", methods=["POST"])
def api_send_message_to_agent(agent_id):
    """Send a message to a specific agent."""
    agent = get_agent_details(agent_id)
    if not agent:
        return jsonify({"error": f"Agent {agent_id} not found"}), 404

    # Parse request data
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400

    message = data.get('message')
    input_type = data.get('type', 'text')  # text, voice, file, canvas

    # For now, return a static response
    if agent_id == 'cody':
        response = f"I'm Cody, your code assistant. I'll help you with: {message[:50]}..."
    elif agent_id == 'perry':
        response = f"I'm Perry, your project manager. I'll help you manage: {message[:50]}..."
    elif agent_id == 'shelly':
        response = f"I'm Shelly, your shell expert. I'll help you with: {message[:50]}..."
    else:
        response = f"I'm an agent. I'll help you with: {message[:50]}..."

    return jsonify({
        'success': True,
        'content': response,
        'agent_id': agent_id,
        'agent_name': agent.get('name')
    })

# New API routes for LangChain integration
@app.route("/api/chat", methods=["POST"])
async def api_chat():
    """Process a chat message using LangChain."""
    try:
        data = request.json
        message = data.get("message", "")
        agent_id = data.get("agent_id", None)

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Process the message using LangChain
        response = await process_message(message, agent_id)

        return jsonify({
            "response": response,
            "agent_id": agent_id or "default"
        })
    except Exception as e:
        logger.exception(f"Error processing chat message: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/web-scrape", methods=["POST"])
async def api_web_scrape():
    """Process a web scraping request."""
    try:
        data = request.json
        url = data.get("url", "")
        depth = data.get("depth", 1)
        max_pages = data.get("max_pages", 10)

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        # Process the web scraping request using LangChain
        response = await process_web_scraping(url, depth, max_pages)

        return jsonify({
            "response": response,
            "url": url,
            "depth": depth,
            "max_pages": max_pages
        })
    except Exception as e:
        logger.exception(f"Error processing web scraping request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools", methods=["GET"])
def api_tools():
    """Get available tools."""
    try:
        from langchain_integration.chat_integration import get_available_tools
        tools = get_available_tools()
        return jsonify(tools)
    except Exception as e:
        logger.exception(f"Error getting available tools: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/benchmarks", methods=["GET"])
def get_benchmarks():
    """Get all benchmark results."""
    # This would typically fetch data from the database
    # For now, return static data
    benchmarks = [
        {
            "id": "benchmark_1",
            "name": "Question Answering",
            "description": "Benchmark for question answering tasks",
            "results": [
                {
                    "agent_id": "cody",
                    "model": "ollama:llama2",
                    "score": 0.85,
                    "timestamp": "2023-04-07T12:00:00Z"
                },
                {
                    "agent_id": "flora",
                    "model": "ollama:llama2",
                    "score": 0.92,
                    "timestamp": "2023-04-07T12:30:00Z"
                }
            ]
        },
        {
            "id": "benchmark_2",
            "name": "Web Search",
            "description": "Benchmark for web search tasks",
            "results": [
                {
                    "agent_id": "cody",
                    "model": "ollama:llama2",
                    "score": 0.78,
                    "timestamp": "2023-04-07T13:00:00Z"
                },
                {
                    "agent_id": "flora",
                    "model": "ollama:llama2",
                    "score": 0.88,
                    "timestamp": "2023-04-07T13:30:00Z"
                }
            ]
        }
    ]
    return jsonify(benchmarks)

@app.route("/api/datasets", methods=["GET"])
def get_datasets():
    """Get all datasets."""
    # This would typically fetch data from the database
    # For now, return static data
    datasets = [
        {
            "id": "dataset_1",
            "name": "Web Search Dataset",
            "description": "Dataset for training web search agents",
            "size": 1000,
            "created_at": "2023-04-07T10:00:00Z"
        },
        {
            "id": "dataset_2",
            "name": "Code Completion Dataset",
            "description": "Dataset for training code completion agents",
            "size": 5000,
            "created_at": "2023-04-07T11:00:00Z"
        }
    ]
    return jsonify(datasets)

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Get all tasks."""
    # This would typically fetch data from the database
    # For now, return static data
    tasks = [
        {
            "id": "task_1",
            "name": "Research Python Libraries",
            "description": "Research and document popular Python libraries for data science",
            "status": "in_progress",
            "assigned_to": "flora",
            "due_date": "2023-04-15T00:00:00Z",
            "created_at": "2023-04-07T09:00:00Z"
        },
        {
            "id": "task_2",
            "name": "Optimize Database Queries",
            "description": "Optimize database queries for better performance",
            "status": "pending",
            "assigned_to": "cody",
            "due_date": "2023-04-20T00:00:00Z",
            "created_at": "2023-04-07T10:00:00Z"
        },
        {
            "id": "task_3",
            "name": "Create Project Timeline",
            "description": "Create a timeline for the project with milestones",
            "status": "completed",
            "assigned_to": "perry",
            "due_date": "2023-04-10T00:00:00Z",
            "created_at": "2023-04-05T14:00:00Z",
            "completed_at": "2023-04-09T16:30:00Z"
        }
    ]
    return jsonify(tasks)

# Initialize the application
async def init_app():
    """Initialize the application."""
    try:
        # Initialize LangChain
        await initialize_langchain()

        logger.info("Application initialized successfully")
    except Exception as e:
        logger.exception(f"Error initializing application: {e}")
        raise

# Run the application
if __name__ == "__main__":
    # Run the initialization
    asyncio.run(init_app())

    # Run the Flask app
    app.run(host="0.0.0.0", port=1300, debug=True)
