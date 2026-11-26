import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Ensure scripts directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import openheart_helper

def test_text_to_diagram_sequence():
    desc = "Analyze Java CFG and generate SSA form"
    diagram = openheart_helper.text_to_diagram(desc, diagram_type="sequence")
    
    assert "sequenceDiagram" in diagram
    assert "autonumber" in diagram
    assert desc in diagram

def test_text_to_diagram_class():
    desc = "Symbol table component"
    diagram = openheart_helper.text_to_diagram(desc, diagram_type="class")
    
    assert "classDiagram" in diagram
    assert "OpenHeartAnalyzer" in diagram
    assert desc in diagram

def test_encode_mermaid_for_kroki():
    code = "sequenceDiagram\n    A->>B: Hello"
    encoded = openheart_helper.encode_mermaid_for_kroki(code)
    
    assert isinstance(encoded, str)
    assert len(encoded) > 0
    # Should be URL safe (no +, /, or = padding)
    assert "+" not in encoded
    assert "/" not in encoded
    assert "=" not in encoded

def test_get_kroki_url():
    code = "sequenceDiagram\n    A->>B: Hello"
    url = openheart_helper.get_kroki_url(code, format_type="svg", server_url="https://kroki.io")
    
    assert url.startswith("https://kroki.io/mermaid/svg/")

@patch('openheart_helper.requests.get')
def test_render_diagram_remotely(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<svg></svg>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    code = "sequenceDiagram\n    A->>B: Test"
    result = openheart_helper.render_diagram_remotely(code)

    assert result == "<svg></svg>"
    mock_get.assert_called_once()
