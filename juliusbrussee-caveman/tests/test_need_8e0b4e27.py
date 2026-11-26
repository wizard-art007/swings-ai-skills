import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

import llm_token_budget_estimator as m

def test_token_budget_estimator():
    messages = [{"role": "user", "content": "Hello, write a quicksort function in Python."}]
    budget = m.estimate_tokens(messages, model="gpt-4")
    assert isinstance(budget, int)
    assert budget > 0

def test_estimator_class():
    estimator = m.LLMTokenBudgetEstimator()
    messages = [{"role": "user", "content": "Test content"}]
    budget = estimator.estimate_tokens(messages)
    assert isinstance(budget, int)
    assert budget > 0
