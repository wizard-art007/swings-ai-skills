---
name: ahmadhassan-bted-openheart
description: Succinct Compositional Program Graph (SCPG) static analysis engine & 14-diagram UML generator in Rust.
source: https://github.com/AhmadHassan-BTed/OpenHeart
license: MIT
stars: 5918
language: Rust
topics: code-property-graph, compiler-theory, program-analysis, robdd, rust, static-analysis, succinct-data-structures, tree-sitter, uml-generator
saved: 2026-11-26
---

# AhmadHassan-BTed/OpenHeart

OpenHeart is an experimental static program analysis engine written in Rust. It ingests source code via tree-sitter, processes it through a ten-phase static analysis pipeline (producing symbol tables, control-flow graphs, SSA representations, call graphs, and path summaries), and exports UML diagrams and graph representations.

## When to use

- **Java Static Analysis:** Analyzing Java source code to extract symbol tables, Control Flow Graphs (CFGs), Static Single Assignment (SSA) form, or call graphs.
- **UML & Architecture Diagram Generation:** Generating structural and behavioral diagrams (e.g., class, sequence, call graph) from Java projects.
- **Code Property Graph (CPG / SCPG) Research:** Researching succinct graph representations, tree-sitter pipeline architectures, and Binary Decision Diagram (ROBDD) program representations.
- **Compiler IR & Program Representation Inspection:** Inspecting mid-level intermediate representations derived directly from tree-sitter concrete syntax trees.

## How to use

### 1. Build from Source

Ensure you have a recent Rust toolchain installed (edition 2021+):

```bash
git clone https://github.com/AhmadHassan-BTed/OpenHeart.git
cd OpenHeart
cargo build --release
```

### 2. Run Analysis CLI

Analyze a Java file or directory:

```bash
# Analyze a single Java file
cargo run --release -- analyze path/to/Source.java

# Analyze a directory of Java sources
cargo run --release -- analyze path/to/java/project/src/
```

### 3. Generate Diagrams

Generate UML and graph representations (DOT, SVG, or JSON):

```bash
# Export all generated diagram formats to an output directory
cargo run --release -- export-diagrams --input path/to/Source.java --output ./diagrams/

# Generate specific graph formats (e.g., CFG, Call Graph)
cargo run --release -- cfg --input path/to/Source.java --format dot -o cfg.dot
dot -Tsvg cfg.dot -o cfg.svg
```

### 4. Running the Web Diagram Studio

OpenHeart includes a browser-based diagram inspection studio:

```bash
cargo run --release -- serve --port 8080 --data ./diagrams/
# Navigate to http://localhost:8080 in a browser
```

### 5. Running Tests and Validations

```bash
cargo test
cargo clippy
```

## Limitations

- **Experimental Research Status:** OpenHeart is an active research prototype. Several pipeline passes are incomplete and may produce approximate results.
- **Java Only:** Although tree-sitter parsers for other languages (such as JavaScript) are linked in the workspace, complete pipeline adapters and lowerings exist **only for Java** (Tier 1 experimental). Languages like Kotlin, C++, or Go are not supported.
- **Template Diagrams:** Several of the 14 UML views are currently template-based and do not dynamically reflect the semantics of the analyzed code.
- **Withdrawn Claims & Missing Features:** Per the project's `docs/status.md`:
  - Does not implement Andersen's points-to analysis or full IFDS framework.
  - Does not include Rudell BDD sifting or zero-copy memory mapping.
  - Previous claims of multi-language parity (F1 = 1.0) and 128× memory compression are not valid. Always verify generated outputs before using them in downstream verification pipelines.