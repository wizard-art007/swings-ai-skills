import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Ensure scripts/ is in sys.path as required by the prompt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from c4_generator import generate_c4_puml, render_via_kroki

def test_generate_c4_puml():
    desc = "A simple e-commerce web app with an API backend and database."
    puml = generate_c4_puml(desc)
    
    assert "@startuml" in puml
    assert "!include" in puml
    assert "C4_Container.puml" in puml
    assert desc in puml
    assert "Person(user" in puml
    assert "Container(web_app" in puml
    assert "ContainerDb(database" in puml
    assert "@enduml" in puml

@patch('c4_generator.requests.post')
def test_render_via_kroki_mocked(mock_post):
    mock_response = MagicMock()
    mock_response.text = "<svg>mocked svg content</svg>"
    mock_response.raise_for_status = lambda: None
    mock_post.return_value = mock_response

    puml = "@startuml\nPerson(u, \"User\")\n@enduml"
    result = render_via_kroki(puml, format_type="svg")

    assert "<svg>" in result
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "kroki.io/plantuml/svg" in args[0]
    assert kwargs["json"]["diagram_source"] == puml
