---
type: Playbook
title: CI role guard review
description: Use CI guards for genuinely incompatible roles, and remove them when a role becomes CI-compatible so coverage is regained.
tags: [steering, ci, guards]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# CI role guard review

- `when: not is_gh_actions` remains the standard guard for roles that are genuinely incompatible with GitHub Actions constraints.
- Before adding or keeping a CI guard, attempt a CI run and use the result as the decision input.
- If a role becomes CI-compatible after an implementation change, remove the guard and regain coverage instead of preserving a historical skip.
- Slack is the current example: the snap-based install required skipping in CI, while the APT-based install path allowed the role to run under the normal workstation playbook in CI.
- After a role is back in CI, consider whether moving it earlier in the playbook will produce faster feedback while the role is being stabilised.

Related concepts:
- [CI as enforcement gate](./ci-as-enforcement-gate.md)
- [CI feedback playbook ordering](./ci-feedback-playbook-ordering.md)
- [Recent-Ubuntu simple paths](./recent-ubuntu-simple-paths.md)
