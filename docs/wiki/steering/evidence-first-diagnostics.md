---
type: Playbook
title: Evidence-first diagnostics
description: Obtain diagnostics first when behavior is unclear, then make the minimal targeted change.
tags: [steering, diagnostics]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# Evidence-first diagnostics

- Do not assume root cause when failures are ambiguous or silent.
- Gather logs, test output, and direct observations before proposing fixes.
- Prefer small, reversible fixes that directly address verified evidence.

Related concepts:
- [Simplicity by default](./simplicity-default.md)
- [Vendor repo diagnostics](./vendor-repo-diagnostics.md)
- [CI as enforcement gate](./ci-as-enforcement-gate.md)
