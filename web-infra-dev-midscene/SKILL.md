---
name: web-infra-dev-midscene
description: See interfaces like a human. E2E testing in natural language.
source: https://github.com/web-infra-dev/midscene
license: MIT
stars: 15798
language: TypeScript
topics: browser-use, computer-use, e2e-testing, gpt-operator, gui-agent, javascript, phone-use, testing
saved: 2026-11-28
---

# web-infra-dev/midscene

Use this skill when the task involves: browser-use, computer-use, e2e-testing, gpt-operator, gui-agent, javascript, phone-use, testing.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): see source
- Original README: `README_source.md`

## Summary from README
Use the UI like a user. Vision-driven E2E testing in natural language — a GUI Agent and a newly designed test framework for web, mobile, and desktop apps. Website · English / 简体中文 ## Back to the essence of E2E testing with vision E2E testing should verify the interface, not its code structure. Tests tied to UI code structure are inherently fragile — and even more importantly, they cannot tell whether a user can actually understand and use the interface, or whether the UI conveys the right information. In the AI-native era, vision models give us the ability to test closer to the essence of E2E — looking at the screen to act and judge like a user. With accuracy and cost now in balance, the next stage of E2E testing is already here. ## Write a test in natural language Describe what a user wants to do and what they should see. You can organize tests in YAML with **Midscene Test**, or add the **GUI Agent** directly to your existing test suite. ### YAML test cases with Midscene Test After [creating a Midscene Test project](https://www.midscenejs.com/midscene-test/use) and configuring a model and the Web runtime, write a case like this. Replace the example URL with your app's address: ```yaml beforeEach: - gotoUrl: https://your-shop.example cases: - name: Find headphones under $100 steps: - aiAct: Search for headphones and filter the results to prices under $100 - aiWaitFor: The filtered search results are visible - aiAssert: There are products in the search results, and each [...]
