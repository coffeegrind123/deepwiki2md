# deepwiki2md

A modern Python package for scraping DeepWiki content to Markdown using PyDoll browser automation.

## Features

- **Browser Automation**: Uses PyDoll for reliable JavaScript-heavy site scraping
- **Async Support**: Full async/await support for efficient concurrent operations
- **Fallback Support**: Automatic fallback to requests-based scraping when browser automation isn't available
- **Clean API**: Simple, intuitive interface for scraping DeepWiki sites
- **Markdown Conversion**: Converts HTML content to clean Markdown format
- **Navigation Detection**: Automatically discovers and follows site navigation
- **File Organization**: Saves files in organized directory structure

## Installation

### Requirements

- Python 3.8+
- Google Chrome (for full browser automation)

### Install Package

```bash
pip install -e .
```

### Install Dependencies

```bash
pip install pydoll-python beautifulsoup4 markdownify requests
```

### Install Chrome (if not already installed)

**Ubuntu/Debian:**
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install -y google-chrome-stable
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
Download from [https://www.google.com/chrome/](https://www.google.com/chrome/)

## Usage

### Basic Usage

```python
import asyncio
from deepwiki2md import DeepWikiScraper

async def main():
    scraper = DeepWikiScraper(output_dir="output", headless=True)
    
    # Scrape a single page
    page = await scraper.scrape_page("https://deepwiki.com/rei-2/Amalgam")
    print(f"Title: {page['title']}")
    print(f"Content length: {len(page['content'])}")
    
    # Scrape an entire library
    pages = await scraper.scrape_library("https://deepwiki.com/rei-2/Amalgam", save_files=True)
    print(f"Scraped {len(pages)} pages")

asyncio.run(main())
```

### Command Line Interface

```bash
# Scrape a single library
deepwiki2md scrape https://deepwiki.com/rei-2/Amalgam

# Scrape multiple libraries
deepwiki2md scrape https://deepwiki.com/project/lib1 https://deepwiki.com/project/lib2

# Custom output directory
deepwiki2md scrape --output-dir ./docs https://deepwiki.com/rei-2/Amalgam

# Show browser (non-headless mode)
deepwiki2md scrape --show-browser https://deepwiki.com/rei-2/Amalgam
```

### Advanced Usage

```python
from deepwiki2md import DeepWikiScraper, MarkdownConverter, DeepWikiURL

# Custom converter settings
converter = MarkdownConverter(heading_style="SETEXT", strip_navigation=True)

# URL utilities
url = DeepWikiURL("https://deepwiki.com/rei-2/Amalgam")
print(f"Library name: {url.library_name}")
print(f"Is valid: {url.is_valid_deepwiki()}")

# Scraper with custom settings
scraper = DeepWikiScraper(output_dir="custom_output", headless=False)
```

## API Reference

### DeepWikiScraper

The main scraper class for extracting DeepWiki content.

```python
DeepWikiScraper(output_dir="output", headless=True)
```

**Parameters:**
- `output_dir` (str): Directory to save markdown files
- `headless` (bool): Whether to run browser in headless mode

**Methods:**

#### `async scrape_page(url: str) -> Optional[Dict[str, Any]]`

Scrape a single page and convert to markdown.

**Returns:** Dictionary with `url`, `title`, `content`, and `html` keys.

#### `async scrape_library(url: str, save_files: bool = True) -> List[Dict[str, Any]]`

Scrape an entire DeepWiki library by following navigation links.

**Returns:** List of scraped page dictionaries.

#### `async scrape_multiple_libraries(urls: List[str], save_files: bool = True) -> Dict[str, List[Dict[str, Any]]]`

Scrape multiple libraries concurrently.

**Returns:** Dictionary mapping library names to lists of scraped pages.

### MarkdownConverter

Converts HTML content to clean Markdown format.

```python
MarkdownConverter(heading_style="ATX", strip_navigation=True)
```

**Methods:**

#### `convert_page(html_content: str, url: str = None) -> Dict[str, Any]`

Convert HTML page to markdown.

**Returns:** Dictionary with `content`, `title`, and `success` keys.

### DeepWikiURL

Utility class for handling DeepWiki URLs.

```python
url = DeepWikiURL("https://deepwiki.com/rei-2/Amalgam")
```

**Properties:**
- `domain`: Extract domain from URL
- `library_name`: Extract library name from URL path
- `path_parts`: Get URL path as list

**Methods:**
- `is_valid_deepwiki()`: Check if URL is a valid DeepWiki URL
- `get_base_url()`: Get base URL for the site

## Output Structure

```
output/
└── LibraryName/
    ├── Page1.md
    ├── Page2.md
    └── Page3.md
```

## Browser Automation vs Fallback

The package automatically uses:

1. **PyDoll Browser Automation** (preferred): Full JavaScript support, handles dynamic content
2. **Requests Fallback**: Used when Chrome is not available or PyDoll fails

You can check which mode is being used:

```python
from deepwiki2md import _USE_PYDOLL
print(f"Using PyDoll: {_USE_PYDOLL}")
```

## Error Handling

The package includes comprehensive error handling:

- Automatic retries with exponential backoff
- Graceful fallback between scraping methods
- Detailed logging for debugging
- Timeout handling for long-running operations

## Examples

See the `examples/` directory for more usage examples:

- `basic_usage.py`: Simple scraping example
- `advanced_usage.py`: Custom configuration example
- `batch_scraping.py`: Multiple library scraping

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Troubleshooting

### Chrome Not Found

If you get "Chrome not found" errors:

1. Install Google Chrome
2. Ensure it's in your system PATH
3. Try running with `--show-browser` to verify Chrome works

### Memory Issues

For large sites, use headless mode and consider:

```python
# Process in smaller batches
scraper = DeepWikiScraper(headless=True)
```

### Network Issues

The package includes automatic retry logic, but for unreliable connections:

```python
# Increase wait times in scraper implementation
await asyncio.sleep(5)  # Longer waits between requests
```