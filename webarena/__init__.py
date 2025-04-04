"""
WebArena package for DMac.

This package provides integration with WebArena for agent evaluation.
"""

from webarena.webarena_manager import webarena_manager
from webarena.ollama_integration import webarena_ollama_integration
from webarena.webarena_api import setup_webarena_routes
from webarena.visualization import webarena_visualization

__all__ = [
    'webarena_manager',
    'webarena_ollama_integration',
    'setup_webarena_routes',
    'webarena_visualization',
]
