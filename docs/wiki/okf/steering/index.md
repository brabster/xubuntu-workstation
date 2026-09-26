# Steering

* [Simplicity by default](./simplicity-default.md) - Prefer the simplest viable path first and add complexity only when evidence requires it.
* [Recent-Ubuntu simple paths](./recent-ubuntu-simple-paths.md) - Optimise for recent vanilla Ubuntu/Xubuntu installs and avoid extra branches unless evidence requires them.
* [Evidence-first diagnostics](./evidence-first-diagnostics.md) - Gather diagnostics before remediation when behavior is unclear.
* [Vendor repo diagnostics](./vendor-repo-diagnostics.md) - Validate third-party package repository paths and package availability from CI evidence and vendor-published metadata.
* [CI as enforcement gate](./ci-as-enforcement-gate.md) - Treat required CI checks as merge control, with local hooks as fast feedback.
* [CI role guard review](./ci-role-guard-review.md) - Keep CI guards only for genuinely incompatible roles and remove them when coverage can be regained.
* [Cost-tiered agent selection](./cost-tiered-agent-selection.md) - Use lower-cost agents for broad discovery and reserve expensive context for integration.
