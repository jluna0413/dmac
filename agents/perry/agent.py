"""
Perry - Prompt Engineer Agent

This agent specializes in crafting effective prompts for various LLMs and
optimizing prompt strategies for different tasks.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional

from utils.secure_logging import get_logger
from agents.base_agent import BaseAgent
from models.model_provider import OllamaModelProvider
from config.config import config

logger = get_logger('dmac.agents.perry')

class PerryAgent(BaseAgent):
    """Prompt Engineer agent for DMac."""
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the prompt engineer agent.
        
        Args:
            agent_id: Unique identifier for the agent. If not provided, a UUID will be generated.
            config: Configuration for the agent.
        """
        super().__init__(agent_id or "perry", "PromptEngineer", "Agent for prompt engineering and optimization")
        
        # Default configuration
        self.default_config = {
            'model_name': 'gemma:7b',
            'temperature': 0.7,
            'prompt_templates_dir': os.path.join('data', 'prompt_templates'),
            'prompt_history_dir': os.path.join('data', 'prompt_history'),
            'max_history_items': 100,
            'benchmark_results_dir': os.path.join('data', 'benchmarks', 'prompts')
        }
        
        # Merge default config with provided config
        self.config = {**self.default_config, **(config or {})}
        
        # Initialize the model provider
        self.model_provider = OllamaModelProvider(
            model_name=self.config['model_name'],
            temperature=self.config['temperature']
        )
        
        # Create directories if they don't exist
        os.makedirs(self.config['prompt_templates_dir'], exist_ok=True)
        os.makedirs(self.config['prompt_history_dir'], exist_ok=True)
        os.makedirs(self.config['benchmark_results_dir'], exist_ok=True)
        
        # Set up capabilities
        self.capabilities = [
            "prompt_creation",
            "prompt_optimization",
            "prompt_analysis",
            "prompt_benchmarking",
            "prompt_template_management",
            "chain_of_thought_design",
            "few_shot_example_selection"
        ]
        
        # Load prompt templates
        self.prompt_templates = self._load_prompt_templates()
        
        logger.info(f"Perry Prompt Engineer agent initialized with {len(self.prompt_templates)} templates")
    
    def _load_prompt_templates(self) -> Dict[str, Any]:
        """Load prompt templates from the templates directory.
        
        Returns:
            Dictionary of prompt templates.
        """
        templates = {}
        template_dir = self.config['prompt_templates_dir']
        
        if not os.path.exists(template_dir):
            return templates
        
        for filename in os.listdir(template_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(template_dir, filename), 'r') as f:
                        template_data = json.load(f)
                        template_id = os.path.splitext(filename)[0]
                        templates[template_id] = template_data
                except Exception as e:
                    logger.error(f"Error loading prompt template {filename}: {str(e)}")
        
        return templates
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message sent to the agent.
        
        Args:
            message: Message to process
            
        Returns:
            Response message
        """
        prompt = message.get('prompt', '')
        task_type = message.get('task_type', 'prompt_creation')
        
        if task_type == 'prompt_creation':
            result = await self.create_prompt(prompt)
        elif task_type == 'prompt_optimization':
            result = await self.optimize_prompt(prompt)
        elif task_type == 'prompt_analysis':
            result = await self.analyze_prompt(prompt)
        elif task_type == 'prompt_benchmarking':
            result = await self.benchmark_prompt(prompt)
        else:
            result = await self.create_prompt(prompt)
        
        return {
            'success': True,
            'result': result,
            'agent_id': self.agent_id
        }
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task assigned to the agent.
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
        """
        task_type = task.get('type', '')
        task_data = task.get('data', {})
        
        if task_type == 'create_prompt':
            description = task_data.get('description', '')
            target_model = task_data.get('target_model', 'general')
            use_case = task_data.get('use_case', 'general')
            
            prompt = await self.create_prompt(description, target_model, use_case)
            
            return {
                'success': True,
                'result': prompt,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'optimize_prompt':
            original_prompt = task_data.get('prompt', '')
            target_model = task_data.get('target_model', 'general')
            optimization_goal = task_data.get('optimization_goal', 'quality')
            
            optimized_prompt = await self.optimize_prompt(original_prompt, target_model, optimization_goal)
            
            return {
                'success': True,
                'result': optimized_prompt,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        elif task_type == 'analyze_prompt':
            prompt = task_data.get('prompt', '')
            
            analysis = await self.analyze_prompt(prompt)
            
            return {
                'success': True,
                'result': analysis,
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
        
        else:
            return {
                'success': False,
                'error': f"Unknown task type: {task_type}",
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
    
    async def create_prompt(self, description: str, target_model: str = 'general', use_case: str = 'general') -> str:
        """Create a prompt based on the description.
        
        Args:
            description: Description of what the prompt should do
            target_model: Target model for the prompt
            use_case: Use case for the prompt
            
        Returns:
            Generated prompt
        """
        system_prompt = """You are Perry, an expert prompt engineer. Your task is to create an effective prompt based on the description provided.
Follow these guidelines:
1. Be clear and specific about the desired output format and content
2. Include relevant context and constraints
3. Use appropriate techniques like chain-of-thought, few-shot examples, or structured formatting
4. Tailor the prompt to the target model's capabilities
5. Consider the specific use case requirements"""
        
        user_prompt = f"""Create a prompt based on the following description:
Description: {description}
Target Model: {target_model}
Use Case: {use_case}

Your response should include:
1. The crafted prompt
2. A brief explanation of your prompt design choices
3. Any suggestions for further optimization"""
        
        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Save to history
        self._save_to_history('create', {
            'description': description,
            'target_model': target_model,
            'use_case': use_case,
            'result': response
        })
        
        return response
    
    async def optimize_prompt(self, prompt: str, target_model: str = 'general', optimization_goal: str = 'quality') -> str:
        """Optimize an existing prompt.
        
        Args:
            prompt: Original prompt to optimize
            target_model: Target model for the prompt
            optimization_goal: Goal of optimization (quality, specificity, etc.)
            
        Returns:
            Optimized prompt
        """
        system_prompt = """You are Perry, an expert prompt engineer. Your task is to optimize the provided prompt to make it more effective.
Follow these guidelines:
1. Improve clarity and specificity
2. Add relevant context or constraints if missing
3. Restructure for better flow and understanding
4. Consider the target model's capabilities and limitations
5. Focus on the specific optimization goal"""
        
        user_prompt = f"""Optimize the following prompt:
Original Prompt: {prompt}
Target Model: {target_model}
Optimization Goal: {optimization_goal}

Your response should include:
1. The optimized prompt
2. A comparison between the original and optimized versions
3. Explanation of the changes made and their expected impact"""
        
        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Save to history
        self._save_to_history('optimize', {
            'original_prompt': prompt,
            'target_model': target_model,
            'optimization_goal': optimization_goal,
            'result': response
        })
        
        return response
    
    async def analyze_prompt(self, prompt: str) -> str:
        """Analyze a prompt and provide feedback.
        
        Args:
            prompt: Prompt to analyze
            
        Returns:
            Analysis of the prompt
        """
        system_prompt = """You are Perry, an expert prompt engineer. Your task is to analyze the provided prompt and give detailed feedback.
Follow these guidelines:
1. Evaluate clarity, specificity, and structure
2. Identify potential ambiguities or issues
3. Assess the prompt's effectiveness for different models
4. Consider how the prompt might be interpreted
5. Provide actionable suggestions for improvement"""
        
        user_prompt = f"""Analyze the following prompt:
Prompt: {prompt}

Your analysis should include:
1. Overall assessment of the prompt's effectiveness
2. Strengths and weaknesses
3. Potential ambiguities or issues
4. Suggestions for improvement
5. How different models might respond to this prompt"""
        
        response = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Save to history
        self._save_to_history('analyze', {
            'prompt': prompt,
            'result': response
        })
        
        return response
    
    async def benchmark_prompt(self, prompt: str, models: Optional[List[str]] = None) -> str:
        """Benchmark a prompt across different models.
        
        Args:
            prompt: Prompt to benchmark
            models: List of models to benchmark against (defaults to available models)
            
        Returns:
            Benchmark results
        """
        # If no models specified, use default set
        if not models:
            models = ['gemma:7b', 'llama3:8b', 'mistral:7b']
        
        results = {}
        
        # Test the prompt with each model
        for model_name in models:
            try:
                # Create a temporary model provider for this model
                temp_provider = OllamaModelProvider(
                    model_name=model_name,
                    temperature=0.7
                )
                
                # Generate a response
                response = await temp_provider.generate(user_prompt=prompt)
                
                # Store the result
                results[model_name] = {
                    'response': response,
                    'length': len(response),
                    'status': 'success'
                }
                
            except Exception as e:
                results[model_name] = {
                    'response': str(e),
                    'status': 'error'
                }
        
        # Generate a comparison report
        system_prompt = """You are Perry, an expert prompt engineer. Your task is to analyze the benchmark results of a prompt across different models.
Follow these guidelines:
1. Compare the responses from different models
2. Identify strengths and weaknesses in each response
3. Assess how the prompt performed across models
4. Provide insights on model-specific behaviors
5. Suggest prompt improvements based on the benchmark results"""
        
        user_prompt = f"""Analyze the benchmark results for the following prompt:
Prompt: {prompt}

Results:
{json.dumps(results, indent=2)}

Your analysis should include:
1. Overall assessment of the prompt's performance across models
2. Comparison of responses between models
3. Model-specific behaviors or issues
4. Recommendations for prompt improvements
5. Which model performed best with this prompt and why"""
        
        analysis = await self.model_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        # Save benchmark results
        benchmark_data = {
            'prompt': prompt,
            'models': models,
            'results': results,
            'analysis': analysis
        }
        
        benchmark_file = os.path.join(
            self.config['benchmark_results_dir'],
            f"benchmark_{self.agent_id}_{int(asyncio.get_event_loop().time())}.json"
        )
        
        with open(benchmark_file, 'w') as f:
            json.dump(benchmark_data, f, indent=2)
        
        return analysis
    
    def _save_to_history(self, action_type: str, data: Dict[str, Any]) -> None:
        """Save an action to the prompt history.
        
        Args:
            action_type: Type of action (create, optimize, analyze)
            data: Data associated with the action
        """
        history_dir = self.config['prompt_history_dir']
        
        # Create a history entry
        history_entry = {
            'timestamp': asyncio.get_event_loop().time(),
            'agent_id': self.agent_id,
            'action_type': action_type,
            'data': data
        }
        
        # Generate a filename
        filename = f"{action_type}_{self.agent_id}_{int(history_entry['timestamp'])}.json"
        filepath = os.path.join(history_dir, filename)
        
        # Save the entry
        with open(filepath, 'w') as f:
            json.dump(history_entry, f, indent=2)
        
        # Cleanup old history if needed
        self._cleanup_history()
    
    def _cleanup_history(self) -> None:
        """Clean up old history entries if there are too many."""
        history_dir = self.config['prompt_history_dir']
        max_items = self.config['max_history_items']
        
        # Get all history files
        history_files = [
            os.path.join(history_dir, f) 
            for f in os.listdir(history_dir) 
            if f.endswith('.json')
        ]
        
        # Sort by modification time (oldest first)
        history_files.sort(key=lambda f: os.path.getmtime(f))
        
        # Remove oldest files if there are too many
        if len(history_files) > max_items:
            for file_to_remove in history_files[:len(history_files) - max_items]:
                try:
                    os.remove(file_to_remove)
                    logger.debug(f"Removed old history file: {file_to_remove}")
                except Exception as e:
                    logger.error(f"Error removing history file {file_to_remove}: {str(e)}")
