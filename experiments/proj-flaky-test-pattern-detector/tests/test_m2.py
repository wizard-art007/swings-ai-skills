import sys
sys.path.insert(0, 'src')
from app.diagrammer import generate_sequence_diagram

def test_generate_sequence_diagram():
    events = [
        {'actor': 'Runner', 'target': 'API', 'message': 'GET /user (500)'},
        {'actor': 'Runner', 'target': 'API', 'message': 'GET /user (200)'}
    ]
    puml = generate_sequence_diagram(events, title='Retry Flow')
    assert '@startuml' in puml
    assert 'Retry Flow' in puml
