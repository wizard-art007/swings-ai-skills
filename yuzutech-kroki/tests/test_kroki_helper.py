import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import kroki_helper

def test_text_to_mermaid_single_line():
    desc = "User logs in"
    source = kroki_helper.text_to_mermaid(desc)
    assert "graph TD" in source
    assert 'A["User logs in"]' in source

def test_text_to_mermaid_multi_line():
    desc = "Step one\nStep two\nStep three"
    source = kroki_helper.text_to_mermaid(desc)
    assert "graph TD" in source
    assert 'N0["Step one"]' in source
    assert 'N1["Step two"]' in source
    assert 'N2["Step three"]' in source
    assert "N0 --> N1" in source
    assert "N1 --> N2" in source

def test_text_to_mermaid_empty():
    source = kroki_helper.text_to_mermaid("")
    assert "graph TD" in source
    assert "Empty Description" in source

def test_generate_kroki_url():
    diagram = "graph TD\n    A --> B"
    url = kroki_helper.generate_kroki_url(diagram, "mermaid", "svg")
    assert url.startswith("https://kroki.io/mermaid/svg/")
    # Ensure it generated a non-empty encoded string part
    encoded_part = url.split("/")[-1]
    assert len(encoded_part) > 0
