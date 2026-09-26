---
type: Playbook
title: Vendor repo diagnostics
description: Validate third-party package repository configuration from CI logs and vendor-published package metadata, not from repository addition alone.
tags: [steering, diagnostics, package-management]
---

# Vendor repo diagnostics

- For third-party package repositories, inspect GitHub Actions logs first when installs fail in CI.
- Treat "repository added successfully" as necessary but not sufficient evidence; it does not prove the package exists in the configured suite or path.
- Compare the configured repository URI, suite, and package name against the vendor's published package index or generated config output.
- Prefer CI-tested repository paths over inferred distro mappings when the vendor publishes a surprising alias or compatibility path.
- Document any non-obvious repository path or suite choice in the wiki and changelog so future maintainers do not rediscover it.

Checklist:
- verify the published repository path
- verify the package name is available from that path/suite
- prefer CI-tested paths over inferred distro mappings
- document surprising distribution aliases in the wiki/changelog

Related concepts:
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
- [Slack package source](../decisions/slack-package-source.md)
