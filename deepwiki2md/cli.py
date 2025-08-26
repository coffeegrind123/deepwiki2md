"""Command-line interface for deepwiki2md."""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import List

from .scraper import DeepWikiScraper
from .utils import DeepWikiURL


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


async def scrape_command(args) -> None:
    """Execute the scrape command."""
    # Prepare converter kwargs for SVG conversion
    converter_kwargs = {}
    if args.svg_api_base_url:
        converter_kwargs['svg_api_base_url'] = args.svg_api_base_url
    if args.svg_api_key:
        converter_kwargs['svg_api_key'] = args.svg_api_key
    if args.svg_model:
        converter_kwargs['svg_model'] = args.svg_model
    
    scraper = DeepWikiScraper(
        output_dir=args.output_dir,
        headless=not args.show_browser,
        converter_kwargs=converter_kwargs
    )
    
    if len(args.urls) == 1:
        # Single library
        url = args.urls[0]
        deepwiki_url = DeepWikiURL(url)
        
        if not deepwiki_url.is_valid_deepwiki():
            print(f"Error: Invalid DeepWiki URL: {url}")
            sys.exit(1)
            
        print(f"Scraping library: {deepwiki_url.library_name}")
        pages = await scraper.scrape_library(url, save_files=True)
        print(f"Successfully scraped {len(pages)} pages")
        
    else:
        # Multiple libraries
        print(f"Scraping {len(args.urls)} libraries...")
        results = await scraper.scrape_multiple_libraries(args.urls, save_files=True)
        
        total_pages = sum(len(pages) for pages in results.values())
        print(f"Successfully scraped {total_pages} pages from {len(results)} libraries")
        
        for library_name, pages in results.items():
            print(f"  - {library_name}: {len(pages)} pages")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DeepWiki to Markdown converter using PyDoll",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  deepwiki2md scrape https://deepwiki.com/rei-2/Amalgam
  deepwiki2md scrape https://deepwiki.com/project/lib1 https://deepwiki.com/project/lib2
  deepwiki2md scrape --output-dir ./docs --show-browser https://deepwiki.com/project/lib
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape DeepWiki content')
    scrape_parser.add_argument(
        'urls',
        nargs='+',
        help='DeepWiki URLs to scrape'
    )
    scrape_parser.add_argument(
        '--output-dir', '-o',
        default='output',
        help='Output directory for markdown files (default: output)'
    )
    scrape_parser.add_argument(
        '--show-browser',
        action='store_true',
        help='Show browser window (default: headless)'
    )
    scrape_parser.add_argument(
        '--svg-api-base-url',
        help='OpenAI-compatible API base URL for SVG flowchart conversion (e.g., http://localhost:1234/v1)'
    )
    scrape_parser.add_argument(
        '--svg-api-key',
        help='API key for SVG flowchart conversion'
    )
    scrape_parser.add_argument(
        '--svg-model',
        default='gpt-4o-mini',
        help='Model name for SVG flowchart conversion (default: gpt-4o-mini)'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    if args.command == 'scrape':
        try:
            asyncio.run(scrape_command(args))
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()