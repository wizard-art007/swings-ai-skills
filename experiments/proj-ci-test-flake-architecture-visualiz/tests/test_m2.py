import sys
sys.path.insert(0, 'src')
from app.flake_visualizer import generate_flake_sequence

def test_generate_flake_sequence():
    analysis = {'test_auth': {'flaky': True, 'reason': 'timeout'}}
    puml = generate_flake_sequence(analysis)
    assert 'sequenceDiagram' in puml or 'actor' in puml
