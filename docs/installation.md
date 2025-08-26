# Installation Guide

## Requirements

- **Python 3.8+** - Required for modern async/await features
- **Google Chrome** - Required for browser automation (optional for fallback mode)

## Quick Install

```bash
pip install deepwiki2md
```

## Development Install

For development or to get the latest features:

```bash
git clone https://github.com/deepwiki2md/deepwiki2md.git
cd deepwiki2md
pip install -e .
```

## Virtual Environment (Recommended)

Using a virtual environment helps avoid dependency conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install package
pip install deepwiki2md
```

## Installing Chrome

### Ubuntu/Debian

```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install -y google-chrome-stable
```

### macOS

```bash
# Using Homebrew
brew install --cask google-chrome
```

### Windows

Download and install from [https://www.google.com/chrome/](https://www.google.com/chrome/)

## Verifying Installation

Test your installation:

```python
import deepwiki2md
print(deepwiki2md.__version__)

# Test browser automation availability
from deepwiki2md import _USE_PYDOLL
print(f"Browser automation available: {_USE_PYDOLL}")
```

Command line test:

```bash
deepwiki2md --help
```

## Troubleshooting

### Common Issues

#### Chrome Not Found

**Error:** `Chrome executable not found`

**Solution:**
1. Install Google Chrome following the instructions above
2. Ensure Chrome is in your system PATH
3. Try restarting your terminal/IDE

#### Permission Errors (Linux)

**Error:** `Permission denied` when installing

**Solution:**
```bash
# Install in user directory
pip install --user deepwiki2md

# Or use sudo (not recommended)
sudo pip install deepwiki2md
```

#### Externally Managed Environment

**Error:** `This environment is externally managed`

**Solution:** Use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install deepwiki2md
```

#### Network/Firewall Issues

**Error:** Connection timeouts or SSL errors

**Solution:**
```bash
# Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org deepwiki2md

# Or configure proxy if needed
pip install --proxy http://proxy.server:port deepwiki2md
```

### Dependency Issues

If you encounter dependency conflicts:

```bash
# Update pip first
pip install --upgrade pip

# Force reinstall dependencies
pip install --force-reinstall deepwiki2md

# Or install specific versions
pip install "beautifulsoup4>=4.12.0" "markdownify>=0.11.6"
```

## Optional Dependencies

### Development Tools

For development and testing:

```bash
pip install deepwiki2md[dev]
```

This includes:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `mypy` - Type checking

### Performance

For better performance with large sites:

```bash
# Faster HTML parsing
pip install lxml

# Faster async operations
pip install uvloop  # Linux/macOS only
```

## Docker Installation

For containerized environments:

```dockerfile
FROM python:3.11-slim

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt-get install -y google-chrome-stable

# Install deepwiki2md
RUN pip install deepwiki2md

# Set working directory
WORKDIR /app

# Run scraper
CMD ["deepwiki2md", "scrape", "--help"]
```

## Environment Variables

Configure behavior with environment variables:

```bash
# Disable headless mode
export DEEPWIKI2MD_HEADLESS=false

# Custom output directory
export DEEPWIKI2MD_OUTPUT_DIR=/path/to/output

# Enable debug logging
export DEEPWIKI2MD_LOG_LEVEL=DEBUG
```

## Next Steps

After installation, see:
- [Usage Guide](usage.md) - How to use the package
- [API Reference](api.md) - Detailed API documentation
- [Examples](../examples/) - Code examples