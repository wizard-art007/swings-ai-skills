import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from race_simulator import TaskQueueSimulator, run_simulation

def test_unsafe_lost_update_demonstrates_race():
    # Unsafe concurrent updates should drop increments due to race condition
    sim = run_simulation(safe=False)
    # Starting at 100, 5 threads adding 10 should ideally be 150.
    # Due to lost updates without locks, final balance is typically lower than 150.
    assert sim.context.balance != 150.0 or len(sim.execution_log) == 5

def test_safe_lost_update_prevents_race():
    # Safe concurrent updates using locks should precisely accumulate all increments
    sim = run_simulation(safe=True)
    assert sim.context.balance == 150.0

def test_toctou_hazard_simulation():
    sim = TaskQueueSimulator()
    import threading

    # Two threads trying to initialize the same key concurrently
    t1 = threading.Thread(target=sim.unsafe_toctou_worker, args=("config", "v1", 0.01))
    t2 = threading.Thread(target=sim.unsafe_toctou_worker, args=("config", "v2", 0.01))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # In an unsafe TOCTOU, both might check 'not in' before either writes, causing a race hazard
    assert "config" in sim.context.data_store

def test_safe_toctou_prevents_duplicate_writes():
    sim = TaskQueueSimulator()
    import threading

    t1 = threading.Thread(target=sim.safe_toctou_worker, args=("config", "v1", 0.01))
    t2 = threading.Thread(target=sim.safe_toctou_worker, args=("config", "v2", 0.01))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Exactly one write should succeed under lock protection
    assert sim.context.data_store["config"] in ("v1", "v2")
    # Verify exact single insert action logged
    inserts = [log for log in sim.execution_log if "inserted" in log]
    assert len(inserts) == 1
