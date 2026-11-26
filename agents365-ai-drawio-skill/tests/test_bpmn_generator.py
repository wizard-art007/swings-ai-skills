import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from bpmn_generator import generate_bpmn

def test_bpmn_process_generation():
    res = generate_bpmn("Start -> Task -> End")
    assert isinstance(res, str)
    assert "<definitions" in res
    assert "Task" in res
    assert "StartEvent" in res or "Start" in res
    assert "EndEvent" in res or "End" in res
