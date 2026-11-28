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

## When to use
Use this skill when the task involves:
- Writing and executing agentic end-to-end tests for web and mobile applications.
- Natural language to UI action generation using local or API-based AI models.
- Setting up CI release gates that require deterministic replay without model calls using cached recordings (`.e2e/cache/`).
- Playwright-based multi-browser test execution (Chromium, Firefox, WebKit).
- Combining traditional assertions (`expect(locator)`) with conversational agent steps (`agent.act`, `agent.assert`).

## How to use
The skill includes simulation and integration entry points via `e2e_simulator.py`.

### Running tests with the simulator
To run e2e test suites or simulate agent-driven user interactions via the provided helper script:
```bash
python3 e2e_simulator.py --run --target ./tests/checkout.e2e.ts
```

### Strict CI Replay Mode
To run tests in CI ensuring that recordings match and zero model calls are made:
```bash
npx e2e run --strict-cache
```

### Standard Execution
Execute tests normally with live model fallback for unrecorded steps:
```bash
npx e2e run
```

## Limitations
- Requires valid user subscriptions, API keys, or local model configurations for unrecorded natural-language `agent.act` and `agent.assert` steps.
- Strict cache mode (`--strict-cache`) will fail immediately if any recorded action sequence diverges from the current application UI or contains gaps.
- Sandbox execution is mandatory; generated code and agent interactions must run strictly within designated isolated environments.