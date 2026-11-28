import sys
sys.path.insert(0, 'src')
from app.report import generate_coverage_diagram

def test_generate_coverage_diagram():
    diagram = generate_coverage_diagram('module A changed', 'Component A -> Component B')
    assert isinstance(diagram, str)
    assert len(diagram) > 0