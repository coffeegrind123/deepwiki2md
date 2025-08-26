"""
deepwiki2md - A modern Python package for scraping DeepWiki content to Markdown

This package provides a clean, async interface for converting DeepWiki documentation
to Markdown format using PyDoll for reliable browser automation.
"""

from .converter import MarkdownConverter
from .utils import DeepWikiURL

# Try to use PyDoll scraper with Chrome browser automation
try:
    from pydoll.browser.chromium import Chrome
    from .scraper import DeepWikiScraper
    _USE_PYDOLL = True
except ImportError:
    # Fall back to requests-based scraper if PyDoll is not available
    from .fallback_scraper import FallbackScraper as DeepWikiScraper
    _USE_PYDOLL = False

__version__ = "1.0.0"
__all__ = ["DeepWikiScraper", "MarkdownConverter", "DeepWikiURL"]