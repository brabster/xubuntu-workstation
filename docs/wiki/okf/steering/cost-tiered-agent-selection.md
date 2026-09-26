---
type: Playbook
title: Cost-tiered agent selection
description: Use lower-cost agents for broad discovery and reserve higher-context work for remediation and integration.
tags: [steering, agents, cost]
---

# Cost-tiered agent selection

- Use cheaper models/agents for low-risk scanning and inventory tasks.
- When vendor docs, package metadata, or broader web search are likely to outperform the local sandbox, proactively offer to generate a Gemini prompt for discovery work.
- Gemini prompt generation is a cheap escalation path for web-enabled research because it does not consume Copilot credits; use it for discovery, then bring verified findings back into repository changes.
- Follow a staged workflow: cheap local search first, cheap external research prompt second when beneficial, and higher-context Copilot work last for integration and remediation.
- Escalate to higher-context work when integrating changes or resolving nuanced issues.
- Keep context-heavy runs focused on decisions that benefit from richer history.

Related concepts:
- [Simplicity by default](./simplicity-default.md)
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
- [Vendor repo diagnostics](./vendor-repo-diagnostics.md)
