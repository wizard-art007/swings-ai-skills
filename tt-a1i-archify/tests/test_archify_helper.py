import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, "scripts")

from archify_helper import (
    text_to_mermaid,
    text_to_plantuml,
    generate_diagram,
    encode_kroki_url,
    render_kroki,
)
import requests


class TestArchifyHelper(unittest.TestCase):
    def test_text_to_mermaid_flowchart(self):
        desc = "A -> B\nB -> C"
        res = text_to_mermaid(desc, "flowchart")
        self.assertIn("graph TD", res)
        self.assertIn("A -> B", res)
        self.assertIn("B -> C", res)

    def test_text_to_mermaid_empty(self):
        res = text_to_mermaid("", "flowchart")
        self.assertIn("Empty Diagram", res)

    def test_text_to_mermaid_sequence(self):
        desc = "Client -> Server: Request\nServer -> Database: Query"
        res = text_to_mermaid(desc, "sequence")
        self.assertIn("sequenceDiagram", res)
        self.assertIn("Client -> Server: Request", res)

    def test_text_to_plantuml(self):
        desc = "Alice -> Bob: Hello\nBob -> Alice: Hi"
        res = text_to_plantuml(desc, "sequence")
        self.assertTrue(res.startswith("@startuml"))
        self.assertTrue(res.endswith("@enduml"))
        self.assertIn("Alice -> Bob: Hello", res)

    def test_generate_diagram(self):
        puml = generate_diagram("A -> B", engine="plantuml")
        self.assertIn("@startuml", puml)

        mrm = generate_diagram("A -> B", engine="mermaid")
        self.assertIn("graph TD", mrm)

    def test_encode_kroki_url(self):
        source = "graph TD\n  A --> B"
        url = encode_kroki_url(source, diagram_type="mermaid", output_format="svg")
        self.assertTrue(url.startswith("https://kroki.io/mermaid/svg/"))
        self.assertNotIn(" ", url)

    @patch("requests.post")
    def test_render_kroki_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = b"<svg>Mock Diagram</svg>"
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        source = "graph TD\n  A --> B"
        content = render_kroki(source, diagram_type="mermaid", output_format="svg")

        self.assertEqual(content, b"<svg>Mock Diagram</svg>")
        mock_post.assert_called_once_with(
            "https://kroki.io/mermaid/svg",
            data=source.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8"},
            timeout=10.0,
        )

    @patch("requests.post")
    def test_render_kroki_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error")
        mock_post.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError):
            render_kroki("invalid diagram", diagram_type="mermaid")


if __name__ == "__main__":
    unittest.main()
