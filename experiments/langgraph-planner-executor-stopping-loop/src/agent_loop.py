from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class AgentState:
    goal: str
    plan: List[str] = field(default_factory=list)
    completed_steps: List[str] = field(default_factory=list)
    execution_logs: List[Dict[str, Any]] = field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 5
    is_finished: bool = False
    status_message: str = "Initialized"

class Planner:
    """Creates or updates the execution plan based on the agent state."""
    def plan(self, state: AgentState) -> None:
        if not state.plan and not state.completed_steps:
            # Initial decomposition of the goal
            state.plan = [
                f"Analyze requirements for: {state.goal}",
                f"Draft initial solution for: {state.goal}",
                f"Validate and finalize: {state.goal}"
            ]
            state.status_message = "Plan generated."

class Executor:
    """Executes the next pending step in the plan."""
    def execute_step(self, state: AgentState) -> Optional[str]:
        if not state.plan:
            return None
        current_step = state.plan.pop(0)
        # Simulate execution result
        result = f"Successfully executed: '{current_step}'"
        state.completed_steps.append(current_step)
        state.execution_logs.append({
            "step": current_step,
            "result": result,
            "iteration": state.iteration
        })
        state.status_message = f"Executed step: {current_step}"
        return result

class StoppingChecker:
    """Evaluates whether the agent loop should terminate."""
    def should_stop(self, state: AgentState) -> bool:
        if state.is_finished:
            return True
        if state.iteration >= state.max_iterations:
            state.is_finished = True
            state.status_message = "Stopped: Max iterations reached."
            return True
        if not state.plan and state.completed_steps:
            state.is_finished = True
            state.status_message = "Stopped: All plan steps completed successfully."
            return True
        return False

class AgentRunner:
    """Orchestrates Planner, Executor, and StoppingChecker in a controlled loop."""
    def __init__(self, max_iterations: int = 5):
        self.planner = Planner()
        self.executor = Executor()
        self.stopper = StoppingChecker()
        self.max_iterations = max_iterations

    def run(self, goal: str) -> AgentState:
        state = AgentState(goal=goal, max_iterations=self.max_iterations)
        
        while not self.stopper.should_stop(state):
            state.iteration += 1
            self.planner.plan(state)
            self.executor.execute_step(state)
            
        # Final evaluation check
        self.stopper.should_stop(state)
        return state
