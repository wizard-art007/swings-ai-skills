import sys
import os

# Ensure src is in sys.path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from unkernel_sandbox import WasmLinuxSandbox, parse_manifest_file_content


def test_sandbox_lifecycle():
    sandbox = WasmLinuxSandbox("test-node", memory_pages=512)
    assert sandbox.status == "INITIALIZED"
    
    sandbox.add_process(1, "/bin/init")
    sandbox.add_process(42, "/usr/bin/app")
    
    assert sandbox.boot() is True
    assert sandbox.status == "RUNNING"
    assert len(sandbox.processes) == 2


def test_manifest_parsing_and_diagram():
    manifest_data = """
    # Unkernel configuration manifest
    NAME: edge-wasm-runtime
    MEMORY: 1024
    PROC: 1 : /sbin/loader
    PROC: 100 : /app/worker.wasm
    """
    
    sandbox = parse_manifest_file_content(manifest_data)
    assert sandbox.name == "edge-wasm-runtime"
    assert sandbox.memory_pages == 1024
    assert len(sandbox.processes) == 2
    
    # Test skill tool integration (archify mermaid generator)
    mermaid_out = sandbox.generate_architecture_diagram(engine="mermaid")
    assert isinstance(mermaid_out, str)
    assert len(mermaid_out) > 0

    # Test skill tool integration (archify plantuml generator)
    plantuml_out = sandbox.generate_architecture_diagram(engine="plantuml")
    assert isinstance(plantuml_out, str)
    assert len(plantuml_out) > 0
