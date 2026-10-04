---
type: Playbook
title: Session workflow
description: Default end-to-end workflow for issue handling, research, planning, implementation, and evidence-driven iteration.
tags: [steering, workflow, research]
generated: { by: github-copilot/coding-agent, at: 2026-10-04T12:21:54Z }
stale_after: 2027-04-04T00:00:00Z
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
10. **Review non-trivial helper script changes independently**: for repository-owned helper scripts, ask a separate agent to review substantive changes before finalizing.
11. **Keep helper-script tests focused and current**: add or update focused unit tests for repository-owned Python scripts by default, run them locally before finishing, and keep the tests aligned with the script's observable behavior.
12. **Run normal security validation before closing**: do not stop at functional checks for helper scripts or other code changes; complete the usual review and security-validation path as well.
13. **Iterate until accepted**: respond to review, new evidence, or external research by refining the implementation, re-aligning the MR description if needed, and repeating validation.
14. **For agent sessions, verify lint bootstrap first**: confirm hook-based lint prerequisites are active (for example `.githooks` hooks path and lint dependencies) before relying on pre-commit behavior.
15. **Capture reusable lessons before closing**: when a session discovers durable steering, workflow, linting, or decision guidance, update the relevant OKF wiki pages and keep any contributor-facing summary aligned in `CHANGELOG.md`.
16. **Run behavioral evaluations for agent-system changes**: when a change touches `docs/wiki/`, `AGENTS.md`, `prompts/`, `evals/`, agent instructions, developer-container configuration, hooks, or agent setup dependencies, run every applicable case from `evals/kb.json` as a separate prompt against the current agent system. Compare each response with its `expected_answer` and cited evidence. After all cases pass, write and commit `evals/agent-eval-attestation.json` with `python3 .github/scripts/agent_eval_attestation.py record --evaluator "human:<id>" --runtime "<agent/runtime and model>"`. If you cannot run the agent behaviorally, do not create a passing attestation; explain the limitation for human review. Keep the offline evidence-integrity check distinct from these behavioral evaluations.
17. **Keep knowledge evaluations aligned with the agent system**: when changing the knowledge base, `AGENTS.md`, prompts, or agent capabilities, assess whether `evals/kb.json` needs new or updated cases. Propose focused cases for meaningful behavior changes and explain when no useful case can be added.

Related concepts:
- [Agent bootstrap rules](./agent-bootstrap-rules.md)
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
- [Cost-tiered agent selection](./cost-tiered-agent-selection.md)
- [Helper script quality bar](./helper-script-quality-bar.md)
- [Simplicity by default](./simplicity-default.md)
