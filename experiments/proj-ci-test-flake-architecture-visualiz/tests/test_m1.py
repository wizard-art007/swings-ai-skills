import sys
sys.path.insert(0, 'src')
from app.flake_detector import detect_flaky_patterns

def test_detect_flaky():
    logs = ['test_auth PASSED', 'test_auth FAILED timeout', 'test_auth PASSED']
    result = detect_flaky_patterns(logs)
    assert 'test_auth' in result
    assert result['test_auth']['flaky'] is True
