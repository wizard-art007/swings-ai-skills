"""LLM Token Budget Estimator tool for estimating token counts of messages."""

from typing import Any, Dict, List


class LLMTokenBudgetEstimator:
    """Estimates token budgets for message lists."""

    def estimate_tokens(self, messages: List[Dict[str, Any]], model: str = "gpt-4") -> int:
        """Estimate the number of tokens required for a list of messages.

        A lightweight estimation method roughly approximating cl100k_base / tiktoken
        character-to-token ratios without requiring external dependencies or network.
        """
        total_chars = 0
        # Base overhead per message (role, formatting tokens)
        overhead_per_message = 4

        for msg in messages:
            total_chars += overhead_per_message
            for key, value in msg.items():
                if isinstance(value, str):
                    total_chars += len(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                if isinstance(v, str):
                                    total_chars += len(v)
                        elif isinstance(item, str):
                            total_chars += len(item)

        # Rough approximation: ~4 characters per token for English text
        estimated_tokens = max(1, total_chars // 4)
        return int(estimated_tokens)


def estimate_tokens(messages: List[Dict[str, Any]], model: str = "gpt-4") -> int:
    """Convenience function matching the tool interface."""
    estimator = LLMTokenBudgetEstimator()
    return estimator.estimate_tokens(messages, model=model)
