import sys
import os
import pytest

# Ensure scripts/ is in sys.path as requested
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import diagram_helper


def test_text_to_mermaid_basic():
    desc = "Run Playwright tests across browsers"
    mermaid_code = diagram_helper.text_to_mermaid(desc)
    assert "graph TD" in mermaid_code
    assert "Playwright" in mermaid_code


def test_text_to_mermaid_arrow_syntax():
    desc = "Init Project -> Run Tests -> Generate Report"
    mermaid_code = diagram_helper.text_to_mermaid(desc)
    assert "graph TD" in mermaid_code
    assert "Init Project" in mermaid_code
    assert "Run Tests" in mermaid_code
    assert "Generate Report" in mermaid_code
    assert "Step1 --> Step2" in mermaid_code


def test_text_to_mermaid_empty():
    mermaid_code = diagram_helper.text_to_mermaid("")
    assert "graph TD" in mermaid_code
    assert "Start" in mermaid_code


def test_get_kroki_url():
    source = "graph TD\nA-->B"
    url = diagram_helper.get_kroki_url(source, diagram_type="mermaid", format="svg")
    assert url.startswith("https://kroki.io/mermaid/svg/")
    assert len(url) > len("https://kroki.io/mermaid/svg/")


def test_render_via_kroki_mocked(monkeypatch):
    class MockResponse:
        status_code = 200
        text = "<svg>mocked</svg>"
        def raise_for_status(self):
            pass

    def mock_post(url, json=None, timeout=10):
        return MockResponse()

    monkeypatch.setattr(diagram_helper.requests, "post", mock_post)

    result = diagram_helper.render_via_kroki("graph TD\nA-->B")
    assert result == "<svg>mocked</svg>"
