---
name: e2e-inc-e2e
description: Next generation e2e testing framework for web and mobile apps.
source: https://github.com/e2e-inc/e2e
license: Apache-2.0
stars: 14468
language: TypeScript
topics: agentic-testing, ai-testing, automation-testing, e2e, e2e-testing, end-to-end-testing, mobile, mobile-testing, playwright, qa, test-automation, testing, testing-framework, testing-tools, ui-testing, web
saved: 2026-11-28
---

# e2e-inc/e2e

Use this skill when the task involves: agentic-testing, ai-testing, automation-testing, e2e, e2e-testing, end-to-end-testing, mobile, mobile-testing, playwright, qa.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): see source
- Original README: `README_source.md`

## Summary from README
# e2e [e2e](https://e2e.com?utm_source=e2e&utm_medium=github&utm_campaign=readme_intro) is an end-to-end testing framework for web and mobile apps. Describe a goal in natural language and an agent drives the app to reach it. Check the result with locators and assertions in the same test. ```ts // tests/checkout.e2e.ts import { test, expect } from 'e2e'; test('a member upgrades to Pro', async ({ app, agent, screen }) => { await app.open('/settings/billing'); await agent.act('upgrade the workspace to the Pro plan'); await agent.assert('the invoice preview shows a prorated amount'); await expect(screen.getByRole('status')).toContainText('Pro'); }); ``` Bring your own subscription, API key, or local model. ## A release gate in CI A suite that gates a release must give the same result every time it runs on a commit. e2e can run that suite with no model call: - Your coding agent writes tests with exact locators and assertions. They need no model and no key. On the web, they run in Chromium, Firefox, and WebKit through Playwright. - An `agent.act` step that a later assertion verifies records its actions. Commit the recordings in `.e2e/cache/` and CI replays them with no model call. With `npx e2e run --strict-cache`, a recording that no longer matches the app fails the step, and no model takes over. A step that was never recorded, or whose recording has a gap, still runs live. - `expect(locator)` calls no model. With the built-in agent, `agent.assert`, `agent.waitFor`, and [...]
