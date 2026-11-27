# ===== Cell 15: 24/7 on GitHub Actions =====
# Your Drive skills folder becomes a (private) GitHub repo. A scheduled GitHub Actions workflow
# runs the same agent every few hours, even when Colab is closed, and commits its work back.
# Colab and GitHub stay in sync with sync_skills().
import base64 as _b64

ENGINE_CELLS = ["1", "2", "3", "4", "5", "10", "11", "12", "13", "17", "18", "19", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37"]   # cells the engine needs

def _notebook_cells():
    from google.colab import _message
    nb = _message.blocking_request("get_ipynb", timeout_sec=30)["ipynb"]
    return ["".join(c["source"]) if isinstance(c["source"], list) else c["source"]
            for c in nb["cells"] if c["cell_type"] == "code"]

def _apply_heals(src):
    """Keep the fixes the system made to itself (engine/heals.json) whenever the engine is re-exported."""
    hf = SKILLS_DIR / "engine" / "heals.json"
    for h in (json.loads(hf.read_text()) if hf.exists() else []):
        if h.get("status") not in ("trial", "kept"):
            continue
        if h["old_source"] in src:
            i = src.rfind(h["old_source"])
            src = src[:i] + h["new_source"] + src[i + len(h["old_source"]):]
        elif h["new_source"] not in src:
            print(f"self-heal #{h['id']} ({h['function']}) no longer matches the notebook code; not re-applied")
    return src

def build_engine_source():
    """Turn the notebook cells into one plain Python module (no !pip, no notebook-only demos)."""
    parts = {}
    for src in _notebook_cells():
        m = re.match(r"# ===== Cell (\w+):", src)
        if m and m.group(1) in ENGINE_CELLS:
            src = src.split("# " + "▶ notebook-only")[0]   # split so this line never matches itself
            src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("!"))
            parts[m.group(1)] = src
    missing = [c for c in ENGINE_CELLS if c not in parts]
    if missing:
        raise RuntimeError(f"Cells not found: {missing}")
    header = '"""Swings AI engine — generated from Swings_AI.ipynb. Edit the notebook, then export_engine()."""\n'
    return _apply_heals(header + "\n\n".join(parts[c] for c in ENGINE_CELLS) + "\n")

RUN_AUTOPILOT = '''"""Entry point for GitHub Actions: one autopilot cycle (+ weekly GitHub refresh), with a private run log."""
import os, sys, json, datetime, shutil, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import swings_core
except Exception:
    # A fix the system made to itself broke the engine: restore the last good engine, mark the fix reverted.
    heals_file = os.path.join(HERE, "heals.json")
    heals = json.load(open(heals_file)) if os.path.exists(heals_file) else []
    good = os.path.join(HERE, "swings_core.last_good.py")
    if not (os.path.exists(good) and any(h.get("status") == "trial" for h in heals)):
        raise
    traceback.print_exc()
    shutil.copy(good, os.path.join(HERE, "swings_core.py"))
    for h in heals:
        if h.get("status") == "trial":
            h.update(status="reverted", reason="engine failed to start after this fix")
    json.dump(heals, open(heals_file, "w"), indent=2)
    print("Engine restored from the last good version")
    sys.modules.pop("swings_core", None)
    import swings_core
from swings_core import *  # noqa
import time as _time
swings_core.CYCLE_DEADLINE = _time.time() + 60 * int(os.environ.get("SWINGS_TIME_BUDGET_MIN", "30"))

init_skill_versioning()
start_run_log("actions")
status = "ok"
try:
    state_file = SKILLS_DIR / "autopilot_state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    last = state.get("last_refresh")
    due = not last or (datetime.date.today() - datetime.date.fromisoformat(last)).days >= REFRESH_DAYS
    if due or os.environ.get("FORCE_REFRESH") == "true":
        try:
            refresh_skills()
            state["last_refresh"] = datetime.date.today().isoformat()
        except Exception as e:
            log(f"refresh failed: {e}")
    print("Sandbox:", SANDBOX_MODE)
    autopilot_cycle()
    state["last_run"] = datetime.datetime.now().isoformat(timespec="minutes")
    state_file.write_text(json.dumps(state, indent=2))
except Exception as e:
    status = "crashed"
    syslog_exception("run", e)
    raise
finally:
    finish_run_log(status)
    commit_skills("autopilot run")
'''

REQUIREMENTS = "requests\nscikit-learn\nschedule\npytest\ngoogle-genai\n"

WORKFLOW = '''name: Swings AI autopilot
on:
  schedule:
    - cron: "23 */3 * * *"        # every 3 hours (keeps private repos inside the free minutes)
  workflow_dispatch:
    inputs:
      force_refresh:
        description: "Re-scan GitHub for UML projects now"
        type: boolean
        default: false
permissions:
  contents: write
  actions: read          # the engine reads the latest test result (Phase 5)
concurrency:
  group: swings-ai
  cancel-in-progress: false
jobs:
  autopilot:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
        with: { ref: "${{ github.ref_name }}" }   # latest main, not the commit the run was queued at
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip, cache-dependency-path: engine/requirements.txt }
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - uses: actions/setup-java@v5
        with: { distribution: temurin, java-version: "17" }
      - uses: actions/cache@v4
        with:
          path: .skill_repos
          key: skill-repos-${{ hashFiles('registry.json') }}
          restore-keys: skill-repos-
      - run: pip install -r engine/requirements.txt
      - name: Run autopilot
        run: python -u engine/run_autopilot.py
        timeout-minutes: 38
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SWINGS_SKILLS_DIR: ${{ github.workspace }}
          SWINGS_REPO_CACHE: ${{ github.workspace }}/.skill_repos
          FORCE_REFRESH: ${{ inputs.force_refresh }}
          SWINGS_GH_TOKEN: ${{ secrets.SWINGS_GH_TOKEN }}          # PAT that can create repos (GitHub plugin)
          SWINGS_GITHUB_DRY_RUN: ${{ vars.SWINGS_GITHUB_DRY_RUN || 'true' }}   # repo variable; set to false to publish
      - name: Push the agent's work
        if: always()        # save whatever was done, even if the run step failed or timed out
        run: |
          git config user.name "Swings AI"
          git config user.email "swings-ai@users.noreply.github.com"
          git add -A
          git commit -m "autopilot: $(date -u +%Y-%m-%dT%H:%MZ)" || echo "nothing new"
          git pull --rebase -X ours origin "${GITHUB_REF_NAME}" || true
          git push origin "HEAD:${GITHUB_REF_NAME}"
'''

TESTS_WORKFLOW = '''name: Swings AI tests
on:
  push:
    paths: ["engine/swings_core.py", "engine/run_autopilot.py", "engine/notebook_cell15.py", "tests/**", ".github/workflows/tests.yml"]
  schedule:
    - cron: "41 4 * * *"          # daily: also covers self-fixes the autopilot commits (its pushes trigger no workflow)
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: swings-tests
  cancel-in-progress: true
jobs:
  tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip, cache-dependency-path: engine/requirements.txt }
      - run: pip install -r engine/requirements.txt
      - name: Run all tests (8 suites + 6-run simulated regression)
        run: python tests/run_tests.py --full --json test-results.json
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: test-results, path: test-results.json, retention-days: 14 }
'''

def export_engine():
    """Write engine/ + the workflow into the skills folder (re-run after editing notebook cells)."""
    (SKILLS_DIR / "engine").mkdir(exist_ok=True)
    (SKILLS_DIR / "engine" / "swings_core.py").write_text(build_engine_source(), encoding="utf-8")
    (SKILLS_DIR / "engine" / "run_autopilot.py").write_text(RUN_AUTOPILOT, encoding="utf-8")
    (SKILLS_DIR / "engine" / "requirements.txt").write_text(REQUIREMENTS)
    wf = SKILLS_DIR / ".github" / "workflows"; wf.mkdir(parents=True, exist_ok=True)
    (wf / "autopilot.yml").write_text(WORKFLOW)
    (wf / "tests.yml").write_text(TESTS_WORKFLOW)
    c15 = next((c for c in _notebook_cells() if c.startswith("# ===== Cell 15:")), "")   # this cell, so CI tests the real sync code
    (SKILLS_DIR / "engine" / "notebook_cell15.py").write_text(c15.split("# " + "\u25b6 notebook-only")[0], encoding="utf-8")
    compile((SKILLS_DIR / "engine" / "swings_core.py").read_text(), "swings_core.py", "exec")
    commit_skills("export engine + workflow")
    print("Engine exported to", SKILLS_DIR / "engine")

def _auth_args():
    """Token goes in a one-off HTTP header, never into the saved remote URL."""
    token = GITHUB_TOKEN or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Add a GITHUB_TOKEN secret with 'repo' (or Contents: read/write) access.")
    basic = _b64.b64encode(f"x-access-token:{token}".encode()).decode()
    return ["-c", f"http.https://github.com/.extraheader=AUTHORIZATION: basic {basic}"]

def connect_github(repo_url):
    """repo_url like https://github.com/<you>/swings-ai-skills.git (create it empty + private first)."""
    git(["remote", "remove", "origin"], SKILLS_DIR)
    git(["remote", "add", "origin", repo_url], SKILLS_DIR)
    git(["branch", "-M", "main"], SKILLS_DIR)
    r = git(_auth_args() + ["push", "-u", "origin", "main"], SKILLS_DIR)
    print(r.stdout or r.stderr or "pushed")

def sync_skills():
    """Pull what the GitHub autopilot did, then push what you did in Colab (conflicts resolved automatically)."""
    for stuck in ("rebase", "merge"):                       # clean up any half-finished earlier attempt
        git([stuck, "--abort"], SKILLS_DIR)
    commit_skills("colab changes")
    git(_auth_args() + ["fetch", "-q", "origin", "main"], SKILLS_DIR)
    r1 = git(["merge", "-q", "-X", "theirs", "-m", "sync: merge autopilot work", "origin/main"], SKILLS_DIR)
    if r1.returncode != 0:                                  # e.g. both sides edited the same file
        git(["checkout", "--theirs", "."], SKILLS_DIR); git(["add", "-A"], SKILLS_DIR)
        git(["commit", "-q", "-m", "sync: merge autopilot work (auto-resolved)"], SKILLS_DIR)
    r2 = git(_auth_args() + ["push", "origin", "HEAD:main"], SKILLS_DIR)
    print("merge:", (r1.stdout + r1.stderr).strip()[-300:] or "ok")
    print("push :", (r2.stdout + r2.stderr).strip()[-300:] or "ok")

# ---- F10: notebook sync ------------------------------------------------------------------------------------
# Before an export: a sync report (self-fixes, evolved prompts, weights, rules) and a drift guard that compares the
# engine on GitHub with the notebook build, cell by cell. After the push: the IDENTICAL check.
import hashlib as _hl, difflib as _dl
EXPORT_RECORD = SKILLS_DIR / "engine" / "export.json"
DRIFT_DIR = SKILLS_DIR / "engine" / "drift"
SYNC_REPORT_FILE = SKILLS_DIR / "engine" / "SYNC.md"
CELL_HEAD = re.compile(r"^# =+ Cell (\w+):", re.M)

def _sha(text):
    return _hl.sha256(text.encode("utf-8")).hexdigest()[:16]

def _engine_cells_raw():
    """{cell: source} exactly as build_engine_source() joins them, before any self-fix is applied."""
    parts = {}
    for src in _notebook_cells():
        m = re.match(r"# =+ Cell (\w+):", src)
        if m and m.group(1) in ENGINE_CELLS:
            src = src.split("# " + "▶ notebook-only")[0]
            src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("!"))
            parts[m.group(1)] = src
    return parts

def _heals_file():
    return SKILLS_DIR / "engine" / "heals.json"

def _cell_at(lines, i):
    for k in range(min(i, len(lines) - 1), -1, -1):
        m = CELL_HEAD.match(lines[k]) if k >= 0 else None
        if m:
            return m.group(1)
    return "header"

def _cell_of_code(text, code):
    i = text.rfind(code)
    if i < 0:
        return None
    before = text[:i].splitlines()
    return _cell_at(before, len(before) - 1) if before else "header"

def heal_states(raw=None):
    """Kept fix whose new code is now in the notebook -> folded. Fix whose old AND new code are both gone
    (you rewrote the function) -> superseded: your version wins. Saved to heals.json, never silently dropped."""
    raw = raw if raw is not None else "\n\n".join(_engine_cells_raw().values())
    hf = _heals_file()
    heals = json.loads(hf.read_text()) if hf.exists() else []
    now, changed = datetime.datetime.now().isoformat(timespec="minutes"), False
    for h in heals:
        if h.get("status") not in ("trial", "kept"):
            continue
        has_new, has_old = h["new_source"] in raw, h["old_source"] in raw
        if h["status"] == "kept" and has_new and not has_old:
            h.update(status="folded", folded=now); changed = True
        elif not has_new and not has_old:
            h.update(status="superseded", superseded=now,
                     reason="the function was rewritten in the notebook; the notebook version wins"); changed = True
    if changed:
        hf.write_text(json.dumps(heals, indent=2))
    return heals

def _short_diff(a, b, n=20):
    d = list(_dl.unified_diff(a.splitlines(), b.splitlines(), "before", "after", lineterm="", n=1))
    return d[:n] + ([f"... {len(d) - n} more lines"] if len(d) > n else [])

def drift_check(live, built, record=None, cells=None):
    """Every line difference between the GitHub engine and the notebook build, assigned to its cell.
    expected = that cell was edited in the notebook since the last export (or there is no record yet)."""
    record = record if record is not None else (json.loads(EXPORT_RECORD.read_text()) if EXPORT_RECORD.exists() else {})
    cells = cells if cells is not None else _engine_cells_raw()
    old = record.get("cells") or {}
    edited = None if not old else {c for c in set(cells) | set(old)          # changed, added or removed cells
                                    if old.get(c) != (_sha(cells[c]) if c in cells else None)}
    lv, bl, out = live.splitlines(), built.splitlines(), {}
    def where(lines, a, b):                       # the first non-blank line decides: a new cell starts after a blank
        return _cell_at(lines, next((j for j in range(a, b) if lines[j].strip()), a))
    for tag, i1, i2, j1, j2 in _dl.SequenceMatcher(None, lv, bl, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        cell = where(bl, j1, j2) if j2 > j1 else where(lv, i1, i2)
        h = out.setdefault(cell, {"cell": cell, "github_lines": 0, "notebook_lines": 0,
                                  "expected": edited is None or cell in edited, "sample": []})
        h["github_lines"] += i2 - i1; h["notebook_lines"] += j2 - j1
        if len(h["sample"]) < 6:
            h["sample"] += [f"- {l}" for l in lv[i1:i2][:3]] + [f"+ {l}" for l in bl[j1:j2][:3]]
    return list(out.values())

def sync_report(show=True):
    """What the system changed in itself, and whether GitHub runs what this notebook builds."""
    cells = _engine_cells_raw()
    raw = "\n\n".join(cells[c] for c in ENGINE_CELLS if c in cells)
    heals = heal_states(raw)
    built = build_engine_source()
    live_f = SKILLS_DIR / "engine" / "swings_core.py"
    live = live_f.read_text(encoding="utf-8") if live_f.exists() else ""
    record = json.loads(EXPORT_RECORD.read_text()) if EXPORT_RECORD.exists() else {}
    hunks = drift_check(live, built, record, cells) if live else []
    unexpected = [h for h in hunks if not h["expected"]]
    L = [f"# Notebook sync report ({datetime.datetime.now():%Y-%m-%d %H:%M})", "", "## Self-fixes", ""]
    for h in heals or []:
        where = (_cell_of_code(built, h["new_source"]) or _cell_of_code(raw, h["old_source"])
                 or _cell_of_code(raw, f"def {h['function']}(") or "?")
        L.append(f"- #{h['id']} **{h['status']}** `{h['function']}()` in Cell {where} ({h.get('ts', '')[:16]}): {h.get('summary', '')[:120]}")
        if h["status"] == "kept":
            L.append(f"  - ready to fold: paste the new version of `{h['function']}()` into Cell {where}; "
                     "the next sync marks it folded")
        if h["status"] in ("trial", "kept"):
            L += ["  ```diff"] + [f"  {l}" for l in _short_diff(h["old_source"], h["new_source"])] + ["  ```"]
    if not heals:
        L.append("- None yet.")
    L += ["", "## Evolved agent prompts", ""]
    seeds = {s.name: s.system_prompt for s in globals().get("SEED_AGENTS", [])}
    evolved = False
    for n, a in sorted(load_agents().items()):
        if a.version <= 1 and not a.history:
            continue
        evolved = True
        L.append(f"- **{n}** is at v{a.version}" + (" (the seed in Cell 19 is only used on a fresh install)" if n in seeds else ""))
        for k, h in enumerate(a.history):
            L.append(f"  - v{h['version']} replaced {h.get('replaced', '')[:16]}: {h.get('reason', '')[:140]}")
        prev = a.history[-1]["prompt"] if a.history else seeds.get(n, "")
        L += ["  ```diff"] + [f"  {l}" for l in _short_diff(prev, a.system_prompt, 12)] + ["  ```"]
    if not evolved:
        L.append("- None yet.")
    w = _jload(WEIGHTS_FILE, {}) if "WEIGHTS_FILE" in globals() else {}
    learned = {k: v for k, v in w.items() if not k.startswith("_") and DEFAULT_WEIGHTS.get(k) != v}
    L += ["", "## Learned score weights", "",
          "- " + (", ".join(f"{k} {DEFAULT_WEIGHTS.get(k)} -> {v}" for k, v in learned.items()) if learned else "Defaults in use.")]
    rules = _jload(RULES_FILE, {}) if "RULES_FILE" in globals() else {}
    active = [(k, r["text"]) for k, rs in rules.items() for r in rs if r.get("status") == "active"]
    L += ["", "## Active rules", ""] + ([f"- ({k}) {t}" for k, t in active] or ["- None."])
    L += ["", "## GitHub engine vs this notebook", ""]
    if not live:
        L.append("- No engine on GitHub yet.")
    elif not hunks:
        L.append("- **IDENTICAL**: GitHub runs exactly what this notebook builds.")
    for h in hunks:
        kind = "you edited this cell (will be exported)" if h["expected"] else "**changed on GitHub outside the notebook**"
        L.append(f"- Cell {h['cell']}: {h['github_lines']} line(s) on GitHub vs {h['notebook_lines']} in the notebook; {kind}")
        L += ["  ```diff"] + [f"  {l}" for l in h["sample"]] + ["  ```"]
    saved = None
    if unexpected:
        DRIFT_DIR.mkdir(parents=True, exist_ok=True)
        saved = DRIFT_DIR / f"swings_core.{datetime.datetime.now():%Y%m%d-%H%M%S}.py"
        saved.write_text(live, encoding="utf-8")
        L += ["", f"Export skipped: GitHub's copy was saved to engine/drift/{saved.name}. Fold the change into its cell, "
                  "or run export_engine(force=True) to replace it."]
    text = "\n".join(L) + "\n"
    SYNC_REPORT_FILE.write_text(text, encoding="utf-8")
    if show:
        print(text)
    return {"identical": bool(live) and not hunks, "differences": hunks, "unexpected": unexpected,
            "safe_to_export": not unexpected, "drift_copy": str(saved) if saved else None,
            "ready_to_fold": [h["id"] for h in heals if h.get("status") == "kept"]}

if "_export_engine_plain" not in globals():
    _export_engine_plain = export_engine
def _tests_gate(skip=False):
    """Phase 5, step 1: the quick test suites run on the candidate engine before it can reach GitHub."""
    if skip:
        return True, "skipped by export_engine(skip_tests=True)"
    if os.environ.get("SWINGS_TESTING"):
        return True, "inside the test suite"
    runner = SKILLS_DIR / "tests" / "run_tests.py"
    if not runner.exists():
        return True, "no tests/ folder yet"
    import tempfile as _tf
    d = _tf.mkdtemp(prefix="swings-gate-")
    cand, res = os.path.join(d, "engine.py"), os.path.join(d, "results.json")
    with open(cand, "w", encoding="utf-8") as f:
        f.write(build_engine_source())
    print("Testing the candidate engine (quick suites)...")
    r = subprocess.run([sys.executable, str(runner), "--engine", cand, "--json", res], capture_output=True, text=True, timeout=1200)
    out = (r.stdout or "") + (r.stderr or "")
    print("\n".join(l for l in out.splitlines() if l.startswith(("PASS", "FAIL", "RESULT", "     -"))))
    summary = json.load(open(res)) if os.path.exists(res) else {}
    shutil.rmtree(d, ignore_errors=True)
    return bool(r.returncode == 0 and summary.get("ok")), (out.strip().splitlines() or ["no output"])[-1]

def export_engine(force=False, skip_tests=False):
    """Export only when GitHub has nothing the notebook would overwrite unseen; record per-cell fingerprints."""
    rep = sync_report(show=True)
    if not rep["safe_to_export"] and not force:
        print(f"Export skipped: GitHub changed outside the notebook in cell(s) "
              f"{[h['cell'] for h in rep['unexpected']]}; copy saved to {rep['drift_copy']}. See engine/SYNC.md.")
        return False
    tests_ok, tests_note = _tests_gate(skip_tests)
    if not tests_ok:
        print(f"Export refused: the candidate engine fails its tests ({tests_note}). Fix the cell, "
              "or run export_engine(skip_tests=True) to override; the override is recorded.")
        return False
    cells = _engine_cells_raw()
    rec = json.loads(EXPORT_RECORD.read_text()) if EXPORT_RECORD.exists() else {}
    rec.update(ts=datetime.datetime.now().isoformat(timespec="minutes"), engine_sha=_sha(build_engine_source()),
               cells={c: _sha(t) for c, t in cells.items()}, forced=bool(force and not rep["safe_to_export"]),
               tests={"ok": tests_ok, "note": tests_note, "skipped": bool(skip_tests)})
    EXPORT_RECORD.write_text(json.dumps(rec, indent=2))
    if rec["forced"]:
        with open(SYNC_REPORT_FILE, "a", encoding="utf-8") as f:
            f.write("\nForced export: the notebook version replaced GitHub's; the saved copy stays in engine/drift/.\n")
    _export_engine_plain()
    return True

def verify_identical(remote_text=None):
    """After the push: the engine on GitHub must be exactly what the notebook builds."""
    if remote_text is None:
        git(_auth_args() + ["fetch", "-q", "origin", "main"], SKILLS_DIR)
        r = git(["show", "origin/main:engine/swings_core.py"], SKILLS_DIR)
        remote_text = r.stdout if r.returncode == 0 else ""
    built = build_engine_source()
    hunks = drift_check(remote_text, built, {}, {}) if remote_text != built else []
    ok = remote_text == built
    rec = json.loads(EXPORT_RECORD.read_text()) if EXPORT_RECORD.exists() else {}
    rec["identical"] = ok
    rec["checks"] = (rec.get("checks", []) + [{"ts": datetime.datetime.now().isoformat(timespec="minutes"),
                                               "identical": ok, "cells": sorted({h["cell"] for h in hunks})}])[-60:]
    EXPORT_RECORD.write_text(json.dumps(rec, indent=2))
    with open(SYNC_REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n## After the export\n\n- {'IDENTICAL' if ok else 'DIFFERENT in cells ' + str(sorted({h['cell'] for h in hunks}))}\n")
    commit_skills("sync: export record + report")
    print("IDENTICAL: GitHub runs exactly what this notebook builds." if ok else
          f"DIFFERENT: GitHub's engine differs from the notebook build in cells {sorted({h['cell'] for h in hunks})}")
    return ok

