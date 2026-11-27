#!/usr/bin/env python3
"""Helper tool to convert text descriptions to diagram sources (Mermaid/PlantUML)

and render them via Kroki.
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import zlib
from typing import Dict, List, Optional, Tuple

import requests


def sanitize_id(raw_id: str) -> str:
    """Sanitize identifier for diagram nodes."""
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", raw_id.strip())
    return cleaned if cleaned else "node"


def parse_connection_line(line: str) -> Optional[Tuple[str, str, str, str]]:
    """Parse a line representing a connection between two nodes.

    Supports formats like:
      Source -> Target: Label
      Source --> Target: Label
      Source -> Target
    Returns (source, target, arrow_type, label) or None.
    """
    match = re.match(
        r"^\s*([A-Za-z0-9_\-\s]+?)\s*(-->|->)\s*([A-Za-z0-9_\-\s]+?)(?:\s*:\s*(.+))?\s*$",
        line,
    )
    if match:
        src = match.group(1).strip()
        arrow = match.group(2).strip()
        tgt = match.group(3).strip()
        label = (match.group(4) or "").strip()
        return src, tgt, arrow, label
    return None


def text_to_mermaid(text: str, diagram_style: str = "flowchart") -> str:
    """Convert simple text descriptions into Mermaid diagram source.

    Supports 'flowchart' and 'sequence'.
    """
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    lines = [line for line in lines if not line.startswith(("#", "//"))]

    if diagram_style == "sequence":
        out = ["sequenceDiagram"]
        for line in lines:
            conn = parse_connection_line(line)
            if conn:
                src, tgt, arrow, label = conn
                arrow_sym = "->>" if arrow == "->" else "-->>"
                lbl_part = f": {label}" if label else ": "
                out.append(f"    {sanitize_id(src)}{arrow_sym}{sanitize_id(tgt)}{lbl_part}")
            else:
                out.append(f"    Note over all: {line}")
        return "\n".join(out)

    # Default: flowchart TD
    out = ["flowchart TD"]
    node_labels: Dict[str, str] = {}

    for line in lines:
        conn = parse_connection_line(line)
        if conn:
            src, tgt, arrow, label = conn
            src_id = sanitize_id(src)
            tgt_id = sanitize_id(tgt)
            node_labels.setdefault(src_id, src)
            node_labels.setdefault(tgt_id, tgt)
            if label:
                out.append(f"    {src_id}[\"{node_labels[src_id]}\"] -->|\"{label}\"| {tgt_id}[\"{node_labels[tgt_id]}\"]")
            else:
                out.append(f"    {src_id}[\"{node_labels[src_id]}\"] --> {tgt_id}[\"{node_labels[tgt_id]}\"]")
        else:
            # Single node declaration or note
            node_id = sanitize_id(line)
            out.append(f"    {node_id}[\"{line}\"]")

    return "\n".join(out)


def text_to_plantuml(text: str, diagram_style: str = "flowchart") -> str:
    """Convert simple text descriptions into PlantUML diagram source."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    lines = [line for line in lines if not line.startswith(("#", "//", "'"))]

    out = ["@startuml"]

    if diagram_style == "c4":
        out.append("!include <C4/C4_Container>")
        out.append("Person(user, \"User\", \"System User\")")
        for line in lines:
            conn = parse_connection_line(line)
            if conn:
                src, tgt, _, label = conn
                lbl = label if label else "interacts with"
                out.append(f"Rel({sanitize_id(src)}, {sanitize_id(tgt)}, \"{lbl}\")")
            else:
                comp_id = sanitize_id(line)
                out.append(f"Container({comp_id}, \"{line}\", \"Service\")")
    elif diagram_style == "sequence":
        for line in lines:
            conn = parse_connection_line(line)
            if conn:
                src, tgt, arrow, label = conn
                arrow_sym = "->" if arrow == "->" else "-->"
                lbl_part = f" : {label}" if label else ""
                out.append(f"{sanitize_id(src)} {arrow_sym} {sanitize_id(tgt)}{lbl_part}")
            else:
                out.append(f"note over {sanitize_id(line)}: {line}")
    else:  # flowchart / component
        for line in lines:
            conn = parse_connection_line(line)
            if conn:
                src, tgt, arrow, label = conn
                arrow_sym = "-->" if arrow == "-->" else "->"
                lbl_part = f" : {label}" if label else ""
                out.append(f"[{src}] {arrow_sym} [{tgt}]{lbl_part}")
            else:
                out.append(f"[{line}]")

    out.append("@enduml")
    return "\n".join(out)


def text_to_diagram(text: str, diagram_type: str = "mermaid", style: str = "flowchart") -> str:
    """Generate diagram code based on diagram type and style."""
    normalized_type = diagram_type.strip().lower()
    if normalized_type == "mermaid":
        return text_to_mermaid(text, diagram_style=style)
    elif normalized_type == "plantuml":
        return text_to_plantuml(text, diagram_style=style)
    else:
        raise ValueError(f"Unsupported diagram type '{diagram_type}'. Choose 'mermaid' or 'plantuml'.")


def encode_kroki_payload(diagram_source: str) -> str:
    """Encode diagram source using Deflate + URL-safe Base64 for Kroki GET requests."""
    compressed = zlib.compress(diagram_source.encode("utf-8"), level=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def build_kroki_url(
    diagram_source: str,
    diagram_type: str = "mermaid",
    output_format: str = "svg",
    base_url: str = "https://kroki.io",
) -> str:
    """Construct Kroki GET URL with compressed diagram payload."""
    encoded = encode_kroki_payload(diagram_source)
    return f"{base_url.rstrip('/')}/{diagram_type.lower()}/{output_format.lower()}/{encoded}"


def render_diagram(
    diagram_source: str,
    diagram_type: str = "mermaid",
    output_format: str = "svg",
    kroki_url: str = "https://kroki.io",
    timeout: int = 15,
    session: Optional[requests.Session] = None,
) -> bytes:
    """Render diagram source using Kroki HTTP POST API."""
    url = f"{kroki_url.rstrip('/')}/{diagram_type.lower()}/{output_format.lower()}"
    headers = {"Content-Type": "text/plain; charset=utf-8"}

    req_client = session or requests
    response = req_client.post(
        url,
        data=diagram_source.encode("utf-8"),
        headers=headers,
        timeout=timeout,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Kroki rendering failed with HTTP {response.status_code}: {response.text}"
        )

    return response.content


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Convert text descriptions into diagrams and render via Kroki.")
    parser.add_argument("description", nargs="?", help="Text description of the diagram")
    parser.add_argument("--type", choices=["mermaid", "plantuml"], default="mermaid", help="Diagram engine")
    parser.add_argument("--style", choices=["flowchart", "sequence", "c4"], default="flowchart", help="Diagram style")
    parser.add_argument("--format", default="svg", choices=["svg", "png", "pdf"], help="Output format")
    parser.add_argument("--kroki-url", default="https://kroki.io", help="Kroki server base URL")
    parser.add_argument("--source-only", action="store_true", help="Only output generated diagram source")
    parser.add_argument("--output", "-o", help="Output file path for rendered diagram")

    args = parser.parse_args(argv)

    raw_text = args.description
    if not raw_text:
        if not sys.stdin.isatty():
            raw_text = sys.stdin.read().strip()
        else:
            parser.error("Please provide diagram text description or pipe into stdin.")

    source = text_to_diagram(raw_text, diagram_type=args.type, style=args.style)

    if args.source_only:
        print(source)
        return 0

    rendered = render_diagram(
        diagram_source=source,
        diagram_type=args.type,
        output_format=args.format,
        kroki_url=args.kroki_url,
    )

    if args.output:
        mode = "wb" if isinstance(rendered, bytes) else "w"
        with open(args.output, mode) as f:
            f.write(rendered)
    else:
        sys.stdout.buffer.write(rendered)

    return 0


if __name__ == "__main__":
    sys.exit(main())
