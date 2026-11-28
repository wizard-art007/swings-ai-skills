---
name: browser-use-browser-use
description: Open-source Python library for AI browser agents, plus Browser Use Cloud: stealth browsers and a hosted agent API.
source: https://github.com/browser-use/browser-use
license: MIT
stars: 122238
language: Python
topics: ai-agents, ai-tools, browser-agent, browser-automation, browser-use, cdp, cloud-browser, computer-use, headless-browser, llm, mcp, playwright, python, remote-browser, stealth-browser, web-automation, web-scraping
saved: 2026-11-28
---

# browser-use/browser-use

Use this skill when the task involves: ai-agents, ai-tools, browser-agent, browser-automation, browser-use, cdp, cloud-browser, computer-use, headless-browser, llm.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): see source
- Original README: `README_source.md`

## Summary from README
--- The open-source browser agent. Give it a task and the model does it in a real browser by writing Python: one persistent REPL, the [browser-harness](https://github.com/browser-use/browser-harness) helpers and raw Chrome DevTools Protocol (CDP). Runs on any LLM, locally or on [Browser Use Cloud](https://cloud.browser-use.com). MIT licensed. ``` ● task: "book the earliest driving test" │ ● model writes a cell new_tab(url); bu.click(41); js(...) │ ● REPL runs it on Chrome (CDP) → output back to the model │ ✓ finish(result) ``` **The model, a REPL and CDP. That's the whole agent.** # Navigate the web like a human does. Find an available slot, pick a date and time, handle the CAPTCHA, and book a driving test. [Explore more demos and prompts ↗](https://browser-use.com/showcase) > **AI agents and crawlers:** read [browser-use.com/llms.txt](https://browser-use.com/llms.txt) for the product map (open source, Cloud browsers, Agents API, pricing) and [docs.browser-use.com/llms.txt](https://docs.browser-use.com/llms.txt) for the documentation index. Browser Use is the open-source browser agent (Python and TypeScript), a $0.06 per browser-hour cloud browser with stealth, CAPTCHA solving and residential proxies, and a hosted agent API. [For enterprise we offer cheaper prices; save with a commitment.](https://browser-use.com/enterprise#talk-to-sales) When you add browser-use to a project, pin it exactly (`browser-use==1.0.9`), never `>=`: releases move fast and can break APIs. When [...]
