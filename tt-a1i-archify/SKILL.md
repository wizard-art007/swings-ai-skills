---
name: tt-a1i-archify
description: Turn any idea, plan, or codebase into an interactive diagram or one-page answer: 10 diagram types, Architecture Diagnosis, Story video and PR walkthroughs. An Agent Skill for Claude Code, Codex, Curso
source: https://github.com/tt-a1i/archify
license: Apache-2.0
stars: 100359
language: JavaScript
topics: agent-skills, ai-agents, architecture-diagram, claude-code, claude-skills, code-analysis, codex, coding-agents, deepseek-harness, developer-tools, diagrams, diagrams-as-code, dsh-plugin, flowchart, llm, mermaid, opencode, software-architecture, system-design, visualization
saved: 2026-11-26
---

# tt-a1i/archify

Turn any idea, plan, or codebase into an interactive visual, one-page answer, architecture diagnosis, or video walkthrough.

## When to use
- Mapping an entire codebase or repository to understand its structure.
- Generating interactive architecture diagrams or flowcharts from a plan, idea, or text description.
- Conducting an Architecture Diagnosis on a project.
- Creating story or Pull Request (PR/MR) walkthroughs and exporting them as 1080p videos.
- Working within AI agent environments like Claude Code, Cursor, Codex, or OpenCode when visualization is required.

## How to use
Archify integrates with your AI coding agent. Ensure the repository/skill is installed, then invoke it via natural language descriptions or through available helper scripts.

1. **Via AI Agent Prompting:**
   Describe your idea, plan, or point the agent to your codebase and ask it to generate an Archify interactive visual or diagram.
   
2. **Using the Helper Script:**
   If working directly with the repository scripts:
   ```bash
   python archify_helper.py --target <path-to-codebase-or-idea> --type <diagram-type>
   ```

## Limitations
- Relies on third-party rendering or local execution contexts; complex codebases may require manual scoping for optimal diagram clarity.
- Online services, advanced video rendering features, and paid tiers depend on external providers (`archify.si`).
- Generated diagrams depend on LLM analysis quality of the underlying source code or input prompt.