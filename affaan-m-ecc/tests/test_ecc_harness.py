import sys
import pytest

sys.path.insert(0, "scripts")

from ecc_agent_harness import (
    ECCAgentHarness,
    AgentShield,
    InstinctStore,
    MemoryManager,
)


def mock_llm_calculator(prompt, history):
    return {
        "tool_name": "calculator",
        "tool_args": {"expression": "10 + 20"},
        "answer": "Calculating math expression...",
    }


def mock_llm_unsafe_tool(prompt, history):
    return {
        "tool_name": "exec_cmd",
        "tool_args": {"command": "rm -rf /"},
        "answer": "Executing system command...",
    }


def mock_llm_unsafe_args(prompt, history):
    return {
        "tool_name": "calculator",
        "tool_args": {"expression": "sudo rm -rf"},
        "answer": "Calculating math expression...",
    }


def mock_llm_direct_answer(prompt, history):
    return {
        "tool_name": None,
        "tool_args": {},
        "answer": "Direct response without tools.",
    }


def test_agent_shield_allowed_and_blocked():
    shield = AgentShield(allowed_tools=["calculator"], blocked_patterns=["sudo"])

    is_safe, msg = shield.inspect_tool_call("calculator", {"expression": "5 + 5"})
    assert is_safe is True
    assert msg == "Approved"

    is_safe, msg = shield.inspect_tool_call("unknown_tool", {})
    assert is_safe is False
    assert "not in allowed" in msg

    is_safe, msg = shield.inspect_tool_call("calculator", {"expression": "sudo 5"})
    assert is_safe is False
    assert "blocked pattern" in msg


def test_instinct_store():
    store = InstinctStore()
    store.add_instinct(
        "code_style", "refactor", "Use clean Python syntax with type hints"
    )

    active = store.get_relevant_instincts("Please refactor this method")
    assert len(active) == 1
    assert "code_style" in active[0]

    inactive = store.get_relevant_instincts("Write tests for this module")
    assert len(inactive) == 0


def test_memory_manager():
    mem = MemoryManager()
    mem.remember("key1", "val1")
    mem.remember("key2", 42)
    recalled = mem.recall_all()
    assert recalled == {"key1": "val1", "key2": 42}


def test_harness_successful_execution():
    harness = ECCAgentHarness(llm_fn=mock_llm_calculator)
    harness.instincts.add_instinct(
        "math", "calculate", "Double check math operations"
    )

    res = harness.execute("Please calculate 10 + 20")
    assert res["status"] == "success"
    assert res["result"] == "30.0"
    assert res["instincts_applied"] == 1
    assert harness.memory.recall_all().get("tool_output_calculator") == "30.0"


def test_harness_shield_blocks_unallowed_tool():
    harness = ECCAgentHarness(llm_fn=mock_llm_unsafe_tool)
    res = harness.execute("Run command")
    assert res["status"] == "shield_blocked"
    assert "not in allowed tools" in res["error"]


def test_harness_shield_blocks_unsafe_args():
    harness = ECCAgentHarness(llm_fn=mock_llm_unsafe_args)
    res = harness.execute("Calculate with sudo")
    assert res["status"] == "shield_blocked"
    assert "blocked pattern" in res["error"]


def test_harness_direct_answer():
    harness = ECCAgentHarness(llm_fn=mock_llm_direct_answer)
    res = harness.execute("Hello world")
    assert res["status"] == "success"
    assert res["answer"] == "Direct response without tools."
