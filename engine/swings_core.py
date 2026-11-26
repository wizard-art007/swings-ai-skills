"""Swings AI engine — generated from Swings_AI.ipynb. Edit the notebook, then export_engine()."""
# ===== Cell 1: Setup =====
import os, json, re, shutil, subprocess, datetime, base64, textwrap
from pathlib import Path
import requests

# GitHub token is optional but raises the API limit from 60 to 5,000 requests/hour.
# In Colab: click the key icon (Secrets) -> add GITHUB_TOKEN -> enable notebook access.
GITHUB_TOKEN = None
try:
    from google.colab import userdata
    GITHUB_TOKEN = userdata.get("GITHUB_TOKEN")
except Exception:
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"
print("GitHub auth:", "token" if GITHUB_TOKEN else "anonymous (60 req/hr)")

# ===== Cell 2: Config =====
# Skill knowledge (SKILL.md, scripts, tests, registry, history) lives on Google Drive -> survives resets.
# Large cloned source code lives on fast local disk and can be re-cloned any time;
# the agent's edits to that code are saved on Drive as patch files.
try:
    import google.colab  # noqa: F401
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    from google.colab import drive
    if not os.path.ismount("/content/drive"):
        drive.mount("/content/drive")
    SKILLS_DIR = Path("/content/drive/MyDrive/wings/skills")   # your existing Drive folder
    REPO_CACHE = Path("/content/skill_repos")
else:  # GitHub Actions / local machine
    SKILLS_DIR = Path(os.environ.get("SWINGS_SKILLS_DIR", "./skills")).resolve()
    REPO_CACHE = Path(os.environ.get("SWINGS_REPO_CACHE", "./.skill_repos")).resolve()
SKILLS_DIR.mkdir(parents=True, exist_ok=True)
REPO_CACHE.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = SKILLS_DIR / "registry.json"
print("Skills on:", SKILLS_DIR, "| source cache:", REPO_CACHE)

SEARCH_QUERIES = [
    "topic:uml",
    "topic:plantuml",
    "uml diagram in:name,description",
]
MIN_STARS = 500
MAX_RESULTS = 10          # how many repos to turn into skills
CLONE_DEPTH = 1           # shallow clone = latest code only

# OSI-approved open-source licences we accept (SPDX ids)
OPEN_SOURCE_LICENSES = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "GPL-2.0", "GPL-3.0",
    "LGPL-2.1", "LGPL-3.0", "AGPL-3.0", "MPL-2.0", "EPL-1.0", "EPL-2.0",
    "ISC", "Unlicense", "0BSD", "Zlib", "Artistic-2.0", "BSL-1.0",
}

# ===== Cell 3: Search GitHub =====
def search_repos(query, min_stars=MIN_STARS, per_page=50):
    q = f"{query} stars:>={min_stars} is:public archived:false"
    r = requests.get("https://api.github.com/search/repositories",
                     headers=HEADERS,
                     params={"q": q, "sort": "stars", "order": "desc", "per_page": per_page},
                     timeout=30)
    r.raise_for_status()
    return r.json().get("items", [])

def is_open_source(repo):
    lic = (repo.get("license") or {}).get("spdx_id")
    return lic in OPEN_SOURCE_LICENSES, lic

def find_uml_projects():
    seen, results = set(), []
    for q in SEARCH_QUERIES:
        for repo in search_repos(q):
            if repo["full_name"] in seen:
                continue
            seen.add(repo["full_name"])
            ok, lic = is_open_source(repo)
            if ok:
                results.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "url": repo["html_url"],
                    "clone_url": repo["clone_url"],
                    "stars": repo["stargazers_count"],
                    "license": lic,
                    "language": repo.get("language"),
                    "topics": repo.get("topics", []),
                    "description": repo.get("description") or "",
                    "default_branch": repo.get("default_branch"),
                })
            else:
                print(f"  skipped {repo['full_name']} (licence: {lic})")
    results.sort(key=lambda x: x["stars"], reverse=True)
    return results[:MAX_RESULTS]

# ===== Cell 4: Clone + save as skill =====
def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]

def get_readme(full_name):
    r = requests.get(f"https://api.github.com/repos/{full_name}/readme", headers=HEADERS, timeout=30)
    if r.status_code != 200:
        return ""
    return base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")

def repo_dir(skill_name):
    return REPO_CACHE / skill_name

def clone_repo(project, dest):
    if dest.exists():
        shutil.rmtree(dest)
    subprocess.run(["git", "clone", "--depth", str(CLONE_DEPTH), "--quiet",
                    project["clone_url"], str(dest)], check=True)

def ensure_repo(skill):
    """Make sure the skill's source code is on local disk; re-clone + re-apply saved patches if needed."""
    dest = repo_dir(skill["skill_name"])
    if not dest.exists():
        clone_repo(skill, dest)
        patches = sorted(Path(skill["path"], "patches").glob("*.patch"))
        if patches:
            subprocess.run(["git", "checkout", "-q", "-B", "swings-ai"], cwd=dest)
            for p in patches:
                r = subprocess.run(["git", "-c", "user.name=Swings AI", "-c", "user.email=swings-ai@local",
                                    "am", "-q", "--3way", str(p)], cwd=dest, capture_output=True, text=True)
                if r.returncode != 0:
                    subprocess.run(["git", "am", "--abort"], cwd=dest)
                    print(f"  patch {p.name} no longer applies to upstream; skipped")
    return dest

def save_as_skill(project, clone=True):
    skill_name = slug(project["full_name"].replace("/", "-"))
    skill_dir = SKILLS_DIR / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    readme = get_readme(project["full_name"])
    (skill_dir / "README_source.md").write_text(readme, encoding="utf-8")

    if clone:
        clone_repo(project, repo_dir(skill_name))

    # keep the licence file with the skill (required by most OSS licences)
    lic_files = []
    for p in repo_dir(skill_name).glob("LICEN*"):
        shutil.copy(p, skill_dir / p.name)
        lic_files.append(p.name)

    skill_md_path = skill_dir / "SKILL.md"
    if skill_md_path.exists() and "## How to use" in skill_md_path.read_text(encoding="utf-8"):
        pass   # keep the agent-improved SKILL.md on refresh
    else:
        skill_md = f"""---
name: {skill_name}
description: {project['description'][:200].replace(chr(10), ' ')}
source: {project['url']}
license: {project['license']}
stars: {project['stars']}
language: {project['language']}
topics: {', '.join(project['topics'])}
saved: {datetime.date.today().isoformat()}
---

# {project['full_name']}

Use this skill when the task involves: {', '.join(project['topics'][:10]) or 'UML diagrams'}.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): {', '.join(lic_files) or 'see source'}
- Original README: `README_source.md`

## Summary from README
{textwrap.shorten(re.sub(r'<[^>]+>|!\\[.*?\\]\\(.*?\\)', '', readme), 1500)}
"""
        skill_md_path.write_text(skill_md, encoding="utf-8")
    return {**project, "skill_name": skill_name, "readme_text": readme[:5000]}

def build_skills(clone=True):
    projects = find_uml_projects()
    registry = load_registry()
    for p in projects:
        print(f"-> {p['full_name']}  ★{p['stars']}  [{p['license']}]")
        try:
            skill = save_as_skill(p, clone=clone)
            registry[skill["skill_name"]] = skill
        except Exception as e:
            print("   failed:", e)
    stored = {k: {kk: vv for kk, vv in v.items() if kk not in ("path", "repo_path")} for k, v in registry.items()}
    REGISTRY_FILE.write_text(json.dumps(stored, indent=2))
    print(f"\nSaved {len(registry)} skills to {SKILLS_DIR}")
    return load_registry()

def load_registry():
    """Paths are worked out at load time, so the registry works on Drive, Colab and GitHub Actions."""
    if not REGISTRY_FILE.exists():
        return {}
    reg = json.loads(REGISTRY_FILE.read_text())
    for name, s in reg.items():
        s["skill_name"] = name
        s["path"] = str(SKILLS_DIR / name)
        s["repo_path"] = str(repo_dir(name))
    return reg

# ===== Cell 5: Use a skill when needed =====
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SkillRouter:
    """Picks the best saved skill for a natural-language task."""
    def __init__(self):
        self.registry = load_registry()
        self.names = list(self.registry)
        docs = [" ".join([s["full_name"], s["description"], " ".join(s["topics"]),
                          s.get("language") or "", s.get("readme_text", "")])
                for s in self.registry.values()]
        self.vec = TfidfVectorizer(stop_words="english")
        self.matrix = self.vec.fit_transform(docs) if docs else None

    def find(self, task, top_k=3):
        if self.matrix is None:
            return []
        scores = cosine_similarity(self.vec.transform([task]), self.matrix)[0]
        ranked = sorted(zip(self.names, scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self.registry[n], round(float(s), 3)) for n, s in ranked]

    def use(self, task):
        matches = self.find(task, top_k=1)
        if not matches or matches[0][1] == 0:
            print("No matching skill found.")
            return None
        skill, score = matches[0]
        print(f"Using skill: {skill['skill_name']} (score {score})")
        print(Path(skill["path"], "SKILL.md").read_text()[:1500])
        return skill

# ===== Cell 10: LLM brain (free Gemini) =====
# In Colab: built-in google.colab.ai (no API key).
# Elsewhere (GitHub Actions): Gemini API with a GEMINI_API_KEY secret (free tier from Google AI Studio).
LLM_MODEL = os.environ.get("SWINGS_LLM_MODEL")   # None = default model

def _colab_ai():
    try:
        from google.colab import ai
        return ai
    except Exception:
        return None

def llm(prompt, system="You are an expert software engineer.", model=LLM_MODEL, retries=3):
    full = f"{system}\n\n{prompt}"
    for attempt in range(retries):
        try:
            ai = _colab_ai()
            if ai is not None:
                return ai.generate_text(full, model_name=model) if model else ai.generate_text(full)
            key = os.environ.get("GEMINI_API_KEY")
            if not key:
                try:
                    from google.colab import userdata
                    key = userdata.get("GEMINI_API_KEY")
                except Exception:
                    pass
            if not key:
                raise RuntimeError("No LLM: google.colab.ai missing and no GEMINI_API_KEY.")
            from google import genai
            client = genai.Client(api_key=key)
            return client.models.generate_content(model=model or "gemini-flash-latest", contents=full).text
        except RuntimeError:
            raise
        except Exception as e:          # rate limits / transient errors
            if attempt == retries - 1:
                raise
            time.sleep(20 * (attempt + 1))

FILE_BLOCK = re.compile(r"###\s*FILE:\s*(?P<path>[^\n]+)\n```[\w+-]*\n(?P<body>.*?)```", re.S)

def parse_files(text):
    """LLM replies with  ### FILE: path  followed by a fenced code block."""
    return {m["path"].strip(): m["body"] for m in FILE_BLOCK.finditer(text)}

FILE_FORMAT = ("Reply ONLY with files in this exact format, one block per file:\n"
               "### FILE: relative/path.ext\n```python\n<full file content>\n```")


# ===== Cell 11: Versioning + isolated sandbox =====
import tempfile, sys, time, ast, resource

def git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)

GITIGNORE_LINES = ["*/repo/", "outputs/", "*.npz", "__pycache__/", ".skill_repos/", ".pytest_cache/"]

def init_skill_versioning():
    """SKILLS_DIR is a git repo so every self-edit can be reviewed or rolled back."""
    if not (SKILLS_DIR / ".git").exists():
        git(["init", "-q", "-b", "main"], SKILLS_DIR)
    git(["config", "user.email", "swings-ai@local"], SKILLS_DIR)
    git(["config", "user.name", "Swings AI"], SKILLS_DIR)
    gi = SKILLS_DIR / ".gitignore"
    have = gi.read_text().splitlines() if gi.exists() else []
    gi.write_text("\n".join(dict.fromkeys(have + GITIGNORE_LINES)) + "\n")
    commit_skills("baseline")

def commit_skills(message):
    git(["add", "-A"], SKILLS_DIR)
    r = git(["commit", "-q", "-m", message], SKILLS_DIR)
    return "nothing to commit" not in (r.stdout + r.stderr)

def skill_history(n=10):
    print(git(["log", f"-{n}", "--oneline"], SKILLS_DIR).stdout)

def rollback(steps=1):
    """Undo the last N self-edits."""
    print(git(["reset", "--hard", f"HEAD~{steps}"], SKILLS_DIR).stdout)

# ---- isolation layers ------------------------------------------------------------
def _works(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=10).returncode == 0
    except Exception:
        return False

def _detect_isolation():
    """Pick the strongest isolation available: no network + unprivileged 'nobody' user.
    Root (Colab) uses unshare directly; GitHub Actions runners use passwordless sudo."""
    drop = ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups", "--"]
    for sudo in ([], ["sudo", "-n", "-E"]):
        base = sudo + ["unshare", "-n"]
        if _works(base + drop + ["true"]):
            return sudo, ["unshare", "-n"] + drop, "network blocked + runs as 'nobody'"
        if _works(base + ["true"]):
            return sudo, ["unshare", "-n"], "network blocked"
    return [], [], "basic (temp copy + limits only)"

SANDBOX_SUDO, SANDBOX_PREFIX, SANDBOX_MODE = _detect_isolation()

def _sandbox_cmd(cmd):
    # sudo resets PATH, so pass it through explicitly (keeps node/javac/python from setup actions)
    keep_path = ["env", f"PATH={os.environ.get('PATH', '')}"] if SANDBOX_SUDO else []
    return SANDBOX_SUDO + keep_path + SANDBOX_PREFIX + list(cmd)
SECRET_HINTS = ("TOKEN", "KEY", "SECRET", "PASSWORD", "CREDENTIAL", "AUTH")
BLOCKED_CALLS = {"os.system", "os.popen", "os.remove", "os.unlink", "os.rmdir", "shutil.rmtree",
                 "subprocess.run", "subprocess.Popen", "subprocess.call", "subprocess.check_output",
                 "eval", "exec", "__import__", "ctypes.CDLL"}
BLOCKED_IMPORTS = {"ctypes", "socket", "paramiko", "pty"}

def _safe_env(home):
    env = {k: v for k, v in os.environ.items() if not any(h in k.upper() for h in SECRET_HINTS)}
    env.update(HOME=str(home), PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(home))
    return env

def _limits(memory_mb):
    def apply():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
        resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 2**20, 100 * 2**20))
        if memory_mb:
            resource.setrlimit(resource.RLIMIT_AS, (memory_mb * 2**20, memory_mb * 2**20))
    return apply

def scan_python(code, filename="<llm>"):
    """Static check of LLM-written Python before it ever runs. Returns a list of problems."""
    try:
        tree = ast.parse(code, filename)
    except SyntaxError as e:
        return [f"syntax error: {e}"]
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            problems += [f"blocked import: {n}" for n in names if n.split(".")[0] in BLOCKED_IMPORTS]
        if isinstance(node, ast.Call):
            f = node.func
            name = (f"{f.value.id}.{f.attr}" if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                    else f.id if isinstance(f, ast.Name) else "")
            if name in BLOCKED_CALLS:
                problems.append(f"blocked call: {name}()")
    return problems

def run_sandboxed(workdir, cmd, timeout=120, memory_mb=None):
    """Run `cmd` in a throw-away copy of `workdir`: no network, no secrets, 'nobody' user,
    CPU/file-size/memory limits and a timeout. Real files are never touched."""
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / "work"
        shutil.copytree(workdir, dst, ignore=shutil.ignore_patterns(".git", "repo", "outputs"))
        os.chmod(tmp, 0o777)
        for root, dirs, files in os.walk(dst):
            os.chmod(root, 0o777)
            for f in files:
                os.chmod(os.path.join(root, f), 0o666)
        try:
            r = subprocess.run(_sandbox_cmd(cmd), cwd=dst, capture_output=True, text=True,
                               timeout=timeout, env=_safe_env(tmp),
                               preexec_fn=_limits(memory_mb))
            return r.returncode == 0, (r.stdout + r.stderr)[-4000:]
        except subprocess.TimeoutExpired:
            return False, f"Timed out after {timeout}s"


# ===== Cell 12: Self-editing code agent =====
AGENT_LOG = SKILLS_DIR / "agent_log.md"

def log(event):
    line = f"- {datetime.datetime.now():%Y-%m-%d %H:%M} — {event}\n"
    with open(AGENT_LOG, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def _skill_context(skill, max_chars=6000):
    md = Path(skill["path"], "SKILL.md").read_text(encoding="utf-8")
    scripts = Path(skill["path"], "scripts")
    existing = "\n".join(p.name for p in scripts.glob("*.py")) if scripts.exists() else "none"
    return f"SKILL.md:\n{md[:max_chars]}\n\nExisting scripts: {existing}"

# ---- language-aware checks for re-engineering ------------------------------------
LANG_GLOBS = {"Python": "**/*.py", "Java": "**/*.java", "JavaScript": "**/*.js",
              "TypeScript": "**/*.ts", "Kotlin": "**/*.kt", "Go": "**/*.go"}

SYNTAX_CHECKER = r'''
import sys, os, ast, json, subprocess, shutil, tempfile, re
# javac errors that only mean "a dependency/other file is missing", not "your code is broken"
SEMANTIC = re.compile(r"cannot find symbol|does not exist|cannot access|is not abstract|"
                      r"incompatible types|cannot be applied|has private access|unreported exception|"
                      r"not found in|already defined|is not public|does not override")
bad = []
for f in sys.argv[1:]:
    ext = os.path.splitext(f)[1].lower()
    try:
        if ext == ".py":
            ast.parse(open(f, encoding="utf-8").read(), f)
        elif ext == ".json":
            json.load(open(f, encoding="utf-8"))
        elif ext in (".js", ".mjs", ".cjs"):
            r = subprocess.run(["node", "--check", f], capture_output=True, text=True)
            if r.returncode: bad.append(f"{f}: {r.stderr.strip()[-600:]}")
        elif ext in (".ts", ".tsx"):
            tool = shutil.which("esbuild") or shutil.which("tsc")
            if tool:
                args = [tool, f, "--log-level=error"] if "esbuild" in tool else [tool, "--noEmit", "--skipLibCheck", f]
                r = subprocess.run(args, capture_output=True, text=True)
                if r.returncode and "error TS2307" not in r.stdout: bad.append(f"{f}: {(r.stdout+r.stderr)[-600:]}")
            else:
                print(f"skip {f}: no TypeScript checker installed")
        elif ext == ".java":
            with tempfile.TemporaryDirectory() as out:
                r = subprocess.run(["javac", "-proc:none", "-nowarn", "-Xmaxerrs", "200", "-d", out, f],
                                   capture_output=True, text=True)
            errs = [l for l in r.stderr.splitlines() if ": error:" in l]
            syntax = [l for l in errs if not SEMANTIC.search(l)]
            if syntax: bad.append(f"{f}:\n" + "\n".join(syntax[:10]))
            elif r.returncode and not errs:      # javac itself failed to run -> fail closed
                bad.append(f"{f}: javac did not run: {r.stderr.strip()[-400:]}")
        else:
            print(f"skip {f}: no checker for {ext}")
    except Exception as e:
        bad.append(f"{f}: {e}")
print("\n".join(bad) if bad else "syntax OK")
sys.exit(1 if bad else 0)
'''
CHECKER_PATH = Path(tempfile.gettempdir()) / "swings_tools" / "syntax_check.py"   # readable by 'nobody'
CHECKER_PATH.parent.mkdir(parents=True, exist_ok=True)
CHECKER_PATH.write_text(SYNTAX_CHECKER)
os.chmod(CHECKER_PATH.parent, 0o755); os.chmod(CHECKER_PATH, 0o644)

def default_check(files):
    """Syntax/compile check that works for Python, Java, JavaScript, TypeScript and JSON."""
    return [sys.executable, str(CHECKER_PATH), *files]

class CodeAgent:
    """Writes, tests and improves skill code by itself. Keeps a change only if its checks pass."""
    def __init__(self, max_attempts=3):
        self.max_attempts = max_attempts

    # --- 1. write a new tool for a skill -------------------------------------------
    def write_tool(self, skill, goal):
        skill_dir = Path(skill["path"])
        prompt = (f"{_skill_context(skill)}\n\nGOAL: {goal}\n\n"
                  "Write a small, self-contained Python tool for this skill in scripts/, "
                  "plus a pytest file in tests/ that checks it WITHOUT network access. "
                  "Use only the standard library and `requests`; do not use subprocess, os.system, "
                  "eval/exec or delete files. Tests must import the tool via "
                  "sys.path.insert(0, 'scripts').\n" + FILE_FORMAT)
        return self._attempt(skill_dir, prompt, goal, test_cmd=[sys.executable, "-m", "pytest", "-q", "-p",
                             "no:cacheprovider", "tests"], label=skill["skill_name"],
                             memory_mb=2048)   # cap memory for LLM-written Python

    # --- 2. rewrite the SKILL.md so the skill explains itself better -----------------
    def improve_doc(self, skill):
        skill_dir = Path(skill["path"])
        new = llm(f"{_skill_context(skill)}\n\nRewrite this SKILL.md. Keep the YAML frontmatter "
                  "keys unchanged. Add sections: 'When to use', 'How to use' (with commands/scripts), "
                  "'Limitations'. Return only the markdown.")
        new = re.sub(r"^```(markdown)?\n|```$", "", new.strip())
        if not new.startswith("---") or "name:" not in new.split("---")[1]:
            log(f"{skill['skill_name']}: doc rewrite rejected (frontmatter broken)")
            return False
        (skill_dir / "SKILL.md").write_text(new, encoding="utf-8")
        commit_skills(f"{skill['skill_name']}: improve SKILL.md")
        log(f"{skill['skill_name']}: SKILL.md improved")
        return True

    # --- 3. re-engineer the cloned project --------------------------------------------
    def reengineer(self, skill, goal, files=None, file_glob=None, max_files=3, check_cmd=None):
        """Edit the upstream code on a 'swings-ai' branch. Kept only if the language-aware check
        (or your own check_cmd, e.g. ["mvn","-q","-o","compile"]) passes. Saved to Drive as a patch."""
        repo = ensure_repo(skill)
        if files:
            paths = [repo / f for f in files]
        else:
            pattern = file_glob or LANG_GLOBS.get(skill.get("language"), "**/*.py")
            paths = [p for p in sorted(repo.glob(pattern))
                     if p.is_file() and p.stat().st_size < 20_000 and "test" not in p.name.lower()][:max_files]
        paths = [p for p in paths if p.exists()]
        if not paths:
            log(f"{skill['skill_name']}: no files to re-engineer")
            return False
        rel = [str(p.relative_to(repo)) for p in paths]
        src = "\n\n".join(f"### FILE: {r}\n```\n{p.read_text(errors='ignore')}\n```" for r, p in zip(rel, paths))
        prompt = (f"GOAL: {goal}\n\nCurrent files:\n{src}\n\n"
                  "Return the full new content of every file you change. Keep the same language.\n"
                  + FILE_FORMAT)
        git(["checkout", "-q", "-B", "swings-ai"], repo)
        ok = self._attempt(repo, prompt, goal, test_cmd=check_cmd or default_check(rel),
                           sandbox_repo=True, label=f"{skill['skill_name']}/repo")
        if ok:
            git(["add", "-A"], repo)
            git(["-c", "user.name=Swings AI", "-c", "user.email=swings-ai@local",
                 "commit", "-q", "-m", f"Swings AI: {goal}"], repo)
            patch_dir = Path(skill["path"], "patches"); patch_dir.mkdir(exist_ok=True)
            n = len(list(patch_dir.glob("*.patch"))) + 1
            patch = git(["format-patch", "-1", "--stdout"], repo).stdout
            (patch_dir / f"{n:03d}-{slug(goal)[:40]}.patch").write_text(patch, encoding="utf-8")
            commit_skills(f"{skill['skill_name']}: patch '{goal}'")
        return ok

    # --- shared generate -> scan -> test -> fix loop ---------------------------------
    def _attempt(self, workdir, prompt, goal, test_cmd, sandbox_repo=False, label=None, memory_mb=None):
        label = label or Path(workdir).name
        feedback = ""
        for i in range(1, self.max_attempts + 1):
            files = parse_files(llm(prompt + feedback))
            files = {r: b for r, b in files.items() if ".." not in Path(r).parts and not Path(r).is_absolute()}
            if not files:
                feedback = "\n\nYour last reply had no FILE blocks. Follow the format exactly."
                continue
            problems = [] if sandbox_repo else [f"{r}: {p}" for r, b in files.items()
                                                if r.endswith(".py") for p in scan_python(b, r)]
            if problems:
                feedback = ("\n\nRejected by the safety scan:\n" + "\n".join(problems) +
                            "\nRewrite without those calls/imports and resend all files.")
                log(f"{label}: attempt {i} blocked by safety scan ({problems[0]})")
                continue
            with tempfile.TemporaryDirectory() as tmp:
                trial = Path(tmp) / "trial"
                skip = (".git", "outputs") if sandbox_repo else (".git", "outputs", "repo")
                shutil.copytree(workdir, trial, ignore=shutil.ignore_patterns(*skip))
                for rel, body in files.items():
                    (trial / rel).parent.mkdir(parents=True, exist_ok=True)
                    (trial / rel).write_text(body, encoding="utf-8")
                ok, out = run_sandboxed(trial, test_cmd, memory_mb=memory_mb)
            if ok:
                for rel, body in files.items():
                    (Path(workdir) / rel).parent.mkdir(parents=True, exist_ok=True)
                    (Path(workdir) / rel).write_text(body, encoding="utf-8")
                if not sandbox_repo:
                    commit_skills(f"{label}: {goal}")
                log(f"{label}: '{goal}' PASSED on attempt {i} ({', '.join(files)})")
                return True
            feedback = f"\n\nAttempt {i} failed. Check output:\n{out}\nFix the code and resend all files."
        log(f"{label}: '{goal}' FAILED after {self.max_attempts} attempts — nothing changed")
        return False

agent = CodeAgent()

# ===== Cell 13: Autopilot + scheduler =====
import schedule, threading

TASKS_FILE = SKILLS_DIR / "tasks.json"   # queue you (or the agent) can add to
REFRESH_DAYS = 7

def add_task(kind, skill_name, goal="", **kw):
    tasks = json.loads(TASKS_FILE.read_text()) if TASKS_FILE.exists() else []
    tasks.append({"kind": kind, "skill": skill_name, "goal": goal, "status": "todo", **kw})
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))

def run_task_queue(limit=3):
    """Process up to `limit` queued tasks: write_tool | improve_doc | reengineer."""
    if not TASKS_FILE.exists():
        return
    tasks, reg, done = json.loads(TASKS_FILE.read_text()), load_registry(), 0
    for t in tasks:
        if t["status"] != "todo" or done >= limit:
            continue
        skill = reg.get(t["skill"])
        if not skill:
            t["status"] = "skipped: unknown skill"; continue
        try:
            if t["kind"] == "write_tool":
                ok = agent.write_tool(skill, t["goal"])
            elif t["kind"] == "improve_doc":
                ok = agent.improve_doc(skill)
            elif t["kind"] == "reengineer":
                ok = agent.reengineer(skill, t["goal"], files=t.get("files"), file_glob=t.get("file_glob"),
                                      check_cmd=t.get("check_cmd"))
            else:
                ok = False
            t["status"] = "done" if ok else "failed"
        except Exception as e:
            t["status"] = f"error: {e}"
        t["finished"] = datetime.datetime.now().isoformat(timespec="minutes")
        done += 1
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))

def autopilot_plan():
    """The agent decides its own work: skills with no tools or thin docs get tasks."""
    queued = {(t["kind"], t["skill"]) for t in (json.loads(TASKS_FILE.read_text()) if TASKS_FILE.exists() else [])}
    for name, s in load_registry().items():
        if not any(Path(s["path"], "scripts").glob("*.py")) and ("write_tool", name) not in queued:
            add_task("write_tool", name, "a helper that turns a short text description into this "
                     "skill's diagram source (e.g. PlantUML/Mermaid) and can render it via Kroki")
        if "## How to use" not in Path(s["path"], "SKILL.md").read_text() and ("improve_doc", name) not in queued:
            add_task("improve_doc", name)

def refresh_skills():
    log("refresh: searching GitHub for new/updated UML projects")
    build_skills(clone=False)        # source is cloned lazily by ensure_repo()
    commit_skills("refresh skills from GitHub")

def autopilot_cycle():
    autopilot_plan()
    run_task_queue(limit=3)

_stop = threading.Event()
def start_scheduler(every_minutes=60, refresh_days=REFRESH_DAYS):
    schedule.clear()
    schedule.every(every_minutes).minutes.do(autopilot_cycle)
    schedule.every(refresh_days).days.do(refresh_skills)
    _stop.clear()
    def loop():
        while not _stop.is_set():
            schedule.run_pending()
            time.sleep(30)
    threading.Thread(target=loop, daemon=True).start()
    log(f"scheduler started: autopilot every {every_minutes} min, refresh every {refresh_days} days")

def stop_scheduler():
    _stop.set(); schedule.clear(); log("scheduler stopped")
