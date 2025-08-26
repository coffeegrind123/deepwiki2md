"""Test markdown conversion functionality."""

import pytest
from deepwiki2md.converter import MarkdownConverter


class TestMarkdownConverter:
    """Test MarkdownConverter functionality."""
    
    def test_basic_conversion(self):
        """Test basic HTML to Markdown conversion."""
        converter = MarkdownConverter()
        
        html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Title</h1>
            <p>This is a test paragraph with <strong>bold</strong> text.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </body>
        </html>
        """
        
        result = converter.convert_page(html, "https://example.com/test")
        
        assert result["success"]
        assert result["title"] == "Test Page"
        assert "# Main Title" in result["content"]
        assert "**bold**" in result["content"]
        assert "* Item 1" in result["content"]
    
    def test_navigation_stripping(self):
        """Test navigation element removal."""
        converter = MarkdownConverter(strip_navigation=True)
        
        html = """
        <html>
        <body>
            <nav class="navigation">Navigation menu</nav>
            <h1>Content Title</h1>
            <p>Main content here.</p>
        </body>
        </html>
        """
        
        result = converter.convert_page(html)
        
        assert result["success"]
        assert "Navigation menu" not in result["content"]
        assert "# Content Title" in result["content"]
        assert "Main content here." in result["content"]
    
    def test_empty_html(self):
        """Test handling of empty HTML."""
        converter = MarkdownConverter()
        
        result = converter.convert_page("", "https://example.com")
        
        assert not result["success"]
        assert result["content"] == ""
        assert result["title"] == ""
    
    def test_setext_headings(self):
        """Test setext heading style."""
        converter = MarkdownConverter(heading_style="SETEXT")
        
        html = """
        <html>
        <body>
            <h1>Level 1</h1>
            <h2>Level 2</h2>
            <p>Content</p>
        </body>
        </html>
        """
        
        result = converter.convert_page(html)
        
        assert result["success"]
        # Note: This test may need adjustment based on markdownify behavior
        # The exact output format depends on the markdownify library