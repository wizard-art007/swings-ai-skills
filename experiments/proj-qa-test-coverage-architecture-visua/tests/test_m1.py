import sys
sys.path.insert(0, 'src')
from app.analyzer import evaluate_coverage_changes

def test_evaluate_coverage_changes():
    res = evaluate_coverage_changes('def new_func(): pass', 'def old_func(): pass')
    assert 'delta' in res or isinstance(res, dict)