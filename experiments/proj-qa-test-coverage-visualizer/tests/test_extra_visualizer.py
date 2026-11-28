import sys
sys.path.insert(0, 'src')
from app.visualizer import analyze_coverage

def test_extra_analyze_coverage_structure():
    res = analyze_coverage('print("hello")', 'print("hello"); print("world")')
    assert isinstance(res, dict)
    assert 'delta' in res
