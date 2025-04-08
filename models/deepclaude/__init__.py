"""
DeepClaude Module for DMac

This module provides the core functionality of DeepClaude, combining DeepSeek R1 for reasoning
with Claude 3.7 Sonnet (or other models) for refinement and generation.
"""

from models.deepclaude.deepclaude_module import DeepClaudeModule

__all__ = ['DeepClaudeModule']
