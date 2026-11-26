from captools import load_tool

def test_tech_graph_mermaid():
    mod = load_tool('yizhiyanhua-ai-fireworks-tech-graph', 'diagram_helper')
    graph = mod.parse_text_description("Frontend -> Backend -> Database")
    mermaid = mod.to_mermaid(graph, style="default", direction="TD")
    assert isinstance(mermaid, str)
    assert "graph TD" in mermaid
    assert "Frontend" in mermaid
    assert "Database" in mermaid
