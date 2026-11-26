from captools import load_tool

def test_agent_prompt_router():
    m = load_tool('*', 'agent_prompt_router')
    result = m.route_prompt("Debug this Python segmentation fault error in async code.")
    assert isinstance(result, dict)
    assert "agent_type" in result
    assert result["agent_type"] in ["coding", "debugging", "general"]
