import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import diagram_helper

def test_generate_mermaid_source():
    desc = "User Login Flow"
    source = diagram_helper.generate_mermaid_source(desc)
    assert "graph TD" in source
    assert "User Login Flow" in source

def test_generate_plantuml_source():
    desc = "Database Schema"
    source = diagram_helper.generate_plantuml_source(desc)
    assert "@startuml" in source
    assert "@enduml" in source
    assert "Database Schema" in source

def test_get_kroki_url_mermaid():
    source = "graph TD\nA-->B"
    url = diagram_helper.get_kroki_url("mermaid", source, "svg")
    assert url.startswith("https://kroki.io/mermaid/svg/")

def test_get_kroki_url_plantuml():
    source = "@startuml\nA->B\n@enduml"
    url = diagram_helper.get_kroki_url("plantuml", source, "svg")
    assert url.startswith("https://kroki.io/plantuml/svg/")

def test_get_kroki_url_unsupported():
    with pytest.raises(ValueError):
        diagram_helper.get_kroki_url("unknown", "source")

@patch('diagram_helper.requests.get')
def test_render_diagram_mocked(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<svg>mocked svg</svg>"
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = diagram_helper.render_diagram("mermaid", "Test description")
    assert result == "<svg>mocked svg</svg>"
    mock_get.assert_called_once()
