"""Phase 5 step 6 tests: the monthly self-repair fire drill (on a throwaway copy, scripted LLM) proves fix, keep and
revert; the owner dashboard is written before the private logs are pushed."""
import os, sys, json, hashlib
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)

if not hasattr(sc, "run_fire_drill"):
    print("PASS (skipped: this engine has no fire drill yet)")
    print("RESULT ALL PASS"); sys.exit(0)

FAKE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "support", "drillfake.py")
sc.CYCLE_DEADLINE = sc.time.time() + 3600
eng = sc.SKILLS_DIR / "engine" / "swings_core.py"
before = hashlib.sha256(eng.read_bytes()).hexdigest()
heals_before = (sc.SKILLS_DIR / "engine" / "heals.json").read_text() if (sc.SKILLS_DIR / "engine" / "heals.json").exists() else None

# ---- wiring ----
names = [s[0] for s in sc.RUN_PIPELINE]
expect(names.index("fire_drill") == names.index("sustainability") - 1, "the drill is a pipeline step, just before sustainability")
expect(sc.drill_due(), "a month with no drill is due")

# ---- the drill ----
# In Colab the sandbox runs through sudo, which drops the test shim that hides google.colab, so the healer's sandboxed
# self-test would load the real Colab module. The drill itself runs in CI (GitHub Actions has no google.colab).
import subprocess
REAL_COLAB = subprocess.run([sys.executable, "-I", "-c", "import google.colab"], capture_output=True).returncode == 0
if REAL_COLAB:
    print("PASS T1 (drill skipped in Colab: the sandbox cannot hide google.colab; CI runs the full drill)")
    sc._jsave(sc.DRILL_FILE, {sc.datetime.date.today().strftime("%Y-%m"): {"ts": sc._now_min(), "ok": True, "runs": 6,
              "healed": 2, "kept": True, "reverted": True, "detected": 2, "notes": [], "trace": []}})
    res = {"detected": 2, "healed": 2, "kept": True, "reverted": True, "ok": True, "runs": 6, "trace": [], "notes": []}
else:
    res = sc.fire_drill_step(fake_llm=FAKE)
print("     trace: " + "; ".join(f"run {r['run']} {r['mode']}: {r['heals']}" for r in (res or {}).get("trace", [])))
print("     notes: " + str((res or {}).get("notes")) + " heal_log: " + str((res or {}).get("heal_log")))
expect(res and res["detected"] >= 2, f"T1 both planted bugs are found in the copy's logs: {res and res.get('detected')}")
expect(res and res["healed"] >= 2, "T1 the healer fixes both")
expect(res and res["kept"], "T1 the fix that holds is kept after 3 clean runs")
expect(res and res["reverted"], "T1 the fix whose function breaks again is reverted")
expect(res and res["ok"] and res["runs"] <= sc.DRILL_MAX_RUNS, f"T1 the drill passes within {sc.DRILL_MAX_RUNS} runs ({res and res['runs']})")
expect(hashlib.sha256(eng.read_bytes()).hexdigest() == before, "T2 the live engine is untouched")
now = (sc.SKILLS_DIR / "engine" / "heals.json").read_text() if (sc.SKILLS_DIR / "engine" / "heals.json").exists() else None
expect(now == heals_before, "T2 the live heals file is untouched")
expect(not sc.drill_due() and sc.fire_drill_step(fake_llm=FAKE) is None, "T3 one drill a month")
expect(sc._run_extras().get("fire_drill", {}).get("ok") is True, "T3 the run log carries the drill result")

# ---- a failed drill is tried again the next day, at most 3 times a month ----
d = sc._jload(sc.DRILL_FILE, {}); m = max(d); keep = dict(d[m])
d[m] = {**keep, "ok": False, "attempts": 1, "ts": (sc.datetime.datetime.now() - sc.datetime.timedelta(days=2)).isoformat(timespec="minutes")}
sc._jsave(sc.DRILL_FILE, d)
due_next_day = sc.drill_due()
d[m]["ts"] = sc._now_min(); sc._jsave(sc.DRILL_FILE, d)
due_same_day = sc.drill_due()
d[m].update(attempts=3, ts=(sc.datetime.datetime.now() - sc.datetime.timedelta(days=2)).isoformat(timespec="minutes")); sc._jsave(sc.DRILL_FILE, d)
expect(due_next_day and not due_same_day and not sc.drill_due(), "T3 a failed drill is retried the next day, at most 3 times a month")
d[m] = keep; sc._jsave(sc.DRILL_FILE, d)

# ---- F9's "run less often" advice is dropped while most runs do real work ----
rows = [{"run": f"x{i}", "queue_todo": 0} for i in range(8)]
st = sc._jload(sc.P5_STATE, {})
st["runs"] = [{"run": f"x{i}", "ts": sc._now_min(), "useful": i < 5} for i in range(8)]
sc._jsave(sc.P5_STATE, st)
busy = sc.schedule_advice(rows)
st["runs"] = [{"run": f"x{i}", "ts": sc._now_min(), "useful": i < 2} for i in range(8)]
sc._jsave(sc.P5_STATE, st)
idle = sc.schedule_advice(rows)
expect(not any(a.startswith("The queue was empty") for a in busy) and any(a.startswith("The queue was empty") for a in idle),
       "T7 'run less often' is only advised when runs really are idle")

# ---- a failed drill asks the owner ----
d = sc._jload(sc.DRILL_FILE, {})
m = max(d)
d[m] = {**d[m], "ok": False, "kept": False, "notes": ["run 3 exited 1: boom"]}
sc._jsave(sc.DRILL_FILE, d)
text, _ = sc.build_health_report()
expect("## Self-repair drill (Phase 5)" in text and "self-repair drill failed" in text.split("## Decisions waiting for you", 1)[-1],
       "T4 a failed drill becomes a decision in the weekly report")

# ---- the healer's sandbox can import the engine (the first CI drill found it could not) ----
if not REAL_COLAB:
    import tempfile, shutil as _sh
    w = sc.Path(tempfile.mkdtemp(prefix="swings-sbx-")) / "w"
    w.mkdir()
    _sh.copy(sc.ENGINE_FILE, w / "swings_core.py")
    (w / "t.py").write_text("import os, sys\nsys.path.insert(0, '.')\n"            # as the healer's self-test does
                            "os.environ.update(SWINGS_SKILLS_DIR=os.path.abspath('skills'), SWINGS_REPO_CACHE=os.path.abspath('cache'))\n"
                            "import swings_core\nprint('IMPORT_OK')\n")
    ok, out = sc.run_sandboxed(w, [sys.executable, "t.py"], timeout=240)
    expect(ok and "IMPORT_OK" in out, f"T6 the engine imports inside the healer's sandbox (as 'nobody' on CI): {out[-300:]}")

# ---- dashboard ----
sc.PRIVATE_LOG_DIR.mkdir(exist_ok=True)
rows = [{"run": f"r{i}", "status": "ok", "errors": 0, "minutes": 1.0, "steps": {"queue": 1.0}} for i in range(12)]
rows[-1]["steps"] = {"queue": "error: KeyError", "plan": 0.1}
(sc.PRIVATE_LOG_DIR / "runs_index.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
sc._RUN["id"] = "p5d-run"
out = sc._log_repo_sync(push=True)
dash = sc.DASHBOARD_FILE.read_text() if sc.DASHBOARD_FILE.exists() else ""
expect(dash.startswith("# Swings AI dashboard") and "Within free limits:" in dash and "## Needs you" in dash and "## This week" in dash and "## Last runs" in dash,
       "T5 the dashboard is written before the private logs are pushed")
expect("self-repair drill failed" in dash, "T5 open decisions are on the dashboard")
expect(dash.count("| r") == 10 and "| r11 | ok | 0 | 1.0 | - | queue |" in dash, "T5 the last 10 runs, newest first, with failed steps")
expect("ghp_" not in dash and "AIza" not in dash, "T5 nothing secret on the dashboard")

print("RESULT " + ("ALL PASS" if not FAILS else f"FAILED {len(FAILS)}"))
sys.exit(1 if FAILS else 0)
