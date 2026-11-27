import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from vim_trainer import VimTrainerGame

def test_initial_state():
    game = VimTrainerGame("abc", "adc")
    assert game.mode == "NORMAL"
    assert game.cursor == 0
    assert game.text == ['a', 'b', 'c']

def test_movement_normal_mode():
    game = VimTrainerGame("hello", "hello")
    game.handle_key('l')
    assert game.cursor == 1
    game.handle_key('h')
    assert game.cursor == 0

def test_insert_mode_and_backspace():
    game = VimTrainerGame("hl", "hel")
    game.handle_key('l') # cursor at 'l'
    game.handle_key('i') # enter insert
    assert game.mode == "INSERT"
    game.handle_key('e')
    assert game.text == ['h', 'e', 'l']
    game.handle_key('\x7f') # backspace
    assert game.text == ['h', 'l']

def test_winning_condition():
    game = VimTrainerGame("cat", "dog")
    game.text = list("dog")
    status = game.handle_key('h')
    assert status == "WON"
