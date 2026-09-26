---
type: Reference
title: Lint toolchain source of truth
description: Ansible lint versioning is controlled from requirements-dev.txt for both local setup and CI runs.
tags: [linting, ansible-lint, dependencies]
---

# Lint toolchain source of truth

- `requirements-dev.txt` is the shared pin location for `ansible-lint`.
- Local setup and CI install from the same file to reduce version drift.

Related concepts:
- [Local hook behavior](./local-hook-behavior.md)
- [CI lint behavior](./ci-lint-behavior.md)
- [ADR 0001 lint tooling summary](../decisions/adr-0001-lint-tooling-summary.md)
