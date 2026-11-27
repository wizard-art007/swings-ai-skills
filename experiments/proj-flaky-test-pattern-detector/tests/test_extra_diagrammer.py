import sys
sys.path.insert(0, 'src')
from app.diagrammer import generate_sequence_diagram, generate_retry_sequence_diagram


def test_generate_sequence_diagram_basic():
    events = [
        {'actor': 'Runner', 'target': 'API', 'message': 'GET /user (500)'},
        {'actor': 'Runner', 'target': 'API', 'message': 'GET /user (200)'}
    ]
    puml = generate_sequence_diagram(events, title='Retry Flow')
    assert '@startuml' in puml
    assert 'Retry Flow' in puml
    assert 'Runner' in puml
    assert 'API' in puml


def test_generate_sequence_diagram_tuples():
    events = [
        ('Client', 'Server', 'Ping'),
        ('Server', 'Client', 'Pong')
    ]
    puml = generate_sequence_diagram(events, title='PingPong')
    assert '@startuml' in puml
    assert 'PingPong' in puml
    assert 'Client' in puml


def test_generate_retry_sequence_diagram():
    runs = [
        {'status': 'failed', 'error': 'Timeout'},
        {'status': 'passed'}
    ]
    puml = generate_retry_sequence_diagram('test_login', runs)
    assert '@startuml' in puml
    assert 'Retry Trace: test_login' in puml
    assert 'Attempt 1: failed' in puml
    assert 'Attempt 2: passed' in puml
