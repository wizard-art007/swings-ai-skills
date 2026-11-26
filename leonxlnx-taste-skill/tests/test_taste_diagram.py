import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Ensure scripts/ is in sys.path as required
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import taste_diagram

def test_description_to_mermaid_default():
    code = taste_diagram.description_to_mermaid("")
    assert "flowchart TD" in code
    assert "Default Taste Skill Workflow" in code

def test_description_to_mermaid_custom():
    custom_desc = "Build a stunning landing page for AI agents"
    code = taste_diagram.description_to_mermaid(custom_desc)
    assert "flowchart TD" in code
    assert custom_desc in code
    assert "Real Browser Checker" in code

@patch('taste_diagram.requests.get')
def test_render_via_kroki_offline(mock_get):
    # Setup mock response to test without network access
    mock_response = MagicMock()
    mock_response.text = "<svg>mocked svg content</svg>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    mermaid_code = "flowchart TD\nA-->B"
    result = taste_diagram.render_via_kroki(mermaid_code, format="svg")

    assert "<svg>" in result
    mock_get.assert_called_once()
    called_url = mock_get.call_args[0][0]
    assert called_url.startswith("https://kroki.io/mermaid/svg/")
