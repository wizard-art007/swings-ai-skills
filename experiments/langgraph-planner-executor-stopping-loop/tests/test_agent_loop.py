import sys
import os

# Ensure src is in python path for offline testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent_loop import AgentState, Planner, Executor, StoppingChecker, AgentRunner

def test_planner_creates_plan():
    state = AgentState(goal="Build a test feature")
    planner = Planner()
    planner.plan(state)
    assert len(state.plan) == 3
    assert "Analyze requirements" in state.plan[0]

def test_executor_runs_step():
    state = AgentState(goal="Test goal", plan=["Step 1: Do work"])
    executor = Executor()
    res = executor.execute_step(state)
    assert res is not None
    assert len(state.completed_steps) == 1
    assert state.completed_steps[0] == "Step 1: Do work"
    assert len(state.plan) == 0

def test_stopping_checker_conditions():
    checker = StoppingChecker()
    
    # Condition 1: Max iterations reached
    state1 = AgentState(goal="Test", iteration=5, max_iterations=5)
    assert checker.should_stop(state1) is True
    assert state1.is_finished is True

    # Condition 2: Plan empty and steps completed
    state2 = AgentState(goal="Test", plan=[], completed_steps=["A", "B"])
    assert checker.should_stop(state2) is True
    assert state2.is_finished is True

    # Condition 3: Active state (should not stop)
    state3 = AgentState(goal="Test", plan=["Step 1"], completed_steps=[])
    assert checker.should_stop(state3) is False

def test_agent_runner_full_lifecycle():
    runner = AgentRunner(max_iterations=10)
    final_state = runner.run("Create a documentation site")
    
    assert final_state.is_finished is True
    assert len(final_state.completed_steps) == 3
    assert final_state.iteration <= 3
    assert "All plan steps completed successfully" in final_state.status_message
