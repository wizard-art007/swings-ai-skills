"""
Midscene-inspired offline simulator helper for natural-language E2E test cases,
assertions, and AI action step logging.
"""

import json
from typing import Dict, List, Any, Optional

class MidsceneSimulator:
    """Simulates vision-driven natural language E2E testing steps offline."""
    
    def __init__(self, target_url: str = "https://example.com") -> None:
        self.target_url = target_url
        self.history: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {"page": target_url, "elements": [], "visible": True}

    def goto_url(self, url: str) -> Dict[str, Any]:
        self.target_url = url
        self.state["page"] = url
        record = {"action": "gotoUrl", "url": url, "status": "success"}
        self.history.append(record)
        return record

    def ai_act(self, instruction: str) -> Dict[str, Any]:
        """Simulate a natural language UI interaction command."""
        if not instruction or not isinstance(instruction, str):
            raise ValueError("Instruction must be a non-empty string")
        
        simulated_effect = f"Executed action based on: {instruction}"
        self.state["last_action"] = instruction
        record = {"action": "aiAct", "instruction": instruction, "result": simulated_effect, "status": "success"}
        self.history.append(record)
        return record

    def ai_wait_for(self, condition: str) -> Dict[str, Any]:
        """Simulate waiting for a natural language condition on screen."""
        if not condition or not isinstance(condition, str):
            raise ValueError("Condition must be a non-empty string")
            
        record = {"action": "aiWaitFor", "condition": condition, "satisfied": True, "status": "success"}
        self.history.append(record)
        return record

    def ai_assert(self, assertion: str) -> bool:
        """Simulate a vision assertion in natural language."""
        if not assertion or not isinstance(assertion, str):
            raise ValueError("Assertion must be a non-empty string")
            
        passed = len(assertion) > 0
        record = {"action": "aiAssert", "assertion": assertion, "passed": passed, "status": "success"}
        self.history.append(record)
        return passed

    def run_yaml_suite(self, suite_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run a parsed YAML-like suite dict containing setup and cases."""
        results = []
        before_each = suite_data.get("beforeEach", [])
        cases = suite_data.get("cases", [])

        for step in before_each:
            if "gotoUrl" in step:
                self.goto_url(step["gotoUrl"])

        for case in cases:
            case_name = case.get("name", "Unnamed case")
            case_results = {"name": case_name, "steps": []}
            for step in case.get("steps", []):
                if "aiAct" in step:
                    res = self.ai_act(step["aiAct"])
                    case_results["steps"].append(res)
                elif "aiWaitFor" in step:
                    res = self.ai_wait_for(step["aiWaitFor"])
                    case_results["steps"].append(res)
                elif "aiAssert" in step:
                    passed = self.ai_assert(step["aiAssert"])
                    case_results["steps"].append({"action": "aiAssert", "passed": passed})
            results.append(case_results)
        return results

    def export_report(self) -> str:
        return json.dumps(self.history, indent=2)
