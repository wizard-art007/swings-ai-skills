import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from yt_punisher.core import AdPunisherEngine, PunisherState

def test_initial_state():
    engine = AdPunisherEngine()
    assert engine.state == PunisherState.NORMAL
    assert engine.total_punishments == 0

def test_normal_content():
    engine = AdPunisherEngine()
    state = engine.evaluate_page_state({"ad_showing": False, "classes": "html5-video-player"})
    assert state == PunisherState.NORMAL

def test_ad_triggers_punishment():
    engine = AdPunisherEngine()
    state = engine.evaluate_page_state({"ad_showing": True, "classes": "ytp-ad-module"})
    assert state == PunisherState.PUNISHING_RELOAD
    assert engine.total_punishments == 1

def test_rate_limiting_lockout():
    engine = AdPunisherEngine(max_reloads=2, time_window=10.0)
    
    # 1st ad -> reload
    assert engine.evaluate_page_state({"ad_showing": True}) == PunisherState.PUNISHING_RELOAD
    # back to normal briefly
    assert engine.evaluate_page_state({"ad_showing": False}) == PunisherState.NORMAL
    # 2nd ad -> reload
    assert engine.evaluate_page_state({"ad_showing": True}) == PunisherState.PUNISHING_RELOAD
    # back to normal briefly
    assert engine.evaluate_page_state({"ad_showing": False}) == PunisherState.NORMAL
    # 3rd ad -> should hit max_reloads limit and lock out
    assert engine.evaluate_page_state({"ad_showing": True}) == PunisherState.LOCKED_OUT
    assert engine.total_punishments == 2
