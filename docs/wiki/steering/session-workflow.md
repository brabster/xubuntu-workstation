---
type: Playbook
title: Session workflow
description: Default end-to-end workflow for issue handling, research, planning, implementation, and evidence-driven iteration.
tags: [steering, workflow, research]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# Session workflow

1. **Review the task**: classify whether it needs explanation, diagnosis, planning, or implementation.
2. **Investigate locally first**: inspect repository context, relevant files, logs, tests, and CI evidence.
3. **Research externally only when needed**: if local evidence is insufficient and the question depends on public-domain or vendor information, generate a Gemini prompt, process the results, and repeat only while more rounds materially improve confidence.
4. **Offer diagnosis**: explain the most evidence-backed understanding of the problem before proposing changes.
5. **Offer options when warranted**: do this for ambiguous, risky, or architectural choices; skip broad option trees for narrow fixes.
6. **Produce a plan for review**: describe the intended path before implementation when the task is non-trivial.
7. **Keep the merge request description decision-aligned**: keep early MR descriptions high-level while decisions are still fluid, then update them whenever the agreed approach changes materially so reviews and automation stay in sync with the implementation.
8. **Implement incrementally**: make the smallest secure change that satisfies the agreed direction.
9. **Validate on evidence**: run the smallest relevant checks early, then broader validation before completion.
10. **Iterate until accepted**: respond to review, new evidence, or external research by refining the implementation, re-aligning the MR description if needed, and repeating validation.
11. **For agent sessions, verify lint bootstrap first**: confirm hook-based lint prerequisites are active (for example `.githooks` hooks path and lint dependencies) before relying on pre-commit behavior.
12. **Capture reusable lessons before closing**: when a session discovers durable linting/bootstrap guidance, update the relevant OKF steering/linting pages and keep any contributor-facing summary aligned in `CHANGELOG.md`.

Related concepts:
- [Agent bootstrap rules](./agent-bootstrap-rules.md)
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
- [Cost-tiered agent selection](./cost-tiered-agent-selection.md)
- [Simplicity by default](./simplicity-default.md)
