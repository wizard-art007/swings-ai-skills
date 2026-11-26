"""
A small offline Python helper embodying the Leonxlnx Taste Skill core technique:
Evaluating frontend design compliance and anti-slop rules using structured checking.
"""

import json
from typing import Dict, Any, List


class TasteChecker:
    """Evaluates HTML/UI text structure against high-end design taste rules."""

    ANTIPATTERNS = [
        "supercharge",
        "revolutionize",
        "seamlessly integrate",
        "cutting-edge",
        "dive into",
        "unlock the power",
    ]

    def __init__(self, markup: str):
        self.markup = markup.lower()

    def check_plain_copy(self) -> List[str]:
        """Detects cliché marketing buzzwords (AI slop)."""
        found = []
        for term in self.ANTIPATTERNS:
            if term in self.markup:
                found.append(term)
        return found

    def check_structural_alignment(self) -> bool:
        """Verifies basic container alignment classes or structural edges."""
        # Simple check for modern layout classes like max-w or container structures
        has_container = "max-w-" in self.markup or "container" in self.markup
        return has_container

    def evaluate(self) -> Dict[str, Any]:
        """Runs all taste checks and returns a summary report."""
        slop_terms = self.check_plain_copy()
        has_alignment = self.check_structural_alignment()

        score = 100
        score -= len(slop_terms) * 15
        if not has_alignment:
            score -= 30

        score = max(0, score)

        passed = score >= 70 and not slop_terms

        return {
            "score": score,
            "passed": passed,
            "slop_terms_found": slop_terms,
            "has_proper_alignment": has_alignment,
        }
