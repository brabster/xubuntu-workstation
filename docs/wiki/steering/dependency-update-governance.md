---
type: Playbook
title: Dependency update governance
description: Prefer automated point-of-use dependency updates gated by CI tests, with cooldown and explicit recording of resolved versions.
tags: [steering, dependencies, supply-chain]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# Dependency update governance

- Apply dependency updates automatically in CI and developer environments at point of use where possible.
- Keep repository-level cooldown controls enabled for supported ecosystems to reduce immediate exposure to newly published malicious releases.
- Treat automated test and validation outcomes as the primary merge gate, not semantic-version category alone.
- If an update passes required validation, allow it through without mandatory per-update human review.
- Record the exact resolved versions used by automation runs so build outcomes can be reproduced independently of source control pin state.
- Publish SBOM artifacts from update/validation pipelines where feasible so provenance and version evidence are easy to inspect.
- Accept the interim risk that a centralized multi-repo control plane is not yet available, and plan to introduce one for global allow/block/override control and faster incident response.
- Design unattended automation to fail loudly: raise alerts on failed update runs and on missing expected update activity.

Related concepts:
- [CI as enforcement gate](./ci-as-enforcement-gate.md)
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
- [Simplicity by default](./simplicity-default.md)
