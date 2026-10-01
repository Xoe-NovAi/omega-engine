<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Soul Distillation Pipeline — Deep Research
**AP Token**: `AP-SOUL-DISTILLATION-20260726`
**Date**: 2026-07-26 | **Priority**: P0 — Core to M5/M11
**Researcher**: Sovereign Researcher

---

## Executive Summary

The L1→L2→L3 distillation pipeline design exists conceptually but the **session hook** (triggering distillation on session close), the **proposed_lessons.yaml blind staging pattern**, and the **Scribe agent** execution are not fully wired.

## Pipeline Architecture

```
Session Ends
    │
    ▼
┌─────────────────────────┐
│ Session Hook (trigger)  │ ← opencode.json hooks or post-session callback
│ oracle.close_session()  │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ L1 Capture (narrative)  │ ← What happened in this session?
│ exchanges.jsonl          │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ L2 Insight (meaning)    │ ← What does this mean?
│ Extract key findings    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ L3 Principle (truth)    │ ← What is the timeless truth?
│ Universal abstraction   │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Staging Gate            │ ← Blind staging (no entity context)
│ proposed_lessons.yaml   │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ User/Scribe Approval    │ ← Vet before promotion
│ approved_lessons.yaml   │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Soul Write              │ ← Merged into soul.yaml
│ soul.yaml               │
└─────────────────────────┘
```

## Current State

| Component | Status | File |
|-----------|--------|------|
| Session hook | ✅ Registered in opencode.json | .opencode/opencode.json |
| L1 Capture | ✅ MemoryStore persists exchanges | memory_store.py |
| L2 Insight | 🟡 Manual extraction | distiller.py |
| L3 Principle | 🟡 Manual extraction | distiller.py |
| Staging gate | ✅ proposed_lessons.yaml | soul_store.py |
| Scribe agent | 🟡 Designed, not implemented | scribe/ |
| User approval | ❌ Not wired | — |
| Soul write | ✅ SoulStore.write_atomic() | soul_store.py |

## Key Gaps

1. **Session hook reliability**: The hook must fire reliably even on crashes. Current implementation depends on OpenCode's post-session callback.
2. **L2→L3 extraction quality**: Current extraction is manual/LLM-based. Need quality gate before promotion.
3. **Cross-entity learning**: L3 principles from one entity should cross-pollinate to related entities (R-31).
4. **Privacy sanitization**: L3 principles going to git-tracked soul.yaml must strip PII (soul privacy model).

## Implementation Plan

| Phase | Task | Effort |
|-------|------|--------|
| 1 | Verify session hook fires on all exit paths | 2h |
| 2 | Build Scribe agent (L1→L2→L3 extraction) | 8h |
| 3 | Add staging gate (proposed_lessons.yaml blind staging) | 4h |
| 4 | Add privacy sanitization before L3 promotion | 3h |
| 5 | Wire cross-entity learning (embedding proximity) | 4h |
| **Total** | | **~21h** |
