---
name: seleniumbase-seleniumbase
description: SeleniumBase browser automation handles E2E testing, web scraping, and stealth. CDP Mode bypasses bot-detection. Lots of integrations.
source: https://github.com/seleniumbase/SeleniumBase
license: MIT
stars: 13287
language: Python
topics: bot-detection, cdp, chrome-devtools-protocol, chromedriver, cloudflare-bypass, e2e-testing, end-to-end-testing, mcp, playwright, pytest, python, selenium-python, seleniumbase, test-automation, web-automation, web-scraping
saved: 2026-11-26
---

# seleniumbase/SeleniumBase

## Summary from README
Reliable browser automation for testing, scraping, and stealth. SeleniumBase provides robust capabilities for end-to-end testing, web scraping, and advanced anti-bot bypass mechanisms using CDP Mode, UC Mode, and Stealthy Playwright.

## When to use
Use this skill when the task involves:
- End-to-end (E2E) testing and test automation using `pytest` or Python scripts.
- Web scraping and browser automation requiring bot-detection bypasses (such as Cloudflare Turnstile or CAPTCHAs).
- Advanced stealth interactions using Chromium DevTools Protocol (CDP Mode) or Stealthy Playwright Mode.
- Interacting with web pages, typing, clicking, and extracting DOM data reliably.

## How to use

### Basic CDP Mode Example
To launch a stealth browser using SeleniumBase CDP mode to bypass bot-detection:

```python
from seleniumbase import sb_cdp

sb = sb_cdp.Chrome()  # Launch a stealth browser
sb.goto("https://www.planetminecraft.com/account")
sb.type('[name="email"]', "Test123")
sb.type('[name="password"]', "Pass")
sb.click("input#autologin")
# Add further actions or scraping logic as needed
sb.quit()
```

### Running Tests with Pytest
SeleniumBase integrates heavily with `pytest`. Run tests using standard pytest commands with SeleniumBase parameters:
```bash
pytest my_test_script.py --browser=chrome
```

## Limitations
- Stealth modes (CDP / UC Mode) rely on Chromium-based browsers; behavior on non-Chromium browsers may differ or lack specific stealth hooks.
- Highly aggressive WAFs (Web Application Firewalls) and zero-day anti-bot updates may occasionally require tweaking options, user agents, or proxy settings to maintain successful bypasses.