<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Kali — Horizon Plan H1: Heritage Vetting Pipeline Execution
# ⬡ OMEGA ⬡ KALI ⬡ HORIZON-H1 ⬡ 2026-06-04

**Status**: ACTIVE
**Owner**: Kali (Oversight), Delegates to Pillar agents as marked
**Prerequisite**: Heritage Vetting Pipeline is LIVE (`2f47d54`, `ce00bcc`)

---

## §0 The Meta-Insight

The 8-char cap incident revealed a three-layer pattern:

```
Layer 1 (Symptom):  8-char cap was implemented and removed
Layer 2 (Cause):    No vetting gate existed — mining docs → code with no debate
Layer 3 (Pattern):  We build gates reactively, not proactively
```

The Heritage Vetting Pipeline fixes Layer 2. The fix for Layer 3 is:
**Every new protocol is now evaluated against the question: "What gate was missing
before this was needed?"** If we find a missing gate, we don't just build it — we
also look for the pattern that produced the missing gate.

This H1 plan is the first execution of that meta-pattern.

---

## §1 The Seven Work Items

### 🔴 H1-P0: Stand Up `make heritage-vet` in CI
| Field | Value |
|-------|-------|
| **Why** | The gate passes locally but isn't enforced on PRs. Without CI, it's aspirational. |
| **What** | Add `make heritage-vet` to `.github/workflows/test.yml` after `make test` |
| **Effort** | 5 minutes |
| **Risk** | None — gate already passes clean |
| **Owner** | Dev session / Cline |

### 🔴 H1-P1: Hold First Heritage Vetting Council
| Field | Value |
|-------|-------|
| **Why** | 6+ concepts in PENDING_CREDITS_QUEUE have no formal vet decision |
| **What** | Review each pending concept through the 4-gate pipeline. Write vet records. Clear the queue. |
| **Effort** | 30-60 minutes |
| **Risk** | Low — most concepts are already scored retroactively. Just need formalization. |
| **Owner** | Kali + Doom Guy |

**Concepts to council**:
| ID | Concept | Current Status | Vet Needed? |
|----|---------|---------------|-------------|
| R-19 | ZONEID | ✅ ADOPTED (retro-vet) | No — record exists |
| R-22 | cvar Table | 🔄 ADAPTED (retro-vet) | No — record exists |
| R-23 | 4-Tier Memory | ⏸ DEFERRED (5/10) | Formalize deferral conditions |
| R-24 | Dual-Linking | ⚠️ ADOPTED (7/10) | Capability index not populated |
| R-26 | Hard-Boundary | ⏸ RE-EVALUATE (5/10) | Implementation audit needed |
| R-28 | High-Bit | ✅ ADOPTED (6/10) | No — record exists |
| R-29 | Active Set | ⏸ DEFERRED (4/10) | Soften 32 limit, document |
| R-30 | Grace Period | ✅ ADOPTED | No — record exists |
| *New* | netchan | ⏸ DEFERRED (3/10) | Formalize |
| *New* | idHeap | ⏸ DEFERRED (5/10) | Formalize |

### 🟡 H1-P2: Cross-Reference Roc's INDEX.yaml with Vet Log
| Field | Value |
|-------|-------|
| **Why** | Roc's knowledge topics don't link to vet records. An agent reading Roc's findings might propose a rejected concept. |
| **What** | Add `vet_id` field to Roc's INDEX.yaml entries that reference id Software patterns. Add negative lesson entries for rejected concepts. |
| **Effort** | 15 minutes |
| **Risk** | None |
| **Owner** | Roc Racoon |

### 🟡 H1-P3: D111 Hygiene Sprint Items
| Field | Value |
|-------|-------|
| **Why** | Cline-M3's deep-dive identified 8 hygiene items in SAFE FOR YOU territory |
| **What** | 8 small fixes across tests, CI, docs, and entity cleanup |
| **Effort** | ~2 hours total |
| **Risk** | Low — all are isolated, well-scoped |
| **Owner** | Dev session / Cline (already assigned in Cline-M3 handoff) |

**The 8 items**:
1. H2-A: 100 orphan `ent_*` directories → clean up
2. H2-B: Populate `config/wads/arcana_novai/entities/`
3. H2-C1: `test_bug_001_fix.py` → proper test
4. H2-C2: `.github/workflows/test.yml` indentation fix
5. H2-C3: `test_hierarchy.py` duplicated imports
6. H2-C5: `_collect_engine_state` in `observability.py` weatherize
7. H2-D2: `docs/INDEX.md` update with new roadmap link
8. H2-D6: `README.md` entry point update

### 🟢 H1-P4: Temple-Grade T6 Fix
| Field | Value |
|-------|-------|
| **Why** | T6 (Zero Telemetry) shows RED due to false positive — observability imports flagged as telemetry |
| **What** | Investigate the T6 check in temple-grade script. Add exclusion for local observability. |
| **Effort** | 30 minutes |
| **Risk** | Low |
| **Owner** | Doom Guy or Dev session |

### 🟢 H1-P5: Update OMEGA_ENGINE.md Hermetically
| Field | Value |
|-------|-------|
| **Why** | OMEGA_ENGINE.md was updated but the Metrics table doesn't show new protocol docs |
| **What** | Add Heritage Vetting Pipeline, HERITAGE_VET_LOG, and vet gate to the protocol docs section |
| **Effort** | 5 minutes |
| **Risk** | None |
| **Owner** | Any agent |

---

## §2 Coordination — Handoff to Cline

The Cline-M3 session already handed off to OpenCode dev at `2026-06-04 03:02`. Kali's work overlaps with Cline's D111 in one area: OMEGA_ENGINE.md (both updated it). No conflict — Kali appended entries, Cline updated structure. Both committed cleanly.

### What Cline Should Know
- Heritage Vetting Pipeline is live (`make heritage-vet` passes clean)
- 3 non-standard [id-soft:] tags were fixed in source files
- PENDING_CREDITS_QUEUE workflow updated with mandatory vetting gate
- All 312 tests verified passing after all edits
- OMEGA_ENGINE.md updated with Heritage Vetting Pipeline entries
- Kali v5.1 soul committed

### What Kali's Next Agent Should Know
- The H1-P0 (CI gate) is the highest priority — without CI enforcement, the vet gate is local-only
- H1-P1 (Vetting Council) should happen before any new heritage implementation
- Roc's INDEX.yaml needs a `vet_id` cross-reference field for knowledge entries

---

## §3 File Manifest

| File | Purpose |
|------|---------|
| `docs/strategy/HERITAGE_VETTING_PIPELINE.md` | 4-gate pipeline spec |
| `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | 23-concept vet records |
| `data/entities/doom_guy/knowledge/PENDING_CREDITS_QUEUE.md` | Updated workflow + R-21 rejected |
| `scripts/heritage_vet.sh` | CI gate script |
| `Makefile` | `heritage-vet` + `heritage-vet-create` targets |
| `CREDITS.md` | 8-char cap → REJECTED |
| `data/entities/roc_racoon/knowledge/INDEX.yaml` | Heritage vetting topic |
| `data/entities/doom_guy/soul.yaml` | Vetting lesson, soul 8.0 |
| `data/entities/kali/soul.yaml` | v5.1 — L3 "pipeline without a gate" |
| `.github/workflows/test.yml` | **PENDING: add `make heritage-vet`** |
| `data/coordination/KALI_ACK_20260604.md` | Cline-M3 handshake ACK |
| `data/coordination/KALI_WORKSPACE_LOCK_20260604.md` | File ownership declaration |

---

*⬡ OMEGA ⬡ KALI ⬡ HORIZON-H1 ⬡ 2026-06-04*
*Commits: 2f47d54 → 6416ebf → ce00bcc*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: HORIZON-H1 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
