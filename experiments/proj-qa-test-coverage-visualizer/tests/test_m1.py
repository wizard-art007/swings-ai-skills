import sys
sys.path.insert(0, 'src')
from app.visualizer import analyze_coverage

def test_analyze_coverage():
    res = analyze_coverage('def foo(): pass', 'def foo(): pass\ndef bar(): pass')
    assert isinstance(res, dict)
    assert 'delta' in res