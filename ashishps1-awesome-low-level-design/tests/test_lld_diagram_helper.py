import io
import sys
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, "scripts")

from lld_diagram_helper import (
    encode_kroki,
    get_kroki_url,
    render_kroki,
    parse_dsl_to_elements,
    to_plantuml,
    to_mermaid,
    generate_diagram,
    get_template,
    list_templates,
    LLD_TEMPLATES,
    KrokiError,
    main,
)


def test_encode_and_get_kroki_url():
    sample = "@startuml\nclass User\n@enduml"
    encoded = encode_kroki(sample)
    assert isinstance(encoded, str)
    assert len(encoded) > 0

    url = get_kroki_url(sample, diagram_type="plantuml", output_format="svg")
    assert url.startswith("https://kroki.io/plantuml/svg/")
    assert encoded in url

    custom_url = get_kroki_url(sample, diagram_type="mermaid", output_format="png", base_url="https://mykroki.local/")
    assert custom_url.startswith("https://mykroki.local/mermaid/png/")


def test_parse_dsl_to_elements_with_shorthand():
    text = """
    title Parking System
    class ParkingLot
    class Car
    Car is-a Vehicle
    ParkingLot composes Floor
    Order implements IPayment
    Service depends-on Repo
    """
    title, lines = parse_dsl_to_elements(text)
    assert title == "Parking System"
    assert "Car --|> Vehicle" in lines
    assert "ParkingLot *-- Floor" in lines
    assert "Order ..|> IPayment" in lines
    assert "Service ..> Repo" in lines


def test_to_plantuml_structure():
    text = """
    class Shape {
      +draw(): void
    }
    class Circle
    Circle extends Shape
    """
    plantuml = to_plantuml(text, default_title="Geometry LLD")
    assert plantuml.startswith("@startuml")
    assert plantuml.endswith("@enduml")
    assert "title Geometry LLD" in plantuml
    assert "Circle --|> Shape" in plantuml
    assert "+draw(): void" in plantuml


def test_to_mermaid_structure():
    text = """
    title: Observer Pattern
    Subject o-- Observer : notifies
    """
    mermaid = to_mermaid(text)
    assert "classDiagram" in mermaid
    assert "title: Observer Pattern" in mermaid
    assert "Subject o-- Observer : notifies" in mermaid


def test_generate_diagram_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported format 'graphviz'"):
        generate_diagram("class A", target_format="graphviz")


def test_lld_templates_retrieval():
    templates = list_templates()
    assert "strategy" in templates
    assert "observer" in templates
    assert "parking_lot" in templates

    tmpl = get_template("strategy")
    assert "PaymentStrategy" in tmpl["description"]

    # Test kebab-case alias
    tmpl_kebab = get_template("parking-lot")
    assert tmpl_kebab["title"] == "LLD - Parking Lot System"

    with pytest.raises(KeyError, match="Unknown template"):
        get_template("nonexistent_pattern")


def test_render_kroki_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<svg>mock diagram</svg>"

    with patch("requests.post", return_value=mock_response) as mock_post:
        result = render_kroki("class A", diagram_type="plantuml", output_format="svg")
        assert result == b"<svg>mock diagram</svg>"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://kroki.io/plantuml/svg"
        assert kwargs["data"] == b"class A"
        assert kwargs["headers"]["Content-Type"] == "text/plain; charset=utf-8"


def test_render_kroki_error_response():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Syntax error on line 2"

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(KrokiError, match="Kroki rendering failed \\(400\\): Syntax error"):
            render_kroki("broken syntax")


def test_render_kroki_network_exception():
    import requests
    with patch("requests.post", side_effect=requests.ConnectionError("Connection refused")):
        with pytest.raises(KrokiError, match="Network error while connecting"):
            render_kroki("class A")


def test_cli_list_templates(capsys):
    exit_code = main(["--template", "list"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Available LLD templates:" in captured.out
    assert "strategy" in captured.out


def test_cli_generate_template_plantuml(capsys):
    exit_code = main(["--template", "strategy", "--format", "plantuml"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "@startuml" in captured.out
    assert "PaymentStrategy" in captured.out
    assert "@enduml" in captured.out


def test_cli_generate_mermaid_from_text(capsys):
    exit_code = main(["--text", "Order composes Item\nItem is-a Product", "--format", "mermaid"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "classDiagram" in captured.out
    assert "Order *-- Item" in captured.out
    assert "Item --|> Product" in captured.out


def test_cli_kroki_url_generation(capsys):
    exit_code = main(["--text", "class User", "--kroki-url"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("https://kroki.io/plantuml/svg/")


def test_cli_render_kroki(capsys):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<svg>rendered</svg>"

    with patch("requests.post", return_value=mock_response):
        with patch("sys.stdout.buffer.write") as mock_buf_write:
            exit_code = main(["--text", "class Foo", "--render", "svg"])
            assert exit_code == 0
            mock_buf_write.assert_called_once_with(b"<svg>rendered</svg>")


def test_cli_file_input(tmp_path):
    input_file = tmp_path / "diagram.txt"
    input_file.write_text("class DatabaseConnection\nDatabaseConnection has-a Config", encoding="utf-8")

    output_file = tmp_path / "output.puml"
    exit_code = main(["-i", str(input_file), "-o", str(output_file)])
    assert exit_code == 0
    content = output_file.read_text(encoding="utf-8")
    assert "@startuml" in content
    assert "DatabaseConnection o-- Config" in content


def test_cli_empty_input(capsys):
    exit_code = main(["--text", "   "])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Diagram description is empty" in captured.err
