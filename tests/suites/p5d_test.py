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
res = sc.fire_drill_step(fake_llm=FAKE)
print("     trace: " + "; ".join(f"run {r['run']} {r['mode']}: {r['heals']}" for r in (res or {}).get("trace", [])))
print("     notes: " + str((res or {}).get("notes")))
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

# ---- a failed drill asks the owner ----
d = sc._jload(sc.DRILL_FILE, {})
m = max(d)
d[m] = {**d[m], "ok": False, "kept": False, "notes": ["run 3 exited 1: boom"]}
sc._jsave(sc.DRILL_FILE, d)
text, _ = sc.build_health_report()
expect("## Self-repair drill (Phase 5)" in text and "self-repair drill failed" in text.split("## Decisions waiting for you", 1)[-1],
       "T4 a failed drill becomes a decision in the weekly report")

# ---- dashboard ----
sc.PRIVATE_LOG_DIR.mkdir(exist_ok=True)
rows = [{"run": f"r{i}", "status": "ok", "errors": 0, "minutes": 1.0, "steps": {"queue": 1.0}} for i in range(12)]
rows[-1]["steps"] = {"queue": "error: KeyError", "plan": 0.1}
(sc.PRIVATE_LOG_DIR / "runs_index.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
sc._RUN["id"] = "p5d-run"
out = sc._log_repo_sync(push=True)
dash = sc.DASHBOARD_FILE.read_text() if sc.DASHBOARD_FILE.exists() else ""
expect(dash.startswith("# Swings AI dashboard") and "## Needs you" in dash and "## This week" in dash and "## Last runs" in dash,
       "T5 the dashboard is written before the private logs are pushed")
expect("self-repair drill failed" in dash, "T5 open decisions are on the dashboard")
expect(dash.count("| r") == 10 and "| r11 | ok | 0 | 1.0 | - | queue |" in dash, "T5 the last 10 runs, newest first, with failed steps")
expect("ghp_" not in dash and "AIza" not in dash, "T5 nothing secret on the dashboard")

print("RESULT " + ("ALL PASS" if not FAILS else f"FAILED {len(FAILS)}"))
sys.exit(1 if FAILS else 0)
