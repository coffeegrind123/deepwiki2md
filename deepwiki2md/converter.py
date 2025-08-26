"""Markdown conversion functionality for deepwiki2md."""

import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from markdownify import markdownify

from .utils import ContentCleaner

logger = logging.getLogger(__name__)


class MarkdownConverter:
    """Converts HTML content to clean Markdown format."""
    
    def __init__(self, heading_style: str = "ATX", strip_navigation: bool = True):
        """
        Initialize the converter.
        
        Args:
            heading_style: Style for headings ("ATX" or "SETEXT")
            strip_navigation: Whether to remove navigation elements
        """
        self.heading_style = heading_style
        self.strip_navigation = strip_navigation
        self.cleaner = ContentCleaner()
        
    def extract_main_content(self, html_content: str, url: str = None) -> Optional[BeautifulSoup]:
        """
        Extract main content from HTML, removing navigation and other non-content elements.
        
        Args:
            html_content: Raw HTML content
            url: Optional URL for logging purposes
            
        Returns:
            BeautifulSoup object containing main content, or None if not found
        """
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try multiple selectors for main content, ordered by specificity
        content_selectors = [
            'main article',
            'main .content', 
            'main',
            'article',
            '.content',
            '.article-content',
            '#content',
            '.markdown-body',
            '.documentation-content',
            '.page-content',
            '[role="main"]'
        ]
        
        main_content = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                logger.debug(f"Found content using selector: {selector}")
                main_content = element
                break
                
        # Fallback: find the div with the most text content
        if not main_content:
            body = soup.find('body')
            if body:
                divs = body.find_all('div', recursive=True)
                if divs:
                    main_content = max(divs, key=lambda x: len(x.get_text(strip=True)))
                else:
                    main_content = body
                    
        if not main_content or not main_content.get_text(strip=True):
            logger.warning(f"No main content found for URL: {url}")
            return None
            
        return main_content
        
    def html_to_markdown(self, html_element) -> str:
        """
        Convert HTML element to Markdown.
        
        Args:
            html_element: BeautifulSoup element or HTML string
            
        Returns:
            Converted Markdown content
        """
        if not html_element:
            return ""
            
        # Handle different input types
        if isinstance(html_element, str):
            html_content = html_element
        elif hasattr(html_element, 'name'):  # BeautifulSoup Tag
            html_content = str(html_element)
        else:
            html_content = str(html_element)
            
        # Strip navigation elements if requested
        if self.strip_navigation:
            html_content = self.cleaner.remove_navigation_elements(html_content)
            
        # Convert to markdown
        markdown = markdownify(
            html_content, 
            heading_style=self.heading_style,
            strip=['script', 'style']  # Remove script and style tags
        )
        
        # Clean up the markdown
        markdown = self._clean_markdown(markdown)
        
        return markdown
        
    def _clean_markdown(self, markdown: str) -> str:
        """Clean up markdown content."""
        if not markdown:
            return ""
            
        lines = markdown.split('\n')
        cleaned_lines = []
        
        # Remove excessive empty lines
        prev_empty = False
        for line in lines:
            line = line.rstrip()
            is_empty = not line
            
            if is_empty and prev_empty:
                continue  # Skip multiple consecutive empty lines
                
            cleaned_lines.append(line)
            prev_empty = is_empty
            
        return '\n'.join(cleaned_lines).strip()
        
    def convert_page(self, html_content: str, url: str = None) -> Dict[str, Any]:
        """
        Convert a complete page to markdown.
        
        Args:
            html_content: Raw HTML content
            url: Optional URL for context
            
        Returns:
            Dictionary containing:
            - content: Converted markdown
            - title: Extracted title
            - success: Whether conversion succeeded
        """
        result = {
            'content': '',
            'title': '',
            'success': False
        }
        
        try:
            # Extract main content
            main_content = self.extract_main_content(html_content, url)
            if not main_content:
                return result
                
            # Extract title
            title = self.cleaner.extract_title_from_content(html_content)
            if title:
                result['title'] = title
                
            # Convert to markdown
            markdown_content = self.html_to_markdown(main_content)
            if markdown_content:
                # Clean markdown links
                markdown_content = self.cleaner.clean_markdown_links(markdown_content)
                result['content'] = markdown_content
                result['success'] = True
                
        except Exception as e:
            logger.error(f"Error converting page to markdown: {e}")
            
        return result