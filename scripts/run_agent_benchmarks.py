#!/usr/bin/env python3
"""
Run benchmarks for DMac agents.

This script runs benchmarks for the agents and generates leaderboards.
"""

import os
import sys
import json
import asyncio
import argparse
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from benchmarking import BenchmarkManager
from agents.agent_factory import agent_factory
from utils.secure_logging import get_logger

logger = get_logger('dmac.scripts.run_agent_benchmarks')

async def run_benchmarks(
    agent_ids: List[str],
    model_names: List[str],
    benchmark_ids: Optional[List[str]] = None,
    category: Optional[str] = None
) -> None:
    """Run benchmarks for the specified agents and models.
    
    Args:
        agent_ids: List of agent IDs to benchmark
        model_names: List of model names to benchmark
        benchmark_ids: Optional list of specific benchmark IDs to run
        category: Optional category to filter benchmarks
    """
    # Initialize the benchmark manager
    benchmark_manager = BenchmarkManager()
    
    # Get the benchmarks to run
    if benchmark_ids:
        # Use the specified benchmark IDs
        benchmarks = []
        for benchmark_id in benchmark_ids:
            # Find the benchmark file
            for cat in benchmark_manager.config['benchmark_categories']:
                potential_file = os.path.join(benchmark_manager.config['benchmarks_dir'], cat, f"{benchmark_id}.json")
                if os.path.exists(potential_file):
                    with open(potential_file, 'r') as f:
                        benchmarks.append(json.load(f))
                    break
    else:
        # Get benchmarks from the manager
        benchmarks = await benchmark_manager.list_benchmarks(category)
    
    if not benchmarks:
        logger.error("No benchmarks found")
        return
    
    logger.info(f"Running {len(benchmarks)} benchmarks for {len(agent_ids)} agents with {len(model_names)} models")
    
    # Run benchmarks for each agent and model
    for agent_id in agent_ids:
        for model_name in model_names:
            for benchmark in benchmarks:
                benchmark_id = benchmark['id']
                logger.info(f"Running benchmark {benchmark_id} for agent {agent_id} with model {model_name}")
                
                try:
                    result = await benchmark_manager.run_benchmark(
                        benchmark_id=benchmark_id,
                        agent_id=agent_id,
                        model_name=model_name
                    )
                    
                    logger.info(f"Benchmark {benchmark_id} completed for agent {agent_id} with model {model_name}")
                    logger.info(f"Accuracy: {result['metrics']['accuracy']:.2f}, "
                               f"Average Score: {result['metrics']['average_score']:.2f}, "
                               f"Average Latency: {result['metrics']['average_latency']:.2f}s")
                    
                except Exception as e:
                    logger.error(f"Error running benchmark {benchmark_id} for agent {agent_id} with model {model_name}: {str(e)}")
    
    # Get and display leaderboards
    if category:
        leaderboard = await benchmark_manager.get_leaderboard(category)
        print(f"\nLeaderboard for category: {category}")
        _display_leaderboard(leaderboard)
    else:
        # Display leaderboards for all categories
        for cat in benchmark_manager.config['benchmark_categories']:
            leaderboard = await benchmark_manager.get_leaderboard(cat)
            print(f"\nLeaderboard for category: {cat}")
            _display_leaderboard(leaderboard)

def _display_leaderboard(leaderboard: Dict[str, Any]) -> None:
    """Display a leaderboard in a formatted way.
    
    Args:
        leaderboard: Leaderboard data
    """
    if not leaderboard.get('entries'):
        print("  No entries in leaderboard")
        return
    
    # Sort entries by average score
    entries = sorted(leaderboard['entries'], key=lambda e: e['metrics']['average_score'], reverse=True)
    
    # Print header
    print(f"  {'Rank':<5} {'Agent':<10} {'Model':<15} {'Score':<10} {'Accuracy':<10} {'Latency':<10}")
    print(f"  {'-'*5} {'-'*10} {'-'*15} {'-'*10} {'-'*10} {'-'*10}")
    
    # Print entries
    for i, entry in enumerate(entries[:10]):  # Show top 10
        print(f"  {i+1:<5} {entry['agent_id']:<10} {entry['model_name']:<15} "
              f"{entry['metrics']['average_score']:<10.2f} {entry['metrics']['accuracy']:<10.2f} "
              f"{entry['metrics']['average_latency']:<10.2f}s")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run benchmarks for DMac agents')
    parser.add_argument('--agents', nargs='+', default=['codey', 'perry', 'shelly', 'flora'],
                        help='Agent IDs to benchmark')
    parser.add_argument('--models', nargs='+', default=['gemma:7b', 'llama3:8b', 'mistral:7b'],
                        help='Model names to benchmark')
    parser.add_argument('--benchmarks', nargs='+', help='Specific benchmark IDs to run')
    parser.add_argument('--category', help='Category to filter benchmarks')
    
    args = parser.parse_args()
    
    # Run the benchmarks
    asyncio.run(run_benchmarks(
        agent_ids=args.agents,
        model_names=args.models,
        benchmark_ids=args.benchmarks,
        category=args.category
    ))

if __name__ == '__main__':
    main()
