# Swings AI — Findings

_Last updated: 2026-11-26_

## Notebook
- Colab notebook renamed: `Untitled0.ipynb` → `Swings_AI.ipynb`
- 6 code cells added (Setup → Config → Search → Clone & save skill → Skill router → Run)

## Flow
1. **Connect to GitHub** — REST Search API via `requests`. Optional `GITHUB_TOKEN` in Colab Secrets (60 → 5,000 req/hr).
2. **Filter UML projects** — queries `topic:uml`, `topic:plantuml`, `uml diagram in:name,description`; `stars:>=500`, public, not archived; sorted by stars.
3. **Verify open source** — keep only repos whose SPDX licence is in an OSI-approved allow-list (MIT, Apache-2.0, GPL/LGPL/AGPL, BSD, MPL, EPL, ISC…).
4. **Copy the project** — `git clone --depth 1` into `/content/skills/<owner-repo>/repo`.
5. **Save as a skill** — writes `SKILL.md` (frontmatter: name, description, source, licence, stars, language, topics) + `README_source.md`; all skills indexed in `registry.json`.
6. **Use when needed** — `SkillRouter` (scikit-learn TF-IDF + cosine similarity) matches a natural-language task to the best skill.

## Test run (sandbox, no clone)
| Repo | ★ | Licence |
|---|---|---|
| ashishps1/awesome-low-level-design | 28,257 | GPL-3.0 |
| plantuml/plantuml | 13,438 | LGPL-3.0 |
| yizhiyanhua-ai/fireworks-tech-graph | 12,062 | MIT |
| Agents365-ai/drawio-skill | 10,947 | MIT |
| plantuml-stdlib/C4-PlantUML | 7,465 | MIT |
| purocean/yn | 6,783 | AGPL-3.0 |
| AhmadHassan-BTed/OpenHeart | 5,918 | MIT |
| yuzutech/kroki | 4,415 | MIT |
| k1LoW/tbls | 4,407 | MIT |
| skanaar/nomnoml | 2,842 | MIT |

**Rejected (no / unclear licence):** gaphor/gaphor, awesome-diagramming, KSHObjcUML, markdown-preview-enhanced, vscode-markdown-pdf, aws-icons-for-plantuml, Mermrender, unclebob/uml-viewer.

**Router check:** "UML class diagram editor in the browser" → nomnoml (0.40); "draw a sequence diagram from text" → nomnoml / plantuml / kroki.

## Observations
- Licence API returns `None` or `NOASSERTION` for some popular repos (e.g. gaphor is Apache-2.0 but not detected) → they're rejected to stay safe.
- "Awesome"/curated-list repos slip in via topics; could add a filter on name containing `awesome`.
- Copyleft licences (GPL/AGPL) are open source but impose sharing obligations if you redistribute — consider restricting to permissive licences if the skills will be reused in company code.
- `/content` in Colab is wiped when the runtime resets → mount Google Drive to persist skills.

## Update 2 — Semantic router + executor (2026-11-26)
**New cells**
- **Cell 7 – `SemanticSkillRouter`**: `sentence-transformers` (`all-MiniLM-L6-v2`). Hybrid score = 0.75 × embedding similarity + 0.25 × TF-IDF. Embeddings cached to `SKILLS_DIR/embeddings_<model>.npz` (rebuilt only when skills change).
- **Cell 8 – `SkillExecutor` + Kroki**: auto-detects diagram language from the text (PlantUML, C4-PlantUML, Mermaid, Graphviz, nomnoml), falls back to the skill's topics, POSTs to `https://kroki.io/<engine>/svg`, displays inline and saves to `SKILLS_DIR/outputs/`.
- **Cell 9 – demo**: TF-IDF vs semantic comparison + two end-to-end renders.

**Verified in Colab**
- Model downloaded and loaded; cell 7 ~1 min (pip), cell 9 ~20 s.
- PlantUML sequence diagram rendered → `outputs/plantuml_20261126_001008.svg`
- Mermaid class diagram rendered → `outputs/mermaid_20261126_001011.svg`
- Routing differences observed:
  - "draw a sequence diagram from text" — TF-IDF: drawio-skill, fireworks-tech-graph, kroki · Semantic: nomnoml, fireworks-tech-graph, drawio-skill
  - "visualise my database schema" — TF-IDF: tbls, nomnoml, drawio-skill (semantic also surfaces tbls)

**Observations**
- `SKILLS_DIR` is still `/content/skills` (local runtime disk) — outputs and skills are lost on runtime reset unless pointed at `/content/drive/MyDrive/...`.
- Kroki public server receives the diagram text → use self-hosted Kroki for confidential diagrams.
- Router picks a skill but rendering is decided by the diagram text, so the chosen skill is informational for now.

## Update 3 — Self-editing agent + scheduler (2026-11-26)
**New cells**
- **Cell 10 – LLM brain**: free Gemini via Colab's built-in `google.colab.ai` (no API key). Available models include `google/gemini-3.5-flash-lite`, `gemini-3.6-flash`, `gemini-3.8-flash…`. Fallback: `GEMINI_API_KEY` secret + `google-genai`.
- **Cell 11 – Versioning + sandbox**: `SKILLS_DIR` is a git repo; `skill_history()`, `rollback(n)`. `run_sandboxed()` runs commands in a throw-away copy with a timeout.
- **Cell 12 – `CodeAgent`**:
  - `write_tool(skill, goal)` → writes `scripts/*.py` + `tests/test_*.py`, runs pytest in sandbox, retries with the error output (max 3), keeps + commits only on pass.
  - `improve_doc(skill)` → rewrites SKILL.md with When to use / How to use / Limitations; rejected if frontmatter breaks.
  - `reengineer(skill, goal, file_glob)` → edits cloned upstream code on a `swings-ai` branch inside `repo/`; kept only if a check command passes (default `py_compile`).
  - All actions logged to `SKILLS_DIR/agent_log.md`.
- **Cell 13 – Autopilot**: `tasks.json` queue (`add_task`), `autopilot_plan()` (agent queues its own work: skills with no scripts → write a tool; SKILL.md with no "How to use" → improve), `run_task_queue()`, `start_scheduler(every_minutes, refresh_days)` / `stop_scheduler()` using `schedule` in a background thread; weekly GitHub refresh.
- **Cell 14 – demo**.

**Verified**
- Locally with a fake LLM: failed attempt retried and fixed (passed attempt 2); broken re-engineering rejected after 3 attempts with no files changed; good re-engineering committed to `swings-ai` branch; git history correct.
- In Colab with real Gemini: `plantuml-plantuml` → `scripts/sequence_generator.py` + tests **PASSED on attempt 1**; SKILL.md improved; both committed (`65f57d9 plantuml-plantuml: improve SKILL.md`).

**Observations / limits**
- Scheduler only runs while the Colab runtime is alive (Colab disconnects idle/long sessions). 24/7 needs GitHub Actions, a cron VM, or Cloud Run jobs.
- "Sandbox" = temp copy + timeout; generated code still runs with the runtime's network and permissions. Fine for experiments, not true isolation (Docker/`firejail` would be).
- Re-engineering default check is `py_compile`; most UML repos are Java/JS (PlantUML is Java) → pass a `check_cmd` (e.g. `node --check`, `mvn -q compile`) for those.
- `SKILLS_DIR` still `/content/skills` → move to Drive or all self-edits vanish on reset.

## Update 4 — Drive, 24/7, isolation, multi-language checks (2026-11-26)
**1. Skills on Drive**
- `SKILLS_DIR = /content/drive/MyDrive/wings/skills` (the folder Mel had already moved to Drive). 10 skills + git history load correctly.
- Cloned source code now lives on local disk (`/content/skill_repos`, re-clonable via `ensure_repo()`); agent edits to it are saved on Drive as `patches/*.patch` and re-applied automatically after a re-clone (tested).
- Registry no longer stores absolute paths → same files work in Colab, Drive and GitHub Actions.
- Cell 4b = one-time migration helper. It found 10 old `repo/` folders inside the Drive skills folder that are no longer used (~0.5 GB, safe to delete).

**2. 24/7 via GitHub Actions (Cell 15)**
- `export_engine()` turns notebook cells 1–5, 10–13 into `engine/swings_core.py` + `engine/run_autopilot.py` + `.github/workflows/autopilot.yml` inside the skills folder (done, compiles).
- Workflow: every 3 h (+ manual run button, optional forced GitHub re-scan), Python 3.11 + Node 20 + Java 17, caches cloned repos, commits the agent's work back.
- Outside Colab the LLM is Gemini API (`GEMINI_API_KEY` repo secret, free tier from Google AI Studio, default model `gemini-flash-latest`).
- `connect_github(url)` (once) and `sync_skills()` keep Drive ⇄ GitHub in sync; the token goes in a one-off header, never saved in the remote URL.
- Simulated an Actions run locally: planner queued 3 tasks, all done and committed.
- Not yet connected — needs Mel's repo + secrets (see Next steps).

**3. Real isolation**
- Detected automatically: Colab → `unshare -n` + `setpriv` as `nobody`; Actions → same via passwordless `sudo`; fallback = temp copy + limits.
- Live Colab check: runs as `nobody`, network **blocked**, secrets **hidden**, CPU/file-size limits, 2 GB memory cap for LLM-written Python.
- Static safety scan rejects LLM code using subprocess / os.system / eval / exec / file deletion / ctypes / socket before it runs; the model is told why and retries.

**4. Language-aware re-engineering checks**
- Default check auto-selects by file type: Python (ast), Java (`javac`, ignores missing-dependency errors but catches syntax errors), JavaScript (`node --check`), TypeScript (esbuild/tsc if installed), JSON. Custom `check_cmd` still supported (e.g. Maven/Gradle builds).
- Default file pattern follows the skill's language (PlantUML → `**/*.java`).
- Bug found & fixed during testing: the 2 GB memory cap was inherited by `javac`, which then couldn't start, and the checker treated that as "OK". Memory cap now only applies to Python tests and the checker fails closed.
- Live: Gemini added Javadoc to `src/main/java/com/plantuml/ubrex/Capture.java`; Java check passed; patch `001-add-clear-javadoc-comments-to-every-publ.patch` saved on Drive.

**New Cell 16** – re-runnable health check of all of the above.

## Update 5 — Self-building agents, news watchers, GitHub plugin (2026-11-26)
**New cells**
- **Cell 17 – Plugins**: `ToolRegistry` (agents only get the tools in their spec; some tools are *protected*), `NewsPlugin` (Hacker News front page, rising GitHub repos from the last 7 days, dev.to / arXiv cs.SE / GitHub blog RSS; de-duplicated; daily digest in `news/YYYY-MM-DD.md`), knowledge log (`knowledge.md`), experiment builder, `GitHubPlugin`, `add_skill_from_repo` (licence-checked).
- **Cell 18 – Agent framework**: agents are JSON specs in `agents/` (role, prompt, tools, triggers, schedule, version, prompt history, success stats per version). Event bus `state/events.json`. `run_agent` = JSON tool-calling loop (max 6 tool calls). `orchestrator_tick()` runs due watchers, turns demand signals into events (pending tasks → `tasks.pending`; ≥3 new failures → `system.review`), dispatches events, and calls `auto_rollback()`.
- **Cell 19 – Seed agents**: architect, planner, maintainer, news_scout (every 3 h), builder, publisher, evolver (daily + on review). `autopilot_cycle()` now = skill upkeep + `orchestrator_tick()`, so Colab's scheduler and GitHub Actions both run the agents. `set_goal("...")` gives the system a goal.
- **Cell 20 – Live demo**.
- Cell 15 updated: engine now includes cells 17–19; workflow passes `SWINGS_GH_TOKEN` + `SWINGS_GITHUB_DRY_RUN`.

**How the system builds / evolves itself**
- Unhandled event → `agent.needed` → architect designs a new agent (max 20 agents, cannot grant protected tools, watchers at most hourly) → waiting events are re-queued to it.
- Evolver rewrites at most one weak agent's prompt per run (≥3 runs, <60% success); architect & evolver can't be rewritten; if a new prompt scores >25 points worse than the previous one after ≥3 runs, it's auto-rolled back.
- Experiments: one folder per experiment under `experiments/`, must pass offline pytest in the sandbox; record in `experiments.json`.

**GitHub plugin (one private repo per experiment)**
- Repo name `swings-exp-<slug>`, private, topic `swings-ai-experiment`; later runs push new commits to the same repo.
- Safety: only experiments that passed tests; secret scan before every push (blocked a planted `ghp_` token in testing); max 3 new repos/day; token sent as a one-off header; **dry-run by default** (`GITHUB_DRY_RUN = True`).
- Uses `SWINGS_GH_TOKEN` if set, else `GITHUB_TOKEN`.

**Verified**
- Local (scripted model): goal → planner → idea → builder (tests passed) → publisher; unhandled event → architect rejected a protected tool, then created a valid agent which handled the re-queued event; evolver blocked from rewriting architect; auto-rollback restored a worse prompt; live push to a local test repo produced a correct commit; secret scan blocked a leaked token.
- Colab (real Gemini + real news, ~5 min, dry-run publishing):
  - news_scout read live tech news, saved a trend note (audio DSP / PipeWire), queued 2 ideas.
  - builder built `loudness-equalization-dsp-filter` and `algorithmic-integer-factorization-discre…` — both **passed** tests.
  - publisher handled both (dry run — nothing created on GitHub).
  - planner turned the goal into a task; maintainer ran it → `plantuml-plantuml/scripts/class_diagram_generator.py` + tests **passed on attempt 1**.
- Found: **no GitHub token in Colab secrets** → plugin shows "not connected".

**Observations / risks**
- News is untrusted input: agents are told to treat it as data; the news-reading agent has no publish/create-agent tools; builds run sandboxed (no network, `nobody`); publishing needs passed tests + secret scan.
- Each tick makes many LLM calls (~5 min for 3 ticks); free Gemini limits may slow 24/7 runs.
- The publisher's LLM summary says "Published" even in dry-run — the tool result itself says DRY RUN.

## Update 6 — Live with GitHub (2026-11-26)
**Changes**
- Cell 1: Colab secret is named **`Wings`** (not `GITHUB_TOKEN`) → code now checks `GITHUB_SECRET_NAMES = ["GITHUB_TOKEN", "Wings"]` and hands the token to the GitHub plugin. Never printed.
- Cell 17: publishing is **LIVE by default in Colab** (`SWINGS_GITHUB_DRY_RUN` env can still force dry-run; GitHub Actions stays dry-run until the repo variable is set to `false`).
- Cell 21 (new): GitHub connection check + system health report.
- Cell 22 (new): publish all passed-but-unpublished experiments + verify on GitHub.
- Cell 23 (new): run one full system cycle with timing and model-call count.

**Results**
- GitHub: connected as **wizard-art007**, fine-grained token, API limit 5,000/h (was 60 anonymous).
- First live publish — both experiments now private repos with topic `swings-ai-experiment` and README/src/tests:
  - https://github.com/wizard-art007/swings-exp-loudness-equalization-dsp-filter
  - https://github.com/wizard-art007/swings-exp-algorithmic-integer-factorization-discre
- Full cycle: **4.1 min, 8 model calls, 0 failures**. Skills with tested tools 1 → 4 (ashishps1-awesome-low-level-design, yizhiyanhua-ai-fireworks-tech-graph, agents365-ai-drawio-skill), skills with good docs 1 → 4. 12 tasks still queued (~2 more cycles).
- Architect has 0 runs — no unhandled event occurred in real use yet.

**Gaps observed in the live run**
- Same generic tool goal for every skill ("text → diagram helper"), even for non-diagram skills.
- Success is self-reported by the model → "0 failures" is not a trustworthy quality signal.
- Tests are written by the same model as the code → can be shallow.
- News ideas are off-topic for UML (audio DSP, integer factorization); no interest profile.
- `knowledge.md` has 1 note; nothing is learned from failures; no search over past knowledge.
- ~30 s per model call; queue grows faster than it drains.
- Publisher's summary says "Published" during dry runs.
- 24/7 not yet connected (no skills repo, no `GEMINI_API_KEY` in GitHub).

## Capability roadmap (prioritised)
| # | Add | Why (seen in testing) | Effort |
|---|---|---|---|
| **P1 — reliability & quality** ||||
| 1 | Objective scoring: tests passed, coverage, lint, run time → replaces self-reported success | Evolver currently optimises a self-reported flag | M |
| 2 | Independent reviewer agent (different prompt/model) that critiques code + tests before keep/publish; reject trivial tests (coverage/mutation check) | Same model writes code and tests | M |
| 3 | Skill-specific goals: planner reads README and proposes a useful tool per skill, scored for value | Identical generic goal for all skills | S |
| 4 | Learn from failures: post-mortem note after every failed attempt, fed into next prompts | No failure learning | S |
| 5 | Structured tool results (status codes) so summaries can't misreport (dry-run vs published) | Publisher summary mismatch | S |
| 6 | Run lock + conflict handling so Colab scheduler and GitHub Actions don't edit at once | Two writers once 24/7 is on | S |
| **P2 — learning & memory** ||||
| 7 | Vector memory (ChromaDB/FAISS + sentence-transformers) over knowledge, news, experiments, code | 1 flat note file, no recall | M |
| 8 | Interest profile (UML, QA automation, Playwright/TS, agents…) to score news relevance + de-dupe ideas | Off-topic experiments | S |
| 9 | More sources: arXiv cs.AI, Product Hunt, Reddit (API), PyPI/npm trending, GitHub releases of tracked skills | Narrow view of "what's new" | M |
| 10 | Weekly "what I learned" digest (markdown + charts) committed to the skills repo | Hard to see progress | S |
| **P3 — building more kinds of projects** ||||
| 11 | Multi-language experiment templates: TypeScript/Playwright (matches Mel's stack), Java, web UI | Python-only now | M |
| 12 | Multi-step builds: plan → scaffold → implement → test → refactor (instead of one shot ≤300 lines) | Only tiny projects possible | L |
| 13 | Turn re-engineering patches into forks + PRs (with human approval) | Patches stay local | M |
| 14 | Skill composition: agents chain skills (e.g. code → class diagram → render → publish docs) | Skills used one at a time | M |
| **P4 — GitHub plugin** ||||
| 15 | Each experiment repo gets CI (GitHub Actions running its tests), status badge, LICENSE (MIT), `.gitignore` | Repos have no CI | S |
| 16 | "Experiments index" repo/README with table of all experiments, status, dates, links | Records spread across repos | S |
| 17 | Issues for follow-up ideas & failures; releases when an experiment improves | No tracking inside GitHub | S |
| 18 | Lifecycle: archive stale/failed repos after N days; promote good ones (approval to make public) | Repo sprawl at 3/day | S |
| **P5 — operations** ||||
| 19 | Finish 24/7: create skills repo, `GEMINI_API_KEY` + `SWINGS_GH_TOKEN` secrets, `SWINGS_GITHUB_DRY_RUN=false`, `connect_github()` | Not connected yet | S |
| 20 | Model routing + budget: flash-lite for agent steps, stronger model for code; max calls per cycle; response cache | ~30 s/call, queue backlog | M |
| 21 | Dashboard (agents, success over time, experiments, queue) + daily notification (email/Telegram/Slack) | Only visible inside notebook | M |
| 22 | Human approval queue for risky actions (public repos, PRs to others, new watcher agents) | Full autonomy on sensitive actions | S |
| 23 | Stronger security: gitleaks scan, dependency licence check, prompt-injection test set for agents | Regex-only secret scan | M |
| 24 | Move engine from notebook into a Python package repo with unit tests + CI; notebook becomes the control panel | 24 cells, hard to maintain | L |
| 25 | Clean-up: delete the 10 unused `repo/` folders on Drive (~0.5 GB) | Wasted space | S |

## Maturity & hosting assessment (2026-11-26)
**"Fully on its own" — realistic target:** it will always need an LLM, the internet (news/GitHub) and somewhere to run. The goal is *no single point of failure* and *graceful degradation*, not zero dependencies.

**Must-haves for unattended operation**
1. Own runtime: Docker Compose service + restart policy, heartbeat/watchdog, health endpoint (replaces Colab thread / Drive mount).
2. LLM independence: provider layer with fallbacks (Gemini API → second provider → local model via Ollama), retries, call budget, response cache. Colab's free `google.colab.ai` does not exist outside Colab.
3. Real storage: SQLite/Postgres instead of JSON files; daily backups (skills git repo push + DB dump off-server).
4. Real scheduler + queue: cron/systemd timers or APScheduler; persistent job queue with locks.
5. Container sandbox per experiment (`docker run --network none --memory --cpus --read-only`) instead of `unshare`.
6. Objective evaluation (tests/coverage/lint) driving the evolver; reviewer agent.
7. Self-healing: auto-disable agents that keep failing, retry with backoff, quarantine bad skills, auto-rollback.
8. Protected core: agents may evolve prompts/skills/experiments, but changes to the engine itself require tests + human approval.
9. Guardrails: global kill switch, spend/repo/day limits, approval queue for risky actions, least-privilege tokens, secret rotation.
10. Observability: structured logs with rotation, metrics, dashboard, daily summary + alerts (Telegram/email).
11. Engine as a tested package with CI; notebook only as control panel.

**Hosting on Hostinger**
- Shared / web / cloud hosting: not suitable (no long-running processes, no root, no Docker sandbox).
- KVM VPS: suitable. ~2 vCPU / 8 GB is a comfortable minimum with a hosted LLM API; more RAM/CPU only needed for a local fallback model (CPU-only inference is slow — fine as backup, not as main brain). No GPU.
- Pros: always on, root + Docker, predictable cost, no Colab disconnects or GitHub Actions minute/6-hour limits.
- Cons/risks: you are the sysadmin (updates, firewall, SSH keys, backups); the server runs AI-written code → strict container isolation, no open ports except SSH, nothing else important on that VPS; keep secrets in `.env` (chmod 600) or a secret manager.
- Recommended path: GitHub Actions now (free, already built) → VPS when continuous runs, a dashboard or longer jobs are needed. If any work (Aleron) data or credentials are involved, check with IT before hosting externally.

## Can Swings AI build its own model? (2026-11-26)
- **Training a general LLM from scratch:** not feasible on Colab/VPS (needs huge data + GPU clusters). Only toy-size models (nanoGPT-style, ~10–100M params) are possible — good for learning, too weak to be the brain.
- **Fine-tuning an open model (realistic path):** small open code models (~0.5B–7B, e.g. Qwen-Coder / Gemma / Llama families) with LoRA/QLoRA (Unsloth, PEFT/TRL) on a free Colab/Kaggle GPU; export to GGUF and serve with Ollama/llama.cpp on a CPU VPS as the local fallback brain. Check each model's licence.
- **Data it already generates:** every passed attempt (prompt → files that passed tests), failed attempts (negative examples), reviewer feedback, agent transcripts. Currently far too few (~10 good examples); hundreds–thousands needed.
- **Self-improving model loop (programmable):** collect → clean/dedupe/secret-scan → fine-tune → evaluate on a fixed held-out benchmark of tasks (tests pass rate) → promote only if better than current model → keep previous model for rollback. Human approval before promotion.
- **Caution:** using Gemini outputs as training data may be restricted by Google's API terms — check before training on them; prefer data from passed tests + open-licensed code.
- **Quick wins (small models, CPU-friendly):** news-relevance classifier, task router, test-quality scorer — trainable with scikit-learn / sentence-transformers on the system's own logs.

## Status check: does it run with the notebook closed? (2026-11-26)
- **No, not yet.** Everything so far ran inside the Colab runtime; closing the tab (or the runtime timing out) stops it. The Colab scheduler was never started.
- What already lives outside Colab: the skills folder on Drive and the 2 private experiment repos on GitHub (they stay).
- GitHub Actions engine + workflow are exported into the Drive skills folder but **not connected**: no skills repo on GitHub, `connect_github()` not run, no repo secrets.
- Still needed: (1) private repo `swings-ai-skills`; (2) push via `connect_github()` (token needs Contents + Workflows write, Administration write to create repos); (3) repo secrets `GEMINI_API_KEY` (Google AI Studio key — Colab's free Gemini doesn't exist on GitHub) and `SWINGS_GH_TOKEN`; (4) repo variable `SWINGS_GITHUB_DRY_RUN=false`; (5) one manual "Run workflow" to confirm.

## Connection progress (2026-11-26)
- Mel created private repo **wizard-art007/swings-ai-skills** and added the two Actions secrets himself.
- Could not verify the secrets page or continue: the Claude in Chrome extension failed on every action (screenshot, read, navigate) in both the existing and a fresh tab.
- Remaining: confirm secret names, push via `connect_github()` in Colab (Cell 15), set variable `SWINGS_GITHUB_DRY_RUN=false`, run the workflow once.
- Mel reports all steps done. Extension still failing on all tabs (Colab + GitHub), so verification moved into a self-check notebook cell (Cell 24): checks repo/private, pushed files, secret names, variable, last 5 workflow runs, failing step + last 40 log lines, latest autopilot commits, and prints a verdict. Awaiting its output.

## First GitHub Actions run (2026-11-26)
- Mel: the autopilot workflow run **failed**; Cell 24 shows "workflow runs found: 0".
- The 0 is most likely the fine-grained token lacking **Actions: read** (API returns 403/404 → empty list), not a missing workflow — the run is visible in the GitHub UI.
- Extension still failing → can't read the run log myself. Need the error text from the failed step.
- Bugs found while reviewing the engine for Actions (fix pending, independent of the failure):
  1. Cell 1 sets `SWINGS_GH_TOKEN` = `GITHUB_TOKEN`; on Actions that's the built-in token, which **overwrites** the PAT secret → repo creation would fail. Fix: only set it if `SWINGS_GH_TOKEN` isn't already set.
  2. `orchestrator_tick()` doesn't catch errors per agent → one model/API error fails the whole workflow. Fix: try/except around each `run_agent`.
  3. Single hard-coded API model name → add a fallback list of model names.

## GitHub Actions debugging (2026-11-26)
**Run #1 — failed in 27 s:** `SyntaxError: f-string expression part cannot include a backslash` (engine line 186). Colab = Python 3.12 (allowed), Actions = 3.11 (not allowed). Culprit: README-summary regex inside the SKILL.md f-string (Cell 4). Every other engine cell compiled fine on 3.11.

**Fixes pushed (commit 4adf9ac):**
- Cell 4: summary computed outside the f-string (3.11-safe; also corrected the regex).
- Cell 1: no longer overwrites the `SWINGS_GH_TOKEN` secret with the Actions built-in token.
- Cell 18: `_safe_run` — one agent error is logged, never stops the cycle.
- Cell 19: `autopilot_cycle` keeps going if skill upkeep or agents fail.
- Cell 15: workflow → Python 3.12, `setup-java@v5`; weekly refresh can't crash the run; `sync_skills()` replaces the one-time `connect_github$.
- Tested locally on Python 3.11 + 3.12, full agent test suite, and a "model always errors" test (cycle survives).

**Run #2 — "succeeded" in 4m40s but did no AI work:** `404 NOT_FOUND — models/gemini-2.0-flash is no longer available`; all hard-coded Gemini names are retired on the API (Colab offers gemini-3.5-flash-lite / 3.6-flash / 3.8-flash). Proved the `GEMINI_API_KEY` is valid. It did refresh skills and commit back ("refresh skills from GitHub", "autopilot run").

**Fix pushed (commit 7420f0b):** Cell 10 asks the API for its live model list (`_gemini_models`), picks newest *flash* text model first, skips image/tts/embedding, falls back through the rest. Unit-tested.
- `sync_skills()` correctly pulled the autopilot's commits and rebased Colab's change on top → two-way sync works.

**Run #3 — ✅ succeeded in 20m53s with real AI work** (unattended, laptop-independent): improved SKILL.md for `purocean-yn` and `ahmadhassan-bted-openheart`, committed + pushed (`d23507f autopilot run`). Log showed `503 UNAVAILABLE — model experiencing high demand` (free tier) and ~16 min between doc improvements.

**Reliability fixes (commit 7e7d154):**
- 503 / 429 / RESOURCE_EXHAUSTED → try the next available model instead of failing.
- 30-min time budget per GitHub run (`SWINGS_TIME_BUDGET_MIN`): stops starting new tasks/agents with 5 min margin.
- Workflow: `python -u` (live log), step `timeout-minutes: 38`, push step `if: always()` (partial work is never lost).
- Task errors are logged (with code location).
- `sync_skills()` rewritten: aborts half-finished rebases, merges autopilot work (`-X theirs`, auto-resolve), pushes `HEAD:main`. Needed because Colab + autopilot both edit log/state files → earlier push was rejected.

**Run #4 (live log works):** `GitHub auth: token` · `Sandbox: network blocked + runs as 'nobody'` · `Gemini models available: gemini-3.8-flash, 3.7-flash, 3.6-flash, 3.5-flash, 3.5-flash-lite` · SKILL.md improved for `yuzutech-kroki`, `k1low-tbls`.
- New GitHub-only bug: every `write_tool` → `PermissionError: [Errno 1] Operation not permitted`. Cause: tests run as `nobody` and create sub-folders the normal runner user can't delete → temp-dir cleanup crashed (Colab runs as root, so never seen there). **Reproduced locally as a non-root user with sudo** (old code fails with the identical error; new code passes).
- Fix (commit 2829502): after each sandboxed run, files are handed back (`chmod -R a+rwX` as `nobody`), and temp-dir cleanup can no longer crash a task.
- Gemini requests now time out after 120 s (commit f5eb44f; SDK option verified in Colab: "Gemini SDK timeout option: ok").
- Note: I briefly misread the clock and thought run #4 was hung for 25 min — it was ~9 min since the last log line; it was just slow, not stuck.

**Status:** 24/7 autopilot is live. Next scheduled runs (every 3 h at :23 UTC) use all fixes. Remaining limits: free-tier Gemini speed/503s (~20 min per cycle), GitHub Actions minutes on a private repo (~8 runs/day × ~20–30 min ≈ more than the 2,000 free min/month → consider every 6 h or a public repo).

## Repo made public (2026-11-26)
- Mel made `wizard-art007/swings-ai-skills` **public** → GitHub Actions on standard GitHub-hosted runners is free with no minute cap for public repos, so the every-3-hours schedule can stay.
- Verified: anonymous clone works (34 commits, 784 KB).
- Full-history scan of the public repo: **no tokens/keys** (only the code template `x-access-token:{self._token()}`); all "password" hits are open-source README text, docs examples or a news headline; no personal/work strings (name, company, Pearl, Tempus); every commit author is `swings-ai@local`.
- Secret values stay hidden; workflow only triggers on schedule + manual dispatch (no fork PRs), so outsiders can't run it or read secrets.
- Still true: experiment repos (`swings-exp-*`) are private; everything the system logs/learns in this repo is now public.
- Recommended: enable GitHub **Secret scanning + Push protection** (free for public repos), and add a secret scan before the autopilot's own push; never feed work (Aleron) data into this system.

## Hourly schedule?
- Mel wants the autopilot every **1 hour** instead of 3 (minutes are now unlimited).
- Assessment: GitHub side is fine (concurrency group queues runs; a cycle takes ~20–30 min). The real limit is the **free Gemini API quota** (requests per minute *and* per day): 24 cycles/day × dozens of calls can exhaust the daily quota, after which runs only collect 429 errors until the reset.
- Proposal: hourly cron + (1) daily model-call budget tracked in `state/`, (2) quick exit when there's nothing to do (no pending tasks/events/due watchers), (3) news scout stays every 3 h, evolver daily. → Busy hours do real work, idle hours cost ~1 min and 0 model calls.

## Next steps to go live 24/7
1. Create an empty **private** GitHub repo (e.g. `swings-ai-skills`).
2. Colab secret `GITHUB_TOKEN` must allow pushing to it, incl. workflow files (classic: `repo` + `workflow`; fine-grained: Contents + Workflows read/write).
3. Free Gemini API key from Google AI Studio → repo secret `GEMINI_API_KEY`.
4. Run `connect_github("https://github.com/<user>/swings-ai-skills.git")` in Cell 15.
5. GitHub → Actions → "Swings AI autopilot" → Run workflow once to confirm.

## Next ideas
- LLM layer: turn plain English ("class diagram for an order system") into PlantUML/Mermaid, then render.
- Code → UML: reverse-engineer diagrams from cloned repos (`pyreverse`, `py2puml`).
- Vector store (ChromaDB/FAISS) for chunk-level search across READMEs and code.
- Skill quality score: stars + recent commits + release cadence + permissive licence.
- Licence scanning of the actual files (`scancode-toolkit`), not only GitHub metadata.
- Gradio UI + scheduled refresh.
