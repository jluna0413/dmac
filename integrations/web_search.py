"""
Web Search Integration for DMac.

This module provides functionality for searching the web and retrieving information.
"""

import aiohttp
import asyncio
import json
import logging
import re
import time
from typing import Dict, List, Optional, Any, Tuple, Literal
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlencode
from datetime import datetime, timedelta

from utils.secure_logging import get_logger

logger = get_logger('dmac.integrations.web_search')

class SearchResult:
    """Class representing a search result."""

    def __init__(self, title: str, url: str, snippet: str, source: str):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source  # Which search engine provided this result
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'url': self.url,
            'snippet': self.snippet,
            'source': self.source,
            'timestamp': self.timestamp.isoformat()
        }

class SearchCache:
    """Class for caching search results."""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """Initialize the search cache.

        Args:
            max_size: Maximum number of queries to cache.
            ttl_seconds: Time to live for cache entries in seconds.
        """
        self.cache: Dict[str, Tuple[List[SearchResult], datetime]] = {}
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, query: str) -> Optional[List[SearchResult]]:
        """Get cached results for a query.

        Args:
            query: The search query.

        Returns:
            The cached results, or None if not found or expired.
        """
        normalized_query = query.lower().strip()
        if normalized_query in self.cache:
            results, timestamp = self.cache[normalized_query]
            if datetime.now() - timestamp < self.ttl:
                logger.info(f"Cache hit for query: {query}")
                return results
            else:
                # Remove expired entry
                del self.cache[normalized_query]
        return None

    def set(self, query: str, results: List[SearchResult]) -> None:
        """Set cached results for a query.

        Args:
            query: The search query.
            results: The search results.
        """
        normalized_query = query.lower().strip()
        self.cache[normalized_query] = (results, datetime.now())

        # Trim cache if it's too large
        if len(self.cache) > self.max_size:
            # Remove oldest entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
            for i in range(len(self.cache) - self.max_size):
                del self.cache[sorted_items[i][0]]

class WebSearch:
    """Class for searching the web and retrieving information."""

    def __init__(self):
        """Initialize the web search."""
        self.session = None
        self.cache = SearchCache()
        self.search_engines = ['duckduckgo', 'google']
        self.default_engine = 'duckduckgo'  # More privacy-friendly default
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

    async def search(self, query: str, num_results: int = 5, engine: str = None) -> List[Dict[str, Any]]:
        """Search the web for information.

        Args:
            query: The search query.
            num_results: The number of results to return.
            engine: The search engine to use. If None, uses the default engine.

        Returns:
            A list of search results.
        """
        if not self.session:
            await self.initialize()

        # Check cache first
        cached_results = self.cache.get(query)
        if cached_results:
            # Convert SearchResult objects to dictionaries
            return [result.to_dict() for result in cached_results[:num_results]]

        # Use specified engine or default
        engine = engine or self.default_engine
        if engine not in self.search_engines:
            logger.warning(f"Unknown search engine: {engine}. Using {self.default_engine} instead.")
            engine = self.default_engine

        try:
            results = []

            if engine == 'duckduckgo':
                duck_results = await self._search_duckduckgo(query, num_results)
                results.extend(duck_results)
            elif engine == 'google':
                google_results = await self._search_google(query, num_results)
                results.extend(google_results)

            # Cache the results
            if results:
                self.cache.set(query, results)

            # Convert SearchResult objects to dictionaries
            return [result.to_dict() for result in results]
        except Exception as e:
            logger.exception(f"Error searching the web: {e}")
            return []

    async def _search_duckduckgo(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Search DuckDuckGo for information.

        Args:
            query: The search query.
            num_results: The number of results to return.

        Returns:
            A list of search results.
        """
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

                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source='DuckDuckGo'
                        ))

                    logger.info(f"Found {len(results)} DuckDuckGo search results for query: {query}")
                    return results
                else:
                    logger.warning(f"Error searching DuckDuckGo: {response.status}")
                    return []
        except Exception as e:
            logger.exception(f"Error searching DuckDuckGo: {e}")
            return []

    async def _search_google(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Search Google for information.

        Args:
            query: The search query.
            num_results: The number of results to return.

        Returns:
            A list of search results.
        """
        try:
            # Encode the query for URL
            params = {
                'q': query,
                'num': min(num_results + 2, 10),  # Google sometimes includes non-result elements
                'hl': 'en',
                'gl': 'us'
            }
            url = f"https://www.google.com/search?{urlencode(params)}"

            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
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
                    # Google search results are in divs with class 'g'
                    result_elements = soup.select('div.g')

                    for i, result in enumerate(result_elements):
                        if i >= num_results:
                            break

                        # Extract title
                        title_element = result.select_one('h3')
                        title = title_element.get_text(strip=True) if title_element else "No title"

                        # Extract URL
                        url_element = result.select_one('a')
                        url = url_element.get('href', '') if url_element else ""
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        elif not url.startswith(('http://', 'https://')):
                            continue  # Skip results without valid URLs

                        # Extract snippet
                        snippet_element = result.select_one('div.VwiC3b')
                        snippet = snippet_element.get_text(strip=True) if snippet_element else "No description available"

                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source='Google'
                        ))

                    logger.info(f"Found {len(results)} Google search results for query: {query}")
                    return results
                else:
                    logger.warning(f"Error searching Google: {response.status}")
                    return []
        except Exception as e:
            logger.exception(f"Error searching Google: {e}")
            return []

    async def get_page_content(self, url: str, max_length: int = 10000) -> str:
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

                    # Extract main content (prioritize article content)
                    main_content = soup.select_one('article, main, #content, .content, .article, .post')
                    if main_content:
                        # Get text from main content
                        text = main_content.get_text()
                    else:
                        # Fallback to body text
                        text = soup.get_text()

                    # Break into lines and remove leading and trailing space on each
                    lines = (line.strip() for line in text.splitlines())

                    # Break multi-headlines into a line each
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

                    # Drop blank lines
                    text = '\n'.join(chunk for chunk in chunks if chunk)

                    # Limit length
                    if len(text) > max_length:
                        text = text[:max_length] + "...\n\n(Content truncated for brevity)"

                    logger.info(f"Retrieved content from {url}")
                    return text
                else:
                    logger.warning(f"Error getting page content: {response.status}")
                    return f"Error: Could not retrieve content from {url} (Status code: {response.status})"
        except Exception as e:
            logger.exception(f"Error getting page content: {e}")
            return f"Error: Could not retrieve content from {url} ({str(e)})"

    async def search_and_summarize(self, query: str, num_results: int = 3, engine: str = None) -> str:
        """Search the web and summarize the results.

        Args:
            query: The search query.
            num_results: The number of results to summarize.
            engine: The search engine to use. If None, uses the default engine.

        Returns:
            A summary of the search results.
        """
        if not self.session:
            await self.initialize()

        try:
            # Search for results
            results = await self.search(query, num_results, engine)

            if not results:
                return f"No results found for query: {query}"

            # Build a summary
            summary = f"### Web Search Results for: {query}\n\n"

            for i, result in enumerate(results):
                summary += f"**{i+1}. {result['title']}**\n"
                summary += f"Source: {result['source']} | URL: [{result['url']}]({result['url']})\n"
                summary += f"Summary: {result['snippet']}\n\n"

            # Get content from the first result for more details
            if results and 'url' in results[0] and results[0]['url']:
                content = await self.get_page_content(results[0]['url'])

                # Truncate content to a reasonable length
                if len(content) > 2000:
                    content = content[:2000] + "...\n\n(Content truncated for brevity)"

                summary += f"### Detailed content from top result ({results[0]['source']}):\n\n{content}\n"
                summary += f"\nSource: [{results[0]['url']}]({results[0]['url']})\n"

            # Add timestamp
            summary += f"\n\n*Search performed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

            logger.info(f"Generated summary for query: {query}")
            return summary
        except Exception as e:
            logger.exception(f"Error searching and summarizing: {e}")
            return f"Error searching the web: {str(e)}"


# Create a singleton instance
web_search = WebSearch()
