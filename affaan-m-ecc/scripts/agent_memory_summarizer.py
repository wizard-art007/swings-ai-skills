"""Agent Memory Summarizer module for ECC."""

def summarize_trace(trace):
    """Summarize a list of agent execution steps."""
    if not trace:
        return "Empty trace provided."
    summary_lines = []
    for item in trace:
        step = item.get("step", "unknown")
        action = item.get("action", "unknown action")
        result = item.get("result", "unknown result")
        summary_lines.append(f"Step {step}: {action} -> {result}")
    return "\n".join(summary_lines)
