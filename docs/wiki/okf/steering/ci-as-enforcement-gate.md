---
type: Playbook
title: CI as enforcement gate
description: Use required CI checks as the merge-time control while local hooks provide fast local feedback.
tags: [steering, ci, controls]
---

# CI as enforcement gate

- Treat CI status checks as the source of merge enforcement.
- Use local hooks to shorten feedback loops, not as the sole control.
- Keep CI controls explicit, deterministic, and aligned with repository policy.
- Guard roles out of CI only when the environment is genuinely incompatible, and restore them to CI once a compatible implementation exists.

Related concepts:
- [CI role guard review](./ci-role-guard-review.md)
- [Cost-tiered agent selection](./cost-tiered-agent-selection.md)
- [Local hook behavior](../linting/local-hook-behavior.md)
- [CI lint behavior](../linting/ci-lint-behavior.md)
