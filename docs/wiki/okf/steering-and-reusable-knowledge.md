---
type: Playbook
title: Steering and Reusable Knowledge
description: Session steering decisions and reusable repository knowledge for future contributors and agents.
tags: [okf, steering, reusable-knowledge]
---

# Steering and Reusable Knowledge

## Steering captured from this session

### S1. Prefer lower dependency count by default
- choose the simpler path with fewer third-party tools unless evidence shows it is insufficient
- revisit if reliability or developer-experience issues appear
- current example: native git hook + shared dependency pin instead of pre-commit toolchain

### S2. Prefer full-scope linting when baseline is clean
- linting full scoped targets (`roles/`, `workstation.y*ml`, `test.y*ml`) simplifies logic and removes diff edge cases
- changed-file selection is acceptable only when needed for incremental adoption

### S3. CI is the central enforcement gate
- local hooks are fast-feedback ergonomics, not the final control
- merge safety is provided by required CI checks

### S4. Use cheaper agents for broad scan tasks
- for low-risk discovery (for example, collecting lint failures), use a lower-cost agent/model first
- reserve higher-context/manual work for remediation and integration steps

## Reusable repository knowledge

### K1. Lint toolchain source of truth
- ansible-lint version is pinned in `requirements-dev.txt`
- CI and local setup install from that file

### K2. Local lint hook behavior
- hook path: `.githooks/pre-commit`
- hook runs only when scoped Ansible files are staged
- when it runs, it lints the full scoped targets offline

### K3. CI lint behavior
- workflow: `.github/workflows/ansible_lint.yml`
- runs ansible-lint offline on full scoped targets
- runs focused hook tests before linting

### K4. Compatibility and risk handling pattern
- where distro package naming diverges, prefer explicit compatibility handling with clear fallback logic
- document security trade-offs and net risk changes in changelog entries

## When to revisit these decisions

- lint runtime becomes materially slow for normal contributor workflow
- false positives/noise from full-scope linting significantly degrades productivity
- native hook setup friction appears repeatedly across contributors/environments
- supply-chain posture or compliance constraints require a different toolchain
