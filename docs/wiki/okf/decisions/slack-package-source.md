---
type: Reference
title: Slack package source
description: Summary of the repository decision to install Slack from Slack's packagecloud APT repository instead of snap.
tags: [decisions, slack, package-management]
resource: ../../../../roles/slack/tasks/main.yml
---

# Slack package source

- Decision status: accepted.
- Selected approach: install Slack from Slack's packagecloud APT repository and install `slack-desktop`; do not use the snap package in this repository.
- Verified published path: use `https://packagecloud.io/slacktechnologies/slack/debian/` with suite `jessie`, even on recent Ubuntu releases.
- Evidence basis: this was validated from CI failure analysis after the Ubuntu-codename packagecloud path added successfully but did not expose `slack-desktop` to apt.
- Implementation note: manage `/etc/apt/sources.list.d/slack.list` directly so Ansible owns the same source file path Slack's package hooks may touch after install, keep the repository definition explicit in versioned configuration, and verify a vendored copy of the packagecloud public key against the expected full fingerprint before use.
- Stability note: live key fetches can fail in CI even when the repository itself is reachable, so vendoring the public key is an acceptable stability trade-off here because the full fingerprint is pinned and validated in the role.
- Supply-chain note: vendoring the public key is only acceptable with explicit fingerprint validation and clear provenance; do not replace one opaque bootstrap path with another.

Canonical sources:
- [Slack role tasks](../../../../roles/slack/tasks/main.yml)
- [Vendored Slack packagecloud key](../../../../roles/slack/files/slack-packagecloud.asc)
- [PR #73 changelog entry](../../../../CHANGELOG.md)

Related concepts:
- [Vendor repo diagnostics](../steering/vendor-repo-diagnostics.md)
- [Recent-Ubuntu simple paths](../steering/recent-ubuntu-simple-paths.md)
- [Cost-tiered agent selection](../steering/cost-tiered-agent-selection.md)
