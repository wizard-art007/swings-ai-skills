---
name: juliusbrussee-caveman
description: why use many token when few token do trick. Skill + local proxy for coding agents: shorter answers, smaller tool output, every original recoverable.
source: https://github.com/JuliusBrussee/caveman
license: Apache-2.0
stars: 123057
language: Go
topics: ai, anthropic, caveman, claude, claude-code, llm, meme, prompt-engineering, skill, tokens
saved: 2026-11-26
---

# JuliusBrussee/caveman

Use this skill when the task involves: ai, anthropic, caveman, claude, claude-code, llm, meme, prompt-engineering, skill, tokens.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): see source
- Original README: `README_source.md`

## Summary from README
Caveman Code reduces token usage for AI coding agents (such as Claude Code and Codex) by making them say less and read less while keeping code exact. It achieves 21% lower cost per solved task on Terminal-Bench 4, 33.2% fewer input tokens across whole sessions, and 1.4x to 2.4x cheaper outputs through caveman-style formatting and local proxy management.

## When to use
- You want to reduce token consumption and lower API costs when running LLM coding agents.
- You need concise AI responses and compressed tool outputs without losing fidelity or recoverability.
- You are working with token-heavy environments like Claude Code or Terminal-Bench.

## How to use
- Run token budget estimations using the provided helper script:
  ```bash
  python llm_token_budget_estimator.py
  ```
- Integrate the Caveman local proxy with your coding agents to compress tool outputs and agent responses automatically.

## Limitations
- Compressed "caveman-style" output may occasionally lack conversational nuance or verbosity desired for high-level explanatory tasks.
- Requires local proxy setup alongside your coding agent workflow.