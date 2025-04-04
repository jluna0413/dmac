"""
Task Types for DMac.

This module defines different task types for testing agent performance.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger('dmac.tasks.task_types')

# Web Scraping Tasks
WEB_SCRAPING_TASKS = [
    {
        'id': 'scrape_ai_news',
        'name': 'Scrape AI News',
        'description': 'Scrape and summarize the latest 10 articles from InTheWorldOfAI.com',
        'type': 'web_scraping',
        'url': 'https://intheworldofai.com/',
        'complexity': 'medium',
        'metrics': ['accuracy', 'completeness', 'summarization_quality']
    },
    {
        'id': 'scrape_tech_news',
        'name': 'Scrape Tech News',
        'description': 'Scrape and summarize the latest 10 articles from TechCrunch',
        'type': 'web_scraping',
        'url': 'https://techcrunch.com/',
        'complexity': 'medium',
        'metrics': ['accuracy', 'completeness', 'summarization_quality']
    },
    {
        'id': 'scrape_research_papers',
        'name': 'Scrape Research Papers',
        'description': 'Scrape and summarize the latest 10 AI research papers from arXiv',
        'type': 'web_scraping',
        'url': 'https://arxiv.org/list/cs.AI/recent',
        'complexity': 'high',
        'metrics': ['accuracy', 'technical_understanding', 'summarization_quality']
    },
    {
        'id': 'search_github_projects',
        'name': 'Search GitHub Projects',
        'description': 'Search for free and open-source projects on GitHub that could enhance our system',
        'type': 'web_scraping',
        'url': 'https://github.com/topics/ai-agents',
        'complexity': 'high',
        'metrics': ['relevance', 'compatibility_analysis', 'agent_suitability']
    },
    {
        'id': 'search_gitlab_projects',
        'name': 'Search GitLab Projects',
        'description': 'Search for free and open-source projects on GitLab that could enhance our system',
        'type': 'web_scraping',
        'url': 'https://gitlab.com/explore/projects/topics/ai',
        'complexity': 'high',
        'metrics': ['relevance', 'compatibility_analysis', 'agent_suitability']
    }
]

# Text Analysis Tasks
TEXT_ANALYSIS_TASKS = [
    {
        'id': 'sentiment_analysis',
        'name': 'Sentiment Analysis',
        'description': 'Analyze the sentiment of customer reviews',
        'type': 'text_analysis',
        'data_source': 'amazon_reviews.json',
        'complexity': 'medium',
        'metrics': ['accuracy', 'precision', 'recall']
    },
    {
        'id': 'topic_classification',
        'name': 'Topic Classification',
        'description': 'Classify news articles into topics',
        'type': 'text_analysis',
        'data_source': 'news_articles.json',
        'complexity': 'medium',
        'metrics': ['accuracy', 'f1_score', 'confusion_matrix']
    },
    {
        'id': 'named_entity_recognition',
        'name': 'Named Entity Recognition',
        'description': 'Extract named entities from text',
        'type': 'text_analysis',
        'data_source': 'wikipedia_articles.json',
        'complexity': 'high',
        'metrics': ['precision', 'recall', 'f1_score']
    }
]

# Code Generation Tasks
CODE_GENERATION_TASKS = [
    {
        'id': 'python_function',
        'name': 'Python Function Generation',
        'description': 'Generate Python functions based on descriptions',
        'type': 'code_generation',
        'language': 'python',
        'complexity': 'medium',
        'metrics': ['correctness', 'efficiency', 'readability']
    },
    {
        'id': 'javascript_component',
        'name': 'JavaScript Component Generation',
        'description': 'Generate React components based on descriptions',
        'type': 'code_generation',
        'language': 'javascript',
        'complexity': 'high',
        'metrics': ['correctness', 'efficiency', 'readability']
    },
    {
        'id': 'sql_query',
        'name': 'SQL Query Generation',
        'description': 'Generate SQL queries based on descriptions',
        'type': 'code_generation',
        'language': 'sql',
        'complexity': 'medium',
        'metrics': ['correctness', 'efficiency', 'readability']
    }
]

# Reasoning Tasks
REASONING_TASKS = [
    {
        'id': 'logical_reasoning',
        'name': 'Logical Reasoning',
        'description': 'Solve logical puzzles and problems',
        'type': 'reasoning',
        'complexity': 'high',
        'metrics': ['accuracy', 'step_by_step_reasoning', 'time_to_solution']
    },
    {
        'id': 'mathematical_reasoning',
        'name': 'Mathematical Reasoning',
        'description': 'Solve mathematical problems',
        'type': 'reasoning',
        'complexity': 'high',
        'metrics': ['accuracy', 'step_by_step_reasoning', 'time_to_solution']
    },
    {
        'id': 'common_sense_reasoning',
        'name': 'Common Sense Reasoning',
        'description': 'Answer questions requiring common sense',
        'type': 'reasoning',
        'complexity': 'medium',
        'metrics': ['accuracy', 'relevance', 'completeness']
    }
]

# Conversation Tasks
CONVERSATION_TASKS = [
    {
        'id': 'customer_support',
        'name': 'Customer Support',
        'description': 'Handle customer support conversations',
        'type': 'conversation',
        'complexity': 'medium',
        'metrics': ['helpfulness', 'empathy', 'accuracy']
    },
    {
        'id': 'interview_simulation',
        'name': 'Interview Simulation',
        'description': 'Simulate a job interview conversation',
        'type': 'conversation',
        'complexity': 'high',
        'metrics': ['relevance', 'coherence', 'engagement']
    },
    {
        'id': 'debate',
        'name': 'Debate',
        'description': 'Engage in a debate on a controversial topic',
        'type': 'conversation',
        'complexity': 'high',
        'metrics': ['argument_quality', 'evidence_use', 'persuasiveness']
    }
]

# All Tasks
ALL_TASKS = (
    WEB_SCRAPING_TASKS +
    TEXT_ANALYSIS_TASKS +
    CODE_GENERATION_TASKS +
    REASONING_TASKS +
    CONVERSATION_TASKS
)

def get_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
    """Get a task by ID.

    Args:
        task_id: The ID of the task to get.

    Returns:
        The task, or None if not found.
    """
    for task in ALL_TASKS:
        if task['id'] == task_id:
            return task
    return None

def get_tasks_by_type(task_type: str) -> List[Dict[str, Any]]:
    """Get tasks by type.

    Args:
        task_type: The type of tasks to get.

    Returns:
        A list of tasks of the specified type.
    """
    return [task for task in ALL_TASKS if task['type'] == task_type]

def get_all_tasks() -> List[Dict[str, Any]]:
    """Get all tasks.

    Returns:
        A list of all tasks.
    """
    return ALL_TASKS
