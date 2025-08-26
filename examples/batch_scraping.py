#!/usr/bin/env python3
"""Batch scraping example for multiple DeepWiki libraries."""

import asyncio
from pathlib import Path
from deepwiki2md import DeepWikiScraper, DeepWikiURL


async def main():
    """Demonstrate batch scraping of multiple libraries."""
    
    # List of libraries to scrape
    libraries = [
        "https://deepwiki.com/rei-2/Amalgam",
        # Add more libraries here as needed
    ]
    
    # Validate URLs first
    print("🔍 Validating URLs...")
    valid_libraries = []
    
    for url_str in libraries:
        url = DeepWikiURL(url_str)
        if url.is_valid_deepwiki():
            valid_libraries.append(url_str)
            print(f"   ✅ {url.library_name}")
        else:
            print(f"   ❌ Invalid URL: {url_str}")
    
    if not valid_libraries:
        print("❌ No valid URLs found. Exiting.")
        return
    
    print(f"\n📦 Starting batch scraping of {len(valid_libraries)} libraries...")
    
    # Create batch output directory
    batch_output = Path("batch_output")
    batch_output.mkdir(exist_ok=True)
    
    # Create scraper
    scraper = DeepWikiScraper(
        output_dir=str(batch_output),
        headless=True  # Use headless mode for batch operations
    )
    
    try:
        # Track progress
        total_pages = 0
        successful_libraries = 0
        
        # Scrape libraries concurrently
        results = await scraper.scrape_multiple_libraries(
            valid_libraries,
            save_files=True
        )
        
        # Process results
        print("\n📊 Batch Scraping Results:")
        print("=" * 50)
        
        for library_url, pages in results.items():
            url = DeepWikiURL(library_url)
            library_name = url.library_name
            
            if pages:
                successful_libraries += 1
                page_count = len(pages)
                total_pages += page_count
                
                # Calculate total content size
                total_chars = sum(len(page['content']) for page in pages)
                
                print(f"✅ {library_name}")
                print(f"   Pages: {page_count}")
                print(f"   Characters: {total_chars:,}")
                
                # Show file info
                library_dir = batch_output / library_name
                if library_dir.exists():
                    files = list(library_dir.glob("*.md"))
                    total_size = sum(f.stat().st_size for f in files)
                    print(f"   Files: {len(files)} ({total_size:,} bytes)")
            else:
                print(f"❌ {library_name} - Failed to scrape")
            
            print()
        
        # Final summary
        print("📈 Final Summary:")
        print(f"   Libraries processed: {len(valid_libraries)}")
        print(f"   Successful: {successful_libraries}")
        print(f"   Total pages: {total_pages}")
        print(f"   Output directory: {batch_output.absolute()}")
        
        if successful_libraries < len(valid_libraries):
            failed_count = len(valid_libraries) - successful_libraries
            print(f"   ⚠️  {failed_count} libraries failed")
    
    except Exception as e:
        print(f"❌ Batch scraping failed: {e}")
    
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())