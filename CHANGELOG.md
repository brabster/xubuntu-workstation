# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [PR #93 - Add knowledge base evaluations](https://github.com/brabster/xubuntu-workstation/pull/93)

### Added

- **An offline knowledge-base evaluation set now protects representative answers**: added question/evidence cases for agent bootstrap, failure diagnosis, CI lint triage, CI role guards, and the Slack package-source decision. The existing helper-test gate checks that expected evidence remains in its cited wiki pages, and CI runs it when the knowledge base or evaluation set changes.
- **Evaluation scope is explicit**: documented how to run the checks and how to use the cases to assess agent answers; the offline checks validate corpus evidence, not model response quality.
- **Knowledge-base evaluations now run on every pull request and merge-queue group**: added a dedicated workflow without path filters, so its `kb_evals / evals` status is available to require before merging. Repository rulesets must select that status check; this branch-protection setting cannot be enforced from workflow files alone.
- **Agent sessions now assess eval coverage when the agent system changes**: session guidance asks contributors to consider focused evaluation additions when changing the knowledge base, agent instructions, prompts, or capabilities.
- **Behavioral evaluation evidence is committed alongside agent-system changes**: after running and reviewing every applicable case in-session, run `python3 .github/scripts/agent_eval_attestation.py` to record case IDs, result, time, and a digest of the agent-system inputs in `evals/agent-eval-attestation.json`. CI checks that evidence file against the current inputs, so changes make it stale until the evals are rerun; `--check` is the only option CI needs. The fixed repository output path and case set need no user-supplied arguments. No PR-body metadata or model credentials are needed.
- **Eval instructions are included in the evidence digest**: changing the procedure invalidates the previous run. Merge-queue synthetic trees run corpus-integrity checks; behavioral evidence is checked on each PR before it enters the queue.
- **Behavioral cases now define expected answers as well as source evidence**: the role-guard case specifically requires agents to surface the existing difference between `AGENTS.md` and the CI guard playbook instead of repeating one rule as settled guidance.

### Changed

- **Behavioral evaluation timestamps are validated as timezone-aware ISO 8601 values**: CI rejects malformed or timezone-naive timestamps instead of accepting unauditable text.

### Security

- **Threat Model Assessment**: This change **reduces knowledge-regression and change-review risk while keeping workstation runtime risk unchanged**.
    - **Rationale**: The behavioral run occurs in the contributor's session; CI validates a committed evidence file against a digest of agent-system inputs and checks that its timestamp is an auditable timezone-aware value, with no model credentials or calls. The attestation is not cryptographic proof, so a required human reviewer must verify the report.
    - **Benefit**: A repeatable, offline check protects selected setup, diagnostic, and security-decision knowledge, supporting UK Cyber Essentials expectations for controlled, reviewable configuration and change management.
    - **Net risk statement**: Knowledge-regression and review risk is **reduced**; workstation runtime risk is **unchanged**.
    - **CLI simplification**: Removing self-reported evaluator/runtime fields reduces recording friction without changing the gate; commit history and human review remain the attribution and verification mechanisms. The net change to workstation runtime risk is **unchanged**.

## [PR #89 - Simplify Google Chrome installation dependency resolution](https://github.com/brabster/xubuntu-workstation/pull/89)

### Changed

- **Chrome now installs directly from Google's current stable package through APT**: Removed the manual ALSA package/cache checks and install steps. APT resolves the local `.deb` dependencies, while the download remains the unpinned `stable_current` package from Google's official HTTPS domain.

### Security

- **Threat Model Assessment**: This change **reduces installation complexity and dependency-management risk while leaving workstation runtime risk unchanged**.
    - **Rationale**: The role no longer separately chooses or installs an ALSA package; APT resolves dependencies declared by Chrome's local package. The download source remains `https://dl.google.com`, with no third-party repository added. Browser policy configuration and update behavior are unchanged.
    - **Benefit**: Fewer package-management steps reduce the chance of dependency drift or unnecessary package changes, supporting UK Cyber Essentials expectations for secure, controlled configuration. Existing managed Chrome policies remain in force.
    - **Net risk statement**: Installation and dependency-management risk is **reduced**; workstation runtime and browser policy risk are **unchanged**.

## [PR #87 - Publish resolved-version manifest and SBOM from CI](https://github.com/brabster/xubuntu-workstation/pull/87)

### Added

- **CI jobs now publish resolved dependency evidence artifacts**: the `ansible_lint` and `test_install` workflows now generate a repository-owned `resolved-versions.json` manifest for each job run, capturing the exact Python packages, declared Ansible collections, runner metadata, and tool versions that the repository automation adds or manages in the CI environment that produced the result.
- **CI jobs now publish SPDX SBOM artifacts alongside the manifest**: the same workflow step now emits an `sbom.spdx.json` artifact per job using that repo-managed resolved dependency set, so supply-chain provenance and post-run dependency inspection do not rely only on source-level pins or transitive package resolver behavior at a later date.
- **Artifact generation logic is unit tested in-repo**: added focused Python unit tests for the dependency-artifact generator so the existing `ansible_lint` helper-test gate protects the manifest/SBOM structure and parsing behavior before workflow execution.
- **Wiki steering now records the CI trigger policy, helper-script quality bar, and evidence-validation checks**: added explicit guidance that PR branches use `pull_request` path filters while `push` validation is reserved for `main`, documented a stdlib-first and independently reviewed quality bar for repository-owned helper scripts, and kept the artifact validation checks easy to reapply when verifying generated `resolved-versions.json` and `sbom.spdx.json` output.

### Changed

- **`test_install` artifact naming is now shell-portable in GitHub Actions**: the workflow now sanitizes matrix image names with a POSIX-compatible pipeline instead of Bash-only parameter substitution, so the default `sh` runner in the container job can always prepare artifact paths successfully.
- **PR branches no longer run duplicate push and pull-request CI for the same change**: `ansible_lint` and `test_install` now keep push-based validation on `main`, while pull-request validation remains the review-time gate for proposed changes. `test_install` pull-request coverage is now expressed as an explicit allowlist of workflow, helper-test, dependency, and workstation automation paths, so relevant PR changes still run without needing a second branch-push execution of the same workflow.
- **Ansible collection evidence now reflects repository-declared dependencies rather than every installed collection**: the CI generator still inspects the live CI environment for versions, but it now filters Ansible collection entries down to the collections declared in `roles/requirements.yml` when that declaration is available, which keeps the SBOM/manifest aligned with the repository's actual external collection dependency set instead of unrelated collections bundled into the runner image.
- **CI dependency evidence no longer inventories the base distro package set**: the manifest and SBOM now exclude Debian package enumeration, keeping the artifact focused on the dependency surface this repository adds or manages rather than the user's pre-existing OS install choice.
- **`bootstrap.sh` and `test_install` now share the same Ansible dependency bootstrap path**: `bootstrap.sh` now installs `ansible-core` plus the collections declared in `roles/requirements.yml`, and `test_install` now prepares CI-specific vars before invoking `bootstrap.sh` so workflow validation exercises the same dependency setup path used for real bootstrap installs as closely as the container environment allows.

### Security

- **Threat Model Assessment**: This change **reduces CI supply-chain traceability risk** while keeping workstation runtime risk unchanged.
    - **Rationale**: The generator only reads package/version metadata already present in the CI environment and writes it to workflow artifacts; it does not add new privileged execution paths, package sources, or unattended download/install bootstrap logic. Publishing both a resolved-version manifest and an SPDX SBOM improves evidence retention for dependency investigations, incident response, and reproducibility when upstream repositories change after a run has completed. The follow-up workflow fixes keep artifact-path setup compatible with the job's actual shell and remove redundant branch-push CI on open PR branches without reducing review-time or main-branch validation coverage.
    - **Benefit**: Reviewers and maintainers can inspect the exact dependency set used by each validation run without re-resolving packages later, and CI now fails less often for shell-compatibility reasons while avoiding duplicate executions for the same reviewed change. This strengthens controlled change evidence and supports UK Cyber Essentials expectations for secure configuration management and auditable change records.
    - **Net risk statement**: Net risk is **reduced** for CI supply-chain diagnostics and validation reliability, and **unchanged** for managed workstation runtime controls.

## [PR #86 - Tidy OKF structure and documentation alignment](https://github.com/brabster/xubuntu-workstation/pull/86)

### Changed

- **OKF wiki path is flatter and less redundant**: moved the repository knowledge bundle from `docs/wiki/okf/` to `docs/wiki/`, keeping the same decomposed `steering/`, `linting/`, and `decisions/` structure without the extra single-child `okf/` directory layer.
- **Imported OKF specification reference is now clearly named and sourced**: renamed the local spec copy to `docs/wiki/okf_spec_v0.2.md` and recorded the canonical GoogleCloudPlatform `open-knowledge-format` source in frontmatter so the file name and provenance both reflect the actual OKF v0.2 document.
- **Wiki concept frontmatter now captures authorship/freshness signals**: added `generated` and `stale_after` metadata to the non-reserved wiki concept documents so the bootstrap and reference pages expose who last generated the content and when it should be reviewed for staleness, in line with OKF v0.2 lifecycle guidance.
- **Wiki update history now defaults to normal repository history instead of a separate root log file**: removed the standalone wiki `log.md`, updated bootstrap/session guidance accordingly, and documented that git history plus `CHANGELOG.md` are the default change record unless a future subtree genuinely needs a scope-local prose log.
- **ADR separation is now explicit rather than implicit**: the wiki `decisions/` section now states that canonical ADR records remain in `docs/adr/`, while the wiki keeps short summaries and links for bootstrap-friendly navigation.
- **Repository docs are aligned with the tidied wiki layout**: updated `AGENTS.md`, the wiki overview/index pages, and the root `README.md` so contributor and agent guidance points at the new `docs/wiki/` paths and current structure.

### Security

- **Threat Model Assessment**: This change **keeps workstation runtime risk unchanged while reducing documentation ambiguity risk**.
    - **Rationale**: The change is documentation-only. It does not alter package sources, privilege boundaries, service state, network exposure, or update behavior. The main effect is to reduce ambiguity in where agents and contributors look for repository steering, and to make provenance/freshness metadata explicit on wiki concept pages.
    - **Benefit**: Clearer bootstrap paths, explicit source provenance for the imported OKF spec, and frontmatter freshness metadata make repository guidance easier to review and less likely to drift silently, supporting UK Cyber Essentials expectations for controlled, reviewable change management.
    - **Net risk statement**: Net workstation runtime risk is **unchanged**, while documentation-governance and change-traceability risk are **reduced**.


## [PR #84 - Fix missing ClamAV update log lines after overnight suspend](https://github.com/brabster/xubuntu-workstation/pull/84)

### Fixed

- **FreshClam logging now rotates by activity, not just elapsed time**: the role now manages the relevant `freshclam.conf` logging directives directly, keeping `/var/log/clamav/freshclam.log` enabled while turning on ClamAV's built-in `LogRotate` support with `LogFileMaxSize 128K`. On a quiet laptop this keeps the active log current for longer, while still bounding log growth if update logging becomes unexpectedly noisy.
- **ClamAV health check now exhausts available FreshClam evidence before giving up**: the verification script checks the current FreshClam log first, then scans rotated `freshclam.log.N` and `freshclam.log.N.gz` files in generation order, and finally falls back to current-boot `clamav-freshclam` journal entries containing FreshClam update markers before reporting that no recent update lines were found.
- **Regression coverage now protects the broader fallback behavior directly**: the helper-script unit tests now cover later rotated logs, compressed rotated logs, and the current-boot journal fallback, while the GitHub Actions smoke test still verifies the managed FreshClam logging directives and a deterministic first-rotation fixture end to end.
- **Health-check `runuser -l` execution no longer depends on preserved environment variables**: the script now passes test payload and target file paths as positional arguments to the login-shell command so login-mode environment scrubbing cannot blank required values during create/cleanup operations.
- **FreshClam config tasks are idempotent again and compressed-log regressions are covered**: the role now keeps a single managed FreshClam logging block (avoiding unconditional remove-then-add churn and needless service restarts), creates the FreshClam log file only when absent while separately normalizing ownership/mode without touch-style timestamp churn, and adds a regression test that warns on unreadable `.gz` rotations while continuing to later usable log sources.
- **CI helper-test expectation now matches the idempotent FreshClam logging approach**: updated the FreshClam logging unit test to assert the old remove-before-reinsert cleanup task is absent, aligning test coverage with the current single-managed-block implementation so `ansible_lint` workflow helper tests no longer fail before linting.
- **`test_install (ubuntu:latest)` no longer fails on ClamAV verifier template parsing and log-path drift**: fixed a Jinja/bash collision in array-index loops that caused template rendering to fail, aligned FreshClam evidence lookup to use the configured `clamav_freshclam_log_file` path (including rotations) rather than a hard-coded `/var/log/clamav/freshclam.log` prefix, and now ensures the configured FreshClam log parent directory exists before managing the log file.

### Changed

- **Agent bootstrap trimmed to a minimal always-read set**: `AGENTS.md` now points sessions at the OKF root index, overview, a new bootstrap rules page, and a new session workflow page, instead of requiring agents to preload the full wiki tree and specification on every run.
- **Wiki now distinguishes mandatory rules from lookup-on-demand detail**: the OKF root and overview pages now explicitly separate the small bootstrap set from deeper steering/linting/decision references, and clarify that Copilot memory should remain a sparse complement rather than the main repository rules engine.
- **Workflow now requires MR-description realignment when implementation direction changes**: the bootstrap rules and session workflow now tell agents to keep early merge request descriptions high-level while decisions are still fluid, then update the description after any material approach change so review bots and human reviewers are not left comparing the code against stale intent.
- **Copilot agent sessions now bootstrap hook-based lint prerequisites**: added `.github/workflows/copilot-setup-steps.yml` so agent sessions set `core.hooksPath` to `.githooks`, install `requirements-dev.txt`, and install `roles/requirements.yml` collections before coding, making `.githooks/pre-commit` ansible-lint checks consistently available in agent environments.
- **OKF wiki now captures agent-session lint bootstrap and feedback-loop guidance**: added linting guidance for setup-step prerequisites, restricted-network collection-install behavior, and lint-review scope, and expanded session workflow guidance to explicitly verify lint bootstrap in agent sessions and capture durable steering/linting lessons back into the wiki.
- **OKF linting KB now captures `ansible_lint` triage order explicitly**: added CI lint guidance that workflow failures should be diagnosed from helper-test output first, before investigating ansible-lint findings, because the job can fail before linting runs.

### Security

- **Threat Model Assessment**: This change **keeps workstation malware-protection risk unchanged while reducing operational and diagnostic risk**.
    - **Rationale**: The change does not alter ClamAV package sources, scanning scope, service privileges, or quarantine behavior. It hardens login-shell execution by passing values as positional arguments (avoiding reliance on environment-variable preservation in `runuser -l`), keeps FreshClam configuration idempotent to avoid unnecessary service restarts and timestamp churn on unchanged runs, and preserves bounded log handling with resilient fallback across rotated logs and current-boot journal evidence.
    - **Benefit**: Verification remains reliable after login-shell environment scrubbing, unchanged playbook runs stay quiet, and unreadable compressed logs now produce explicit warnings while still allowing fallback to later usable evidence. This supports UK Cyber Essentials expectations for reliable protective monitoring and controlled, reviewable configuration.
    - **Net risk statement**: Net runtime protection risk is **unchanged**, while operational execution and diagnostic reliability risk are **reduced**.
    - **CI fix note**: The verifier template/render fix and configurable FreshClam log-path alignment improve reliability of protective-check execution and evidence collection; workstation runtime protection controls remain **unchanged** while operational false-failure risk is **reduced**, supporting UK Cyber Essentials expectations for dependable, reviewable security checks.
    - **Bootstrap note**: The wiki/bootstrap restructuring is documentation and agent-guidance only, so workstation runtime risk is **unchanged** while future session context-loading overhead and stale-memory reliance should be reduced.
    - **Agent setup note**: Copilot setup-step changes affect ephemeral CI/agent preparation only and do not alter workstation runtime controls; net runtime risk is **unchanged** while lint-gate reliability risk is **reduced**.
    - **Knowledge-capture note**: The new OKF wiki updates are documentation/process guidance only, so workstation runtime risk remains **unchanged** while steering consistency and future-session lint setup reliability risk are **reduced**.
    - **Lint triage note**: The CI lint KB update is documentation-only; runtime risk is **unchanged** while CI failure triage reliability risk is **reduced**.

## [PR #77 - Ensure dependencies are up to date with a 3-day cooldown policy](https://github.com/brabster/xubuntu-workstation/pull/77)

### Changed

- **GitHub Actions dependencies updated to current major releases**: Updated workflow actions from `actions/checkout@v5` to `actions/checkout@v7` and from `actions/setup-python@v6` to `actions/setup-python@v7` so CI dependencies are current.
- **Automated dependency policy added with supply-chain cooldown**: Added `.github/dependabot.yml` with a 3-day cooldown (`default-days: 3`) for `github-actions` and `pip` version updates, while still allowing Dependabot security updates to open immediately.
- **Dependency governance clarified for future automation**: Added OKF steering guidance documenting a repository preference for automated point-of-use updates gated by CI evidence, with resolved-version/SBOM evidence capture and explicit interim risk acceptance while no centralized multi-repo control plane exists.
- **PR CI coverage restored for workstation changes**: Reverted `test_install` pull-request triggering to run on all PRs so dependency/workflow updates are included without dropping validation coverage for other repository changes.

### Security

- **Threat Model Assessment**: This change **reduces supply-chain risk** while keeping workstation runtime risk unchanged.
    - **Rationale**: Moving CI actions to current maintained major versions reduces exposure to stale dependency code in the CI control plane. Applying a 3-day delay for routine version-update PRs lowers the chance of immediately ingesting newly published malicious packages or compromised releases, while security updates remain immediate. For Ubuntu packages managed through apt, this repository already relies on Canonical's signed archive and release process, so an additional repository-level cooldown is not applied there.
    - **Governance rationale**: Repository guidance now explicitly favors automated update flow with CI/test gates and recorded resolved-version evidence over per-update semver-based manual review, while acknowledging an interim risk until centralized allow/block override controls are in place.
    - **CI assurance rationale**: Keeping broad PR CI coverage reduces the chance that unrelated but security-relevant playbook regressions bypass the `test_install` gate.
    - **Benefit**: Dependency updates stay timely and controlled with an explicit anti-poisoning delay for ecosystems where cooldown is supported, aligning with UK Cyber Essentials goals for secure configuration management and controlled change.
    - **Net risk statement**: Net risk is **reduced** for CI/dependency supply chain and **unchanged** for managed workstation runtime controls.

## [PR #75 - Fix GitHub Actions Node.js 20 deprecation warning](https://github.com/brabster/xubuntu-workstation/pull/75)

### Changed

- **GitHub Actions Node runtime compatibility update**: Upgraded workflow action versions from `actions/checkout@v4` to `actions/checkout@v5` and from `actions/setup-python@v5` to `actions/setup-python@v6` so workflows no longer rely on Node.js 20-based action majors.

### Security

- **Threat Model Assessment**: This change **slightly reduces operational risk** with **no change to workstation runtime risk**.
    - **Rationale**: The update only changes CI action majors to supported Node.js 24-compatible releases and does not alter local workstation packages, privileges, or network exposure. Staying on maintained action runtimes reduces CI supply-chain and reliability risk from deprecated execution environments.
    - **Benefit**: CI remains aligned with supported GitHub runner behavior, preserving dependable validation and supporting UK Cyber Essentials expectations for controlled, repeatable change assurance.
    - **Net risk statement**: Net risk is **reduced** for CI operations and **unchanged** for managed workstation runtime behavior.

## [PR #73 - Switch Slack installation from snap to the official APT package](https://github.com/brabster/xubuntu-workstation/pull/73)

### Changed

- **Slack install path moved from snap to native APT package**: The `slack` role now adds Slack's official packagecloud APT repository using Slack's published Debian `jessie` distribution path and installs `slack-desktop` instead of using `snap install slack`.
- **Slack repository setup is intentionally minimal**: The role now verifies a vendored copy of Slack's packagecloud signing key against the expected full fingerprint before installing a dearmored keyring into `/etc/apt/keyrings/slack.gpg`, manages `/etc/apt/sources.list.d/slack.list` directly as a plain APT source file with an explicit `amd64` architecture constraint, hardcodes Slack's published `debian jessie` suite, and installs `slack-desktop` through normal apt operations.
- **Slack now runs in CI coverage again**: Because Slack is no longer installed through snap, the `slack` role is no longer skipped in GitHub Actions and is exercised as part of the normal workstation playbook path.
- **OKF wiki compatibility cleanup**: Removed the temporary `docs/wiki/okf/steering-and-reusable-knowledge.md` compatibility pointer so the new wiki uses the decomposed `steering/`, `linting/`, and `decisions/` structure directly.

### Security

- **Threat Model Assessment**: This change **keeps net workstation risk broadly unchanged while shifting the risk profile toward desktop compatibility and away from opaque repository bootstrap behavior**.
    - **Rationale**: Moving from the snap package to the native `slack-desktop` package removes snap strict-confinement protections, so a compromised Slack desktop process would have the normal access of the logged-in user rather than snap's tighter sandbox. In exchange, Slack is now installed through the vendor's published Ubuntu/Debian package channel using repository configuration expressed directly in Ansible rather than a bootstrap shell script.
    - **Benefit**: Slack should integrate more reliably with desktop workflows such as file selection and screen sharing, while updates continue to flow through the standard apt path already covered by this repository's controlled update workflow. Running the role in CI again also improves change confidence for this part of the workstation build, supporting UK Cyber Essentials expectations for repeatable, validated system configuration.
    - **Net risk statement**: Net workstation risk is **unchanged overall**: snap confinement is removed, but repository trust is now explicitly pinned and validated in Ansible while CI coverage for the Slack role is restored.
- **Threat Model Assessment (OKF wiki compatibility cleanup)**: Removing the temporary OKF compatibility pointer **does not change workstation runtime risk**.
    - **Rationale**: This is a documentation-only cleanup that removes a transitional wiki page now that the decomposed OKF structure is established. It changes contributor guidance clarity, not package sources, privileges, or runtime controls.
    - **Benefit**: Repository knowledge becomes easier to navigate and harder to duplicate, improving documentation hygiene without weakening any UK Cyber Essentials-relevant control.


## [Run ansible-lint as part of pre-commit hook and in CI build](https://github.com/brabster/xubuntu-workstation/pull/71)

### Added

- **Ansible linting gate in local hooks and CI**: Added a native git hook at `.githooks/pre-commit` and `.github/workflows/ansible_lint.yml` so local checks (when scoped Ansible files are staged) and CI both run `ansible-lint` against the full scoped targets (`roles/`, `workstation.y*ml`, `test.y*ml`).
- **Shared lint dependency pin**: Added `requirements-dev.txt` so local setup and CI install the same `ansible-lint` version from one place, with straightforward dependency updates.
- **Complexity reduction for lint execution**: Removed changed-file selection logic from the lint execution path; linting now runs over the fixed scoped targets for simpler, more predictable behavior.
- **Hook behavior coverage retained**: Added focused tests for the native git hook fixed-target behavior (`tests/test_pre_commit_hook.py`) and run them in CI before lint execution.
- **ADR decision finalized**: Updated `docs/adr/0001-lint-tooling-approach.md` to accepted status and documented the selected lower-dependency approach, with explicit revisit criteria if issues emerge.
- **OKF-style wiki bootstrap for agents**: Added `docs/wiki/okf/README.md` and `docs/wiki/okf/steering-and-reusable-knowledge.md` to capture session steering and reusable repository knowledge, and updated `AGENTS.md` so agents review this wiki seed on session start.
- **OKF v0.2 conformance alignment for wiki seed**: Added `docs/wiki/okf/index.md` with `okf_version: "0.2"` and added concept frontmatter metadata to non-reserved wiki markdown files so the local wiki proposal matches the uploaded OKF v0.2 structure more closely.
- **OKF concept decomposition and linking model**: Replaced the single combined steering page with topic-grouped concept documents under `docs/wiki/okf/steering/`, `docs/wiki/okf/linting/`, and `docs/wiki/okf/decisions/`, each connected via reserved `index.md` navigation and cross-links between related concepts.
- **Wiki change history support**: Added `docs/wiki/okf/log.md` at wiki root for dated update tracking using OKF `log.md` conventions.
- **Baseline lint compliance updates**: Resolved outstanding ansible-lint findings across scoped targets, including role rename to `chrome_browser`, role-local variable prefix fixes, FQCN/import updates, safer file permission declarations, idempotency metadata, and YAML hygiene fixes in affected playbooks and role task files.

### Security

- **Threat Model Assessment**: This change **reduces risk** by preventing non-linting Ansible from being merged.
    - **Rationale**: Linting catches unsafe or error-prone Ansible patterns earlier in the development lifecycle, reducing configuration mistakes that could weaken workstation security controls.
    - **Benefit**: Improves change quality and consistency for automation that underpins security posture, supporting UK Cyber Essentials expectations for controlled, repeatable configuration management, while reducing local tooling supply-chain surface and simplifying lint execution paths.
    - **Net risk statement**: For runtime package behavior, risk is **unchanged to slightly reduced** because the Chrome ALSA preinstall compatibility task now checks package availability before install, reducing failure risk from hard-coded release assumptions.
    - **Supply-chain note**: Chrome installation still relies on downloading the vendor `.deb` directly over TLS as in prior versions; this PR does not change that trust model, so supply-chain risk in that path remains **unchanged**.
    - **Documentation/control note**: The OKF wiki addition, decomposition, and v0.2 conformance alignment change guidance quality, not runtime behavior; net runtime risk is **unchanged**, while decision-traceability, discoverability, and consistency are improved.

## [Fix remote_tmp warning](https://github.com/brabster/xubuntu-workstation/pull/69)

### Fixed

- **Ansible remote_tmp mode 0700 warning**: Added a `pre_tasks` block to `workstation.yml` that pre-creates `~{{ username }}/.ansible/tmp` (the default `remote_tmp` path) with mode `0700` and the correct owner before any `become_user` task runs. Ansible only emits the warning when it must create the directory itself; pre-creating it with the right ownership and permissions eliminates the warning entirely, which is the approach recommended by Ansible's own warning message.

### Security

- **Threat Model Assessment**: This change **does not change the risk** for the managed workstation.
    - **Rationale**: The `~/.ansible/tmp` directory is still created with mode `0700`, owned by the target user — identical to what Ansible would create. Pre-creating it with explicit ownership ensures the directory belongs to the correct user from the start. No secrets are exposed and no permissions are weakened. The fix does not affect any control required by UK Cyber Essentials.
    - **Benefit**: Eliminates a warning that could obscure genuine issues in playbook output, improving signal-to-noise ratio in both CI and manual runs.
## [Fix updates role Ansible fact deprecation warning](https://github.com/brabster/xubuntu-workstation/pull/66)

### Fixed

- **Deprecated fact reference in sudoers update task**: Replaced `ansible_hostname` with `ansible_facts["hostname"]` in `roles/updates/tasks/main.yml` to align with ansible-core deprecation guidance and avoid reliance on top-level fact injection (`INJECT_FACTS_AS_VARS`).

### Security

- **Threat Model Assessment**: This change **slightly reduces operational risk** and does not change workstation privilege boundaries.
    - **Rationale**: The `updates` role manages privileged update access (`/etc/sudoers`). Removing deprecated fact usage prevents future ansible-core behavior changes from silently breaking this automation path.
    - **Benefit**: Keeps security update workflows reliable over ansible-core upgrades, supporting UK Cyber Essentials intent for timely, dependable patching processes.
## [Make cleanup_services idempotent after avahi-daemon removal](https://github.com/brabster/xubuntu-workstation/pull/63)

### Fixed

- **Repeat setup runs after service removal**: The `cleanup_services` role now skips stop/disable actions when `service_facts` reports `not-found` for `avahi-daemon.service` or `ModemManager.service`. This prevents reruns failing after the packages were already removed on a previous run.

### Security

- **Threat Model Assessment**: This change **keeps net risk unchanged** while improving reliability of the hardening workflow.
    - **Rationale**: The role still removes unnecessary services and packages to reduce exposed functionality. The update only prevents failures when units are already absent, preserving least-functionality controls expected by UK Cyber Essentials.
    - **Benefit**: Re-running setup remains safe and repeatable without weakening existing service-removal protections.

## [Fix ISO signature verification by using Ubuntu archive keyring](https://github.com/brabster/xubuntu-workstation/pull/61)

### Fixed

- **ISO verification public key failure**: `download_verified_iso.sh` now verifies `SHA256SUMS.gpg` with the system Ubuntu archive keyring (`/usr/share/keyrings/ubuntu-archive-keyring.gpg`) instead of the caller's personal GPG keyring. This resolves `gpg: Can't check signature: No public key` when validating current Xubuntu release images.

### Security

- **Threat Model Assessment**: This change **reduces risk** in installation media verification while preserving existing trust boundaries.
    - **Rationale**: Verifying against the explicit, distro-managed Ubuntu archive keyring prevents false verification failures caused by missing user keyring state, and avoids ad-hoc key imports from keyservers that can increase supply-chain and trust-on-first-use risk.
    - **Benefit**: ISO authenticity checks are now reliable on clean systems where `ubuntu-keyring` is installed, improving integrity assurance for bootstrap media and supporting UK Cyber Essentials expectations for using trusted software sources and verification.

## [Set up a minimal devcontainer image](https://github.com/brabster/xubuntu-workstation/pull/58)

### Added

- **Devcontainer configuration**: Added `.devcontainer/Dockerfile` and `.devcontainer/devcontainer.json` to support development of this project in a GitHub Codespace. The image extends `mcr.microsoft.com/devcontainers/base:ubuntu` and pre-installs `ansible` and `ansible-lint`, providing the minimum tooling needed to edit roles, run linting (`ansible-lint workstation.yml`), and test in check mode (`ansible-playbook --check`).

### Security

- **Threat Model Assessment**: This change has a **small net reduction in contributor setup risk** and **no change to managed workstation runtime risk**.
    - **Rationale**: Using the official Microsoft devcontainers base image (`mcr.microsoft.com/devcontainers/base:ubuntu`) ensures a maintained, trusted foundation with a non-root user by default, reducing privilege-escalation risk in the development environment. Only `ansible` and `ansible-lint` are added on top, and no secrets or credentials are embedded.
    - **Benefit**: Contributors can develop and validate Ansible roles in an isolated, reproducible container without needing to configure a local environment manually. This reduces the risk of environment-specific configuration drift and accidental changes to a developer's own system while leaving production and workstation security controls unchanged.


## [Prevent GitHub Actions from running on documentation changes](https://github.com/brabster/xubuntu-workstation/pull/55)

### Changed

- **CI path filtering added**: The `push` trigger in `.github/workflows/test_install.yml` now uses `paths-ignore` to skip CI runs when only documentation and meta files are changed (`**/*.md`, `prompts/**`, `.vars_example.yml`). The `workflow_dispatch` and `schedule` triggers are unaffected and continue to run unconditionally.

### Security

- **Threat Model Assessment**: This change **does not affect workstation runtime configuration or security posture**.
    - **Rationale**: Running the full CI suite on every documentation commit wastes compute resources and adds noise without providing any validation signal, since documentation files are not exercised by the Ansible playbook tests.
    - **Benefit**: CI runs remain reliable and fast for changes that matter; documentation-only commits no longer consume runner minutes unnecessarily. This does not weaken any control required by UK Cyber Essentials, as the CI validation suite is unchanged.

## [Disable DNS over TLS to restore name resolution when using NordVPN](https://github.com/brabster/xubuntu-workstation/pull/54)

### Fixed

-   **DNS resolution broken when using NordVPN**: `DNSOverTLS=yes` has been removed from the Cloudflare for Families `systemd-resolved` configuration. DNS over TLS (DoT) requires a direct TLS connection to Cloudflare on port 853, which NordVPN intercepts and breaks, causing name resolution to fail entirely while the VPN is active.

### Security

-   **Threat Model Assessment**: This change **removes DNS over TLS (DoT) from the Cloudflare for Families configuration** to restore compatibility with NordVPN.
    -   **Rationale**: DoT provides transport-layer encryption for DNS queries, protecting against eavesdropping on the local network path to the resolver. However, when NordVPN is active it routes all DNS traffic through its own encrypted tunnel, so DoT's protection is effectively duplicated. Enabling DoT simultaneously causes TLS handshake failures to port 853, breaking DNS for all applications.
    -   **Benefit**: DNS resolution is reliable whether or not NordVPN is in use. The Cloudflare for Families content-filtering DNS servers (blocking malware and adult content) remain in effect. When NordVPN is connected, DNS traffic is protected by the VPN tunnel, maintaining confidentiality without requiring DoT. This aligns with UK Cyber Essentials requirements for a functioning, consistently available network configuration.

## [Set up Copilot coding agent instructions](https://github.com/brabster/xubuntu-workstation/pull/53)

### Added

- **Repository Copilot instructions**: Added `.github/copilot-instructions.md` to define secure and stable coding-agent defaults, faster validation feedback loops, and explicit prompting-quality guidance (including suggesting prompt improvements when interactions are inefficient).

### Security

- **Threat Model Assessment**: This change **improves delivery safety and consistency without changing workstation runtime configuration**.
    - **Rationale**: Standardized agent instructions reduce the risk of unsafe automation suggestions (for example unnecessary privilege escalation or weak provenance practices), and reinforce evidence-first diagnostics before remediation.
    - **Benefit**: Improves alignment with UK Cyber Essentials intent by reinforcing secure change behaviour, traceable security rationale, and reliable validation practices in repository contributions.

## [Ubuntu 26.04 compatibility: fix Chrome install on rolling release](https://github.com/brabster/xubuntu-workstation/pull/52)

### Fixed

- **Chrome installation on Ubuntu 26.04+**: Google Chrome's `.deb` package declares a dependency on `libasound2 (>= 1.0.17)`, but in Ubuntu 24.04 the ALSA sound library was renamed to `libasound2t64` as part of the 64-bit `time_t` transition. In Ubuntu 26.04, `libasound2t64` no longer provides `libasound2` as a virtual package, making the dependency unsatisfiable and blocking Chrome installation. The `chrome-browser` role now pre-installs `libasound2t64` (with a cache refresh) before installing Chrome, which satisfies the runtime library requirement and allows the plain `apt install` of Chrome to succeed.

### Security

- **Threat Model Assessment**: This change **maintains the existing security posture** while restoring Chrome installation on the latest Ubuntu rolling release.
    - **Rationale**: Without this fix, Chrome could not be installed on Ubuntu 26.04, leaving users without a managed, policy-controlled browser. Pre-installing `libasound2t64` is a minimal, targeted change that ensures the required ALSA shared library is present before Chrome is installed.
    - **Benefit**: Chrome's managed policy configuration (enforced HTTPS, Safe Browsing, download restrictions) remains fully applied on Ubuntu 26.04, maintaining the browser security controls required for UK Cyber Essentials compliance. Chrome updates via Google's apt repository (registered automatically by the Chrome installer) remain unaffected.

## [Disable and remove unneeded services by default](https://github.com/brabster/xubuntu-workstation/pull/45)

Fixes on [PR#46](https://github.com/brabster/xubuntu-workstation/pull/46).

### Added

- **Unnecessary services disabled and removed**: The cleanup role now disables the ModemManager and avahi-daemon services and removes the associated packages by default. This ensures the services are not running after reboot and the packages are not present unless explicitly required.

### Security

- **Threat Model Assessment**: This change **reduces the attack surface and supports compliance with UK Cyber Essentials requirements**.
    - **Rationale**: Services are not required for most workstation use cases and represents an unnecessary service and software package. Disabling and removing it aligns with the principle of least functionality, as mandated by UK Cyber Essentials, and reduces the risk of exploitation via unused system components.
    - **Benefit**: Ensures only necessary services are present and running, improving overall system security and regulatory compliance.

## [Enable UFW Firewall by Default](https://github.com/brabster/xubuntu-workstation/pull/44)

### Added

-   **UFW Firewall Enabled and Running After Reboot**: The UFW role now ensures UFW is installed, enabled, and started on boot. This can be selectively enabled or disabled for different environments.

### Security

-   **Threat Model Assessment**: This change **significantly improves the system’s network security posture and facilitates compliance with UK Cyber Essentials requirements**.
    -   **Rationale**: Enabling UFW by default ensures that only explicitly allowed network traffic is permitted, reducing exposure to remote attacks and unauthorized access. UK Cyber Essentials mandates a properly configured firewall as a baseline control for all internet-connected devices.
    -   **Benefit**: The firewall acts as a first line of defense against network-based threats, especially important for systems exposed to untrusted networks. Automating its activation and persistence across reboots eliminates the risk of accidental misconfiguration or firewall downtime, and ensures the system meets regulatory requirements for basic cyber hygiene.

## Fixes and security improvement to ClamAV on-access setup

- [PR#39](https://github.com/brabster/xubuntu-workstation/pull/39)
- [PR#32](https://github.com/brabster/xubuntu-workstation/pull/32)
- [PR#31](https://github.com/brabster/xubuntu-workstation/pull/31)

### Changed

- **Disable NordVPN killswitch by default**: unable to login without network access. Updated post-install messaging to remind user.
- **Modern, lower-risk approach to ClamAV on-access scanning**: switch from `clamd` to `clamonacc` service performing the file quaratine operation, to avoid elevating privileges of `clamd` that scans potentially malicious code.

### Security

- **NordVPN killswitch off by default**: no change to threat model, as killswitch must be disabled to log in.
- **clamonacc performs quarantine**: reduces the risk of infection, by reducing the permissions of the riskier `clamd` service.

## [Configure NordVPN](https://github.com/brabster/xubuntu-workstation/pull/30)

### Added

-   **Opinionated NordVPN Configuration**: The `nordvpn` role now automates post-installation configuration to enforce secure defaults. This includes enabling the `threatprotectionlite` feature.

### Security

-   **Threat Model Assessment**: This change **reduces the risk of malware infection**. The addition of threat protection blocks malicious websites at the DNS level. Automating these settings ensures a consistent and secure baseline, mitigating risks associated with manual configuration.

## [Automate ISO download and signature verification](https://github.com/brabster/xubuntu-workstation/pull/29)

### Added

-   **Automated ISO Download and Verification**: Introduced a new script to securely download the latest Xubuntu ISO and verify its integrity using SHA256 checksums. This ensures the base operating system image is authentic and has not been tampered with.

### Security

-   **Threat Model Assessment**: This feature **improves the security and integrity of the initial installation media**. By automating the verification of the ISO, it mitigates the risk of installing a compromised or corrupt operating system, which is a critical step in establishing a secure baseline.

## [Fix Ansible lint errors](https://github.com/brabster/xubuntu-workstation/pull/28)

### Fixed

-   **Ansible Linting Errors**: Resolved all linting issues reported by `ansible-lint`. This improves the overall quality and maintainability of the Ansible automation code.

### Security

-   **Threat Model Assessment**: This change has **no direct impact on the threat model** of the deployed workstation. It is a maintenance update focused on code quality, which indirectly supports security by ensuring the automation is robust and predictable.

## [Add ClamAV on-access scanning](https://github.com/brabster/xubuntu-workstation/pull/27)

### Added

-   **On-Access AV Scanning**: Implemented real-time, blocking antivirus scanning for the `~/Downloads` directory using ClamAV and `fanotify`.
-   **Automated Quarantine & Notification**: Infected files are now automatically moved to a quarantine folder (`~/Downloads/.quarantine`), and a desktop notification is sent to the user.

### Security

-   **Threat Model Assessment for On-Access Scanning**: This feature represents a **significant improvement in overall security posture**.
    -   **Rationale**: The shift from manual-only scanning to real-time, blocking on-access scanning drastically reduces the window of vulnerability for malware entering via the `~/Downloads` directory. By using the kernel's `fanotify` capabilities, the system prevents any access to a new file until it is confirmed to be safe.
    -   **Benefit**: This proactive and automated threat containment mechanism significantly lowers the risk of accidental malware execution by the user, providing a much more robust defense against common threat vectors.

## [Passwordless sudo for update script](https://github.com/brabster/xubuntu-workstation/pull/26)

### Added

-   **Passwordless `sudo` for Update Script**: The `update` script can now be executed via `sudo update` without requiring a password, making routine system maintenance more convenient. (#26)

### Security

-   **Threat Model Assessment for Passwordless Updates**: A threat model assessment was conducted for the passwordless `sudo` feature. The conclusion is that this change represents a **net decrease in overall risk**. (#26)
    -   **Rationale**: While it introduces a minor theoretical risk (an attacker with user-level access can trigger a system update), this is heavily mitigated because the script itself is owned by `root` and cannot be modified by the user.
    -   **Benefit**: The removal of friction for a routine, safe task encourages more frequent system updates. This tangible improvement in security posture outweighs the minor introduced risk.
