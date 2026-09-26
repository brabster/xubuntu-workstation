---
type: Playbook
title: CI feedback playbook ordering
description: Move actively changing or failing roles earlier in the playbook when that will shorten CI feedback loops.
tags: [steering, ci, playbook-order]
---

# CI feedback playbook ordering

- When iterating on a role or debugging a failing area, consider moving that role earlier in `workstation.yml` so CI fails faster.
- Use playbook ordering as a feedback-speed tool, not as a permanent workaround.
- Prefer temporary or clearly justified ordering changes that make active work easier to validate and review.
- After stabilising the role, keep the final ordering intentional, readable, and easy for future contributors to understand.
- Slack is the current example: after restoring CI coverage by removing the snap-era guard, it was useful to consider earlier placement in the role list so install failures surfaced sooner in GitHub Actions.

Related concepts:
- [CI as enforcement gate](./ci-as-enforcement-gate.md)
- [CI role guard review](./ci-role-guard-review.md)
- [Recent-Ubuntu simple paths](./recent-ubuntu-simple-paths.md)
