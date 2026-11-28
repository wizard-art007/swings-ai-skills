"""Offline simulator for the e2e-inc/e2e testing framework.

Captures agentic test execution, recorded step caching, fluent assertions,
and retry/wait mechanics for web/mobile automation specs without network calls.
"""

from typing import Any, Callable, Dict, List, Optional
import time


class Element:
    """Represents a DOM or UI element found on the screen."""

    def __init__(self, role: str, text: str = "", visible: bool = True):
        self.role = role
        self.text = text
        self.visible = visible


class Screen:
    """Inspects the current state of the application screen."""

    def __init__(self, elements: Optional[List[Element]] = None):
        self.elements = elements or []

    def get_by_role(self, role: str) -> "Locator":
        return Locator(self, role=role)


class Locator:
    """Locates elements and performs assertions on them."""

    def __init__(self, screen: Screen, role: str):
        self.screen = screen
        self.role = role

    def _find_matching(self) -> List[Element]:
        return [e for e in self.screen.elements if e.role == self.role and e.visible]

    def to_contain_text(self, expected_text: str) -> bool:
        matches = self._find_matching()
        if not matches:
            raise AssertionError(f"No visible element found with role '{self.role}'")
        for m in matches:
            if expected_text in m.text:
                return True
        raise AssertionError(
            f"Element with role '{self.role}' does not contain text '{expected_text}'. Found texts: {[m.text for m in matches]}"
        )


class Expect:
    """Fluent assertion helper matching Playwright / e2e style."""

    def __init__(self, screen: Screen):
        self.screen = screen

    def get_by_role(self, role: str) -> Locator:
        return self.screen.get_by_role(role)


class Agent:
    """Simulates an AI agent performing actions, assertions, and waits."""

    def __init__(self, app: "App", strict_cache: bool = False):
        self.app = app
        self.strict_cache = strict_cache
        self.recordings: Dict[str, str] = {}
        self.action_log: List[str] = []

    def record_action(self, description: str, result: str) -> None:
        self.recordings[description] = result

    _deterministic_rules: Dict[str, Callable[["App"], None]] = {}

    @classmethod
    def register_rule(cls, description_keyword: str, handler: Callable[["App"], None]) -> None:
        cls._deterministic_rules[description_keyword] = handler

    def act(self, instruction: str) -> str:
        self.action_log.append(f"act: {instruction}")
        
        # Check cache replay (strict cache mode)
        if instruction in self.recordings:
            res = self.recordings[instruction]
            # Execute registered state transition if available
            for kw, handler in self._deterministic_rules.items():
                if kw in instruction.lower():
                    handler(self.app)
            return f"Replayed: {res}"

        if self.strict_cache:
            raise RuntimeError(f"Strict cache enabled: no recording found for action '{instruction}'")

        # Execute live simulation behavior based on instruction keywords
        executed = False
        for kw, handler in self._deterministic_rules.items():
            if kw in instruction.lower():
                handler(self.app)
                executed = True
                break

        result = f"Executed live: {instruction}"
        self.recordings[instruction] = result
        if not executed:
            # Default state mutation simulation
            self.app.state["last_action"] = instruction
        return result

    def assert_cond(self, condition: str) -> bool:
        self.action_log.append(f"assert: {condition}")
        if condition in self.recordings:
            return True
        # Evaluate simple state assertions
        if "pro" in condition.lower():
            if self.app.state.get("plan") == "Pro":
                return True
            raise AssertionError(f"Agent assertion failed: {condition} (Current app state: {self.app.state})")
        return True

    def wait_for(self, condition: str, timeout_ms: int = 1000) -> bool:
        start = time.time()
        while (time.time() - start) * 1000 < timeout_ms:
            try:
                if self.assert_cond(condition):
                    return True
            except AssertionError:
                time.sleep(0.01)
        raise TimeoutError(f"Timeout waiting for condition: {condition}")


class App:
    """Represents the application under test."""

    def __init__(self, initial_route: str = "/"):
        self.current_route = initial_route
        self.state: Dict[str, Any] = {"plan": "Free"}
        self.elements: List[Element] = []

    def open(self, route: str) -> None:
        self.current_route = route
        if route == "/settings/billing":
            self.elements = [
                Element(role="status", text="Free Plan Active", visible=True),
                Element(role="button", text="Upgrade to Pro", visible=True)
            ]

    @property
    def screen(self) -> Screen:
        return Screen(self.elements)


# Register default UI behavior handlers
def _upgrade_handler(app: App) -> None:
    app.state["plan"] = "Pro"
    app.elements = [
        Element(role="status", text="Pro Plan Active", visible=True),
        Element(role="region", text="invoice preview shows a prorated amount", visible=True)
    ]

Agent.register__rule = Agent.register_rule
Agent.register_rule("upgrade", _upgrade_handler)
