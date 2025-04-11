"""
DeepClaude Module for DMac

This module provides the core functionality of DeepClaude, combining DeepSeek R1 for reasoning
with Claude 3.7 Sonnet (or other models) for refinement and generation.

The DeepClaude approach works by:
1. Using DeepSeek R1 to generate reasoning about a problem or task
2. Extracting this reasoning and passing it to Claude 3.7 Sonnet
3. Using Claude 3.7 Sonnet to generate the final output based on the reasoning

This hybrid approach leverages the strengths of both models:
- DeepSeek R1's strong reasoning capabilities
- Claude 3.7 Sonnet's high-quality output generation

The module is designed to be flexible and can be used by any agent in the system.
It supports various use cases including code generation, explanation, and refactoring.

Implementation based on: https://github.com/ErlichLiu/deepclaude
"""

import time
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union

from utils.secure_logging import get_logger
from models.model_manager import ModelManager

logger = get_logger('dmac.models.deepclaude')

class DeepClaudeModule:
    """
    DeepClaude module that combines DeepSeek R1 for reasoning with Claude 3.7 Sonnet
    (or other models) for refinement and generation.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the DeepClaude module.

        Args:
            config: Configuration for the module
        """
        self.config = config or {}
        self.model_manager = ModelManager()

        # Default configuration
        self.default_config = {
            'reasoning_model': 'GandalfBaum/deepseek_r1-claude3.7:latest',
            'generation_model': 'claude-3-7-sonnet',
            'temperature': 0.2,
            'max_reasoning_tokens': 2000,
            'max_generation_tokens': 4000,
            'supports_native_reasoning': True,
            'reasoning_tag': '<think>',
            'reasoning_end_tag': '</think>',
            'reasoning_max_tokens': 5,  # For DeepSeek R1, to save tokens
            'enable_proxy': {
                'reasoning_model': False,
                'generation_model': True
            },
            'cache_enabled': True,
            'cache_ttl': 3600,  # 1 hour
        }

        # Merge default config with provided config
        self.config = {**self.default_config, **self.config}

        # Initialize cache
        self.cache = {}
        self.cache_timestamps = {}

        logger.info("DeepClaude module initialized")

    async def generate_with_reasoning(self,
                                     prompt: str,
                                     system_message: Optional[str] = None,
                                     context: Optional[str] = None,
                                     model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate content using the DeepClaude approach.

        Args:
            prompt: The prompt for generation
            system_message: Optional system message to guide the generation
            context: Optional additional context
            model_config: Optional model configuration overrides

        Returns:
            Generation result with reasoning
        """
        # Merge default config with provided model config
        config = {**self.config}
        if model_config:
            config.update(model_config)

        # Check cache if enabled
        if config['cache_enabled']:
            cache_key = self._generate_cache_key(prompt, system_message, context, config)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Using cached result for prompt")
                return cached_result

        # Step 1: Generate reasoning with DeepSeek R1
        reasoning_start_time = time.time()
        reasoning_result = await self._generate_reasoning(
            prompt,
            system_message,
            context,
            config
        )
        reasoning_time = time.time() - reasoning_start_time

        # Extract reasoning
        reasoning, reasoning_raw = self._extract_reasoning(reasoning_result, config)

        # Step 2: Generate final content with Claude 3.7 Sonnet or other model
        generation_start_time = time.time()
        generation_result = await self._generate_final_content(
            prompt,
            reasoning,
            system_message,
            context,
            config
        )
        generation_time = time.time() - generation_start_time

        # Prepare result
        result = {
            'success': True,
            'content': generation_result.get('content', ''),
            'reasoning': reasoning,
            'reasoning_raw': reasoning_raw,
            'reasoning_time': reasoning_time,
            'generation_time': generation_time,
            'total_time': reasoning_time + generation_time,
            'reasoning_model': config['reasoning_model'],
            'generation_model': config['generation_model'],
            'timestamp': time.time()
        }

        # Cache result if enabled
        if config['cache_enabled']:
            self._add_to_cache(cache_key, result)

        return result

    async def generate_code(self,
                           prompt: str,
                           language: Optional[str] = None,
                           system_message: Optional[str] = None,
                           context: Optional[str] = None,
                           model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate code using the DeepClaude approach.

        Args:
            prompt: The prompt for code generation
            language: The programming language
            system_message: Optional system message to guide the generation
            context: Optional additional context
            model_config: Optional model configuration overrides

        Returns:
            Generated code result with reasoning
        """
        # Prepare prompt with language specification if provided
        if language:
            enhanced_prompt = f"Generate {language} code: {prompt}"

            # Add language-specific system message if not provided
            if not system_message:
                system_message = f"You are an expert {language} programmer. Generate high-quality, efficient, and well-documented {language} code."
        else:
            enhanced_prompt = f"Generate code: {prompt}"

            # Add generic system message if not provided
            if not system_message:
                system_message = "You are an expert programmer. Generate high-quality, efficient, and well-documented code."

        # Generate with reasoning
        result = await self.generate_with_reasoning(
            enhanced_prompt,
            system_message,
            context,
            model_config
        )

        # Add language information to result
        result['language'] = language or 'unknown'

        return result

    async def explain_code(self,
                          code: str,
                          language: Optional[str] = None,
                          system_message: Optional[str] = None,
                          model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Explain code using the DeepClaude approach.

        Args:
            code: The code to explain
            language: The programming language
            system_message: Optional system message to guide the explanation
            model_config: Optional model configuration overrides

        Returns:
            Code explanation result with reasoning
        """
        # Prepare prompt
        if language:
            prompt = f"Explain the following {language} code in detail:\n\n```{language}\n{code}\n```"

            # Add language-specific system message if not provided
            if not system_message:
                system_message = f"You are an expert {language} programmer. Explain code clearly and thoroughly."
        else:
            prompt = f"Explain the following code in detail:\n\n```\n{code}\n```"

            # Add generic system message if not provided
            if not system_message:
                system_message = "You are an expert programmer. Explain code clearly and thoroughly."

        # Generate with reasoning
        result = await self.generate_with_reasoning(
            prompt,
            system_message,
            None,
            model_config
        )

        # Add code and language information to result
        result['code'] = code
        result['language'] = language or 'unknown'

        return result

    async def refactor_code(self,
                           code: str,
                           instructions: str,
                           language: Optional[str] = None,
                           system_message: Optional[str] = None,
                           model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Refactor code using the DeepClaude approach.

        Args:
            code: The code to refactor
            instructions: Instructions for refactoring
            language: The programming language
            system_message: Optional system message to guide the refactoring
            model_config: Optional model configuration overrides

        Returns:
            Refactored code result with reasoning
        """
        # Prepare prompt
        if language:
            prompt = f"Refactor the following {language} code according to these instructions: {instructions}\n\n```{language}\n{code}\n```"

            # Add language-specific system message if not provided
            if not system_message:
                system_message = f"You are an expert {language} programmer. Refactor code to improve quality, readability, and efficiency."
        else:
            prompt = f"Refactor the following code according to these instructions: {instructions}\n\n```\n{code}\n```"

            # Add generic system message if not provided
            if not system_message:
                system_message = "You are an expert programmer. Refactor code to improve quality, readability, and efficiency."

        # Generate with reasoning
        result = await self.generate_with_reasoning(
            prompt,
            system_message,
            None,
            model_config
        )

        # Add code, instructions, and language information to result
        result['original_code'] = code
        result['instructions'] = instructions
        result['language'] = language or 'unknown'

        return result

    async def _generate_reasoning(self,
                                 prompt: str,
                                 system_message: Optional[str] = None,
                                 context: Optional[str] = None,
                                 config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate reasoning using DeepSeek R1.

        Args:
            prompt: The prompt for reasoning
            system_message: Optional system message
            context: Optional additional context
            config: Configuration for generation

        Returns:
            Reasoning result
        """
        # Prepare messages
        messages = []

        # Add system message if provided
        if system_message:
            messages.append({
                'role': 'system',
                'content': system_message
            })
        else:
            # Default system message for reasoning
            messages.append({
                'role': 'system',
                'content': "You are an expert problem solver. Think step-by-step about the problem before providing a solution."
            })

        # Add context if provided
        if context:
            messages.append({
                'role': 'user',
                'content': context
            })

        # Add prompt
        reasoning_prompt = prompt
        if not config.get('supports_native_reasoning', True):
            # For models that don't support native reasoning, add a prompt to encourage thinking
            reasoning_prompt = f"Please think through this problem step by step. Use {config['reasoning_tag']} and {config['reasoning_end_tag']} tags to show your reasoning.\n\n{prompt}"

        messages.append({
            'role': 'user',
            'content': reasoning_prompt
        })

        # Generate reasoning
        try:
            # Get the model from the model manager
            model_name = config.get('reasoning_model', self.default_config['reasoning_model'])

            # Prepare generation parameters
            params = {
                'messages': messages,
                'temperature': config.get('temperature', self.default_config['temperature']),
                'max_tokens': config.get('max_reasoning_tokens', self.default_config['max_reasoning_tokens']),
                'reasoning_max_tokens': config.get('reasoning_max_tokens', self.default_config['reasoning_max_tokens']),
                'enable_proxy': config.get('enable_proxy', {}).get('reasoning_model', False)
            }

            # Generate reasoning
            response = await self.model_manager.generate(model_name, params)

            return response
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'reasoning_content': ''
            }

    async def _generate_final_content(self,
                                     prompt: str,
                                     reasoning: str,
                                     system_message: Optional[str] = None,
                                     context: Optional[str] = None,
                                     config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate final content using Claude 3.7 Sonnet or other model with reasoning.

        Args:
            prompt: The original prompt
            reasoning: The reasoning from DeepSeek R1
            system_message: Optional system message
            context: Optional additional context
            config: Configuration for generation

        Returns:
            Final content result
        """
        # Prepare messages
        messages = []

        # Add system message if provided
        if system_message:
            messages.append({
                'role': 'system',
                'content': system_message
            })
        else:
            # Default system message for generation
            messages.append({
                'role': 'system',
                'content': "You are a helpful assistant. Use the provided reasoning to generate a high-quality response."
            })

        # Add context if provided
        if context:
            messages.append({
                'role': 'user',
                'content': context
            })

        # Add prompt with reasoning
        generation_prompt = f"""
Here is a request: {prompt}

I've thought about this problem and here's my reasoning:
{reasoning}

Based on this reasoning, provide a comprehensive and accurate response to the original request.
"""

        messages.append({
            'role': 'user',
            'content': generation_prompt
        })

        # Generate final content
        try:
            # Get the model from the model manager
            model_name = config.get('generation_model', self.default_config['generation_model'])

            # Prepare generation parameters
            params = {
                'messages': messages,
                'temperature': config.get('temperature', self.default_config['temperature']),
                'max_tokens': config.get('max_generation_tokens', self.default_config['max_generation_tokens']),
                'enable_proxy': config.get('enable_proxy', {}).get('generation_model', True)
            }

            # Generate final content
            response = await self.model_manager.generate(model_name, params)

            return response
        except Exception as e:
            logger.error(f"Error generating final content: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': ''
            }

    def _extract_reasoning(self, reasoning_result: Dict[str, Any], config: Dict[str, Any]) -> Tuple[str, str]:
        """
        Extract reasoning from the reasoning result.

        Args:
            reasoning_result: The reasoning result
            config: Configuration for extraction

        Returns:
            Tuple of (processed_reasoning, raw_reasoning)
        """
        # Check if the model supports native reasoning
        if config.get('supports_native_reasoning', True):
            # Extract reasoning from reasoning_content field
            raw_reasoning = reasoning_result.get('reasoning_content', '')

            # If reasoning_content is empty, try to extract from content
            if not raw_reasoning:
                content = reasoning_result.get('content', '')

                # Try to extract reasoning from content using tags
                reasoning_tag = config.get('reasoning_tag', '<think>')
                reasoning_end_tag = config.get('reasoning_end_tag', '</think>')

                if reasoning_tag in content and reasoning_end_tag in content:
                    start_idx = content.find(reasoning_tag) + len(reasoning_tag)
                    end_idx = content.find(reasoning_end_tag)
                    if start_idx < end_idx:
                        raw_reasoning = content[start_idx:end_idx].strip()
                else:
                    # If no tags found, use the entire content as reasoning
                    raw_reasoning = content
        else:
            # Extract reasoning from content using tags
            content = reasoning_result.get('content', '')
            reasoning_tag = config.get('reasoning_tag', '<think>')
            reasoning_end_tag = config.get('reasoning_end_tag', '</think>')

            if reasoning_tag in content and reasoning_end_tag in content:
                start_idx = content.find(reasoning_tag) + len(reasoning_tag)
                end_idx = content.find(reasoning_end_tag)
                if start_idx < end_idx:
                    raw_reasoning = content[start_idx:end_idx].strip()
                else:
                    # If tags are malformed, use the entire content as reasoning
                    raw_reasoning = content
            else:
                # If no tags found, use the entire content as reasoning
                raw_reasoning = content

        # Process reasoning (clean up, format, etc.)
        processed_reasoning = raw_reasoning.strip()

        return processed_reasoning, raw_reasoning

    def _generate_cache_key(self,
                           prompt: str,
                           system_message: Optional[str] = None,
                           context: Optional[str] = None,
                           config: Dict[str, Any] = None) -> str:
        """
        Generate a cache key for the given inputs.

        Args:
            prompt: The prompt for generation
            system_message: Optional system message
            context: Optional additional context
            config: Configuration for generation

        Returns:
            Cache key
        """
        # Create a dictionary with the inputs
        cache_dict = {
            'prompt': prompt,
            'system_message': system_message,
            'context': context,
            'reasoning_model': config.get('reasoning_model'),
            'generation_model': config.get('generation_model'),
            'temperature': config.get('temperature')
        }

        # Convert to JSON string and hash
        cache_str = json.dumps(cache_dict, sort_keys=True)
        import hashlib
        cache_key = hashlib.md5(cache_str.encode()).hexdigest()

        return cache_key

    def _add_to_cache(self, key: str, value: Any) -> None:
        """
        Add a value to the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = value
        self.cache_timestamps[key] = time.time()

        # Clean up old cache entries
        self._cleanup_cache()

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self.cache:
            return None

        # Check if the cache entry has expired
        timestamp = self.cache_timestamps.get(key, 0)
        if time.time() - timestamp > self.config.get('cache_ttl', self.default_config['cache_ttl']):
            # Remove expired entry
            del self.cache[key]
            del self.cache_timestamps[key]
            return None

        return self.cache[key]

    def _cleanup_cache(self) -> None:
        """
        Clean up expired cache entries.
        """
        current_time = time.time()
        cache_ttl = self.config.get('cache_ttl', self.default_config['cache_ttl'])

        # Find expired keys
        expired_keys = [
            key for key, timestamp in self.cache_timestamps.items()
            if current_time - timestamp > cache_ttl
        ]

        # Remove expired entries
        for key in expired_keys:
            del self.cache[key]
            del self.cache_timestamps[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
