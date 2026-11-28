from vendor.sebastianbergmann_php_code_coverage.test_coverage_analyzer import calculate_delta
from vendor.mermaid_js_mermaid.mermaid_helper import text_to_mermaid, get_kroki_url, fetch_diagram

def analyze_coverage(old_code: str, new_code: str) -> dict:
    """
    Analyze coverage metrics between old_code and new_code using vendor tools.
    Returns a dictionary containing at least the 'delta' key as required by the acceptance test.
    """
    # Note: calculate_delta in vendor signature is calculate_delta(new_code, old_code)
    delta_result = calculate_delta(new_code, old_code)
    
    # Ensure return is a dictionary with 'delta'
    if isinstance(delta_result, dict):
        res = delta_result.copy()
        if 'delta' not in res:
            res['delta'] = res
    else:
        res = {'delta': delta_result}
        
    return res
