"""
Model types for DMac.
"""

from enum import Enum


class ModelType(Enum):
    """Enum representing the type of model."""
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    LOCAL = "local"
