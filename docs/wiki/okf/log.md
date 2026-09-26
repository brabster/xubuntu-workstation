# OKF Wiki Update Log

## 2026-09-26
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
