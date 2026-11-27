"""
Anchor Security Linter Heuristic (AnchorSecLint)
A lightweight static analysis tool for Solana/Anchor smart contract source code 
to detect missing signer validation, unchecked accounts, and unconstrained mutations.
"""

import re
import sys
from typing import List, Dict, Any

class SecurityFinding:
    def __init__(self, rule_id: str, severity: str, message: str, line_number: int):
        self.rule_id = rule_id
        self.severity = severity
        self.message = message
        self.line_number = line_number

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "line_number": self.line_number
        }

class AnchorSecLinter:
    def __init__(self):
        # Rules detecting common Anchor security pitfalls
        self.rules = [
            {
                "id": "SEC-001",
                "severity": "HIGH",
                "pattern": r"pub\s+\w+\s*:\s*UncheckedAccount",
                "message": "Use of UncheckedAccount without explicit manual validation bypasses Anchor's safety guarantees."
            },
            {
                "id": "SEC-002",
                "severity": "CRITICAL",
                "pattern": r"pub\s+(\w+)\s*:\s*AccountInfo\b",
                "message": "Raw AccountInfo used. Ensure owner and signer checks are manually enforced in instruction logic."
            },
            {
                "id": "SEC-003",
                "severity": "MEDIUM",
                "pattern": r"#\[account\(mut\)\]\s*\n\s*pub\s+\w+\s*:\s*Account\s*<",
                "message": "Mutable account found. Verify that the signer constraint #[account(signer)] or authority check is present."
            },
            {
                "id": "SEC-004",
                "severity": "HIGH",
                "pattern": r"ctx\.accounts\.\w+\.key\(\)\s*!=\s*",
                "message": "Manual key inequality comparison detected; prefer Anchor constraint attributes like `has_one` or `constraint`."
            }
        ]

    def lint_source(self, source_code: str) -> List[SecurityFinding]:
        findings: List[SecurityFinding:] = []
        lines = source_code.splitlines()

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue

            for rule in self.rules:
                # Multi-line or single-line match check
                if re.search(rule["pattern"], line):
                    findings.append(SecurityFinding(
                        rule_id=rule["id"],
                        severity=rule["severity"],
                        message=rule["message"],
                        line_number=idx
                    ))

        return findings

def analyze_code(source_code: str) -> List[Dict[str, Any]]:
    linter = AnchorSecLinter()
    findings = linter.lint_source(source_code)
    return [f.to_dict() for f in findings]
