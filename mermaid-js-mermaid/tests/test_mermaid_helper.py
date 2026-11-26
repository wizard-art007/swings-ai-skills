import sys
import unittest
from unittest.mock import patch

# Setup path to import scripts
sys.path.insert(0, 'scripts')
import mermaid_helper

class TestMermaidHelper(unittest.TestCase):

    def test_text_to_mermaid_flow(self):
        result = mermaid_helper.text_to_mermaid("Process data")
        self.assertIn("graph TD", result)
        self.assertIn("Process data", result)

    def test_kroki_url_generation(self):
        source = "graph TD\n    A-->B"
        url = mermaid_helper.get_kroki_url(source)
        self.assertTrue(url.startswith("https://kroki.io/mermaid/svg/"))
        # Ensure encoding doesn't contain forbidden chars
        self.assertNotIn("+", url.split("/")[-1])
        self.assertNotIn("=", url.split("/")[-1])

    @patch('requests.get')
    def test_fetch_diagram_mocked(self, mock_get):
        mock_get.return_value.text = "<svg>Test</svg>"
        mock_get.return_value.raise_for_status.return_value = None
        
        url = "https://kroki.io/mermaid/svg/test"
        svg = mermaid_helper.fetch_diagram(url)
        
        self.assertEqual(svg, "<svg>Test</svg>")
        mock_get.assert_called_once_with(url, timeout=10)

if __name__ == '__main__':
    unittest.main()
