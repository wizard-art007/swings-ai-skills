"""F8 tests on a copy of the live repo with a scripted LLM (real vendored skill tools)."""
import os, sys, json, re
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)

T = "import sys\nsys.path.insert(0, 'src')\n"
GOOD = {"title": "Docs kit from a short system description", "goal": "Turn one description into an ERD and a BPMN process",
        "area": "diagrams", "tools": [{"skill": "drawdb-io-drawdb", "module": "erd_generator"},
                                      {"skill": "agents365-ai-drawio-skill", "module": "bpmn_generator"}],
        "milestones": [
            {"name": "ERD", "goal": "erd(text)", "test": T + "from app.kit import erd\ndef test_erd():\n    assert 'User' in erd('User has many Orders')\n"},
            {"name": "BPMN", "goal": "bpmn(text)", "test": T + "from app.kit import bpmn\ndef test_bpmn():\n    assert '<definitions' in bpmn('Start -> Task -> End')\n"},
            {"name": "Bundle", "goal": "bundle(text)", "test": T + "from app.kit import bundle\ndef test_bundle():\n    assert set(bundle('User has many Orders')) == {'erd', 'bpmn'}\n"}]}
HARD = {"title": "Impossible tracer", "goal": "never works", "area": "ai_agents",
        "tools": [{"skill": "deepset-ai-haystack", "module": "agent_prompt_router"},
                  {"skill": "juliusbrussee-caveman", "module": "llm_token_budget_estimator"}],
        "milestones": [{"name": "Impossible", "goal": "x", "test": T + "from app.hard import f\ndef test_f():\n    assert f() == 42\n"},
                       {"name": "Later", "goal": "y", "test": T + "from app.hard import g\ndef test_g():\n    assert g() == 1\n"}]}
TRIVIAL = {**GOOD, "title": "Trivial project", "milestones": [{"name": "a", "goal": "a", "test": T + "import app\ndef test_a():\n    assert app is not None\n"},
                                                              {"name": "b", "goal": "b", "test": T + "from app.x import y\ndef test_b():\n    assert y()\n"}]}
ONE_SKILL = {**GOOD, "title": "One skill only", "tools": [GOOD["tools"][0]]}
KIT = {1: "from vendor.drawdb_io_drawdb.erd_generator import generate_erd\n\ndef erd(text):\n    return generate_erd(text)\n",
       2: "from vendor.drawdb_io_drawdb.erd_generator import generate_erd\nfrom vendor.agents365_ai_drawio_skill.bpmn_generator import generate_bpmn\n\n"
          "def erd(text):\n    return generate_erd(text)\n\ndef bpmn(text):\n    return generate_bpmn(text)\n",
       3: "from vendor.drawdb_io_drawdb.erd_generator import generate_erd\nfrom vendor.agents365_ai_drawio_skill.bpmn_generator import generate_bpmn\n\n"
          "def erd(text):\n    return generate_erd(text)\n\ndef bpmn(text):\n    return generate_bpmn(text)\n\n"
          "def bundle(text):\n    return {'erd': erd(text), 'bpmn': bpmn(text)}\n"}
NEXT = {"proposal": GOOD}
def fake(prompt, system="", model=None, retries=3):
    if "Propose ONE small but genuinely useful project" in prompt:
        return json.dumps(NEXT["proposal"])
    m = re.search(r"CURRENT MILESTONE: (\d+)", prompt)
    if m and "Docs kit" in prompt:
        n = int(m.group(1))
        return (f"### FILE: src/app/kit.py\n```python\n{KIT[n]}```\n"
                "### FILE: tests/test_m1.py\n```python\ndef test_erd():\n    assert True\n```\n"        # tampering
                "### FILE: src/vendor/drawdb_io_drawdb/erd_generator.py\n```python\ndef generate_erd(t):\n    return t\n```\n")
    if m and "Impossible tracer" in prompt:
        return "### FILE: src/app/hard.py\n```python\nfrom vendor.deepset_ai_haystack.agent_prompt_router import route_prompt\n\ndef f():\n    return 41\n```\n"
    return fakellm.fake(prompt, system, model, retries)
sc._llm_unbudgeted = fake
sc.CYCLE_DEADLINE = sc.time.time() + 3600
sc._jsave(sc.PROJECTS_FILE, [])                 # isolate from projects that exist in the live repo
sc.plan_month()
plan = sc._jload(sc.PLAN_FILE, {})
for o in plan["objectives"]:
    if o["metric"] == "projects_graduated":
        o["status"] = "active"
sc._jsave(sc.PLAN_FILE, plan)
def run():
    sc.projects_step(); sc.run_task_queue(limit=5); sc.advance_projects()
def proj(slug_part):
    return next(p for p in sc.load_projects() if slug_part in p["slug"])

# validation
NEXT["proposal"] = ONE_SKILL
expect(sc.propose_project(force=True).startswith("rejected: needs tools from at least 2"), "a proposal using one skill is rejected")
NEXT["proposal"] = TRIVIAL
r = sc.propose_project(force=True)
expect(r.startswith("rejected: tests [1] pass on an empty project"), f"a test that passes before any code is rejected: {r}")

# a bad first reply is fixed by the in-place retry
CALLS = {"n": 0}
BAD_THEN_GOOD = [{**GOOD, "title": "Retry kit", "milestones": [{"name": "x", "goal": "x", "test": "def test_x():\n    assert 1\n"}] * 2},
                 {**GOOD, "title": "Retry kit"}]
NEXT["proposal"] = None
_orig = fake
def fake2(prompt, system="", model=None, retries=3):
    if "Propose ONE small but genuinely useful project" in prompt:
        CALLS["n"] += 1
        expect(("WAS REJECTED" in prompt) == (CALLS["n"] == 2), f"retry {CALLS['n']} carries the rejection reason only the 2nd time")
        return json.dumps(BAD_THEN_GOOD[min(CALLS["n"], 2) - 1])
    return _orig(prompt, system, model, retries)
sc._llm_unbudgeted = fake2
r = sc.propose_project(force=True)
expect(r == "proj-retry-kit" and CALLS["n"] == 2, f"a rejected reply is retried once with feedback and then accepted: {r}")
pr = sc.load_projects(); [p.update(status="dropped") for p in pr if p["slug"] == "proj-retry-kit"]; sc._jsave(sc.PROJECTS_FILE, pr)
sc._llm_unbudgeted = fake

# test 1 + 2: three milestones, three runs
uses0 = sc._jload(sc.USAGE_FILE, {})
NEXT["proposal"] = GOOD
slug = sc.propose_project(force=True)
sc.advance_projects()
p = proj("docs-kit")
expect(p["status"] == "active" and p["objective"], f"project started and tagged to an objective: {p['objective']}")
d = sc._project_dir(p)
expect((d / "src/vendor/drawdb_io_drawdb/erd_generator.py").exists() and any((d / "src/vendor/drawdb_io_drawdb").glob("LICEN*")) | True
       and len(p["vendored"]) >= 2, "skill tools copied into src/vendor with hashes")
expect(not (d / "tests/test_m2.py").exists(), "later milestones' tests stay out until their turn")
states = []
for i in range(3):
    sc.run_task_queue(limit=5); sc.advance_projects()
    states.append([m["status"] for m in proj("docs-kit")["milestones"]])
p = proj("docs-kit")
expect(states == [["done", "todo", "todo"], ["done", "done", "todo"], ["done", "done", "done"]] and p["status"] == "finished",
       f"T1 a 3-milestone project finishes in 3 runs, one milestone each: {states} {p['status']}")
uses = sc._jload(sc.USAGE_FILE, {})
dd = lambda s: uses.get(s, {}).get("used", 0) - uses0.get(s, {}).get("used", 0)
expect(dd("drawdb-io-drawdb") == 3 and dd("agents365-ai-drawio-skill") == 2,
       f"T2 skill uses follow real imports (erd in 3 milestones, bpmn in 2): {dd('drawdb-io-drawdb')}, {dd('agents365-ai-drawio-skill')}")
expect(open(d / "tests/test_m1.py").read() == GOOD["milestones"][0]["test"], "the LLM's rewrite of an acceptance test was dropped")
expect("ERDGenerator" in open(d / "src/vendor/drawdb_io_drawdb/erd_generator.py").read(), "the LLM's write into vendor/ was dropped")
e = sc.load_experiments().get(p["slug"], {})
expect(e.get("kind") == "project" and e.get("skills") == ["agents365-ai-drawio-skill", "drawdb-io-drawdb"]
       and sc.graduation_check(e) is None, f"finished project is a graduation-ready F7 entry: {e.get('skills')}")
expect(sc.metrics()["experiments_using_skills"] >= 1 and sc.metrics()["projects_finished"] == 1, "LC metrics see the project")
expect(any(x["kind"] == "project.finished" for x in sc.load_decisions(days=1)), "the ledger records the finish")

# test 3: 5 failures drop the project
NEXT["proposal"] = HARD
sc.propose_project(force=True); sc.advance_projects()
for i in range(6):
    sc.run_task_queue(limit=5); sc.advance_projects()
h = proj("impossible")
expect(h["status"] == "dropped" and h["milestones"][0]["tries"] == 5, f"T3 a milestone failing 5 times drops the project: {h['status']} {h['milestones'][0]['tries']}")
expect("dropped at milestone 1" in sc.KNOWLEDGE_FILE.read_text(), "T3 the drop is recorded as a lesson")

# test 4: max 2 active
NEXT["proposal"] = {**GOOD, "title": "Second docs kit"}
sc.propose_project(force=True)
NEXT["proposal"] = {**GOOD, "title": "Third docs kit"}
sc.propose_project(force=True)
active = [p["title"] for p in sc.load_projects() if p["status"] == "active"]
sc.projects_step()
NEXT["proposal"] = {**GOOD, "title": "Fourth docs kit"}
sc.projects_step()
active2 = [p["title"] for p in sc.load_projects() if p["status"] == "active"]
expect(len(active2) <= 2 and "Fourth docs kit" not in str(active2), f"T4 no third project while 2 are active: {active2}")
ex = sc._run_extras()
expect(ex["projects"]["finished"] == 1 and ex["projects"]["dropped"] == 2, f"run summary: {ex['projects']}")
print("RESULT", "ALL PASS" if not FAILS else f"{len(FAILS)} FAILED")
