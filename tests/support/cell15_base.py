# Reconstruction of the notebook's Cell 15 functions (read from Colab on 27 Nov), for offline tests.
import base64 as _b64
ENGINE_CELLS = ["1", "2", "3", "4", "5", "10", "11", "12", "13", "17", "18", "19", "26", "27", "28", "29", "30", "31",
                "32", "33", "34", "35", "36", "37"]

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

def export_engine():
    (SKILLS_DIR / "engine").mkdir(exist_ok=True)
    (SKILLS_DIR / "engine" / "swings_core.py").write_text(build_engine_source(), encoding="utf-8")
    compile((SKILLS_DIR / "engine" / "swings_core.py").read_text(), "swings_core.py", "exec")
    commit_skills("export engine + workflow")
    print("Engine exported to", SKILLS_DIR / "engine")

def _auth_args():
    return []

def sync_skills():
    for stuck in ("rebase", "merge"):
        git([stuck, "--abort"], SKILLS_DIR)
    commit_skills("colab changes")
    git(_auth_args() + ["fetch", "-q", "origin", "main"], SKILLS_DIR)
    r1 = git(["merge", "-q", "-X", "theirs", "-m", "sync: merge autopilot work", "origin/main"], SKILLS_DIR)
    if r1.returncode != 0:
        git(["checkout", "--theirs", "."], SKILLS_DIR); git(["add", "-A"], SKILLS_DIR)
        git(["commit", "-q", "-m", "sync: merge autopilot work (auto-resolved)"], SKILLS_DIR)
    r2 = git(_auth_args() + ["push", "origin", "HEAD:main"], SKILLS_DIR)
    print("merge:", (r1.stdout + r1.stderr).strip()[-300:] or "ok")
    print("push :", (r2.stdout + r2.stderr).strip()[-300:] or "ok")
