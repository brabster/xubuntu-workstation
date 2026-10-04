---
type: Playbook
title: Agent bootstrap rules
description: Minimal always-read rules for agent behavior in this repository.
tags: [steering, bootstrap, rules]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# Agent bootstrap rules

- Treat the wiki as the primary repository knowledge system; use lookup-on-demand pages instead of preloading all detailed guidance.
- Work from evidence first: gather diagnostics before remediation when behavior is unclear or silent.
- Prefer the simplest secure implementation that is easy to review and validate; only add complexity when evidence requires it.
- When upgrading a dependency or action, compare the latest stable release with the current version and choose the latest compatible option; verify compatibility and behavior changes from authoritative sources, and explain any decision not to use the latest.
- For repository-owned Python helper scripts, default to lean stdlib-only implementations unless repository evidence shows an added dependency is necessary.
- Use CI as the merge-time enforcement gate and local checks as fast feedback.
- Escalate to Gemini or another web-enabled external agent only when public-domain or vendor research is needed and local repository evidence is insufficient.
- For ambiguous, risky, or architectural tasks: diagnose first, offer options, then provide a plan before implementation.
- For straightforward, narrow tasks: diagnose briefly, provide a concise plan, and move to implementation without unnecessary option expansion.
- During implementation, iterate on evidence until the merge request is accepted.
- Keep the merge request description aligned with the current agreed approach: avoid premature low-level specifics, and update the description after any material change in direction so review automation and reviewers see the same story as the code.
- If wiki guidance conflicts with newer ADRs or explicit user direction, follow the user direction first and then update the wiki.
- Keep changelog and security rationale up to date for repository changes, including UK Cyber Essentials impacts when relevant.
- Treat the wiki as a token-efficiency tool as well as a knowledge base: when durable preferences such as helper-script quality expectations are discovered, record them here once instead of re-explaining them in later sessions.
- Treat Copilot memory as sparse hints only: durable user preferences and a few expensive-to-rediscover facts. Do not rely on memory as the main repository rules engine when the wiki already captures the guidance.

Related concepts:
- [Session workflow](./session-workflow.md)
- [Simplicity by default](./simplicity-default.md)
- [Helper script quality bar](./helper-script-quality-bar.md)
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
- [CI as enforcement gate](./ci-as-enforcement-gate.md)
- [Cost-tiered agent selection](./cost-tiered-agent-selection.md)
