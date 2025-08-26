#!/usr/bin/env python3
"""Test with real SVG content from DeepWiki to diagnose the issue."""

import asyncio
import logging
import re
from pathlib import Path
from deepwiki2md.scraper import DeepWikiScraper
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def extract_real_svg():
    """Extract actual SVG content from DeepWiki for testing."""
    
    options = ChromiumOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    async with Chrome(options=options) as browser:
        tab = await browser.start()
        
        # Navigate to the Getting Started page which has SVGs
        url = 'https://deepwiki.com/rei-2/Amalgam/2-getting-started'
        await tab.navigate(url)
        await tab.wait_for_load_state('networkidle')
        
        # Get page HTML
        html_content = await tab.eval('document.documentElement.outerHTML')
        
        # Find SVG flowcharts
        svg_pattern = r'<svg[^>]*aria-roledescription="flowchart[^"]*"[^>]*>.*?</svg>'
        matches = re.findall(svg_pattern, html_content, flags=re.DOTALL | re.IGNORECASE)
        
        print(f"Found {len(matches)} SVG flowcharts")
        
        # Save them for analysis
        output_dir = Path('real_svg_debug')
        output_dir.mkdir(exist_ok=True)
        
        for i, svg_content in enumerate(matches):
            svg_file = output_dir / f'svg_{i}.svg'
            with open(svg_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"Saved SVG {i} to {svg_file} ({len(svg_content)} chars)")
            
            # Print preview
            preview = svg_content[:500] + "..." if len(svg_content) > 500 else svg_content
            print(f"SVG {i} preview:\n{preview}\n")
        
        # Save full HTML for reference
        with open(output_dir / 'full_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Saved full page HTML to {output_dir / 'full_page.html'}")
        return matches

async def test_real_svg_conversion():
    """Test the actual SVG conversion with real content."""
    
    # First extract real SVGs
    real_svgs = await extract_real_svg()
    
    if not real_svgs:
        print("No SVGs found!")
        return
    
    # Test conversion with the first real SVG
    from deepwiki2md.svg_converter import SVGToD2Converter
    
    svg_converter = SVGToD2Converter(
        api_base_url='https://portal.qwen.ai/v1',
        api_key='67K-uSto8g1OIfQucSCVfDamZxHNwlKFMDRz7D4-PAH0c56Tyn_nNM3YgGlqDFfpCHET9OjGYmOXn87DRKcrEA',
        model='qwen3-coder-plus'
    )
    
    print(f"\n=== Testing conversion of first real SVG ===")
    test_svg = real_svgs[0]
    print(f"Testing SVG with {len(test_svg)} chars")
    
    result = svg_converter.convert_svg_to_ascii(test_svg)
    
    print(f"Conversion result:")
    print(f"- Success: {result['success']}")
    print(f"- Error: {result.get('error', 'None')}")
    print(f"- D2 Code Length: {len(result.get('d2_code', ''))}")
    print(f"- ASCII Diagram Length: {len(result.get('ascii_diagram', ''))}")
    
    if result.get('d2_code'):
        print(f"\nD2 Code:\n{result['d2_code']}")
        
        # Save D2 code for inspection
        with open('real_svg_debug/real_d2_code.d2', 'w', encoding='utf-8') as f:
            f.write(result['d2_code'])
    
    if result.get('ascii_diagram'):
        print(f"\nASCII Diagram:\n{result['ascii_diagram']}")
        
        # Save ASCII diagram for inspection
        with open('real_svg_debug/real_ascii_diagram.txt', 'w', encoding='utf-8') as f:
            f.write(result['ascii_diagram'])
    else:
        print("\nNo ASCII diagram generated!")

if __name__ == "__main__":
    asyncio.run(test_real_svg_conversion())