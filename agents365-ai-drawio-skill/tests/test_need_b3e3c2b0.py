from captools import load_tool

def test_bpmn_process_generation():
    mod = load_tool('*', 'bpmn_generator')
    res = mod.generate_bpmn("Start -> Task -> End")
    assert isinstance(res, str)
    assert "<definitions" in res
    assert "Task" in res
