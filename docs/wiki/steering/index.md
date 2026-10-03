# Steering

* [Agent bootstrap rules](./agent-bootstrap-rules.md) - Minimal always-read rules for agent behavior in this repository.
* [Session workflow](./session-workflow.md) - Default end-to-end workflow for review, research, planning, implementation, and evidence-driven iteration.
* [Simplicity by default](./simplicity-default.md) - Prefer the simplest viable path first and add complexity only when evidence requires it.
* [Helper script quality bar](./helper-script-quality-bar.md) - Default to stdlib-first, well-tested, independently reviewed helper scripts with normal security validation.
* [Recent-Ubuntu simple paths](./recent-ubuntu-simple-paths.md) - Optimise for recent vanilla Ubuntu/Xubuntu installs and avoid extra branches unless evidence requires them.
* [Evidence-first diagnostics](./evidence-first-diagnostics.md) - Gather diagnostics before remediation when behavior is unclear.
* [Activity-driven thresholds](./activity-driven-thresholds.md) - Prefer activity-based triggers over elapsed-time triggers when that better matches operator intent and CI validation needs.
* [Vendor repo diagnostics](./vendor-repo-diagnostics.md) - Validate third-party package repository paths and package availability from CI evidence and vendor-published metadata.
* [CI as enforcement gate](./ci-as-enforcement-gate.md) - Treat required CI checks as merge control, with local hooks as fast feedback.
* [CI role guard review](./ci-role-guard-review.md) - Keep CI guards only for genuinely incompatible roles and remove them when coverage can be regained.
* [CI feedback playbook ordering](./ci-feedback-playbook-ordering.md) - Move active or failing roles earlier in the playbook when faster CI evidence is worth the reordering.
* [Cost-tiered agent selection](./cost-tiered-agent-selection.md) - Use lower-cost agents for broad discovery and reserve expensive context for integration.
* [Dependency update governance](./dependency-update-governance.md) - Prefer automated point-of-use updates with test gates, cooldown, and resolved-version evidence capture.
