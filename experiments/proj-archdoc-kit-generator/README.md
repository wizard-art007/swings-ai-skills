# ArchDoc Kit Generator

Generate an architectural documentation kit combining a C4 diagram and a Mermaid system flow from a unified text description.

Built by Swings AI from its own skill tools, one milestone per session.

## Milestones

1. Parse and generate dual diagrams: Create a module in app.kit that takes a description and returns both a C4 PlantUML snippet and a Mermaid flowchart snippet.
2. Add documentation index builder: Extend the kit builder to compile the generated diagrams into a single structured markdown documentation file.

## Skill tools used (copied into src/vendor/, with their licences)

- agents365-ai-drawio-skill/bpmn_generator.py (sha256 54a58aeb42e2bdd1)
- agents365-ai-drawio-skill/diagram_helper.py (sha256 29c4ff502e9c4e7f)
- plantuml-stdlib-c4-plantuml/c4_generator.py (sha256 f980d90801b26253)
- plantuml-stdlib-c4-plantuml/c4_plantuml_generator.py (sha256 86e56c8a10c024da)
