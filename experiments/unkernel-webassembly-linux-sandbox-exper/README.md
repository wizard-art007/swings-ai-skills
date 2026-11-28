# Unkernel WebAssembly Linux Sandbox Experiment

## Idea
Inspired by modern browser-based virtualization and WebAssembly Linux experiments (`unkernel.dev`), this project provides a lightweight, offline Python simulator and parser for WebAssembly Linux environment payloads, process descriptors, and execution states. 

## How It Works
- **Sandbox Loader**: Parses simulated WebAssembly binary module manifests, memory pages, and environment variable configurations.
- **Virtual Process Lifecycle**: Tracks virtual PID states, system call trace buffers, and resource limits.
- **Skill Integration**: Integrates the vendor `tt_a1i_archify` skill tool to automatically translate runtime container/sandbox architecture and process layout descriptors into Mermaid and PlantUML diagrams for developer visualization.

## Skill Tool Used
- `vendor.tt_a1i_archify.archify_helper`: Utilized to convert sandbox layout descriptions and state configurations into Mermaid/PlantUML architecture diagrams, helping developers audit sandbox components visually.

## How to Run
```bash
# Run tests offline
pytest tests/
```

## What Was Learned
- Lightweight offline parsers can effectively simulate complex container/WebAssembly isolation primitives without heavy virtualization runtimes.
- Combining sandbox instrumentation inspection directly with diagram generation tools (`archify`) provides instant visual feedback for developer security audits and architecture review.
