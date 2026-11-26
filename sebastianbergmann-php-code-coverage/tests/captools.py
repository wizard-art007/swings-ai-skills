
import importlib.util, pathlib, sys, pytest
SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
def load_tool(skill, module):
    """Acceptance-test loader: the need's tool must live in this skill's scripts/ folder."""
    p = SCRIPTS / f"{module}.py"
    if not p.exists():
        pytest.fail(f"missing tool scripts/{module}.py")
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(f"need_{module}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
