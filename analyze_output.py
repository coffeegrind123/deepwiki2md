#!/usr/bin/env python3
"""Analyze the output to understand what happened with SVG conversion."""

import re
from pathlib import Path

def analyze_output():
    """Analyze the generated markdown files."""
    
    output_dir = Path('output/Amalgam')
    
    if not output_dir.exists():
        print("No output directory found!")
        return
    
    for md_file in output_dir.glob('*.md'):
        print(f"\n=== Analyzing {md_file.name} ===")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count empty code blocks
        empty_blocks = 0
        total_blocks = 0
        lines = content.split('\n')
        
        in_code_block = False
        code_block_content = []
        
        for i, line in enumerate(lines):
            if line.strip() == '```':
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    total_blocks += 1
                    code_block_content = []
                else:
                    # Ending a code block
                    in_code_block = False
                    if not any(code_block_content):  # All lines were empty
                        empty_blocks += 1
                        print(f"  Empty code block found at line {i - len(code_block_content) - 1}")
            elif in_code_block:
                code_block_content.append(line.strip())
        
        print(f"  Total code blocks: {total_blocks}")
        print(f"  Empty code blocks: {empty_blocks}")
        print(f"  File length: {len(content)} chars")
        
        # Check for SVG-related content
        svg_mentions = len(re.findall(r'svg|SVG|flowchart|placeholder', content, re.IGNORECASE))
        print(f"  SVG/flowchart/placeholder mentions: {svg_mentions}")
        
        # Look for any remaining placeholders
        placeholders = re.findall(r'SVG_PLACEHOLDER_\d+', content)
        if placeholders:
            print(f"  Found unreplaced placeholders: {placeholders}")
        
        # Check for ASCII art patterns
        ascii_boxes = len(re.findall(r'[┌└│─]', content))
        if ascii_boxes > 0:
            print(f"  ASCII box characters found: {ascii_boxes}")

if __name__ == "__main__":
    analyze_output()