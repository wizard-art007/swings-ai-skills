"""LC tests on a copy of the live repo with a scripted LLM."""
import os, sys, json, datetime, re
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)
SYSTEMS = []
def fake(prompt, system="", model=None, retries=3):
    SYSTEMS.append(system)
    if "Set 3 to 5 objectives" in prompt:
        return json.dumps({"objectives": [
            {"title": "Reach full QA capability", "area": "qa_testing", "metric": "capability_score:qa_testing", "target": 1.0, "why": "flake hunter missing"},
            {"title": "Graduate one skill-based project", "area": "", "metric": "projects_graduated", "target": 1, "why": "F8"},
            {"title": "Zero publish failures", "area": "", "metric": "publish_failures_7d", "target": 0, "why": "F7"},
            {"title": "bogus", "metric": "not_a_metric", "target": 3}]})
    if "memory of this system" in prompt:
        return "Week summary: the publisher prompt changed twice; F7 shipped."
    return fakellm.fake(prompt, system, model, retries)
sc._llm_unbudgeted = fake
sc.CYCLE_DEADLINE = sc.time.time() + 3600
sc.backfill_ledger()

# 1. ledger lines with reason + evidence
reg = sc._jload(sc.REGISTRY_FILE, {})
victim = sorted(reg)[0]
arch = sc._jload(sc.ARCHIVE_FILE, {})
arch[victim] = {**reg.pop(victim), "archived": str(datetime.date.today()), "reason": "score 50.0 < cut-off 66.0", "score": 50.0}
sc._jsave(sc.REGISTRY_FILE, reg); sc._jsave(sc.ARCHIVE_FILE, arch)
needs = sc._jload(sc.NEEDS_FILE, [])
needs.append({"id": "eeee0001", "need": "test need", "type": "external", "status": "open", "priority": 1})
sc._jsave(sc.NEEDS_FILE, needs); sc.commit_skills("add test need")
needs = sc._jload(sc.NEEDS_FILE, [])
for n in needs:
    if n["id"] == "eeee0001":
        n["status"] = "parked"; n["log"] = [{"ts": "x", "to": "parked", "why": "not a tool"}]
sc._jsave(sc.NEEDS_FILE, needs)
sc.commit_skills("test: archive + park")
d = {x["kind"] + ":" + x["target"]: x for x in sc.load_decisions(days=1)}
expect(f"skill.archived:{victim}" in d and "cut-off" in d[f"skill.archived:{victim}"]["why"], "T1 archiving a skill writes a ledger line with its reason")
expect("need.parked:eeee0001" in d and d["need.parked:eeee0001"]["why"] == "not a tool", "T1 parking a need writes a ledger line with its reason")
r = sc._update_prompt_unguarded("builder", "You are the Builder. v2 test prompt.", "test change")
d = [x for x in sc.load_decisions(days=1, target="builder") if x["kind"] == "agent.prompt"]
expect(d and d[-1]["why"] == "test change" and "old_prompt" in d[-1]["evidence"], "T1 a prompt change is recorded with old and new prompt")

# 2. prompt guard
r = sc.TOOLS.call("update_agent_prompt", {"name": "builder", "new_prompt": "You are the Builder. v3.", "reason": "again"}, ["update_agent_prompt"])
expect("blocked" in r and sc.load_agents()["builder"].version == 2, f"T2 second change to one agent within 3 days blocked: {r[:70]}")
sc._jsave(sc.OVERRIDES_FILE, [{"kind": "agent.prompt", "target": "builder", "ts": sc._now_min()}])
r = sc.TOOLS.call("update_agent_prompt", {"name": "builder", "new_prompt": "You are the Builder. v3.", "reason": "approved"}, ["update_agent_prompt"])
expect("v3" in r, f"T2 an override lets it through: {r}")
sc._jsave(sc.OVERRIDES_FILE, [])
bad = "You are the Publisher. A BAD PROMPT that did worse and was rolled back by the system."
sc.record_decision("agent.rollback", "news_scout", "v2 -> v3", "auto-rollback", evidence={"old_prompt": bad}, ts="2026-11-01T00:00")
why = sc.guard_prompt_change("news_scout", bad + " ")
expect(why and "rolled back" in why, f"T2 returning to a rolled-back prompt blocked: {why}")

# 3. skill churn
sc._jsave(sc.SCORES_FILE, {"candidates": [{"full_name": arch[victim]["full_name"], "score": 52.0}]})
proj = {k: arch[victim].get(k) for k in ("name", "full_name", "url", "clone_url", "stars", "license", "language", "topics", "description", "default_branch")}
proj = {k: (v if v is not None else ([] if k == "topics" else "")) for k, v in proj.items()}
try:
    sc.save_as_skill(proj, clone=False); expect(False, "T3 re-add at the same score blocked")
except sc.GuardBlocked as e:
    expect("has not risen" in str(e), "T3 re-adding an archived skill at about the same score is blocked")
sc._jsave(sc.SCORES_FILE, {"candidates": [{"full_name": arch[victim]["full_name"], "score": 60.0}]})
ok = sc.save_as_skill(proj, clone=False)
expect(ok["skill_name"] == victim, "T3 re-added once its score rose past the archive margin")

# weights see-saw
w0 = {k: v for k, v in sc._jload(sc.WEIGHTS_FILE, {}).items() if not k.startswith("_")} or dict(sc.DEFAULT_WEIGHTS)
sc._jsave(sc.WEIGHTS_FILE, {**w0, "_history": []})
sc.tune_score_weights("fit", 3, "more fit")
f1 = sc.score_weights()["fit"]
sc.tune_score_weights("fit", -3, "less fit")
expect(abs(sc.score_weights()["fit"] - f1) < 0.6, f"T3 weight reversal within 3 days blocked (fit {f1} -> {sc.score_weights()['fit']})")

# contradicting rule
rules = sc._jload(sc.RULES_FILE, {})
rules.setdefault("write_tool", []).append({"text": "Always mock the network in tool tests", "status": "active", "uses": 0, "ok": 0, "created": "2026-11-01T00:00"})
rules["write_tool"].append({"text": "Never mock the network in tool tests", "status": "active", "uses": 0, "ok": 0, "created": sc._now_min()})
sc._jsave(sc.RULES_FILE, rules)
sc.promote_and_demote_rules()
st = {r["text"]: r["status"] for r in sc._jload(sc.RULES_FILE, {})["write_tool"]}
expect(st["Never mock the network in tool tests"] == "flagged" and st["Always mock the network in tool tests"] == "active",
       "T3 a new rule that contradicts an active one is flagged")

# parked need repeated by the review
caps = sc._jload(sc.CAPABILITIES_FILE, [])
miss = next(c for c in caps if c["status"] in ("missing", "weak"))
needs = sc._jload(sc.NEEDS_FILE, [])
needs.append({"id": "eeee0002", "need": miss["name"], "capability": miss["id"], "type": "external", "status": "parked", "tries": 3})
needs = [n for n in needs if not (n.get("capability") == miss["id"] and n.get("status") == "open")]
sc._jsave(sc.NEEDS_FILE, needs)
created = sc._sync_needs([{"title": miss["name"], "type": "external", "capability": miss["id"], "evidence": ["x"], "priority": 2, "action": "a"}], caps)
new = [n for n in sc._jload(sc.NEEDS_FILE, []) if n["id"] in {c["id"] for c in created}]
expect(new and new[0]["status"] == "parked" and "repeats parked need" in new[0]["log"][-1]["why"], "T3 a parked need is not reopened without new evidence")

# 4. invariants
sc.HEAL_PROTECTED.discard("revert_heal")
inv = {i["name"]: i for i in sc.check_invariants()}
expect(not inv["healer cannot touch the guard rails"]["ok"] and inv["healer cannot touch the guard rails"]["repaired"]
       and "revert_heal" in sc.HEAL_PROTECTED, "T4 a protected function missing from the healer's list is reported and repaired")
needs = sc._jload(sc.NEEDS_FILE, []); needs.append({"id": "eeee0003", "need": "x", "status": "searching", "updated": "2026-11-01T00:00"})
sc._jsave(sc.NEEDS_FILE, needs)
inv = {i["name"]: i for i in sc.check_invariants()}
expect(inv["no need stuck in searching"]["repaired"] and next(n for n in sc._jload(sc.NEEDS_FILE, []) if n["id"] == "eeee0003")["status"] == "open",
       "T4 a need stuck in searching is reported and released")
real_dom = dict(sc.MISSION["domains"]); sc.MISSION["domains"]["finance"] = {"about": "x", "queries": []}
inv = {i["name"]: i for i in sc.check_invariants()}
expect(not inv["mission areas unchanged"]["ok"], "T4 a changed mission is an invariant failure (not auto-repaired)")
sc.MISSION["domains"].clear(); sc.MISSION["domains"].update(real_dom)

# 5. charter in every prompt
plan = sc.plan_month(force=True)
ids = [(o["id"], o["metric"]) for o in plan["objectives"]]
expect(len(ids) == 3 and ("O1", "capability_score:qa_testing") in ids, f"LC4 plan keeps the 3 valid objectives, drops the bogus one: {ids}")
SYSTEMS.clear()
sc.run_agent("planner", "test task")
expect(SYSTEMS and SYSTEMS[0].startswith("# Swings AI charter"), "T5 an agent's system prompt starts with the charter")
expect("This month's objectives: O1 Reach full QA capability" in sc.charter_text(), "T5 the charter carries this month's objectives")
fixed_before = sc.charter_text().split("Now:")[0]
sc.build_charter()
expect(sc.charter_text().split("Now:")[0] == fixed_before and len(sc.charter_text()) <= 1500, "T5 the fixed part is unchanged after a rebuild; under 1,500 chars")
SYSTEMS.clear()
with sc._as_purpose("heal"):
    sc.llm("fix", system="HEAL SYSTEM")
expect(SYSTEMS[-1] == "HEAL SYSTEM", "T5 heal prompts are left exact (no charter)")

# 6. plan steers work
sc.add_task("write_tool", "microsoft-playwright", "a flaky test detector for pytest runs")
sc.add_task("write_tool", "plantuml-plantuml", "zzz")
ts = sc._jload(sc.TASKS_FILE, [])
a, b = ts[-2], ts[-1]
expect(a.get("objective") == "O1", f"T6 a QA task is tagged to the QA objective: {a.get('objective')}")
b["objective"] = None; a2 = dict(a); a2["objective"] = "O1"
expect(sc.task_value(a2) > sc.task_value({**a2, "objective": None}), "T6 a task tagged to an active objective is worth more")
exps = sc.load_experiments()
for k in list(exps):
    if str(exps[k].get("created", "")).startswith(str(datetime.date.today())):
        exps[k]["created"] = "2026-11-01T00:00"
sc._jsave(sc.EXPERIMENTS_FILE, exps)
r1 = sc.TOOLS.call("build_experiment", {"title": "Recipe Shuffler", "description": "shuffles cooking recipes"}, ["build_experiment"])
r2 = sc.TOOLS.call("build_experiment", {"title": "Garden Planner", "description": "plans flower beds"}, ["build_experiment"])
expect(r1["status"] == "passed" and r2["status"] == "deferred", f"T6 the 2nd off-plan idea of the day is deferred: {r1['status']}, {r2['status']}")
r3 = sc.TOOLS.call("build_experiment", {"title": "Flaky test detector", "description": "find flaky pytest tests from rerun history"}, ["build_experiment"])
expect(r3["status"] == "passed" and sc.load_experiments()[r3["slug"]].get("objective") == "O1", "T6 an on-plan idea is still built and tagged")

# 7. weekly memory + trimming
sc.write_daily_digest(str(datetime.date.today()))
f = sc.write_summary("weekly", key="2026-W48")
txt = f.read_text()
expect("publisher prompt changed twice" in txt and "agent.prompt builder" in txt, "T7 weekly summary uses the LLM text plus the ledger")
with open(sc.AGENT_LOG, "a") as fh:
    fh.write("- 2026-10-01 10:00 — very old line\n")
n = sc.trim_agent_log()
expect(n >= 1 and "very old line" not in sc.AGENT_LOG.read_text() and sc.DECISIONS_FILE.stat().st_size > 0,
       "T7 raw log lines older than 14 days are trimmed after a weekly summary; the ledger stays")
ex = sc._run_extras()
expect("objectives" in ex and "work_on_plan" in ex and ex["guard_blocked"], f"run summary carries coherence metrics: {list(ex['objectives'])}")
print("RESULT", "ALL PASS" if not FAILS else f"{len(FAILS)} FAILED")
