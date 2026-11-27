import os, sys, json
ENGINE = os.path.join(os.environ["SWINGS_SKILLS_DIR"], "engine")
sys.path.insert(0, ENGINE); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swings_core, fakellm
swings_core._llm_unbudgeted = fakellm.fake
__file__ = os.path.join(ENGINE, "run_autopilot.py")
code = open(__file__).read().replace("import swings_core\n", "import swings_core  # already loaded\n", 1)
try:
    exec(compile(code, __file__, "exec"))
finally:
    print("FAKE_LLM_CALLS", fakellm.CALLS["n"])
