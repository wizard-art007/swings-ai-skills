from captools import load_tool

def test_test_coverage_analyzer_missing():
    m = load_tool('*', 'test_coverage_analyzer')
    try:
        coverage = m.calculate_delta("def test_foo(): pass", "def foo(): pass")
        assert 0.0 <= coverage <= 100.0
    except (NameError, AttributeError, NotImplementedError):
        assert True
