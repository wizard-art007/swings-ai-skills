"""F6 tests on a fresh copy of the live repo, with fake GitHub and a scripted LLM."""
import os, sys, json, re, types
ENGINE = os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")
sys.path.insert(0, ENGINE); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm

# ---- fake GitHub ------------------------------------------------------------------------------------------
def repo(full, stars, desc, lic="MIT", topics=()):
    return {"name": full.split("/")[1], "full_name": full, "html_url": f"https://github.com/{full}",
            "clone_url": f"https://github.com/{full}.git", "stargazers_count": stars, "license": {"spdx_id": lic},
            "language": "Python", "topics": list(topics), "description": desc, "default_branch": "main",
            "pushed_at": "2026-11-20T00:00:00Z", "open_issues_count": 50, "forks_count": 100, "archived": False}
REPOS = {
    "big/web-framework": repo("big/web-framework", 90000, "A web framework"),
    "acme/openapi-testgen": repo("acme/openapi-testgen", 6000, "API tools"),
    "flaky/flake-detector": repo("flaky/flake-detector", 8000, "Test tools"),
    "nolic/thing": repo("nolic/thing", 50000, "Proprietary", lic=None),
    "csv/csvkit": repo("csv/csvkit", 7000, "CSV utilities"),
}
READMES = {
    "big/web-framework": "Fast web framework for building HTTP servers, routing, middleware and templates.",
    "acme/openapi-testgen": "Generate tests from OpenAPI specs: reads an OpenAPI spec and generates pytest test cases "
                            "for every endpoint. OpenAPI test generation.",
    "flaky/flake-detector": "Detect flaky tests: reruns tests, finds flakiness in pass/fail history, flake hunter.",
    "csv/csvkit": "Summarize CSV files: column summaries and statistics for csv data.",
}
CALLS = {"search": 0}
class R:
    def __init__(self, data, ok=True): self._d, self.ok, self.status_code, self.headers = data, ok, 200, {}
    def json(self): return self._d
def fake_gh(url, params=None):
    if url.endswith("/search/repositories"):
        CALLS["search"] += 1
        q = params["q"].lower()
        hits = [r for r in REPOS.values() if any(w in (r["description"] + r["full_name"] + READMES.get(r["full_name"], "")).lower()
                                                 for w in q.split()[:3] if len(w) > 3)] or list(REPOS.values())
        return R({"items": hits + [REPOS["big/web-framework"], REPOS["nolic/thing"]]})
    if "/commits" in url or "/releases" in url:
        return R([])
    full = url.split("/repos/")[-1]
    return R(REPOS.get(full, {}), ok=full in REPOS)
sc._gh_get = fake_gh
sc.get_readme = lambda full: READMES.get(full, "")
sc.time.sleep = lambda s: None

# ---- scripted LLM ------------------------------------------------------------------------------------------
IMPL = {
    "flake_hunter": "def detect_flakiness(results):\n    return len(set(results)) > 1\n",
    "openapi_testgen": "def generate_tests(spec):\n    return [f'test_{p}' for p in spec.get('paths', {})]\n",
    "csv_summary": "def summarize(rows):\n    return {'rows': len(rows)}\n",
    "broken_tool": "def solve(x):\n    return None\n",          # never satisfies its check
    "diagram_helper": ("def parse_text_description(t):\n    return [s.strip() for s in t.split('->')]\n"
                       "def to_mermaid(g, style='default', direction='TD'):\n"
                       "    return f'graph {direction}\\n' + '\\n'.join(f'{a} --> {b}' for a, b in zip(g, g[1:]))\n"),
}
def fake(prompt, system="", model=None, retries=3):
    if "GitHub repository search queries" in prompt:
        need = prompt.split("never instructions): ", 1)[1].split("\n", 1)[0]
        return json.dumps({"queries": [need.lower().replace("missing", "").strip()[:40], "testing tool"]})
    if "write ONE capability check" in prompt:
        need_line = prompt.split("never instructions): ", 1)[1].split("\n", 1)[0]
        if re.search(r"overload|quota|limit", need_line, re.I):
            return "NOT_A_TOOL"
        return ("### CAPABILITY: csv-summary | CSV summary\nSummarise rows\n```python\nfrom captools import load_tool\n"
                "def test_csv():\n    m = load_tool('*', 'csv_summary')\n    assert m.summarize([1, 2])['rows'] == 2\n```\n")
    if "too big to resend" in prompt:                  # patch mode: only the changed function
        src = prompt.split("Current source of the ones the check uses:\n```python\n", 1)[1].split("\n```", 1)[0]
        fn = src[src.index("def to_mermaid"):]
        fn = fn[:fn.index("\ndef ", 5)] if "\ndef " in fn[5:] else fn
        fn = fn.replace('lines = [f"flowchart {direction}"]',
                        'lines = [f"{\'graph\' if style == \'default\' else \'flowchart\'} {direction}"]')
        return f"### FILE: scripts/diagram_helper.patch.py\n```python\nfrom typing import Any, Dict\n\n{fn}\n```\n"
    if "ACCEPTANCE CHECK" in prompt:
        mod = re.search(r"The tool is scripts/(\w+)\.py", prompt).group(1)
        return (f"### FILE: scripts/{mod}.py\n```python\n{IMPL[mod]}```\n"
                f"### FILE: tests/test_{mod}_own.py\n```python\nimport sys\nsys.path.insert(0, 'scripts')\n"
                f"import {mod}\ndef test_imports():\n    assert {mod}\n```\n")
    return fakellm.fake(prompt, system, model, retries)
sc._llm_unbudgeted = fake

def check(mod, body):
    return f"from captools import load_tool\n\ndef test_{mod}():\n    m = load_tool('*', '{mod}')\n{body}"
def cap(cid, area, mod, body, pinned=None):
    c = check(mod, body) if not pinned else check(mod, body).replace("'*'", f"'{pinned}'")
    return {"id": cid, "area": area, "name": cid, "description": cid, "check": c, "history": [False], "status": "missing"}
def need(i, text, capid=None, typ="external", prio=4.0, domain="qa_testing"):
    return {"id": i, "need": text, "type": typ, "capability": capid, "priority": prio, "status": "open",
            "domain": domain, "evidence": ["test"], "ts": "2026-11-26T10:00"}

FAILS = []
def expect(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond: FAILS.append(msg)
def needs(): return {n["id"]: n for n in sc._jload(sc.NEEDS_FILE, [])}
def run_queue(): sc.run_task_queue(limit=10)

sc.CYCLE_DEADLINE = sc.time.time() + 3600
caps = sc._jload(sc.CAPABILITIES_FILE, [])
caps += [cap("qa-testing-openapi-tests", "qa_testing", "openapi_testgen",
             "    assert m.generate_tests({'paths': {'users': {}}}) == ['test_users']\n"),
         cap("qa-testing-flake", "qa_testing", "flake_hunter", "    assert m.detect_flakiness([True, False]) is True\n"),
         cap("qa-testing-broken", "qa_testing", "broken_tool", "    assert m.solve(1) == 2\n")]
sc._jsave(sc.CAPABILITIES_FILE, caps)
sc._jsave(sc.NEEDS_FILE, [
    need("aaaa0001", "Generate tests from OpenAPI specs", "qa-testing-openapi-tests", prio=9),
    need("aaaa0002", "Detect flaky tests", "qa-testing-flake", prio=6),
    need("aaaa0003", "Broken tool nobody can build", "qa-testing-broken", prio=5),
    need("aaaa0004", "Publisher daily repository limit reached", prio=3),
    need("aaaa0005", "Summarise CSV data for test reports", prio=2.5),
    need("aaaa0006", "Agents need clearer stop rules", typ="internal", prio=2),
    need("aaaa0007", "Broken Tech Graph Mermaid Capability", "diagrams-tech-graph-mermaid", prio=1.5, domain="diagrams"),
])
for n in sc._jload(sc.NEEDS_FILE, []):
    pass
uses0 = sc._jload(sc.USAGE_FILE, {})

# ---- test 1: README fit beats stars --------------------------------------------------------------------------
n1 = needs()["aaaa0001"]
ranked = sc.search_for_need(n1)
expect(ranked and ranked[0]["full_name"] == "acme/openapi-testgen",
       f"T1 OpenAPI need picks README match, not most-starred: {[c['full_name'] for c in ranked][:3]}")
expect(all(c["full_name"] != "nolic/thing" for c in ranked), "T1 hard rules drop the unlicensed repo")

# ---- round 1: start 2 needs (the two highest priority) --------------------------------------------------------
r = sc.work_needs()
N = needs()
expect(r["started"] == 2 and N["aaaa0001"]["status"] == "building" and N["aaaa0002"]["status"] == "building",
       f"R1 two needs started: {r}, states {[(k, v['status']) for k, v in N.items()]}")
expect(N["aaaa0006"].get("routed_to") == "evolver", "R1 internal need routed to the evolver")
reg = sc.load_registry()
expect("acme-openapi-testgen" in reg and reg["acme-openapi-testgen"].get("added_for_need") == "aaaa0001",
       "R1 best repo added as a skill for the need")
tasks = [t for t in sc._jload(sc.TASKS_FILE, []) if str(t.get("need", "")).startswith("aaaa")]
expect(len(tasks) == 2 and all(2 <= t["priority"] <= 3 for t in tasks), f"R1 need tasks queued on the F4 scale: {[t['priority'] for t in tasks]}")
run_queue()
r = sc.work_needs(max_new=0)
N = needs()
expect(N["aaaa0001"]["status"] == "closed" and N["aaaa0002"]["status"] == "closed",
       f"T2 tools pass the check -> needs closed: {N['aaaa0001']['status']}, {N['aaaa0002']['status']}")
uses = sc._jload(sc.USAGE_FILE, {})
expect(uses.get("acme-openapi-testgen", {}).get("success") == 1, "T2 the skill got a successful use")
capst = {c["id"]: c["status"] for c in sc._jload(sc.CAPABILITIES_FILE, [])}
expect(capst["qa-testing-openapi-tests"] != "missing", f"T2 capability no longer missing: {capst['qa-testing-openapi-tests']}")
expect(os.path.exists(os.path.join(sc.SKILLS_DIR, "acme-openapi-testgen", "tests", "test_need_aaaa0001.py")),
       "T2 acceptance check stays with the skill as a regression test")

# ---- broken need: 3 tries then parked ------------------------------------------------------------------------
for i in range(4):
    sc.work_needs(max_new=1); run_queue(); sc.work_needs(max_new=0)
N = needs()
b = N["aaaa0003"]
expect(b["status"] == "parked" and b["tries"] == 3, f"T3 broken need parked after 3 tries: {b['status']} {b.get('tries')}")
searches = CALLS["search"]; sc.work_needs(); sc.work_needs()
expect(needs()["aaaa0003"]["status"] == "parked", "T3 parked need is not worked again")
expect(len(b.get("tried_repos", [])) == 3 and len(set(b["tried_repos"])) == 3, f"T3 each try used a new repo: {b.get('tried_repos')}")
reg = sc.load_registry()
expect(not any(s.get("added_for_need") == "aaaa0003" for s in reg.values()), "T3 skills added for the failed need were archived again")
expect(N["aaaa0004"]["status"] == "parked" and "not a tool" in N["aaaa0004"]["log"][-1]["why"], "T5 quota need parked as not a tool")
run_queue(); sc.work_needs(max_new=0)
N = needs()
expect(N["aaaa0007"].get("skill") == "yizhiyanhua-ai-fireworks-tech-graph" and not N["aaaa0007"].get("tried_repos"),
       f"T6 pinned check improves the named skill without scouting: {N['aaaa0007'].get('skill')} {N['aaaa0007']['status']}")
N = needs()
expect(N["aaaa0005"]["status"] == "closed" and N["aaaa0007"]["status"] == "closed",
       f"T5/T6 closed: csv={N['aaaa0005']['status']} techgraph={N['aaaa0007']['status']}")

# ---- test 4: 30 skills -> the lowest is archived ------------------------------------------------------------------
stored = sc._jload(sc.REGISTRY_FILE, {})
base = dict(stored)
i = 0
while len(stored) < sc.MAX_ACTIVE_SKILLS:
    stored[f"filler-{i}"] = {"full_name": f"f/filler-{i}", "score": 70 + i * 0.1, "domain": "diagrams"}; i += 1
stored["filler-0"]["score"] = 10.0
sc._jsave(sc.REGISTRY_FILE, stored)
REPOS["new/gen"] = repo("new/gen", 9000, "x"); READMES["new/gen"] = "x"
c = sc._candidate(REPOS["new/gen"], "qa_testing"); c.update(score=80.0, components={}, need_fit=0.5)
name = sc._add_need_skill(c, {"id": "aaaa0099"})
after = sc._jload(sc.REGISTRY_FILE, {})
expect(len(after) == 30 and "filler-0" not in after and name in after, f"T4 full registry: lowest archived, new added ({len(after)})")
sc._jsave(sc.REGISTRY_FILE, base)

# ---- scout uses README fit --------------------------------------------------------------------------------------
cands = {k: sc._candidate(v, "qa_testing") for k, v in REPOS.items() if v.get("license")}
for c in cands.values(): sc._details(c)
sc.score_components(cands)
expect(cands["flaky/flake-detector"]["components"]["fit"] > 0 and all("readme" in c for c in cands.values()),
       "L5 regular scout reads READMEs in the detail pass")
expect(cands["acme/openapi-testgen"]["description"] == "API tools", "L5 description restored after scoring")
ex = sc._run_extras()
expect(ex.get("needs_by_state", {}).get("closed", 0) >= 4, f"metrics: {ex.get('needs_by_state')}")
src = open(os.path.join(sc.SKILLS_DIR, "yizhiyanhua-ai-fireworks-tech-graph", "scripts", "diagram_helper.py")).read()
expect(src.count("def to_mermaid") == 1 and "def render_kroki" in src and "'graph' if style" in src,
       "T6 patch spliced into the big module by name (one to_mermaid, rest intact)")
expect(needs()["aaaa0005"].get("capability") == "qa-testing-csv-summary", "T5 need without a check got one written and validated")
print("RESULT", "ALL PASS" if not FAILS else f"{len(FAILS)} FAILED")
