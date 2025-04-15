"""
Benchmark Manager for DMac.

This module provides functionality for benchmarking agents and models,
tracking performance metrics, and generating leaderboards.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from utils.secure_logging import get_logger
from config.config import config
from models.model_provider import OllamaModelProvider

logger = get_logger('dmac.benchmarking.manager')

class BenchmarkManager:
    """Manager for benchmarking agents and models."""

    def __init__(self):
        """Initialize the benchmark manager."""
        # Load configuration
        self.config = {
            'benchmarks_dir': config.get('benchmarking.benchmarks_dir', os.path.join('data', 'benchmarks')),
            'results_dir': config.get('benchmarking.results_dir', os.path.join('data', 'benchmark_results')),
            'leaderboards_dir': config.get('benchmarking.leaderboards_dir', os.path.join('data', 'leaderboards')),
            'default_timeout': config.get('benchmarking.default_timeout', 300),  # 5 minutes
            'default_metrics': config.get('benchmarking.default_metrics', ['accuracy', 'latency', 'tokens_per_second']),
            'available_models': config.get('benchmarking.available_models', []),
            'benchmark_categories': config.get('benchmarking.categories', [
                'code_generation', 'prompt_engineering', 'shell_scripting', 'frontend_development'
            ])
        }

        # Create directories if they don't exist
        os.makedirs(self.config['benchmarks_dir'], exist_ok=True)
        os.makedirs(self.config['results_dir'], exist_ok=True)
        os.makedirs(self.config['leaderboards_dir'], exist_ok=True)

        # Create category directories
        for category in self.config['benchmark_categories']:
            os.makedirs(os.path.join(self.config['benchmarks_dir'], category), exist_ok=True)
            os.makedirs(os.path.join(self.config['results_dir'], category), exist_ok=True)

        # Load available models if not provided in config
        if not self.config['available_models']:
            self.config['available_models'] = self._discover_available_models()

        logger.info(f"Benchmark manager initialized with {len(self.config['available_models'])} available models")

    def _discover_available_models(self) -> List[str]:
        """Discover available models from Ollama.

        Returns:
            List of available model names
        """
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                models_data = response.json()
                return [model['name'] for model in models_data.get('models', [])]
            else:
                logger.warning(f"Failed to get models from Ollama API: {response.status_code}")
                return ['gemma:7b', 'llama3:8b', 'mistral:7b']  # Default fallback
        except Exception as e:
            logger.error(f"Error discovering models: {str(e)}")
            return ['gemma:7b', 'llama3:8b', 'mistral:7b']  # Default fallback

    async def list_benchmarks(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available benchmarks.

        Args:
            category: Optional category to filter benchmarks

        Returns:
            List of benchmark metadata
        """
        benchmarks = []

        if category:
            # List benchmarks for a specific category
            category_dir = os.path.join(self.config['benchmarks_dir'], category)
            if os.path.exists(category_dir):
                for filename in os.listdir(category_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(category_dir, filename), 'r') as f:
                                benchmark_data = json.load(f)
                                benchmarks.append(benchmark_data)
                        except Exception as e:
                            logger.error(f"Error loading benchmark {filename}: {str(e)}")
        else:
            # List all benchmarks across categories
            for category in self.config['benchmark_categories']:
                category_dir = os.path.join(self.config['benchmarks_dir'], category)
                if os.path.exists(category_dir):
                    for filename in os.listdir(category_dir):
                        if filename.endswith('.json'):
                            try:
                                with open(os.path.join(category_dir, filename), 'r') as f:
                                    benchmark_data = json.load(f)
                                    benchmarks.append(benchmark_data)
                            except Exception as e:
                                logger.error(f"Error loading benchmark {filename}: {str(e)}")

        return benchmarks

    async def create_benchmark(self,
                              name: str,
                              category: str,
                              description: str,
                              tasks: List[Dict[str, Any]],
                              evaluation_criteria: Dict[str, Any],
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new benchmark.

        Args:
            name: Name of the benchmark
            category: Category of the benchmark
            description: Description of the benchmark
            tasks: List of tasks for the benchmark
            evaluation_criteria: Criteria for evaluating benchmark results
            metadata: Additional metadata for the benchmark

        Returns:
            Created benchmark data
        """
        if category not in self.config['benchmark_categories']:
            raise ValueError(f"Invalid category: {category}")

        # Generate a benchmark ID
        benchmark_id = f"{category}_{name.lower().replace(' ', '_')}_{int(time.time())}"

        # Create benchmark data
        benchmark_data = {
            'id': benchmark_id,
            'name': name,
            'category': category,
            'description': description,
            'tasks': tasks,
            'evaluation_criteria': evaluation_criteria,
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # Save benchmark to file
        benchmark_file = os.path.join(self.config['benchmarks_dir'], category, f"{benchmark_id}.json")
        with open(benchmark_file, 'w') as f:
            json.dump(benchmark_data, f, indent=2)

        logger.info(f"Created benchmark: {benchmark_id}")

        return benchmark_data

    async def run_benchmark(self,
                           benchmark_id: str,
                           agent_id: str,
                           model_name: str,
                           timeout: Optional[int] = None) -> Dict[str, Any]:
        """Run a benchmark for a specific agent and model.

        Args:
            benchmark_id: ID of the benchmark to run
            agent_id: ID of the agent to benchmark
            model_name: Name of the model to use
            timeout: Timeout in seconds (defaults to config value)

        Returns:
            Benchmark results
        """
        # Find the benchmark file
        benchmark_file = None
        for category in self.config['benchmark_categories']:
            category_dir = os.path.join(self.config['benchmarks_dir'], category)
            if os.path.exists(category_dir):
                for filename in os.listdir(category_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(category_dir, filename), 'r') as f:
                                data = json.load(f)
                                if data.get('id') == benchmark_id:
                                    benchmark_file = os.path.join(category_dir, filename)
                                    break
                        except Exception as e:
                            logger.error(f"Error loading benchmark {filename}: {str(e)}")
            if benchmark_file:
                break

        if not benchmark_file:
            raise ValueError(f"Benchmark not found: {benchmark_id}")

        # Load the benchmark
        with open(benchmark_file, 'r') as f:
            benchmark_data = json.load(f)

        # Get the agent class
        agent_class = self._get_agent_class(agent_id)
        if not agent_class:
            raise ValueError(f"Agent not found: {agent_id}")

        # Initialize the agent with the specified model
        agent = agent_class(agent_id=agent_id, config={'model_name': model_name})

        # Set timeout
        if timeout is None:
            timeout = self.config['default_timeout']

        # Run the benchmark tasks
        results = []
        total_latency = 0
        total_tokens = 0

        for task_index, task in enumerate(benchmark_data['tasks']):
            task_id = f"{benchmark_id}_task_{task_index}"
            task_start_time = time.time()

            try:
                # Execute the task with timeout
                task_result = await asyncio.wait_for(
                    agent.execute_task({
                        'task_id': task_id,
                        'type': task['type'],
                        'data': task['data']
                    }),
                    timeout=timeout
                )

                task_end_time = time.time()
                task_latency = task_end_time - task_start_time

                # Evaluate the result
                evaluation = await self._evaluate_task_result(
                    task_result,
                    task.get('expected_result'),
                    benchmark_data['evaluation_criteria']
                )

                # Calculate tokens if available
                tokens = task_result.get('tokens', 0)
                if tokens > 0:
                    tokens_per_second = tokens / task_latency
                else:
                    tokens_per_second = 0

                # Add to totals
                total_latency += task_latency
                total_tokens += tokens

                # Store the result
                results.append({
                    'task_id': task_id,
                    'success': task_result.get('success', False),
                    'latency': task_latency,
                    'tokens': tokens,
                    'tokens_per_second': tokens_per_second,
                    'evaluation': evaluation,
                    'result': task_result.get('result', '')
                })

            except asyncio.TimeoutError:
                # Task timed out
                results.append({
                    'task_id': task_id,
                    'success': False,
                    'latency': timeout,
                    'tokens': 0,
                    'tokens_per_second': 0,
                    'evaluation': {
                        'score': 0,
                        'reason': f"Task timed out after {timeout} seconds"
                    },
                    'result': "Timeout"
                })

                total_latency += timeout

            except Exception as e:
                # Task failed with an error
                results.append({
                    'task_id': task_id,
                    'success': False,
                    'latency': time.time() - task_start_time,
                    'tokens': 0,
                    'tokens_per_second': 0,
                    'evaluation': {
                        'score': 0,
                        'reason': f"Error: {str(e)}"
                    },
                    'result': f"Error: {str(e)}"
                })

                total_latency += time.time() - task_start_time

        # Calculate overall metrics
        num_tasks = len(benchmark_data['tasks'])
        successful_tasks = sum(1 for r in results if r['success'])
        average_score = sum(r['evaluation'].get('score', 0) for r in results) / num_tasks

        # Create benchmark result
        benchmark_result = {
            'benchmark_id': benchmark_id,
            'agent_id': agent_id,
            'model_name': model_name,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'accuracy': successful_tasks / num_tasks,
                'average_score': average_score,
                'total_latency': total_latency,
                'average_latency': total_latency / num_tasks,
                'total_tokens': total_tokens,
                'tokens_per_second': total_tokens / total_latency if total_latency > 0 else 0
            },
            'task_results': results
        }

        # Save the result
        result_file = os.path.join(
            self.config['results_dir'],
            benchmark_data['category'],
            f"{benchmark_id}_{agent_id}_{model_name}_{int(time.time())}.json"
        )

        with open(result_file, 'w') as f:
            json.dump(benchmark_result, f, indent=2)

        # Update leaderboards
        await self._update_leaderboards(benchmark_data['category'], benchmark_id, benchmark_result)

        logger.info(f"Completed benchmark {benchmark_id} for agent {agent_id} with model {model_name}")

        return benchmark_result

    async def get_leaderboard(self, category: str, benchmark_id: Optional[str] = None) -> Dict[str, Any]:
        """Get the leaderboard for a category or specific benchmark.

        Args:
            category: Category to get leaderboard for
            benchmark_id: Optional specific benchmark ID

        Returns:
            Leaderboard data
        """
        if benchmark_id:
            # Get leaderboard for a specific benchmark
            leaderboard_file = os.path.join(self.config['leaderboards_dir'], f"{benchmark_id}_leaderboard.json")
            if os.path.exists(leaderboard_file):
                with open(leaderboard_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'benchmark_id': benchmark_id,
                    'entries': []
                }
        else:
            # Get leaderboard for a category
            leaderboard_file = os.path.join(self.config['leaderboards_dir'], f"{category}_leaderboard.json")
            if os.path.exists(leaderboard_file):
                with open(leaderboard_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'category': category,
                    'entries': []
                }

    async def _evaluate_task_result(self,
                                   result: Dict[str, Any],
                                   expected_result: Optional[Any],
                                   evaluation_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a task result against expected result and criteria.

        Args:
            result: Task result to evaluate
            expected_result: Expected result (if available)
            evaluation_criteria: Criteria for evaluation

        Returns:
            Evaluation result
        """
        # Default evaluation
        evaluation = {
            'score': 0,
            'reason': "No evaluation performed"
        }

        # Check if task was successful
        if not result.get('success', False):
            evaluation['score'] = 0
            evaluation['reason'] = "Task failed"
            return evaluation

        # If there's an expected result, compare directly
        if expected_result is not None:
            if isinstance(expected_result, str) and isinstance(result.get('result'), str):
                # For string results, use similarity scoring
                similarity = self._calculate_string_similarity(result.get('result', ''), expected_result)
                evaluation['score'] = similarity
                if similarity > 0.9:
                    evaluation['reason'] = "Excellent match with expected result"
                elif similarity > 0.7:
                    evaluation['reason'] = "Good match with expected result"
                elif similarity > 0.5:
                    evaluation['reason'] = "Partial match with expected result"
                else:
                    evaluation['reason'] = "Poor match with expected result"
            else:
                # For other types, use direct comparison
                if result.get('result') == expected_result:
                    evaluation['score'] = 1.0
                    evaluation['reason'] = "Exact match with expected result"
                else:
                    evaluation['score'] = 0.0
                    evaluation['reason'] = "Does not match expected result"

        # If there's a custom evaluation function, use that
        elif 'evaluation_type' in evaluation_criteria:
            eval_type = evaluation_criteria['evaluation_type']

            if eval_type == 'contains_keywords':
                keywords = evaluation_criteria.get('keywords', [])
                if isinstance(result.get('result'), str):
                    result_text = result.get('result', '').lower()
                    matched_keywords = [kw for kw in keywords if kw.lower() in result_text]
                    score = len(matched_keywords) / len(keywords) if keywords else 0

                    evaluation['score'] = score
                    evaluation['reason'] = f"Matched {len(matched_keywords)} of {len(keywords)} keywords"
                    evaluation['matched_keywords'] = matched_keywords

            elif eval_type == 'code_compiles':
                # This would require actual code compilation testing
                # For now, we'll just check for syntax errors in the code
                if isinstance(result.get('result'), str):
                    code = result.get('result', '')
                    has_syntax_error = '```' in code and 'SyntaxError' in code

                    if has_syntax_error:
                        evaluation['score'] = 0.0
                        evaluation['reason'] = "Code contains syntax errors"
                    else:
                        evaluation['score'] = 0.8  # Not perfect since we can't actually compile
                        evaluation['reason'] = "No obvious syntax errors in code"

            elif eval_type == 'length_check':
                min_length = evaluation_criteria.get('min_length', 0)
                max_length = evaluation_criteria.get('max_length', float('inf'))

                if isinstance(result.get('result'), str):
                    length = len(result.get('result', ''))

                    if length < min_length:
                        evaluation['score'] = 0.5 * (length / min_length)
                        evaluation['reason'] = f"Result too short: {length} < {min_length} characters"
                    elif max_length < float('inf') and length > max_length:
                        evaluation['score'] = 0.5
                        evaluation['reason'] = f"Result too long: {length} > {max_length} characters"
                    else:
                        evaluation['score'] = 1.0
                        evaluation['reason'] = f"Result length within acceptable range"

        # Default to a basic success score if no other evaluation was performed
        else:
            evaluation['score'] = 0.7  # Moderate score for successful completion without specific criteria
            evaluation['reason'] = "Task completed successfully, no specific evaluation criteria"

        return evaluation

    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score between 0 and 1
        """
        # Simple implementation using difflib
        import difflib

        # Normalize strings
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()

        # Calculate similarity
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    async def _update_leaderboards(self, category: str, benchmark_id: str, result: Dict[str, Any]) -> None:
        """Update leaderboards with a new benchmark result.

        Args:
            category: Benchmark category
            benchmark_id: Benchmark ID
            result: Benchmark result
        """
        # Update benchmark-specific leaderboard
        benchmark_leaderboard_file = os.path.join(self.config['leaderboards_dir'], f"{benchmark_id}_leaderboard.json")

        if os.path.exists(benchmark_leaderboard_file):
            with open(benchmark_leaderboard_file, 'r') as f:
                benchmark_leaderboard = json.load(f)
        else:
            benchmark_leaderboard = {
                'benchmark_id': benchmark_id,
                'entries': []
            }

        # Create a leaderboard entry
        entry = {
            'agent_id': result['agent_id'],
            'model_name': result['model_name'],
            'timestamp': result['timestamp'],
            'metrics': result['metrics'],
            'result_id': os.path.basename(benchmark_id)
        }

        # Add to benchmark leaderboard
        benchmark_leaderboard['entries'].append(entry)

        # Sort entries by average score (descending)
        benchmark_leaderboard['entries'].sort(
            key=lambda e: e['metrics']['average_score'],
            reverse=True
        )

        # Save benchmark leaderboard
        with open(benchmark_leaderboard_file, 'w') as f:
            json.dump(benchmark_leaderboard, f, indent=2)

        # Update category leaderboard
        category_leaderboard_file = os.path.join(self.config['leaderboards_dir'], f"{category}_leaderboard.json")

        if os.path.exists(category_leaderboard_file):
            with open(category_leaderboard_file, 'r') as f:
                category_leaderboard = json.load(f)
        else:
            category_leaderboard = {
                'category': category,
                'entries': []
            }

        # Add to category leaderboard
        category_leaderboard['entries'].append({
            'benchmark_id': benchmark_id,
            'agent_id': result['agent_id'],
            'model_name': result['model_name'],
            'timestamp': result['timestamp'],
            'metrics': result['metrics'],
            'result_id': os.path.basename(benchmark_id)
        })

        # Sort entries by average score (descending)
        category_leaderboard['entries'].sort(
            key=lambda e: e['metrics']['average_score'],
            reverse=True
        )

        # Save category leaderboard
        with open(category_leaderboard_file, 'w') as f:
            json.dump(category_leaderboard, f, indent=2)

        # Update model leaderboard
        model_leaderboard_file = os.path.join(self.config['leaderboards_dir'], f"model_leaderboard.json")

        if os.path.exists(model_leaderboard_file):
            with open(model_leaderboard_file, 'r') as f:
                model_leaderboard = json.load(f)
        else:
            model_leaderboard = {
                'models': {}
            }

        # Add to model leaderboard
        model_name = result['model_name']
        if model_name not in model_leaderboard['models']:
            model_leaderboard['models'][model_name] = {
                'benchmarks': {},
                'average_score': 0,
                'total_benchmarks': 0
            }

        model_leaderboard['models'][model_name]['benchmarks'][benchmark_id] = {
            'agent_id': result['agent_id'],
            'timestamp': result['timestamp'],
            'metrics': result['metrics']
        }

        # Recalculate average score for the model
        benchmarks = model_leaderboard['models'][model_name]['benchmarks']
        total_score = sum(b['metrics']['average_score'] for b in benchmarks.values())
        model_leaderboard['models'][model_name]['average_score'] = total_score / len(benchmarks)
        model_leaderboard['models'][model_name]['total_benchmarks'] = len(benchmarks)

        # Save model leaderboard
        with open(model_leaderboard_file, 'w') as f:
            json.dump(model_leaderboard, f, indent=2)

    def _get_agent_class(self, agent_id: str):
        """Get the agent class for a given agent ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent class or None if not found
        """
        # Map agent IDs to their classes
        agent_classes = {
            'codey': 'agents.coding.CodingAgent',
            'perry': 'agents.perry.PerryAgent',
            'shelly': 'agents.shelly.ShellyAgent',
            'flora': 'agents.flora.FloraAgent'
        }

        if agent_id not in agent_classes:
            return None

        # Import the agent class
        try:
            module_path, class_name = agent_classes[agent_id].rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Error importing agent class for {agent_id}: {str(e)}")
            return None
