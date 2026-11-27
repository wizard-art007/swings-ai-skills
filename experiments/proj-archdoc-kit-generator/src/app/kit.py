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
