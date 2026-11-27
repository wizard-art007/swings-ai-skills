"""Swings AI test runner.

    python tests/run_tests.py            # quick: the 8 suites (~40 s)
    python tests/run_tests.py --full     # suites + the 6-run simulated regression (~3 min)
    python tests/run_tests.py --engine /tmp/candidate.py   # test an engine before it is exported

Every suite runs on a fresh copy of this repo with all tokens removed and Gemini replaced by a scripted stand-in
(tests/support/fakellm.py), so a test can never touch GitHub, Gemini or the live state. Exit code 0 = all passed.
"""
import os, sys, json, shutil, subprocess, tempfile, time, datetime, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SUITES = ["lc_test", "f6_test", "f6_tamper", "f7_test", "pub_direct_test", "f8_test", "f9_test", "f10_test"]
SKIP_DIRS = {".git", ".skill_repos", ".private_logs", ".projects_repo", "__pycache__", ".pytest_cache", "node_modules"}
SECRETS = ("GITHUB_TOKEN", "SWINGS_GH_TOKEN", "GEMINI_API_KEY", "GOOGLE_API_KEY", "SWINGS_FALLBACK_API_KEY")


def _repo_files():
    """The files a fresh clone would have: git-tracked plus new unignored files (never the gitignored skill clones)."""
    if os.path.isdir(os.path.join(REPO, ".git")):
        r = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=REPO,
                           capture_output=True)
        if r.returncode == 0:
            return [f for f in r.stdout.decode("utf-8", "replace").split("\0")
                    if f and not f.startswith("tests/") and os.path.isfile(os.path.join(REPO, f))]
    out = []
    for d, dirs, files in os.walk(REPO):
        rel = os.path.relpath(d, REPO)
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and x != "outputs" and not (rel == "tests" or (d == REPO and x == "tests"))
                   and not (x == "repo" and rel.count(os.sep) == 0 and rel != ".")]
        out += [os.path.normpath(os.path.join(rel, f)) for f in files if not f.endswith((".pyc", ".npz"))]
    return out

_BASE = {}
def _base_copy():
    """Read the repo once (it may sit on a slow network drive), then copy locally for each suite."""
    if "dir" not in _BASE:
        base = tempfile.mkdtemp(prefix="swings-base-")
        for f in _repo_files():
            dst = os.path.join(base, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(REPO, f), dst)
        _BASE["dir"] = base
    return _BASE["dir"]


def fresh_copy(engine, tmp):
    """A throwaway copy of the repo: the candidate engine in place, scouting off, nothing secret."""
    work = os.path.join(tmp, "work")
    shutil.copytree(_base_copy(), work)
    if engine:
        shutil.copy(engine, os.path.join(work, "engine", "swings_core.py"))
    state = os.path.join(work, "autopilot_state.json")
    st = json.load(open(state)) if os.path.exists(state) else {}
    st["last_refresh"] = datetime.date.today().isoformat()          # no live GitHub scouting in tests
    json.dump(st, open(state, "w"))
    return work


def env_for(work, tmp):
    env = {k: v for k, v in os.environ.items() if k not in SECRETS}
    env.update(SWINGS_SKILLS_DIR=work, SWINGS_REPO_CACHE=os.path.join(work, ".skill_repos"),
               SWINGS_TIME_BUDGET_MIN="30", VERIFY_MODE_FILE=os.path.join(tmp, "mode.json"),
               SWINGS_TESTING="1", PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=os.pathsep.join([os.path.join(HERE, "support", "nocolab"), os.path.join(HERE, "support"),
                                           env.get("PYTHONPATH", "")]))
    json.dump({"outage": False}, open(env["VERIFY_MODE_FILE"], "w"))
    return env


def isolation_check(engine):
    """Refuse to run any suite unless the engine, as the suites will load it, works on the throwaway copy only.
    (In Colab the engine would otherwise switch to the real Drive folder: found on 27 Nov, Phase 5 step 1.)"""
    tmp = tempfile.mkdtemp(prefix="swings-isolation-")
    try:
        work = fresh_copy(engine, tmp)
        code = ("import sys, json; sys.path.insert(0, %r); import swings_core as s; "
                "print(json.dumps({'dir': str(s.SKILLS_DIR), 'colab': s.IN_COLAB}))" % os.path.join(work, "engine"))
        r = subprocess.run([sys.executable, "-c", code], cwd=tmp, env=env_for(work, tmp), capture_output=True, text=True, timeout=300)
        line = next((l for l in reversed(r.stdout.splitlines()) if l.startswith("{")), "{}")
        got = json.loads(line)
        ok = got.get("dir") == os.path.realpath(work) and got.get("colab") is False
        return ok, (got if line != "{}" else (r.stdout + r.stderr)[-800:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_suite(name, engine, timeout=900):
    tmp = tempfile.mkdtemp(prefix=f"swings-{name}-")
    try:
        work = fresh_copy(engine, tmp)
        t0 = time.time()
        r = subprocess.run([sys.executable, os.path.join(HERE, "suites", f"{name}.py")], cwd=tmp,
                           env=env_for(work, tmp), capture_output=True, text=True, timeout=timeout)
        out = r.stdout + r.stderr
        passed = [l[5:] for l in out.splitlines() if l.startswith("PASS ")]
        failed = [l[5:] for l in out.splitlines() if l.startswith("FAIL ")]
        ok = r.returncode == 0 and "RESULT ALL PASS" in out and not failed
        return {"suite": name, "ok": ok, "passed": len(passed), "failed": failed,
                "seconds": round(time.time() - t0, 1), "tail": "" if ok else out[-3000:]}
    except subprocess.TimeoutExpired:
        return {"suite": name, "ok": False, "passed": 0, "failed": [f"timed out after {timeout}s"], "seconds": timeout, "tail": ""}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_regression(engine):
    """Six simulated runs: four normal, one with Gemini down, one after it; every run must end ok with 0 errors."""
    tmp = tempfile.mkdtemp(prefix="swings-regression-")
    t0, rows, failed = time.time(), [], []
    try:
        work = fresh_copy(engine, tmp)
        env = env_for(work, tmp)
        for i, outage in enumerate([False, False, False, False, True, False], 1):
            json.dump({"outage": outage}, open(env["VERIFY_MODE_FILE"], "w"))
            if i == 5:                                             # give the outage run real work to lose
                tasks_f = os.path.join(work, "tasks.json")
                tasks = json.load(open(tasks_f)) if os.path.exists(tasks_f) else []
                tasks += [{"kind": "write_tool", "skill": "leonxlnx-taste-skill", "goal": "a flaky agent loop helper with retries", "status": "todo"},
                          {"kind": "write_tool", "skill": "seleniumbase-seleniumbase", "goal": "a wait helper", "status": "todo"}]
                json.dump(tasks, open(tasks_f, "w"), indent=2)
                ag = os.path.join(work, "agents", "news_scout.json")
                if os.path.exists(ag):                             # make the news scout due, so an agent meets the outage
                    a_ = json.load(open(ag)); a_["last_run"] = "2026-11-20T00:00"; json.dump(a_, open(ag, "w"), indent=2)
                notes = env["VERIFY_MODE_FILE"] + ".notes"
                if os.path.exists(notes):
                    os.remove(notes)
            r = subprocess.run([sys.executable, os.path.join(HERE, "support", "verify_run.py")], cwd=tmp, env=env,
                               capture_output=True, text=True, timeout=1500)
            idx = os.path.join(work, ".private_logs", "runs_index.jsonl")
            last = json.loads(open(idx).read().splitlines()[-1]) if os.path.exists(idx) else {}
            row = {"run": i, "outage": outage, "status": last.get("status"), "errors": last.get("errors"),
                   "llm_calls": last.get("llm_calls"), "breaker": last.get("llm_breaker_open")}
            rows.append(row)
            if r.returncode != 0 or row["status"] != "ok" or row["errors"]:
                failed.append(f"run {i}: exit {r.returncode}, status {row['status']}, errors {row['errors']}")
                if r.returncode != 0:
                    failed.append((r.stdout + r.stderr)[-2000:])
        if not any(r["breaker"] for r in rows if r["outage"]):
            failed.append("the outage run did not open the LLM circuit breaker")
        return {"suite": "regression (6 runs)", "ok": not failed, "passed": sum(1 for r in rows if r["status"] == "ok" and not r["errors"]),
                "failed": failed, "seconds": round(time.time() - t0, 1), "runs": rows, "tail": ""}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="also run the 6-run simulated regression")
    ap.add_argument("--engine", help="test this engine file instead of engine/swings_core.py")
    ap.add_argument("--suite", action="append", help="run only these suites")
    ap.add_argument("--json", help="write the results here")
    a = ap.parse_args(argv)
    engine = os.path.abspath(a.engine) if a.engine else None
    ok_iso, seen = isolation_check(engine)
    if not ok_iso:
        print(f"FAIL isolation: the engine would not run on a throwaway copy ({seen}); no suite was run")
        print("RESULT FAILED: isolation check")
        return 2
    results = [run_suite(s, engine) for s in (a.suite or SUITES)]
    for r in results:
        print(f"{'PASS' if r['ok'] else 'FAIL'} {r['suite']}: {r['passed']} passed, {len(r['failed'])} failed, {r['seconds']}s")
        for f in r["failed"][:10]:
            print(f"     - {f[:300]}")
        if r["tail"]:
            print("     last output:\n" + "\n".join("       " + l for l in r["tail"].splitlines()[-25:]))
    if a.full:
        g = run_regression(engine)
        results.append(g)
        print(f"{'PASS' if g['ok'] else 'FAIL'} {g['suite']}: {g['passed']}/6 runs ok, {g['seconds']}s")
        for f in g["failed"]:
            print(f"     - {f[:500]}")
    if "dir" in _BASE:
        shutil.rmtree(_BASE["dir"], ignore_errors=True)
    ok = all(r["ok"] for r in results)
    total = sum(r["passed"] for r in results if r["suite"] in SUITES)
    print(f"RESULT {'ALL PASS' if ok else 'FAILED'}: {total} tests in {len([r for r in results if r['suite'] in SUITES])} suites"
          + (", regression " + ("ok" if results[-1]["ok"] else "FAILED") if a.full else ""))
    summary = {"ok": ok, "ts": datetime.datetime.now().isoformat(timespec="seconds"), "tests": total,
               "suites": [{k: v for k, v in r.items() if k != "tail"} for r in results]}
    if a.json:
        json.dump(summary, open(a.json, "w"), indent=2)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(f"## Swings AI tests: {'all pass' if ok else 'FAILED'}\n\n| Suite | Result | Passed | Time |\n|---|---|---|---|\n")
            for r in results:
                f.write(f"| {r['suite']} | {'pass' if r['ok'] else 'FAIL'} | {r['passed']} | {r['seconds']} s |\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
