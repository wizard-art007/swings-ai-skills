import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "scripts")
import c4_plantuml_generator


def test_text_to_spec_parsing():
    sample_text = """
    title: Online Banking System
    type: container
    remote_include: true

    person: user, Customer, A customer of the bank
    system_ext: core_bank, Core Banking, Main legacy banking system
    container: web_app, Web App, React, Front-end interface
    container_db: db, Database, PostgreSQL, User data store

    rel: user, web_app, Uses, HTTPS
    web_app -> db: Reads/Writes (SQL)
    """

    spec = c4_plantuml_generator.text_to_spec(sample_text)

    assert spec["title"] == "Online Banking System"
    assert spec["type"] == "container"
    assert spec["remote_include"] is True
    assert len(spec["elements"]) == 4
    assert spec["elements"][0] == {
        "kind": "person",
        "alias": "user",
        "label": "Customer",
        "desc": "A customer of the bank",
    }
    assert len(spec["relations"]) == 2
    assert spec["relations"][0] == {
        "kind": "rel",
        "from": "user",
        "to": "web_app",
        "label": "Uses",
        "tech": "HTTPS",
    }
    assert spec["relations"][1] == {
        "kind": "rel",
        "from": "web_app",
        "to": "db",
        "label": "Reads/Writes",
        "tech": "SQL",
    }


def test_generate_plantuml_context():
    text = """
    title: Store System
    type: context
    person: customer, Customer, Purchases products
    system: store, Online Store, E-commerce system
    rel: customer, store, Places order
    """
    puml = c4_plantuml_generator.generate_plantuml(text)

    assert "@startuml" in puml
    assert "!include <C4/C4_Context>" in puml
    assert 'title Store System' in puml
    assert "LAYOUT_WITH_LEGEND()" in puml
    assert 'Person(customer, "Customer", "Purchases products")' in puml
    assert 'System(store, "Online Store", "E-commerce system")' in puml
    assert 'Rel(customer, store, "Places order")' in puml
    assert "@enduml" in puml


def test_generate_plantuml_container_remote():
    spec = {
        "title": "Payment Container Diagram",
        "type": "container",
        "remote_include": True,
        "elements": [
            {
                "kind": "container",
                "alias": "api",
                "label": "API Service",
                "tech": "Go",
                "desc": "Handles payments",
            },
            {
                "kind": "container_db",
                "alias": "db",
                "label": "Payment DB",
                "tech": "PostgreSQL",
            },
        ],
        "relations": [
            {"kind": "rel", "from": "api", "to": "db", "label": "Queries", "tech": "SQL"}
        ],
    }

    puml = c4_plantuml_generator.generate_plantuml(spec)

    assert "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml" in puml
    assert 'Container(api, "API Service", "Go", "Handles payments")' in puml
    assert 'ContainerDb(db, "Payment DB", "PostgreSQL")' in puml
    assert 'Rel(api, db, "Queries", "SQL")' in puml


def test_generate_plantuml_invalid_input():
    with pytest.raises(ValueError):
        c4_plantuml_generator.generate_plantuml(12345)


def test_encode_kroki_url():
    puml = "@startuml\n!include <C4/C4_Context>\n@enduml"
    url = c4_plantuml_generator.encode_kroki_url(puml, output_format="png", kroki_url="https://kroki.example.com")

    assert url.startswith("https://kroki.example.com/plantuml/png/")
    encoded_part = url.split("https://kroki.example.com/plantuml/png/")[1]
    assert len(encoded_part) > 0


@patch("requests.post")
def test_render_kroki_success(mock_post):
    mock_response = MagicMock()
    mock_response.content = b"<svg>Mocked SVG Output</svg>"
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    puml = "@startuml\n!include <C4/C4_Context>\n@enduml"
    result = c4_plantuml_generator.render_kroki(
        puml, output_format="svg", kroki_url="https://kroki.io"
    )

    assert result == b"<svg>Mocked SVG Output</svg>"
    mock_post.assert_called_once_with(
        "https://kroki.io/plantuml/svg",
        data=puml.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        timeout=10,
    )
