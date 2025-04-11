"""
Tasks package for DMac.

This package provides task definitions and execution for the DMac system.
"""

from .task_types import (
    ALL_TASKS,
    WEB_SCRAPING_TASKS,
    TEXT_ANALYSIS_TASKS,
    CODE_GENERATION_TASKS,
    REASONING_TASKS,
    CONVERSATION_TASKS,
    get_task_by_id,
    get_tasks_by_type,
    get_all_tasks
)
from .task_executor import task_executor

__all__ = [
    'ALL_TASKS',
    'WEB_SCRAPING_TASKS',
    'TEXT_ANALYSIS_TASKS',
    'CODE_GENERATION_TASKS',
    'REASONING_TASKS',
    'CONVERSATION_TASKS',
    'get_task_by_id',
    'get_tasks_by_type',
    'get_all_tasks',
    'task_executor'
]
