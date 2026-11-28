import sys
import os

# Ensure src/ is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unkernel_sandbox import WasmLinuxSandbox, parse_manifest_file_content, generate_sandbox_architecture_diagram


def test_sandbox_lifecycle():
    sandbox = WasmLinuxSandbox(name="test-box", memory_mb=32)
    assert sandbox.state == "CREATED"
    
    boot_msg = sandbox.boot()
    assert "booted successfully" in boot_msg
    assert sandbox.state == "RUNNING"
    
    res = sandbox.execute_wasm("wasm_bytecode_sample")
    assert res["status"] == "success"
    assert res["executed_bytes"] > 0


def test_manifest_parser():
    content = """
    # Comment line
    NAME=custom-node
    MEMORY=256
    MOUNT=/var/log
    """
    config = parse_manifest_file_content(content)
    assert config["name"] == "custom-node"
    assert config["memory"] == 256
    assert "/var/log" in config["volumes"]


def test_archify_mermaid_generation():
    diagram = generate_sandbox_architecture_diagram()
    assert isinstance(diagram, str)
    assert len(diagram) > 0
    assert "sequenceDiagram" in diagram or "graph" in diagram or "diagram" in diagram.lower()
