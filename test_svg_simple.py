#!/usr/bin/env python3
"""Simple test to check if SVG conversion is working by testing the converter directly."""

import logging
from deepwiki2md.svg_converter import SVGToD2Converter
from deepwiki2md.utils import ContentCleaner

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_svg_conversion():
    """Test SVG conversion with a simple example."""
    
    # Initialize SVG converter
    svg_converter = SVGToD2Converter(
        api_base_url='https://portal.qwen.ai/v1',
        api_key='67K-uSto8g1OIfQucSCVfDamZxHNwlKFMDRz7D4-PAH0c56Tyn_nNM3YgGlqDFfpCHET9OjGYmOXn87DRKcrEA',
        model='qwen3-coder-plus'
    )
    
    # Create a simple test SVG
    test_svg = '''<svg aria-roledescription="flowchart-v2" class="flowchart" xmlns="http://www.w3.org/2000/svg">
    <g class="node">
        <foreignObject><div>Step 1<br/>Initialize</div></foreignObject>
    </g>
    <g class="node">
        <foreignObject><div>Step 2<br/>Process</div></foreignObject>
    </g>
    <g class="edgePaths">
        <path id="L_Step1_Step2_0"></path>
    </g>
    </svg>'''
    
    print("=== Testing SVG Converter Directly ===")
    result = svg_converter.convert_svg_to_ascii(test_svg)
    
    print(f"Conversion Result:")
    print(f"- Success: {result['success']}")
    print(f"- Error: {result.get('error', 'None')}")
    print(f"- D2 Code: {len(result.get('d2_code', ''))} chars")
    print(f"- ASCII Diagram: {len(result.get('ascii_diagram', ''))} chars")
    
    if result.get('d2_code'):
        print(f"\nD2 Code:\n{result['d2_code']}")
    
    if result.get('ascii_diagram'):
        print(f"\nASCII Diagram:\n{result['ascii_diagram']}")
    
    # Test with ContentCleaner
    print("\n=== Testing ContentCleaner ===")
    content_cleaner = ContentCleaner(svg_converter)
    
    # Create test HTML with SVG
    test_html = f'''
    <div>
        <h2>Test Page</h2>
        <p>This is a test with an SVG:</p>
        {test_svg}
        <p>End of test</p>
    </div>
    '''
    
    print(f"Original HTML length: {len(test_html)}")
    
    # Extract and convert SVGs
    modified_html, svg_replacements = content_cleaner.extract_and_convert_svgs(test_html)
    
    print(f"Modified HTML length: {len(modified_html)}")
    print(f"SVG replacements: {len(svg_replacements)}")
    
    for placeholder, ascii_diagram in svg_replacements.items():
        print(f"Placeholder: {placeholder}")
        print(f"ASCII Diagram ({len(ascii_diagram)} chars):\n{ascii_diagram}\n")
    
    # Test markdown conversion simulation
    print("=== Testing Placeholder Replacement ===")
    
    # Simulate converting HTML to markdown (simplified)
    fake_markdown = f"""# Test Page

This is a test with an SVG:

{list(svg_replacements.keys())[0] if svg_replacements else 'NO_PLACEHOLDER'}

End of test"""
    
    print(f"Fake markdown before replacement:\n{fake_markdown}\n")
    
    # Test replacement
    final_markdown = content_cleaner.insert_svg_replacements(fake_markdown, svg_replacements)
    
    print(f"Final markdown after replacement:\n{final_markdown}\n")

if __name__ == "__main__":
    test_svg_conversion()