import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure scripts/ is in sys.path as required by rules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from next_ai_draw_io_helper import text_to_diagram_source, render_diagram


class TestNextAiDrawIoHelper(unittest.TestCase):

    def test_text_to_diagram_source_flowchart(self):
        desc = "Create an architecture diagram for an AI system"
        source = text_to_diagram_source(desc)
        self.assertIn("graph TD", source)
        self.assertIn("User Input", source)

    def test_text_to_diagram_source_sequence(self):
        desc = "A sequence diagram for user login"
        source = text_to_diagram_source(desc)
        self.assertIn("sequenceDiagram", source)
        self.assertIn("autonumber", source)

    def test_text_to_diagram_source_class(self):
        desc = "Class diagram for our data models"
        source = text_to_diagram_source(desc)
        self.assertIn("classDiagram", source)
        self.assertIn("class DiagramGenerator", source)

    def test_text_to_diagram_source_invalid(self):
        with self.assertRaises(ValueError):
            text_to_diagram_source("")
        with self.assertRaises(ValueError):
            text_to_diagram_source(None)

    @patch('next_ai_draw_io_helper.requests.get')
    def test_render_diagram_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<svg>mocked svg</svg>"
        mock_get.return_value = mock_response

        source = "graph TD\n    A --> B"
        result = render_diagram(source, "svg")
        
        self.assertEqual(result, "<svg>mocked svg</svg>")
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertTrue(called_url.startswith("https://kroki.io/mermaid/svg/"))

    @patch('next_ai_draw_io_helper.requests.get')
    def test_render_diagram_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500")
        mock_get.return_value = mock_response

        source = "graph TD\n    A --> B"
        with self.assertRaises(RuntimeError):
            render_diagram(source)

    def test_render_diagram_invalid_source(self):
        with self.assertRaises(ValueError):
            render_diagram("")
        with self.assertRaises(ValueError):
            render_diagram(None)


if __name__ == '__main__':
    unittest.main()
