import sys
import os

# Ensure scripts/ is in sys.path for offline import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

import pytest
from e2e_simulator import App, Agent, Expect, Element, Screen


def test_app_navigation_and_screen():
    app = App()
    app.open("/settings/billing")
    assert app.current_route == "/settings/billing"
    
    screen = app.screen
    status_el = screen.get_by_role("status")
    status_el.to_contain_text("Free Plan Active")


def test_agent_act_and_assert():
    app = App()
    agent = Agent(app)
    
    app.open("/settings/billing")
    agent.act("upgrade the workspace to the Pro plan")
    agent.assert_cond("the invoice preview shows a prorated amount")
    
    expect = Expect(app.screen)
    expect.get_by_role("status").to_contain_text("Pro")


def test_strict_cache_recording_and_replay():
    app = App()
    agent = Agent(app, strict_cache=False)
    
    app.open("/settings/billing")
    # First run (live execution, populates cache)
    agent.act("upgrade the workspace to the Pro plan")
    
    # Second run with strict cache enabled
    app2 = App()
    app2.open("/settings/billing")
    agent2 = Agent(app2, strict_cache=True)
    # Pre-seed recording from agent 1
    agent2.recordings = agent.recordings
    
    # Should replay successfully without model call
    res = agent2.act("upgrade the workspace to the Pro plan")
    assert "Replayed" in res
    assert app2.state["plan"] == "Pro"


def test_strict_cache_miss_fails():
    app = App()
    app.open("/settings/billing")
    agent = Agent(app, strict_cache=True)
    
    with pytest.raises(RuntimeError, match="Strict cache enabled"):
        agent.act("unknown unrecorded action")


def test_fluent_assertion_failure():
    app = App()
    app.open("/settings/billing")
    expect = Expect(app.screen)
    
    with pytest.raises(AssertionError, match="does not contain text"):
        expect.get_by_role("status").to_contain_text("NonExistentText")
