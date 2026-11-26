import base64
import json
import zlib
import requests

def text_to_mermaid(description: str) -> str:
    """Convert a short text description into a Mermaid diagram source."""
    lines = [line.strip() for line in description.split("\n") if line.strip()]
    if not lines:
        return "graph TD\n    Start([Start]) --> End([End])"
    
    mermaid_lines = ["graph TD"]
    # Add a title node
    first_line = lines[0].replace('"', '\\"')
    mermaid_lines.append(f'    Title["{first_line}"]')
    
    prev_node = "Title"
    for i, line in enumerate(lines[1:], start=1):
        clean_line = line.replace('"', '\\"')
        node_id = f"Step{i}"
        mermaid_lines.append(f'    {node_id}["{clean_line}"]')
        mermaid_lines.append(f'    {prev_node} --> {node_id}')
        prev_node = node_id
        
    return "\n".join(mermaid_lines)

def render_diagram_kroki(diagram_source: str, diagram_type: str = "mermaid", format_type: str = "svg") -> str:
    """Render a diagram source using the Kroki API."""
    data = diagram_source.encode("utf-8")
    compressed = zlib.compress(data, 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    
    url = f"https://kroki.io/{diagram_type}/{format_type}/{encoded}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text
