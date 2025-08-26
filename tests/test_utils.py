"""Test utilities and URL handling."""

import pytest
from deepwiki2md.utils import DeepWikiURL


class TestDeepWikiURL:
    """Test DeepWikiURL functionality."""
    
    def test_valid_deepwiki_url(self):
        """Test valid DeepWiki URL parsing."""
        url = DeepWikiURL("https://deepwiki.com/rei-2/Amalgam")
        
        assert url.is_valid_deepwiki()
        assert url.domain == "deepwiki.com"
        assert url.library_name == "Amalgam"
        assert url.get_base_url() == "https://deepwiki.com"
    
    def test_invalid_url(self):
        """Test invalid URL handling."""
        url = DeepWikiURL("https://example.com/not-deepwiki")
        
        assert not url.is_valid_deepwiki()
        assert url.domain == "example.com"
    
    def test_url_with_path(self):
        """Test URL with additional path components."""
        url = DeepWikiURL("https://deepwiki.com/rei-2/Amalgam/1-overview")
        
        assert url.is_valid_deepwiki()
        assert url.library_name == "Amalgam"
        assert len(url.path_parts) == 3
    
    def test_malformed_url(self):
        """Test malformed URL handling."""
        url = DeepWikiURL("not-a-url")
        
        assert not url.is_valid_deepwiki()
        assert url.domain == ""
    
    def test_empty_url(self):
        """Test empty URL handling."""
        url = DeepWikiURL("")
        
        assert not url.is_valid_deepwiki()
        assert url.domain == ""
        assert url.library_name == ""