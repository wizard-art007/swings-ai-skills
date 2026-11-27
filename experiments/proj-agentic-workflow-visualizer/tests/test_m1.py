import sys
sys.path.insert(0, 'src')
from app.visualizer import route_and_spec

def test_route_and_spec(tmp_path):
    spec = route_and_spec("Search the web and summarize results")
    assert "nodes" in spec
    assert "edges" in spec
