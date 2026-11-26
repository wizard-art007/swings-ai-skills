---
name: affaan-m-ecc
description: The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond.
source: https://github.com/affaan-m/ECC
license: MIT
stars: 311077
language: JavaScript
topics: ai-agents, anthropic, claude, claude-code, developer-tools, llm, mcp, productivity
saved: 2026-11-26
---

# Everything Claude Code (ECC)

ECC (Everything Claude Code) is an agent harness performance optimization system designed to enhance developer productivity, memory management, security, and skill execution across LLM-powered development tools like Claude Code, Codex, OpenCode, Cursor, and related platforms.

## When to use

Use this skill when:
- Building, configuring, or optimizing AI agent workflows and harnesses for Claude Code, OpenCode, Codex, or Cursor.
- Enhancing agent autonomy with structured skills, instinct systems, persistent memory, and security sandboxing.
- Setting up Model Context Protocol (MCP) servers, tool integration, or developer security shields (`ecc-agentshield`).
- Implementing research-first workflows, automated prompt optimization, and agent harness benchmarking.

## How to use

### Installation & Setup

Install official ECC components from verified channels:

```bash
# Install universal ECC package via npm
npm install -g ecc-universal

# Install security shield package
npm install -g ecc-agentshield
```

In Claude Code, add the official plugin:
```bash
/plugin add ecc@ecc
```

### Script Execution

Use the included diagram generator to visualize architecture and workflow flows:

```bash
# Run the diagram script
python3 ecc_diagram.py
```

### Primary Workflows

1. **Agent Harness Optimization:** Configure context windows, memory persistent layers, and prompt instincts within your target agent configuration.
2. **Security & Sandboxing:** Deploy `ecc-agentshield` to inspect agent tool calls and enforce permission boundaries before code execution.
3. **MCP Integration:** Configure custom Model Context Protocol servers to expose repository context and external tooling directly to Claude Code.

## Limitations

- **Official Channel Verification:** Must only be installed via verified npm packages (`ecc-universal`, `ecc-agentshield`) or official plugin slug `ecc@ecc` to avoid malicious forks.
- **Harness Differences:** Features such as deep memory hooks and custom instinct triggers may behave differently across different platforms (e.g., Claude Code vs. Cursor vs. OpenCode).
- **Pro Features:** While core OSS features are MIT-licensed, certain private repository enterprise management features require ECC Pro.