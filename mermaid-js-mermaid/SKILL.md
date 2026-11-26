---
name: mermaid-js-mermaid
description: Generation of diagrams like flowcharts or sequence diagrams from text in a similar manner as markdown
source: https://github.com/mermaid-js/mermaid
license: MIT
stars: 91264
language: TypeScript
topics: diagrams, diagrams-as-code, documentation, flowchart, javascript, mindmap, typescript, uml-diagrams
saved: 2026-11-26
---

# mermaid-js/mermaid

## About
Mermaid is a JavaScript-based diagramming and charting tool that uses Markdown-inspired text definitions and a renderer to create and modify complex diagrams, such as flowcharts, sequence diagrams, mindmaps, and UML diagrams.

## When to use
Use this skill when the task involves:
- Creating, generating, or modifying diagrams as code (flowcharts, sequence diagrams, mindmaps, UML, etc.).
- Writing or parsing Markdown-like text definitions for documentation visuals.
- Automating diagram rendering using JavaScript, TypeScript, or helper scripts.

## How to use
This repository provides helper scripts to interact with and generate diagrams.

- **Helper script**: `mermaid_helper.py`
  - Run or inspect the helper script for common automation tasks related to Mermaid diagram generation and parsing.
- **Node/TypeScript API**: 
  - Import `mermaid` in your project to render diagrams programmatically:
    ```typescript
    import mermaid from 'mermaid';
    mermaid.initialize({ startOnLoad: true });
    ```

## Limitations
- Complex layouts can occasionally result in overlapping text or edge crossings depending on the diagram type and renderer constraints.
- Advanced styling and custom themes require familiarity with Mermaid's configuration structure.
- Requires an appropriate environment (browser or Node.js with a DOM/canvas polyfill) for full SVG rendering capabilities.