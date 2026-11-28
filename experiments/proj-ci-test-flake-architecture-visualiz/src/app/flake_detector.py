"""Flaky test pattern detector module."""

from typing import List, Dict, Any


def detect_flaky_patterns(logs: List[str]) -> Dict[str, Dict[str, Any]]:
    """Parse input execution logs for intermittent test failure patterns.

    A test is considered flaky if it appears multiple times in the logs and exhibits
    mixed outcomes (both PASS and FAIL/TIMEOUT/ERROR, etc.), or explicitly alternates.

    Args:
        logs: A list of log string lines representing test executions (e.g., 'test_auth PASSED').

    Returns:
        A dictionary mapping test names to details including whether they are flaky.
    """
    test_outcomes: Dict[str, List[str]] = {}

    for line in logs:
        parts = line.strip().split()
        if len(parts) >= 2:
            test_name = parts[0]
            status = parts[1].upper()
            if test_name not in test_outcomes:
                test_outcomes[test_name] = []
            test_outcomes[test_name].append(status)

    result: Dict[str, Dict[str, Any]] = {}
    for test_name, outcomes in test_outcomes.items():
        has_passed = any(status in ('PASSED', 'PASS', 'SUCCESS') for status in outcomes)
        has_failed = any(status in ('FAILED', 'FAIL', 'TIMEOUT', 'ERROR', 'CRASH') for status in outcomes)

        # Flaky if there are multiple occurrences with mixed results, or explicitly both pass and fail
        is_flaky = (has_passed and has_failed) or (len(set(outcomes)) > 1)

        result[test_name] = {
            'flaky': is_flaky,
            'outcomes': outcomes
        }

    return result
