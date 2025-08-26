"""Test script to verify the deepwiki2md implementation."""

import asyncio
import logging
from deepwiki2md import DeepWikiScraper, _USE_PYDOLL

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_scraper():
    """Test the scraper with a real DeepWiki URL."""
    scraper = DeepWikiScraper(output_dir="test_output", headless=True)
    
    # Test URL from the requirement
    test_url = "https://deepwiki.com/rei-2/Amalgam"
    
    print(f"Testing scraper with URL: {test_url}")
    print(f"Using PyDoll: {_USE_PYDOLL}")
    
    try:
        # Test single page scraping first
        print("Testing single page scraping...")
        page_result = await scraper.scrape_page(test_url)
        
        if page_result:
            print(f"✓ Single page scraping successful!")
            print(f"  Title: {page_result['title']}")
            print(f"  Content length: {len(page_result['content'])} characters")
        else:
            print("✗ Single page scraping failed")
            return
            
        # Test library scraping
        print("\nTesting library scraping...")
        library_results = await scraper.scrape_library(test_url, save_files=True)
        
        if library_results:
            print(f"✓ Library scraping successful!")
            print(f"  Scraped {len(library_results)} pages")
            for page in library_results[:3]:  # Show first 3 pages
                print(f"    - {page['title']}")
            if len(library_results) > 3:
                print(f"    ... and {len(library_results) - 3} more")
        else:
            print("✗ Library scraping failed")
            
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())