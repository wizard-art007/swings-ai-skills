import sys
import os
import pytest

# Ensure scripts/ is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from taste_checker import TasteChecker


def test_taste_checker_clean_markup():
    clean_html = """
    <div class="max-w-7xl mx-auto px-6">
        <h1>Design systems for modern engineering teams.</h1>
        <p>Build software with precision and speed.</p>
    </div>
    """
    checker = TasteChecker(clean_html)
    result = checker.evaluate()

    assert result["passed"] is True
    assert result["score"] == 100
    assert result["slop_terms_found"] == []
    assert result["has_proper_alignment"] is True


def test_taste_checker_detects_slop():
    slopy_html = """
    <div class="container">
        <h1>Supercharge your workflow and revolutionize how you build.</h1>
        <p>Unlock the power of cutting-edge AI seamlessly integrated.</p>
    </div>
    """
    checker = TasteChecker(slopy_html)
    result = checker.evaluate()

    assert result["passed"] is False
    assert len(result["slop_terms_found"]) > 0
    assert "supercharge" in result["slop_terms_found"]
    assert "revolutionize" in result["slop_terms_found"]
    assert result["score"] < 70


def test_taste_checker_missing_alignment():
    unaligned_html = """
    <div>
        <h1>Plain copy text here.</h1>
    </div>
    """
    checker = TasteChecker(unaligned_html)
    result = checker.evaluate()

    assert result["has_proper_alignment"] is False
    assert result["score"] <= 70
