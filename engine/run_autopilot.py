"""Entry point for GitHub Actions: one autopilot cycle (+ weekly GitHub refresh), with a private run log."""
import os, sys, json, datetime, shutil, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import swings_core
except Exception:
    # A fix the system made to itself broke the engine: restore the last good engine, mark the fix reverted.
    heals_file = os.path.join(HERE, "heals.json")
    heals = json.load(open(heals_file)) if os.path.exists(heals_file) else []
    good = os.path.join(HERE, "swings_core.last_good.py")
    if not (os.path.exists(good) and any(h.get("status") == "trial" for h in heals)):
        raise
    traceback.print_exc()
    shutil.copy(good, os.path.join(HERE, "swings_core.py"))
    for h in heals:
        if h.get("status") == "trial":
            h.update(status="reverted", reason="engine failed to start after this fix")
    json.dump(heals, open(heals_file, "w"), indent=2)
    print("Engine restored from the last good version")
    sys.modules.pop("swings_core", None)
    import swings_core
from swings_core import *  # noqa
import time as _time
swings_core.CYCLE_DEADLINE = _time.time() + 60 * int(os.environ.get("SWINGS_TIME_BUDGET_MIN", "30"))

init_skill_versioning()
start_run_log("actions")
status = "ok"
try:
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
except Exception as e:
    status = "crashed"
    syslog_exception("run", e)
    raise
finally:
    finish_run_log(status)
    commit_skills("autopilot run")
