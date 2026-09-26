---
type: Playbook
title: Activity-driven thresholds
description: Prefer activity-based triggers over elapsed-time triggers when time-only behavior creates avoidable noise and activity better matches intent.
tags: [steering, simplicity, testing]
---

# Activity-driven thresholds

- When a control exists mainly to surface recent activity, prefer an activity-based threshold such as size or count over elapsed time if the time-based trigger creates avoidable noise on quiet systems.
- Favor the smallest configuration change that aligns runtime behavior with operator intent and makes CI validation more deterministic.
- Keep a small fallback path for expected boundary cases, but do not preserve broader defensive behavior once the underlying trigger has been made more intentional.

Related concepts:
- [Simplicity by default](./simplicity-default.md)
- [Recent-Ubuntu simple paths](./recent-ubuntu-simple-paths.md)
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
