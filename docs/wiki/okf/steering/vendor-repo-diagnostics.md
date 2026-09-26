---
type: Playbook
title: Vendor repo diagnostics
description: Validate third-party package repository configuration from CI logs and vendor-published package metadata, not from repository addition alone.
tags: [steering, diagnostics, package-management]
---

# Vendor repo diagnostics

- For third-party package repositories, inspect GitHub Actions logs first when installs fail in CI.
- Treat "repository added successfully" as necessary but not sufficient evidence; it does not prove the package exists in the configured suite or path.
- Treat "repository reachable" and "key URL reachable" as necessary but not sufficient evidence; they do not prove the fetched content is valid package metadata or valid OpenPGP key material.
- Compare the configured repository URI, suite, and package name against the vendor's published package index or generated config output.
- Prefer CI-tested repository paths over inferred distro mappings when the vendor publishes a surprising alias or compatibility path.
- If local network access is blocked or flaky, offer to generate a Gemini prompt so web-enabled research can verify vendor documentation and published metadata cheaply before implementation.
- Document any non-obvious repository path or suite choice in the wiki and changelog so future maintainers do not rediscover it.

Checklist:
- verify the published repository path
- verify the package name is available from that path/suite
- verify fetched key material is valid OpenPGP data before trusting it
- prefer CI-tested paths over inferred distro mappings
- document surprising distribution aliases in the wiki/changelog

Related concepts:
- [Evidence-first diagnostics](./evidence-first-diagnostics.md)
- [Slack package source](../decisions/slack-package-source.md)
