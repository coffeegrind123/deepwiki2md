# Usage Guide

## Quick Start

### Command Line Usage

Scrape a single DeepWiki library:

```bash
deepwiki2md scrape https://deepwiki.com/rei-2/Amalgam
```

Scrape multiple libraries:

```bash
deepwiki2md scrape \
  https://deepwiki.com/rei-2/Amalgam \
  https://deepwiki.com/other/Library
```

Custom output directory:

```bash
deepwiki2md scrape --output-dir ./docs https://deepwiki.com/rei-2/Amalgam
```

Show browser window (helpful for debugging):

```bash
deepwiki2md scrape --show-browser https://deepwiki.com/rei-2/Amalgam
```

### Python API Usage

#### Basic Single Page Scraping

```python
import asyncio
from deepwiki2md import DeepWikiScraper

async def scrape_single_page():
    scraper = DeepWikiScraper(output_dir="output", headless=True)
    
    try:
        page = await scraper.scrape_page("https://deepwiki.com/rei-2/Amalgam/1-overview")
        
        if page:
            print(f"Title: {page['title']}")
            print(f"Content length: {len(page['content'])} characters")
        else:
            print("Failed to scrape page")
    
    finally:
        await scraper.close()

# Run the async function
asyncio.run(scrape_single_page())
```

#### Scrape Entire Library

```python
import asyncio
from deepwiki2md import DeepWikiScraper

async def scrape_library():
    scraper = DeepWikiScraper(output_dir="output", headless=True)
    
    try:
        # This will automatically discover and scrape all pages
        pages = await scraper.scrape_library(
            "https://deepwiki.com/rei-2/Amalgam", 
            save_files=True
        )
        
        print(f"Successfully scraped {len(pages)} pages")
        for page in pages[:5]:  # Show first 5
            print(f"- {page['title']}")
    
    finally:
        await scraper.close()

asyncio.run(scrape_library())
```

#### Batch Processing Multiple Libraries

```python
import asyncio
from deepwiki2md import DeepWikiScraper

async def batch_scrape():
    scraper = DeepWikiScraper(output_dir="batch_output", headless=True)
    
    libraries = [
        "https://deepwiki.com/rei-2/Amalgam",
        "https://deepwiki.com/other/Project"
    ]
    
    try:
        # Scrape all libraries concurrently
        results = await scraper.scrape_multiple_libraries(
            libraries, 
            save_files=True
        )
        
        for library_url, pages in results.items():
            print(f"Library: {library_url}")
            print(f"Pages: {len(pages)}")
    
    finally:
        await scraper.close()

asyncio.run(batch_scrape())
```

## Advanced Configuration

### Custom Markdown Conversion

```python
from deepwiki2md import MarkdownConverter

# Configure markdown converter
converter = MarkdownConverter(
    heading_style="SETEXT",  # Use === and --- for headings
    strip_navigation=True    # Remove navigation elements
)

# Use with scraper
scraper = DeepWikiScraper(
    output_dir="custom_output",
    headless=True
)
```

### URL Utilities

```python
from deepwiki2md import DeepWikiURL

# Parse and validate URLs
url = DeepWikiURL("https://deepwiki.com/rei-2/Amalgam")

print(f"Valid DeepWiki URL: {url.is_valid_deepwiki()}")
print(f"Library name: {url.library_name}")
print(f"Domain: {url.domain}")
print(f"Base URL: {url.get_base_url()}")
print(f"Path parts: {url.path_parts}")
```

### Error Handling

```python
import asyncio
import logging
from deepwiki2md import DeepWikiScraper

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

async def robust_scraping():
    scraper = DeepWikiScraper(output_dir="output", headless=True)
    
    urls = [
        "https://deepwiki.com/rei-2/Amalgam",
        "https://deepwiki.com/invalid/url",  # This will fail gracefully
    ]
    
    try:
        for url in urls:
            try:
                pages = await scraper.scrape_library(url, save_files=True)
                print(f"✅ Success: {url} ({len(pages)} pages)")
            except Exception as e:
                print(f"❌ Failed: {url} - {e}")
                # Continue with next URL
                
    finally:
        await scraper.close()

asyncio.run(robust_scraping())
```

## Output Structure

The scraper creates organized directory structures:

```
output/
├── Amalgam/
│   ├── Overview.md
│   ├── Getting_Started.md
│   ├── Core_Architecture.md
│   └── ...
└── OtherLibrary/
    ├── Introduction.md
    ├── Setup.md
    └── ...
```

### File Naming

- Spaces in page titles become underscores
- Special characters are removed or replaced
- Files use `.md` extension
- Duplicate names get numeric suffixes

## Browser Automation vs Fallback

The package automatically chooses the best scraping method:

1. **PyDoll Browser Automation** (preferred)
   - Full JavaScript support
   - Handles dynamic content
   - More reliable for complex sites

2. **Requests Fallback** (automatic fallback)
   - Used when Chrome unavailable
   - Lighter weight
   - May miss some dynamic content

Check which mode is active:

```python
from deepwiki2md import _USE_PYDOLL

if _USE_PYDOLL:
    print("Using browser automation")
else:
    print("Using fallback mode")
```

## Performance Tips

### Memory Management

For large sites, use these strategies:

```python
# Use headless mode
scraper = DeepWikiScraper(headless=True)

# Process libraries sequentially instead of concurrently
for library_url in library_urls:
    pages = await scraper.scrape_library(library_url)
    # Process pages immediately
    process_pages(pages)
```

### Rate Limiting

Be respectful to target sites:

```python
import asyncio

async def rate_limited_scraping():
    scraper = DeepWikiScraper()
    
    urls = ["url1", "url2", "url3"]
    
    for url in urls:
        pages = await scraper.scrape_library(url)
        print(f"Scraped {url}: {len(pages)} pages")
        
        # Wait between libraries
        await asyncio.sleep(2)
```

### Concurrent Processing

For multiple independent libraries:

```python
import asyncio

async def concurrent_scraping():
    # Create separate scraper instances for true concurrency
    async def scrape_one(url):
        scraper = DeepWikiScraper(output_dir=f"output_{url.split('/')[-1]}")
        try:
            return await scraper.scrape_library(url)
        finally:
            await scraper.close()
    
    # Run concurrently
    results = await asyncio.gather(*[
        scrape_one("https://deepwiki.com/rei-2/Amalgam"),
        scrape_one("https://deepwiki.com/other/Project")
    ])
    
    return results
```

## Troubleshooting

### Common Issues

#### "No navigation found"
The scraper couldn't find navigation elements on the page. This might mean:
- The URL is not a DeepWiki library page
- The site structure has changed
- JavaScript hasn't loaded yet (try non-headless mode)

#### "Chrome not found"
Install Google Chrome and ensure it's in your system PATH.

#### Memory errors
Use headless mode and process libraries sequentially:
```python
scraper = DeepWikiScraper(headless=True)
```

#### Timeout errors
Increase wait times or use fallback mode:
```python
# The package handles timeouts automatically, but you can
# implement your own retry logic if needed
```

## Next Steps

- See [API Reference](api.md) for detailed API documentation
- Check out [examples/](../examples/) for more code samples
- Read about [browser automation setup](installation.md#installing-chrome)