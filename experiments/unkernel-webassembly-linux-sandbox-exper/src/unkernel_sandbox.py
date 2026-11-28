"""
Unkernel WebAssembly Linux Sandbox Simulator & Architecture Visualizer.
Simulates a WebAssembly Linux environment loader and utilizes the archify skill
to generate architectural diagrams of the sandbox layout.
"""

import sys
import os

# Ensure vendor is available
VENDOR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor'))
if VENDOR_PATH not in sys.path:
    sys.path.insert(0, VENDOR_PATH)

from tt_a1i_archify.archify_helper import parse_text_lines, text_to_mermaid, text_to_plantuml


class WasmLinuxSandbox:
    """Simulates a WebAssembly Linux sandbox instance."""

    def __init__(self, name: str, memory_pages: int = 256):
        self.name = name
        self.memory_pages = memory_pages
        self.processes = []
        self.env_vars = {}
        self.status = "INITIALIZED"

    def add_process(self, pid: int, command: str):
        self.processes.append({"pid": pid, "command": command, "state": "READY"})

    def set_env(self, key: str, value: str):
        self.env_vars[key] = value

    def boot(self):
        if not self.processes:
            self.status = "FAILED_NO_PROCESSES"
            return False
        self.status = "RUNNING"
        return True

    def get_manifest_description(self) -> str:
        """Generates a text description of the sandbox state for archify."""
        lines = [
            f"Sandbox: {self.name}",
            f"Status: {self.status}",
            f"MemoryPages: {self.memory_pages}",
            f"EnvVarsCount: {len(self.env_vars)}",
        ]
        for p in self.processes:
            lines.append(f"Process PID {p['pid']}: {p['command']} [{p['state']}]")
        return "\n".join(lines)

    def generate_architecture_diagram(self, engine: str = "mermaid") -> str:
        """Uses tt_a1i_archify skill to generate architecture diagrams."""
        desc = self.get_manifest_description()
        if engine.lower() == "plantuml":
            return text_to_plantuml(desc, kind="component")
        return text_to_mermaid(desc, kind="flowchart")


def parse_manifest_file_content(content: str) -> WasmLinuxSandbox:
    """Parses simple config text using parse_text_lines from archify skill."""
    lines = parse_text_lines(content)
    sandbox_name = "default-sandbox"
    pages = 128
    sandbox = None

    for line in lines:
        if line.startswith("NAME:"):
            sandbox_name = line.split(":", 1)[1].strip()
            sandbox = WasmLinuxSandbox(sandbox_name, pages)
        elif line.startswith("MEMORY:") and sandbox:
            try:
                sandbox.memory_pages = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("PROC:") and sandbox:
            parts = line.split(":", 2)
            if len(parts) == 3:
                try:
                    pid = int(parts[1].strip())
                    cmd = parts[2].strip()
                    sandbox.add_process(pid, cmd)
                except ValueError:
                    pass

    if not sandbox:
        sandbox = WasmLinuxSandbox(sandbox_name, pages)
    return sandbox
