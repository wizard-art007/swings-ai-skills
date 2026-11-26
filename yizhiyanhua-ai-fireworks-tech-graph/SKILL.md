---
name: yizhiyanhua-ai-fireworks-tech-graph
description: Generate production-quality SVG+PNG technical diagrams from natural language. 7 styles, UML support, and AI/Agent workflow patterns.
source: https://github.com/yizhiyanhua-ai/fireworks-tech-graph
license: MIT
stars: 12062
language: Python
topics: agent-workflows, ai, claude-code, developer-tools, diagrams, svg
saved: 2026-11-26
---

# fireworks-tech-graph

Generate geometry-safe SVG, PNG, and animated diagrams from structured specifications or natural language. Supports architecture graphs, AI agent workflows, and standard UML diagrams in both English and Chinese.

## When to use

Use this skill when you need to:
- Generate production-grade architecture, system, or dataflow diagrams without manual layout editing.
- Visualize AI/Agent patterns (e.g., multi-agent collaboration, tool invocation loops, RAG pipelines, memory architectures).
- Render standard UML diagrams (sequence diagrams, state machines, class relationships).
- Export vector (SVG) or raster (PNG) assets with precise text fitting and truncation safety.
- Generate bilingual technical diagrams (English/Chinese).

## How to use

### 1. Using the Helper Script

Use `diagram_helper.py` to quickly generate diagrams from text descriptions or config files:

```bash
# Generate a diagram from a prompt
python3 diagram_helper.py --prompt "User sends request to API Gateway, which routes to Auth Service and Worker Queue" --style modern --output system_arch.svg

# Render from a JSON/YAML specification
python3 diagram_helper.py --spec architecture.json --output diagram.png --format png

# Enforce strict text limits (rejects visible truncations)
python3 diagram_helper.py --spec workflow.json --text-policy strict --output workflow.svg
```

### 2. Using Core Python Package Directly

If running scripts within `repo/`:

```bash
# Generate SVG directly via module CLI
python3 -m fireworks_tech_graph.cli \
  --input diagram_spec.json \
  --output output/graph.svg \
  --style tech-dark \
  --theme auto
```

### 3. Programmatic Usage

```python
from fireworks_tech_graph import DiagramGenerator

generator = DiagramGenerator(
    style="modern",            # Options: modern, tech-dark, hand-drawn, minimal, etc.
    text_policy="strict",      # Reject output if text bounds are violated
    language="en"              # "en" or "zh"
)

spec = {
    "type": "agent_workflow",
    "nodes": [
        {"id": "planner", "label": "Planner Agent"},
        {"id": "executor", "label": "Code Executor"},
        {"id": "verifier", "label": "Result Verifier"}
    ],
    "edges": [
        {"from": "planner", "to": "executor", "label": "Task"},
        {"from": "executor", "to": "verifier", "label": "Output"},
        {"from": "verifier", "to": "planner", "label": "Retry", "condition": "fail"}
    ]
}

svg_content = generator.render(spec)
with open("agent_workflow.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
```

## Limitations

- **Text Length Bounds**: Enabling `"text_policy": "strict"` will fail fast if node text cannot fit within standard geometric bounds. Long labels must be manually edited or shortened.
- **Raster Export Dependencies**: Generating PNGs or animated GIFs requires underlying rendering utilities (e.g., `cairosvg`, headless Chromium, or `imageio`).
- **Complex Overlaps**: Extremely dense graphs (>50+ interconnected nodes) may experience edge crossing or sub-optimal auto-routing without manual layout hints.
- **Offline Interactivity**: Embedded scripts in offline interactive SVGs depend on modern browser SVG rendering capabilities.