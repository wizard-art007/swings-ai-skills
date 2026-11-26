import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Ensure scripts/ is in sys.path as required
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from skill_diagram import text_to_diagram, render_via_kroki

def test_text_to_diagram_cdp():
    desc = "Run a script with CDP mode to bypass Cloudflare stealth."
    diagram = text_to_diagram(desc)
    assert "graph TD" in diagram
    assert "sb_cdp.Chrome" in diagram
    assert "Cloudflare" in diagram

def test_text_to_diagram_pytest():
    desc = "Execute end-to-end testing using pytest and SeleniumBase."
    diagram = text_to_diagram(desc)
    assert "graph TD" in diagram
    assert "Pytest Suite" in diagram

def test_text_to_diagram_default():
    desc = "Custom scraping workflow."
    diagram = text_to_diagram(desc)
    assert "graph TD" in diagram
    assert "Custom scraping workflow." in diagram

@patch('skill_diagram.requests.get')
def test_render_via_kroki_success(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    diagram_src = "graph TD\nA-->B"
    url = render_via_kroki(diagram_src, diagram_type="mermaid", format_type="svg")
    
    assert url.startswith("https://kroki.io/mermaid/svg/")
    mock_get.assert_called_once()
