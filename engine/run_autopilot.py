"""Entry point for GitHub Actions: one autopilot cycle (+ weekly GitHub refresh)."""
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swings_core import *  # noqa

init_skill_versioning()
state_file = SKILLS_DIR / "autopilot_state.json"
state = json.loads(state_file.read_text()) if state_file.exists() else {}
last = state.get("last_refresh")
due = not last or (datetime.date.today() - datetime.date.fromisoformat(last)).days >= REFRESH_DAYS
if due or os.environ.get("FORCE_REFRESH") == "true":
    refresh_skills()
    state["last_refresh"] = datetime.date.today().isoformat()
print("Sandbox:", SANDBOX_MODE)
autopilot_cycle()
state["last_run"] = datetime.datetime.now().isoformat(timespec="minutes")
state_file.write_text(json.dumps(state, indent=2))
commit_skills("autopilot run")
