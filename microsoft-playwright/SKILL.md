---
name: microsoft-playwright
description: Playwright is a framework for Web Testing and Automation. It allows testing Chromium, Firefox and WebKit with a single API. 
source: https://github.com/microsoft/playwright
license: Apache-2.0
stars: 101112
language: TypeScript
topics: automation, chrome, chromium, e2e-testing, electron, end-to-end-testing, firefox, javascript, playwright, test, test-automation, testing, testing-tools, web, webkit
saved: 2026-11-26
---

# microsoft/playwright

Playwright is a framework for web automation and testing. It drives Chromium, Firefox, and WebKit with a single API — in your tests, in your scripts, and as a tool for AI agents.

## When to use
Use this skill when the task involves:
- End-to-end (E2E) testing for web applications across multiple browsers (Chromium, Firefox, WebKit).
- Web automation, browser scripting, and web scraping.
- Generating automated browser workflows using Playwright Test, the Playwright CLI, or Playwright MCP for AI agents.
- Interacting with single-page applications, handling auto-waiting, and using web-first assertions.

## How to use

### Installation
Choose the path that fits your workflow:
- **Playwright Test (E2E Testing):**
  ```bash
  npm init playwright@latest
  ```
- **Playwright Library (Browser automation scripts):**
  ```bash
  npm i playwright
  ```
- **Playwright CLI (Coding agents):**
  ```bash
  npm i -g @playwright/cli@latest
  ```
- **Playwright MCP (AI agents and LLM-driven automation):**
  ```bash
  npx @playwright/mcp@latest
  ```

### Basic Automation Script Example (TypeScript/JavaScript)
```typescript
import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://playwright.dev');
  console.log(await page.title());
  await browser.close();
})();
```

### Running Tests
Execute your Playwright test suite using the CLI:
```bash
npx playwright test
```

## Limitations
- **Browser Binary Size:** Downloading and caching browser binaries (Chromium, Firefox, WebKit) requires significant disk space and network bandwidth during initial setup.
- **Environment Dependencies:** Running WebKit and certain headless browser configurations on minimal Linux containers may require additional system dependencies and libraries installed via `npx playwright install-deps`.
- **Anti-Bot Protections:** Modern web scraping targets often employ advanced bot detection (e.g., Cloudflare, Akamai) that can flag headless browser automation unless properly configured with stealth plugins or user-agent tweaks.