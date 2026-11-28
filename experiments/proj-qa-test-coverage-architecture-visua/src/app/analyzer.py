from vendor.sebastianbergmann_php_code_coverage.test_coverage_analyzer import calculate_delta

def evaluate_coverage_changes(new_code: str, old_code: str) -> dict:
    """Evaluates test coverage changes between new and old code snippets.

    Uses calculate_delta from the sebastianbergmann_php_code_coverage skill tool
    and maps the results along with component architecture descriptions.
    """
    delta_result = calculate_delta(new_code, old_code)
    
    # Ensure result is structured cleanly as a dict
    if not isinstance(delta_result, dict):
        delta_result = {"delta": delta_result}

    # Map components and descriptive text
    result = {
        "delta": delta_result,
        "component_mapping": {
            "new_code_length": len(new_code),
            "old_code_length": len(old_code),
            "description": "Evaluated coverage delta between new and old architecture components."
        }
    }
    return result
