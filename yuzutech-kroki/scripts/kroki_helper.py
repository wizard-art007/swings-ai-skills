import base64
import zlib
import requests

def text_to_mermaid(description: str) -> str:
    """Converts a short text description into a Mermaid flowchart syntax."""
    cleaned = description.strip()
    if not cleaned:
        return "graph TD\n    A[Empty Description]"
    
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    mermaid_lines = ["graph TD"]
    
    if len(lines) == 1:
        mermaid_lines.append(f'    A["{lines[0]}"]')
    else:
        for i, line in enumerate(lines):
            node_id_curr = f"N{i}"
            mermaid_lines.append(f'    {node_id_curr}["{line}"]')
            if i > 0:
                node_id_prev = f"N{i-1}"
                mermaid_lines.append(f"    {node_id_prev} --> {node_id_curr}")
                
    return "\n".join(mermaid_lines)

def generate_kroki_url(diagram_source: str, diagram_type: str = "mermaid", output_format: str = "svg") -> str:
    """Generates the URL-safe Base64 encoded Kroki GET URL."""
    compressed = zlib.compress(diagram_source.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return f"https://kroki.io/{diagram_type}/{output_format}/{encoded}"

def render_diagram(diagram_source: str, diagram_type: str = "mermaid", output_format: str = "svg", endpoint: str = "https://kroki.io") -> bytes:
    """Renders the diagram by sending a POST request to the Kroki instance."""
    url = f"{endpoint.rstrip('/')}/{diagram_type}/{output_format}"
    response = requests.post(
        url,
        data=diagram_source.encode("utf-8"),
        headers={"Content-Type": "text/plain"}
    )
    response.raise_for_status()
    return response.content
