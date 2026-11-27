"""F9 tests: fake Gemini replies, fake GitHub replies, a fake week of runs."""
import os, sys, json, datetime, hashlib, gzip, time as _time
os.environ["GITHUB_TOKEN"] = "tok-actions"; os.environ["SWINGS_GH_TOKEN"] = "tok-pat"
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
import requests
sc._llm_unbudgeted = fakellm.fake
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)
sc.CYCLE_DEADLINE = sc.time.time() + 3600
sc._RUN.update(id="20261127-120000-test", started=sc.time.time() - 600)
sc.GITHUB_TOKEN = "tok-actions"; sc.HEADERS["Authorization"] = "Bearer tok-actions"
for f in (sc.GEMINI_QUOTA_FILE, sc.LIMITS_FILE, sc.LIMITS_HISTORY_FILE, sc.REPORTS_FILE):
    f.unlink(missing_ok=True)
sc._apply_learned_cap()

# ---------------- 1: Gemini daily quota learned, used-up model skipped, all used up = no LLM ----------------
QUOTA_ERR = ("429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your current quota', 'status': "
             "'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': "
             "[{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', "
             "'quotaId': 'GenerateRequestsPerDayPerProjectPerModel-FreeTier', 'quotaDimensions': {'model': 'm-a'}, "
             "'quotaValue': '250'}]}]}}")
MINUTE_ERR = QUOTA_ERR.replace("PerDay", "PerMinute")
SENT = []
def inner(self, *, model, contents):
    SENT.append(model)
    if model == "m-a":
        raise RuntimeError(QUOTA_ERR)
    return "ok"
try:
    sc._metered_generate(inner, None, model="m-a", contents="x")
except Exception as e:
    pass
try:
    sc._metered_generate(inner, None, model="m-a", contents="x"); skipped = False
except sc.GeminiQuotaUsed as e:
    skipped = "429" in str(e)
expect(SENT == ["m-a"] and skipped, f"T1 a model that used its daily quota is skipped without a call: {SENT} {skipped}")
expect(sc._metered_generate(inner, None, model="m-b", contents="x") == "ok", "T1 the next model still works")
expect(sc._gemini_state()["quota"]["m-a"]["per_day"] == 250 and sc.LLM_DAILY_CAP == sc._CAP_DEFAULT,
       f"T1 the daily quota is learned; F3's cap is not lowered from partial knowledge (run #40): {sc.LLM_DAILY_CAP}")
def inner_min(self, *, model, contents):
    raise RuntimeError(MINUTE_ERR)
try:
    sc._metered_generate(inner_min, None, model="m-c", contents="x")
except Exception:
    pass
g = sc._gemini_state()["days"][sc._pacific_day()]
expect(g["m-c"]["minute_429"] == 1 and not g["m-c"]["used_up"], "T1 a per-minute 429 does not mark a model used up")
sc._GEMINI_CACHE[:] = ["m-a", "m-b"]
expect(sc.llm_allowed("write_tool") and not sc.gemini_all_used_up(), "T1 LLM still allowed while one model has quota")
def inner_b(self, *, model, contents):
    raise RuntimeError(QUOTA_ERR.replace("m-a", model))
try:
    sc._metered_generate(inner_b, None, model="m-b", contents="x")
except Exception:
    pass
expect(sc.gemini_all_used_up() and not sc.llm_allowed("write_tool"), "T1 every model used up: no LLM work, even high value")
expect(any(h["limit"].startswith("gemini: every model") for h in sc._f9_run()["hits"]), "T1 that is recorded as a limit hit")
next_day = datetime.datetime(2026, 11, 28, 8, 30, tzinfo=datetime.timezone.utc)      # 00:30 Pacific next day
expect(sc._pacific_day(next_day) == "2026-11-28" and sc._pacific_day(datetime.datetime(2026, 11, 28, 7, 30, tzinfo=datetime.timezone.utc)) == "2026-11-27",
       "T1 Gemini days follow midnight Pacific")

# ---------------- 2: 85% of the learned quota (only when every model's quota is known) ----------------
sc.GEMINI_QUOTA_FILE.unlink()
q = sc._gemini_state(); q["quota"]["m-a"] = {"per_day": 100}
rec = sc._gemini_rec(q, "m-a"); rec["calls"] = 85; sc._jsave(sc.GEMINI_QUOTA_FILE, q)
sc._GEMINI_CACHE[:] = ["m-a", "m-z"]
expect(sc.llm_allowed("lesson"), "T2 with one model's quota unknown, the learned view does not block (run #40 lesson)")
sc._GEMINI_CACHE[:] = ["m-a"]
expect(not sc.llm_allowed("lesson") and sc.llm_allowed("write_tool"),
       "T2 at 85% of the fully known daily quota low-value work is refused, high-value runs")
sc._GEMINI_CACHE[:] = []
sc.GEMINI_QUOTA_FILE.unlink()
expect(sc.LLM_DAILY_CAP == sc._CAP_DEFAULT and sc.llm_allowed("lesson"), "T2 with nothing learned F3's own cap stays in charge")

# ---------------- fake GitHub ----------------
GH = {"remaining": {"tok-actions": 900, "tok-pat": 4900}, "sent": [], "issues": 0, "patched": []}
def resp(status=200, body=None, headers=None, url=""):
    r = requests.models.Response(); r.status_code = status; r.url = url
    r._content = json.dumps(body if body is not None else {}).encode(); r.headers.update(headers or {})
    return r
def fake_send(self, method, url, *a, **kw):
    tok = str((kw.get("headers") or {}).get("Authorization", "")).split()[-1] if (kw.get("headers") or {}).get("Authorization") else ""
    GH["sent"].append((method, url, tok))
    lim = 5000 if tok == "tok-pat" else 1000
    h = {"x-ratelimit-limit": str(lim), "x-ratelimit-remaining": str(GH["remaining"].get(tok, 50)),
         "x-ratelimit-reset": str(int(_time.time()) + 1800), "x-ratelimit-resource": "search" if "/search/" in url else "core"}
    if url.endswith("/rate_limit"):
        return resp(200, {"resources": {"core": {"limit": lim, "remaining": GH["remaining"].get(tok, 50), "reset": int(_time.time()) + 1800},
                                        "search": {"limit": 30, "remaining": 30, "reset": int(_time.time()) + 60}}}, h, url)
    if url.endswith("/issues") and method.upper() == "POST":
        GH["issues"] += 1; return resp(201, {"number": 6 + GH["issues"]}, h, url)
    if "/issues/" in url and method.upper() == "PATCH":
        GH["patched"].append(url); return resp(200, {}, h, url)
    if method.upper() == "POST":
        return resp(201, {}, h, url)
    return resp(200, {"size": 2048, "private": False}, h, url)
sc._gh_send_plain = fake_send
sc.GITHUB.whoami = lambda: "tester"

# ---------------- 3: Actions token at 10% ----------------
GH["remaining"]["tok-actions"] = 100
requests.get("https://api.github.com/repos/x/y", headers=sc.HEADERS, timeout=5)
ok, why = sc.allowed("scout")
expect(not ok and "actions" in why, f"T3 scouting not allowed at 10% left: {why}")
expect(str(sc.scout_repos()).startswith("skipped"), "T3 repo scouting skipped")
expect(sc._safe_run("news_scout", "scan news")["summary"].startswith("skipped"), "T3 news scouting skipped")
needs = sc._jload(sc.NEEDS_FILE, [])
n = {"id": "need-f9", "need": "a test tool", "status": "open", "tries": 0, "type": "external", "domain": "qa_testing",
     "check": "from scripts.f9_dummy import f\nassert f() == 1\n"}
try:
    sc.search_for_need(n); raised = False
except sc.GitHubUnavailable as e:
    raised = "reserve" in str(e)
expect(raised, "T3 a need search raises GitHubUnavailable (the need keeps its tries)")
n0 = len(GH["sent"])
r = requests.post("https://api.github.com/user/repos", headers={"Authorization": "Bearer tok-pat"}, json={}, timeout=5)
expect(r.status_code == 201 and len(GH["sent"]) == n0 + 1, "T3 publishing with the personal token still goes through")

# ---------------- 4: 3% left = held back, not sent ----------------
GH["remaining"]["tok-actions"] = 30
requests.get("https://api.github.com/repos/x/y", headers=sc.HEADERS, timeout=5)
n0 = len(GH["sent"])
r = requests.get("https://api.github.com/repos/x/z", headers=sc.HEADERS, timeout=5)
expect(r.status_code == 429 and "Swings F9" in r.text and len(GH["sent"]) == n0, "T4 at 3% left the request is held back and not sent")
expect("rate limit" not in r.text.lower(), "T4 the held-back reply does not trigger _gh_get's 60-second rate-limit sleeps")
before = len(GH["sent"])
requests.get("https://api.github.com/repos/p/q", headers={"Authorization": "Bearer tok-pat"}, timeout=5)
expect(len(GH["sent"]) == before + 1, "T4 the other token is not affected")

# ---------------- 5: writes per minute and per hour ----------------
SLEPT = []
real_sleep = sc.time.sleep
sc.time.sleep = lambda s: SLEPT.append(s)
st = sc._f9_run(); st["writes"].clear()
for i in range(71):
    requests.post("https://api.github.com/repos/p/q/topics", headers={"Authorization": "Bearer tok-pat"}, json={}, timeout=5)
expect(len(SLEPT) == 1 and 0 < SLEPT[0] <= 61, f"T5 the 71st write in a minute pauses to the next minute: {SLEPT}")
st["writes"].clear(); st["writes"].extend([_time.time() - 3000 + i for i in range(450)])
n0 = len(GH["sent"])
r = requests.post("https://api.github.com/repos/p/q/topics", headers={"Authorization": "Bearer tok-pat"}, json={}, timeout=5)
expect(r.status_code == 429 and len(GH["sent"]) == n0 and not sc.allowed("github_write")[0], "T5 the 451st write in an hour is refused")
st["writes"].clear()
sc.time.sleep = real_sleep

# ---------------- 6: a fake week -> one report, every section ----------------
GH["remaining"]["tok-actions"] = 900
sc._f9_run()["gh"].clear()
rows, now = [], datetime.datetime.now()
for i in range(56):
    ts = (now - datetime.timedelta(hours=3 * i)).isoformat(timespec="seconds")
    rows.append({"ts": ts, "run": f"r{i}", "gemini_calls": 40 + i % 30, "gemini_cap": 225, "gemini_overloads": i % 4,
                 "gemini_used_up": [], "gh_min_pct": {"actions:core": 80, "personal:core": 95}, "writes": 12, "minutes": 4 + i % 20,
                 "budget": 30, "near_budget": False, "new_repos": i % 2, "git_mb": 6.2, "big_files": 0, "queue_todo": 3,
                 "slowdowns": ["GitHub writes"] if i == 5 else [], "hits": []})
sc.LIMITS_HISTORY_FILE.write_text("".join(json.dumps(r) + "\n" for r in reversed(rows)))
sc.PRIVATE_LOG_DIR.mkdir(exist_ok=True)
with open(sc.PRIVATE_LOG_DIR / "runs_index.jsonl", "a") as f:
    for i in range(3):
        f.write(json.dumps({"run": (now - datetime.timedelta(hours=3 * i)).strftime("%Y%m%d-%H%M%S") + "-actions",
                            "status": "ok", "errors": i, "open_issues": 1}) + "\n")
p = sc.weekly_report()
text = p.read_text() if p else ""
expect(p and all(s in text for s in ("Within free limits: yes", "## Growth", "## Health", "## Limits", "## Decisions waiting for you"))
       and "Gemini daily calls" in text and "GitHub actions:core" in text, "T6 a week of runs gives a report with every section")
expect(GH["issues"] == 1 and sc._jload(sc.REPORTS_FILE, {})[sc._week_key()].get("issue") == 7, "T6 one issue is opened")
expect(sc.weekly_report() is None and GH["issues"] == 1, "T6 a second run in the same week writes nothing")
rep = sc._jload(sc.REPORTS_FILE, {}); rep["2026-W40"] = {"issue": 3, "verdict": "yes"}; sc._jsave(sc.REPORTS_FILE, rep)
sc.weekly_report(force=True)
expect(any(u.endswith("/issues/3") for u in GH["patched"]), "T6 last week's issue is closed when the new one opens")
rows[0]["hits"] = ["GitHub rate limit (actions)"]
sc.LIMITS_HISTORY_FILE.write_text("".join(json.dumps(r) + "\n" for r in reversed(rows)))
t2, v2 = sc.build_health_report()
expect(v2 == "no" and t2.splitlines()[2].startswith("**Within free limits: no.**") and "GitHub rate limit (actions)" in t2,
       "T6 a week with a limit hit says no on the first line")
expect("tok-" not in text, "T6 no token in the report")

# ---------------- 7: big files and pruning ----------------
def fingerprint(paths):
    h = hashlib.sha256()
    for root in paths:
        for f in sorted(sc.Path(root).rglob("*")) if sc.Path(root).is_dir() else [sc.Path(root)]:
            if f.is_file() and ".git" not in f.parts:
                h.update(str(f).encode()); h.update(f.read_bytes())
    return h.hexdigest()
KEEP = [sc.SKILLS_DIR / "plantuml-plantuml", sc.STATE_DIR / "experiences.jsonl", sc.SKILLS_DIR / "memory" / "decisions.jsonl",
        sc.STATE_DIR / "plan.json", sc.SKILLS_DIR / "registry.json"]
fp0 = fingerprint(KEEP)
big = sc.EXPERIMENTS_DIR / "f9-big" / "data.bin"; big.parent.mkdir(parents=True, exist_ok=True)
with open(big, "wb") as f:
    f.truncate(60 * 1000 * 1000)
got = sc.size_guard()
gi = (sc.SKILLS_DIR / ".gitignore").read_text()
expect("experiments/f9-big/data.bin" in got and "experiments/f9-big/data.bin" in gi and big.exists(), "T7 a 60 MB file is kept out of git, not deleted")
runs = sc.PRIVATE_LOG_DIR / "runs"
old = runs / (datetime.date.today() - datetime.timedelta(days=45)).isoformat(); old.mkdir(parents=True, exist_ok=True)
(old / "a.jsonl").write_text('{"x": 1}\n')
new = runs / (datetime.date.today() - datetime.timedelta(days=10)).isoformat(); new.mkdir(parents=True, exist_ok=True)
(new / "b.jsonl").write_text('{"y": 2}\n')
packed = sc.prune_old_logs()
arch = runs / "archive" / f"{datetime.date.today() - datetime.timedelta(days=45):%Y-%m}.jsonl.gz"
expect(old.name in packed and not old.exists() and new.exists() and arch.exists() and b'"x": 1' in gzip.open(arch).read(),
       "T7 logs older than 30 days are packed, the last 30 days stay")
expect(fingerprint(KEEP) == fp0, "T7 skills, tools, experiences, decisions, plan and registry untouched")
big.unlink()

# ---------------- 8: schedule advice, workflow untouched ----------------
wf = sc.SKILLS_DIR / ".github" / "workflows" / "autopilot.yml"
wf0 = wf.read_text() if wf.exists() else None
eight = [{"ts": now.isoformat(), "queue_todo": 0 if i < 7 else 2, "gh_min_pct": {}, "gemini_calls": 10, "gemini_cap": 225} for i in range(8)]
adv = sc.schedule_advice(eight)
expect(adv and "every 6 hours" in adv[0], f"T8 an empty queue in 7 of 8 runs gives schedule advice: {adv}")
sc.sustainability_step()
expect((wf.read_text() if wf.exists() else None) == wf0, "T8 the workflow file is unchanged")

# ---------------- 9: snapshot + meter safety ----------------
s = sc._jload(sc.LIMITS_FILE, {})
expect(all(k in s for k in ("gemini", "github", "runtime", "repos", "sizes", "queue_todo", "slowdowns", "hits")) and
       s["github"].get("actions", {}).get("core", {}).get("limit") == 1000 and s["sizes"]["daily"].get("skills_mb") == 2.0,
       f"T9 limits.json holds header values and repo sizes: {s.get('github')}")
expect(len(sc._read_history()) >= 1 and sc._read_history()[-1]["run"] == sc._RUN["id"], "T9 one history line per run")
real_before = sc._gh_before
def boom(*a, **k):
    raise ValueError("meter bug")
sc._gh_before = boom
n0 = len(GH["sent"])
r = requests.get("https://api.github.com/repos/x/y", headers=sc.HEADERS, timeout=5)
expect(len(GH["sent"]) == n0 + 1 and r.status_code == 200, "T9 a broken meter lets the request through")
sc._gh_before = real_before
ex = sc._run_extras()
expect("limits" in ex and "gemini_cap" in ex["limits"], f"T9 the run summary carries limits: {ex.get('limits')}")
print("RESULT", "ALL PASS" if not FAILS else f"{len(FAILS)} FAILED")
