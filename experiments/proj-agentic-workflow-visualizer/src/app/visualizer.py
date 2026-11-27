from vendor.deepset_ai_haystack.agent_prompt_router import route_prompt
from vendor.yizhiyanhua_ai_fireworks_tech_graph.diagram_helper import parse_text_description, build_pattern_spec


def route_and_spec(prompt: str) -> dict:
    """Route an input prompt and generate a corresponding graph specification."""
    agent_type = route_prompt(prompt)
    
    # Try parsing text description or building pattern spec based on routed agent or prompt
    # parse_text_description handles concise natural language or arrow-based descriptions
    spec = parse_text_description(prompt)
    if not spec or not spec.get("nodes"):
        # Fallback to building pattern spec if parsing doesn't produce nodes
        spec = build_pattern_spec(agent_type, {"prompt": prompt})
        
    return spec
