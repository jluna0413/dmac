"""
Web Scraper for DMac.

This module provides a web scraper for extracting content from websites using Beautiful Soup.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger('dmac.integrations.web_scraper')

class WebScraper:
    """Client for scraping web content."""
    
    def __init__(self):
        """Initialize the web scraper."""
        self.session = None
        logger.info("Web scraper initialized")
    
    async def initialize(self) -> bool:
        """Initialize the client.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            self.session = aiohttp.ClientSession()
            logger.info("Web scraper session initialized")
            return True
        except Exception as e:
            logger.exception(f"Error initializing web scraper: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the client."""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("Web scraper cleaned up")
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL.
        
        Args:
            url: The URL to scrape.
            
        Returns:
            A dictionary containing the scraped content.
        """
        if not self.session:
            await self.initialize()
        
        try:
            logger.info(f"Scraping URL: {url}")
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse the HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract the title
                    title = soup.title.string if soup.title else "No title found"
                    
                    # Extract all article elements
                    articles = []
                    
                    # Look for common article containers
                    article_elements = soup.find_all(['article', 'div', 'section'], 
                                                    class_=['post', 'article', 'entry', 'blog-post'])
                    
                    for article in article_elements[:10]:  # Limit to 10 articles
                        # Extract article title
                        article_title = None
                        title_elem = article.find(['h1', 'h2', 'h3'])
                        if title_elem:
                            article_title = title_elem.get_text(strip=True)
                        
                        # Extract article content
                        content = ""
                        paragraphs = article.find_all('p')
                        for p in paragraphs:
                            content += p.get_text(strip=True) + " "
                        
                        # Extract article date
                        date = None
                        date_elem = article.find(['time', 'span', 'div'], 
                                                class_=['date', 'time', 'published', 'post-date'])
                        if date_elem:
                            date = date_elem.get_text(strip=True)
                        
                        # Extract article URL
                        article_url = None
                        link = article.find('a')
                        if link and link.has_attr('href'):
                            article_url = link['href']
                            # Handle relative URLs
                            if article_url.startswith('/'):
                                article_url = url + article_url
                        
                        # Add the article to the list
                        if article_title and content:
                            articles.append({
                                'title': article_title,
                                'content': content[:500] + "..." if len(content) > 500 else content,
                                'date': date,
                                'url': article_url
                            })
                    
                    # If no articles were found using the above method, try a more general approach
                    if not articles:
                        # Look for headings followed by paragraphs
                        headings = soup.find_all(['h1', 'h2', 'h3'])
                        
                        for heading in headings[:10]:  # Limit to 10 headings
                            article_title = heading.get_text(strip=True)
                            
                            # Get the next paragraphs
                            content = ""
                            next_elem = heading.find_next_sibling()
                            while next_elem and next_elem.name in ['p', 'div']:
                                if next_elem.name == 'p':
                                    content += next_elem.get_text(strip=True) + " "
                                next_elem = next_elem.find_next_sibling()
                            
                            # Add the article to the list
                            if article_title and content:
                                articles.append({
                                    'title': article_title,
                                    'content': content[:500] + "..." if len(content) > 500 else content,
                                    'date': None,
                                    'url': None
                                })
                    
                    logger.info(f"Scraped {len(articles)} articles from {url}")
                    
                    return {
                        'url': url,
                        'title': title,
                        'articles': articles,
                        'timestamp': time.time()
                    }
                else:
                    logger.warning(f"Error scraping {url}: {response.status}")
                    return {
                        'url': url,
                        'error': f"HTTP error: {response.status}",
                        'timestamp': time.time()
                    }
        except Exception as e:
            logger.exception(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def summarize_with_model(self, content: str, model: str) -> str:
        """Summarize content using a model.
        
        Args:
            content: The content to summarize.
            model: The model to use for summarization.
            
        Returns:
            The summarized content.
        """
        try:
            # Import here to avoid circular imports
            from integrations import ollama_client
            
            # Create a prompt for summarization
            prompt = f"""
            Please summarize the following content in 2-3 sentences:
            
            {content}
            """
            
            # Generate a summary using the model
            result = await ollama_client.generate(model, prompt)
            
            return result.get('text', "Failed to generate summary")
        except Exception as e:
            logger.exception(f"Error summarizing content: {e}")
            return f"Error generating summary: {str(e)}"
    
    async def scrape_and_summarize(self, url: str, model: str) -> Dict[str, Any]:
        """Scrape content from a URL and summarize it using a model.
        
        Args:
            url: The URL to scrape.
            model: The model to use for summarization.
            
        Returns:
            A dictionary containing the scraped content and summaries.
        """
        # Scrape the URL
        scraped_data = await self.scrape_url(url)
        
        if 'error' in scraped_data:
            return scraped_data
        
        # Summarize each article
        articles = scraped_data.get('articles', [])
        for article in articles:
            try:
                # Create content for summarization
                content_to_summarize = f"Title: {article['title']}\n\nContent: {article['content']}"
                
                # Generate a summary
                article['summary'] = await self.summarize_with_model(content_to_summarize, model)
                
                # Add a short delay to avoid rate limiting
                await asyncio.sleep(1)
            except Exception as e:
                logger.exception(f"Error summarizing article: {e}")
                article['summary'] = f"Error generating summary: {str(e)}"
        
        # Add the model used for summarization
        scraped_data['model'] = model
        
        logger.info(f"Summarized {len(articles)} articles from {url} using {model}")
        return scraped_data


# Create a singleton instance
web_scraper = WebScraper()
