import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Ensure scripts/ is in sys.path without using os.system or subprocess
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts"))
)

import tbls_helper


def test_generate_mermaid_er():
    tables = [
        {
            "name": "users",
            "columns": [
                {"name": "id", "type": "int"},
                {"name": "email", "type": "string"},
            ],
        },
        {
            "name": "orders",
            "columns": [
                {"name": "id", "type": "int"},
                {"name": "user_id", "type": "int"},
            ],
            "relations": [
                {"parent": "users", "cardinality": "||--o{", "label": "places"}
            ],
        },
    ]

    result = tbls_helper.generate_mermaid_er(tables)
    assert "erDiagram" in result
    assert "users {" in result
    assert "int id" in result
    assert "orders {" in result
    assert "users ||--o{ orders : places" in result


def test_generate_plantuml_er():
    tables = [
        {
            "name": "accounts",
            "columns": [
                {
                    "name": "id",
                    "type": "bigint",
                    "primary_key": True,
                },
                {"name": "name", "type": "varchar"},
            ],
        }
    ]

    result = tbls_helper.generate_plantuml_er(tables)
    assert "@startuml" in result
    assert 'entity "accounts" {' in result
    assert "bigint * id" in result
    assert "@enduml" in result


@patch("tbls_helper.requests.get")
def test_render_via_kroki_offline(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<svg>mocked svg</svg>"
    mock_get.return_value = mock_response

    source = "erDiagram\n    A ||--o{ B : has"
    res = tbls_helper.render_via_kroki(source, "mermaid", "svg")

    assert res == "<svg>mocked svg</svg>"
    mock_get.assert_called_once()
    called_url = mock_get.call_args[0][0]
    assert called_url.startswith("https://kroki.io/mermaid/svg/")
