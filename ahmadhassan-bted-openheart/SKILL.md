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

Use this skill when the task involves: code-property-graph, compiler-theory, program-analysis, robdd, rust, static-analysis, succinct-data-structures, tree-sitter, uml-generator.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): see source
- Original README: `README_source.md`

## Summary from README
# OpenHeart ### Succinct Compositional Program Graph (SCPG) Engine & UML Diagram Studio [](Cargo.toml) [](LICENSE) [](https://ahmadhassan-bted.github.io/OpenHeart/) [](https://github.com/AhmadHassan-BTed/OpenHeart/actions/workflows/ci.yml) [](docs/status.md) [-blueviolet.svg?style=flat-square)](https://github.com/AhmadHassan-BTed) An experimental static program-analysis engine for Java: a ten-phase Rust pipeline from tree-sitter ingestion to symbol tables, control-flow and SSA form, call graphs, path summaries and UML diagrams, with a browser-based diagram studio. --- ## Project Status OpenHeart is **experimental research software**. The pipeline runs end to end on Java sources, but several analyses are partial, and several diagram views are still templates whose content does not depend on the analysed program. Before relying on any output, read **[Implementation Status, Support Matrix & Claims Ledger](docs/status.md)**. That page is the source of truth for what the code does, and it records every earlier headline claim that has been withdrawn (including "128× memory compression", "F1 = 1.0000 across six languages", "zero-copy memory mapping", IFDS, Andersen points-to and Rudell sifting). | Area | State | |---|---| | Languages | **Java** only (Tier 1, experimental). Only the Java and JavaScript tree-sitter grammars are linked, and only Java has adapters for every phase. No other language — Kotlin included — is supported; see the [language support [...]
