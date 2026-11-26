import base64
import zlib
import requests

def text_to_diagram_source(description: str, diagram_type: str = "mermaid") -> str:
    """
    Turns a short text description into diagram source code (Mermaid or PlantUML).
    """
    desc = description.strip()
    if diagram_type.lower() == "plantuml":
        return f"@startuml\nactor User\nUser -> ( {desc} )\n@enduml"
    else:
        # Default to Mermaid flowchart
        safe_desc = desc.replace('"', '\\"')
        return f"graph TD;\n    A[User Request] -->|{safe_desc}| B(Yank Note Action);"

def encode_kroki(source: str) -> str:
    """
    Encodes diagram source for Kroki API (deflate + base64url).
    """
    compressed = zlib.compress(source.encode("utf-8"), 9)
    # Kroki uses raw deflate (sometimes omitting zlib header/checksum, but standard zlib works or standard base64url of zlib)
    # Standard Kroki compression: zlib.compress, then base64 url safe with padding stripped or kept
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return encoded

def render_diagram_url(source: str, diagram_type: str = "mermaid") -> str:
    """
    Generates the Kroki render URL for a given diagram source.
    """
    encoded = encode_kroki(source)
    return f"https://kroki.io/{diagram_type.lower()}/svg/{encoded}"

def fetch_diagram_svg(source: str, diagram_type: str = "mermaid", timeout: int = 10) -> str:
    """
    Fetches the rendered SVG from the public Kroki API.
    """
    url = render_diagram_url(source, diagram_type)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text
