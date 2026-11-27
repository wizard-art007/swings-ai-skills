"""Scripted stand-in for Gemini used only by the end-to-end verification."""
import json, os, re
MODE_FILE = os.environ["VERIFY_MODE_FILE"]
def mode():
    return json.load(open(MODE_FILE))
GOOD = ("### FILE: scripts/{m}.py\n```python\ndef run(x):\n    \"\"\"Verified helper.\"\"\"\n    return x\n```\n"
        "### FILE: tests/test_{m}.py\n```python\nimport sys\nsys.path.insert(0, 'scripts')\nfrom {m} import run\n"
        "def test_run():\n    assert run({v}) == 1\n```\n")
CALLS = {"n": 0}
def fake(prompt, system="", model=None, retries=3):
    CALLS["n"] += 1
    m = mode()
    if m.get("outage"):
        raise Exception("503 UNAVAILABLE: The model is overloaded")
    if "ROOT CAUSE" in prompt:                                  # self-heal: fix the function it was shown
        fn = prompt.split("```python\n", 1)[1].split("\n```", 1)[0]
        fixed = fn.replace('t["status"]', 't.get("status", "todo")')
        return ("### FUNCTION\n```python\n" + fixed + "\n```\n### TEST\n```python\ndef test_regression():\n"
                "    sc.TASKS_FILE.write_text('[{\"kind\": \"write_tool\", \"skill\": \"x\", \"goal\": \"g\"}]')\n"
                "    sc.autopilot_plan()\n```\n")
    if "In ONE line" in prompt:
        return "Assert on the helper's real return value before writing the tool."
    if "self-analysis" in prompt:
        cap = re.search(r"(ai-agents-[a-z0-9-]+) \[ai_agents\] missing", prompt)
        return json.dumps({"gaps": [
            {"title": "Token budget capability missing", "type": "internal", "capability": cap.group(1) if cap else None,
             "evidence": ["capability check failed"], "blocking": 3, "relevance": 3, "effort": 1, "action": "build it"},
            {"title": "Agents need clearer stop rules", "type": "internal", "capability": None,
             "evidence": ["agent_failures: none recent"], "blocking": 1, "relevance": 2, "effort": 1, "action": "tighten prompts"}],
            "proposals": ["Consider a data-engineering area"]})
    if "Rewrite this SKILL.md" in prompt:
        return "---\nname: verified\ndescription: d\n---\n## When to use\nx\n## How to use\ny\n## Limitations\nz\n"
    if "YOU ARE: news_scout" in prompt:                         # an agent that needs 12 steps (limit 10)
        n = prompt.count("CALL save_note")
        done = json.load(open(MODE_FILE + ".notes")) if os.path.exists(MODE_FILE + ".notes") else 0
        if done >= 12:
            return '{"final": "scouted after resuming", "success": true}'
        json.dump(done + 1, open(MODE_FILE + ".notes", "w"))
        return json.dumps({"tool": "save_note", "args": {"text": f"verification note {done}"}})
    if "YOU ARE:" in prompt:
        return '{"final": "nothing to do in verification", "success": true}'
    if "SKILL TOOLS YOU MUST BUILD ON" in prompt:              # Phase 5: an experiment built on a vendored tool
        pkg, mod = re.search(r"`from vendor\.(\w+)\.(\w+) import", prompt).groups()
        name = "vexp_" + str(abs(hash(prompt.split("IDEA:")[-1][:80])) % 10**6)
        return (f"### FILE: src/{name}.py\n```python\nfrom vendor.{pkg} import {mod} as _tool\n\n"
                "def run(x):\n    return x\n\ndef tool():\n    return _tool.__name__\n```\n"
                f"### FILE: tests/test_{name}.py\n```python\nimport sys\nsys.path.insert(0, 'src')\nfrom {name} import run, tool\n"
                f"def test_run():\n    assert run(1) == 1 and tool().endswith('{mod}')\n```\n")
    if "Reply ONLY with files" in prompt or "### FILE:" in prompt:
        name = "vtool_" + str(abs(hash(prompt.split("GOAL:")[-1][:80])) % 10**6)
        flaky = "flaky" in prompt and "Attempt 1 failed" not in prompt
        return GOOD.format(m=name, v=2 if flaky else 1)
    return "ok"
