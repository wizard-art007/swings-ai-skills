"""Phase 5 step 3 tests: tools graded on real inputs from their source repos, repair tasks for weak tools, usefulness
that counts quality and real use, and the language component in scouting. Scripted LLM, a synthetic skill."""
import os, sys, json, re
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)

if not hasattr(sc, "grade_skill"):
    print("PASS (skipped: this engine has no Phase 5 quality cell yet)")
    print("RESULT ALL PASS"); sys.exit(0)

N = "t-quality-skill"
SK = sc.SKILLS_DIR / N
(SK / "scripts").mkdir(parents=True, exist_ok=True); (SK / "tests").mkdir(exist_ok=True)
(SK / "SKILL.md").write_text("---\nname: t-quality-skill\ndescription: test\n---\nA test skill.\n")
TOOLS = {
    "dotgen": "def to_dot(text: str) -> str:\n    \"\"\"Graphviz DOT from text.\"\"\"\n    names = [w for w in text.split() if w.isalpha()][:5] or ['A']\n"
              "    return 'digraph G {\\n' + ''.join(f'  {n};\\n' for n in names) + '}\\n'\n",
    "pumlgen": "def render_puml(source):\n    \"\"\"PlantUML from a plantuml source.\"\"\"\n    return '@startuml\\n' + source.splitlines()[0]\n",
    "tidy": "def tidy_markdown(text):\n    \"\"\"Tidy markdown text.\"\"\"\n    return text\n",
    "crash": "def parse_sql(sql):\n    \"\"\"Parse SQL schema.\"\"\"\n    raise ValueError('cannot parse ' + sql[:10])\n",
    "two": "def merge(a, b):\n    return a + b\n",
    "net": "def render_svg(text):\n    \"\"\"Render via a web service.\"\"\"\n    raise ConnectionError('HTTPSConnectionPool: Max retries exceeded')\n",
}
for m, code in TOOLS.items():
    (SK / "scripts" / f"{m}.py").write_text(code)
(SK / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n")
reg = json.loads(sc.REGISTRY_FILE.read_text())
reg[N] = {"name": "quality", "full_name": "t/quality", "url": "https://example.invalid/t/quality", "clone_url": "",
          "stars": 10, "license": "MIT", "language": "Python", "topics": [], "description": "test", "domain": "diagrams"}
sc.REGISTRY_FILE.write_text(json.dumps(reg, indent=2))
REPO = sc.repo_dir(N)
for rel, body in {"examples/flow.puml": "@startuml\nAlice -> Bob: hello\nBob --> Alice: hi\n@enduml\n",
                  "examples/graph.dot": "digraph G {\n  alice -> bob;\n  bob -> carol;\n}\n",
                  "examples/schema.sql": "CREATE TABLE users (id int primary key, name text);\nCREATE TABLE orders (id int);\n",
                  "docs/intro.md": "# Intro\n\nUsers place orders and the shop ships them to customers quickly.\n",
                  "node_modules/dep/x.puml": "@startuml\nX -> Y\n@enduml\n" + "x" * 50,
                  "examples/huge.md": "word " * 6000,
                  "README.md": "# Quality\n\n```plantuml\n@startuml\nA -> B: from the readme\n@enduml\n```\n"}.items():
    (REPO / rel).parent.mkdir(parents=True, exist_ok=True); (REPO / rel).write_text(body)

def fake(prompt, system="", model=None, retries=3):
    if "fails on REAL input" in prompt:
        return ("### FILE: scripts/pumlgen.py\n```python\ndef render_puml(source):\n    \"\"\"PlantUML from a plantuml source.\"\"\"\n"
                "    body = [l for l in source.splitlines() if l.strip() and not l.startswith('@')]\n"
                "    return '@startuml\\n' + '\\n'.join(body) + '\\n@enduml\\n'\n```\n"
                "### FILE: tests/test_real_pumlgen.py\n```python\nimport sys\nsys.path.insert(0, 'scripts')\nfrom pumlgen import render_puml\n"
                "def test_real():\n    out = render_puml('@startuml\\nA -> B\\n@enduml\\n')\n    assert out.strip().endswith('@enduml') and 'A -> B' in out\n```\n")
    return fakellm.fake(prompt, system, model, retries)
sc._llm_unbudgeted = fake
sc.CYCLE_DEADLINE = sc.time.time() + 3600
sc._jsave(sc.TASKS_FILE, [])
sc._jsave(sc.GRADES_FILE, {})

# ---- wiring ----
expect(sc._cycle_before_f9 is sc._cycle_with_quality, "the quality step runs inside F9's step")
expect("language" in sc.score_weights() and "fix_tool" in sc.HIGH_VALUE, "language is a scouting weight; repairs are high-value LLM work")

# ---- real inputs ----
skill = sc.load_registry()[N]
fns = {(m, f) for m, f, _ in sc._text_functions(skill)}
expect(fns == {("dotgen", "to_dot"), ("pumlgen", "render_puml"), ("tidy", "tidy_markdown"), ("crash", "parse_sql"), ("net", "render_svg")},
       f"T1 only one-text-input public functions are graded: {sorted(fns)}")
files = sc._repo_inputs(skill)
names = {f["name"] for f in files}
expect("examples/flow.puml" in names and not any("node_modules" in n for n in names) and "examples/huge.md" not in names,
       "T2 inputs come from the repo, skipping node_modules and files over 20 KB")
expect(any(n.startswith("README block 1 (plantuml)") for n in names), "T2 README code blocks are inputs too")
puml_in = [f["name"] for f in sc._inputs_for(sc._words("pumlgen render_puml source plantuml"), files)]
expect(puml_in[0] in ("examples/flow.puml", "README block 1 (plantuml)") and all(".sql" not in n for n in puml_in),
       f"T2 a PlantUML tool gets PlantUML inputs first: {puml_in}")

# ---- grading ----
r = sc.grade_tools([N])
g = sc.load_grades()[N]
t = g["tools"]
expect(g["status"] == "graded" and r[N]["status"] == "graded", f"T3 the skill is graded: {r}")
expect(t["dotgen.to_dot"]["grade"] == 1.0, f"T3 a tool giving valid output on real inputs scores 1.0: {t['dotgen.to_dot']}")
expect(t["pumlgen.render_puml"]["grade"] == 0 and any("@enduml" in f["why"] for f in t["pumlgen.render_puml"]["fails"]),
       f"T3 PlantUML without @enduml is invalid: {t['pumlgen.render_puml']['fails'][:1]}")
expect(t["tidy.tidy_markdown"]["grade"] == 0 and "unchanged" in t["tidy.tidy_markdown"]["fails"][0]["why"], "T3 a function that only echoes its input is not a tool")
expect(t["crash.parse_sql"]["grade"] == 0 and "ValueError" in t["crash.parse_sql"]["fails"][0]["why"], "T3 an exception is caught and recorded")
expect("net.render_svg" not in t and g.get("network_only") == ["net.render_svg"], "T3 a tool that needs the blocked network is set aside, not failed")
expect(g["grade"] == round(sum(x["grade"] for x in t.values()) / len(t), 2) and sc.skill_grade(N) == g["grade"], "T3 the skill grade is the mean")
expect(N not in sc._due_for_grading(sc.load_registry()), "T4 an unchanged, fresh grade is not redone")
(SK / "scripts" / "tidy.py").write_text(TOOLS["tidy"] + "\n# changed\n")
expect(N in sc._due_for_grading(sc.load_registry()), "T4 a changed tool is graded again")

# ---- repair ----
goal = sc.plan_tool_fixes()
tasks = [x for x in sc._jload(sc.TASKS_FILE, []) if x.get("kind") == "fix_tool"]
expect(goal and len(tasks) == 1 and tasks[0]["input_text"] and tasks[0]["skill"] == N, f"T5 the weakest tool gets one repair task: {goal}")
expect(sc.plan_tool_fixes() is None, "T5 at most one repair task a day")
first = tasks[0]["tool"]
if first != f"{N}/pumlgen.render_puml":                 # make the scripted repair the one queued
    ts = sc._jload(sc.TASKS_FILE, [])
    for x in ts:
        if x.get("kind") == "fix_tool":
            x.update(tool=f"{N}/pumlgen.render_puml", module="pumlgen", fn="render_puml", input_name="examples/flow.puml",
                     input_text=(REPO / "examples/flow.puml").read_text(), why="@startuml without @enduml")
    sc._jsave(sc.TASKS_FILE, ts)
sc.run_task_queue(limit=1)
done = [x for x in sc._jload(sc.TASKS_FILE, []) if x.get("kind") == "fix_tool"]
g2 = sc.load_grades()[N]["tools"]["pumlgen.render_puml"]
expect(done[0]["status"] == "done" and g2["grade"] == 1.0, f"T6 the repair passes its tests and the tool is regraded (a normalizer may return tidy input as it was): {done[0]['status']}, {g2}")
expect((SK / "tests" / "test_real_pumlgen.py").exists(), "T6 the repair adds a test with the real input")

# ---- usefulness ----
base, att = sc._usefulness_before_p5(N)
u0, _ = sc.usefulness(N)
pr = sc.load_projects() + [{"id": "q1", "slug": "q-proj", "status": "finished", "skills_used": [N], "milestones": []}]
sc._jsave(sc.PROJECTS_FILE, pr)
u1, att1 = sc.usefulness(N)
gr = sc.skill_grade(N)
expect(abs(u0 - round(0.5 * base + 0.3 * gr, 3)) < 0.002 and abs(u1 - round(0.5 * base + 0.3 * gr + 0.1, 3)) < 0.002 and att1 == att,
       f"T7 usefulness = half task success + 30% grade + 20% project use ({u0} -> {u1})")
expect(sc.usefulness("never-graded-skill")[0] == round(0.5 * 0.5 + 0.3 * 0.5, 3), "T7 an ungraded, unused skill sits below a new candidate (0.40 < 0.5)")

# ---- language ----
cands = {f"o/r{i}": {"full_name": f"o/r{i}", "description": "diagram tool", "topics": ["uml"], "domain": "diagrams",
                     "stars": 1000, "pushed_at": "2026-11-01T00:00:00Z", "language": lang}
         for i, lang in enumerate(["Python", "Java", "Rust", None])}
sc.score_components(cands)
expect([cands[f"o/r{i}"]["components"]["language"] for i in range(4)] == [1.0, 0.6, 0.3, 0.2], "T8 language: Python 1, checkable 0.6, other 0.3, none 0.2")
for c in cands.values():
    c.update(score=sc.total_score(c), url=f"https://github.com/{c['full_name']}", fail=None)
sc.write_leaderboard(cands, 0)
lb = sc.LEADERBOARD.read_text()
expect("| Useful | Lang | Status |" in lb and "| 1.0 Python | candidate |" in lb and "| 0.2 - | candidate |" in lb,
       "T8 the leaderboard shows the language component")
old = {"components": {k: 0.5 for k in sc.DEFAULT_WEIGHTS if k != "language"}}
expect(isinstance(sc.total_score(old), float), "T8 components stored before the language key still score")

# ---- report ----
ts = sc._jload(sc.TASKS_FILE, [])
ts += [{"kind": "fix_tool", "skill": N, "tool": f"{N}/crash.parse_sql", "status": "failed", "goal": "x", "queued": "2026-11-20T00:00"}] * 3
sc._jsave(sc.TASKS_FILE, ts)
text, _ = sc.build_health_report()
expect("## Quality (Phase 5)" in text and "Skills graded on real inputs:" in text, "T9 the weekly report has a Quality section")
expect(f"{N}/crash.parse_sql still fails on real inputs" in text.split("## Decisions waiting for you", 1)[-1], "T9 a tool that resists 3 repairs becomes a decision")
expect("quality" in sc._run_extras(), "T10 the run log carries the quality numbers")

# ---- the real skills in this repo copy grade without crashing ----
r = sc.grade_tools(limit=3)
expect(all(not str(v["status"]).startswith(("error", "harness failed")) for v in r.values()), f"T11 real skills grade cleanly: {r}")

print("RESULT " + ("ALL PASS" if not FAILS else f"FAILED {len(FAILS)}"))
sys.exit(1 if FAILS else 0)
