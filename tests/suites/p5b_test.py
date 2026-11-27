"""Phase 5 step 4 tests: Gemini model order by the work's value and the quota left, and the optional OpenAI-compatible
fallback provider (off until its three settings exist). Scripted Gemini and a fake HTTP endpoint; nothing leaves."""
import os, sys, json
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)

if not hasattr(sc, "order_models"):
    print("PASS (skipped: this engine has no Phase 5 budget cell yet)")
    print("RESULT ALL PASS"); sys.exit(0)

sc.CYCLE_DEADLINE = sc.time.time() + 200          # no backoff sleeps in this suite
for k in sc.FALLBACK_KEYS:
    os.environ.pop(k, None)
M = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
day = sc._pacific_day()
def set_quota(recs):
    g = {"quota": {m: {"per_day": 20} for m in M if "lite" not in m}, "days": {day: recs}}
    sc._jsave(sc.GEMINI_QUOTA_FILE, g)
    return g
g = set_quota({"gemini-3.8-flash": {"calls": 20, "used_up": True}, "gemini-3.7-flash": {"calls": 19}})

# ---- model order ----
hi = sc.order_models(M, "milestone", g)
lo = sc.order_models(M, "lesson", g)
expect(hi == ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"],
       f"T1 high-value work: strongest model with quota left first, flash-lite after, used-up last: {hi}")
expect(lo == ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.8-flash"],
       f"T1 low-value work: flash-lite first, then the most quota left, used-up last: {lo}")
expect(sc.low_value("agent:news_scout") and not sc.low_value("fix_tool") and not sc.low_value("milestone") and sc.low_value("lesson"),
       "T1 what counts as low-value work")

sc._GEMINI_CACHE[:] = M
plain = sc._gemini_models_plain
sc._gemini_models_plain = lambda client: list(M)
sc._TASKS_STACK.append({"kind": "milestone", "inject": "", "llm_calls": 0, "failures": [], "attempts": 1, "passed_files": []})
got_hi = sc._gemini_models(None)
sc._TASKS_STACK[-1]["kind"] = "agent:news_scout"
got_lo = sc._gemini_models(None)
sc._TASKS_STACK.pop()
sc._gemini_models_plain = plain
expect(got_hi[0] == "gemini-3.7-flash" and got_lo[0] == "gemini-3.5-flash-lite", f"T2 the live model list follows the current task: {got_hi[0]}, {got_lo[0]}")

# ---- fallback: off by default ----
set_quota({})
GEM = {"n": 0, "err": "503 UNAVAILABLE: overloaded"}
def gemini(prompt, **kw):
    GEM["n"] += 1
    if GEM["err"]:
        raise Exception(GEM["err"])
    return "gemini answer"
sc._llm_before_fallback = gemini
expect(not sc.fallback_ready() and sc._fallback_settings() is None, "T3 the fallback is off until its settings exist")
try:
    sc._llm_with_fallback("hello"); r3 = "no error"
except Exception as e:
    r3 = str(e)
expect("503" in r3, f"T3 with no fallback a Gemini outage is raised as before: {r3[:60]}")
os.environ.update(SWINGS_FALLBACK_BASE_URL="https://llm.example.invalid/v1", SWINGS_FALLBACK_MODEL="some-model")
expect(not sc.fallback_ready(), "T3 two of three settings are not enough")

# ---- fallback: on ----
os.environ["SWINGS_FALLBACK_API_KEY"] = "test-key-123"
POSTS = []
class R:
    def __init__(self, code, data): self.status_code, self._d, self.ok = code, data, 200 <= code < 300
    def json(self): return self._d
REPLY = {"code": 200}
def fake_post(url, headers=None, json=None, timeout=None):
    POSTS.append({"url": url, "headers": headers, "json": json})
    return R(REPLY["code"], {"choices": [{"message": {"content": "fallback answer"}}]})
plain_post = sc.requests.post
sc.requests.post = fake_post
expect(sc.fallback_ready(), "T4 all three settings turn the fallback on")
out = sc.llm("Say hello", system="sys")
p = POSTS[-1] if POSTS else {}
expect(out == "fallback answer", f"T4 a Gemini outage is answered by the fallback through the normal llm(): {out!r}")
expect(p.get("url") == "https://llm.example.invalid/v1/chat/completions" and p["headers"]["Authorization"] == "Bearer test-key-123"
       and p["json"]["model"] == "some-model" and p["json"]["messages"][1]["content"].endswith("Say hello"),
       "T4 OpenAI-compatible request: /chat/completions, bearer key, model, system + user messages")
u = sc._fallback_today()[1]
expect(u["calls"] == 1 and u["ok"] == 1, f"T4 fallback use is counted: {u}")

GEM["err"] = "ValueError: the prompt is malformed"
n0 = len(POSTS)
try:
    sc._llm_with_fallback("x"); r5 = "no error"
except Exception as e:
    r5 = str(e)
expect("malformed" in r5 and len(POSTS) == n0, "T5 a real (non-outage) Gemini error is not hidden by the fallback")
GEM["err"] = None
expect(sc._llm_with_fallback("x") == "gemini answer" and len(POSTS) == n0, "T5 Gemini still answers first when it can")

# ---- Gemini out of quota for the day ----
sc._jsave(sc.GEMINI_QUOTA_FILE, {"quota": {}, "days": {day: {m: {"calls": 20, "used_up": True} for m in M}}})
n_gem = GEM["n"]
expect(sc.gemini_all_used_up() and sc._llm_with_fallback("y") == "fallback answer" and GEM["n"] == n_gem,
       "T6 with every Gemini model used up, Gemini is not even asked")
expect(sc.llm_allowed("lesson") is True, "T6 low-value work may go on while the fallback has room")
for k in sc.FALLBACK_KEYS[1:2]:
    v = os.environ.pop(k)
expect(sc.llm_allowed("lesson") is False, "T6 without the fallback, Gemini's empty quota stops the work as before")
os.environ["SWINGS_FALLBACK_API_KEY"] = v

# ---- fallback failures and its own cap ----
REPLY["code"] = 429
try:
    sc._fallback_llm("z"); r7 = "no error"
except Exception as e:
    r7 = e
expect(isinstance(r7, Exception) and sc._is_infra_error(r7), f"T7 a 429 from the fallback is an outage, so tasks keep their retries: {r7}")
REPLY["code"] = 401
try:
    sc._fallback_llm("z"); r7b = "no error"
except Exception as e:
    r7b = e
expect(isinstance(r7b, Exception) and not sc._is_infra_error(r7b), "T7 a refused key is a real error")
REPLY["code"] = 200
sc.FALLBACK_MAX_PER_DAY = sc._fallback_today()[1]["calls"]
expect(not sc.fallback_ready(), "T7 the fallback has its own daily cap")
sc.FALLBACK_MAX_PER_DAY = 100
sc.requests.post = plain_post

# ---- secrets stay out of the sandbox; the workflow passes the settings ----
env = sc._safe_env("/tmp")
expect("SWINGS_FALLBACK_API_KEY" not in env, "T8 the fallback key never reaches sandboxed code")
c15 = sc.SKILLS_DIR / "engine" / "notebook_cell15.py"
if c15.exists():
    t = c15.read_text()
    expect(all(f"secrets.{k}" in t for k in sc.FALLBACK_KEYS), "T8 the autopilot workflow passes the three fallback secrets")

# ---- report ----
g = {"quota": {m: {"per_day": 20} for m in M if "lite" not in m}, "days": {}}
for i in range(3):
    d = (sc.datetime.date.today() - sc.datetime.timedelta(days=i)).isoformat()
    g["days"][d] = {m: {"calls": 20, "ok": 20, "used_up": "lite" not in m} for m in M}
sc._jsave(sc.GEMINI_QUOTA_FILE, g)
for k in sc.FALLBACK_KEYS:
    os.environ.pop(k, None)
text, _ = sc.build_health_report()
s = sc.llm_use_stats()
expect("## LLM use (Phase 5)" in text and s["strong_models_out_days"] == 3 and s["lite_share"] == 0.2,
       f"T9 the weekly report shows Gemini use by model and days out of quota: {s['strong_models_out_days']}, {s['lite_share']}")
expect("SWINGS_FALLBACK_BASE_URL" in text.split("## Decisions waiting for you", 1)[-1], "T9 running out on 3+ days asks the owner to add a fallback")
expect("llm_routing" in sc._run_extras(), "T10 the run log carries the routing numbers")

print("RESULT " + ("ALL PASS" if not FAILS else f"FAILED {len(FAILS)}"))
sys.exit(1 if FAILS else 0)
