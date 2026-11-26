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

Use this skill when the task involves: bot-detection, cdp, chrome-devtools-protocol, chromedriver, cloudflare-bypass, e2e-testing, end-to-end-testing, mcp, playwright, pytest.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): see source
- Original README: `README_source.md`

## Summary from README
Reliable browser automation for testing, scraping, and stealth. 🚀 Start | 🏰 Features | 🎛️ Options | 📚 Examples | 💻 Scripts | 🗾 Locales 📗 API | 📘 Stealth API | 🔠 Syntax Formats | 🔴 Recorder | 📊 Dashboard 🎖️ GUI | 📰 Test Page | 👤 UC Mode | 🐙 CDP Mode | 📶 Charts | 🖥️ Farm 👁️ How | 🚝 Migration | 🎭 Stealthy Playwright | 🛂 MasterQA | 🚎 Tours 🤖 MCP | 🟨 JS Tools | 🌏 Translator | 🎞️ Presenter | 🖼️ Visual | 🗂️ CPlans -------- 🐙 CDP Mode bypasses bot-detection with Chromium-based browsers.(Examples: ./examples/cdp_mode/) 🎭 Stealthy Playwright Mode extends CDP Mode's stealth to Playwright.(Examples: ./examples/cdp_mode/playwright) 📚 In addition to stealth modes, SeleniumBase has regular modes for E2E testing. * 🧪 [**Over 200 end-to-end testing examples included**](https://github.com/seleniumbase/SeleniumBase/tree/master/examples).(Many of those run with **`pytest`** instead of **`python`**) -------- 📝 [This example](https://github.com/seleniumbase/SeleniumBase/blob/master/examples/cdp_mode/raw_cdp_mode.py) uses seleniumbase sb_cdp (*[Pure CDP Mode](https://github.com/seleniumbase/SeleniumBase/blob/master/examples/cdp_mode/ReadMe.md#Pure_CDP_Mode)*):(It calls a few basic methods and bypasses a Cloudflare Turnstile) ```python from seleniumbase import sb_cdp sb = sb_cdp.Chrome() # Launch a stealth browser sb.goto("https://www.planetminecraft.com/account") sb.type('[name="email"]', "Test123") sb.type('[name="password"]', "Pass") sb.click("input#autologin") # Uncheck a checkbox [...]
