import sys
sys.path.insert(0, 'src')
from app.visualizer import generate_workflow_diagram

def test_generate_workflow_diagram(tmp_path):
    result = generate_workflow_diagram("Run QA tests and report status", format_type="mermaid")
    assert isinstance(result, str)
    assert "graph" in result or "flowchart" in result
