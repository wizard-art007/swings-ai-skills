"""
diagram_helper.py: Technical diagram generator and Kroki renderer.

Generates Mermaid and PlantUML technical diagram specifications from
short text descriptions or predefined agent workflow patterns, with theme
support and Kroki rendering.
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import zlib
from typing import Any, Dict, List, Optional, Tuple

import requests

SUPPORTED_STYLES = [
    "modern",
    "blueprint",
    "dark",
    "minimal",
    "vibrant",
    "cyberpunk",
    "monochrome",
]

STYLE_THEMES: Dict[str, Dict[str, str]] = {
    "modern": {
        "primary": "#3B82F6",
        "secondary": "#60A5FA",
        "bg": "#F8FAFC",
        "text": "#1E293B",
        "border": "#CBD5E1",
        "accent": "#10B981",
    },
    "blueprint": {
        "primary": "#0284C7",
        "secondary": "#38BDF8",
        "bg": "#0B2545",
        "text": "#E0F2FE",
        "border": "#1E40AF",
        "accent": "#93C5FD",
    },
    "dark": {
        "primary": "#6366F1",
        "secondary": "#818CF8",
        "bg": "#0F172A",
        "text": "#E2E8F0",
        "border": "#334155",
        "accent": "#EC4899",
    },
    "minimal": {
        "primary": "#475569",
        "secondary": "#94A3B8",
        "bg": "#FFFFFF",
        "text": "#0F172A",
        "border": "#E2E8F0",
        "accent": "#64748B",
    },
    "vibrant": {
        "primary": "#8B5CF6",
        "secondary": "#F43F5E",
        "bg": "#FFFBEB",
        "text": "#1C1917",
        "border": "#FBBF24",
        "accent": "#10B981",
    },
    "cyberpunk": {
        "primary": "#00FFCC",
        "secondary": "#FF007F",
        "bg": "#120E24",
        "text": "#FDFDFD",
        "border": "#7928CA",
        "accent": "#FFE600",
    },
    "monochrome": {
        "primary": "#262626",
        "secondary": "#525252",
        "bg": "#FAFAFA",
        "text": "#171717",
        "border": "#A3A3A3",
        "accent": "#737373",
    },
}


def parse_text_description(text: str) -> Dict[str, Any]:
    """
    Parse a concise natural-language or arrow-based description into nodes and edges.

    Supports:
      - Line-by-line connections:
          Client -> API Gateway: HTTP GET
          API Gateway --> Auth Service: Validate Token
          A -> B -> C
      - Comments starting with '#'
    """
    edges: List[Dict[str, str]] = []
    nodes: Dict[str, Dict[str, str]] = {}

    def clean_id(name: str) -> str:
        cleaned = re.sub(r"[^\w\s-]", "", name.strip())
        return re.sub(r"\s+", "_", cleaned)

    lines = text.strip().splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        label = ""
        if ":" in line:
            parts = line.split(":", 1)
            line = parts[0].strip()
            label = parts[1].strip()

        arrow_match = re.split(r"\s*(-->|->|=>)\s*", line)
        if len(arrow_match) >= 3:
            sequence_nodes: List[str] = []
            for i in range(0, len(arrow_match), 2):
                token = arrow_match[i].strip()
                if token:
                    sequence_nodes.append(token)

            for i in range(len(sequence_nodes) - 1):
                src_label = sequence_nodes[i]
                dst_label = sequence_nodes[i + 1]
                src_id = clean_id(src_label)
                dst_id = clean_id(dst_label)

                nodes[src_id] = {"id": src_id, "label": src_label}
                nodes[dst_id] = {"id": dst_id, "label": dst_label}

                edge_label = label if i == len(sequence_nodes) - 2 else ""
                edges.append({
                    "from": src_id,
                    "to": dst_id,
                    "label": edge_label,
                })
        else:
            nid = clean_id(line)
            if nid:
                nodes[nid] = {"id": nid, "label": line}

    return {"nodes": list(nodes.values()), "edges": edges}


def build_pattern_spec(pattern: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate graph specifications for agent/AI workflow patterns.
    Supported patterns:
      - 'chain': Sequential pipeline
      - 'router': Router distributing inputs to specialized agents
      - 'orchestrator_workers': Orchestrator with parallel worker agents and aggregator
      - 'evaluator_optimizer': Iterative generator-evaluator feedback loop
    """
    params = params or {}
    pattern_normalized = pattern.lower().replace("-", "_").strip()

    if pattern_normalized == "chain":
        steps = params.get("steps") or ["Input", "Preprocess", "LLM_Agent", "Postprocess", "Output"]
        edges = []
        nodes = [{"id": f"step_{i}", "label": step} for i, step in enumerate(steps)]
        for i in range(len(nodes) - 1):
            edges.append({"from": nodes[i]["id"], "to": nodes[i + 1]["id"], "label": "next"})
        return {"nodes": nodes, "edges": edges, "title": "Sequential Agent Chain"}

    if pattern_normalized == "router":
        routes = params.get("routes") or ["Code_Agent", "Search_Agent", "Creative_Agent"]
        nodes = [
            {"id": "user_input", "label": "User Input"},
            {"id": "intent_router", "label": "Intent Router"},
            {"id": "response_synth", "label": "Response Synthesis"},
        ]
        edges = [
            {"from": "user_input", "to": "intent_router", "label": "prompt"},
        ]
        for idx, route in enumerate(routes):
            rid = f"worker_{idx}"
            nodes.append({"id": rid, "label": route})
            edges.append({"from": "intent_router", "to": rid, "label": f"classify: {route}"})
            edges.append({"from": rid, "to": "response_synth", "label": "result"})
        return {"nodes": nodes, "edges": edges, "title": "Router Agent Pattern"}

    if pattern_normalized in ("orchestrator_workers", "orchestrator"):
        workers = params.get("workers") or ["Worker_1", "Worker_2", "Worker_3"]
        nodes = [
            {"id": "task_input", "label": "Task Input"},
            {"id": "orchestrator", "label": "Orchestrator Agent"},
            {"id": "synthesizer", "label": "Synthesis & Reduce"},
            {"id": "final_output", "label": "Final Output"},
        ]
        edges = [
            {"from": "task_input", "to": "orchestrator", "label": "delegate"},
        ]
        for idx, worker in enumerate(workers):
            wid = f"worker_{idx}"
            nodes.append({"id": wid, "label": worker})
            edges.append({"from": "orchestrator", "to": wid, "label": f"subtask {idx + 1}"})
            edges.append({"from": wid, "to": "synthesizer", "label": "output"})
        edges.append({"from": "synthesizer", "to": "final_output", "label": "assembled"})
        return {"nodes": nodes, "edges": edges, "title": "Orchestrator-Workers Pattern"}

    if pattern_normalized in ("evaluator_optimizer", "evaluator"):
        nodes = [
            {"id": "goal", "label": "User Goal"},
            {"id": "generator", "label": "Generator LLM"},
            {"id": "evaluator", "label": "Evaluator / Critic"},
            {"id": "accepted", "label": "Accepted Solution"},
        ]
        edges = [
            {"from": "goal", "to": "generator", "label": "initial requirement"},
            {"from": "generator", "to": "evaluator", "label": "candidate draft"},
            {"from": "evaluator", "to": "generator", "label": "critique & revisions"},
            {"from": "evaluator", "to": "accepted", "label": "meets threshold"},
        ]
        return {"nodes": nodes, "edges": edges, "title": "Evaluator-Optimizer Loop"}

    raise ValueError(f"Unknown pattern '{pattern}'. Available: chain, router, orchestrator_workers, evaluator_optimizer")


def to_mermaid(
    graph_spec: Dict[str, Any],
    style: str = "modern",
    direction: str = "TD",
) -> str:
    """Generate Mermaid flowchart markup with applied theme styling."""
    theme_key = style if style in STYLE_THEMES else "modern"
    theme = STYLE_THEMES.get(theme_key, STYLE_THEMES["modern"])
    lines = [f"flowchart {direction}"]

    for node in graph_spec.get("nodes", []):
        nid = node["id"]
        label = node.get("label", nid)
        lines.append(f'    {nid}["{label}"]')

    for edge in graph_spec.get("edges", []):
        src = edge["from"]
        dst = edge["to"]
        label = edge.get("label")
        if label:
            lines.append(f'    {src} -->|"{label}"| {dst}')
        else:
            lines.append(f"    {src} --> {dst}")

    # Styling class definitions
    lines.append(
        f'    classDef default fill:{theme["bg"]},stroke:{theme["primary"]},stroke-width:2px,color:{theme["text"]};'
    )
    lines.append(
        f'    classDef accent fill:{theme["primary"]},stroke:{theme["accent"]},stroke-width:2px,color:#FFFFFF;'
    )

    return "\n".join(lines)


def to_plantuml(
    graph_spec: Dict[str, Any],
    style: str = "modern",
) -> str:
    """Generate PlantUML component/flow markup with styled skinparam settings."""
    theme = STYLE_THEMES.get(style, STYLE_THEMES["modern"])
    title = graph_spec.get("title", "Technical Architecture")

    lines = [
        "@startuml",
        f"title {title}",
        "skinparam monochrome false",
        "skinparam shadowing false",
        f"skinparam defaultFontColor {theme['text']}",
        f"skinparam backgroundColor {theme['bg']}",
        f"skinparam componentBackgroundColor {theme['bg']}",
        f"skinparam componentBorderColor {theme['primary']}",
        f"skinparam componentFontColor {theme['text']}",
        f"skinparam arrowColor {theme['secondary']}",
        f"skinparam arrowFontColor {theme['accent']}",
    ]

    for node in graph_spec.get("nodes", []):
        nid = node["id"]
        label = node.get("label", nid)
        lines.append(f'[{label}] as {nid}')

    for edge in graph_spec.get("edges", []):
        src = edge["from"]
        dst = edge["to"]
        label = edge.get("label")
        if label:
            lines.append(f'{src} --> {dst} : "{label}"')
        else:
            lines.append(f"{src} --> {dst}")

    lines.append("@enduml")
    return "\n".join(lines)


def encode_kroki_payload(source: str) -> str:
    """
    Encode diagram text using Kroki's URL-safe deflate + base64 algorithm.
    Used for Kroki GET requests.
    """
    compressed = zlib.compress(source.encode("utf-8"), 9)
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def get_kroki_url(
    source: str,
    diagram_type: str = "mermaid",
    output_format: str = "svg",
    base_url: str = "https://kroki.io",
) -> str:
    """Get the GET URL for a rendered diagram from Kroki."""
    encoded = encode_kroki_payload(source)
    return f"{base_url.rstrip('/')}/{diagram_type}/{output_format}/{encoded}"


def render_kroki(
    source: str,
    diagram_type: str = "mermaid",
    output_format: str = "svg",
    base_url: str = "https://kroki.io",
    timeout: int = 15,
    session: Optional[requests.Session] = None,
) -> bytes:
    """
    Render a diagram via Kroki POST API endpoint.
    Returns rendered image/vector bytes (e.g., SVG, PNG).
    """
    url = f"{base_url.rstrip('/')}/{diagram_type}/{output_format}"
    client = session or requests
    headers = {"Content-Type": "text/plain; charset=utf-8"}

    response = client.post(url, data=source.encode("utf-8"), headers=headers, timeout=timeout)
    if response.status_code != 200:
        raise RuntimeError(
            f"Kroki rendering failed with HTTP {response.status_code}: {response.text[:200]}"
        )
    return response.content


def generate_diagram(
    description: Optional[str] = None,
    pattern: Optional[str] = None,
    diagram_type: str = "mermaid",
    style: str = "modern",
    direction: str = "TD",
) -> str:
    """
    High-level entry point to convert a description or agent workflow pattern
    into diagram markup (Mermaid or PlantUML).
    """
    if style not in STYLE_THEMES:
        style = "modern"

    if pattern:
        spec = build_pattern_spec(pattern)
    elif description:
        spec = parse_text_description(description)
    else:
        raise ValueError("Either 'description' or 'pattern' must be provided.")

    if diagram_type.lower() == "mermaid":
        return to_mermaid(spec, style=style, direction=direction)
    elif diagram_type.lower() in ("plantuml", "puml"):
        return to_plantuml(spec, style=style)
    else:
        raise ValueError(f"Unsupported diagram_type: '{diagram_type}'. Choose 'mermaid' or 'plantuml'.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert short descriptions or AI agent patterns into Mermaid/PlantUML and render via Kroki."
    )
    parser.add_argument("--text", "-t", type=str, help="Natural language or arrow-based description")
    parser.add_argument(
        "--pattern",
        "-p",
        choices=["chain", "router", "orchestrator_workers", "evaluator_optimizer"],
        help="Predefined AI/Agent workflow pattern",
    )
    parser.add_argument(
        "--type",
        choices=["mermaid", "plantuml"],
        default="mermaid",
        help="Target diagram syntax (default: mermaid)",
    )
    parser.add_argument(
        "--style",
        choices=SUPPORTED_STYLES,
        default="modern",
        help="Visual style/theme (default: modern)",
    )
    parser.add_argument(
        "--render",
        choices=["svg", "png"],
        help="Render diagram via Kroki to this format",
    )
    parser.add_argument("--output", "-o", help="Output file path to save source or rendered image")
    parser.add_argument(
        "--kroki-url",
        default="https://kroki.io",
        help="Kroki server base URL",
    )

    args = parser.parse_args()

    if not args.text and not args.pattern:
        parser.error("Either --text or --pattern must be specified.")

    source = generate_diagram(
        description=args.text,
        pattern=args.pattern,
        diagram_type=args.type,
        style=args.style,
    )

    if args.render:
        rendered_bytes = render_kroki(
            source=source,
            diagram_type=args.type,
            output_format=args.render,
            base_url=args.kroki_url,
        )
        if args.output:
            with open(args.output, "wb") as f:
                f.write(rendered_bytes)
            print(f"Rendered {args.render.upper()} written to {args.output}")
        else:
            sys.stdout.buffer.write(rendered_bytes)
    else:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(source)
            print(f"Diagram source written to {args.output}")
        else:
            print(source)

    return 0


if __name__ == "__main__":
    sys.exit(main())
