"""
Agent prompt router tool for Haystack skill.
"""
from typing import Dict, Any

def route_prompt(prompt: str) -> Dict[str, Any]:
    """
    Route a given prompt to an appropriate agent type based on keywords.
    """
    lower_prompt = prompt.lower()
    
    # Check for debugging keywords
    if any(kw in lower_prompt for kw in ["debug", "error", "segmentation fault", "fix", "issue", "crash", "bug"]):
        return {"agent_type": "debugging"}
    
    # Check for coding keywords
    if any(kw in lower_prompt for kw in ["code", "python", "async", "script", "function", "class", "implement", "programming"]):
        return {"agent_type": "coding"}
        
    return {"agent_type": "general"}
