---
type: Playbook
title: CI lint behavior
description: The ansible_lint workflow runs hook tests before lint and enforces full-scope ansible-lint on repository-scoped Ansible targets.
tags: [linting, ci, workflow]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# CI lint behavior

- Workflow path: `.github/workflows/ansible_lint.yml`.
- Installs lint dependencies from `requirements-dev.txt`.
- Runs hook behavior tests before linting.
- Treat those helper-script unit tests as part of the merge gate for repository-owned Python helpers, not as optional extras.
- Keep helper-script tests aligned with the script behavior they protect so CI failures reflect real regressions in repository automation.
- Runs ansible-lint in offline mode on `roles/`, `workstation.y*ml`, and `test.y*ml`.

## Failure-diagnosis order

- Treat helper-test failures as first-class `ansible_lint` workflow failures; this job can fail before lint runs.
- When the job fails, inspect the unittest step output in Actions logs before investigating ansible-lint findings.
- Only debug lint findings after the helper-test step passes.

Related concepts:
- [Local hook behavior](./local-hook-behavior.md)
- [CI as enforcement gate](../steering/ci-as-enforcement-gate.md)
