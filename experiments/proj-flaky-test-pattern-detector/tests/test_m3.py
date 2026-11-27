import sys
sys.path.insert(0, 'src')
from app.report_builder import build_flaky_report

def test_build_flaky_report():
    runs = [
        {'test_name': 'test_checkout', 'status': 'failed', 'code': 'def test_checkout(): pass'},
        {'test_name': 'test_checkout', 'status': 'passed', 'code': 'def test_checkout(): pass'}
    ]
    events = [
        {'actor': 'Runner', 'target': 'DB', 'message': 'Query timeout'}
    ]
    report = build_flaky_report(runs, events)
    assert '# Flaky Test Diagnostic Report' in report
    assert 'test_checkout' in report
    assert '@startuml' in report
