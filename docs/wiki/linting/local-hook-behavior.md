---
type: Playbook
title: Local hook behavior
description: The native pre-commit hook runs ansible-lint for scoped Ansible changes and validates staged-to-working-tree consistency.
tags: [linting, hooks, pre-commit]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# Local hook behavior

- Hook path: `.githooks/pre-commit`.
- Trigger: runs when scoped Ansible files are staged.
- Execution: lints full scoped targets (`roles/`, `workstation.y*ml`, `test.y*ml`) in offline mode.
- Guard: fails fast on staged vs unstaged mismatches for relevant files.

Related concepts:
- [CI lint behavior](./ci-lint-behavior.md)
- [CI as enforcement gate](../steering/ci-as-enforcement-gate.md)
