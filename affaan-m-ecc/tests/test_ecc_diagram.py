import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Ensure scripts directory is in sys.path as required
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from ecc_diagram import text_to_mermaid, render_diagram_kroki

def test_text_to_mermaid_basic():
    description = "Step 1: Initialize\nStep 2: Execute\nStep 3: Finish"
    mermaid = text_to_mermaid(description)
    
    assert "graph TD" in mermaid
    assert 'Title["Step 1: Initialize"]' in mermaid
    assert 'Step1["Step 2: Execute"]' in mermaid
    assert 'Step2["Step 3: Finish"]' in mermaid
    assert "Title --> Step1" in mermaid
    assert "Step1 --> Step2" in mermaid

def test_text_to_mermaid_empty():
    mermaid = text_to_mermaid("")
    assert "graph TD" in mermaid
    assert "Start" in mermaid

@patch('ecc_diagram.requests.get')
def test_render_diagram_kroki(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<svg>mocked svg</svg>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = render_diagram_kroki("graph TD\nA-->B", "mermaid", "svg")
    assert result == "<svg>mocked svg</svg>"
    mock_get.assert_called_once()
    args, _ = mock_get.call_args
    assert "https://kroki.io/mermaid/svg/" in args[0]
