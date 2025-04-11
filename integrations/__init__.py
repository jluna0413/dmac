"""
Integrations package for DMac.

This package provides integrations with external systems.
"""

from .ollama_client import ollama_client
from .webarena_client import webarena_client
from .web_scraper import web_scraper
from .voice_interaction import voice_interaction

__all__ = ['ollama_client', 'webarena_client', 'web_scraper', 'voice_interaction']