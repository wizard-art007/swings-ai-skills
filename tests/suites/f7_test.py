"""F7 tests: a local bare git repo stands in for GitHub."""
import os, sys, json, subprocess, tempfile, shutil, datetime
sys.path.insert(0, os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core as sc, fakellm
sc._llm_unbudgeted = fakellm.fake
FAILS = []
def expect(c, m):
    print(("PASS " if c else "FAIL ") + m); c or FAILS.append(m)
HUB = tempfile.mkdtemp(prefix="fakegh-")
CREATED = []
G = sc.GITHUB
G._token = lambda: "test-token"
G.whoami = lambda: "tester"
G.repo_exists = lambda owner, name: os.path.exists(os.path.join(HUB, name + ".git"))
def create_repo(name, description, private=True):
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", os.path.join(HUB, name + ".git")], check=True)
    CREATED.append(name); return f"https://github.com/tester/{name}"
G.create_repo = create_repo
G._remote = lambda owner, name: os.path.join(HUB, name + ".git")
class R:
    ok = True
    def json(self): return {"private": True}
real_get = sc.requests.get
sc.requests.get = lambda url, *a, **k: R() if "/repos/tester/" in url else real_get(url, *a, **k)
sc.CYCLE_DEADLINE = sc.time.time() + 3600
def remote_files(name):
    out = subprocess.run(["git", "--git-dir", os.path.join(HUB, name + ".git"), "ls-tree", "-r", "--name-only", "main"],
                         capture_output=True, text=True).stdout.split()
    return out
def remote_blob(name, path):
    return subprocess.run(["git", "--git-dir", os.path.join(HUB, name + ".git"), "rev-parse", f"main:{path}"],
                          capture_output=True, text=True).stdout.strip()

exps = sc.load_experiments()
for s_, v in list(exps.items()):                # start from the pre-F7 state, whatever the live repo has now
    if v.get("kind") == "project":              # F8 projects came later (one graduated on 27 Nov)
        exps.pop(s_); continue
    for k in ("projects_path", "projects_url", "pushed"):
        v.pop(k, None)
sc._jsave(sc.EXPERIMENTS_FILE, exps)
expect(publisher_ok := "projects repo" in sc.load_agents()["publisher"].system_prompt and
       "graduate_project" in sc.load_agents()["publisher"].tools, "publisher agent upgraded (prompt + tool)")
expect(sc.load_agents()["publisher"].version == 3, f"publisher prompt change is versioned: v{sc.load_agents()['publisher'].version}")

# migration: all passed experiments go in, the 3 own-repo ones keep their links
r = sc.publish_pending()
files = remote_files("swings-ai-projects")
passed = [s for s, e in exps.items() if e["status"] == "passed"]
expect(CREATED == ["swings-ai-projects"], f"only the projects repo was created: {CREATED}")
expect(all(any(f.startswith(f"experiments/{s}/") for f in files) for s in passed), f"all {len(passed)} passed experiments are folders")
expect(not any(f.startswith("experiments/snaptrap-fake-server/") for f in files), "the failed experiment is not published")
idx = subprocess.run(["git", "--git-dir", os.path.join(HUB, "swings-ai-projects.git"), "show", "main:README.md"],
                     capture_output=True, text=True).stdout
expect(all(exps[s]["title"][:30] in idx for s in passed) and idx.count("[own repo]") == 3, "index lists every experiment; the 3 old repos linked")

# test 1: five more in one day -> no new repo
for i in range(5):
    d = sc.EXPERIMENTS_DIR / f"t-exp-{i}"; (d / "src").mkdir(parents=True, exist_ok=True); (d / "tests").mkdir(exist_ok=True)
    (d / "src" / "m.py").write_text(f"X = {i}\n"); (d / "tests" / "test_m.py").write_text("def test_x():\n    assert True\n")
    (d / "README.md").write_text(f"# t{i}\n")
    e = sc.load_experiments(); e[f"t-exp-{i}"] = {"title": f"Test exp {i}", "status": "passed", "created": "2026-11-27T01:00"}
    sc._jsave(sc.EXPERIMENTS_FILE, e)
for i in range(5):
    sc.GITHUB.publish_experiment(f"t-exp-{i}")            # old entry point -> folder
files = remote_files("swings-ai-projects")
expect(CREATED == ["swings-ai-projects"] and all(f"experiments/t-exp-{i}/src/m.py" in files for i in range(5)),
       "T1 5 experiments published in one day: 5 folders, no new repo")
expect(sc._run_extras()["projects_waiting"] == 0, "nothing left waiting")

# test 2: fake token refused
d = sc.EXPERIMENTS_DIR / "t-secret"; (d / "src").mkdir(parents=True, exist_ok=True)
(d / "src" / "cfg.py").write_text('TOKEN = "ghp_' + "a" * 36 + '"\n')
e = sc.load_experiments(); e["t-secret"] = {"title": "secret", "status": "passed"}; sc._jsave(sc.EXPERIMENTS_FILE, e)
out = sc.publish_experiment_folder("t-secret")
expect("possible secrets" in out and not any(f.startswith("experiments/t-secret/") for f in remote_files("swings-ai-projects")),
       f"T2 file with a fake token refused: {out[:60]}")

# test 3: republish touches only its own folder
before = {f: remote_blob("swings-ai-projects", f) for f in remote_files("swings-ai-projects") if f.startswith("experiments/t-exp-")}
(sc.EXPERIMENTS_DIR / "t-exp-2" / "src" / "m.py").write_text("X = 'changed'\n")
sc.publish_experiment_folder("t-exp-2")
after = {f: remote_blob("swings-ai-projects", f) for f in remote_files("swings-ai-projects") if f.startswith("experiments/t-exp-")}
changed = [f for f in before if before[f] != after.get(f)]
expect(changed == ["experiments/t-exp-2/src/m.py"], f"T3 republish changed only its folder: {changed}")

# test 4: graduation
e = sc.load_experiments()
e["t-exp-0"].update(kind="project", skills=["mermaid-js-mermaid", "microsoft-playwright"],
                    milestones=[{"name": "a", "done": True}, {"name": "b", "done": True}])
e["t-exp-1"].update(kind="project", skills=["mermaid-js-mermaid"], milestones=[{"name": "a", "done": True}])
e["t-exp-3"].update(kind="project", skills=["a", "b"], milestones=[{"name": "a", "done": True}, {"name": "b", "done": False}])
e["t-exp-4"].update(kind="project", skills=["a", "b"], milestones=[{"name": "a", "done": True}])
sc._jsave(sc.EXPERIMENTS_FILE, e)
got = sc.graduate_ready()
e = sc.load_experiments()
expect("swings-exp-t-exp-0" in CREATED and e["t-exp-0"].get("graduated"), f"T4 qualifying project graduated: {got}")
expect("stays a folder" in sc.graduate_project("t-exp-1") and "stays a folder" in sc.graduate_project("t-exp-3"),
       "T4 one skill / unfinished milestones -> stays a folder")
expect("limit" in sc.graduate_project("t-exp-4"), "T4 second graduation the same day waits (1/day)")
idx = subprocess.run(["git", "--git-dir", os.path.join(HUB, "swings-ai-projects.git"), "show", "main:README.md"],
                     capture_output=True, text=True).stdout
expect("swings-exp-t-exp-0" in idx, "index links the graduated project's repo")
expect("swings-exp-t-exp-0" in "".join(remote_files("swings-ai-projects")) or remote_files("swings-exp-t-exp-0"),
       "graduated repo has the code")
# dry run + public repo guard
expect("would publish" in str(sc.publish_to_projects_repo("t-exp-1", dry_run=True).get("dry_run")), "dry run pushes nothing")
R.json = lambda self: {"private": False}
try:
    sc.publish_to_projects_repo("t-exp-1"); expect(False, "public projects repo refused")
except RuntimeError as ex:
    expect("PUBLIC" in str(ex), "public projects repo refused")
R.json = lambda self: {"private": True}
gi = (sc.SKILLS_DIR / ".gitignore").read_text()
expect(".projects_repo/" in gi, "local clone is git-ignored in the public skills repo")
print("RESULT", "ALL PASS" if not FAILS else f"{len(FAILS)} FAILED")
