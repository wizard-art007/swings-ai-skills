import time
from typing import Dict, Any

class PunisherState:
    NORMAL = "normal"
    AD_DETECTED = "ad_detected"
    PUNISHING_RELOAD = "punishing_reload"
    LOCKED_OUT = "locked_out"

class AdPunisherEngine:
    def __init__(self, max_reloads: int = 3, time_window: float = 60.0):
        self.max_reloads = max_reloads
        self.time_window = time_window
        self.reload_timestamps = []
        self.state = PunisherState.NORMAL
        self.total_punishments = 0

    def evaluate_page_state(self, player_payload: Dict[str, Any]) -> str:
        """
        Evaluates player state dictionary to determine if an ad is present
        and whether to punish (reload) or lock out due to frequency limits.
        """
        now = time.time()
        # Prune old timestamps outside the sliding window
        self.reload_timestamps = [t for t in self.reload_timestamps if now - t < self.time_window]

        is_ad = player_payload.get("ad_showing", False) or "ytp-ad-module" in player_payload.get("classes", "")

        if not is_ad:
            self.state = PunisherState.NORMAL
            return self.state

        # Ad is showing
        self.state = PunisherState.AD_DETECTED

        if len(self.reload_timestamps) >= self.max_reloads:
            self.state = PunisherState.LOCKED_OUT
            return self.state

        # Trigger punishment
        self.state = PunisherState.PUNISHING_RELOAD
        self.reload_timestamps.append(now)
        self.total_punishments += 1
        return self.state

    def reset_stats(self) -> None:
        self.reload_timestamps.clear()
        self.total_punishments = 0
        self.state = PunisherState.NORMAL
