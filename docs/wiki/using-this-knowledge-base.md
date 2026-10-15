---
type: Guide
title: Using this knowledge base in other repositories
description: Adopt reusable agent guidance in another repository and contribute improvements back here.
tags: [knowledge-base, reuse, contribution]
generated: { by: github-copilot/coding-agent, at: 2026-10-15T07:25:00Z }
stale_after: 2027-04-15T00:00:00Z
---

# Using this knowledge base in other repositories

This wiki lives in `brabster/xubuntu-workstation`; it is not a separately versioned package or automatically loaded by agents in other repositories. Its guidance also includes workstation-specific decisions, so copying the whole wiki would give another project irrelevant instructions.

## Adopt reusable guidance

1. Select only the general guidance that applies, such as [evidence-first diagnostics](./steering/evidence-first-diagnostics.md) and [simplicity by default](./steering/simplicity-default.md). Keep workstation-specific decisions and linting instructions in this repository.
2. Copy the selected pages into the other repository's own knowledge-base directory. Record each source page's GitHub URL so future maintainers can compare it with upstream, and repair or remove relative links to pages that were not copied.
3. Point that repository's agent entry point, such as `AGENTS.md` or `.github/copilot-instructions.md`, at its local knowledge-base index and bootstrap pages. Keep the target repository's domain instructions alongside the shared guidance rather than replacing them.
4. Review upstream changes and update the local copies when useful. There is no automatic synchronization; agents should rely on the checked-in local copies, not on links to remote files.

For example, `tw-site-mkdocs` can retain its `.github/copilot-instructions.md` writing and publishing guidance, then add a local `AGENTS.md` that points to selected, copied general guidance. Do not import workstation setup requirements or decisions such as the Slack package source.

## Contribute improvements

- Keep repository-specific guidance in the repository where it applies.
- When a lesson is useful across repositories, generalize it, remove local assumptions, and propose it here as a pull request. Include evidence and update the wiki navigation and relevant knowledge-evaluation cases when appropriate.
- For improvements that apply only to another project, update that project's local knowledge base instead. A pull request here is not a mechanism for automatically updating other repositories.

The `evals/` cases and attestation validate this repository's guidance; they are not a plug-in test suite for downstream repositories. A consuming repository should add or adapt checks for its own instructions and sources.
