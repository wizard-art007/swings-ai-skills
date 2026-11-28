import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from midscene_sim import MidsceneSimulator

def test_simulator_init():
    sim = MidsceneSimulator("https://shop.example")
    assert sim.target_url == "https://shop.example"
    assert len(sim.history) == 0

def test_goto_url():
    sim = MidsceneSimulator()
    res = sim.goto_url("https://test.example")
    assert res["status"] == "success"
    assert sim.target_url == "https://test.example"
    assert len(sim.history) == 1

def test_ai_actions_and_assertions():
    sim = MidsceneSimulator()
    
    act_res = sim.ai_act("Search for headphones and filter under $100")
    assert act_res["status"] == "success"
    
    wait_res = sim.ai_wait_for("Filtered search results are visible")
    assert wait_res["satisfied"] is True
    
    asserted = sim.ai_assert("There are products in the search results")
    assert asserted is True
    
    with pytest.raises(ValueError):
        sim.ai_act("")
        
    with pytest.raises(ValueError):
        sim.ai_wait_for("")
        
    with pytest.raises(ValueError):
        sim.ai_assert("")

def test_run_yaml_suite():
    sim = MidsceneSimulator()
    suite = {
        "beforeEach": [
            {"gotoUrl": "https://my-store.example"}
        ],
        "cases": [
            {
                "name": "Find headphones under $100",
                "steps": [
                    {"aiAct": "Search for headphones"},
                    {"aiWaitFor": "Results load"},
                    {"aiAssert": "Products are shown"}
                ]
            }
        ]
    }
    
    results = sim.run_yaml_suite(suite)
    assert len(results) == 1
    assert results[0]["name"] == "Find headphones under $100"
    assert len(results[0]["steps"]) == 3
    
    report = sim.export_report()
    assert "gotoUrl" in report
    assert "aiAct" in report
