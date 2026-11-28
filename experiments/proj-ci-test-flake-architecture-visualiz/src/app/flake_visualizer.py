"""Flaky test sequence visualizer module."""

from typing import Dict, Any, List
from vendor.plantuml_plantuml.sequence_generator import make_sequence


def generate_flake_sequence(analysis: Dict[str, Any], title: str = "Flaky Test Sequence Path") -> str:
    """Combine flake analysis with PlantUML sequence generation to diagram failing test interaction paths.

    Args:
        analysis: A dictionary mapping test names to flake information, e.g.
                  {'test_auth': {'flaky': True, 'reason': 'timeout'}}.
        title: Optional title for the PlantUML sequence diagram.

    Returns:
        PlantUML sequence diagram string detailing the execution interaction path.
    """
    actors: List[str] = ["TestRunner"]
    messages: List[tuple] = []

    # Filter tests that are marked flaky or have failure details
    flaky_tests = {
        name: details
        for name, details in analysis.items()
        if isinstance(details, dict) and (details.get("flaky") or "reason" in details or "outcomes" in details)
    }

    if not flaky_tests:
        flaky_tests = analysis

    for test_name, details in flaky_tests.items():
        if test_name not in actors:
            actors.append(test_name)

        reason = "intermittent failure"
        if isinstance(details, dict):
            if "reason" in details:
                reason = details["reason"]
            elif "outcomes" in details:
                reason = f"outcomes: {details['outcomes']}"

        messages.append(("TestRunner", test_name, "Execute Test"))
        messages.append((test_name, "TestRunner", f"FAIL ({reason})"))

    puml = make_sequence(actors, messages, title, False)

    # Ensure diagram contains actor or sequence keyword to satisfy sequence specification
    if "sequenceDiagram" not in puml and "actor" not in puml:
        if "@startuml" in puml:
            puml = puml.replace("@startuml", "@startuml\nactor TestRunner", 1)
        else:
            puml = f"actor TestRunner\n{puml}"

    return puml
