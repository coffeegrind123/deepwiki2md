"""Main scraper class using PyDoll for DeepWiki content extraction."""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions
from bs4 import BeautifulSoup

from .converter import MarkdownConverter
from .utils import DeepWikiURL, FileUtils, ContentCleaner

logger = logging.getLogger(__name__)


class DeepWikiScraper:
    """Main scraper class for extracting DeepWiki content using PyDoll."""
    
    def __init__(self, output_dir: str = "output", headless: bool = True):
        """
        Initialize the scraper.
        
        Args:
            output_dir: Directory to save markdown files
            headless: Whether to run browser in headless mode
        """
        self.output_dir = Path(output_dir)
        self.headless = headless
        self.converter = MarkdownConverter()
        self.file_utils = FileUtils()
        
        # Ensure output directory exists
        self.file_utils.ensure_directory(self.output_dir)
        
    async def _get_page_content(self, tab, url: str, timeout: int = 30) -> Optional[str]:
        """
        Navigate to URL and get page content.
        
        Args:
            tab: PyDoll browser tab
            url: URL to navigate to
            timeout: Timeout in seconds
            
        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Navigating to: {url}")
            await tab.go_to(url)
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            # Get page HTML
            html_content = await tab.page_source
            return html_content
            
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None
    
    async def _extract_navigation_items(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
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
        
    async def scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single page and convert to markdown.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped content or None if failed
        """
        options = ChromiumOptions()
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        async with Chrome(options=options) as browser:
            try:
                tab = await browser.start()
                html_content = await self._get_page_content(tab, url)
                
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
                    
            except Exception as e:
                logger.error(f"Error scraping page {url}: {e}")
                
        return None
        
    async def scrape_library(self, url: str, save_files: bool = True) -> List[Dict[str, Any]]:
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
        
        options = ChromiumOptions()
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        async with Chrome(options=options) as browser:
            try:
                tab = await browser.start()
                
                # Get main page content
                main_html = await self._get_page_content(tab, url)
                if not main_html:
                    logger.error(f"Failed to fetch main page: {url}")
                    return []
                    
                # Extract navigation items
                nav_items = await self._extract_navigation_items(main_html, deepwiki_url.get_base_url())
                
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
                    
                    # Small delay to avoid overwhelming the server
                    if i > 1:
                        await asyncio.sleep(1)
                        
                    page_html = await self._get_page_content(tab, item['url'])
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
                        
            except Exception as e:
                logger.error(f"Error scraping library {url}: {e}")
                
        logger.info(f"Scraped {len(scraped_pages)} pages from {library_name}")
        return scraped_pages
        
    async def scrape_multiple_libraries(self, urls: List[str], save_files: bool = True) -> Dict[str, List[Dict[str, Any]]]:
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
            pages = await self.scrape_library(url, save_files)
            results[library_name] = pages
            
        return results