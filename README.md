# deepwiki-to-md

A Python package to scrape and convert deepwiki content to Markdown format.

## Features

- Scrapes deepwiki pages using browser automation (pydoll)
- Converts content to clean Markdown format
- Handles dynamic content loading in React/Next.js applications
- Supports multiple pages and navigation structures
- Preserves content hierarchy and links

## Installation

```bash
pip install deepwiki-to-md
```

## Usage

### Command Line Interface

```bash
# Basic usage
deepwiki-to-md https://deepwiki.com/rei-2/Amalgam/

# Specify output directory
deepwiki-to-md https://deepwiki.com/rei-2/Amalgam/ --output-dir ./docs
```

### Python API

```python
from deepwiki_to_md import DeepwikiScraper

# Create scraper instance
scraper = DeepwikiScraper(output_dir="Documents")

# Scrape a library
scraper.scrape_library("Amalgam", "https://deepwiki.com/rei-2/Amalgam/")

# Or scrape multiple libraries
libraries = [
    {"name": "Amalgam", "url": "https://deepwiki.com/rei-2/Amalgam/"},
    # Add more libraries as needed
]
scraper.run(libraries)
```

## Requirements

- Python 3.7+
- pydoll (for browser automation)
- beautifulsoup4
- markdownify
- requests

## Changes in v0.4.0

- Added pydoll browser automation for dynamic content handling
- Fixed compatibility with React/Next.js based deepwiki sites
- Improved content extraction and navigation parsing
- Enhanced error handling and logging

## License

MIT License