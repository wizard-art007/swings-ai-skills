import sys
import os
import pytest

# Ensure scripts/ is importable without network or external system calls
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from offline_calculator import OfflineCalculator

def test_calculator_addition():
    calc = OfflineCalculator()
    assert calc.add(2, 3) == 5.0
    assert len(calc.history) == 1
    assert "add(2, 3)" in calc.history[0]

def test_calculator_division():
    calc = OfflineCalculator()
    assert calc.divide(10, 2) == 5.0

def test_calculator_zero_division():
    calc = OfflineCalculator()
    with pytest.raises(ZeroDivisionError):
        calc.divide(5, 0)

def test_calculator_type_error():
    calc = OfflineCalculator()
    with pytest.raises(TypeError):
        calc.add("2", 3)

def test_calculator_memory():
    calc = OfflineCalculator()
    calc.store_memory(42.5)
    assert calc.recall_memory() == 42.5
