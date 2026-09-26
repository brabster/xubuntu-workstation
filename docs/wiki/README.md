---
type: Reference
title: OKF Wiki Overview
description: Scope, purpose, and update policy for this repository's OKF-style wiki seed.
tags: [okf, wiki, steering]
generated: { by: github-copilot/coding-agent, at: 2026-09-26T20:54:32Z }
stale_after: 2027-03-26T00:00:00Z
---

# OKF Wiki Overview

This directory is the repository's working OKF-style wiki for agent and contributor bootstrap.

## Bootstrap model

- always-read bootstrap pages should stay minimal:
  - root navigation (`index.md`)
  - this overview (`README.md`)
  - [agent bootstrap rules](./steering/agent-bootstrap-rules.md)
  - [session workflow](./steering/session-workflow.md)
- other steering, linting, and decision pages are lookup-on-demand reference material
- avoid preloading the whole wiki tree unless a task genuinely depends on it

## Purpose

- capture steering from active sessions
- preserve reusable, generalisable repository knowledge
- reduce repeated debate on already-settled trade-offs
- keep future agent runs aligned with current operating intent

## Structure

- [Root index](./index.md): top-level navigation for progressive disclosure.
- [Steering](./steering/): playbooks describing operating principles.
- [Linting](./linting/): lint toolchain behavior and controls.
- [Decisions](./decisions/): ADR-backed decision summaries, while canonical ADR records remain in `docs/adr/` so their status, date, and PR context stay in a conventional ADR location.
- [Specification reference](./okf_spec_v0.2.md): imported OKF v0.2 reference from GoogleCloudPlatform/open-knowledge-format.

## Memory versus wiki

- the wiki is the primary repository knowledge system
- Copilot memory should be sparse and complementary:
  - durable user preferences
  - a few expensive-to-rediscover facts
- repository rules, workflow, examples, and decision rationale should live in versioned wiki pages, not in broad memory injection

## Authoring rules (OKF v0.2 aligned)

- non-reserved `.md` files are concept documents and include YAML frontmatter with at least a non-empty `type`
- non-reserved concept documents should also record `generated.by`, `generated.at`, and `stale_after` so authorship and review freshness stay queryable in frontmatter
- reserved filenames `index.md` and `log.md` follow OKF section structures when present
- root `index.md` may include only `okf_version` frontmatter
- prefer links to canonical concepts over duplicate prose

## Update policy

- add only durable, reusable knowledge
- prefer evidence-backed statements over assumptions
- keep entries short, practical, and action-oriented
- keep workflow guidance aligned with review tooling expectations, including checking that merge request descriptions still match the agreed approach after material changes
- when a decision changes, update the wiki entry and link the relevant ADR/PR
- add new canonical guidance in the decomposed section pages (`steering/`, `linting/`, `decisions/`)
- use git history and `CHANGELOG.md` as the default change record for wiki updates; add a dedicated `log.md` only when a subtree needs extra human-written scope history beyond what normal repository history provides
