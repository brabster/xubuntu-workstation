---
type: Playbook
title: CI smoke-test diagnostics
description: Diagnose failures and make smoke-test assertions reliable.
tags: [ci, diagnostics, testing]
generated: { by: github-copilot/coding-agent, at: 2026-10-20T21:26:00Z }
stale_after: 2027-04-20T00:00:00Z
---

# CI smoke-test diagnostics

- Inspect the failed step's command trace and output; distinguish expected negative-test diagnostics from unexpected failures.
- Enable strict shell handling before the first assertion, and use command names available in the target image (for example, `python3` rather than assuming `python` exists).
- Keep expected failures explicit with a conditional that fails if the command unexpectedly succeeds; do not rely on `!` checks being honored under `set -e`.
- Verify authorization directly with a command-specific `sudo -l -U USER COMMAND` query. Do not infer authorization from a privileged command failing for an unrelated reason.
- Assert security-sensitive state directly, including sudoers content, group membership, ownership, and modes; validate sudoers syntax with `visudo -c`.
- After editing a workflow check, test its shell syntax and add a focused test for the assertion so future edits cannot silently weaken it.

Related concepts:
- [Session workflow](./session-workflow.md)
- [CI lint behavior](../linting/ci-lint-behavior.md)
