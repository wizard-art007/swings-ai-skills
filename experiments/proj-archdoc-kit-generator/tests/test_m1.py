import sys
sys.path.insert(0, 'src')
from app.kit import generate_kit

def test_generate_kit():
    desc = 'System: WebApp handling user login via AuthMicroservice.'
    result = generate_kit(desc)
    assert 'c4' in result
    assert 'mermaid' in result
    assert len(result['c4']) > 0
    assert len(result['mermaid']) > 0