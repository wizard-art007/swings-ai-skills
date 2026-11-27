import sys
sys.path.insert(0, 'src')
from app.report_builder import build_flaky_report


def test_build_flaky_report_empty():
    report = build_flaky_report([])
    assert '# Flaky Test Diagnostic Report' in report
    assert '@startuml' in report
    assert 'No flaky tests detected.' in report


def test_build_flaky_report_with_dict_events():
    runs = [
        {'test_name': 'test_login', 'status': 'failed'},
        {'test_name': 'test_login', 'status': 'passed'},
    ]
    events = {
        'test_login': [{'actor': 'Client', 'target': 'AuthService', 'message': 'Login attempt'}]
    }
    report = build_flaky_report(runs, events)
    assert '# Flaky Test Diagnostic Report' in report
    assert 'test_login' in report
    assert 'AuthService' in report
    assert '@startuml' in report
