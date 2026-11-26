import sys
import os
import pytest

# Ensure scripts/ is importable without network access or complex path setups
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from diagram_helper import (
    DiagramBuilder,
    DiagramEvaluator,
    DiagramPageObject,
    RetryPolicy,
    TimeoutError
)


def test_fluent_diagram_builder():
    """Test the fluent builder pattern for adding nodes and connections."""
    diagram = (
        DiagramBuilder("System Architecture")
        .add_node("Client")
        .add_node("API Gateway")
        .add_node("Database")
        .connect("Client", "API Gateway")
        .connect("API Gateway", "Database")
        .set_metadata("env", "staging")
        .build()
    )

    assert diagram["title"] == "System Architecture"
    assert diagram["nodes"] == ["Client", "API Gateway", "Database"]
    assert diagram["connections"] == [("Client", "API Gateway"), ("API Gateway", "Database")]
    assert diagram["metadata"]["env"] == "staging"


def test_builder_missing_node_validation():
    """Test that connecting non-existent nodes raises ValueError immediately."""
    builder = DiagramBuilder()
    builder.add_node("Start")
    
    with pytest.raises(ValueError, match="Node 'End' must be added before connecting"):
        builder.connect("Start", "End")


def test_evaluator_wait_for_condition_success():
    """Test that the evaluator successfully retries until a condition becomes True."""
    counter = {"attempts": 0}

    def flaky_condition():
        counter["attempts"] += 1
        return counter["attempts"] >= 3

    evaluator = DiagramEvaluator(RetryPolicy(retries=5, delay=0.001))
    result = evaluator.wait_for_condition(flaky_condition)
    
    assert result is True
    assert counter["attempts"] == 3


def test_evaluator_wait_for_condition_timeout():
    """Test that TimeoutError is raised when retries are exhausted."""
    def never_true():
        return False

    evaluator = DiagramEvaluator(RetryPolicy(retries=2, delay=0.001))
    
    with pytest.raises(TimeoutError, match="Condition not met after 2 retries"):
        evaluator.wait_for_condition(never_true)


def test_diagram_page_object_workflow():
    """Test the Page Object Model pattern helper for end-to-end diagram generation."""
    pom = DiagramPageObject("Deployment Pipeline")
    steps = ["Commit", "Test", "Build", "Deploy"]
    
    diagram = pom.create_basic_flow(steps)

    assert diagram["title"] == "Deployment Pipeline"
    assert diagram["nodes"] == steps
    assert len(diagram["connections"]) == 3
    assert diagram["connections"][0] == ("Commit", "Test")
