from vendor.plantuml_stdlib_c4_plantuml.c4_generator import generate_c4_puml
from vendor.agents365_ai_drawio_skill.diagram_helper import text_to_mermaid

def generate_kit(description: str) -> dict:
    """Generate an architectural documentation kit combining a C4 diagram 
    and a Mermaid system flow from a unified text description.
    """
    c4_snippet = generate_c4_puml(description)
    mermaid_snippet = text_to_mermaid(description, diagram_style="flowchart")
    
    return {
        "c4": c4_snippet or "",
        "mermaid": mermaid_snippet or ""
    }

def build_markdown_docs(description: str) -> str:
    """Compile the generated diagrams into a single structured markdown documentation file."""
    kit = generate_kit(description)
    c4_code = kit.get("c4", "")
    mermaid_code = kit.get("mermaid", "")

    md_lines = [
        "# Architecture Documentation",
        "",
        "## C4 Architecture Diagram",
        "```plantuml",
        c4_code,
        "```",
        "",
        "## System Flow (Mermaid)",
        "```mermaid",
        mermaid_code,
        "```",
        ""
    ]
    return "\n".join(md_lines)
