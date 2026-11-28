"""
A small, self-contained offline Python helper illustrating robust logic,
input validation, and state handling suitable for testing and automation pipelines.
"""

class OfflineCalculator:
    """A robust calculator with history tracking and state validation."""
    
    def __init__(self):
        self.history = []
        self._memory = 0.0

    def add(self, a: float, b: float) -> float:
        self._validate_number(a)
        self._validate_number(b)
        result = a + b
        self.history.append(f"add({a}, {b}) = {result}")
        return result

    def divide(self, a: float, b: float) -> float:
        self._validate_number(a)
        self._validate_number(b)
        if b == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        result = a / b
        self.history.append(f"divide({a}, {b}) = {result}")
        return result

    def store_memory(self, value: float) -> None:
        self._validate_number(value)
        self._memory = value

    def recall_memory(self) -> float:
        return self._memory

    def clear_history(self) -> None:
        self.history.clear()

    @staticmethod
    def _validate_number(val):
        if not isinstance(val, (int, float)):
            raise TypeError(f"Expected int or float, got {type(val).__name__}")
