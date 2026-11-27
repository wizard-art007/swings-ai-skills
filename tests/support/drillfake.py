"""Scripted LLM for the fire-drill test: fixes the two planted drill bugs the way a careful engineer would."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fakellm
TESTS = {"drill_open_count": "    assert sc.drill_open_count([{'kind': 'x'}, {'status': 'todo'}]) == 1\n",
         "drill_skill_names": "    assert sc.drill_skill_names([{'name': 'b'}, {'skill_name': 'a'}]) == ['a', 'b']\n"}
def fake(prompt, system="", model=None, retries=3):
    if "ROOT CAUSE" in prompt:
        fn = prompt.split("```python\n", 1)[1].split("\n```", 1)[0]
        name = re.search(r"def (\w+)", fn).group(1)
        fixed = fn.replace('t["status"]', 't.get("status")').replace('s["name"]', 's.get("name", s.get("skill_name", ""))')
        return ("### FUNCTION\n```python\n" + fixed + "\n```\n### TEST\n```python\ndef test_regression():\n"
                + TESTS.get(name, "    assert True\n") + "```\n")
    return fakellm.fake(prompt, system, model, retries)
