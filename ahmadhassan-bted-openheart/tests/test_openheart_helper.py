import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure scripts directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from openheart_helper import OpenHeartDiagramHelper


class TestOpenHeartDiagramHelper(unittest.TestCase):
    def setUp(self):
        self.helper = OpenHeartDiagramHelper()

    def test_generate_plantuml_default(self):
        desc = "Analyze Java Control Flow Graph"
        source = self.helper.generate_diagram_source(desc, "plantuml")
        self.assertIn("@startuml", source)
        self.assertIn("@enduml", source)
        self.assertIn(desc, source)

    def test_generate_mermaid(self):
        desc = "Call graph extraction"
        source = self.helper.generate_diagram_source(desc, "mermaid")
        self.assertIn("graph TD;", source)
        self.assertIn(desc, source)

    def test_generate_dot(self):
        desc = "SSA generation"
        source = self.helper.generate_diagram_source(desc, "dot")
        self.assertIn("digraph", source)
        self.assertIn(desc, source)

    @patch('requests.post')
    def test_render_via_kroki_mock(self, mock_post):
        # Mock the requests.post response to ensure no network access is performed
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<svg>mocked svg</svg>"
        mock_post.return_value = mock_response

        diagram_src = "@startuml\nA -> B\n@enduml"
        result = self.helper.render_via_kroki(diagram_src, "plantuml", "svg")

        self.assertEqual(result, "<svg>mocked svg</svg>")
        mock_post.assert_called_once()
        
        # Verify call parameters
        args, kwargs = mock_post.call_args
        self.assertIn("https://kroki.io/plantuml/svg", args[0])
        self.assertEqual(kwargs['data'], diagram_src.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
