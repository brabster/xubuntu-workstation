# OKF Wiki Update Log

## 2026-09-26
* **Update**: Added linting guidance for Copilot agent-session bootstrap, including hooks-path setup, dependency/collection prerequisites, restricted-network behavior for collection install failures, and review-scope checks when lint setup changes.
* **Update**: Expanded session workflow guidance to require agent-session lint-bootstrap verification and explicit capture of durable steering/linting lessons back into the wiki before session close.
* **Update**: Added explicit bootstrap and workflow guidance to keep merge request descriptions high-level while decisions are fluid, then re-align them whenever the agreed approach changes so review automation sees the same story as the code.
* **Update**: Added `steering/agent-bootstrap-rules.md` and `steering/session-workflow.md` so sessions can start from a minimal always-read rules/workflow set and look up detailed guidance only when needed.
* **Update**: Updated the OKF root index, overview, and `AGENTS.md` bootstrap guidance to distinguish mandatory bootstrap pages from lookup-on-demand reference pages, and clarified that Copilot memory should remain a sparse complement to the wiki rather than the primary repository rules engine.
* **Update**: Added `steering/activity-driven-thresholds.md` to capture the preference for activity-based triggers such as size-based log rotation when elapsed-time behavior creates avoidable noise on quiet systems and deterministic CI validation is valuable.
* **Update**: Added `steering/dependency-update-governance.md` to capture repository preference for automated point-of-use dependency updates gated by CI evidence, with cooldown retained and explicit acknowledgment of interim risk until a centralized control plane exists.
* **Update**: Added `steering/ci-feedback-playbook-ordering.md` to capture the rule that active or failing roles can be moved earlier in `workstation.yml` to fail faster in CI while they are being stabilised.
* **Update**: Expanded steering on cost-tiered research escalation so agents proactively offer Gemini prompt generation when web-enabled discovery is likely to be cheaper or more effective than local sandbox research.
* **Update**: Refined vendor-repo diagnostics and Slack package-management knowledge to record that live key fetches can fail in CI even when the package repository is reachable, and that vendoring the public key is acceptable when its full fingerprint is pinned and validated.
* **Update**: Recorded the expanded helper-test convention that CI now runs all `tests/test_*.py` helper tests before linting.
* **Update**: Removed `steering-and-reusable-knowledge.md`; this wiki now uses the decomposed section pages as the only canonical OKF structure.
* **Update**: Added `decisions/slack-package-source.md` to capture the accepted Slack package source, including the published `debian/jessie` packagecloud path validated from CI failure analysis.
* **Update**: Added steering concepts for recent-Ubuntu simple paths, CI role guard review, and vendor repo diagnostics, including the lesson that CI guards should be removed once a role becomes compatible.
* **Update**: Clarified that canonical wiki updates belong in the decomposed section pages.
* **Update**: Replaced a single combined steering page with topic-grouped concept documents under `steering/`, `linting/`, and `decisions/`.
* **Update**: Added subdirectory `index.md` files for progressive disclosure and root-level cross-link navigation.
* **Update**: Added this `log.md` to provide dated wiki change history at the wiki root scope.
