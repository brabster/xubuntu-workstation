---
type: Playbook
title: CI role guard review
description: Use CI guards for genuinely incompatible roles, and remove them when a role becomes CI-compatible so coverage is regained.
tags: [steering, ci, guards]
---

# CI role guard review

- `when: not is_gh_actions` remains the standard guard for roles that are genuinely incompatible with GitHub Actions constraints.
- Before adding or keeping a CI guard, attempt a CI run and use the result as the decision input.
- If a role becomes CI-compatible after an implementation change, remove the guard and regain coverage instead of preserving a historical skip.
- Slack is the current example: the snap-based install required skipping in CI, while the APT-based install path allowed the role to run under the normal workstation playbook in CI.

Related concepts:
- [CI as enforcement gate](./ci-as-enforcement-gate.md)
- [Recent-Ubuntu simple paths](./recent-ubuntu-simple-paths.md)
