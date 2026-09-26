# ADR 0001: Local lint hook and version management approach

- Status: Accepted
- Date: 2026-09-26
- Related PR: [#71](https://github.com/brabster/xubuntu-workstation/pull/71)

## Context

This repository now lint-gates the full scoped Ansible target set in CI and also provides local lint checks before commit when scoped Ansible files are staged.
Recent discussion requested a comparison between:

1. Previous approach:
   - pre-commit manages local hook wiring and hook definition
   - CI installs a pinned ansible-lint version and enforces checks on changed scoped files
2. Alternative approach:
   - put linter version in `requirements.txt` or `pyproject.toml` as a single source of truth for local and CI
   - remove the pre-commit package
   - use a standard `.git/hooks/pre-commit` script and README setup instructions
   - optionally add VSCode task/sync automation for developer convenience

## Decision

Adopt the lower-dependency local setup model now, and revisit only if developer experience or reliability issues appear:

- Manage `ansible-lint` version in normal Python dependency management (`requirements.txt` or `pyproject.toml`)
- Keep CI as the central enforcement gate
- Replace pre-commit package dependency with a standard git hook script and explicit setup instructions

Implementation for this repository uses `requirements-dev.txt` plus `.githooks/pre-commit`, and runs lint over the full scoped targets (`roles/`, `workstation.y*ml`, `test.y*ml`) rather than changed-file selection.

## Options compared

### Option A: Keep pre-commit package + current CI pin

Pros
- Standardized hook runner with broad ecosystem support
- Easy to add more hooks in future with consistent UX
- Good portability across contributor environments

Cons
- Adds one extra tool dependency and update surface
- Version source can become split if CI pin and pre-commit hook revision diverge
- Some repository-specific glue may be needed when aligning behavior across local/CI

### Option B: Use requirements/pyproject version + native git hook + CI enforcement

Pros
- Single obvious place for ansible-lint version; easy for automation such as Dependabot
- Fewer moving parts than maintaining a pre-commit toolchain
- CI remains the central, authoritative merge gate

Cons
- Native git hooks are not cloned by default and require explicit developer setup
- Hook behavior can drift if contributors do not install hooks locally
- Cross-platform hook scripting and lifecycle management is manual

## Consequences

- Positive:
  - Reduced tooling complexity and supply-chain surface for local hook execution
  - Clearer version management path when updating ansible-lint
  - Further reduced complexity by removing diff-based file selection logic from both local hook and CI
- Negative:
  - More responsibility on repository docs/scripts to ensure local git hook installation is performed consistently
- Neutral:
  - CI lint gate remains the key control, so merge protection behavior is unchanged
  - Revisit trigger: if hook setup friction, drift, or platform issues become recurring, reassess pre-commit or alternative tooling.

## Security and compliance assessment

- Threat model net change: **unchanged** for merged code assurance as long as CI remains required.
- Rationale:
  - CI still enforces ansible-lint checks before merge, which is the primary control.
  - Local hook ergonomics affect early feedback quality more than final enforcement.
- UK Cyber Essentials impact:
  - No direct change to workstation runtime controls.
  - Supports controlled, repeatable change validation through CI-gated checks.
