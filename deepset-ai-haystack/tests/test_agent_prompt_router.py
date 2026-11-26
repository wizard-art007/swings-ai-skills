import sys
import os

# Ensure scripts directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import agent_prompt_router

def test_route_prompt_debugging():
    result = agent_prompt_router.route_prompt("Debug this Python segmentation fault error in async code.")
    assert isinstance(result, dict)
    assert "agent_type" in result
    assert result["agent_type"] == "debugging"

def test_route_prompt_coding():
    result = agent_prompt_router.route_prompt("Write a python function to compute fibonacci numbers.")
    assert isinstance(result, dict)
    assert "agent_type" in result
    assert result["agent_type"] == "coding"

def test_route_prompt_general():
    result = agent_prompt_router.route_prompt("What is the capital of France?")
    assert isinstance(result, dict)
    assert "agent_type" in result
    assert result["agent_type"] == "general"
