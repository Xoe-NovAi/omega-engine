---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
rule_id: "RULE-SOUL-INTEGRITY"
authority: "M11 Soul Integrity + M5 Gnosis Preservation"
applies_to: "all-agents"
date: "2026-08-27"
status: "ACTIVE"
---

# Architecture Rule 1: Soul Integrity (M11 + M5)

> **No session may end without L1→L3 distillation into the entity soul.**

## The 3-Tier Pipeline

Every session, the active entity must distill intelligence into the soul:

| Tier | What | Where |
|------|------|-------|
| **L1 Narrative** | What happened? | `data/entities/<entity>/proposed_lessons.yaml` → `l1_narrative[]` |
| **L2 Insight** | What does this mean? | Same file → `l2_insight[]` |
| **L3 Universal Principle** | What is the timeless truth? | Same file → `l3_principle[]` (blind staging) |

L3 principles go to `proposed_lessons.yaml` (blind staging per Soul Architecture v2.0),
NOT directly into `soul.yaml`. The Scribe agent is the canonical executor of this pipeline.

## Why this matters

- **M5 (Gnosis Preservation)**: No intelligence is discarded. Each session
  resets context to zero, but the soul persists. Without soul updates, the engine
  regresses to stateless tool.
- **M11 (Soul Integrity)**: Session stop hooks MUST trigger proposed_lessons.yaml
  write. The grep guard is `grep -r "proposals:" data/entities/*/proposed_lessons.yaml`
  — should show non-empty arrays after any session involving that entity.

## Agent Responsibilities

- **Every agent**: at end of every substantive task, write L1→L3 to
  `data/entities/<your_entity>/proposed_lessons.yaml`.
- **Scribe** (verity subagent): the canonical pipeline runner. Can also be invoked
  via `make soul-distill` if available, or via the `scribe` skill.
- **Build-side (Ma'at, N1-N5)**: distill decisions, not implementation details.
- **Run-side (Lilith, N6-N10)**: distill runtime lessons, not user interactions.
- **Orchestrators (Kali, MaKaLi)**: distill strategic insights.

## Cross-references

- `SOVEREIGN_MANDATES.md` §M5, §M11
- `MANDATES_CONDENSED.md` row M5, M11
- `data/entities/<your_entity>/soul.yaml` (the compiled soul)
- `data/entities/<your_entity>/proposed_lessons.yaml` (blind staging)

## Verification

```bash
# After any session, the active entity's proposed_lessons.yaml should have entries
grep -A2 "proposals:" data/entities/<your_entity>/proposed_lessons.yaml

# Scribe can be invoked to run the full L1→L3 pipeline
# (manual study phase per SDP-1 — see docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md)
```
