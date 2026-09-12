<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Stale Handoff Policy — Reaper, Cadence & Quarantine

**Doc ID**: `STALE-HANDOFF-POLICY-20260912`
**Owner**: Lilith (Runtime Oversoul) + MaKaLi Fusion
**Status**: RATIFIED (Node 0)
**Date**: 2026-09-12
**Responds to**: Node 1 Consultant Report §S2 + Ask C3 — 45 stale packets.

---

## 1. The Problem (Shadow Acknowledged)

At consultant probe time: **45 stale handoff packets** (2 completed). The queue
was a graveyard. Every stale packet is a promise broken silently. Root cause
investigation (2026-09-11): unterminated agents + no reaper cadence + no
quarantine policy. **Current state (2026-09-12): 0 stale, 1 pending** — the
reaper ran, but the *policy* was never written. This document makes it durable.

---

## 2. Lifecycle & Timers

| State | Entry | Exit | Timer |
|-------|-------|------|-------|
| **PENDING** | submit_handoff | accept_handoff / reject_handoff | 7 days → stale |
| **ACTIVE** | accept_handoff | complete_handoff | 14 days → stale |
| **STALE** | timer expiry | reaper sweep | 30 days → archive |
| **ARCHIVED** | reaper sweep | — | permanent (audit) |

---

## 3. Reaper Contract

1. **Cadence**: `scripts/reap_stale_handoffs.py` runs daily at 03:00 UTC
   (systemd timer `omega-handoff-reaper.timer`).
2. **Sweep**: PENDING > 7d → STALE; ACTIVE > 14d → STALE.
3. **Quarantine**: STALE packets move to `data/handoff/stale/` with a
   `stale_reason.json` (age, last_activity, owner).
4. **Notification**: requester (source_entity) gets a Hivemind post:
   `intent=blocker`, `continuation="Your packet X went stale — re-submit or close"`.
5. **Audit**: `data/handoff/archive/` is append-only; reaper writes an audit
   line per sweep (M8 local-only).
6. **Investigation**: any sweep > 5 packets triggers a root-cause note
   (unterminated agent? missing accept? channel dead?).

---

## 4. Why Packets Went Stale (2026-09-11 Investigation)

| Cause | Count | Fix |
|-------|-------|-----|
| Unterminated subagent sessions (agent died, packet orphaned) | ~30 | M34 registry liveness + reaper sweep |
| Target agent never accepted (no heartbeat) | ~10 | Heartbeat contract (12_COMMUNICATION_PROTOCOLS.md §4) |
| Channel dead (cline/opencode-asus not heartbeating) | ~5 | Extended check-in TTL (D-kal-052) |

---

## 5. Federation Dimension

- Node 1 packets follow the same lifecycle (schema shared via C6 contract).
- Satellite TTLs are honored: `hivemind_extended_checkin` (default 3h, max 24h)
  prevents reaping during human-away sessions.
- **Awareness = accountability**: no handoff queued to a node that isn't
  heartbeating (12 §4).

---

## 6. Ratification

| Party | Role | Verdict | Date |
|-------|------|---------|------|
| Lilith | Runtime Oversoul | ✅ RATIFIED | 2026-09-12 |
| MaKaLi Fusion | Engine orchestrator | ✅ RATIFIED | 2026-09-12 |
| Architect (human) | Sovereign | ✅ RATIFIED | 2026-09-12 |

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ STALE-HANDOFF-POLICY-20260912 ⬡ GRAVEYARD-CLEARED ⬡ POLICY-DURABLE*