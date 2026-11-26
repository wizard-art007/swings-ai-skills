import base64
import zlib
import requests

def generate_mermaid_source(description: str) -> str:
    """Generates a Mermaid diagram source string from a short text description."""
    cleaned = description.strip()
    return f"graph TD\n    A[Description] --> B[\"{cleaned}\"]"

def generate_plantuml_source(description: str) -> str:
    """Generates a PlantUML diagram source string from a short text description."""
    cleaned = description.strip()
    return f"@startuml\nskinparam monochrome true\n[Description] --> [{cleaned}]\n@enduml"

def _encode_plantuml(source: str) -> str:
    """Encodes PlantUML source for use with the Kroki API (deflate + base64url)."""
    compressed = zlib.compress(source.encode('utf-8'))[2:-4]
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    return encoded

def get_kroki_url(diagram_type: str, source: str, format_type: str = "svg") -> str:
    """Constructs the Kroki API URL for rendering the diagram."""
    if diagram_type.lower() == "plantuml":
        encoded = _encode_plantuml(source)
        return f"https://kroki.io/{diagram_type.lower()}/{format_type}/{encoded}"
    elif diagram_type.lower() == "mermaid":
        encoded = base64.urlsafe_b64encode(source.encode('utf-8')).decode('ascii')
        return f"https://kroki.io/{diagram_type.lower()}/{format_type}/{encoded}"
    else:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")

def render_diagram(diagram_type: str, description: str, format_type: str = "svg", timeout: int = 10) -> str:
    """Fetches the rendered diagram from Kroki given a description and diagram type."""
    if diagram_type.lower() == "mermaid":
        source = generate_mermaid_source(description)
    elif diagram_type.lower() == "plantuml":
        source = generate_plantuml_source(description)
    else:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")

    url = get_kroki_url(diagram_type, source, format_type)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text
