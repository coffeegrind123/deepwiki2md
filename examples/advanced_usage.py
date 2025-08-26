#!/usr/bin/env python3
"""Advanced usage example for deepwiki2md with custom configuration."""

import asyncio
from pathlib import Path
from deepwiki2md import DeepWikiScraper, MarkdownConverter, DeepWikiURL


async def main():
    """Demonstrate advanced scraping with custom configuration."""
    
    # Custom markdown converter settings
    converter = MarkdownConverter(
        heading_style="SETEXT",  # Use setext headings (===, ---)
        strip_navigation=True    # Remove navigation elements
    )
    
    # URL utilities example
    url = DeepWikiURL("https://deepwiki.com/rei-2/Amalgam")
    print(f"📋 Library Analysis:")
    print(f"   Library name: {url.library_name}")
    print(f"   Domain: {url.domain}")
    print(f"   Valid DeepWiki URL: {url.is_valid_deepwiki()}")
    print(f"   Base URL: {url.get_base_url()}")
    print()
    
    # Create output directory
    output_dir = Path("advanced_output")
    output_dir.mkdir(exist_ok=True)
    
    # Scraper with custom settings
    scraper = DeepWikiScraper(
        output_dir=str(output_dir),
        headless=False  # Show browser for debugging
    )
    
    try:
        print("🚀 Starting advanced scraping...")
        
        # Scrape multiple libraries concurrently
        libraries = [
            "https://deepwiki.com/rei-2/Amalgam"
        ]
        
        results = await scraper.scrape_multiple_libraries(
            libraries, 
            save_files=True
        )
        
        print(f"✅ Completed scraping {len(results)} libraries")
        
        # Process results
        for library_url, pages in results.items():
            library_name = DeepWikiURL(library_url).library_name
            print(f"📚 {library_name}: {len(pages)} pages")
            
            # Show file sizes
            library_dir = output_dir / library_name
            if library_dir.exists():
                total_size = sum(
                    f.stat().st_size 
                    for f in library_dir.glob("*.md") 
                    if f.is_file()
                )
                print(f"   Total size: {total_size:,} bytes")
        
        print(f"\n📁 Output saved to: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"❌ Error during advanced scraping: {e}")
    
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())