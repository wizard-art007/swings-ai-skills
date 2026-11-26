import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import diagram_helper

def test_tech_graph_mermaid():
    graph = diagram_helper.parse_text_description("Frontend -> Backend -> Database")
    mermaid = diagram_helper.to_mermaid(graph, style="default", direction="TD")
    assert isinstance(mermaid, str)
    assert "graph TD" in mermaid or "flowchart TD" in mermaid
    assert "Frontend" in mermaid
    assert "Database" in mermaid
