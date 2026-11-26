---
name: leonxlnx-taste-skill
description: Agent skills that give coding agents taste: art direction, reference images and a browser check instead of generic AI pages
source: https://github.com/Leonxlnx/taste-skill
license: MIT
stars: 121844
language: JavaScript
topics: agent-skills, ai-agents, anti-slop, claude-code, codex, cursor, design-system, frontend, landing-page, ui-design, web-design
saved: 2026-11-26
---

# Leonxlnx/taste-skill

## Summary
**Taste Skill** (`tasteskill 2.5.1`) is an Agent Skill designed to elevate coding agents so they build professional, high-end company websites at the `figma.com` and `x.ai` level instead of assembling generic, cliché AI landing pages. Every build enforces strict design principles: plain copy, a cohesive design system, one section per screen, aligned structural edges, real photography, authentic brand icons, real product UI, tasteful hero entrances, quiet micro-interactions, and appropriate shader/scroll effects restricted to tech and gaming domains. All outputs are verified through a real browser checker and finish gate.

## When to use
Use this skill when the task involves:
- Building or refactoring frontend applications, landing pages, or web interfaces.
- Establishing or applying a strict UI/UX design system and art direction.
- Preventing generic "AI slop" aesthetics and injecting high-end design taste (`figma.com` / `x.ai` standard).
- Working with agent workflows in environments like Claude Code, Cursor, or Codex where frontend quality and visual polish are paramount.

## How to use
To install and run the taste skill workflows, use the following commands and scripts:

1. **Install the skill:**
   ```bash
   npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
   ```

2. **Generate architectural taste diagrams:**
   ```bash
   python taste_diagram.py
   ```

3. **Execution rules during development:**
   - Ensure every page uses real or licensed stand-in photography with proper credits.
   - Maintain strict alignment on left and right edges with a single unified design system.
   - Run browser checks and finish gates to validate layout integrity, micro-interactions, and visual standards prior to deployment or final delivery.

## Limitations
- Requires a compatible agent runtime environment (such as Claude Code, Cursor, or Codex) supporting skill integration.
- Shader effects and complex scroll scenes are resource-intensive and should be restricted strictly to tech, gaming, and software landing pages.
- Relies on external open archives or licensed stand-in assets for photography when client-provided imagery is missing.