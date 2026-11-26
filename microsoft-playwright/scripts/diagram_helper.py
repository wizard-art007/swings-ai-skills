"""
diagram_helper.py

A small, offline Python helper that mirrors Playwright-inspired architectural patterns
(such as fluent builders, explicit wait/retry policies, and declarative specs/fixtures)
applied to text-based diagram generation and validation.
"""

import time
from typing import List, Dict, Any, Callable


class TimeoutError(Exception):
    """Raised when an operation exceeds its allotted retry/wait time."""
    pass


class RetryPolicy:
    """Configures retry behavior with backoff, mirroring robust web automation waits."""
    def __init__(self, retries: int = 3, delay: float = 0.01):
        self.retries = retries
        self.delay = delay


class DiagramBuilder:
    """
    A fluent builder pattern for constructing text diagrams, 
    inspired by Playwright's fluent method chaining API.
    """
    def __init__(self, title: str = "Diagram"):
        self._title = title
        self._nodes: List[str] = []
        self._connections: List[tuple[str, str]] = []
        self._metadata: Dict[str, Any] = {}

    def add_node(self, node_name: str) -> 'DiagramBuilder':
        cleaned = node_name.strip()
        if cleaned and cleaned not in self._nodes:
            self._nodes.append(cleaned)
        return self

    def connect(self, source: str, target: str) -> 'DiagramBuilder':
        self._nodes_must_exist(source, target)
        edge = (source, target)
        if edge not in self._connections:
            self._connections.append(edge)
        return self

    def set_metadata(self, key: str, value: Any) -> 'DiagramBuilder':
        self._metadata[key] = value
        return self

    def _nodes_must_exist(self, *names: str) -> None:
        for name in names:
            if name not in self._nodes:
                raise ValueError(f"Node '{name}' must be added before connecting.")

    def build(self) -> Dict[str, Any]:
        """Returns the compiled diagram representation."""
        return {
            "title": self._title,
            "nodes": list(self._nodes),
            "connections": list(self._connections),
            "metadata": dict(self._metadata)
        }


class DiagramEvaluator:
    """
    Evaluates diagram structures with built-in retry and auto-waiting semantics,
    mirroring Playwright's web-first assertions and polling mechanisms.
    """
    def __init__(self, policy: RetryPolicy | None = None):
        self.policy = policy or RetryPolicy()

    def wait_for_condition(self, condition: Callable[[], bool]) -> bool:
        """Repeatedly evaluates a condition until True or retries are exhausted."""
        attempts = 0
        while attempts <= self.policy.retries:
            if condition():
                return True
            attempts += 1
            if attempts <= self.policy.retries:
                time.sleep(self.policy.delay)
        raise TimeoutError(f"Condition not met after {self.policy.retries} retries.")

    def assert_node_count(self, diagram: Dict[str, Any], expected_count: int) -> bool:
        """Asserts node count with retry semantics (useful for async/dynamic rendering)."""
        def check():
            return len(diagram.get("nodes", [])) == expected_count

        return self.wait_for_condition(check)


class DiagramPageObject:
    """
    A Page Object Model pattern encapsulating diagram operations and assertions
    for clean test-case generation and maintainability.
    """
    def __init__(self, title: str = "Workflow"):
        self.builder = DiagramBuilder(title)
        self.evaluator = DiagramEvaluator()

    def create_basic_flow(self, steps: List[str]) -> Dict[str, Any]:
        for step in steps:
            self.builder.add_node(step)
        
        for i in range(len(steps) - 1):
            self.builder.connect(steps[i], steps[i+1])
            
        diagram = self.builder.build()
        self.evaluator.assert_node_count(diagram, len(steps))
        return diagram
