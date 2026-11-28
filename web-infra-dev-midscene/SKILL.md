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

Vision-driven E2E testing framework that interacts with web/mobile UIs via natural language.

## When to use
- When UI tests are brittle due to frequent DOM/selector changes.
- When you need to verify user-perceived experience rather than internal code structure.
- When performing cross-platform (web/mobile/desktop) GUI automation.
- As a GUI agent to perform complex multi-step user flows that are difficult to script with traditional selectors.

## How to use
Midscene can be used via its YAML test engine or integrated directly into existing test suites (e.g., Playwright/Puppeteer).

### 1. Configuration
Ensure the environment is configured with a supported LLM API key.

### 2. YAML-based Testing
Organize test logic in YAML for simplified E2E verification:
```yaml
beforeEach:
  - gotoUrl: https://your-app.example
cases:
  - name: User Workflow Verification
    steps:
      - aiAct: Perform natural language action (e.g., "Login with test credentials")
      - aiWaitFor: Verify condition (e.g., "The dashboard is visible")
      - aiAssert: Assert state (e.g., "The account balance is displayed correctly")
```

### 3. Execution Script
Use the existing infrastructure wrapper:
```bash
# Execute simulation/test suite
python3 midscene_sim.py --config ./test_config.yaml
```

## Limitations
- **Cost/Latency**: Reliance on vision models for every action introduces higher latency and per-token costs compared to traditional selector-based testing.
- **Determinism**: As an AI-native tool, results may occasionally vary due to model non-determinism; require robust assertion logic.
- **Environment**: Requires a stable environment with accessibility to a headless or headed browser runtime.
- **Flakiness**: While it reduces selector-based breakage, "AI hallucination" or misinterpretation of complex UI layouts can cause false negatives (addressable via O1: Flaky Test Pattern Detector).