---
type: Playbook
title: Dependency update governance
description: Prefer automated point-of-use dependency updates gated by CI tests, with cooldown and explicit recording of resolved versions.
tags: [steering, dependencies, supply-chain]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# Dependency update governance

## Strategy for this repository

This is a personal Xubuntu workstation bootstrap, not a versioned application. Keep routine updates automated and use CI results to decide where the sole maintainer's attention is needed:

- Keep daily Dependabot updates for GitHub Actions and pip with the existing three-day cooldown. Let routine updates through when their required checks pass; handle security updates promptly rather than waiting for the routine cooldown.
- Let Ubuntu packages follow the signed distro archives and Ansible collections follow `roles/requirements.yml`; the weekly `test_install` job exercises the bootstrap on Ubuntu latest and rolling. Use its resolved-version manifest and SBOM artifacts as evidence instead of maintaining a duplicate lockfile or version inventory.
- Treat CI as smoke coverage, not proof of every workstation behavior: it cannot exercise graphical setup, systemd, or snap interactions. Spend maintainer review on failed checks and changes to compatibility, package sources, or trust settings that the checks do not cover, rather than manually reviewing every green version bump.

- Apply dependency updates automatically in CI and developer environments at point of use where possible.
- Keep repository-level cooldown controls enabled for supported ecosystems to reduce immediate exposure to newly published malicious releases.
- Treat automated test and validation outcomes as the primary merge gate, not semantic-version category alone.
- If an update passes required validation, allow it through without mandatory per-update human review.
- Record the exact resolved versions added or managed by repository automation runs so build outcomes can be reproduced independently of source control pin state.
- Do not inventory the user's pre-existing distro package baseline in repository-generated dependency evidence; treat the chosen OS installation as an external prerequisite and capture only the dependency surface the repository adds or manages directly.
- Publish SBOM artifacts from update/validation pipelines where feasible so provenance and version evidence are easy to inspect.
- Validate generated evidence artifacts with repository-owned tests and simple structural checks: the manifest and SBOM should parse as JSON, the manifest `package_count` should match the number of emitted packages, the SBOM should report `SPDX-2.3`, and `documentDescribes` should align with the generated package entries.
- When debugging artifact validity, run the generator locally first and inspect the emitted `resolved-versions.json` and `sbom.spdx.json` before relying on CI uploads alone.
- Accept the interim risk that a centralized multi-repo control plane is not yet available, and plan to introduce one for global allow/block/override control and faster incident response.
- Design unattended automation to fail loudly: raise alerts on failed update runs and on missing expected update activity.

Related concepts:
- [CI as enforcement gate](./ci-as-enforcement-gate.md)
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
- [Simplicity by default](./simplicity-default.md)
