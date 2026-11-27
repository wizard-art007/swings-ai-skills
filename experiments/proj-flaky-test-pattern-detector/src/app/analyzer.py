from vendor.sebastianbergmann_php_code_coverage.test_coverage_analyzer import calculate_delta


def analyze_flaky_runs(runs):
    """
    Parse test execution logs to identify tests with inconsistent pass/fail outcomes
    and compute coverage deltas.

    Args:
        runs (list[dict]): List of test execution run records. Each record is a dict
                           containing 'test_name', 'status', and optionally 'code', etc.

    Returns:
        dict: Diagnostic dictionary containing:
            - 'flaky_tests': dict mapping test names to flakiness details
            - 'non_flaky_tests': dict mapping test names to outcome details
            - 'coverage_delta': result from calculate_delta
            - 'total_runs': int
            - 'total_tests': int
    """
    if not runs:
        return {
            'flaky_tests': {},
            'non_flaky_tests': {},
            'coverage_delta': calculate_delta("", ""),
            'total_runs': 0,
            'total_tests': 0
        }

    tests_by_name = {}
    passed_codes = []
    failed_codes = []

    for run in runs:
        name = run.get('test_name', 'unknown')
        status = str(run.get('status', '')).lower()
        code = run.get('code', '')

        if name not in tests_by_name:
            tests_by_name[name] = {
                'passed_count': 0,
                'failed_count': 0,
                'other_count': 0,
                'total_runs': 0,
                'statuses': [],
                'runs': []
            }

        t_entry = tests_by_name[name]
        t_entry['total_runs'] += 1
        t_entry['statuses'].append(status)
        t_entry['runs'].append(run)

        is_pass = status in ('passed', 'pass', 'ok', 'success')
        is_fail = status in ('failed', 'fail', 'error', 'errored')

        if is_pass:
            t_entry['passed_count'] += 1
            if code:
                passed_codes.append(code)
        elif is_fail:
            t_entry['failed_count'] += 1
            if code:
                failed_codes.append(code)
        else:
            t_entry['other_count'] += 1

    flaky_tests = {}
    non_flaky_tests = {}

    for name, data in tests_by_name.items():
        total = data['total_runs']
        passed = data['passed_count']
        failed = data['failed_count']

        # A test is flaky if it has both passing and failing outcomes across runs
        is_flaky = (passed > 0 and failed > 0)
        flakiness_rate = (failed / total) if total > 0 else 0.0

        details = {
            'test_name': name,
            'flakiness_rate': flakiness_rate,
            'total_runs': total,
            'passed_count': passed,
            'failed_count': failed,
            'other_count': data['other_count'],
            'statuses': data['statuses'],
            'runs': data['runs']
        }

        if is_flaky:
            flaky_tests[name] = details
        else:
            non_flaky_tests[name] = details

    new_code = "\n".join(passed_codes) if passed_codes else ""
    old_code = "\n".join(failed_codes) if failed_codes else ""

    cov_delta = calculate_delta(new_code, old_code)

    return {
        'flaky_tests': flaky_tests,
        'non_flaky_tests': non_flaky_tests,
        'coverage_delta': cov_delta,
        'total_runs': len(runs),
        'total_tests': len(tests_by_name)
    }
