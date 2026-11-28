import sys
sys.path.insert(0, 'src')
from app.visualizer import generate_coverage_report

def test_generate_coverage_report():
    report = generate_coverage_report('old code', 'new code with tests')
    assert 'graph' in report or 'flowchart' in report
