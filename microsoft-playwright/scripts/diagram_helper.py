import base64
import json
import zlib
import requests


def text_to_mermaid(description: str) -> str:
    """Converts a short text description into a Mermaid diagram source.

    Designed for Playwright-related workflows and architectures.
    """
    clean_desc = description.strip()
    if not clean_desc:
        return "graph TD\n    Start([Start]) --> End([End])"

    # Generate a sensible structured Mermaid diagram based on keywords or general flow
    lines = ["graph TD", "    classDef default fill:#f9f,stroke:#333,stroke-width:2px;"]
    
    # Simple heuristic to extract steps or build a flowchart
    steps = [s.strip() for s in clean_desc.split("->") if s.strip()]
    if len(steps) > 1:
        node_ids = []
        for i, step in enumerate(steps):
            node_id = f"Step{i+1}"
            node_ids.append(node_id)
            lines.append(f'    {node_id}["{step}"]')
        for i in range(len(node_ids) - 1):
            lines.append(f"    {node_ids[i]} --> {node_ids[i+1]}")
    else:
        # Fallback keyword-based breakdown or generic structured flow
        lines.append(f'    Input["User Input: {clean_desc}"]')
        lines.append('    Playwright["Playwright Automation / Test Runner"]')
        lines.append('    Browsers["Chromium / Firefox / WebKit"]')
        lines.append('    Results["Test Results / Artifacts"]')
        lines.append('    Input --> Playwright')
        lines.append('    Playwright --> Browsers')
        lines.append('    Browsers --> Results')

    return "\n".join(lines)


def get_kroki_url(diagram_source: str, diagram_type: str = "mermaid", format: str = "svg") -> str:
    """Generates the Kroki render URL for the given diagram source."""
    compressed = zlib.compress(diagram_source.encode("utf-8"), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return f"https://kroki.io/{diagram_type}/{format}/{encoded}"


def render_via_kroki(diagram_source: str, diagram_type: str = "mermaid", format: str = "svg", timeout: int = 10) -> str:
    """Renders a diagram via the public Kroki API and returns the response content (e.g., SVG markup)."""
    url = f"https://kroki.io/{diagram_type}/{format}"
    payload = {"diagram_source": diagram_source}
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.text
