from captools import load_tool

def test_erd_model_generator():
    mod = load_tool('*', 'erd_generator')
    res = mod.generate_erd("User has many Orders")
    assert isinstance(res, str)
    assert "User" in res
    assert "Order" in res
