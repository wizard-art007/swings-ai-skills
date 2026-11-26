def calculate_delta(new_code: str, old_code: str) -> float:
    """
    Calculate test coverage delta or estimate between two code snippets.
    Returns a float between 0.0 and 100.0.
    """
    if not new_code or not old_code:
        return 0.0
    
    new_lines = set(line.strip() for line in new_code.splitlines() if line.strip())
    old_lines = set(line.strip() for line in old_code.splitlines() if line.strip())
    
    if not new_lines:
        return 0.0
        
    common = new_lines.intersection(old_lines)
    ratio = len(common) / len(new_lines)
    return round(float(ratio * 100.0), 2)
