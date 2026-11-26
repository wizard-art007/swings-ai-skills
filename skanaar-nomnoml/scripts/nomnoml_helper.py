"""nomnoml_helper.py

A tool to generate nomnoml UML diagram syntax from short text descriptions
and render or encode them using Kroki.
"""

import base64
import re
import sys
import zlib
from typing import Any, Dict, List, Optional
import requests

KROKI_DEFAULT_URL = "https://kroki.io"

# Supported relationship arrows sorted by length (descending) to avoid partial matches
NOMNOML_ARROWS = [
    "<:--",
    "--:>",
    "<:-",
    "-:>",
    "<-->",
    "-->",
    "<--",
    "+->",
    "<-+",
    "o->",
    "<-o",
    "<->",
    "->",
    "<-",
    "+-",
    "-+",
    "o-",
    "-o",
    "--",
    "-",
]

KEYWORD_RELATIONS = [
    (re.compile(r"\binherits\b", re.IGNORECASE), "-:>"),
    (re.compile(r"\bextends\b", re.IGNORECASE), "-:>"),
    (re.compile(r"\bimplements\b", re.IGNORECASE), "--:>"),
    (re.compile(r"\bcontains\b", re.IGNORECASE), "+->"),
    (re.compile(r"\bcomposes\b", re.IGNORECASE), "+->"),
    (re.compile(r"\baggregates\b", re.IGNORECASE), "o->"),
    (re.compile(r"\bhas\b", re.IGNORECASE), "o->"),
    (re.compile(r"\buses\b", re.IGNORECASE), "->"),
    (re.compile(r"\bcalls\b", re.IGNORECASE), "->"),
    (re.compile(r"\bsends to\b", re.IGNORECASE), "->"),
    (re.compile(r"\brelates to\b", re.IGNORECASE), "-"),
    (re.compile(r"\bconnects to\b", re.IGNORECASE), "-"),
]

STEREOTYPES = {
    "actor",
    "usecase",
    "database",
    "start",
    "end",
    "state",
    "choice",
    "package",
    "note",
    "frame",
    "label",
    "instance",
    "class",
    "table",
    "view",
    "pipe",
}


def _ensure_bracketed(node_str: str) -> str:
    """Wraps node in square brackets if not already wrapped."""
    s = node_str.strip()
    if s.startswith("[") and s.endswith("]"):
        return s
    return f"[{s}]"


def _format_node(name: str, stereotype: Optional[str] = None, parts: Optional[List[str]] = None) -> str:
    """Formats a node with optional stereotype and compartment sections."""
    clean_name = name.strip()
    if stereotype:
        st = stereotype.strip().strip("<>")
        if st.lower() != "class":
            clean_name = f"<{st}> {clean_name}"
    
    if parts:
        combined = "|".join([clean_name] + [p.strip() for p in parts if p.strip()])
        return f"[{combined}]"
    return f"[{clean_name}]"


def parse_text_description(
    text: str,
    title: Optional[str] = None,
    direction: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """Converts a short text description into nomnoml syntax.

    Accepts shorthand descriptions, keyword statements, or raw nomnoml fragments.
    """
    output_lines: List[str] = []

    # Directives
    if title:
        output_lines.append(f"#title: {title}")
    if direction:
        output_lines.append(f"#direction: {direction}")
    if config:
        for k, v in config.items():
            output_lines.append(f"#{k}: {v}")

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    # Arrow pattern matching (escaped regex)
    arrow_pattern = "|".join(re.escape(arr) for arr in NOMNOML_ARROWS)
    # Match: (left)(label?)(arrow)(label?)(right)
    # e.g., A -> B or [A] - label -> [B]
    rel_regex = re.compile(rf"^(.*?)\s+({arrow_pattern})\s+(.*)$")

    for line in lines:
        # Ignore comments and direct directives
        if line.startswith("#") or line.startswith("//"):
            output_lines.append(line)
            continue

        # If line is already fully formed nomnoml relation or box, keep as-is if bracketed
        if line.startswith("[") and line.endswith("]"):
            output_lines.append(line)
            continue

        # Check for keyword relations (e.g. "Admin inherits User")
        matched_kw = False
        for kw_pattern, arrow in KEYWORD_RELATIONS:
            m = kw_pattern.search(line)
            if m:
                left = line[: m.start()].strip()
                right = line[m.end() :].strip()
                output_lines.append(f"{_ensure_bracketed(left)} {arrow} {_ensure_bracketed(right)}")
                matched_kw = True
                break
        if matched_kw:
            continue

        # Check for explicit arrow relation (e.g. "User <:- Customer" or "A -> B")
        m_arrow = rel_regex.match(line)
        if m_arrow:
            left_side = m_arrow.group(1).strip()
            arrow = m_arrow.group(2).strip()
            right_side = m_arrow.group(3).strip()
            output_lines.append(f"{_ensure_bracketed(left_side)} {arrow} {_ensure_bracketed(right_side)}")
            continue

        # Check for stereotype shorthand (e.g. "Admin: actor" or "Customer: <actor>")
        if ":" in line and not line.startswith("["):
            parts = line.split(":", 1)
            name = parts[0].strip()
            kind = parts[1].strip().lower().strip("<>")
            if kind in STEREOTYPES or kind.startswith("<") or kind.endswith(">"):
                output_lines.append(_format_node(name, stereotype=kind))
                continue

        # Check for class with attributes / methods: "User | id: int; name: string | login()"
        if "|" in line:
            compartments = line.split("|")
            output_lines.append(_format_node(compartments[0], parts=compartments[1:]))
            continue

        # Default fallback: wrap as node
        output_lines.append(_ensure_bracketed(line))

    return "\n".join(output_lines) + "\n"


def get_kroki_url(diagram_code: str, output_format: str = "svg", server_url: str = KROKI_DEFAULT_URL) -> str:
    """Generates the Kroki GET URL for a given nomnoml diagram."""
    compressed = zlib.compress(diagram_code.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    base = server_url.rstrip("/")
    return f"{base}/nomnoml/{output_format}/{encoded}"


def render_nomnoml(
    diagram_code: str,
    output_format: str = "svg",
    server_url: str = KROKI_DEFAULT_URL,
    timeout: int = 15,
) -> bytes:
    """Renders nomnoml source code via Kroki HTTP POST API."""
    url = f"{server_url.rstrip('/')}/nomnoml/{output_format}"
    response = requests.post(
        url,
        data=diagram_code.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.content


def main() -> None:
    """CLI entrypoint."""
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python nomnoml_helper.py [INPUT_TEXT_OR_FILE]")
        sys.exit(0)

    input_text = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1], "r", encoding="utf-8").read()
    nomnoml_code = parse_text_description(input_text)
    print(nomnoml_code)


if __name__ == "__main__":
    main()
