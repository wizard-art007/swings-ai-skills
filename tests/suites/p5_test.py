"""Phase 5 (step 1 engine side + step 2) tests: the test result is read, idle runs get a second work pass, and news
experiments are built on the system's own skill tools. Scripted LLM, real vendored tools, a copy of the live repo."""
import os, sys, json, re, hashlib
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)

if not hasattr(sc, "build_experiment_skilled"):
    print("PASS (skipped: this engine has no Phase 5 cell yet)")
    print("RESULT ALL PASS"); sys.exit(0)

T = "import sys\nsys.path.insert(0, 'src')\n"
GOOD = {"title": "Docs kit from a short system description", "goal": "Turn one description into an ERD and a BPMN process",
        "area": "diagrams", "tools": [{"skill": "drawdb-io-drawdb", "module": "erd_generator"},
                                      {"skill": "agents365-ai-drawio-skill", "module": "bpmn_generator"}],
        "milestones": [
            {"name": "ERD", "goal": "erd(text)", "test": T + "from app.kit import erd\ndef test_erd():\n    assert 'User' in erd('User has many Orders')\n"},
            {"name": "BPMN", "goal": "bpmn(text)", "test": T + "from app.kit import bpmn\ndef test_bpmn():\n    assert '<definitions' in bpmn('Start -> Task -> End')\n"}]}
KIT = {1: "from vendor.drawdb_io_drawdb.erd_generator import generate_erd\n\ndef erd(text):\n    return generate_erd(text)\n",
       2: "from vendor.drawdb_io_drawdb.erd_generator import generate_erd\nfrom vendor.agents365_ai_drawio_skill.bpmn_generator import generate_bpmn\n\n"
          "def erd(text):\n    return generate_erd(text)\n\ndef bpmn(text):\n    return generate_bpmn(text)\n"}
MODE = {"exp": "skilled"}                                          # skilled | plain | plain_then_skilled | tamper
SEEN = []
def fake(prompt, system="", model=None, retries=3):
    if "Propose ONE small but genuinely useful project" in prompt:
        return json.dumps(GOOD)
    m = re.search(r"CURRENT MILESTONE: (\d+)", prompt)
    if m and "Docs kit" in prompt:
        return f"### FILE: src/app/kit.py\n```python\n{KIT[int(m.group(1))]}```\n"
    if "Build a small experimental project" in prompt:
        SEEN.append(prompt)
        plain = MODE["exp"] == "plain" or (MODE["exp"] == "plain_then_skilled" and "USED NO SKILL TOOL" not in prompt)
        if plain:
            return ("### FILE: src/idea.py\n```python\ndef run(x):\n    return x\n```\n"
                    "### FILE: tests/test_idea.py\n```python\nimport sys\nsys.path.insert(0, 'src')\nfrom idea import run\n"
                    "def test_run():\n    assert run(1) == 1\n```\n")
        out = fakellm.fake(prompt, system, model, retries)
        if MODE["exp"] == "tamper":
            pkg, mod = re.search(r"`from vendor\.(\w+)\.(\w+) import", prompt).groups()
            out += f"### FILE: src/vendor/{pkg}/{mod}.py\n```python\ndef hacked():\n    return 1\n```\n"
        return out
    return fakellm.fake(prompt, system, model, retries)
sc._llm_unbudgeted = fake
sc.CYCLE_DEADLINE = sc.time.time() + 3600
sc._jsave(sc.PROJECTS_FILE, [])
sc._jsave(sc.TASKS_FILE, [])
sc._jsave(sc.P5_STATE, {})

# ---- wiring ----
expect(sc._cycle_before_f9 is sc._cycle_with_phase5, "the Phase 5 step runs inside F9's step (before the limits snapshot)")
expect(sc.PROPOSALS_PER_DAY == 3 and sc.PROPOSAL_ATTEMPTS_PER_DAY == 5, "up to 3 projects a day, 5 proposal attempts")
expect(getattr(sc._build_experiment_unplanned, "_experienced", False), "news experiments go through the skilled builder, still recorded as experiences")

# ---- tool choice ----
tools = sc._experiment_tools("an ERD generator for database entity relationship diagrams")
expect(len(tools) == 3 and len({t["skill"] for t in tools}) == 3, f"3 tools from 3 different skills are offered: {[t['skill'] for t in tools]}")
expect(tools[0]["skill"] == "drawdb-io-drawdb", f"the best word match comes first: {tools[0]['skill']}/{tools[0]['module']}")

# ---- an experiment built on a skill tool ----
usage0 = sc._jload(sc.USAGE_FILE, {})
r = sc._build_experiment_unplanned("ERD sketcher", "draws entity relationship diagrams for a database")
e = sc.load_experiments().get(r["slug"], {})
d = sc.EXPERIMENTS_DIR / r["slug"]
expect(r["status"] == "passed" and e.get("skills"), f"T1 the experiment passes and records the skills it imports: {r}")
expect((d / "src" / "vendor").is_dir() and any((d / "src" / "vendor").iterdir()), "T1 the offered tools are copied into src/vendor/")
expect("SKILL TOOLS YOU MUST BUILD ON" in SEEN[-1] and "from vendor." in SEEN[-1], "T1 the prompt lists the tools and requires one")
usage1 = sc._jload(sc.USAGE_FILE, {})
expect(all(usage1.get(s, {}).get("used", 0) == usage0.get(s, {}).get("used", 0) + 1 for s in e["skills"]), "T1 skill usage is counted")
expect(any(x.get("kind") == "experiment" and "ERD sketcher" in x.get("goal", "") for x in sc._load_experiences(50)),
       "T1 the experiment is recorded as an experience")

# ---- no skill tool: one retry, then failed ----
MODE["exp"] = "plain"; n0 = len(SEEN)
r = sc.build_experiment_skilled("Plain idea", "a helper that uses nothing")
e = sc.load_experiments()[r["slug"]]
expect(r["status"] == "failed" and e.get("note") == "uses no skill tool", f"T2 code that imports no skill tool is failed: {r}")
expect(len(SEEN) - n0 == 2 and "USED NO SKILL TOOL" in SEEN[-1], f"T2 it got exactly one retry, told why ({len(SEEN) - n0} calls)")

MODE["exp"] = "plain_then_skilled"
r = sc.build_experiment_skilled("Second chance", "a sequence diagram helper")
expect(r["status"] == "passed" and r.get("skills"), f"T3 a retry that adds a skill tool passes: {r}")

# ---- the vendored tools are read-only ----
MODE["exp"] = "tamper"
r = sc.build_experiment_skilled("Tamper attempt", "an ERD tool that rewrites its vendored helper")
d = sc.EXPERIMENTS_DIR / r["slug"]
reg = sc.load_registry()
same = all((d / "src" / "vendor" / sc._vendor_pkg(t.split("/")[0]) / f"{t.split('/')[1]}.py").read_text()
           == (sc.Path(reg[t.split("/")[0]]["path"]) / "scripts" / f"{t.split('/')[1]}.py").read_text()
           for t in sc.load_experiments()[r["slug"]]["tools_offered"])
expect(r["status"] == "passed" and same, "T4 an LLM write into src/vendor/ is dropped; the vendored tools stay identical")
expect(sc.parse_files("### FILE: src/vendor/x.py\n```python\nx=1\n```") == {"src/vendor/x.py": "x=1\n"},
       "T4 parse_files is restored after the build")
MODE["exp"] = "skilled"

# ---- the more-work pass ----
sc._RUN["id"] = "p5-run-1"
st = sc.more_work_pass()
pr = sc.load_projects()
expect(st["proposed"] == 1 and len(pr) == 1 and pr[0]["status"] in ("active", "finished"),
       f"T5 an empty queue with no active project starts one in the same run: {st}")
done = [m["n"] for m in pr[0]["milestones"] if m["status"] == "done"]
expect(st["extra_rounds"] >= 1 and done[:1] == [1], f"T5 and works its first milestone in the extra round (done {done}, rounds {st['extra_rounds']})")

sc._RUN["id"] = "p5-run-2"
sc.CYCLE_DEADLINE = sc.time.time() + 600
st = sc.more_work_pass()
expect(st["extra_rounds"] == 0 and st["proposed"] == 0, "T6 no extra round when under 15 minutes are left")
sc.CYCLE_DEADLINE = sc.time.time() + 3600

# ---- useful runs ----
sc._RUN["id"] = "p5-run-3"
sc._save_experience({"id": "p5x", "ts": sc._now_min(), "run": "p5-run-3", "kind": "write_tool", "outcome": "done", "goal": "g"})
a = sc.record_useful_run()
sc._RUN["id"] = "p5-run-4"
sc._save_experience({"id": "p5y", "ts": sc._now_min(), "run": "p5-run-4", "kind": "agent:news_scout", "outcome": "done", "goal": "g"})
b = sc.record_useful_run()
o = sc.output_stats()
expect(a["useful"] and not b["useful"], "T7 a run that finished a task is useful; agents' chatter alone is not")
expect(o["runs"] == 2 and o["useful_runs"] == 1 and o["useful_share"] == 0.5, f"T7 output stats count useful runs: {o['useful_runs']}/{o['runs']}")
expect(o["experiments_7d_with_skills"] >= 3 and o["skills_used_total"] >= 1, "T7 experiments and skills used are counted")

# ---- the test result ----
class R:
    def __init__(self, code, data): self.status_code, self._d, self.ok = code, data, code == 200
    def json(self): return self._d
CALLS = []
def fake_get(url, headers=None, params=None, timeout=None):
    CALLS.append(url)
    return R(200, {"workflow_runs": [
        {"status": "in_progress", "conclusion": None, "run_number": 9},
        {"status": "completed", "conclusion": "failure", "run_number": 8, "head_sha": "abcdef123456",
         "updated_at": "2026-11-28T04:50:00Z", "html_url": "https://github.com/o/r/actions/runs/8"}]})
plain_get, env_t = sc.requests.get, os.environ.pop("SWINGS_TESTING")
os.environ["GITHUB_REPOSITORY"] = "o/r"
sc.requests.get = fake_get
try:
    ci = sc.ci_status()
finally:
    sc.requests.get = plain_get; os.environ["SWINGS_TESTING"] = env_t
expect(CALLS and CALLS[0].endswith("/repos/o/r/actions/workflows/tests.yml/runs"), "T8 the tests workflow's runs are read")
expect(ci.get("conclusion") == "failure" and ci.get("run") == 8 and ci.get("sha") == "abcdef1",
       f"T8 the latest FINISHED run is kept, not the one in progress: {ci}")
expect(sc.ci_status() == ci, "T8 inside the tests no request is made (the stored result is returned)")

text, verdict = sc.build_health_report()
expect("## Output (Phase 5)" in text and "Runs that did real work: 1 of 2" in text, "T9 the weekly report has an Output section")
dec = text.split("## Decisions waiting for you", 1)[-1]
expect("run #8" in text and "fix it before the next export" in dec, "T9 a failed test run becomes a decision for the owner")
st_ = sc._jload(sc.P5_STATE, {}); st_["ci"]["conclusion"] = "success"; sc._jsave(sc.P5_STATE, st_)
text, _ = sc.build_health_report()
expect("fix it before the next export" not in text, "T9 a passing test run asks nothing")

ex = sc._run_extras()
expect("phase5" in ex and set(ex["phase5"]) >= {"extra_rounds", "proposed", "experiments_with_skills", "ci"}, "T10 the run log carries the Phase 5 numbers")

print("RESULT " + ("ALL PASS" if not FAILS else f"FAILED {len(FAILS)}"))
sys.exit(1 if FAILS else 0)
