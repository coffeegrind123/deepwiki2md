"""Utility functions and classes for deepwiki2md package."""

import re
from urllib.parse import urlparse, urljoin
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


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
    
    def __init__(self, svg_converter=None):
        """Initialize ContentCleaner with optional SVG converter."""
        self.svg_converter = svg_converter
    
    @staticmethod
    def clean_markdown_links(content: str) -> str:
        """Clean markdown links by removing URLs but keeping link text."""
        # Pattern to match markdown links with URLs
        link_pattern = re.compile(r'\[([^\]]+)\]\((?![s\)])[^\)]+\)')
        # Replace with empty parentheses
        return link_pattern.sub(r'[\1]()', content)
    
    @staticmethod
    def remove_deepwiki_chrome(content: str) -> str:
        """Remove DeepWiki-specific navigation and promotional content."""
        lines = content.split('\n')
        filtered_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip promotional and navigation content patterns
            skip_patterns = [
                # Promotional links
                r'^\[Get free private DeepWikis.*\]\(\)$',
                r'^\[.*DeepWiki.*\]\(\)$',
                r'^\[.*Devin.*\]\(\).*Share$',
                # Navigation elements
                r'^Menu$',
                r'^Share$',
                r'^Dismiss$',
                r'^Refresh this wiki$',
                r'^Enter email to refresh$',
                r'^Ask Devin about.*$',
                r'^Deep Research$',
                # Combined navigation text
                r'^DismissEnter email to refresh$',
                r'^.*Dismiss.*refresh.*$',
                # Metadata
                r'^Last indexed:.*\(\)$',
                r'^Last indexed:.*$',
                # Table of contents at bottom
                r'^### On this page$',
                r'^Ask.*about.*$'
            ]
            
            # Check if line matches any skip pattern
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            # Skip empty promotional links like [DeepWiki]()
            if re.match(r'^\[.*\]\(\)$', line) and any(keyword in line.lower() for keyword in ['deepwiki', 'devin', 'private']):
                should_skip = True
            
            # Special case: Skip "On this page" sections at the end
            if line == "### On this page" or line.startswith("* [") and i > len(lines) * 0.8:
                should_skip = True
            
            if not should_skip:
                filtered_lines.append(lines[i])
            
            i += 1
        
        return '\n'.join(filtered_lines)
    
    def extract_and_convert_svgs(self, html_content: str) -> tuple[str, dict]:
        """Extract SVG flowcharts from HTML, convert to ASCII, and return modified HTML with replacements."""
        logger.info("=== Starting SVG extraction and conversion from HTML ===")
        logger.debug(f"HTML content length: {len(html_content)} chars")
        
        if not self.svg_converter:
            logger.warning("No SVG converter available, returning unchanged HTML")
            return html_content, {}
        
        # Pattern to find SVG flowcharts
        svg_pattern = r'<svg[^>]*aria-roledescription="flowchart[^"]*"[^>]*>.*?</svg>'
        svg_replacements = {}
        placeholder_counter = 0
        
        logger.debug(f"Using SVG pattern: {svg_pattern}")
        
        # Find all SVG matches first for logging
        matches = list(re.finditer(svg_pattern, html_content, flags=re.DOTALL | re.IGNORECASE))
        logger.info(f"Found {len(matches)} SVG flowcharts in HTML content")
        
        for i, match in enumerate(matches):
            svg_preview = match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0)
            logger.debug(f"SVG {i}: Position {match.start()}-{match.end()}, Preview: {svg_preview}")
        
        def replace_svg(match):
            nonlocal placeholder_counter
            svg_content = match.group(0)
            placeholder = f"<!-- SVG_PLACEHOLDER_{placeholder_counter} -->"
            
            logger.info(f"Processing SVG flowchart {placeholder_counter}: {len(svg_content)} chars")
            logger.debug(f"Placeholder created: {placeholder}")
            
            try:
                logger.info(f"Converting SVG {placeholder_counter} to ASCII...")
                result = self.svg_converter.convert_svg_to_ascii(svg_content)
                
                logger.debug(f"Conversion result for SVG {placeholder_counter}: success={result['success']}, "
                           f"d2_code_length={len(result.get('d2_code', ''))}, "
                           f"ascii_length={len(result.get('ascii_diagram', ''))}")
                
                if result['success']:
                    logger.info(f"Successfully converted SVG {placeholder_counter} to ASCII")
                    svg_replacements[placeholder] = result['ascii_diagram']
                    logger.debug(f"Stored ASCII diagram for {placeholder}: {len(result['ascii_diagram'])} chars")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logger.warning(f"SVG {placeholder_counter} conversion failed: {error_msg}")
                    fallback_content = f"```\n[Flowchart conversion failed: {error_msg}]\n```"
                    svg_replacements[placeholder] = fallback_content
                    logger.debug(f"Stored fallback content for {placeholder}: {fallback_content}")
            except Exception as e:
                logger.error(f"Error converting SVG {placeholder_counter}: {e}")
                import traceback
                logger.debug(f"Full traceback for SVG {placeholder_counter}: {traceback.format_exc()}")
                fallback_content = f"```\n[Flowchart conversion error: {str(e)}]\n```"
                svg_replacements[placeholder] = fallback_content
                logger.debug(f"Stored error fallback for {placeholder}: {fallback_content}")
            
            placeholder_counter += 1
            logger.debug(f"Returning placeholder {placeholder} for SVG replacement")
            return placeholder
        
        # Replace SVG flowcharts with placeholders
        logger.info("Replacing SVG flowcharts with placeholders in HTML...")
        modified_html = re.sub(svg_pattern, replace_svg, html_content, flags=re.DOTALL | re.IGNORECASE)
        
        logger.info(f"SVG extraction completed: {len(svg_replacements)} replacements created")
        logger.debug(f"Replacement keys: {list(svg_replacements.keys())}")
        logger.debug(f"Modified HTML length: {len(modified_html)} chars (original: {len(html_content)})")
        
        return modified_html, svg_replacements
    
    def insert_svg_replacements(self, markdown_content: str, svg_replacements: dict) -> str:
        """Insert SVG ASCII diagrams into markdown at placeholder positions."""
        logger.info("=== Starting SVG placeholder replacement in markdown ===")
        logger.debug(f"Markdown content length: {len(markdown_content)} chars")
        logger.debug(f"Number of replacements to make: {len(svg_replacements)}")
        
        if not svg_replacements:
            logger.info("No SVG replacements to make, returning original markdown")
            return markdown_content
        
        original_content = markdown_content
        replacements_made = 0
        
        for placeholder, ascii_diagram in svg_replacements.items():
            logger.debug(f"Looking for placeholder: {placeholder}")
            
            # Count occurrences before replacement
            occurrence_count = markdown_content.count(placeholder)
            logger.debug(f"Placeholder '{placeholder}' found {occurrence_count} times in markdown")
            
            if occurrence_count == 0:
                logger.warning(f"Placeholder '{placeholder}' not found in markdown content!")
                # Let's search for similar placeholders to debug
                similar_placeholders = [line.strip() for line in markdown_content.split('\n') if 'SVG_PLACEHOLDER' in line]
                logger.debug(f"Found these SVG placeholders in markdown: {similar_placeholders}")
                continue
            
            # Perform replacement
            logger.debug(f"Replacing placeholder with ASCII diagram ({len(ascii_diagram)} chars)")
            markdown_content = markdown_content.replace(placeholder, ascii_diagram)
            replacements_made += 1
            
            # Verify replacement
            remaining_count = markdown_content.count(placeholder)
            logger.debug(f"After replacement: {occurrence_count - remaining_count} instances replaced, {remaining_count} remaining")
            
            if remaining_count > 0:
                logger.warning(f"Still {remaining_count} instances of '{placeholder}' remaining after replacement")
        
        logger.info(f"Placeholder replacement completed: {replacements_made}/{len(svg_replacements)} replacements made")
        logger.debug(f"Final markdown length: {len(markdown_content)} chars (original: {len(original_content)})")
        
        # Check if any placeholders remain in the final content
        remaining_placeholders = [line.strip() for line in markdown_content.split('\n') if 'SVG_PLACEHOLDER' in line]
        if remaining_placeholders:
            logger.warning(f"Found {len(remaining_placeholders)} unreplaced SVG placeholders: {remaining_placeholders[:3]}{'...' if len(remaining_placeholders) > 3 else ''}")
        else:
            logger.info("All SVG placeholders successfully replaced")
        
        return markdown_content
    
    def filter_css_mermaid_content(self, content: str) -> str:
        """Filter out CSS/Mermaid content from markdown."""
        lines = content.split('\n')
        filtered_lines = []
        in_code_block = False
        skip_css_block = False
        
        for line in lines:
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                # Check if this is a CSS/Mermaid block
                if in_code_block and ('#mermaid-' in line or 'font-family:ui-sans-serif' in line):
                    skip_css_block = True
                elif not in_code_block:
                    skip_css_block = False
                
                # Don't include the opening ``` for CSS blocks
                if not skip_css_block:
                    filtered_lines.append(line)
                continue
            
            # Skip CSS/Mermaid content in code blocks
            if skip_css_block:
                continue
                
            # Skip lines that look like CSS/Mermaid IDs or properties
            if (line.strip().startswith('#mermaid-') or 
                'font-family:ui-sans-serif' in line or
                '@keyframes' in line or
                'stroke-dasharray' in line):
                continue
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
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
            '.menu',
            '.header-nav',
            '.footer',
            '.page-nav',
            '.breadcrumb'
        ]
        
        for selector in nav_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
        
        # Remove elements containing promotional text
        promotional_texts = [
            'Get free private DeepWikis',
            'Ask Devin about',
            'Deep Research',
            'Last indexed',
            'Refresh this wiki'
        ]
        
        for text in promotional_texts:
            elements = soup.find_all(string=lambda s: s and text in s)
            for element in elements:
                if element.parent:
                    element.parent.decompose()
        
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