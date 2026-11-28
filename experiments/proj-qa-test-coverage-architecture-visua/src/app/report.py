from vendor.mermaid_js_mermaid.mermaid_helper import text_to_mermaid
from app.analyzer import evaluate_coverage_changes

def generate_coverage_diagram(coverage_input: str, architecture_description: str) -> str:
    """Generates an integrated QA architecture visualizer diagram incorporating coverage metrics and Mermaid generation."""
    # Use analyzer to process inputs
    evaluation = evaluate_coverage_changes(coverage_input, architecture_description)
    
    # Construct descriptive text for Mermaid conversion
    combined_desc = f"Coverage Delta: {evaluation.get('delta')}. Architecture: {architecture_description}"
    
    # Generate mermaid diagram via skill tool
    mermaid_diagram = text_to_mermaid(combined_desc)
    
    if not isinstance(mermaid_diagram, str) or not mermaid_diagram.strip():
        mermaid_diagram = f"graph TD\n  A[{architecture_description}] --> B[Coverage Evaluated]"
        
    return mermaid_diagram
