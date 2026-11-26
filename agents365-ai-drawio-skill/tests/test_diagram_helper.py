import base64
import sys
import zlib
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "scripts")

import diagram_helper


def test_sanitize_id():
    assert diagram_helper.sanitize_id("My Service") == "My_Service"
    assert diagram_helper.sanitize_id("db-replica.01") == "db_replica_01"
    assert diagram_helper.sanitize_id("  ") == "node"


def test_parse_connection_line():
    line = "Client -> Server: Send request"
    parsed = diagram_helper.parse_connection_line(line)
    assert parsed == ("Client", "Server", "->", "Send request")

    line_no_label = "ServiceA --> ServiceB"
    parsed_no_label = diagram_helper.parse_connection_line(line_no_label)
    assert parsed_no_label == ("ServiceA", "ServiceB", "-->", "")

    invalid = "just some random text without arrow"
    assert diagram_helper.parse_connection_line(invalid) is None


def test_text_to_mermaid_flowchart():
    text = """
    User -> Frontend: Browse catalog
    Frontend -> Backend: API request
    Backend -> Database: SQL query
    """
    mermaid_src = diagram_helper.text_to_mermaid(text, diagram_style="flowchart")
    assert mermaid_src.startswith("flowchart TD")
    assert "User[\"User\"] -->|\"Browse catalog\"| Frontend[\"Frontend\"]" in mermaid_src
    assert "Backend[\"Backend\"] -->|\"SQL query\"| Database[\"Database\"]" in mermaid_src


def test_text_to_mermaid_sequence():
    text = """
    Alice -> Bob: Hello
    Bob --> Alice: Response
    """
    seq_src = diagram_helper.text_to_mermaid(text, diagram_style="sequence")
    assert "sequenceDiagram" in seq_src
    assert "Alice->>Bob: Hello" in seq_src
    assert "Bob-->>Alice: Response" in seq_src


def test_text_to_plantuml_flowchart_and_c4():
    text = "API Gateway -> Auth Service: Validate Token"
    puml = diagram_helper.text_to_plantuml(text, diagram_style="flowchart")
    assert puml.startswith("@startuml")
    assert puml.endswith("@enduml")
    assert "[API Gateway] -> [Auth Service] : Validate Token" in puml

    c4_puml = diagram_helper.text_to_plantuml(text, diagram_style="c4")
    assert "!include <C4/C4_Container>" in c4_puml
    assert "Rel(API_Gateway, Auth_Service, \"Validate Token\")" in c4_puml


def test_text_to_diagram_dispatch():
    text = "A -> B: ping"
    m_res = diagram_helper.text_to_diagram(text, diagram_type="mermaid")
    assert "flowchart TD" in m_res

    p_res = diagram_helper.text_to_diagram(text, diagram_type="plantuml", style="sequence")
    assert "@startuml" in p_res
    assert "A -> B : ping" in p_res

    with pytest.raises(ValueError):
        diagram_helper.text_to_diagram(text, diagram_type="unsupported_engine")


def test_encode_and_build_kroki_url():
    source = "graph TD\n  A --> B"
    encoded = diagram_helper.encode_kroki_payload(source)

    decompressed = zlib.decompress(base64.urlsafe_b64decode(encoded.encode("ascii"))).decode("utf-8")
    assert decompressed == source

    url = diagram_helper.build_kroki_url(source, diagram_type="mermaid", output_format="svg")
    assert url.startswith("https://kroki.io/mermaid/svg/")
    assert encoded in url


def test_render_diagram_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<svg>Mocked SVG Diagram</svg>"

    with patch("requests.post", return_value=mock_response) as mock_post:
        result = diagram_helper.render_diagram(
            diagram_source="flowchart TD\n  A --> B",
            diagram_type="mermaid",
            output_format="svg",
            kroki_url="https://kroki.io",
        )
        assert result == b"<svg>Mocked SVG Diagram</svg>"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://kroki.io/mermaid/svg"
        assert kwargs["headers"]["Content-Type"] == "text/plain; charset=utf-8"


def test_render_diagram_error():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Syntax Error in Mermaid"

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(RuntimeError) as exc_info:
            diagram_helper.render_diagram("invalid diagram")
        assert "Kroki rendering failed with HTTP 400" in str(exc_info.value)


def test_main_cli_source_only(capsys):
    ret = diagram_helper.main(["A -> B: Call", "--type", "mermaid", "--source-only"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "flowchart TD" in captured.out
    assert "A[\"A\"] -->|\"Call\"| B[\"B\"]" in captured.out
