# Copilot coding agent instructions for `xubuntu-workstation`

Prioritise secure, stable, minimal changes that align with this repository's Ansible-first approach.

## Core expectations

- Follow existing repository guidance in `AGENTS.md`, `README.md`, and `CHANGELOG.md`.
- Use evidence first: when behaviour is unclear or failing silently, gather diagnostics before proposing fixes.
- Prefer the simplest working change; avoid speculative complexity.
- Use authoritative sources and established best practices (Ansible docs, Ubuntu docs, vendor documentation) for security-sensitive or system-level changes.
- Prefer Ansible modules over ad-hoc shell commands, and preserve idempotency.
- Keep feedback loops fast and reliable: run the smallest relevant validation early, then broader validation before completion.

## Security and compliance

- Treat UK Cyber Essentials as a key compliance baseline for security-related changes.
- Explain security trade-offs and include a concise threat model assessment for security-impacting changes.
- Do not introduce secrets, unsafe download/install patterns, or unnecessary privilege escalation.

## Changelog and documentation standards

- All changes must be documented in the changelog using a consistent style, including a threat model assessment and reference to relevant compliance requirements (e.g., UK Cyber Essentials).
- When excluding roles or tasks from CI, document the reason and supporting evidence in both the changelog and code comments.
- New changelog entries should reference the relevant PR number and be inserted in reverse chronological order, with the most recent change at the top. **Always verify the PR number by checking the open pull requests for this repository using GitHub tools before writing the changelog entry.**
- Changelog security assessments must explicitly state the net change to risk (for example reduced, increased, or unchanged), not just describe the area affected.
- Security rationale should be clear and concise, explaining both the risk and benefit of each change.

## Prompting quality

- If a user prompt is underspecified, risky, or inefficient, suggest a better prompt format before or alongside implementation.
- Include a short "Prompt improvement suggestion" in your response when a more specific prompt would improve speed, safety, or correctness.
- Prefer ASCII-only characters in generated edits and responses unless the target file already requires non-ASCII content or the user explicitly asks for it.
