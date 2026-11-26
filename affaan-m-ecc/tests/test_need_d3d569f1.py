from captools import load_tool

def test_agent_memory_summarizer():
    m = load_tool('*', 'agent_memory_summarizer')
    trace = [
        {"step": 1, "action": "searched web", "result": "found 5 links"},
        {"step": 2, "action": "read page", "result": "extracted API schema"}
    ]
    summary = m.summarize_trace(trace)
    assert isinstance(summary, str)
    assert len(summary) > 0
