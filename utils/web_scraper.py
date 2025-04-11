"""
Web Scraping Utility for DMac

This module provides web scraping functionality to retrieve and parse content from websites.
"""

import requests
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin, urlparse
import time
import random

# Set up logging
logger = logging.getLogger('dmac.web_scraper')

class WebScraper:
    """Web scraping utility for retrieving and parsing web content."""
    
    def __init__(self, user_agent=None):
        """
        Initialize the web scraper.
        
        Args:
            user_agent (str, optional): Custom user agent string. Defaults to a Chrome user agent.
        """
        self.session = requests.Session()
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.session.headers.update({'User-Agent': self.user_agent})
        
    def get_page_content(self, url, timeout=10):
        """
        Retrieve the content of a web page.
        
        Args:
            url (str): The URL to scrape.
            timeout (int, optional): Request timeout in seconds. Defaults to 10.
            
        Returns:
            tuple: (success (bool), content (str) or error message (str))
        """
        try:
            # Add a small random delay to be respectful to servers
            time.sleep(random.uniform(0.5, 1.5))
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            
            # Check if the content is HTML
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                return False, f"Not an HTML page. Content-Type: {content_type}"
            
            return True, response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return False, str(e)
    
    def parse_html(self, html_content):
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html_content (str): HTML content to parse.
            
        Returns:
            BeautifulSoup: Parsed HTML.
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_text_content(self, soup, main_content_selectors=None):
        """
        Extract main text content from a parsed HTML page.
        
        Args:
            soup (BeautifulSoup): Parsed HTML.
            main_content_selectors (list, optional): CSS selectors for main content areas.
                                                    Defaults to common content selectors.
            
        Returns:
            str: Extracted text content.
        """
        # Default selectors for main content areas
        if main_content_selectors is None:
            main_content_selectors = [
                'article', 'main', '.content', '#content', '.post', '.article',
                '.entry-content', '.post-content', '[role="main"]'
            ]
        
        # Try to find main content using selectors
        main_content = None
        for selector in main_content_selectors:
            content = soup.select(selector)
            if content:
                main_content = ' '.join([elem.get_text(strip=True, separator=' ') for elem in content])
                break
        
        # If no main content found, use the body
        if not main_content:
            # Remove script, style, and other non-content elements
            for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
                element.decompose()
            
            main_content = soup.body.get_text(strip=True, separator=' ') if soup.body else ''
        
        # Clean up the text
        main_content = re.sub(r'\s+', ' ', main_content).strip()
        
        return main_content
    
    def extract_article_metadata(self, soup, url):
        """
        Extract metadata from an article page.
        
        Args:
            soup (BeautifulSoup): Parsed HTML.
            url (str): The URL of the page.
            
        Returns:
            dict: Article metadata.
        """
        metadata = {
            'title': '',
            'description': '',
            'author': '',
            'date_published': '',
            'url': url
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        # Try meta tags for description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')
        
        # Try to find author
        author_selectors = [
            'meta[name="author"]', 'meta[property="article:author"]',
            '.author', '.byline', '.entry-author', '[rel="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if author_elem.name == 'meta':
                    metadata['author'] = author_elem.get('content', '')
                else:
                    metadata['author'] = author_elem.get_text(strip=True)
                break
        
        # Try to find publication date
        date_selectors = [
            'meta[property="article:published_time"]', 'time', '.date', '.published',
            '.entry-date', '.post-date', '[itemprop="datePublished"]'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                if date_elem.name == 'meta':
                    metadata['date_published'] = date_elem.get('content', '')
                elif date_elem.get('datetime'):
                    metadata['date_published'] = date_elem.get('datetime', '')
                else:
                    metadata['date_published'] = date_elem.get_text(strip=True)
                break
        
        return metadata
    
    def extract_links(self, soup, base_url):
        """
        Extract links from a parsed HTML page.
        
        Args:
            soup (BeautifulSoup): Parsed HTML.
            base_url (str): Base URL for resolving relative links.
            
        Returns:
            list: List of absolute URLs.
        """
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip empty links, anchors, and javascript
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Only include links to the same domain
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                links.append(absolute_url)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(links))
    
    def scrape_article(self, url):
        """
        Scrape an article page and extract its content and metadata.
        
        Args:
            url (str): The URL of the article to scrape.
            
        Returns:
            tuple: (success (bool), article_data (dict) or error message (str))
        """
        success, content = self.get_page_content(url)
        if not success:
            return False, content
        
        soup = self.parse_html(content)
        
        # Extract article content and metadata
        text_content = self.extract_text_content(soup)
        metadata = self.extract_article_metadata(soup, url)
        
        article_data = {
            **metadata,
            'content': text_content
        }
        
        return True, article_data
    
    def scrape_news_site(self, url, max_articles=5):
        """
        Scrape a news site for articles.
        
        Args:
            url (str): The URL of the news site.
            max_articles (int, optional): Maximum number of articles to scrape. Defaults to 5.
            
        Returns:
            tuple: (success (bool), articles (list) or error message (str))
        """
        success, content = self.get_page_content(url)
        if not success:
            return False, content
        
        soup = self.parse_html(content)
        links = self.extract_links(soup, url)
        
        # Filter links that are likely to be articles
        article_links = []
        for link in links:
            # Common patterns for article URLs
            if re.search(r'/(article|post|news|blog)/|/\d{4}/\d{2}/|/[a-z0-9-]+/$', link):
                article_links.append(link)
        
        # Limit the number of articles
        article_links = article_links[:max_articles]
        
        # Scrape each article
        articles = []
        for link in article_links:
            success, article_data = self.scrape_article(link)
            if success:
                articles.append(article_data)
        
        return True, articles
