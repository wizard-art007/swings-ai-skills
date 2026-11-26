"""
tests/test_diagram_helper.py: Unit tests for diagram generation and Kroki rendering.
Operates completely offline with mocked HTTP requests.
"""

import sys
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, "scripts")

from diagram_helper import (
    SUPPORTED_STYLES,
    STYLE_THEMES,
    build_pattern_spec,
    encode_kroki_payload,
    generate_diagram,
    get_kroki_url,
    parse_text_description,
    render_kroki,
    to_mermaid,
    to_plantuml,
)


def test_supported_styles_and_themes():
    assert len(SUPPORTED_STYLES) >= 7
    for style in SUPPORTED_STYLES:
        assert style in STYLE_THEMES
        theme = STYLE_THEMES[style]
        for key in ["primary", "secondary", "bg", "text", "border", "accent"]:
            assert key in theme
            assert theme[key].startswith("#")


def test_parse_text_description_simple():
    text = """
    # Infrastructure diagram
    Client -> API_Gateway : HTTP Request
    API_Gateway -> Auth_Service : Verify Token
    API_Gateway -> Database : Query
    """
    spec = parse_text_description(text)
    node_ids = [n["id"] for n in spec["nodes"]]
    assert "Client" in node_ids
    assert "API_Gateway" in node_ids
    assert "Auth_Service" in node_ids
    assert "Database" in node_ids

    assert len(spec["edges"]) == 3
    assert spec["edges"][0]["from"] == "Client"
    assert spec["edges"][0]["to"] == "API_Gateway"
    assert spec["edges"][0]["label"] == "HTTP Request"


def test_parse_text_description_chain():
    text = "Frontend -> Backend -> Cache -> DB"
    spec = parse_text_description(text)
    assert len(spec["nodes"]) == 4
    assert len(spec["edges"]) == 3
    assert spec["edges"][0]["from"] == "Frontend"
    assert spec["edges"][0]["to"] == "Backend"
    assert spec["edges"][2]["from"] == "Cache"
    assert spec["edges"][2]["to"] == "DB"


def test_build_pattern_spec_chain():
    spec = build_pattern_spec("chain")
    assert "Sequential Agent Chain" in spec["title"]
    assert len(spec["nodes"]) == 5
    assert len(spec["edges"]) == 4


def test_build_pattern_spec_router():
    spec = build_pattern_spec("router", {"routes": ["SqlAgent", "WebAgent"]})
    assert spec["title"] == "Router Agent Pattern"
    node_labels = [n["label"] for n in spec["nodes"]]
    assert "Intent Router" in node_labels
    assert "SqlAgent" in node_labels
    assert "WebAgent" in node_labels
    assert any("SqlAgent" in e["label"] for e in spec["edges"])


def test_build_pattern_spec_orchestrator():
    spec = build_pattern_spec("orchestrator_workers")
    assert spec["title"] == "Orchestrator-Workers Pattern"
    labels = [n["label"] for n in spec["nodes"]]
    assert "Orchestrator Agent" in labels
    assert "Synthesis & Reduce" in labels


def test_build_pattern_spec_evaluator_optimizer():
    spec = build_pattern_spec("evaluator_optimizer")
    assert spec["title"] == "Evaluator-Optimizer Loop"
    labels = [n["label"] for n in spec["nodes"]]
    assert "Generator LLM" in labels
    assert "Evaluator / Critic" in labels


def test_build_pattern_invalid():
    with pytest.raises(ValueError, match="Unknown pattern"):
        build_pattern_spec("unsupported_pattern")


def test_to_mermaid_formatting():
    spec = {
        "nodes": [{"id": "A", "label": "Service A"}, {"id": "B", "label": "Service B"}],
        "edges": [{"from": "A", "to": "B", "label": "call"}],
    }
    result = to_mermaid(spec, style="cyberpunk", direction="LR")
    assert result.startswith("flowchart LR")
    assert 'A["Service A"]' in result
    assert 'B["Service B"]' in result
    assert 'A -->|"call"| B' in result
    assert "classDef default" in result
    assert STYLE_THEMES["cyberpunk"]["primary"] in result


def test_to_plantuml_formatting():
    spec = {
        "title": "System Arch",
        "nodes": [{"id": "svc1", "label": "Service 1"}, {"id": "svc2", "label": "Service 2"}],
        "edges": [{"from": "svc1", "to": "svc2", "label": "sync"}],
    }
    result = to_plantuml(spec, style="blueprint")
    assert result.startswith("@startuml")
    assert "title System Arch" in result
    assert "[Service 1] as svc1" in result
    assert 'svc1 --> svc2 : "sync"' in result
    assert result.endswith("@enduml")


def test_generate_diagram_high_level():
    # From description with Mermaid
    mermaid_out = generate_diagram(description="Client -> Server: Ping", diagram_type="mermaid", style="dark")
    assert "flowchart TD" in mermaid_out
    assert "Client" in mermaid_out
    assert "Server" in mermaid_out

    # From pattern with PlantUML
    puml_out = generate_diagram(pattern="chain", diagram_type="plantuml", style="minimal")
    assert "@startuml" in puml_out
    assert "LLM_Agent" in puml_out

    # Invalid options
    with pytest.raises(ValueError, match="Either 'description' or 'pattern'"):
        generate_diagram()

    with pytest.raises(ValueError, match="Unsupported diagram_type"):
        generate_diagram(description="A -> B", diagram_type="unknown")


def test_encode_kroki_payload_and_url():
    source = "flowchart TD\n  A --> B"
    encoded = encode_kroki_payload(source)
    assert isinstance(encoded, str)
    assert len(encoded) > 0

    url = get_kroki_url(source, diagram_type="mermaid", output_format="svg")
    assert url.startswith("https://kroki.io/mermaid/svg/")
    assert encoded in url


@patch("diagram_helper.requests.post")
def test_render_kroki_success(mock_post):
    fake_svg = b"<svg><g><text>Diagram</text></g></svg>"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = fake_svg
    mock_post.return_value = mock_response

    output = render_kroki("flowchart TD\n  A --> B", diagram_type="mermaid", output_format="svg")
    assert output == fake_svg
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://kroki.io/mermaid/svg"
    assert kwargs["headers"]["Content-Type"] == "text/plain; charset=utf-8"


@patch("diagram_helper.requests.post")
def test_render_kroki_failure(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Syntax error in diagram description"
    mock_post.return_value = mock_response

    with pytest.raises(RuntimeError, match="Kroki rendering failed with HTTP 400"):
        render_kroki("bad diagram", diagram_type="mermaid", output_format="svg")
