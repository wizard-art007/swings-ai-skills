"""F10 tests: the notebook is simulated from the engine's own cells; a local bare repo stands in for GitHub."""
import os, sys, json, re, subprocess, tempfile, datetime
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
sc._llm_unbudgeted = fakellm.fake
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = sc.SKILLS_DIR / "engine" / "swings_core.py"
TEXT = ENGINE_ORIG = ENGINE.read_text(encoding="utf-8")

def split_cells(text):
    heads = list(re.finditer(r"^# ===== Cell (\w+):", text, re.M))
    out = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        chunk = text[h.start():end]
        out.append(chunk.rstrip("\n"))                  # notebook cells carry no trailing newline
    return out
NB = split_cells(TEXT)
ns = sc.__dict__
ns["_notebook_cells"] = lambda: list(NB)
# the real Cell 15 code (written by each export) when present, else the copy kept in tests/support
REAL = sc.SKILLS_DIR / "engine" / "notebook_cell15.py"
if REAL.exists() and "def verify_identical" in REAL.read_text(encoding="utf-8"):
    exec(compile(REAL.read_text(encoding="utf-8"), "notebook_cell15", "exec"), ns)
    print("using the real Cell 15 code from engine/notebook_cell15.py")
else:
    SUP = os.path.join(os.path.dirname(HERE), "support")
    exec(compile(open(os.path.join(SUP, "cell15_base.py")).read(), "cell15_base", "exec"), ns)
    exec(compile(open(os.path.join(SUP, "cell15_f10.py")).read().split("# " + "▶ notebook-only")[0], "cell15_f10", "exec"), ns)
ns["_notebook_cells"] = lambda: list(NB)                 # stand-ins for Colab and the GitHub token
ns["_auth_args"] = lambda: []
ns["_tests_gate"] = lambda *a, **k: (True, "skipped inside the test suite")
TEXT = sc.build_engine_source(); ENGINE.write_text(TEXT, encoding="utf-8")   # what Cell 15 last exported
compile(TEXT, "built", "exec")
expect([l for l in TEXT.splitlines() if l.strip()] == [l for l in ENGINE_ORIG.splitlines() if l.strip()],
       "the simulated notebook builds the engine (same code, blank lines aside)")

# a local "GitHub"
HUB = tempfile.mkdtemp(prefix="f10hub-")
subprocess.run(["git", "init", "-q", "--bare", "-b", "main", HUB + "/skills.git"], check=True)
sc.init_skill_versioning()
sc.git(["remote", "add", "origin", HUB + "/skills.git"], sc.SKILLS_DIR)
sc.commit_skills("initial"); sc.git(["push", "-q", "origin", "HEAD:main"], sc.SKILLS_DIR)
def cell(n):
    return next(i for i, c in enumerate(NB) if c.startswith(f"# ===== Cell {n}:"))
def github_edit(fn):
    """Something changes the engine on 'GitHub' (another clone pushes)."""
    d = tempfile.mkdtemp(prefix="f10gh-")
    subprocess.run(["git", "clone", "-q", HUB + "/skills.git", d], check=True)
    fn(d)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "github side"], check=True)
    subprocess.run(["git", "-C", d, "push", "-q", "origin", "HEAD:main"], check=True)

# ---- clean start: IDENTICAL, first export records fingerprints ----
rep = sc.sync_report(show=False)
expect(rep["identical"] and rep["safe_to_export"] and "**IDENTICAL**" in sc.SYNC_REPORT_FILE.read_text(), "clean start reports IDENTICAL")
expect(sc.export_engine() and json.loads(sc.EXPORT_RECORD.read_text())["cells"].get("36"), "export records per-cell fingerprints")
sc.sync_skills()
expect(sc.verify_identical(), "after the push GitHub is IDENTICAL")

# ---- 1: a kept fix applied on GitHub ----
fn = re.search(r"def _week_key\(d=None\):\n(?:    .*\n)+", TEXT).group(0)
new = fn.replace('return f"{y}-W{w:02d}"', 'return f"{y}-W{w:02d}"   # healed: zero-padded week')
assert new != fn
heal = {"id": 1, "fingerprint": "fp1", "function": "_week_key", "status": "kept", "ts": "2026-11-10T10:00:00",
        "clean_runs": 3, "summary": "ValueError in _week_key", "old_source": fn, "new_source": new}
def apply_heal(d):
    p = os.path.join(d, "engine", "swings_core.py"); s = open(p).read()
    open(p, "w").write(s[:s.rfind(fn)] + new + s[s.rfind(fn) + len(fn):])
    json.dump([heal], open(os.path.join(d, "engine", "heals.json"), "w"))
github_edit(apply_heal)
sc.sync_skills()
rep = sc.sync_report(show=False)
txt = sc.SYNC_REPORT_FILE.read_text()
expect(rep["identical"] and rep["ready_to_fold"] == [1] and "#1 **kept** `_week_key()` in Cell 36" in txt and "ready to fold" in txt
       and "+    return f\"{y}-W{w:02d}\"   # healed" in txt, "T1 a kept fix shows its cell, diff and 'ready to fold'; still IDENTICAL")
sc.export_engine(); sc.sync_skills()
expect(sc.verify_identical() and new in ENGINE.read_text(), "T1 the export keeps the fix and checks IDENTICAL")

# ---- 2: folding the fix into its cell ----
NB[cell("36")] = NB[cell("36")].replace(fn, new)
sc.heal_states()
h = json.loads((sc.SKILLS_DIR / "engine" / "heals.json").read_text())[0]
rep = sc.sync_report(show=False)
expect(h["status"] == "folded" and rep["identical"] and rep["ready_to_fold"] == [], f"T2 pasting the new code folds the fix: {h['status']}")

# ---- 3: you rewrite a fixed function another way -> superseded ----
fn2 = re.search(r"def _pacific_day\(now=None\):\n(?:    .*\n)+", TEXT).group(0)
new2 = fn2.replace("return (now", "return  (now")
heal2 = {"id": 2, "fingerprint": "fp2", "function": "_pacific_day", "status": "kept", "ts": "2026-11-20T10:00:00",
         "clean_runs": 3, "summary": "tz bug", "old_source": fn2, "new_source": new2}
hs = json.loads((sc.SKILLS_DIR / "engine" / "heals.json").read_text()) + [heal2]
(sc.SKILLS_DIR / "engine" / "heals.json").write_text(json.dumps(hs))
mine = fn2.replace("return (now", "return ((now").rstrip("\n") + ")\n"
NB[cell("36")] = NB[cell("36")].replace(fn2, mine)
sc.heal_states()
h2 = json.loads((sc.SKILLS_DIR / "engine" / "heals.json").read_text())[1]
built = sc.build_engine_source()
expect(h2["status"] == "superseded" and mine in built and new2 not in built, f"T3 your rewrite wins; the fix is superseded: {h2['status']}")
expect(sc.export_engine(), "T5 a notebook edit since the last export is expected: the export goes ahead")
sc.sync_skills()
expect(sc.verify_identical(), "T5 ... and checks IDENTICAL")

# ---- 5b: a NEW engine cell added in the notebook is an expected difference (found live: it was filed under the cell before) ----
sc.ENGINE_CELLS.append("38"); NB.append("# ===== Cell 38: F10 test cell =====\nF10_TEST_FLAG = 1")
rep = sc.sync_report(show=False)
expect(rep["safe_to_export"] and [h["cell"] for h in rep["differences"]] == ["38"], f"T5b a new cell is filed under itself and expected: {[h['cell'] for h in rep['differences']]}")
sc.export_engine(); sc.sync_skills(); sc.verify_identical()
sc.ENGINE_CELLS.remove("38"); NB.pop()
rep = sc.sync_report(show=False)
expect(rep["safe_to_export"] and [h["cell"] for h in rep["differences"]] == ["38"], f"T5b removing a cell is expected too: {[h['cell'] for h in rep['differences']]}")
sc.export_engine(); sc.sync_skills(); sc.verify_identical()

# ---- 4: a change on GitHub outside the notebook ----
def sneak(d):
    p = os.path.join(d, "engine", "swings_core.py"); s = open(p).read()
    open(p, "w").write(s.replace("MAX_AGENTS = 20", "MAX_AGENTS = 25", 1))
github_edit(sneak)
sc.sync_skills()
rep = sc.sync_report(show=False)
expect(not rep["safe_to_export"] and [h["cell"] for h in rep["unexpected"]] == ["18"] and rep["drift_copy"]
       and "MAX_AGENTS = 25" in open(rep["drift_copy"]).read(), f"T4 a GitHub-side change is caught in its cell and saved: {[h['cell'] for h in rep['unexpected']]}")
before = ENGINE.read_text()
expect(sc.export_engine() is False and ENGINE.read_text() == before, "T4 the export is skipped, nothing is overwritten")
expect(sc.export_engine(force=True) and "MAX_AGENTS = 25" not in ENGINE.read_text()
       and json.loads(sc.EXPORT_RECORD.read_text())["forced"], "T4 export_engine(force=True) replaces it, and says so")
sc.sync_skills(); sc.verify_identical()

# ---- 6: prompts, weights, rules ----
txt = sc.SYNC_REPORT_FILE.read_text()
a = sc.load_agents()["publisher"]
expect("**publisher** is at v" in txt and "F7: experiments go to one projects repo" in txt and "```diff" in txt,
       "T6 the evolved publisher prompt shows each version with its reason and a diff")
expect("## Learned score weights" in txt and "## Active rules" in txt and "Validate Mermaid" in txt, "T6 weights and rules are listed")

# ---- 7: engine side ----
hs = json.loads((sc.SKILLS_DIR / "engine" / "heals.json").read_text())
hs.append({**heal, "id": 3, "status": "kept", "ts": "2026-11-15T10:00:00"})
(sc.SKILLS_DIR / "engine" / "heals.json").write_text(json.dumps(hs))
s = sc.sync_status()
expect(s["last_check"]["identical"] and s["ready_to_fold"] and s["ready_to_fold"][0]["cell"] == "36" and s["drift_copies"]
       and s["evolved_agents"].get("publisher", 0) >= 3, f"T7 sync_status reads the record: {s['ready_to_fold']}")
text, verdict = sc.build_health_report()
expect("## Notebook sync" in text and "IDENTICAL" in text and "Self-fix #3 in `_week_key()` has been kept for" in text
       and "Cell 36" in text and "engine/drift/" in text, "T7 the weekly report has a sync section and the fold decision")
expect(text.index("## Notebook sync") < text.index("## Decisions waiting for you"), "T7 sections in order")
print("RESULT", "ALL PASS" if not FAILS else f"{len(FAILS)} FAILED")
