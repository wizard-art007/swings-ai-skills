import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure scripts directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from gitdiagram_helper import text_to_mermaid, render_mermaid_kroki

class TestGitDiagramHelper(unittest.TestCase):
    
    def test_text_to_mermaid_default(self):
        desc = "Visualize a GitHub repository architecture"
        mermaid = text_to_mermaid(desc)
        self.assertIn("graph TD", mermaid)
        self.assertIn("GitDiagram", mermaid)

    def test_text_to_mermaid_sequence(self):
        desc = "Show the interaction sequence between client and API"
        mermaid = text_to_mermaid(desc)
        self.assertIn("sequenceDiagram", mermaid)
        self.assertIn("Client", mermaid)

    def test_text_to_mermaid_class(self):
        desc = "Class structure of the repository and diagram generator"
        mermaid = text_to_mermaid(desc)
        self.assertIn("classDiagram", mermaid)
        self.assertIn("Repository", mermaid)

    def test_text_to_mermaid_empty(self):
        with self.assertRaises(ValueError):
            text_to_mermaid("")
        with self.assertRaises(ValueError):
            text_to_mermaid("   ")

    @patch('gitdiagram_helper.requests.get')
    def test_render_mermaid_kroki(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<svg>test</svg>"
        mock_get.return_value = mock_response

        mermaid_code = "graph TD\nA-->B"
        result = render_mermaid_kroki(mermaid_code, "svg")
        
        self.assertEqual(result, b"<svg>test</svg>")
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertTrue(called_url.startswith("https://kroki.io/mermaid/svg/"))

    def test_render_mermaid_kroki_empty(self):
        with self.assertRaises(ValueError):
            render_mermaid_kroki("")

if __name__ == '__main__':
    unittest.main()
