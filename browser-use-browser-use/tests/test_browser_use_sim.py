import sys
import os

# Ensure scripts/ is in sys.path per instructions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from browser_use_sim import BrowserREPL, SimulatedBrowserAgent


def test_browser_repl_navigation():
    repl = BrowserREPL()
    out = repl.execute("new_tab('https://example.com/login')")
    assert "https://example.com/login" in out
    assert repl.current_url == "https://example.com/login"


def test_browser_repl_click():
    repl = BrowserREPL()
    out = repl.execute("bu.click(41)")
    assert "Clicked element 41" in out


def test_simulated_browser_agent_flow():
    responses = [
        "new_tab('https://example.com/book')",
        "bu.click(12)",
        "finish('Booking confirmed')"
    ]
    call_count = [0]

    def fake_llm(prompt, messages):
        resp = responses[call_count[0]]
        call_count[0] += 1
        return resp

    agent = SimulatedBrowserAgent(llm_generator=fake_llm)
    result = agent.run("book the earliest test", max_steps=5)

    assert "FINISHED" in result
    assert "Booking confirmed" in result
    assert len(agent.repl.history) == 3
