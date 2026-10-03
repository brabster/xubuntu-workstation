---
type: Playbook
title: Helper script quality bar
description: Default quality bar for repository-owned helper scripts so future sessions meet expectations quickly and with less rework.
tags: [steering, python, scripts, quality]
generated: { by: github-copilot/coding-agent, at: 2026-10-03T18:25:40Z }
stale_after: 2027-04-03T00:00:00Z
---

# Helper script quality bar

- Default repository-owned helper scripts to the Python standard library only.
- Add a new script dependency only when repository evidence shows the stdlib path is insufficient.
- Keep helper scripts small in scope, low in abstraction, and easy to review, test, and reason about.
- Prefer direct data flow and explicit validation over framework-style layering or speculative extensibility.
- For non-trivial helper script changes, get an independent review from a separate agent before finalizing the session.
- Treat helper scripts like other production code: run the normal security validation path before completion, not just functional tests.
- Add or update focused unit tests for new helper script behavior by default, and run those tests locally before finishing.
- Keep helper-script tests aligned with the script's public behavior so CI failures point at real regressions.
- Capture durable helper-script expectations here once so future sessions can follow them without re-discovering the same steering.

Related concepts:
- [Agent bootstrap rules](./agent-bootstrap-rules.md)
- [Session workflow](./session-workflow.md)
- [Simplicity by default](./simplicity-default.md)
- [CI lint behavior](../linting/ci-lint-behavior.md)
