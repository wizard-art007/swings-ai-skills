import zlib
import base64
import requests
import json

def text_to_mermaid(description: str) -> str:
    """Converts a high-level description to Mermaid source."""
    # This is a placeholder logic. In a real-world scenario, 
    # one might use an LLM call here, but for this tool,
    # we return a standard flow structure based on input.
    if "sequence" in description.lower():
        return "sequenceDiagram\n    Alice->>John: Hello John, how are you?\n    John-->>Alice: Great!"
    return f"graph TD\n    A[Start] --> B[{description}]\n    B --> C[End]"

def get_kroki_url(diagram_source: str, diagram_type: str = "mermaid") -> str:
    """Generates a Kroki URL using the deflate+base64 encoding."""
    data = diagram_source.encode("utf-8")
    compressed = zlib.compress(data, 9)
    # Kroki expects raw deflate (no zlib headers), 
    # so we slice off the 2-byte header and 4-byte trailer.
    encoded = base64.urlsafe_b64encode(compressed[2:-4]).decode("utf-8")
    return f"https://kroki.io/{diagram_type}/svg/{encoded}"

def fetch_diagram(url: str) -> str:
    """Fetches the rendered SVG from Kroki."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text
