import sys
sys.path.insert(0, 'src')
from normalscript import Interpreter

def test_lexer():
    interp = Interpreter()
    code = "10 -> x"
    interp.run(code)
    assert interp.vars['x'] == 10

def test_reverse_assignment_and_math():
    code = '''
    10 + 5 -> result
    speak result
    '''
    interp = Interpreter()
    out = interp.run(code)
    assert out == [15]

def test_unless_conditional():
    code = '''
    5 -> val
    unless val == 5 {
        speak "should not happen"
    }
    unless val == 10 {
        speak "triggered"
    }
    '''
    interp = Interpreter()
    out = interp.run(code)
    assert out == ["triggered"]

def test_strings_and_comparisons():
    code = '''
    "hello" -> greeting
    speak greeting
    20 > 10 -> check
    speak check
    '''
    interp = Interpreter()
    out = interp.run(code)
    assert out == ["hello", True]
