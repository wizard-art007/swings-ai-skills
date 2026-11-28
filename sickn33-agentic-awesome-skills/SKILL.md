---
name: sickn33-agentic-awesome-skills
description: 3,000+ reusable AI agent skills for Claude Code, Codex, Cursor and Gemini CLI. AAS Core adds local catalog discovery, agent-owned selection and plan preview. CLI, MCP and plugins.
source: https://github.com/sickn33/agentic-awesome-skills
license: MIT
stars: 50452
language: Python
topics: agent-skills, agentic-skills, ai-agent-skills, ai-agents, ai-coding, ai-workflows, antigravity, antigravity-skills, claude-code, claude-code-skills, codex-cli, codex-skills, cursor, cursor-skills, developer-tools, gemini-cli, gemini-skills, kiro, mcp, skill-library
saved: 2026-11-28
---

# sickn33/agentic-awesome-skills

## Summary
Agentic Awesome Skills (AAS) provides a curated library of 3,151+ `SKILL.md` playbooks designed to augment AI coding agents (Claude Code, Codex, Cursor, Gemini CLI). AAS Core facilitates local catalog discovery, allowing agents to select, record, and preview skill-based plans before execution.

## When to use
Use this skill library when:
- You need to standardize workflows for agentic coding tasks.
- The agent requires a repeatable, documented "skill" to perform complex operations (e.g., refactoring, QA, or infrastructure setup).
- You are working with Claude Code, Cursor, or similar MCP-compatible tools.
- You need to integrate specific domain-knowledge playbooks into your development agent’s context.

## How to use
The library is accessed via AAS Core. Integration requires pointing your agent to the local catalog after cloning:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sickn33/agentic-awesome-skills.git ./skills
   ```

2. **Integration with `aas_planner.py`:**
   Use the existing script to ingest the library and generate a plan based on the task objective:
   ```bash
   python3 aas_planner.py --catalog ./skills --task "Refactor test suite for flake detection" --output plan.md
   ```

3. **Agent Setup:**
   - For **Claude Code/Codex**: Ensure the local `/skills` directory is indexed by your agent’s configuration file to allow for skill discovery via natural language queries.
   - For **MCP**: Add the AAS directory as an MCP resource provider to expose the skills via the `mcp-server`.

## Limitations
- **No npm Publishing**: Due to maintainer account locks, all updates must be pulled directly from the GitHub repository; npm installs are currently unsupported.
- **No Ranking**: AAS Core does not rank or recommend skills; it provides a neutral discovery mechanism. The quality of skill selection remains dependent on the agent's reasoning capability.
- **License Compliance**: While the AAS core tooling is MIT, individual skills imported into the library retain their own licenses. Always inspect the `SKILL.md` header for attribution requirements before use in commercial projects.