import base64
import json
import zlib
import requests

def text_to_diagram(description: str, diagram_type: str = "sequence") -> str:
    """
    Converts a short text description into a Mermaid diagram source string
    compatible with OpenHeart diagram conventions.
    """
    clean_desc = description.strip()
    if not clean_desc:
        clean_desc = "No description provided"

    if diagram_type.lower() == "class":
        lines = [
            "classDiagram",
            "    class OpenHeartAnalyzer {",
            f"        +String description",
            f"        +analyze()",
            "    }",
            f"    note for OpenHeartAnalyzer \"{clean_desc}\""
        ]
    else:
        lines = [
            "sequenceDiagram",
            "    autonumber",
            "    participant Client",
            "    participant OpenHeart",
            "    Client->>OpenHeart: analyze(description)",
            f"    Note over OpenHeart: {clean_desc}",
            "    OpenHeart-->>Client: Return diagrams / SCPG"
        ]
    return "\n".join(lines)

def encode_mermaid_for_kroki(mermaid_code: str) -> str:
    """
    Encodes mermaid diagram source code for Kroki API using deflate and base64.
    """
    compressed = zlib.compress(mermaid_code.encode("utf-8"), level=9)
    # Kroki uses URL-safe base64 without padding
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return encoded.rstrip("=")

def get_kroki_url(mermaid_code: str, format_type: str = "svg", server_url: str = "https://kroki.io") -> str:
    """
    Generates the Kroki URL for rendering a Mermaid diagram.
    """
    encoded = encode_mermaid_for_kroki(mermaid_code)
    return f"{server_url}/mermaid/{format_type}/{encoded}"

def render_diagram_remotely(mermaid_code: str, server_url: str = "https://kroki.io", timeout: int = 10) -> str:
    """
    Sends the mermaid code to the Kroki API and returns the rendered content (e.g. SVG).
    """
    encoded = encode_mermaid_for_kroki(mermaid_code)
    url = f"{server_url}/mermaid/svg/{encoded}"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text
