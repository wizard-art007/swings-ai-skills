"""Phase 5 step 5 tests: the explicit run pipeline does exactly what the old stack of nine autopilot_cycle wrappers
did, in the same order, call for call; and one failing step no longer skips the steps after it."""
import os, sys, json
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)

if not hasattr(sc, "run_pipeline"):
    print("PASS (skipped: this engine has no run pipeline yet)")
    print("RESULT ALL PASS"); sys.exit(0)

sc.CYCLE_DEADLINE = sc.time.time() + 3600
LEAVES = {"quality_step": None, "projects_step": None, "coherence_step": None,
          "work_needs": {"started": 1, "verified": 0, "routed": 0}, "self_heal": "skipped", "autopilot_plan": None,
          "run_task_queue": None, "orchestrator_tick": None, "self_review": None, "publish_pending": None,
          "graduate_ready": "nothing to graduate", "update_progress": None, "_diff_and_record": None,
          "advance_projects": None, "more_work_pass": None, "ci_status": None, "record_useful_run": None,
          "sustainability_step": None}
CALLS = []
saved = {n: getattr(sc, n) for n in LEAVES}
def recorder(name, ret):
    def f(*a, **k):
        CALLS.append(name + (f"({k['limit']})" if "limit" in k else ""))
        if name == "autopilot_plan" and BOOM.get("on"):
            raise RuntimeError("planned failure")
        return ret
    return f
BOOM = {}
for n, ret in LEAVES.items():
    setattr(sc, n, recorder(n, ret))
saved_due, saved_token = sc.self_review_due, sc.GITHUB._token
sc.self_review_due = lambda: True
sc.GITHUB._token = lambda: "test-token"

# ---- the same calls in the same order ----
expect(sc.autopilot_cycle is sc.run_pipeline, "the engine's autopilot_cycle is the pipeline")
sc._RUN["id"] = "p5r-legacy"
CALLS.clear(); sc._legacy_autopilot_cycle(); legacy = list(CALLS)
sc._RUN["id"] = "p5r-pipeline"
CALLS.clear(); steps = sc.run_pipeline(); new = list(CALLS)
print("     legacy:   " + " > ".join(legacy))
print("     pipeline: " + " > ".join(new))
expect(len(legacy) >= 18 and new == legacy, f"T1 the pipeline makes the same {len(legacy)} calls in the same order as the old stack")
expect([s["step"] for s in steps if s["status"] == "ok"] == [n for n, *_ in sc.RUN_PIPELINE], "T1 every step ran and is recorded in order")
expect(sc._NEED_RUN.get("p5r-pipeline") == {"started": 2, "verified": 0, "routed": 0}, f"T1 need totals add up over both need steps: {sc._NEED_RUN.get('p5r-pipeline')}")

# ---- in Colab the same steps are skipped as before ----
sc.IN_COLAB = True
CALLS.clear(); sc._legacy_autopilot_cycle(); legacy_c = list(CALLS)
CALLS.clear(); sc.run_pipeline(); new_c = list(CALLS)
sc.IN_COLAB = False
expect(new_c == legacy_c, f"T2 in Colab the same steps run as before: {new_c}")

# ---- isolation ----
sc._RUN["id"] = "p5r-boom"
BOOM["on"] = True
errs0 = sc._RUN.get("errors", 0)
CALLS.clear(); steps = sc.run_pipeline(); BOOM["on"] = False
plan = next(s for s in steps if s["step"] == "plan")
expect(plan["status"].startswith("error") and "run_task_queue(3)" in CALLS and CALLS[-1] == "sustainability_step",
       "T3 a failing step is recorded and every later step still runs (the old stack skipped the queue)")
expect(sc._RUN.get("errors", 0) == errs0 + 1, "T3 the failure is counted in the run log")

# ---- time and the run log ----
sc.CYCLE_DEADLINE = sc.time.time() + 300
sc._RUN["id"] = "p5r-late"
CALLS.clear(); steps = sc.run_pipeline()
expect("work_needs" not in CALLS and "self_review" not in CALLS and
       {s["step"]: s["status"] for s in steps}["needs.before"] == "skipped", "T4 steps that need 10 minutes are skipped when time is short")
d = sc._run_extras()
expect(set(d["steps"]) == {n for n, *_ in sc.RUN_PIPELINE} and d["steps"]["needs.before"] == "skipped", "T5 the run log lists every step")
expect(sc.pipeline_text().splitlines()[0].endswith("quality") and len(sc.pipeline_text().splitlines()) == len(sc.RUN_PIPELINE),
       "T5 the pipeline can be read as one list")

for n, f in saved.items():
    setattr(sc, n, f)
sc.self_review_due, sc.GITHUB._token = saved_due, saved_token
print("RESULT " + ("ALL PASS" if not FAILS else f"FAILED {len(FAILS)}"))
sys.exit(1 if FAILS else 0)
