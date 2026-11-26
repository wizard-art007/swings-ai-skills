"""Entry point for GitHub Actions: one autopilot cycle (+ weekly GitHub refresh)."""
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swings_core import *  # noqa
import swings_core, time as _time
swings_core.CYCLE_DEADLINE = _time.time() + 60 * int(os.environ.get("SWINGS_TIME_BUDGET_MIN", "30"))

init_skill_versioning()
state_file = SKILLS_DIR / "autopilot_state.json"
state = json.loads(state_file.read_text()) if state_file.exists() else {}
last = state.get("last_refresh")
due = not last or (datetime.date.today() - datetime.date.fromisoformat(last)).days >= REFRESH_DAYS
if due or os.environ.get("FORCE_REFRESH") == "true":
    try:
        refresh_skills()
        state["last_refresh"] = datetime.date.today().isoformat()
    except Exception as e:
        log(f"refresh failed: {e}")
print("Sandbox:", SANDBOX_MODE)
autopilot_cycle()
state["last_run"] = datetime.datetime.now().isoformat(timespec="minutes")
state_file.write_text(json.dumps(state, indent=2))
commit_skills("autopilot run")
