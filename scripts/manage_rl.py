#!/usr/bin/env python3
"""
Manage reinforcement learning for agents.

This script manages the reinforcement learning process for agents.
"""

import os
import sys
import json
import asyncio
import argparse
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.secure_logging import get_logger
from config.config import config
from benchmarking.benchmark_manager import BenchmarkManager

logger = get_logger('dmac.scripts.manage_rl')

class RLManager:
    """Manager for reinforcement learning."""
    
    def __init__(self):
        """Initialize the RL manager."""
        self.config = config.get('reinforcement_learning', {})
        self.enabled = self.config.get('enabled', False)
        self.learning_rate = self.config.get('learning_rate', 0.001)
        self.batch_size = self.config.get('batch_size', 32)
        self.epochs = self.config.get('epochs', 10)
        self.evaluation_interval = self.config.get('evaluation_interval', 100)
        self.save_interval = self.config.get('save_interval', 500)
        self.metrics = self.config.get('metrics', ['reward', 'loss', 'accuracy'])
        
        # Initialize the benchmark manager
        self.benchmark_manager = BenchmarkManager()
        
        # Create directories
        self.models_dir = os.path.join('data', 'rl_models')
        self.logs_dir = os.path.join('data', 'rl_logs')
        
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
    
    async def train_agent(self, agent_id: str, model_name: str, epochs: Optional[int] = None) -> Dict[str, Any]:
        """Train an agent using reinforcement learning.
        
        Args:
            agent_id: Agent ID
            model_name: Model name
            epochs: Number of epochs to train for
            
        Returns:
            Training results
        """
        if not self.enabled:
            raise ValueError("Reinforcement learning is not enabled")
        
        # Use the specified epochs or the default
        epochs = epochs or self.epochs
        
        logger.info(f"Training agent {agent_id} with model {model_name} for {epochs} epochs")
        
        # Get the agent's benchmarks
        benchmarks = await self._get_agent_benchmarks(agent_id)
        
        if not benchmarks:
            raise ValueError(f"No benchmarks found for agent {agent_id}")
        
        # Get the agent's benchmark results
        results = await self._get_agent_benchmark_results(agent_id, model_name)
        
        if not results:
            raise ValueError(f"No benchmark results found for agent {agent_id} with model {model_name}")
        
        # Simulate training (in a real implementation, this would use the DeepSeek-RL API)
        training_results = {
            'agent_id': agent_id,
            'model_name': model_name,
            'epochs': epochs,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'metrics': {
                'reward': 0.0,
                'loss': 0.0,
                'accuracy': 0.0
            },
            'benchmarks': len(benchmarks),
            'results': len(results)
        }
        
        # Save the training results
        self._save_training_results(agent_id, model_name, training_results)
        
        return training_results
    
    async def evaluate_agent(self, agent_id: str, model_name: str) -> Dict[str, Any]:
        """Evaluate an agent using benchmarks.
        
        Args:
            agent_id: Agent ID
            model_name: Model name
            
        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating agent {agent_id} with model {model_name}")
        
        # Get the agent's benchmarks
        benchmarks = await self._get_agent_benchmarks(agent_id)
        
        if not benchmarks:
            raise ValueError(f"No benchmarks found for agent {agent_id}")
        
        # Run benchmarks for the agent
        results = []
        for benchmark in benchmarks:
            try:
                result = await self.benchmark_manager.run_benchmark(
                    benchmark_id=benchmark['id'],
                    agent_id=agent_id,
                    model_name=model_name
                )
                
                results.append(result)
            except Exception as e:
                logger.error(f"Error running benchmark {benchmark['id']} for agent {agent_id} with model {model_name}: {str(e)}")
        
        # Calculate overall metrics
        if not results:
            raise ValueError(f"No benchmark results for agent {agent_id} with model {model_name}")
        
        accuracy = sum(r['metrics']['accuracy'] for r in results) / len(results)
        average_score = sum(r['metrics']['average_score'] for r in results) / len(results)
        average_latency = sum(r['metrics']['average_latency'] for r in results) / len(results)
        
        evaluation_results = {
            'agent_id': agent_id,
            'model_name': model_name,
            'benchmarks': len(benchmarks),
            'results': len(results),
            'metrics': {
                'accuracy': accuracy,
                'average_score': average_score,
                'average_latency': average_latency
            }
        }
        
        # Save the evaluation results
        self._save_evaluation_results(agent_id, model_name, evaluation_results)
        
        return evaluation_results
    
    async def get_best_model(self, agent_id: str) -> str:
        """Get the best model for an agent based on benchmark results.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Best model name
        """
        logger.info(f"Getting best model for agent {agent_id}")
        
        # Get the agent's benchmark results for all models
        model_results = {}
        
        # Get all model names
        model_names = config.get('models.ollama.models', [])
        if not model_names:
            model_names = ['gemma:7b', 'llama3:8b', 'mistral:7b']
        
        # Get results for each model
        for model_name in model_names:
            try:
                results = await self._get_agent_benchmark_results(agent_id, model_name)
                
                if results:
                    # Calculate average score
                    average_score = sum(r['metrics']['average_score'] for r in results) / len(results)
                    
                    model_results[model_name] = average_score
            except Exception as e:
                logger.error(f"Error getting benchmark results for agent {agent_id} with model {model_name}: {str(e)}")
        
        if not model_results:
            raise ValueError(f"No benchmark results found for agent {agent_id}")
        
        # Get the model with the highest average score
        best_model = max(model_results.items(), key=lambda x: x[1])
        
        return best_model[0]
    
    async def _get_agent_benchmarks(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get benchmarks for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of benchmarks
        """
        # Map agent IDs to benchmark categories
        agent_categories = {
            'codey': 'code_generation',
            'perry': 'prompt_engineering',
            'shelly': 'shell_scripting',
            'flora': 'frontend_development'
        }
        
        category = agent_categories.get(agent_id)
        
        if not category:
            # Try to infer category from agent ID
            for cat in self.benchmark_manager.config['benchmark_categories']:
                if agent_id in cat:
                    category = cat
                    break
        
        if not category:
            return []
        
        # Get benchmarks for the category
        benchmarks = await self.benchmark_manager.list_benchmarks(category)
        
        return benchmarks
    
    async def _get_agent_benchmark_results(self, agent_id: str, model_name: str) -> List[Dict[str, Any]]:
        """Get benchmark results for an agent and model.
        
        Args:
            agent_id: Agent ID
            model_name: Model name
            
        Returns:
            List of benchmark results
        """
        # Map agent IDs to benchmark categories
        agent_categories = {
            'codey': 'code_generation',
            'perry': 'prompt_engineering',
            'shelly': 'shell_scripting',
            'flora': 'frontend_development'
        }
        
        category = agent_categories.get(agent_id)
        
        if not category:
            # Try to infer category from agent ID
            for cat in self.benchmark_manager.config['benchmark_categories']:
                if agent_id in cat:
                    category = cat
                    break
        
        if not category:
            return []
        
        # Get the leaderboard for the category
        leaderboard = await self.benchmark_manager.get_leaderboard(category)
        
        # Filter entries for the agent and model
        results = [
            entry for entry in leaderboard.get('entries', [])
            if entry['agent_id'] == agent_id and entry['model_name'] == model_name
        ]
        
        return results
    
    def _save_training_results(self, agent_id: str, model_name: str, results: Dict[str, Any]) -> None:
        """Save training results.
        
        Args:
            agent_id: Agent ID
            model_name: Model name
            results: Training results
        """
        # Create the file path
        file_path = os.path.join(self.logs_dir, f"{agent_id}_{model_name}_training.json")
        
        # Save the results
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _save_evaluation_results(self, agent_id: str, model_name: str, results: Dict[str, Any]) -> None:
        """Save evaluation results.
        
        Args:
            agent_id: Agent ID
            model_name: Model name
            results: Evaluation results
        """
        # Create the file path
        file_path = os.path.join(self.logs_dir, f"{agent_id}_{model_name}_evaluation.json")
        
        # Save the results
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2)

async def main_async(args):
    """Main async entry point."""
    # Initialize the RL manager
    rl_manager = RLManager()
    
    # Train agent
    if args.train:
        try:
            results = await rl_manager.train_agent(
                agent_id=args.agent,
                model_name=args.model,
                epochs=args.epochs
            )
            
            print(f"Trained agent {args.agent} with model {args.model} for {results['epochs']} epochs")
            print(f"Metrics: {json.dumps(results['metrics'], indent=2)}")
        except ValueError as e:
            print(f"Error: {str(e)}")
    
    # Evaluate agent
    elif args.evaluate:
        try:
            results = await rl_manager.evaluate_agent(
                agent_id=args.agent,
                model_name=args.model
            )
            
            print(f"Evaluated agent {args.agent} with model {args.model}")
            print(f"Metrics: {json.dumps(results['metrics'], indent=2)}")
        except ValueError as e:
            print(f"Error: {str(e)}")
    
    # Get best model
    elif args.best_model:
        try:
            best_model = await rl_manager.get_best_model(args.agent)
            
            print(f"Best model for agent {args.agent}: {best_model}")
        except ValueError as e:
            print(f"Error: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Manage reinforcement learning for agents')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Train agent parser
    train_parser = subparsers.add_parser('train', help='Train an agent')
    train_parser.add_argument('--agent', required=True, help='Agent ID')
    train_parser.add_argument('--model', required=True, help='Model name')
    train_parser.add_argument('--epochs', type=int, help='Number of epochs to train for')
    
    # Evaluate agent parser
    evaluate_parser = subparsers.add_parser('evaluate', help='Evaluate an agent')
    evaluate_parser.add_argument('--agent', required=True, help='Agent ID')
    evaluate_parser.add_argument('--model', required=True, help='Model name')
    
    # Get best model parser
    best_model_parser = subparsers.add_parser('best-model', help='Get the best model for an agent')
    best_model_parser.add_argument('--agent', required=True, help='Agent ID')
    
    args = parser.parse_args()
    
    # Set flags based on command
    if args.command == 'train':
        args.train = True
        args.evaluate = False
        args.best_model = False
    elif args.command == 'evaluate':
        args.train = False
        args.evaluate = True
        args.best_model = False
    elif args.command == 'best-model':
        args.train = False
        args.evaluate = False
        args.best_model = True
    else:
        parser.print_help()
        return
    
    # Run the async main function
    asyncio.run(main_async(args))

if __name__ == '__main__':
    main()
