import sys
import os
import pytest

# Ensure scripts/ is in sys.path as required by rules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from aas_planner import AASPlanner


@pytest.fixture
def sample_catalog():
    return [
        {
            "name": "claude-code-runner",
            "description": "Run coding tasks using Claude Code workflows",
            "topics": ["claude-code", "ai-coding"]
        },
        {
            "name": "cursor-sync",
            "description": "Synchronize rules and context for Cursor agent",
            "topics": ["cursor", "developer-tools"]
        },
        {
            "name": "flaky-detector",
            "description": "Detect flaky tests and patterns in test automation suites",
            "topics": ["qa", "test-automation"]
        }
    ]


def test_search_catalog(sample_catalog):
    planner = AASPlanner(sample_catalog)
    results = planner.search_catalog("cursor")
    assert len(results) == 1
    assert results[0]["name"] == "cursor-sync"

    results_topic = planner.search_catalog("ai-coding")
    assert len(results_topic) == 1
    assert results_topic[0]["name"] == "claude-code-runner"


def test_select_skill(sample_catalog):
    planner = AASPlanner(sample_catalog)
    success = planner.select_skill("claude-code-runner")
    assert success is True
    assert len(planner.selected_skills) == 1
    assert planner.selected_skills[0]["name"] == "claude-code-runner"

    # Selecting non-existent skill
    fail = planner.select_skill("non-existent")
    assert fail is False
    assert len(planner.selected_skills) == 1


def test_preview_plan(sample_catalog):
    planner = AASPlanner(sample_catalog)
    planner.select_skill("claude-code-runner")
    planner.select_skill("flaky-detector")

    plan = planner.preview_plan("Refactor test suite and fix flake")
    assert plan["task"] == "Refactor test suite and fix flake"
    assert plan["selected_skill_count"] == 2
    assert len(plan["steps"]) == 2
    assert plan["steps"][0]["skill"] == "claude-code-runner"
    assert plan["steps"][1]["skill"] == "flaky-detector"
    assert plan["status"] == "ready_for_execution"


def test_execute_with_fake_llm(sample_catalog):
    planner = AASPlanner(sample_catalog)
    planner.select_skill("cursor-sync")

    def fake_llm(prompt: str) -> str:
        return f"LLM_RESPONSE: SUCCESS for prompt length {len(prompt)}"

    response = planner.execute_with_llm(fake_llm, "Sync settings across environments")
    assert "LLM_RESPONSE: SUCCESS" in response
