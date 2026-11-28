# Unkernel WebAssembly Linux Sandbox Experiment

A small offline Python experiment simulating a WebAssembly Linux environment loader/parser under 300 lines. Inspired by browser-based virtualization trends (Unkernel), this tool parses pseudo-WebAssembly module manifests, validates resource limits, and utilizes the `tt_a1i_archify` skill tool to generate architectural Mermaid diagrams showing sandbox lifecycle and execution flow.

## How It Works
1. **Manifest Parsing**: Reads a simulated Wasm/Linux environment configuration manifest (using `parse_text_lines` from `tt_a1i_archify`).
2. **Sandbox Simulation**: Instantiates a lightweight virtual environment (`WasmLinuxSandbox`) enforcing memory and CPU limits, mounting virtual filesystems.
3. **Diagram Generation**: Converts the sandbox component topology and execution flow into a Mermaid architecture diagram using `text_to_mermaid`.

## Skill Tool Integration
- Uses `vendor.tt_a1i_archify.archify_helper` for parsing configuration lines and generating Mermaid architecture diagrams.

## How to Run
```bash
python3 src/unkernel_sandbox.py
pytest tests/
```

## What Was Learned
Integrating architectural diagram generation directly into the initialization of a simulated container/sandbox parser provides immediate visual feedback for embedded systems and offline developer workflows.
