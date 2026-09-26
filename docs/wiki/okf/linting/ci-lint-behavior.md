---
type: Playbook
title: CI lint behavior
description: The ansible_lint workflow runs hook tests before lint and enforces full-scope ansible-lint on repository-scoped Ansible targets.
tags: [linting, ci, workflow]
---

# CI lint behavior

- Workflow path: `.github/workflows/ansible_lint.yml`.
- Installs lint dependencies from `requirements-dev.txt`.
- Runs hook behavior tests before linting.
- Runs ansible-lint in offline mode on `roles/`, `workstation.y*ml`, and `test.y*ml`.

Related concepts:
- [Local hook behavior](./local-hook-behavior.md)
- [CI as enforcement gate](../steering/ci-as-enforcement-gate.md)
