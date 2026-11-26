# LangGraph Planner/Executor Stopping Loop Simulator

A lightweight, robust Python experiment implementing a classic Plan-and-Execute agent loop with explicit stopping conditions, drawing inspiration from agentic orchestration patterns and recent insights on robust loop termination.

## Idea & How It Works

In many agentic workflows (such as LangGraph-style architectures), a **Planner** agent breaks down a complex goal into sequential or parallel steps, an **Executor** agent runs each step, and a **Stopping Condition Checker** decides whether the goal has been achieved, max iterations have been reached, or an unrecoverable failure occurred.

This simulator models that state machine cleanly using pure Python:
1. **State**: Tracks goal, plan steps, execution history, iteration count, and termination status.
2. **Planner**: Generates or updates the step list based on current progress.
3. **Executor**: Simulates execution of the current pending step (with mock tool output).
4. **Stopping Condition Checker**: Evaluates if all steps are complete or if safety thresholds (max steps/iterations) are breached.

## Project Structure

- `src/agent_loop.py`: Core implementation of the Planner, Executor, Stopping Checker, and AgentRunner.
- `tests/test_agent_loop.py`: Comprehensive offline pytest suite validating successful execution, graceful stopping, and max-iteration guardrails.

## Running Tests

Ensure you have `pytest` installed, then run:

