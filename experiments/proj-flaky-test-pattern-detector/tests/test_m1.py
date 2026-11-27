import sys
sys.path.insert(0, 'src')
from app.analyzer import analyze_flaky_runs

def test_analyze_flaky_runs():
    runs = [
        {'test_name': 'test_login', 'status': 'failed', 'code': 'def test_login(): pass'},
        {'test_name': 'test_login', 'status': 'passed', 'code': 'def test_login(): assert True'}
    ]
    res = analyze_flaky_runs(runs)
    assert 'test_login' in res['flaky_tests']
    assert res['flaky_tests']['test_login']['flakiness_rate'] == 0.5
    assert 'coverage_delta' in res
