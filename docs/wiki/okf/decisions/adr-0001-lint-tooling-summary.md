---
type: Reference
title: ADR 0001 lint tooling summary
description: Summary of the accepted lint-tooling decision and canonical link to ADR 0001.
tags: [decisions, adr, linting]
resource: ../../../adr/0001-lint-tooling-approach.md
---

# ADR 0001 lint tooling summary

- Decision status: accepted.
- Selected approach: native git hook plus shared dependency pin in `requirements-dev.txt`.
- Rationale focus: lower toolchain dependency surface while preserving CI enforcement and local feedback.

Canonical source:
- [ADR 0001: lint tooling approach](../../../adr/0001-lint-tooling-approach.md)

Related concepts:
- [Lint toolchain source of truth](../linting/lint-toolchain-source-of-truth.md)
- [CI as enforcement gate](../steering/ci-as-enforcement-gate.md)
