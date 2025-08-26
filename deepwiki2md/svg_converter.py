"""SVG flowchart to D2 diagram converter using OpenAI-compatible LLM API."""

import os
import logging
import re
import subprocess
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
import requests
import json

logger = logging.getLogger(__name__)


class SVGToD2Converter:
    """Converts SVG flowcharts to ASCII diagrams using LLM and D2."""
    
    SVG_TO_D2_PROMPT = """# SVG Flowchart to D2 Diagram Conversion Prompt

You are tasked with converting an SVG flowchart into working D2 diagram syntax. Follow these steps carefully:

## Step 1: Analyze the SVG Structure
- Look for individual nodes/boxes in the SVG, not containers
- Each `<g class="node">` typically represents a separate component
- Extract the text content from `<foreignObject>` elements within each node
- Ignore visual groupings (clusters) - treat each box as an independent node

## Step 2: Create Node Definitions
Use the simplest D2 syntax for maximum compatibility:

```
NodeName: Single line description combining all text
```

**Critical Rules:**
- Use single-line labels only (multi-line causes box malformation)
- Combine all text from a node into one line, separated by spaces
- Use simple, descriptive node names (no spaces, use camelCase or underscores)
- Do NOT use:
  - Nested containers `{}`
  - Markdown blocks `|md`
  - Shape definitions `shape: rectangle`
  - Explicit sizing `width/height`
  - Multi-line text with `\n`

## Step 3: Extract Connections
- Look for `<path>` elements in the `<g class="edgePaths">` section
- Follow the `id` attributes to match connections (e.g., `L_Menu_Configs_0` means Menu -> Configs)
- Create simple arrow connections: `NodeA -> NodeB`

## Step 4: Format the Output
Structure your D2 code as:
1. All node definitions first
2. A comment line `# Connections`  
3. All connections listed

## Example Conversion

**From SVG node:**
```svg
<foreignObject><span>F::Menu<br>ImGui Interface</span></foreignObject>
```

**To D2:**
```d2
Menu: F::Menu ImGui Interface
```

**From SVG connection path with id="L_Menu_Configs_0":**
```d2
Menu -> Configs
```

## Final Output Format
```d2
NodeName1: Description of first node
NodeName2: Description of second node
NodeName3: Description of third node

# Connections
NodeName1 -> NodeName2
NodeName1 -> NodeName3
NodeName2 -> NodeName3
```

Remember: Keep it simple. The most basic D2 syntax works best for ASCII rendering. Complex formatting breaks the box borders and causes text to escape.

Now convert this SVG flowchart to D2 syntax:"""
    
    def __init__(self, api_base_url: str = None, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize SVG to D2 converter.
        
        Args:
            api_base_url: OpenAI-compatible API base URL (e.g., http://localhost:1234/v1)
            api_key: API key (can be dummy for local APIs)
            model: Model name to use
        """
        self.api_base_url = api_base_url or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "dummy-key")
        self.model = model
        
        # Check if D2 is available
        self.d2_available = self._check_d2_available()
        if not self.d2_available:
            logger.warning("D2 is not available. SVG conversion will return D2 code only.")
    
    def _check_d2_available(self) -> bool:
        """Check if D2 command is available."""
        try:
            subprocess.run(["d2", "--version"], capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _call_llm_api(self, svg_content: str) -> Optional[str]:
        """Call the LLM API to convert SVG to D2."""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Log the request details (excluding full SVG content for brevity)
            svg_preview = svg_content[:200] + "..." if len(svg_content) > 200 else svg_content
            logger.debug(f"LLM API Request - URL: {self.api_base_url}/chat/completions")
            logger.debug(f"LLM API Request - Model: {self.model}")
            logger.debug(f"LLM API Request - SVG Content Preview: {svg_preview}")
            logger.debug(f"LLM API Request - SVG Content Length: {len(svg_content)} chars")
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{self.SVG_TO_D2_PROMPT}\n\n```svg\n{svg_content}\n```"
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            logger.debug(f"LLM API Request - Payload size: {len(json.dumps(payload))} chars")
            logger.info("Sending request to LLM API...")
            
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.debug(f"LLM API Response - Status Code: {response.status_code}")
            logger.debug(f"LLM API Response - Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Log response details
                response_content = result["choices"][0]["message"]["content"]
                logger.debug(f"LLM API Response - Content Length: {len(response_content)} chars")
                logger.debug(f"LLM API Response - Content Preview: {response_content[:300]}...")
                
                # Log token usage if available
                if "usage" in result:
                    usage = result["usage"]
                    logger.info(f"LLM API - Token Usage: input={usage.get('prompt_tokens', 'N/A')}, "
                              f"output={usage.get('completion_tokens', 'N/A')}, "
                              f"total={usage.get('total_tokens', 'N/A')}")
                
                logger.info("Successfully received response from LLM API")
                return response_content
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                logger.debug(f"Failed request payload keys: {list(payload.keys())}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            logger.debug(f"Exception type: {type(e).__name__}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def _extract_d2_code(self, llm_response: str) -> Optional[str]:
        """Extract D2 code from LLM response."""
        logger.debug("Starting D2 code extraction from LLM response")
        
        if not llm_response:
            logger.warning("LLM response is empty, cannot extract D2 code")
            return None
        
        logger.debug(f"LLM response length: {len(llm_response)} chars")
        logger.debug(f"LLM response preview (first 500 chars): {llm_response[:500]}")
        
        # Look for D2 code blocks
        d2_pattern = r'```(?:d2)?\n(.*?)\n```'
        matches = re.findall(d2_pattern, llm_response, re.DOTALL)
        
        logger.debug(f"Found {len(matches)} code block matches using pattern: {d2_pattern}")
        
        if matches:
            extracted_d2 = matches[0].strip()
            logger.debug(f"Extracted D2 code from first match (length: {len(extracted_d2)} chars):")
            logger.debug(f"D2 Code:\n{extracted_d2}")
            return extracted_d2
        
        logger.debug("No code blocks found, trying fallback extraction method")
        
        # If no code blocks, try to extract everything after a certain pattern
        lines = llm_response.split('\n')
        d2_lines = []
        in_d2 = False
        
        logger.debug(f"Processing {len(lines)} lines for D2 content")
        
        for i, line in enumerate(lines):
            if ':' in line and not line.startswith('#') and not line.startswith('**'):
                if not in_d2:
                    logger.debug(f"Found potential D2 content start at line {i}: {line}")
                in_d2 = True
            if in_d2:
                d2_lines.append(line)
                logger.debug(f"Added line {i} to D2 content: {line}")
        
        result = '\n'.join(d2_lines).strip() if d2_lines else None
        
        if result:
            logger.debug(f"Fallback extraction successful, extracted {len(d2_lines)} lines:")
            logger.debug(f"Extracted D2 Code:\n{result}")
        else:
            logger.warning("Fallback extraction failed, no D2 content found")
        
        return result
    
    def _d2_to_ascii(self, d2_content: str) -> Optional[str]:
        """Convert D2 content to ASCII using the D2 command."""
        logger.debug("Starting D2 to ASCII conversion")
        logger.debug(f"D2 content length: {len(d2_content)} chars")
        logger.debug(f"D2 available: {self.d2_available}")
        
        if not self.d2_available:
            logger.info("D2 command not available, skipping D2-to-ASCII conversion")
            return None
            
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as d2_file:
                d2_file.write(d2_content)
                d2_file_path = d2_file.name
            
            logger.debug(f"Created temporary D2 file: {d2_file_path}")
            
            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as svg_file:
                svg_file_path = svg_file.name
            
            logger.debug(f"Created temporary SVG file: {svg_file_path}")
            
            # Convert D2 to SVG first, then we could convert to ASCII
            # For now, let's use a simple ASCII art approach
            cmd = ["d2", "--sketch", d2_file_path, svg_file_path]
            logger.debug(f"Running D2 command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            logger.debug(f"D2 command return code: {result.returncode}")
            logger.debug(f"D2 command stdout: {result.stdout}")
            if result.stderr:
                logger.debug(f"D2 command stderr: {result.stderr}")
            
            if result.returncode == 0:
                logger.info("D2 command executed successfully")
                # For ASCII output, we'll return a simple text representation
                # In a real implementation, you might use SVG-to-ASCII conversion
                ascii_art = self._simple_d2_to_ascii(d2_content)
                logger.debug(f"Generated ASCII art length: {len(ascii_art)} chars")
                return ascii_art
            else:
                logger.error(f"D2 conversion failed with code {result.returncode}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("D2 command timed out after 30 seconds")
            return None
        except Exception as e:
            logger.error(f"Error converting D2 to ASCII: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return None
        finally:
            # Clean up temp files
            try:
                if 'd2_file_path' in locals():
                    logger.debug(f"Cleaning up temporary D2 file: {d2_file_path}")
                    os.unlink(d2_file_path)
                if 'svg_file_path' in locals():
                    logger.debug(f"Cleaning up temporary SVG file: {svg_file_path}")
                    os.unlink(svg_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Error cleaning up temporary files: {cleanup_error}")
    
    def _simple_d2_to_ascii(self, d2_content: str) -> str:
        """Simple D2 to ASCII conversion for basic diagrams."""
        logger.debug("Starting simple D2 to ASCII conversion")
        logger.debug(f"Input D2 content:\n{d2_content}")
        
        lines = d2_content.split('\n')
        nodes = {}
        connections = []
        
        logger.debug(f"Processing {len(lines)} lines from D2 content")
        
        for i, line in enumerate(lines):
            line = line.strip()
            logger.debug(f"Processing line {i}: '{line}'")
            
            if not line or line.startswith('#'):
                logger.debug(f"Skipping empty or comment line {i}")
                continue
                
            if '->' in line:
                # Connection
                parts = line.split('->')
                if len(parts) == 2:
                    connection = (parts[0].strip(), parts[1].strip())
                    connections.append(connection)
                    logger.debug(f"Found connection: {connection[0]} -> {connection[1]}")
                else:
                    logger.warning(f"Invalid connection format on line {i}: {line}")
            elif ':' in line:
                # Node definition
                parts = line.split(':', 1)
                if len(parts) == 2:
                    node_name = parts[0].strip()
                    node_desc = parts[1].strip()
                    nodes[node_name] = node_desc
                    logger.debug(f"Found node: '{node_name}' = '{node_desc}'")
                else:
                    logger.warning(f"Invalid node format on line {i}: {line}")
            else:
                logger.debug(f"Skipping unrecognized line format {i}: {line}")
        
        logger.debug(f"Parsed {len(nodes)} nodes and {len(connections)} connections")
        logger.debug(f"Nodes: {list(nodes.keys())}")
        logger.debug(f"Connections: {connections}")
        
        # Create simple ASCII representation
        ascii_lines = []
        ascii_lines.append("```")
        
        # Add nodes
        for node_name, node_desc in nodes.items():
            truncated_desc = node_desc[:20] + '...' if len(node_desc) > 20 else node_desc
            ascii_lines.append(f"┌─ {node_name} ─┐")
            ascii_lines.append(f"│ {truncated_desc} │")
            ascii_lines.append("└─────────┘")
            ascii_lines.append("    │")
            logger.debug(f"Added ASCII box for node: {node_name}")
        
        # Add connections
        if connections:
            ascii_lines.append("    ▼")
            for src, dest in connections:
                ascii_lines.append(f"{src} --> {dest}")
                logger.debug(f"Added ASCII connection: {src} --> {dest}")
        else:
            logger.debug("No connections to add")
        
        ascii_lines.append("```")
        
        result = '\n'.join(ascii_lines)
        logger.debug(f"Generated ASCII diagram:\n{result}")
        
        return result
    
    def convert_svg_to_ascii(self, svg_content: str) -> Dict[str, Any]:
        """
        Convert SVG flowchart to ASCII diagram.
        
        Args:
            svg_content: Raw SVG content
            
        Returns:
            Dictionary with conversion result:
            - success: bool
            - d2_code: str (D2 syntax)
            - ascii_diagram: str (ASCII representation)
            - error: str (if conversion failed)
        """
        logger.info("=== Starting SVG to ASCII conversion process ===")
        logger.debug(f"SVG content length: {len(svg_content)} chars")
        logger.debug(f"SVG content preview (first 200 chars): {svg_content[:200]}...")
        
        result = {
            'success': False,
            'd2_code': '',
            'ascii_diagram': '',
            'error': ''
        }
        
        try:
            # Step 1: Call LLM to convert SVG to D2
            logger.info("Step 1: Converting SVG to D2 using LLM...")
            llm_response = self._call_llm_api(svg_content)
            
            if not llm_response:
                error_msg = "Failed to get response from LLM API"
                logger.error(f"Step 1 FAILED: {error_msg}")
                result['error'] = error_msg
                return result
            
            logger.info("Step 1 SUCCESS: Received LLM response")
            
            # Step 2: Extract D2 code from LLM response
            logger.info("Step 2: Extracting D2 code from LLM response...")
            d2_code = self._extract_d2_code(llm_response)
            if not d2_code:
                error_msg = "Failed to extract D2 code from LLM response"
                logger.error(f"Step 2 FAILED: {error_msg}")
                logger.debug(f"LLM response was: {llm_response}")
                result['error'] = error_msg
                return result
            
            logger.info("Step 2 SUCCESS: Extracted D2 code")
            result['d2_code'] = d2_code
            
            # Step 3: Convert D2 to ASCII
            logger.info("Step 3: Converting D2 to ASCII diagram...")
            ascii_diagram = self._d2_to_ascii(d2_code)
            if ascii_diagram:
                logger.info("Step 3 SUCCESS: D2 conversion successful")
                result['ascii_diagram'] = ascii_diagram
                result['success'] = True
            else:
                logger.info("Step 3 FALLBACK: Using simple ASCII conversion")
                # Fallback to simple ASCII representation
                result['ascii_diagram'] = self._simple_d2_to_ascii(d2_code)
                result['success'] = True
                logger.info("Step 3 SUCCESS: Fallback ASCII conversion completed")
            
            logger.info("=== SVG to ASCII conversion completed successfully ===")
            logger.debug(f"Final ASCII diagram length: {len(result['ascii_diagram'])} chars")
            
        except Exception as e:
            error_msg = f"Error in SVG to ASCII conversion: {e}"
            logger.error(f"=== CONVERSION FAILED: {error_msg} ===")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            result['error'] = str(e)
        
        return result