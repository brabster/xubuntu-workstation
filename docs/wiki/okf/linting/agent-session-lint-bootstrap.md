---
type: Playbook
title: Agent session lint bootstrap
description: How Copilot agent sessions should prepare and verify hook-based Ansible lint behavior.
tags: [linting, agent, bootstrap]
---

# Agent session lint bootstrap

- Setup workflow path: `.github/workflows/copilot-setup-steps.yml`.
- Session bootstrap should configure `core.hooksPath` to `.githooks`.
- Session bootstrap should install lint dependencies from `requirements-dev.txt`.
- Session bootstrap should install collections from `roles/requirements.yml` so offline lint can resolve expected modules.

## Restricted-network expectation

- In restricted environments, `ansible-galaxy collection install` can fail due to network policy.
- Treat this as environment evidence and continue with `ansible-lint --offline` where possible.
- If module-resolution warnings appear for missing collections, report them explicitly as environment constraints and avoid masking real lint failures.

## Review checklist note

- When lint behavior or hook setup changes, include `.github/workflows/copilot-setup-steps.yml` in the review scope alongside `.githooks/pre-commit` and `.github/workflows/ansible_lint.yml`.

Related concepts:
- [Local hook behavior](./local-hook-behavior.md)
- [CI lint behavior](./ci-lint-behavior.md)
