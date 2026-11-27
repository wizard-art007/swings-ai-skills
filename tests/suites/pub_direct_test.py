import os, sys, json
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
CALLS = []
sc._llm_unbudgeted = lambda p, **k: (CALLS.append(p[:40]), fakellm.fake(p, **k))[1]
published = []
sc.publish_to_projects_repo = lambda slugs, dry_run=None: (published.extend(slugs), {"published": list(slugs), "refused": {}})[1]
sc.GITHUB._token = lambda: "t"
sc.CYCLE_DEADLINE = sc.time.time() + 3600
slug = next(s for s, e in sc.load_experiments().items() if e["status"] == "passed")
sc.emit("experiment.ready", {"slug": slug})
n0 = len(CALLS)
sc.orchestrator_tick()
rows = [json.loads(l) for l in open(sc.STATE_DIR / "agent_runs.jsonl")][-3:]
pub = [r for r in rows if r["agent"] == "publisher"]
print("PASS" if slug in published and pub and pub[-1].get("direct") and pub[-1]["success"] else "FAIL",
      "publisher publishes directly:", published, pub[-1:] )
print("PASS" if not any("publisher" in c.lower() for c in CALLS[n0:]) else "FAIL", "no LLM call for the publisher;",
      len(CALLS) - n0, "calls by other agents")
import subprocess as _sp  # noqa
_ok = published and not any("publisher" in c.lower() for c in CALLS[n0:])
print("RESULT", "ALL PASS" if _ok else "1 FAILED")
