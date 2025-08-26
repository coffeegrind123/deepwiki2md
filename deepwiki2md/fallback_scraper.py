"""Fallback scraper using requests when PyDoll is not available."""

import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .converter import MarkdownConverter
from .utils import DeepWikiURL, FileUtils

logger = logging.getLogger(__name__)


class FallbackScraper:
    """Fallback scraper using requests when PyDoll browser automation is not available."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the fallback scraper.
        
        Args:
            output_dir: Directory to save markdown files
        """
        self.output_dir = Path(output_dir)
        self.converter = MarkdownConverter()
        self.file_utils = FileUtils()
        
        # Ensure output directory exists
        self.file_utils.ensure_directory(self.output_dir)
        
        # Set up session with headers to mimic a browser
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _get_page_content(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Get page content using requests.
        
        Args:
            url: URL to fetch
            timeout: Timeout in seconds
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
            
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None
    
    def _extract_navigation_items(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        """
        Extract navigation items from HTML content.
        
        Args:
            html_content: HTML content to parse
            base_url: Base URL for resolving relative links
            
        Returns:
            List of navigation items with title and url
        """
        if not html_content:
            return []
            
        soup = BeautifulSoup(html_content, 'html.parser')
        nav_items = []
        
        # Try different selectors for navigation
        nav_selectors = [
            'ul.flex-1.flex-shrink-0.space-y-1.overflow-y-auto.py-1',
            'nav ul',
            '.navigation ul',
            '.sidebar ul',
            '.menu ul',
            'ul[class*="nav"]',
            'ul[class*="menu"]'
        ]
        
        for selector in nav_selectors:
            nav_ul = soup.select_one(selector)
            if nav_ul:
                logger.debug(f"Found navigation using selector: {selector}")
                
                for li in nav_ul.find_all('li'):
                    a_tag = li.find('a')
                    if a_tag and a_tag.get('href'):
                        title = a_tag.get_text(strip=True)
                        href = a_tag.get('href')
                        full_url = urljoin(base_url, href)
                        
                        if title and full_url:
                            nav_items.append({
                                'title': title,
                                'url': full_url
                            })
                            
                break  # Use first successful selector
                
        logger.info(f"Found {len(nav_items)} navigation items")
        return nav_items
        
    def _save_markdown(self, content: str, title: str, library_name: str) -> Path:
        """
        Save markdown content to file.
        
        Args:
            content: Markdown content
            title: Page title
            library_name: Library name for directory structure
            
        Returns:
            Path to saved file
        """
        # Create library directory
        library_dir = self.file_utils.ensure_directory(self.output_dir / library_name)
        
        # Sanitize filename
        filename = self.file_utils.sanitize_filename(title or "untitled")
        if not filename.endswith('.md'):
            filename += '.md'
            
        file_path = library_dir / filename
        
        # Write content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Saved: {file_path}")
        return file_path
        
    def scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single page and convert to markdown.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped content or None if failed
        """
        html_content = self._get_page_content(url)
        
        if not html_content:
            return None
            
        # Convert to markdown
        result = self.converter.convert_page(html_content, url)
        if result['success']:
            return {
                'url': url,
                'title': result['title'],
                'content': result['content'],
                'html': html_content
            }
            
        return None
        
    def scrape_library(self, url: str, save_files: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape an entire DeepWiki library.
        
        Args:
            url: DeepWiki library URL
            save_files: Whether to save markdown files
            
        Returns:
            List of scraped pages
        """
        deepwiki_url = DeepWikiURL(url)
        
        if not deepwiki_url.is_valid_deepwiki():
            logger.error(f"Invalid DeepWiki URL: {url}")
            return []
            
        library_name = deepwiki_url.library_name or "unknown_library"
        logger.info(f"Scraping library: {library_name}")
        
        scraped_pages = []
        
        # Get main page content
        main_html = self._get_page_content(url)
        if not main_html:
            logger.error(f"Failed to fetch main page: {url}")
            return []
            
        # Extract navigation items
        nav_items = self._extract_navigation_items(main_html, deepwiki_url.get_base_url())
        
        # If no navigation found, just process the main page
        if not nav_items:
            logger.warning("No navigation items found, processing main page only")
            result = self.converter.convert_page(main_html, url)
            if result['success']:
                page_data = {
                    'url': url,
                    'title': result['title'] or library_name,
                    'content': result['content']
                }
                scraped_pages.append(page_data)
                
                if save_files:
                    self._save_markdown(
                        page_data['content'],
                        page_data['title'],
                        library_name
                    )
            return scraped_pages
            
        # Process each navigation item
        for i, item in enumerate(nav_items, 1):
            logger.info(f"Processing {i}/{len(nav_items)}: {item['title']}")
            
            page_html = self._get_page_content(item['url'])
            if not page_html:
                logger.warning(f"Failed to fetch: {item['title']}")
                continue
                
            # Convert to markdown
            result = self.converter.convert_page(page_html, item['url'])
            if result['success']:
                page_data = {
                    'url': item['url'],
                    'title': result['title'] or item['title'],
                    'content': result['content']
                }
                scraped_pages.append(page_data)
                
                if save_files:
                    self._save_markdown(
                        page_data['content'],
                        page_data['title'],
                        library_name
                    )
            else:
                logger.warning(f"Failed to convert: {item['title']}")
                
        logger.info(f"Scraped {len(scraped_pages)} pages from {library_name}")
        return scraped_pages
        
    def scrape_multiple_libraries(self, urls: List[str], save_files: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape multiple DeepWiki libraries.
        
        Args:
            urls: List of DeepWiki library URLs
            save_files: Whether to save markdown files
            
        Returns:
            Dictionary mapping library names to scraped pages
        """
        results = {}
        
        for url in urls:
            deepwiki_url = DeepWikiURL(url)
            library_name = deepwiki_url.library_name or f"library_{len(results)}"
            
            logger.info(f"Starting library: {library_name}")
            pages = self.scrape_library(url, save_files)
            results[library_name] = pages
            
        return results