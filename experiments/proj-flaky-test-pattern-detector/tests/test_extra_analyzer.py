import sys
sys.path.insert(0, 'src')
from app.analyzer import analyze_flaky_runs


def test_empty_runs():
    res = analyze_flaky_runs([])
    assert res['flaky_tests'] == {}
    assert res['total_runs'] == 0
    assert 'coverage_delta' in res


def test_consistent_runs():
    runs = [
        {'test_name': 'test_a', 'status': 'passed', 'code': 'def test_a(): assert True'},
        {'test_name': 'test_a', 'status': 'passed', 'code': 'def test_a(): assert True'},
        {'test_name': 'test_b', 'status': 'failed', 'code': 'def test_b(): assert False'},
    ]
    res = analyze_flaky_runs(runs)
    assert len(res['flaky_tests']) == 0
    assert 'test_a' in res['non_flaky_tests']
    assert 'test_b' in res['non_flaky_tests']
    assert res['non_flaky_tests']['test_a']['flakiness_rate'] == 0.0
    assert res['non_flaky_tests']['test_b']['flakiness_rate'] == 1.0


def test_multiple_flaky_tests():
    runs = [
        {'test_name': 'test_auth', 'status': 'failed', 'code': 'pass'},
        {'test_name': 'test_auth', 'status': 'passed', 'code': 'assert True'},
        {'test_name': 'test_db', 'status': 'passed', 'code': 'db.connect()'},
        {'test_name': 'test_db', 'status': 'error', 'code': 'db.timeout()'},
    ]
    res = analyze_flaky_runs(runs)
    assert 'test_auth' in res['flaky_tests']
    assert 'test_db' in res['flaky_tests']
    assert res['flaky_tests']['test_auth']['flakiness_rate'] == 0.5
    assert res['flaky_tests']['test_db']['flakiness_rate'] == 0.5
