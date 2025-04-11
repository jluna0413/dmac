#!/usr/bin/env python3
"""
Set up agents and run benchmarks.

This script registers the agents with the task system and runs benchmarks.
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
from agents.agent_factory import agent_factory
from agents.personalities import get_agent_personality
from task_system.task_manager import TaskManager
from benchmarking.benchmark_manager import BenchmarkManager

logger = get_logger('dmac.scripts.setup_agents')

async def setup_agents(
    agent_ids: List[str],
    model_name: Optional[str] = None,
    force: bool = False
) -> None:
    """Register agents with the task system.
    
    Args:
        agent_ids: List of agent IDs to register
        model_name: Optional model name to use for all agents
        force: Whether to force re-registration of existing agents
    """
    # Initialize the task manager
    task_manager = TaskManager()
    
    # Register each agent
    for agent_id in agent_ids:
        try:
            # Check if agent is already registered
            existing_agent = await task_manager.get_agent(agent_id)
            if existing_agent and not force:
                logger.info(f"Agent {agent_id} is already registered")
                continue
            
            # Create the agent
            agent = None
            if agent_id == 'codey':
                agent = await agent_factory.create_codey_agent(agent_id, model_name)
            elif agent_id == 'perry':
                agent = await agent_factory.create_perry_agent(agent_id, model_name)
            elif agent_id == 'shelly':
                agent = await agent_factory.create_shelly_agent(agent_id, model_name)
            elif agent_id == 'flora':
                agent = await agent_factory.create_flora_agent(agent_id, model_name)
            else:
                # Try generic creation
                agent = await agent_factory.create_agent(agent_id, agent_id, model_name=model_name)
            
            if not agent:
                logger.error(f"Failed to create agent {agent_id}")
                continue
            
            # Get agent personality
            personality = get_agent_personality(agent_id)
            
            # Get agent capabilities
            capabilities = agent.capabilities if hasattr(agent, 'capabilities') else []
            
            # Register the agent
            await task_manager.register_agent(
                agent_id=agent_id,
                name=personality.get('name', agent_id),
                description=personality.get('role', f"{agent_id} agent"),
                capabilities=capabilities,
                metadata={
                    'personality': personality,
                    'model_name': model_name or getattr(agent, 'model_name', 'default')
                }
            )
            
            logger.info(f"Agent {agent_id} registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering agent {agent_id}: {str(e)}")

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

async def main_async(args):
    """Main async entry point."""
    # Register agents
    if args.register:
        await setup_agents(
            agent_ids=args.agents,
            model_name=args.model,
            force=args.force
        )
    
    # Run benchmarks
    if args.benchmark:
        await run_benchmarks(
            agent_ids=args.agents,
            model_names=args.models or ['gemma:7b'],
            benchmark_ids=args.benchmark_ids,
            category=args.category
        )

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Set up agents and run benchmarks')
    parser.add_argument('--agents', nargs='+', default=['codey', 'perry', 'shelly', 'flora'],
                        help='Agent IDs to set up')
    parser.add_argument('--model', help='Model name to use for all agents')
    parser.add_argument('--models', nargs='+', help='Model names to benchmark')
    parser.add_argument('--force', action='store_true', help='Force re-registration of existing agents')
    parser.add_argument('--register', action='store_true', help='Register agents')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmarks')
    parser.add_argument('--benchmark-ids', nargs='+', help='Specific benchmark IDs to run')
    parser.add_argument('--category', help='Category to filter benchmarks')
    
    args = parser.parse_args()
    
    # Run the async main function
    asyncio.run(main_async(args))

if __name__ == '__main__':
    main()
