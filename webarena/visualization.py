"""
WebArena Visualization for DMac.

This module provides visualization utilities for WebArena results.
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from config.config import config
from utils.secure_logging import get_logger
from utils.error_handling import handle_async_errors
from webarena.webarena_manager import webarena_manager

logger = get_logger('dmac.webarena.visualization')


class WebArenaVisualization:
    """Visualization utilities for WebArena results."""
    
    def __init__(self):
        """Initialize the WebArena visualization."""
        # Load configuration
        self.enabled = config.get('webarena.visualization.enabled', True)
        self.data_dir = Path(config.get('webarena.data_dir', 'data/webarena'))
        self.results_dir = self.data_dir / 'results'
        self.visualizations_dir = self.data_dir / 'visualizations'
        
        # Create directories if they don't exist
        os.makedirs(self.visualizations_dir, exist_ok=True)
        
        logger.info("WebArena visualization initialized")
    
    @handle_async_errors(default_message="Error generating success rate visualization")
    async def generate_success_rate_visualization(self, run_ids: List[str]) -> Optional[str]:
        """Generate a visualization of success rates for multiple runs.
        
        Args:
            run_ids: The IDs of the runs to visualize.
            
        Returns:
            The path to the generated visualization, or None if an error occurred.
        """
        if not self.enabled:
            logger.warning("WebArena visualization is disabled")
            return None
        
        # Get the run results
        run_results = []
        for run_id in run_ids:
            results = await webarena_manager.get_run_results(run_id)
            if results:
                run_info = await webarena_manager.get_run_status(run_id)
                run_results.append({
                    'run_id': run_id,
                    'task_name': run_info['task_name'],
                    'model_name': run_info['model_name'],
                    'results': results,
                })
        
        if not run_results:
            logger.warning("No results found for the specified runs")
            return None
        
        # Extract success rates
        success_rates = []
        for run in run_results:
            success_rate = self._extract_success_rate(run['results'])
            if success_rate is not None:
                success_rates.append({
                    'run_id': run['run_id'],
                    'task_name': run['task_name'],
                    'model_name': run['model_name'],
                    'success_rate': success_rate,
                })
        
        if not success_rates:
            logger.warning("No success rates found in the results")
            return None
        
        # Create a DataFrame
        df = pd.DataFrame(success_rates)
        
        # Generate the visualization
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Group by task and model
        grouped = df.groupby(['task_name', 'model_name'])['success_rate'].mean().reset_index()
        
        # Create a bar chart
        bars = ax.bar(range(len(grouped)), grouped['success_rate'], width=0.8)
        
        # Set the x-axis labels
        ax.set_xticks(range(len(grouped)))
        ax.set_xticklabels([f"{row['task_name']}\n{row['model_name']}" for _, row in grouped.iterrows()], rotation=45, ha='right')
        
        # Set the y-axis label
        ax.set_ylabel('Success Rate')
        
        # Set the title
        ax.set_title('WebArena Task Success Rates by Model')
        
        # Add a grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add values on top of the bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02, f'{height:.2f}', ha='center', va='bottom')
        
        # Adjust the layout
        plt.tight_layout()
        
        # Save the visualization
        timestamp = int(time.time())
        visualization_path = self.visualizations_dir / f"success_rates_{timestamp}.png"
        plt.savefig(visualization_path)
        plt.close(fig)
        
        logger.info(f"Generated success rate visualization: {visualization_path}")
        return str(visualization_path)
    
    @handle_async_errors(default_message="Error generating task completion time visualization")
    async def generate_completion_time_visualization(self, run_ids: List[str]) -> Optional[str]:
        """Generate a visualization of task completion times for multiple runs.
        
        Args:
            run_ids: The IDs of the runs to visualize.
            
        Returns:
            The path to the generated visualization, or None if an error occurred.
        """
        if not self.enabled:
            logger.warning("WebArena visualization is disabled")
            return None
        
        # Get the run results
        run_results = []
        for run_id in run_ids:
            results = await webarena_manager.get_run_results(run_id)
            if results:
                run_info = await webarena_manager.get_run_status(run_id)
                run_results.append({
                    'run_id': run_id,
                    'task_name': run_info['task_name'],
                    'model_name': run_info['model_name'],
                    'results': results,
                })
        
        if not run_results:
            logger.warning("No results found for the specified runs")
            return None
        
        # Extract completion times
        completion_times = []
        for run in run_results:
            times = self._extract_completion_times(run['results'])
            if times:
                for time_value in times:
                    completion_times.append({
                        'run_id': run['run_id'],
                        'task_name': run['task_name'],
                        'model_name': run['model_name'],
                        'completion_time': time_value,
                    })
        
        if not completion_times:
            logger.warning("No completion times found in the results")
            return None
        
        # Create a DataFrame
        df = pd.DataFrame(completion_times)
        
        # Generate the visualization
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Group by task and model
        grouped = df.groupby(['task_name', 'model_name'])['completion_time'].mean().reset_index()
        
        # Create a bar chart
        bars = ax.bar(range(len(grouped)), grouped['completion_time'], width=0.8)
        
        # Set the x-axis labels
        ax.set_xticks(range(len(grouped)))
        ax.set_xticklabels([f"{row['task_name']}\n{row['model_name']}" for _, row in grouped.iterrows()], rotation=45, ha='right')
        
        # Set the y-axis label
        ax.set_ylabel('Completion Time (seconds)')
        
        # Set the title
        ax.set_title('WebArena Task Completion Times by Model')
        
        # Add a grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add values on top of the bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02, f'{height:.2f}', ha='center', va='bottom')
        
        # Adjust the layout
        plt.tight_layout()
        
        # Save the visualization
        timestamp = int(time.time())
        visualization_path = self.visualizations_dir / f"completion_times_{timestamp}.png"
        plt.savefig(visualization_path)
        plt.close(fig)
        
        logger.info(f"Generated completion time visualization: {visualization_path}")
        return str(visualization_path)
    
    @handle_async_errors(default_message="Error generating action count visualization")
    async def generate_action_count_visualization(self, run_ids: List[str]) -> Optional[str]:
        """Generate a visualization of action counts for multiple runs.
        
        Args:
            run_ids: The IDs of the runs to visualize.
            
        Returns:
            The path to the generated visualization, or None if an error occurred.
        """
        if not self.enabled:
            logger.warning("WebArena visualization is disabled")
            return None
        
        # Get the run results
        run_results = []
        for run_id in run_ids:
            results = await webarena_manager.get_run_results(run_id)
            if results:
                run_info = await webarena_manager.get_run_status(run_id)
                run_results.append({
                    'run_id': run_id,
                    'task_name': run_info['task_name'],
                    'model_name': run_info['model_name'],
                    'results': results,
                })
        
        if not run_results:
            logger.warning("No results found for the specified runs")
            return None
        
        # Extract action counts
        action_counts = []
        for run in run_results:
            counts = self._extract_action_counts(run['results'])
            if counts:
                for action_type, count in counts.items():
                    action_counts.append({
                        'run_id': run['run_id'],
                        'task_name': run['task_name'],
                        'model_name': run['model_name'],
                        'action_type': action_type,
                        'count': count,
                    })
        
        if not action_counts:
            logger.warning("No action counts found in the results")
            return None
        
        # Create a DataFrame
        df = pd.DataFrame(action_counts)
        
        # Generate the visualization
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        # Group by task, model, and action type
        grouped = df.groupby(['task_name', 'model_name', 'action_type'])['count'].mean().reset_index()
        
        # Pivot the data for stacked bars
        pivot_df = grouped.pivot_table(index=['task_name', 'model_name'], columns='action_type', values='count', fill_value=0)
        
        # Create a stacked bar chart
        pivot_df.plot(kind='bar', stacked=True, ax=ax)
        
        # Set the x-axis labels
        ax.set_xticklabels([f"{idx[0]}\n{idx[1]}" for idx in pivot_df.index], rotation=45, ha='right')
        
        # Set the y-axis label
        ax.set_ylabel('Action Count')
        
        # Set the title
        ax.set_title('WebArena Action Counts by Task and Model')
        
        # Add a grid
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add a legend
        ax.legend(title='Action Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Adjust the layout
        plt.tight_layout()
        
        # Save the visualization
        timestamp = int(time.time())
        visualization_path = self.visualizations_dir / f"action_counts_{timestamp}.png"
        plt.savefig(visualization_path)
        plt.close(fig)
        
        logger.info(f"Generated action count visualization: {visualization_path}")
        return str(visualization_path)
    
    @handle_async_errors(default_message="Error generating model comparison visualization")
    async def generate_model_comparison_visualization(self, task_name: str, model_names: List[str]) -> Optional[str]:
        """Generate a visualization comparing models on a specific task.
        
        Args:
            task_name: The name of the task to compare models on.
            model_names: The names of the models to compare.
            
        Returns:
            The path to the generated visualization, or None if an error occurred.
        """
        if not self.enabled:
            logger.warning("WebArena visualization is disabled")
            return None
        
        # Get all runs
        all_runs = await webarena_manager.list_runs()
        
        # Filter runs by task and models
        filtered_runs = [
            run for run in all_runs
            if run['task_name'] == task_name and run['model_name'] in model_names and run['status'] == 'completed'
        ]
        
        if not filtered_runs:
            logger.warning(f"No completed runs found for task '{task_name}' with models {model_names}")
            return None
        
        # Get the run results
        run_results = []
        for run in filtered_runs:
            results = await webarena_manager.get_run_results(run['id'])
            if results:
                run_results.append({
                    'run_id': run['id'],
                    'task_name': run['task_name'],
                    'model_name': run['model_name'],
                    'results': results,
                })
        
        if not run_results:
            logger.warning("No results found for the filtered runs")
            return None
        
        # Extract metrics
        metrics = []
        for run in run_results:
            success_rate = self._extract_success_rate(run['results'])
            completion_times = self._extract_completion_times(run['results'])
            action_counts = self._extract_action_counts(run['results'])
            
            if success_rate is not None and completion_times and action_counts:
                metrics.append({
                    'run_id': run['run_id'],
                    'model_name': run['model_name'],
                    'success_rate': success_rate,
                    'avg_completion_time': sum(completion_times) / len(completion_times),
                    'total_actions': sum(action_counts.values()),
                })
        
        if not metrics:
            logger.warning("No metrics found in the results")
            return None
        
        # Create a DataFrame
        df = pd.DataFrame(metrics)
        
        # Group by model
        grouped = df.groupby('model_name').agg({
            'success_rate': 'mean',
            'avg_completion_time': 'mean',
            'total_actions': 'mean',
        }).reset_index()
        
        # Generate the visualization
        fig = plt.figure(figsize=(15, 10))
        
        # Success rate subplot
        ax1 = fig.add_subplot(131)
        bars1 = ax1.bar(grouped['model_name'], grouped['success_rate'], width=0.6)
        ax1.set_ylabel('Success Rate')
        ax1.set_title('Success Rate by Model')
        ax1.set_ylim(0, 1.1)
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.02, f'{height:.2f}', ha='center', va='bottom')
        
        # Completion time subplot
        ax2 = fig.add_subplot(132)
        bars2 = ax2.bar(grouped['model_name'], grouped['avg_completion_time'], width=0.6)
        ax2.set_ylabel('Avg. Completion Time (seconds)')
        ax2.set_title('Average Completion Time by Model')
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height + 0.02, f'{height:.2f}', ha='center', va='bottom')
        
        # Action count subplot
        ax3 = fig.add_subplot(133)
        bars3 = ax3.bar(grouped['model_name'], grouped['total_actions'], width=0.6)
        ax3.set_ylabel('Avg. Total Actions')
        ax3.set_title('Average Total Actions by Model')
        for i, bar in enumerate(bars3):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2., height + 0.02, f'{height:.2f}', ha='center', va='bottom')
        
        # Set the overall title
        fig.suptitle(f"Model Comparison for Task: {task_name}", fontsize=16)
        
        # Adjust the layout
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        # Save the visualization
        timestamp = int(time.time())
        visualization_path = self.visualizations_dir / f"model_comparison_{task_name}_{timestamp}.png"
        plt.savefig(visualization_path)
        plt.close(fig)
        
        logger.info(f"Generated model comparison visualization: {visualization_path}")
        return str(visualization_path)
    
    def _extract_success_rate(self, results: Dict[str, Any]) -> Optional[float]:
        """Extract the success rate from WebArena results.
        
        Args:
            results: The WebArena results.
            
        Returns:
            The success rate, or None if it could not be extracted.
        """
        try:
            # Check if the results contain a success rate
            if 'success_rate' in results:
                return float(results['success_rate'])
            
            # Check if the results contain episode results
            if 'episodes' in results:
                episodes = results['episodes']
                if episodes:
                    successes = sum(1 for episode in episodes if episode.get('success', False))
                    return successes / len(episodes)
            
            # Check if the results contain a success field
            if 'success' in results:
                return 1.0 if results['success'] else 0.0
            
            return None
        except Exception as e:
            logger.exception(f"Error extracting success rate: {e}")
            return None
    
    def _extract_completion_times(self, results: Dict[str, Any]) -> List[float]:
        """Extract the completion times from WebArena results.
        
        Args:
            results: The WebArena results.
            
        Returns:
            A list of completion times.
        """
        try:
            completion_times = []
            
            # Check if the results contain a completion time
            if 'completion_time' in results:
                completion_times.append(float(results['completion_time']))
            
            # Check if the results contain episode results
            if 'episodes' in results:
                episodes = results['episodes']
                for episode in episodes:
                    if 'completion_time' in episode:
                        completion_times.append(float(episode['completion_time']))
            
            return completion_times
        except Exception as e:
            logger.exception(f"Error extracting completion times: {e}")
            return []
    
    def _extract_action_counts(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Extract the action counts from WebArena results.
        
        Args:
            results: The WebArena results.
            
        Returns:
            A dictionary mapping action types to counts.
        """
        try:
            action_counts = {}
            
            # Check if the results contain action counts
            if 'action_counts' in results:
                return results['action_counts']
            
            # Check if the results contain episode results
            if 'episodes' in results:
                episodes = results['episodes']
                for episode in episodes:
                    if 'actions' in episode:
                        actions = episode['actions']
                        for action in actions:
                            action_type = action.get('type', 'unknown')
                            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            
            return action_counts
        except Exception as e:
            logger.exception(f"Error extracting action counts: {e}")
            return {}


# Create a singleton instance
webarena_visualization = WebArenaVisualization()
