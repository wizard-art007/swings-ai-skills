"""
Archify Helper: Convert text descriptions into Mermaid / PlantUML diagram source code
and render via Kroki without network dependency during unit testing.
"""

import base64
import zlib
import requests
from typing import List


def parse_text_lines(text: str) -> List[str]:
    """Extract non-empty lines from description text, ignoring comments."""
    if not text:
        return []
    lines = []
    for line in text.strip().splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            lines.append(cleaned)
    return lines


def text_to_mermaid(description: str, kind: str = "flowchart") -> str:
    """Convert text description into a Mermaid diagram source string."""
    lines = parse_text_lines(description)
    kind_lower = kind.lower()

    if not lines:
        return "graph TD\n    A[Empty Diagram]"

    if kind_lower in ("flowchart", "flow", "graph"):
        res = ["graph TD"]
        for idx, line in enumerate(lines):
            if "->" in line or "-->" in line:
                res.append(f"    {line}")
            else:
                parts = [p.strip() for p in line.split(":", 1)]
                if len(parts) == 2:
                    res.append(f"    {parts[0]} -->|{parts[1]}| {parts[1]}_node")
                elif idx < len(lines) - 1:
                    res.append(f"    N{idx}[\"{line}\"] --> N{idx+1}")
                else:
                    res.append(f"    N{idx}[\"{line}\"]")
        return "\n".join(res)

    elif kind_lower == "sequence":
        res = ["sequenceDiagram"]
        for line in lines:
            if "->" in line or "-->" in line:
                res.append(f"    {line}")
            elif ":" in line:
                parts = [p.strip() for p in line.split(":", 1)]
                res.append(f"    {parts[0]}->>{parts[1]}: message")
            else:
                res.append(f"    Note over System: {line}")
        return "\n".join(res)

    else:
        res = [f"{kind}"]
        for line in lines:
            res.append(f"    {line}")
        return "\n".join(res)


def text_to_plantuml(description: str, kind: str = "sequence") -> str:
    """Convert text description into a PlantUML diagram source string."""
    lines = parse_text_lines(description)
    puml = ["@startuml"]

    if not lines:
        puml.append("note over System: Empty Diagram")
    elif kind.lower() in ("sequence", "seq"):
        puml.append("autonumber")
        for line in lines:
            if "->" in line or "-->" in line:
                puml.append(f"{line}")
            elif ":" in line:
                parts = [p.strip() for p in line.split(":", 1)]
                puml.append(f"{parts[0]} -> {parts[1]}")
            else:
                puml.append(f"note over System: {line}")
    else:
        for line in lines:
            puml.append(f"{line}")

    puml.append("@enduml")
    return "\n".join(puml)


def generate_diagram(description: str, engine: str = "mermaid", kind: str = "flowchart") -> str:
    """Generate diagram source using requested engine ('mermaid' or 'plantuml')."""
    if engine.lower() == "plantuml":
        return text_to_plantuml(description, kind=kind)
    return text_to_mermaid(description, kind=kind)


def encode_kroki_url(
    diagram_source: str,
    diagram_type: str = "mermaid",
    output_format: str = "svg",
    kroki_base_url: str = "https://kroki.io",
) -> str:
    """Encode diagram source into a GET-compatible Kroki URL."""
    compressed = zlib.compress(diagram_source.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    base = kroki_base_url.rstrip("/")
    return f"{base}/{diagram_type}/{output_format}/{encoded}"


def render_kroki(
    diagram_source: str,
    diagram_type: str = "mermaid",
    output_format: str = "svg",
    kroki_base_url: str = "https://kroki.io",
    timeout: float = 10.0,
) -> bytes:
    """Render diagram source using Kroki API via POST request."""
    base = kroki_base_url.rstrip("/")
    url = f"{base}/{diagram_type}/{output_format}"
    headers = {"Content-Type": "text/plain; charset=utf-8"}
    resp = requests.post(
        url,
        data=diagram_source.encode("utf-8"),
        headers=headers,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.content
