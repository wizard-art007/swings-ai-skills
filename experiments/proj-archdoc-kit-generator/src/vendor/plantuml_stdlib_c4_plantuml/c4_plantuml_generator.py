"""
C4-PlantUML Generator and Kroki Renderer

A helper module to convert short text descriptions or specifications into
C4-PlantUML architecture diagram source code and render them via Kroki.
"""

import argparse
import base64
import sys
import zlib
from typing import Any, Dict, Optional, Union

import requests

C4_INCLUDES = {
    "context": "C4_Context.puml",
    "container": "C4_Container.puml",
    "component": "C4_Component.puml",
    "deployment": "C4_Deployment.puml",
}

ELEMENT_KIND_MAP = {
    "person": "Person",
    "person_ext": "Person_Ext",
    "system": "System",
    "system_ext": "System_Ext",
    "container": "Container",
    "container_db": "ContainerDb",
    "container_ext": "Container_Ext",
    "component": "Component",
    "component_db": "ComponentDb",
    "component_ext": "Component_Ext",
}

RELATION_KIND_MAP = {
    "rel": "Rel",
    "relation": "Rel",
    "rel_r": "Rel_R",
    "rel_l": "Rel_L",
    "rel_u": "Rel_U",
    "rel_d": "Rel_D",
}


def text_to_spec(text: str) -> Dict[str, Any]:
    """
    Parse a textual description into a structured C4 architecture specification.

    Supported directive lines:
      title: <Diagram Title>
      type: context | container | component | deployment
      remote_include: true | false
      person: alias, Label, Description
      person_ext: alias, Label, Description
      system: alias, Label, Description
      system_ext: alias, Label, Description
      container: alias, Label, Technology, Description
      container_db: alias, Label, Technology, Description
      component: alias, Label, Technology, Description
      rel: from_alias, to_alias, Label, Technology
      alias1 -> alias2: Label (Technology)
    """
    lines = [
        line.strip()
        for line in text.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    spec: Dict[str, Any] = {
        "title": "C4 Architecture Diagram",
        "type": "context",
        "remote_include": False,
        "elements": [],
        "relations": [],
        "raw_lines": [],
    }

    for line in lines:
        if ":" in line and not line.startswith("!") and "->" not in line.split(":")[0]:
            parts = [p.strip() for p in line.split(":", 1)]
            key = parts[0].lower()
            val = parts[1]

            if key == "title":
                spec["title"] = val
                continue
            elif key in ("type", "diagram_type"):
                spec["type"] = val.lower()
                continue
            elif key in ("remote_include", "use_remote"):
                spec["remote_include"] = val.lower() in ("true", "1", "yes")
                continue

            sub_parts = [p.strip() for p in val.split(",")]
            if key in ("person", "person_ext", "system", "system_ext"):
                alias = sub_parts[0]
                label = sub_parts[1] if len(sub_parts) > 1 else alias
                desc = sub_parts[2] if len(sub_parts) > 2 else ""
                spec["elements"].append(
                    {"kind": key, "alias": alias, "label": label, "desc": desc}
                )
                continue
            elif key in (
                "container",
                "container_db",
                "container_ext",
                "component",
                "component_db",
                "component_ext",
            ):
                alias = sub_parts[0]
                label = sub_parts[1] if len(sub_parts) > 1 else alias
                tech = sub_parts[2] if len(sub_parts) > 2 else ""
                desc = sub_parts[3] if len(sub_parts) > 3 else ""
                spec["elements"].append(
                    {
                        "kind": key,
                        "alias": alias,
                        "label": label,
                        "tech": tech,
                        "desc": desc,
                    }
                )
                continue
            elif key in ("rel", "relation", "rel_r", "rel_l", "rel_u", "rel_d"):
                if len(sub_parts) >= 2:
                    from_node = sub_parts[0]
                    to_node = sub_parts[1]
                    label = sub_parts[2] if len(sub_parts) > 2 else ""
                    tech = sub_parts[3] if len(sub_parts) > 3 else ""
                    spec["relations"].append(
                        {
                            "kind": key,
                            "from": from_node,
                            "to": to_node,
                            "label": label,
                            "tech": tech,
                        }
                    )
                    continue

        if "->" in line:
            parts = line.split("->", 1)
            from_node = parts[0].strip()
            rest = parts[1].strip()
            if ":" in rest:
                to_node, label_part = [p.strip() for p in rest.split(":", 1)]
                tech = ""
                if "(" in label_part and label_part.endswith(")"):
                    lbl, tech_part = label_part.rsplit("(", 1)
                    label_part = lbl.strip()
                    tech = tech_part[:-1].strip()
                spec["relations"].append(
                    {
                        "kind": "rel",
                        "from": from_node,
                        "to": to_node,
                        "label": label_part,
                        "tech": tech,
                    }
                )
                continue
            else:
                to_node = rest
                spec["relations"].append(
                    {
                        "kind": "rel",
                        "from": from_node,
                        "to": to_node,
                        "label": "",
                        "tech": "",
                    }
                )
                continue

        spec["raw_lines"].append(line)

    return spec


def generate_plantuml(input_data: Union[str, Dict[str, Any]]) -> str:
    """
    Generate C4-PlantUML diagram source code from text or structured specification.
    """
    if isinstance(input_data, str):
        spec = text_to_spec(input_data)
    elif isinstance(input_data, dict):
        spec = input_data
    else:
        raise ValueError("Input must be a string description or dictionary specification.")

    diag_type = spec.get("type", "context").lower()
    include_file = C4_INCLUDES.get(diag_type, "C4_Context.puml")

    if spec.get("remote_include", False):
        include_line = (
            f"!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/{include_file}"
        )
    else:
        include_name = include_file.replace(".puml", "")
        include_line = f"!include <C4/{include_name}>"

    lines = ["@startuml", include_line, ""]

    title = spec.get("title")
    if title:
        lines.append(f"title {title}")
        lines.append("")

    lines.append("LAYOUT_WITH_LEGEND()")
    lines.append("")

    for elem in spec.get("elements", []):
        kind = elem.get("kind", "").lower()
        macro_name = ELEMENT_KIND_MAP.get(kind, "System")
        alias = elem.get("alias", "")
        label = elem.get("label", alias)
        tech = elem.get("tech", "")
        desc = elem.get("desc", "")

        if kind in ("person", "person_ext", "system", "system_ext"):
            if desc:
                lines.append(f'{macro_name}({alias}, "{label}", "{desc}")')
            else:
                lines.append(f'{macro_name}({alias}, "{label}")')
        else:
            if desc:
                lines.append(f'{macro_name}({alias}, "{label}", "{tech}", "{desc}")')
            elif tech:
                lines.append(f'{macro_name}({alias}, "{label}", "{tech}")')
            else:
                lines.append(f'{macro_name}({alias}, "{label}")')

    if spec.get("elements"):
        lines.append("")

    for rel in spec.get("relations", []):
        kind = rel.get("kind", "rel").lower()
        macro_name = RELATION_KIND_MAP.get(kind, "Rel")
        from_node = rel.get("from", "")
        to_node = rel.get("to", "")
        label = rel.get("label", "")
        tech = rel.get("tech", "")

        if tech:
            lines.append(f'{macro_name}({from_node}, {to_node}, "{label}", "{tech}")')
        elif label:
            lines.append(f'{macro_name}({from_node}, {to_node}, "{label}")')
        else:
            lines.append(f'{macro_name}({from_node}, {to_node})')

    if spec.get("raw_lines"):
        lines.append("")
        for raw in spec["raw_lines"]:
            lines.append(raw)

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)


def encode_kroki_url(
    plantuml_code: str, output_format: str = "svg", kroki_url: str = "https://kroki.io"
) -> str:
    """Encode diagram source code into Kroki GET URL."""
    compressed = zlib.compress(plantuml_code.encode("utf-8"))
    encoded = base64.urlsafe_b64encode(compressed).decode("utf-8")
    base_url = kroki_url.rstrip("/")
    return f"{base_url}/plantuml/{output_format}/{encoded}"


def render_kroki(
    plantuml_code: str,
    output_format: str = "svg",
    kroki_url: str = "https://kroki.io",
    timeout: int = 10,
) -> bytes:
    """Render PlantUML diagram via Kroki POST request."""
    base_url = kroki_url.rstrip("/")
    endpoint = f"{base_url}/plantuml/{output_format}"
    response = requests.post(
        endpoint,
        data=plantuml_code.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.content


def main():
    parser = argparse.ArgumentParser(
        description="Convert short text description into C4-PlantUML diagram and render via Kroki."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        help="Text description or file path to diagram specification",
    )
    parser.add_argument(
        "--format",
        default="svg",
        choices=["svg", "png", "pdf", "txt"],
        help="Output format for Kroki rendering (default: svg)",
    )
    parser.add_argument(
        "--kroki-url",
        default="https://kroki.io",
        help="Base URL for Kroki service (default: https://kroki.io)",
    )
    parser.add_argument(
        "--url-only",
        action="store_true",
        help="Print the Kroki GET URL instead of rendering",
    )

    args = parser.parse_args()

    if not args.input:
        description_text = sys.stdin.read()
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                description_text = f.read()
        except FileNotFoundError:
            description_text = args.input

    puml = generate_plantuml(description_text)

    if args.url_only:
        print(encode_kroki_url(puml, output_format=args.format, kroki_url=args.kroki_url))
    else:
        print(puml)


if __name__ == "__main__":
    main()
