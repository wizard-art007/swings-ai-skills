import sys
sys.path.insert(0, 'src')
from app.analyzer import evaluate_coverage_changes

def test_evaluate_coverage_changes_extra():
    res = evaluate_coverage_changes('def test_a(): pass', 'def test_b(): pass')
    assert isinstance(res, dict)
    assert 'delta' in res
    assert 'component_mapping' in res
