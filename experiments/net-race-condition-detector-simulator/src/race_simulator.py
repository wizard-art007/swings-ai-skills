import threading
import time
from typing import Dict, Any, List

class AccountContext:
    def __init__(self, initial_balance: float = 100.0):
        self.balance = initial_balance
        self.file_exists = False
        self.data_store: Dict[str, Any] = {}

class TaskQueueSimulator:
    def __init__(self):
        self.context = AccountContext()
        self.execution_log: List[str] = []
        self._lock = threading.Lock()

    def unsafe_lost_update_worker(self, amount: float, delay: float) -> None:
        """Simulates a non-atomic read-modify-write lost update race condition."""
        current = self.context.balance
        time.sleep(delay)  # Yield to force context switch / race window
        self.context.balance = current + amount
        self.execution_log.append(f"Balance updated by {amount}, new balance: {self.context.balance}")

    def safe_lost_update_worker(self, amount: float, delay: float) -> None:
        """Fixes lost update using a threading lock."""
        time.sleep(delay)
        with self._lock:
            current = self.context.balance
            self.context.balance = current + amount
            self.execution_log.append(f"Safe balance updated by {amount}, new balance: {self.context.balance}")

    def unsafe_toctou_worker(self, key: str, value: Any, delay: float) -> bool:
        """Simulates Time-Of-Check to Time-Of-Use hazard."""
        exists = key in self.context.data_store
        time.sleep(delay)  # Window for another thread to modify state
        if not exists:
            self.context.data_store[key] = value
            self.execution_log.append(f"TOCTOU inserted {key}={value}")
            return True
        self.execution_log.append(f"TOCTOU skipped {key}, already existed")
        return False

    def safe_toctou_worker(self, key: str, value: Any, delay: float) -> bool:
        """Fixes TOCTOU using atomic check-and-set under lock."""
        time.sleep(delay)
        with self._lock:
            if key not in self.context.data_store:
                self.context.data_store[key] = value
                self.execution_log.append(f"Safe TOCTOU inserted {key}={value}")
                return True
            self.execution_log.append(f"Safe TOCTOU skipped {key}, already existed")
            return False

def run_simulation(safe: bool = False) -> TaskQueueSimulator:
    sim = TaskQueueSimulator()
    threads = []

    # Spawn concurrent threads targeting the same resource
    for i in range(5):
        if not safe:
            t = threading.Thread(target=sim.unsafe_lost_update_worker, args=(10.0, 0.001))
        else:
            t = threading.Thread(target=sim.safe_lost_update_worker, args=(10.0, 0.001))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sim
