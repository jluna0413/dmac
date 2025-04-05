"""
Web Search Integration for DMac.

This module provides functionality for searching the web and retrieving information.
"""

import aiohttp
import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from utils.secure_logging import get_logger

logger = get_logger('dmac.integrations.web_search')

class WebSearch:
    """Class for searching the web and retrieving information."""

    def __init__(self):
        """Initialize the web search."""
        self.session = None
        logger.info("Web search initialized")

    async def initialize(self) -> bool:
        """Initialize the web search.

        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            self.session = aiohttp.ClientSession()
            logger.info("Web search initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing web search: {e}")
            return False

    async def cleanup(self) -> None:
        """Clean up resources used by the web search."""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("Web search cleaned up")

    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for information.

        Args:
            query: The search query.
            num_results: The number of results to return.

        Returns:
            A list of search results.
        """
        if not self.session:
            await self.initialize()

        try:
            # Encode the query for URL
            encoded_query = quote_plus(query)
            
            # Use DuckDuckGo as the search engine (more privacy-friendly)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://duckduckgo.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse the HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract search results
                    results = []
                    result_elements = soup.select('.result')
                    
                    for i, result in enumerate(result_elements):
                        if i >= num_results:
                            break
                            
                        # Extract title
                        title_element = result.select_one('.result__title')
                        title = title_element.get_text(strip=True) if title_element else "No title"
                        
                        # Extract URL
                        url_element = result.select_one('.result__url')
                        url = url_element.get_text(strip=True) if url_element else ""
                        if url and not url.startswith(('http://', 'https://')):
                            url = f"https://{url}"
                        
                        # Extract snippet
                        snippet_element = result.select_one('.result__snippet')
                        snippet = snippet_element.get_text(strip=True) if snippet_element else "No description available"
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                    
                    logger.info(f"Found {len(results)} search results for query: {query}")
                    return results
                else:
                    logger.warning(f"Error searching the web: {response.status}")
                    return []
        except Exception as e:
            logger.exception(f"Error searching the web: {e}")
            return []

    async def get_page_content(self, url: str) -> str:
        """Get the content of a web page.

        Args:
            url: The URL of the page to get.

        Returns:
            The content of the page.
        """
        if not self.session:
            await self.initialize()

        try:
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse the HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                    
                    # Get text
                    text = soup.get_text()
                    
                    # Break into lines and remove leading and trailing space on each
                    lines = (line.strip() for line in text.splitlines())
                    
                    # Break multi-headlines into a line each
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    
                    # Drop blank lines
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    logger.info(f"Retrieved content from {url}")
                    return text
                else:
                    logger.warning(f"Error getting page content: {response.status}")
                    return f"Error: Could not retrieve content from {url} (Status code: {response.status})"
        except Exception as e:
            logger.exception(f"Error getting page content: {e}")
            return f"Error: Could not retrieve content from {url} ({str(e)})"

    async def search_and_summarize(self, query: str, num_results: int = 3) -> str:
        """Search the web and summarize the results.

        Args:
            query: The search query.
            num_results: The number of results to summarize.

        Returns:
            A summary of the search results.
        """
        if not self.session:
            await self.initialize()

        try:
            # Search for results
            results = await self.search(query, num_results)
            
            if not results:
                return f"No results found for query: {query}"
            
            # Build a summary
            summary = f"### Web Search Results for: {query}\n\n"
            
            for i, result in enumerate(results):
                summary += f"**{i+1}. {result['title']}**\n"
                summary += f"URL: {result['url']}\n"
                summary += f"Summary: {result['snippet']}\n\n"
            
            # Get content from the first result for more details
            if results and 'url' in results[0] and results[0]['url']:
                content = await self.get_page_content(results[0]['url'])
                
                # Truncate content to a reasonable length
                if len(content) > 2000:
                    content = content[:2000] + "...\n\n(Content truncated for brevity)"
                
                summary += f"### Detailed content from top result:\n\n{content}\n"
            
            logger.info(f"Generated summary for query: {query}")
            return summary
        except Exception as e:
            logger.exception(f"Error searching and summarizing: {e}")
            return f"Error searching the web: {str(e)}"


# Create a singleton instance
web_search = WebSearch()
