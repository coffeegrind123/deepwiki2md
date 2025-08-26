import logging
import os
import re
import time
from urllib.parse import urljoin, urlparse

from markdownify import markdownify
from pydoll import Pydoll

from .localization import get_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrowserDeepwikiScraper:
    """
    A browser-based scraper for deepwiki that handles dynamic content loading
    using pydoll for browser automation.
    """
    
    def __init__(self, output_dir="Documents", headless=True):
        """
        Initialize the BrowserDeepwikiScraper.

        Args:
            output_dir (str): The base directory to save the converted Markdown files.
            headless (bool): Whether to run the browser in headless mode.
        """
        self.output_dir = output_dir
        self.headless = headless
        self.pydoll = None
        
    def _start_browser(self):
        """Start the pydoll browser instance."""
        if self.pydoll is None:
            logger.info("Starting browser...")
            self.pydoll = Pydoll(headless=self.headless)
            
    def _stop_browser(self):
        """Stop the pydoll browser instance."""
        if self.pydoll is not None:
            logger.info("Stopping browser...")
            self.pydoll.close()
            self.pydoll = None
            
    def __enter__(self):
        """Context manager entry."""
        self._start_browser()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._stop_browser()
        
    def get_page_content(self, url, wait_time=5):
        """
        Get the fully rendered HTML content of a page using browser automation.
        
        Args:
            url (str): The URL to fetch.
            wait_time (int): Time to wait for dynamic content to load.
            
        Returns:
            str: The rendered HTML content of the page.
        """
        logger.info(f"Navigating to: {url}")
        
        try:
            # Navigate to the page
            self.pydoll.goto(url)
            
            # Wait for initial load
            time.sleep(2)
            
            # Wait for content to load - look for common selectors
            content_selectors = [
                'article',
                'main',
                '[data-testid="markdown-content"]',
                '.markdown-body',
                '.content'
            ]
            
            content_found = False
            for selector in content_selectors:
                try:
                    elements = self.pydoll.querySelectorAll(selector)
                    if elements and len(elements) > 0:
                        logger.info(f"Found content with selector: {selector}")
                        content_found = True
                        break
                except Exception:
                    continue
                    
            # Wait additional time for dynamic content
            if content_found:
                time.sleep(wait_time)
            else:
                logger.warning("No content selectors found, waiting longer...")
                time.sleep(wait_time * 2)
                
            # Get the fully rendered HTML
            html_content = self.pydoll.get_html()
            logger.info(f"Retrieved HTML content: {len(html_content)} bytes")
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error getting page content for {url}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
            
    def extract_navigation_items(self, url):
        """
        Extract navigation items from the deepwiki page.
        
        Args:
            url (str): The URL of the current page.
            
        Returns:
            list: A list of dictionaries containing the title and URL of each navigation item.
        """
        logger.info("Extracting navigation items...")
        
        try:
            # Look for navigation elements - deepwiki likely uses sidebar navigation
            nav_selectors = [
                'nav a[href]',
                '.sidebar a[href]',
                '.navigation a[href]',
                '.menu a[href]',
                'aside a[href]',
                # React-based navigation patterns
                '[data-testid="navigation"] a',
                '[role="navigation"] a'
            ]
            
            nav_items = []
            
            for selector in nav_selectors:
                try:
                    elements = self.pydoll.querySelectorAll(selector)
                    if elements and len(elements) > 0:
                        logger.info(f"Found navigation links with selector: {selector}")
                        
                        for element in elements:
                            try:
                                href = element.get('href', '')
                                text = element.get('textContent', '').strip()
                                
                                if href and text and href.startswith('/'):
                                    # Convert relative URL to absolute
                                    parsed_url = urlparse(url)
                                    full_url = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                                    
                                    nav_items.append({
                                        'title': text,
                                        'url': full_url
                                    })
                                    
                            except Exception as e:
                                logger.debug(f"Error processing navigation element: {e}")
                                continue
                                
                        if nav_items:
                            break
                            
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
                    
            # Remove duplicates
            seen = set()
            unique_items = []
            for item in nav_items:
                if item['url'] not in seen:
                    seen.add(item['url'])
                    unique_items.append(item)
                    
            logger.info(f"Found {len(unique_items)} unique navigation items")
            return unique_items
            
        except Exception as e:
            logger.error(f"Error extracting navigation: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
            
    def extract_content(self, url):
        """
        Extract the main content from the deepwiki page.
        
        Args:
            url (str): The URL of the page to extract content from.
            
        Returns:
            str: The main content as HTML.
        """
        logger.info("Extracting main content...")
        
        try:
            # Try different content selectors for deepwiki
            content_selectors = [
                'main article',
                'article',
                'main',
                '.content',
                '.markdown-body',
                '[data-testid="markdown-content"]',
                '.prose',
                '#content',
                '.documentation-content',
                '.wiki-content'
            ]
            
            for selector in content_selectors:
                try:
                    elements = self.pydoll.querySelectorAll(selector)
                    if elements and len(elements) > 0:
                        # Get the largest content element
                        content_element = max(elements, key=lambda x: len(x.get('textContent', '')))
                        content_html = content_element.get('innerHTML', '')
                        
                        if content_html and len(content_html.strip()) > 100:
                            logger.info(f"Found main content with selector: {selector}")
                            return content_html
                            
                except Exception as e:
                    logger.debug(f"Error with content selector {selector}: {e}")
                    continue
                    
            # Fallback: get all text content
            logger.warning("Could not find specific content selector, using body")
            body_elements = self.pydoll.querySelectorAll('body')
            if body_elements:
                return body_elements[0].get('innerHTML', '')
                
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ""
            
    def html_to_markdown(self, html_content):
        """
        Convert HTML content to Markdown.
        
        Args:
            html_content (str): The HTML content to convert.
            
        Returns:
            str: The content converted to Markdown.
        """
        if not html_content:
            return ""
            
        try:
            # Clean up the HTML before conversion
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'noscript']):
                element.decompose()
                
            # Remove navigation elements that might be included
            for nav_selector in ['nav', '.navigation', '.sidebar', '.menu']:
                for element in soup.select(nav_selector):
                    element.decompose()
                    
            # Convert to markdown
            markdown = markdownify(str(soup), heading_style="ATX")
            
            # Clean up the markdown
            markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)  # Remove excessive blank lines
            markdown = markdown.strip()
            
            return markdown
            
        except Exception as e:
            logger.error(f"Error converting HTML to markdown: {e}")
            return html_content
            
    def save_markdown(self, library_name, title, markdown_content, path=None):
        """
        Save the Markdown content to a file.

        Args:
            library_name (str): The name of the library.
            title (str): The title of the page.
            markdown_content (str): The Markdown content to save.
            path (str, optional): The path to use for the directory structure.
        """
        # Create directory structure
        if path:
            dir_path = os.path.join(os.path.abspath(os.getcwd()), self.output_dir, path, "md")
        else:
            dir_path = os.path.join(os.getcwd(), self.output_dir, library_name, "md")
        os.makedirs(dir_path, exist_ok=True)

        # Sanitize the title to create a valid filename
        filename = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        filename = re.sub(r'\s+', '_', filename)
        if not filename:
            filename = "index"

        # Save the Markdown content to a file
        file_path = os.path.join(dir_path, f"{filename}.md")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Saved markdown file: {file_path}")
        return file_path
        
    def scrape_page(self, url, library_name, title=None):
        """
        Scrape a single page and convert it to markdown.
        
        Args:
            url (str): The URL to scrape.
            library_name (str): The name of the library.
            title (str, optional): The title for the page.
            
        Returns:
            str: Path to the saved markdown file, or None if failed.
        """
        logger.info(f"Scraping page: {url}")
        
        try:
            # Navigate to the page and get content
            html_content = self.get_page_content(url)
            if not html_content:
                logger.error(f"Failed to get HTML content for {url}")
                return None
                
            # Extract main content
            content_html = self.extract_content(url)
            if not content_html:
                logger.error(f"Failed to extract content from {url}")
                return None
                
            # Convert to markdown
            markdown = self.html_to_markdown(content_html)
            if not markdown:
                logger.error(f"Failed to convert content to markdown for {url}")
                return None
                
            # Use title from URL if not provided
            if not title:
                parsed_url = urlparse(url)
                title = parsed_url.path.split('/')[-1] or library_name
                
            # Save the markdown
            file_path = self.save_markdown(library_name, title, markdown)
            return file_path
            
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
            
    def scrape_library(self, library_name, library_url):
        """
        Scrape a complete library from deepwiki.
        
        Args:
            library_name (str): The name of the library.
            library_url (str): The URL of the library.
        """
        logger.info(f"Scraping library: {library_name} from {library_url}")
        
        try:
            self._start_browser()
            
            # Navigate to the main page
            html_content = self.get_page_content(library_url)
            if not html_content:
                logger.error(f"Failed to get main page content for {library_name}")
                return
                
            # Extract navigation items
            nav_items = self.extract_navigation_items(library_url)
            
            # Scrape the main page
            main_page_path = self.scrape_page(library_url, library_name, library_name)
            if main_page_path:
                logger.info(f"Successfully scraped main page: {main_page_path}")
            
            # Scrape navigation pages
            scraped_count = 1 if main_page_path else 0
            for item in nav_items:
                try:
                    time.sleep(2)  # Be respectful to the server
                    page_path = self.scrape_page(item['url'], library_name, item['title'])
                    if page_path:
                        scraped_count += 1
                        logger.info(f"Successfully scraped: {item['title']}")
                    else:
                        logger.warning(f"Failed to scrape: {item['title']}")
                        
                except Exception as e:
                    logger.error(f"Error scraping {item['title']}: {e}")
                    continue
                    
            logger.info(f"Scraping completed. Successfully scraped {scraped_count} pages for {library_name}")
            
        except Exception as e:
            logger.error(f"Error scraping library {library_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
        finally:
            self._stop_browser()
            
    def run(self, libraries):
        """
        Run the scraper for multiple libraries.

        Args:
            libraries (list): A list of dictionaries containing the name and URL of each library.
        """
        for library in libraries:
            name = library['name']
            url = library['url']
            self.scrape_library(name, url)