import sys
import os
import pytest
from unittest.mock import patch, Mock

# Ensure scripts/ is in sys.path as requested
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import yn_diagram_helper

def test_text_to_diagram_source_mermaid():
    desc = "Create a new note"
    source = yn_diagram_helper.text_to_diagram_source(desc, "mermaid")
    assert "graph TD;" in source
    assert desc in source

def test_text_to_diagram_source_plantuml():
    desc = "Encrypt document"
    source = yn_diagram_helper.text_to_diagram_source(desc, "plantuml")
    assert "@startuml" in source
    assert "@enduml" in source
    assert desc in source

def test_encode_kroki():
    source = "graph TD; A-->B;"
    encoded = yn_diagram_helper.encode_kroki(source)
    assert isinstance(encoded, str)
    assert len(encoded) > 0

def test_render_diagram_url():
    source = "graph TD; A-->B;"
    url = yn_diagram_helper.render_diagram_url(source, "mermaid")
    assert url.startswith("https://kroki.io/mermaid/svg/")

@patch('yn_diagram_helper.requests.get')
def test_fetch_diagram_svg_mocked(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "<svg>mocked</svg>"
    mock_get.return_value = mock_response

    svg = yn_diagram_helper.fetch_diagram_svg("graph TD; A-->B;", "mermaid")
    assert svg == "<svg>mocked</svg>"
    mock_get.assert_called_once()
