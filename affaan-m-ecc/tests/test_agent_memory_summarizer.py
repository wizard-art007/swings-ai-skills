import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import agent_memory_summarizer

def test_summarize_trace_unit():
    trace = [
        {"step": 1, "action": "test action", "result": "success"}
    ]
    summary = agent_memory_summarizer.summarize_trace(trace)
    assert isinstance(summary, str)
    assert "Step 1" in summary
