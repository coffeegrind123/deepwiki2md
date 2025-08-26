#!/usr/bin/env python3
"""Basic usage example for deepwiki2md."""

import asyncio
from deepwiki2md import DeepWikiScraper


async def main():
    """Demonstrate basic scraping functionality."""
    # Create a scraper instance
    scraper = DeepWikiScraper(output_dir="output", headless=True)
    
    try:
        # Scrape a single page
        print("Scraping a single page...")
        page = await scraper.scrape_page("https://deepwiki.com/rei-2/Amalgam/1-overview")
        
        if page:
            print(f"✅ Successfully scraped: {page['title']}")
            print(f"   Content length: {len(page['content'])} characters")
        else:
            print("❌ Failed to scrape page")
        
        # Scrape an entire library
        print("\nScraping entire library...")
        pages = await scraper.scrape_library(
            "https://deepwiki.com/rei-2/Amalgam", 
            save_files=True
        )
        
        print(f"✅ Successfully scraped {len(pages)} pages from library")
        
        # Display summary
        for page in pages[:5]:  # Show first 5 pages
            print(f"   - {page['title']} ({len(page['content'])} chars)")
        
        if len(pages) > 5:
            print(f"   ... and {len(pages) - 5} more pages")
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
    
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())