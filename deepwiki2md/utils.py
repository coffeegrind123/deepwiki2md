"""Utility functions and classes for deepwiki2md package."""

import re
from urllib.parse import urlparse, urljoin
from typing import Optional, List, Dict, Any
from pathlib import Path


class DeepWikiURL:
    """Utility class for handling DeepWiki URLs."""
    
    def __init__(self, url: str):
        self.url = url.rstrip('/')
        self.parsed = urlparse(self.url)
        
    @property
    def domain(self) -> str:
        """Get the domain from the URL."""
        return self.parsed.netloc
        
    @property
    def path_parts(self) -> List[str]:
        """Get URL path parts as a list."""
        return [part for part in self.parsed.path.strip('/').split('/') if part]
        
    @property
    def library_name(self) -> Optional[str]:
        """Extract library name from URL path."""
        parts = self.path_parts
        if len(parts) >= 2:
            return parts[1]  # Usually the second part after domain/project
        return parts[0] if parts else None
        
    def is_valid_deepwiki(self) -> bool:
        """Check if this appears to be a valid DeepWiki URL."""
        return (
            bool(self.domain) and 
            'deepwiki' in self.domain.lower() and
            len(self.path_parts) >= 1
        )
        
    def get_base_url(self) -> str:
        """Get the base URL for this DeepWiki site."""
        return f"{self.parsed.scheme}://{self.parsed.netloc}"


class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize a string to be used as a filename."""
        # Remove or replace invalid characters
        sanitized = re.sub(r'[\\/*?:"<>|]', '', name)
        # Replace whitespace with underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        # Limit length
        return sanitized[:200] if len(sanitized) > 200 else sanitized
    
    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Ensure directory exists, create if it doesn't."""
        path.mkdir(parents=True, exist_ok=True)
        return path


class ContentCleaner:
    """Utility class for cleaning and processing content."""
    
    @staticmethod
    def clean_markdown_links(content: str) -> str:
        """Clean markdown links by removing URLs but keeping link text."""
        # Pattern to match markdown links with URLs
        link_pattern = re.compile(r'\[([^\]]+)\]\((?![s\)])[^\)]+\)')
        # Replace with empty parentheses
        return link_pattern.sub(r'[\1]()', content)
    
    @staticmethod
    def remove_navigation_elements(html_content: str) -> str:
        """Remove common navigation elements from HTML."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove navigation menus (common selectors)
        nav_selectors = [
            'ul.flex-1.flex-shrink-0.space-y-1.overflow-y-auto.py-1',
            'nav',
            '.navigation',
            '.sidebar',
            '.menu'
        ]
        
        for selector in nav_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
        
        return str(soup)
    
    @staticmethod
    def extract_title_from_content(html_content: str) -> Optional[str]:
        """Extract title from HTML content."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try different title selectors
        title_selectors = ['h1', 'title', '.page-title', '.article-title']
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title:
                    return title
        
        return None