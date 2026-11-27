import sys
sys.path.insert(0, 'src')
from app.kit import build_markdown_docs

def test_build_markdown_docs():
    desc = 'System: API Gateway routing requests to PaymentService.'
    md = build_markdown_docs(desc)
    assert '# Architecture Documentation' in md
    assert '```plantuml' in md
    assert '```mermaid' in md