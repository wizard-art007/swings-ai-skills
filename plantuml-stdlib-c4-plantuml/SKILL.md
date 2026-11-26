---
name: plantuml-stdlib-c4-plantuml
description: C4-PlantUML combines the benefits of PlantUML and the C4 model for providing a simple way of describing and communicate software architectures
source: https://github.com/plantuml-stdlib/C4-PlantUML
license: MIT
stars: 7466
language: PlantUML
topics: architecture, c4, c4model, diagram, graphviz, plantuml, uml
saved: 2026-11-26
---

# plantuml-stdlib/C4-PlantUML

## Summary
C4-PlantUML combines the benefits of PlantUML and the C4 model for providing a simple way of describing and communicating software architectures.

## When to use
Use this skill when the task involves:
- Designing or documenting software architectures using the C4 model (Context, Containers, Component, Code).
- Creating PlantUML-based architectural diagrams with standardized C4 shapes, containers, systems, and boundaries.
- Generating, rendering, or validating C4 architecture diagrams via scripts or command-line tools.

## How to use
To generate or process C4 architecture diagrams using the repository and its tooling:

1. Ensure the repository/environment is available (clone or reference the `C4-PlantUML` standard library).
2. Utilize existing helper scripts such as `c4_plantuml_generator.py` to automate diagram generation or batch processing:
   ```bash
   python c4_plantuml_generator.py
   ```
3. Include the standard library in your `.puml` files using the appropriate relative or remote include paths:
   ```plantuml
   !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
   ```

## Limitations
- Requires a working PlantUML environment and Graphviz installed to render the diagrams into visual formats (PNG, SVG, etc.).
- Complex system landscapes with numerous interconnections can result in cluttered or difficult-to-read automatically laid-out diagrams, requiring manual adjustment of layout directions (e.g., `Rel_Down`, `Rel_Left`).