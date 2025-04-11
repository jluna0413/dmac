"""
Web Research Module for DMac

This module provides web research capabilities for the chat interface.
"""

import logging
import re
import json
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from utils.web_scraper import WebScraper

# Set up logging
logger = logging.getLogger('dmac.web_research')

class WebResearch:
    """Web research utility for retrieving information from the web."""
    
    def __init__(self):
        """Initialize the web research utility."""
        self.scraper = WebScraper()
    
    def search_web(self, query, num_results=5):
        """
        Search the web for information.
        
        Args:
            query (str): The search query.
            num_results (int, optional): Number of search results to return. Defaults to 5.
            
        Returns:
            tuple: (success (bool), results (list) or error message (str))
        """
        try:
            # Encode the query for URL
            encoded_query = quote_plus(query)
            
            # Use DuckDuckGo as the search engine (more scraping-friendly than Google)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Get the search results page
            response = requests.get(
                search_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            response.raise_for_status()
            
            # Parse the search results
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results
            for result in soup.select('.result'):
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                url_elem = result.select_one('.result__url')
                
                if title_elem and url_elem:
                    title = title_elem.get_text(strip=True)
                    url = url_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # Ensure URL is properly formatted
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
                    
                    if len(results) >= num_results:
                        break
            
            return True, results
        except Exception as e:
            logger.error(f"Error searching the web: {str(e)}")
            return False, str(e)
    
    def research_topic(self, query, max_sources=3, max_depth=1):
        """
        Research a topic by searching the web and scraping relevant pages.
        
        Args:
            query (str): The research query.
            max_sources (int, optional): Maximum number of sources to scrape. Defaults to 3.
            max_depth (int, optional): Maximum depth of link following. Defaults to 1.
            
        Returns:
            tuple: (success (bool), research_data (dict) or error message (str))
        """
        try:
            # Search the web for relevant pages
            search_success, search_results = self.search_web(query, num_results=max_sources)
            if not search_success:
                return False, search_results
            
            # Scrape each search result
            sources = []
            for result in search_results:
                url = result['url']
                
                # Skip if URL is not accessible or not HTML
                success, article_data = self.scraper.scrape_article(url)
                if success:
                    sources.append({
                        'title': article_data['title'],
                        'url': url,
                        'content': article_data['content'],
                        'date_published': article_data['date_published']
                    })
            
            # Compile research data
            research_data = {
                'query': query,
                'sources': sources,
                'summary': self._generate_summary(sources, query)
            }
            
            return True, research_data
        except Exception as e:
            logger.error(f"Error researching topic: {str(e)}")
            return False, str(e)
    
    def scrape_specific_site(self, url, max_articles=5):
        """
        Scrape a specific website for information.
        
        Args:
            url (str): The URL of the website to scrape.
            max_articles (int, optional): Maximum number of articles to scrape. Defaults to 5.
            
        Returns:
            tuple: (success (bool), site_data (dict) or error message (str))
        """
        try:
            # Scrape the site
            success, articles = self.scraper.scrape_news_site(url, max_articles=max_articles)
            if not success:
                return False, articles
            
            # Compile site data
            site_data = {
                'url': url,
                'articles': articles,
                'summary': self._generate_site_summary(articles, url)
            }
            
            return True, site_data
        except Exception as e:
            logger.error(f"Error scraping site: {str(e)}")
            return False, str(e)
    
    def _generate_summary(self, sources, query):
        """
        Generate a summary of the research sources.
        
        Args:
            sources (list): List of source data dictionaries.
            query (str): The original research query.
            
        Returns:
            str: A summary of the research.
        """
        if not sources:
            return f"No reliable information found for '{query}'."
        
        # In a real implementation, you might use an LLM to generate a summary
        # For now, we'll just create a simple summary
        summary = f"Research results for '{query}':\n\n"
        
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Untitled')
            url = source.get('url', '')
            content_preview = source.get('content', '')[:200] + '...' if source.get('content') else ''
            
            summary += f"{i}. {title}\n"
            summary += f"   URL: {url}\n"
            summary += f"   Preview: {content_preview}\n\n"
        
        return summary
    
    def _generate_site_summary(self, articles, site_url):
        """
        Generate a summary of articles from a specific site.
        
        Args:
            articles (list): List of article data dictionaries.
            site_url (str): The URL of the scraped site.
            
        Returns:
            str: A summary of the articles.
        """
        if not articles:
            return f"No articles found on {site_url}."
        
        # In a real implementation, you might use an LLM to generate a summary
        # For now, we'll just create a simple summary
        summary = f"Latest information from {site_url}:\n\n"
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            date = article.get('date_published', 'Unknown date')
            content_preview = article.get('content', '')[:200] + '...' if article.get('content') else ''
            
            summary += f"{i}. {title} ({date})\n"
            summary += f"   Preview: {content_preview}\n\n"
        
        return summary
