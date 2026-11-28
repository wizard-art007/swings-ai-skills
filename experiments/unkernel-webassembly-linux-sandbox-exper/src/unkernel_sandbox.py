"""
Unkernel WebAssembly Linux Sandbox Experiment
Simulates a WebAssembly Linux environment loader/parser and utilizes tt_a1i_archify for architecture diagram generation.
"""

from vendor.tt_a1i_archify.archify_helper import parse_text_lines, text_to_mermaid


class WasmLinuxSandbox:
    def __init__(self, name: str, memory_mb: int = 64, cpu_shares: int = 1024):
        self.name = name
        self.memory_mb = memory_mb
        self.cpu_shares = cpu_shares
        self.mounted_volumes = []
        self.state = "CREATED"

    def mount(self, path: str):
        self.mounted_volumes.append(path)

    def boot(self) -> str:
        if self.state == "RUNNING":
            return f"Sandbox {self.name} already running."
        self.state = "RUNNING"
        return f"Sandbox {self.name} booted successfully with {self.memory_mb}MB RAM."

    def execute_wasm(self, bytecode_stub: str) -> dict:
        if self.state != "RUNNING":
            raise RuntimeError("Sandbox is not running.")
        return {
            "status": "success",
            "executed_bytes": len(bytecode_stub),
            "output": f"Simulated execution of {bytecode_stub[:16]}..."
        }


def parse_manifest_file_content(content: str) -> dict:
    """Parses manifest file content using tt_a1i_archify helper lines."""
    lines = parse_text_lines(content)
    config = {"name": "default-wasm-env", "memory": 64, "volumes": []}
    
    for line in lines:
        if line.startswith("NAME="):
            config["name"] = line.split("=", 1)[1].strip()
        elif line.startswith("MEMORY="):
            config["memory"] = int(line.split("=", 1)[1].strip())
        elif line.startswith("MOUNT="):
            config["volumes"].append(line.split("=", 1)[1].strip())
            
    return config


def generate_sandbox_architecture_diagram() -> str:
    """Uses tt_a1i_archify to generate a Mermaid architecture diagram for the sandbox."""
    description = (
        "Unkernel Sandbox Architecture\n"
        "1. Host Environment loads Manifest\n"
        "2. WasmLinuxSandbox initializes memory and mounts\n"
        "3. Virtual CPU executes bytecode securely"
    )
    return text_to_mermaid(description, kind="sequence")


if __name__ == "__main__":
    sample_manifest = """
    # Unkernel Linux Environment Manifest
    NAME=edge-worker-01
    MEMORY=128
    MOUNT=/app/data
    """
    cfg = parse_manifest_file_content(sample_manifest)
    sandbox = WasmLinuxSandbox(name=cfg["name"], memory_mb=cfg["memory"])
    for vol in cfg["volumes"]:
        sandbox.mount(vol)
        
    print(sandbox.boot())
    print(sandbox.execute_wasm(b"\x00\x61\x73\x6d\x01\x00\x00\x00"))
    print("Generated Architecture Diagram:\n", generate_sandbox_architecture_diagram())
