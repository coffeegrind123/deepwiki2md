# API Reference

## DeepWikiScraper

The main scraper class for extracting DeepWiki content.

```python
from deepwiki2md import DeepWikiScraper

scraper = DeepWikiScraper(output_dir="output", headless=True)
```

### Constructor Parameters

- **output_dir** (str): Directory to save markdown files. Default: `"output"`
- **headless** (bool): Whether to run browser in headless mode. Default: `True`

### Methods

#### `async scrape_page(url: str) -> Optional[Dict[str, Any]]`

Scrape a single page and convert to markdown.

**Parameters:**
- `url` (str): URL of the DeepWiki page to scrape

**Returns:**
- Dictionary with keys: `url`, `title`, `content`, `html`
- `None` if scraping fails

**Example:**
```python
page = await scraper.scrape_page("https://deepwiki.com/rei-2/Amalgam/1-overview")
if page:
    print(f"Title: {page['title']}")
    print(f"Content: {page['content'][:100]}...")
```

#### `async scrape_library(url: str, save_files: bool = True) -> List[Dict[str, Any]]`

Scrape an entire DeepWiki library by following navigation links.

**Parameters:**
- `url` (str): Base URL of the DeepWiki library
- `save_files` (bool): Whether to save files to disk. Default: `True`

**Returns:**
- List of scraped page dictionaries

**Example:**
```python
pages = await scraper.scrape_library("https://deepwiki.com/rei-2/Amalgam")
print(f"Scraped {len(pages)} pages")
```

#### `async scrape_multiple_libraries(urls: List[str], save_files: bool = True) -> Dict[str, List[Dict[str, Any]]]`

Scrape multiple libraries concurrently.

**Parameters:**
- `urls` (List[str]): List of DeepWiki library URLs
- `save_files` (bool): Whether to save files to disk. Default: `True`

**Returns:**
- Dictionary mapping library names to lists of scraped pages

**Example:**
```python
results = await scraper.scrape_multiple_libraries([
    "https://deepwiki.com/rei-2/Amalgam",
    "https://deepwiki.com/other/Library"
])
```

#### `async close()`

Close the browser connection and clean up resources.

**Example:**
```python
try:
    # Scraping operations
    pass
finally:
    await scraper.close()
```

## MarkdownConverter

Converts HTML content to clean Markdown format.

```python
from deepwiki2md import MarkdownConverter

converter = MarkdownConverter(heading_style="ATX", strip_navigation=True)
```

### Constructor Parameters

- **heading_style** (str): Heading style to use. Options: `"ATX"` (default), `"SETEXT"`
- **strip_navigation** (bool): Whether to remove navigation elements. Default: `True`

### Methods

#### `convert_page(html_content: str, url: str = None) -> Dict[str, Any]`

Convert HTML page content to markdown.

**Parameters:**
- `html_content` (str): Raw HTML content to convert
- `url` (str, optional): Source URL for context

**Returns:**
- Dictionary with keys: `content`, `title`, `success`

**Example:**
```python
result = converter.convert_page(html_content, url="https://example.com")
if result['success']:
    print(f"Title: {result['title']}")
    print(f"Markdown: {result['content']}")
```

## DeepWikiURL

Utility class for handling and parsing DeepWiki URLs.

```python
from deepwiki2md import DeepWikiURL

url = DeepWikiURL("https://deepwiki.com/rei-2/Amalgam")
```

### Properties

- **domain** (str): Extract domain from URL
- **library_name** (str): Extract library name from URL path
- **path_parts** (List[str]): Get URL path components as list

### Methods

#### `is_valid_deepwiki() -> bool`

Check if the URL is a valid DeepWiki URL.

**Returns:**
- `True` if URL is valid DeepWiki format, `False` otherwise

**Example:**
```python
if url.is_valid_deepwiki():
    print("Valid DeepWiki URL")
```

#### `get_base_url() -> str`

Get the base URL (protocol + domain) for the site.

**Returns:**
- Base URL string

**Example:**
```python
base = url.get_base_url()  # "https://deepwiki.com"
```

## Error Handling

All methods include comprehensive error handling:

- **Network errors**: Automatic retries with exponential backoff
- **Parsing errors**: Graceful fallback and logging
- **Timeout errors**: Configurable timeout limits
- **Browser errors**: Fallback to requests-based scraping

## Logging

The package uses Python's standard logging module:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger('deepwiki2md')
logger.setLevel(logging.INFO)
```

## Constants

### `_USE_PYDOLL`

Boolean indicating whether PyDoll browser automation is available.

```python
from deepwiki2md import _USE_PYDOLL

if _USE_PYDOLL:
    print("Using browser automation")
else:
    print("Using fallback scraping")
```