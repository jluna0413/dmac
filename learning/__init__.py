"""
Learning package for DMac.

This package provides learning capabilities for the DMac system.
"""

from learning.learning_system import learning_system, ModelType
from learning.reinforcement_learning import reinforcement_learning
from learning.transfer_learning import transfer_learning
from learning.learning_manager import learning_manager

__all__ = [
    'learning_system',
    'ModelType',
    'reinforcement_learning',
    'transfer_learning',
    'learning_manager',
]
