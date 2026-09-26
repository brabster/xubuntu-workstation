---
type: Playbook
title: CI as enforcement gate
description: Use required CI checks as the merge-time control while local hooks provide fast local feedback.
tags: [steering, ci, controls]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# CI as enforcement gate

- Treat CI status checks as the source of merge enforcement.
- Use local hooks to shorten feedback loops, not as the sole control.
- Keep CI controls explicit, deterministic, and aligned with repository policy.
- Guard roles out of CI only when the environment is genuinely incompatible, and restore them to CI once a compatible implementation exists.
- When actively iterating on a failing role, consider moving it earlier in the playbook so CI reaches the failure sooner and shortens the evidence loop.

Related concepts:
- [CI role guard review](./ci-role-guard-review.md)
- [CI feedback playbook ordering](./ci-feedback-playbook-ordering.md)
- [Cost-tiered agent selection](./cost-tiered-agent-selection.md)
- [Local hook behavior](../linting/local-hook-behavior.md)
- [CI lint behavior](../linting/ci-lint-behavior.md)
