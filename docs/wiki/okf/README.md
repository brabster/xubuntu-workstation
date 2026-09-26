---
type: Reference
title: OKF Wiki Overview
description: Scope, purpose, and update policy for this repository's OKF-style wiki seed.
tags: [okf, wiki, steering]
---

# OKF Wiki Overview

This directory is the repository's working OKF-style wiki for agent and contributor bootstrap.

## Purpose

- capture steering from active sessions
- preserve reusable, generalisable repository knowledge
- reduce repeated debate on already-settled trade-offs
- keep future agent runs aligned with current operating intent

## Structure

- [Root index](./index.md): top-level navigation for progressive disclosure.
- [Steering](./steering/): playbooks describing operating principles.
- [Linting](./linting/): lint toolchain behavior and controls.
- [Decisions](./decisions/): ADR-backed decision summaries.
- [Specification reference](./okc_spec.md): local OKF v0.2 reference.
- [Update log](./log.md): dated history of wiki-level changes.

## Authoring rules (OKF v0.2 aligned)

- non-reserved `.md` files are concept documents and include YAML frontmatter with at least a non-empty `type`
- reserved filenames `index.md` and `log.md` follow OKF section structures
- root `index.md` may include only `okf_version` frontmatter
- prefer links to canonical concepts over duplicate prose

## Update policy

- add only durable, reusable knowledge
- prefer evidence-backed statements over assumptions
- keep entries short, practical, and action-oriented
- when a decision changes, update the wiki entry and link the relevant ADR/PR
- add new canonical guidance in the decomposed section pages (`steering/`, `linting/`, `decisions/`), not in the legacy compatibility pointer
