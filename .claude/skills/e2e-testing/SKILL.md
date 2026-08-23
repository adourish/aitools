---
name: e2e-testing
description: End-to-end and browser testing with Playwright — writing specs against Salesforce LWC features, driving a browser for scraping or automation, and keeping a session alive. Use for "write an e2e test", "test the flow in the browser", "playwright", "does the button work", or "automate this web task".
---

# E2E & browser automation

| Task | Guide |
|------|-------|
| E2E testing of Salesforce LWC features (Playwright CLI + `sf org open`) | `development/skill_e2e_testing.md` |
| General web automation and scraping | `automation/skill_browser_automation.md` |
| Keeping a browser session alive across runs | `development/browser_keep_alive.py` |

## Rules

- Always drive Playwright through the **`npx playwright` CLI** — not the MCP Playwright tools.
- Org logins come from the KeePass vault, never from the spec file.
- A UI test that passes but ignores keyboard access or contrast is not done — see `section-508`.
