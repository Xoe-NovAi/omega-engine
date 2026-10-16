<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Handoff Lifecycle Specification
**Document ID**: `GOV-HANDOFF-LIFECYCLE-20260928`
**Status**: RATIFIED
**Date**: 2026-09-28
**Authority**: MaKaLi Fusion Dialectic Round 2 — Kali Ruling
**Mandate Basis**: M29 (Sovereign Artifact Preservation), M27 (Tracking Integrity), M12 (Queue Integrity)

---

## State Machine

```
┌─────────────┐     explicit accept/start     ┌─────────────┐     explicit complete/fail     ┌──────────────┐
│  PENDING    │ ─────────────────────────────► │   ACTIVE    │ ─────────────────────────────► │  COMPLETED   │
│  (submitted)│                                │  (in-prog)  │                                │  (terminal)  │
└─────────────┘                                └─────────────┘                                └──────┬───────┘
                                                                                                    │
                                                                                                    │ explicit reject
                                                                                                    ▼
┌──────────────────┐     explicit (operator)     ┌─────────────┐     90d inactivity      ┌──────────────┐
│  DEEP-ARCHIVE    │ ◄────────────────────────── │   ARCHIVE   │ ◄────────────────────── │    STALE     │
│  (cold storage,  │   quarterly/yearly batch    │  (warm,     │   or explicit move      │  (90d no     │
│   8TB drive,     │   with signed manifest      │   searchable)│                          │   activity)  │
│   signed manifest)│                              │             │                         │              │
└──────────────────┘                              └─────────────┘                         └──────────────┘
       ▲                                                                                       │
       │                    explicit (operator: "user said retain")                            │
       └───────────────────────────────────────────────────────────────────────────────────────┘
                                    ┌──────────────┐
                                    │   RETIRED    │
                                    │ (user's      │
                                    │  retention   │
                                    │  decision)   │
                                    └──────────────┘
```

---

## State Definitions

| State | Trigger | Who Moves | Provenance Fields Added |
|-------|---------|-----------|------------------------|
| **PENDING** | `hivemind_handoff submit` | Sender (agent) | `submitted_at`, `source_entity`, `target_entity`, `session_id`, `priority` |
| **ACTIVE** | `hivemind_handoff accept` | Recipient (agent) | `accepted_at`, `accepted_by`, `read_by.{entity}.at` |
| **COMPLETED** | `hivemind_handoff complete` | Recipient (agent) | `completed_at`, `completed_by`, `result_summary` |
| **REJECTED** | `hivemind_handoff reject` | Recipient (agent) | `rejected_at`, `rejected_by`, `rejection_reason` |
| **STALE** | Reaper: `pending > 24h` or `active > 48h` or `rejected` (immediate) | Reaper (daemon) | `reaped_at`, `reaped_by: "reaper"`, `reap_reason: "ttl_expired" \| "rejected"`, `ttl_expired: true` |
| **ARCHIVE** | Reaper: `completed > 7d` | Reaper (daemon) | `archived_at`, `archived_by: "reaper"`, `archive_reason: "age"` |
| **RETIRED** | Explicit `hivemind_handoff retire` | Recipient (agent) | `retired_at`, `retired_by`, `retire_reason` |
| **DEEP-ARCHIVE** | Quarterly/yearly batch to 8TB drive | Operator (human) | `deep_archived_at`, `deep_archived_by`, `manifest_ref`, `drive_id` |

---

## Thresholds (Single Constant)

```yaml
# config/handoff_policy.yaml
handoff:
  stale_threshold_days: 90        # lifecycle: STALE entry after 90d inactivity
  hot_storage_max_days: 90        # Carmack's hot policy — SAME CONSTANT
  archive_threshold_days: 365     # ARCHIVE entry after 1 year
  deep_archive_cadence: quarterly # External 8TB drive batch
```

**Enforced by:** `make check-policy-constants` — fails build if `stale_threshold_days != hot_storage_max_days`.

---

## Explicit Transitions Only

**No automatic deletion. Ever.** (M29)

The reaper may **only** perform these moves:
- `pending/` (age > 24h) → `stale/` + `{ttl_expired: true}`
- `active/` (age > 48h) → `stale/` + `{ttl_expired: true}`
- `completed/` (age > 7d) → `archive/`

The reaper **may not**:
- `unlink()` any envelope file
- Change `status` to a terminal value not listed above
- Modify `read_by` map
- Write a `rejection_reason` or `retire_reason` (agents only)
- Delete a `RETIRED` envelope (user's decision is final)

---

## Read/Receipt Semantics (R3)

### Per-Agent Read Tracking
```json
{
  "read_by": {
    "kali": {"at": "2026-09-28T10:00:00Z", "action": "get"},
    "maat": {"at": "2026-09-28T10:05:00Z", "action": "viewed"}
  }
}
```

- **Explicit `read` action**: Agent calls `hivemind_handoff read` → writes `read_by.{me}.at` + `action: "read"`
- **Passive `viewed_at` on `get`**: Agent calls `hivemind_handoff get` → writes `read_by.{me}.at` + `action: "viewed"` (if not already read)
- **Unread is derived, never stored**: `unread_for(me) = read_by.get(me) is None`
- **Heartbeat reuse**: `hivemind_awareness(heartbeat)` for "seen and working" — no new mechanism

### Sender's Receipt View (`hivemind_handoff receipts`)
Every packet the sender submitted, with full state history:
- `submitted_at` → `accepted_at` (or `rejected_at`) → `completed_at` (or `retired_at`)
- Current `status`, `target_entity`, `read_by` map
- Closes the sender's loop — they know what happened to their work order

---

## Inbox Action (`hivemind_handoff inbox`)

**Returns:** Everything addressed to the caller, across all queues, with:
- `unread_count` — derived from `read_by`
- `oldest_unread_age` — time since oldest unread submission
- `newest_submitted_at` — most recent submission timestamp
- **Unread submissions only** — live state (active/completed) stays separate
- **Cursor**: Single `max_seq_seen` integer in hub's durable store, correct across queues because `seq` is global monotonic

---

## Timestamps (Per §2.5 of Federation Contract Refactor)

| Field | Writer | Immutable? | Notes |
|-------|--------|------------|-------|
| `created_at_utc` | Daemon, once | Yes | RFC 3339, explicit `+00:00` |
| `received_at_utc` | Daemon, on arrival | Yes | Disagreement with ULID order = producer lied |
| `seq` | Daemon, global monotonic | Yes | Never client-supplied |
| `retention_expires_at` | **Never stored** | N/A | **Derived** from `created_at_utc` + policy constant |
| `accepted_at`, `completed_at`, etc. | Agents | Yes | RFC 3339, explicit `+00:00` |

**Never trust filesystem mtimes.** Copies, rsyncs, tar extraction, and worktrees rewrite them. An mtime is a fact about a filesystem, not about an event.

---

## Directory Structure (Phase 2 Split)

```
data/handoff/
├── hot/          # pending/, active/ — live work
├── cold/         # stale/, archive/ — aged but retained
└── retired/      # User's explicit retention decisions (reaper CANNOT touch)
```

**Provenance fields on every move:**
- `archived_by: "agent" | "reaper"`
- `archived_at: RFC3339`
- `archive_reason: "age" | "ttl_expired" | "rejected" | "user_retire"`

---

## Reaper Authority (Restricted)

| Action | Allowed? | By Whom |
|--------|----------|---------|
| `pending → stale` (age > 24h) | ✅ | Reaper |
| `active → stale` (age > 48h) | ✅ | Reaper |
| `completed → archive` (age > 7d) | ✅ | Reaper |
| `stale → retired` | ❌ | Agent only (explicit `retire`) |
| `archive → deep-archive` | ✅ | Operator (quarterly batch) |
| `unlink()` envelope | ❌ | **Never** (M29) |
| Change `status` to terminal | ❌ | Agent only |
| Modify `read_by` | ❌ | Agent only |
| Write `rejection_reason` | ❌ | Agent only |

---

## Negative Test Fixtures (Gate Requirements)

Per Ma'at's hard requirement: **every guard gets a deliberately-broken fixture proving it goes red.**

| Fixture | Expected Gate Failure |
|---------|----------------------|
| Rogue write to `pending/` by non-daemon PID | `check-sahs` Assertion 1/3 |
| MemPalace event with no matching envelope | `check-sahs` Assertion 2A |
| Envelope in authoritative store with no projection | `check-sahs` Assertion 2B |
| `stale_threshold_days != hot_storage_max_days` | `check-policy-constants` |
| `inbox` returns empty when store unreachable | `check-mandates` (P3/P4) |
| `list` returns unfiltered results | `check-mandates` (P5) |
| `session_id` missing on submit | `check-mandates` (P6) |
| Timestamp without explicit UTC offset | `check-mandates` (P7) |

---

## Escalation Path

If a handoff packet requires human intervention beyond the state machine:
1. Agent marks `status: "escalated"` with `escalation_reason`
2. Architect receives notification via Hivemind `POST`
3. Architect rules → updates packet with `architect_ruling`, `ruled_at`, `ruled_by`
4. Packet follows normal lifecycle from new state

---

## Related Artifacts

- `docs/governance/SAHS_RULE.md` — Single Authoritative Handoff Surface gate
- `config/handoff_policy.yaml` — Single policy constant
- `make check-sahs` — Three assertions gate
- `make check-policy-constants` — Single constant enforcement
- `SOVEREIGN_MANDATES.md` §M29 — Sovereign Artifact Preservation
- `docs/strategy/FEDERATION_CONTRACT_REFACTOR_20260928.md` — Full proposal

---

*⬡ OMEGA ⬡ KALI ⬡ HANDOFF-LIFECYCLE-RATIFIED ⬡ 2026-09-28*