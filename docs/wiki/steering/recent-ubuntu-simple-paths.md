---
type: Playbook
title: Recent-Ubuntu simple paths
description: Prefer simple, reviewable implementations for this repository's target environment unless evidence requires extra complexity.
tags: [steering, simplicity, ubuntu]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# Recent-Ubuntu simple paths

- Optimise first for initial, vanilla installs on recent Ubuntu/Xubuntu releases, which are this repository's explicit target.
- Prefer the smallest implementation that is clear to review and maintain for that target environment.
- Do not add defensive branches for unlikely edge cases unless CI results, field failures, or support requirements show they are needed.
- When a simpler path restores CI coverage or reduces ambiguity, prefer it over a more defensive but harder-to-review implementation.
- Simplicity also includes reducing CI iteration time when a small ordering change can surface active failures earlier.

Related concepts:
- [Simplicity by default](./simplicity-default.md)
- [CI role guard review](./ci-role-guard-review.md)
- [CI feedback playbook ordering](./ci-feedback-playbook-ordering.md)
- [Vendor repo diagnostics](./vendor-repo-diagnostics.md)
