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

## Summary from README
The open-source browser agent. Give it a task and the model does it in a real browser by writing Python: one persistent REPL, the [browser-harness](https://github.com/browser-harness/browser-harness) helpers and raw Chrome DevTools Protocol (CDP). Runs on any LLM, locally or on [Browser Use Cloud](https://cloud.browser-use.com). MIT licensed. 

Task execution loop:
1. Model writes a cell (`new_tab(url)`, `bu.click(41)`, `js(...)`, etc.)
2. REPL runs it on Chrome (CDP) and returns output to the model
3. Loop continues until `finish(result)`

Browser Use is available as a Python and TypeScript library, a cloud browser service ($0.06 per browser-hour with stealth, CAPTCHA solving, and residential proxies), and a hosted agent API.

> **Important Versioning Note:** When you add `browser-use` to a project, pin it exactly (`browser-use==1.0.9`), never `>=`. Releases move fast and can break APIs.

## When to use
Use this skill when the task involves:
- ai-agents and ai-tools development
- browser-agent and browser-automation workflows
- Web scraping, crawler automation, and data extraction
- Interacting with web pages using LLMs via Chrome DevTools Protocol (CDP) or Playwright
- Handling complex web interactions requiring stealth browsers, CAPTCHA solving, or proxy rotation

## How to use

### Installation
Always pin the exact version to prevent breaking changes:
```bash
pip install browser-use==1.0.9
```

### Running the Simulator
An existing reference script is available to simulate browser-use tasks:
```bash
python browser_use_sim.py
```

### Basic Integration Example
```python
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser

# Initialize the browser and agent
browser = Browser()
agent = Agent(
    task="Find the cheapest flight from NYC to LAX next week",
    llm=ChatOpenAI(model="gpt-4o"),
    browser=browser,
)

# Run the agent asynchronously
import asyncio

async def main():
    result = await agent.run()
    print(result)

asyncio.run(main())
```

## Limitations
- **API Volatility:** Rapid updates in upstream packages can cause breaking changes; version pinning (`==1.0.9`) is strictly required.
- **Resource Intensity:** Running real browser instances (via CDP/Playwright) consumes significantly more memory and CPU than traditional HTTP-based scrapers.
- **LLM Dependency:** Performance and reliability depend heavily on the underlying model's reasoning capabilities and adherence to REPL syntax.
- **Sandbox Execution:** Generated code and browser automation tasks must be executed within secure sandbox environments to protect system integrity and sensitive data.