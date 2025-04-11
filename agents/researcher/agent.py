"""
AI Researcher Agent - Agent for conducting research and gathering information

This module provides an agent for conducting research, gathering information from the web,
and synthesizing findings into comprehensive reports.
"""

import logging
import json
import os
import re
import time
from typing import Dict, List, Any, Optional, Tuple
import asyncio

from agents.base_agent import BaseAgent
from utils.web_research import WebResearch
from utils.web_scraper import WebScraper
from integrations.ollama_client import OllamaClient

# Set up logging
logger = logging.getLogger('dmac.researcher.agent')

class ResearcherAgent(BaseAgent):
    """
    Agent for conducting research and gathering information.
    """
    
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any] = None):
        """
        Initialize the Researcher agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            config: Configuration for the agent
        """
        super().__init__(agent_id, name, agent_type="researcher", config=config)
        
        # Default configuration
        self.default_config = {
            'model_name': 'gemma3:12b',
            'max_sources': 5,
            'max_depth': 2,
            'temperature': 0.7,
            'search_engine': 'duckduckgo',
            'report_format': 'markdown',
            'cache_results': True,
            'cache_dir': 'data/research_cache'
        }
        
        # Merge default config with provided config
        self.config = {**self.default_config, **(config or {})}
        
        # Initialize the model provider
        self.model_provider = OllamaModelProvider(
            model_name=self.config['model_name'],
            temperature=self.config['temperature']
        )
        
        # Initialize the web research utility
        self.web_research = WebResearch()
        
        # Initialize the web scraper
        self.web_scraper = WebScraper()
        
        # Create cache directory if it doesn't exist
        if self.config['cache_results']:
            os.makedirs(self.config['cache_dir'], exist_ok=True)
        
        # Set up capabilities
        self.capabilities = [
            "web_search",
            "web_scraping",
            "information_synthesis",
            "report_generation",
            "trend_analysis",
            "fact_checking",
            "source_evaluation"
        ]
        
        # Research cache
        self.research_cache = {}
        
        # Active research tasks
        self.active_tasks = {}
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message sent to the agent.
        
        Args:
            message: Message to process
            
        Returns:
            Response message
        """
        try:
            # Extract message content
            content = message.get('content', '')
            action = message.get('action', 'chat')
            data = message.get('data', {})
            
            # Process based on the action
            if action == 'chat':
                # General chat interaction
                response_text = await self._handle_chat(content)
                return {
                    'success': True,
                    'content': response_text,
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'research_topic':
                # Research a topic
                topic = data.get('topic', content)
                max_sources = data.get('max_sources', self.config['max_sources'])
                max_depth = data.get('max_depth', self.config['max_depth'])
                
                # Start the research task
                task_id = f"research_{int(time.time())}"
                self.active_tasks[task_id] = {
                    'status': 'in_progress',
                    'topic': topic,
                    'start_time': time.time()
                }
                
                # Run the research task in the background
                asyncio.create_task(self._research_topic_task(task_id, topic, max_sources, max_depth))
                
                return {
                    'success': True,
                    'content': f"I've started researching '{topic}'. This may take a few moments. You can check the status with task ID: {task_id}",
                    'data': {'task_id': task_id},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            elif action == 'get_task_status':
                # Get the status of a research task
                task_id = data.get('task_id', '')
                
                if not task_id:
                    return {
                        'success': False,
                        'content': "Please provide a task ID to check the status.",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                
                if task_id in self.active_tasks:
                    task = self.active_tasks[task_id]
                    
                    return {
                        'success': True,
                        'content': f"Research task '{task['topic']}' is {task['status']}.",
                        'data': {'task': task},
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                else:
                    return {
                        'success': False,
                        'content': f"No research task found with ID: {task_id}",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
            
            elif action == 'scrape_website':
                # Scrape a specific website
                url = data.get('url', content)
                max_articles = data.get('max_articles', 5)
                
                # Scrape the website
                success, site_data = await asyncio.to_thread(
                    self.web_scraper.scrape_news_site,
                    url,
                    max_articles=max_articles
                )
                
                if success:
                    return {
                        'success': True,
                        'content': f"Successfully scraped {len(site_data.get('articles', []))} articles from {url}",
                        'data': {'site_data': site_data},
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                else:
                    return {
                        'success': False,
                        'content': f"Failed to scrape {url}: {site_data}",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
            
            elif action == 'search_web':
                # Search the web
                query = data.get('query', content)
                num_results = data.get('num_results', 5)
                
                # Search the web
                success, results = await asyncio.to_thread(
                    self.web_research.search_web,
                    query,
                    num_results=num_results
                )
                
                if success:
                    return {
                        'success': True,
                        'content': f"Found {len(results)} results for '{query}'",
                        'data': {'results': results},
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                else:
                    return {
                        'success': False,
                        'content': f"Failed to search for '{query}': {results}",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
            
            elif action == 'generate_report':
                # Generate a report from research data
                research_data = data.get('research_data', {})
                report_format = data.get('report_format', self.config['report_format'])
                
                if not research_data:
                    return {
                        'success': False,
                        'content': "Please provide research data to generate a report.",
                        'agent_id': self.agent_id,
                        'agent_name': self.name
                    }
                
                # Generate the report
                report = await self._generate_report(research_data, report_format)
                
                return {
                    'success': True,
                    'content': "Here's your research report:",
                    'data': {'report': report},
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
            
            else:
                # Unknown action
                return {
                    'success': False,
                    'content': f"Unknown action: {action}",
                    'agent_id': self.agent_id,
                    'agent_name': self.name
                }
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'success': False,
                'content': f"Error processing message: {str(e)}",
                'agent_id': self.agent_id,
                'agent_name': self.name
            }
    
    async def _handle_chat(self, content: str) -> str:
        """
        Handle a general chat message.
        
        Args:
            content: Message content
            
        Returns:
            Response text
        """
        # Analyze the message to determine the intent
        if any(keyword in content.lower() for keyword in ['research', 'find information', 'gather data']):
            # Research intent
            topic = content.split('research')[-1].split('find information')[-1].split('gather data')[-1].strip()
            
            # Start a research task
            task_id = f"research_{int(time.time())}"
            self.active_tasks[task_id] = {
                'status': 'in_progress',
                'topic': topic,
                'start_time': time.time()
            }
            
            # Run the research task in the background
            asyncio.create_task(self._research_topic_task(task_id, topic, self.config['max_sources'], self.config['max_depth']))
            
            return f"I'll research '{topic}' for you. This may take a few moments. I'll let you know when I have results (Task ID: {task_id})."
        
        elif any(keyword in content.lower() for keyword in ['scrape', 'extract from', 'get data from']):
            # Web scraping intent
            url_match = re.search(r'https?://[^\s]+', content)
            
            if url_match:
                url = url_match.group(0)
                
                # Scrape the website
                success, site_data = await asyncio.to_thread(
                    self.web_scraper.scrape_news_site,
                    url,
                    max_articles=5
                )
                
                if success:
                    articles = site_data.get('articles', [])
                    
                    if articles:
                        response = f"I found {len(articles)} articles on {url}:\n\n"
                        
                        for i, article in enumerate(articles[:3], 1):
                            title = article.get('title', 'Untitled')
                            date = article.get('date_published', 'Unknown date')
                            
                            response += f"{i}. {title} ({date})\n"
                        
                        if len(articles) > 3:
                            response += f"\nAnd {len(articles) - 3} more articles."
                        
                        return response
                    else:
                        return f"I scraped {url} but didn't find any articles."
                else:
                    return f"I couldn't scrape {url}: {site_data}"
            else:
                return "I'd be happy to scrape a website for you. Please provide a URL to scrape."
        
        elif any(keyword in content.lower() for keyword in ['search', 'look up', 'find']):
            # Web search intent
            query = content.split('search')[-1].split('look up')[-1].split('find')[-1].strip()
            
            # Search the web
            success, results = await asyncio.to_thread(
                self.web_research.search_web,
                query,
                num_results=5
            )
            
            if success:
                if results:
                    response = f"Here are some search results for '{query}':\n\n"
                    
                    for i, result in enumerate(results[:5], 1):
                        title = result.get('title', 'Untitled')
                        url = result.get('url', '')
                        snippet = result.get('snippet', '')
                        
                        response += f"{i}. {title}\n   URL: {url}\n   {snippet}\n\n"
                    
                    return response
                else:
                    return f"I searched for '{query}' but didn't find any results."
            else:
                return f"I couldn't search for '{query}': {results}"
        
        else:
            # General chat
            prompt = f"You are Ari, an AI research assistant. Respond to the following message:\n\n{content}"
            response = await self.model_provider.generate(prompt)
            return response
    
    async def _research_topic_task(self, task_id: str, topic: str, max_sources: int, max_depth: int) -> None:
        """
        Background task to research a topic.
        
        Args:
            task_id: ID of the task
            topic: Topic to research
            max_sources: Maximum number of sources to use
            max_depth: Maximum depth of research
        """
        try:
            # Check if we have cached results
            cache_key = f"{topic}_{max_sources}_{max_depth}"
            
            if self.config['cache_results'] and cache_key in self.research_cache:
                # Use cached results
                research_data = self.research_cache[cache_key]
                
                # Update task status
                self.active_tasks[task_id]['status'] = 'completed'
                self.active_tasks[task_id]['end_time'] = time.time()
                self.active_tasks[task_id]['research_data'] = research_data
                
                logger.info(f"Used cached research results for '{topic}'")
                return
            
            # Research the topic
            success, research_data = await asyncio.to_thread(
                self.web_research.research_topic,
                topic,
                max_sources=max_sources,
                max_depth=max_depth
            )
            
            if success:
                # Generate a report
                report = await self._generate_report(research_data, self.config['report_format'])
                
                # Update task status
                self.active_tasks[task_id]['status'] = 'completed'
                self.active_tasks[task_id]['end_time'] = time.time()
                self.active_tasks[task_id]['research_data'] = research_data
                self.active_tasks[task_id]['report'] = report
                
                # Cache the results
                if self.config['cache_results']:
                    self.research_cache[cache_key] = research_data
                    
                    # Save to disk
                    cache_file = os.path.join(self.config['cache_dir'], f"{cache_key.replace(' ', '_')}.json")
                    with open(cache_file, 'w') as f:
                        json.dump(research_data, f)
                
                logger.info(f"Completed research on '{topic}'")
            else:
                # Update task status
                self.active_tasks[task_id]['status'] = 'failed'
                self.active_tasks[task_id]['end_time'] = time.time()
                self.active_tasks[task_id]['error'] = research_data  # Error message
                
                logger.error(f"Failed to research '{topic}': {research_data}")
        
        except Exception as e:
            # Update task status
            self.active_tasks[task_id]['status'] = 'failed'
            self.active_tasks[task_id]['end_time'] = time.time()
            self.active_tasks[task_id]['error'] = str(e)
            
            logger.error(f"Error researching '{topic}': {str(e)}")
    
    async def _generate_report(self, research_data: Dict[str, Any], report_format: str) -> str:
        """
        Generate a report from research data.
        
        Args:
            research_data: Research data
            report_format: Format of the report
            
        Returns:
            Generated report
        """
        # Extract information from research data
        query = research_data.get('query', '')
        sources = research_data.get('sources', [])
        
        # Create a prompt for the model
        prompt = f"Generate a comprehensive research report on '{query}' based on the following sources:\n\n"
        
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Untitled')
            url = source.get('url', '')
            content = source.get('content', '')
            date = source.get('date_published', '')
            
            prompt += f"Source {i}: {title}\n"
            prompt += f"URL: {url}\n"
            prompt += f"Date: {date}\n"
            
            # Limit content length to avoid token limits
            max_content_length = 1000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            prompt += f"Content: {content}\n\n"
        
        prompt += f"Format the report in {report_format} format. Include:\n"
        prompt += "1. An executive summary\n"
        prompt += "2. Key findings\n"
        prompt += "3. Detailed analysis\n"
        prompt += "4. Conclusions\n"
        prompt += "5. References (cite all sources)\n\n"
        prompt += "Make the report comprehensive, well-structured, and based solely on the provided sources."
        
        # Generate the report
        report = await self.model_provider.generate(prompt)
        
        return report
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to the agent.
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
        """
        task_type = task.get('type', '')
        task_data = task.get('data', {})
        
        if task_type == 'research':
            # Research a topic
            topic = task_data.get('topic', '')
            max_sources = task_data.get('max_sources', self.config['max_sources'])
            max_depth = task_data.get('max_depth', self.config['max_depth'])
            
            if not topic:
                return {
                    'success': False,
                    'result': "No topic provided for research task",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            
            # Research the topic
            success, research_data = await asyncio.to_thread(
                self.web_research.research_topic,
                topic,
                max_sources=max_sources,
                max_depth=max_depth
            )
            
            if success:
                # Generate a report
                report = await self._generate_report(research_data, self.config['report_format'])
                
                return {
                    'success': True,
                    'result': report,
                    'data': {'research_data': research_data},
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            else:
                return {
                    'success': False,
                    'result': f"Failed to research '{topic}': {research_data}",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
        
        elif task_type == 'web_scrape':
            # Scrape a website
            url = task_data.get('url', '')
            max_articles = task_data.get('max_articles', 5)
            
            if not url:
                return {
                    'success': False,
                    'result': "No URL provided for web scraping task",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            
            # Scrape the website
            success, site_data = await asyncio.to_thread(
                self.web_scraper.scrape_news_site,
                url,
                max_articles=max_articles
            )
            
            if success:
                return {
                    'success': True,
                    'result': f"Successfully scraped {len(site_data.get('articles', []))} articles from {url}",
                    'data': {'site_data': site_data},
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            else:
                return {
                    'success': False,
                    'result': f"Failed to scrape {url}: {site_data}",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
        
        elif task_type == 'fact_check':
            # Fact check a statement
            statement = task_data.get('statement', '')
            
            if not statement:
                return {
                    'success': False,
                    'result': "No statement provided for fact checking task",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            
            # Research the statement
            success, research_data = await asyncio.to_thread(
                self.web_research.research_topic,
                statement,
                max_sources=3,
                max_depth=1
            )
            
            if success:
                # Create a prompt for fact checking
                prompt = f"Fact check the following statement based on the provided sources:\n\n"
                prompt += f"Statement: {statement}\n\n"
                
                sources = research_data.get('sources', [])
                for i, source in enumerate(sources, 1):
                    title = source.get('title', 'Untitled')
                    url = source.get('url', '')
                    content = source.get('content', '')
                    
                    prompt += f"Source {i}: {title}\n"
                    prompt += f"URL: {url}\n"
                    
                    # Limit content length
                    max_content_length = 500
                    if len(content) > max_content_length:
                        content = content[:max_content_length] + "..."
                    
                    prompt += f"Content: {content}\n\n"
                
                prompt += "Provide a fact check result with the following information:\n"
                prompt += "1. Verdict (True, False, Partially True, Unverifiable)\n"
                prompt += "2. Explanation of the verdict\n"
                prompt += "3. Supporting evidence from the sources\n"
                prompt += "4. Any missing context or nuance\n"
                
                # Generate the fact check
                fact_check = await self.model_provider.generate(prompt)
                
                return {
                    'success': True,
                    'result': fact_check,
                    'data': {'research_data': research_data},
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
            else:
                return {
                    'success': False,
                    'result': f"Failed to fact check '{statement}': {research_data}",
                    'task_id': task.get('task_id'),
                    'agent_id': self.agent_id
                }
        
        else:
            # Unknown task type
            return {
                'success': False,
                'result': f"Unknown task type: {task_type}",
                'task_id': task.get('task_id'),
                'agent_id': self.agent_id
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the agent.
        
        Returns:
            Agent status
        """
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'type': 'researcher',
            'status': 'active',
            'capabilities': self.capabilities,
            'model_name': self.config['model_name'],
            'active_tasks': len(self.active_tasks),
            'cache_size': len(self.research_cache)
        }
    
    def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the agent configuration.
        
        Args:
            config: New configuration
            
        Returns:
            Updated configuration
        """
        # Update configuration
        self.config.update(config)
        
        # Update model provider if model name changed
        if 'model_name' in config:
            self.model_provider = OllamaModelProvider(
                model_name=self.config['model_name'],
                temperature=self.config['temperature']
            )
        
        # Create cache directory if it doesn't exist and caching is enabled
        if self.config['cache_results']:
            os.makedirs(self.config['cache_dir'], exist_ok=True)
        
        return self.config

class OllamaModelProvider:
    """Model provider using Ollama for LLM capabilities."""
    
    def __init__(self, model_name: str = "gemma3:12b", temperature: float = 0.7):
        """
        Initialize the Ollama model provider.
        
        Args:
            model_name: Name of the Ollama model to use
            temperature: Temperature for generation
        """
        self.model_name = model_name
        self.temperature = temperature
        self.ollama_client = OllamaClient()
    
    async def generate(self, prompt: str) -> str:
        """
        Generate text using the Ollama model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        try:
            result = await self.ollama_client.generate(
                self.model_name, 
                prompt,
                temperature=self.temperature
            )
            
            if 'error' in result:
                logger.error(f"Error generating text: {result['error']}")
                return f"Error: {result['error']}"
            
            return result.get('text', "")
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: {str(e)}"
