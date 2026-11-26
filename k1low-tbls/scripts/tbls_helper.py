"""
tbls_helper.py

A helper tool for k1low-tbls that generates ER diagram source text (Mermaid or PlantUML)
from short text descriptions and renders them via the Kroki API.
"""

import json
import zlib
import requests


def generate_mermaid_er(tables: list[dict]) -> str:
    """Generates a Mermaid ER diagram string from a list of table definitions.

    Each table is expected to be a dict with 'name' and 'columns' (list of dicts with 'name' and 'type').
    """
    lines = ["erDiagram"]
    for t in tables:
        t_name = t.get("name", "table")
        lines.append(f"    {t_name} {{")
        for col in t.get("columns", []):
            c_type = col.get("type", "string")
            c_name = col.get("name", "id")
            lines.append(f"        {c_type} {c_name}")
        lines.append("    }")

        for rel in t.get("relations", []):
            parent = rel.get("parent")
            cardinality = rel.get("cardinality", "||--o{")
            label = rel.get("label", "contains")
            if parent:
                lines.append(f"    {parent} {cardinality} {t_name} : {label}")

    return "\n".join(lines)


def generate_plantuml_er(tables: list[dict]) -> str:
    """Generates a PlantUML ER diagram string from a list of table definitions."""
    lines = ["@startuml", "hide methods", "skinparam linetype ortho"]
    for t in tables:
        t_name = t.get("name", "table")
        lines.append(f"entity \"{t_name}\" {{")
        for col in t.get("columns", []):
            c_type = col.get("type", "varchar")
            c_name = col.get("name", "id")
            pk = " * " if col.get("primary_key") else "   "
            lines.append(f"  {c_type}{pk}{c_name}")
        lines.append("}")

        for rel in t.get("relations", []):
            parent = rel.get("parent")
            if parent:
                lines.append(f"{parent} ||--o{{ {t_name}")

    lines.append("@enduml")
    return "\n".join(lines)


def render_via_kroki(
    diagram_source: str, diagram_type: str = "mermaid", format_type: str = "svg"
) -> str:
    """Encodes diagram source and sends it to the Kroki API, returning the rendered content/URL.

    Uses zlib compression + raw URL-safe base64 encoding as required by Kroki.
    """
    compressed = zlib.compress(diagram_source.encode("utf-8"), level=9)
    # URL-safe base64 encoding without padding '='
    import base64

    encoded = (
        base64.urlsafe_b64encode(compressed).rstrip(b"=").decode("ascii")
    )
    url = f"https://kroki.io/{diagram_type}/{format_type}/{encoded}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text
