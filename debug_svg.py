#!/usr/bin/env python3
"""Debug SVG conversion issue by testing with actual SVG content."""

import asyncio
import logging
from pathlib import Path
from deepwiki2md.scraper import DeepWikiScraper
from deepwiki2md.converter import MarkdownConverter
from deepwiki2md.utils import ContentCleaner
from deepwiki2md.svg_converter import SVGToD2Converter

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_svg_debug():
    """Test SVG conversion with detailed debugging."""
    
    # Initialize SVG converter
    svg_converter = SVGToD2Converter(
        api_base_url='https://portal.qwen.ai/v1',
        api_key='67K-uSto8g1OIfQucSCVfDamZxHNwlKFMDRz7D4-PAH0c56Tyn_nNM3YgGlqDFfpCHET9OjGYmOXn87DRKcrEA',
        model='qwen3-coder-plus'
    )
    
    # Initialize scraper to get actual HTML content
    converter_kwargs = {
        'svg_api_base_url': 'https://portal.qwen.ai/v1',
        'svg_api_key': '67K-uSto8g1OIfQucSCVfDamZxHNwlKFMDRz7D4-PAH0c56Tyn_nNM3YgGlqDFfpCHET9OjGYmOXn87DRKcrEA',
        'svg_model': 'qwen3-coder-plus'
    }
    
    scraper = DeepWikiScraper(
        output_dir='debug_output',
        headless=True,
        converter_kwargs=converter_kwargs
    )
    
    try:
        from pydoll.browser.chromium import Chrome
        from pydoll.browser.options import ChromiumOptions
        
        options = ChromiumOptions()
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        
        async with Chrome(options=options) as browser:
            tab = await browser.open_tab()
            
            # Get the content from the Getting Started page
            url = 'https://deepwiki.com/rei-2/Amalgam/2-getting-started'
            print(f"Navigating to: {url}")
            
            html_content = await scraper._get_page_content(tab, url)
            
            if html_content:
                print(f"Retrieved HTML content: {len(html_content)} chars")
                
                # Test SVG extraction and conversion
                content_cleaner = ContentCleaner(svg_converter)
                
                print("=== Starting SVG extraction test ===")
                modified_html, svg_replacements = content_cleaner.extract_and_convert_svgs(html_content)
                
                print(f"SVG extraction results:")
                print(f"- Original HTML length: {len(html_content)}")
                print(f"- Modified HTML length: {len(modified_html)}")
                print(f"- SVG replacements created: {len(svg_replacements)}")
                
                for placeholder, ascii_diagram in svg_replacements.items():
                    print(f"- {placeholder}: {len(ascii_diagram)} chars")
                    print(f"  Preview: {ascii_diagram[:100]}...")
                
                # Now test markdown conversion
                print("=== Testing markdown conversion ===")
                markdown_content = scraper.converter.html_to_markdown(modified_html, svg_replacements)
                
                print(f"Markdown conversion results:")
                print(f"- Markdown length: {len(markdown_content)}")
                
                # Check for remaining placeholders
                remaining_placeholders = [line for line in markdown_content.split('\n') if 'SVG_PLACEHOLDER' in line]
                if remaining_placeholders:
                    print(f"WARNING: {len(remaining_placeholders)} unreplaced placeholders found:")
                    for placeholder in remaining_placeholders[:5]:
                        print(f"  - {placeholder.strip()}")
                else:
                    print("SUCCESS: All placeholders were replaced")
                
                # Save debug output
                debug_dir = Path('debug_output')
                debug_dir.mkdir(exist_ok=True)
                
                with open(debug_dir / 'debug_html.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                with open(debug_dir / 'debug_modified_html.html', 'w', encoding='utf-8') as f:
                    f.write(modified_html)
                
                with open(debug_dir / 'debug_markdown.md', 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print("Debug files saved to debug_output/")
                
            else:
                print("Failed to retrieve HTML content")
                
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_svg_debug())