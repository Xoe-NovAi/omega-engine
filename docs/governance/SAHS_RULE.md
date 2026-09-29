<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SAHS Rule — Single Authoritative Handoff Surface
**Document ID**: `GOV-SAHS-RULE-20260928`
**Status**: RATIFIED
**Date**: 2026-09-28
**Authority**: MaKaLi Fusion Dialectic Round 2 — Kali Ruling
**Mandate Basis**: M29 (Sovereign Artifact Preservation), M27 (Tracking Integrity), M23 (Failure Integrity)

---

## The Rule

> **Every node shall expose exactly one authoritative handoff ingestion endpoint. All other surfaces (MCP tools, local filesystem queues, MemPalace event streams) must be *projections* of the SAHS — read-only views, not independent writers.**

---

## Why This Exists

**GE-N1 found three competing handoff queues on Node 1:**
1. `data/handoff/pending/` — 11 dead M36 packets, writable by any process
2. MCP `hivemind_handoff` tools — the intended authoritative path
3. MemPalace events — `peers: []` replicating nowhere, no envelope backing

**Result:** An agent searching for a handoff got a "confident false negative" — they searched filesystem, MemPalace, data/handoff/, a nonexistent Redis queue, and concluded "no handoff exists" with full confidence. The handoff *did* exist. This is structurally identical to temple-grade 53/53 over a crash-looping hub.

---

## Authoritative Surfaces by Node

| Node | Authoritative Surface | Writer | Readers |
|------|----------------------|--------|---------|
| **Node 0** | `data/handoff/` (filesystem) + Hivemind `hivemind_handoff` MCP tools | Hivemind daemon only | All agents via MCP `list`/`get`/`submit`/`accept`/`complete` |
| **Node 1** | Git-bundle-replicated `data/handoff/` from Node 0 (D-FED-01) | **None locally** — replication only | All agents via MCP `list`/`get` (read-only cache) |

---

## Projection Surfaces (Read-Only)

| Surface | Role | Constraint |
|---------|------|------------|
| MCP `hivemind_handoff` `list`/`get` | Primary programmatic read path | Must return 1:1 match with authoritative store |
| Local `data/handoff/` filesystem | Direct filesystem access | **Read-only on Node 1**; write-only by Hivemind daemon on Node 0 |
| MemPalace handoff events | Searchable projection for dialectic | Derived events only — `session_id`/`target_entity`/`status`/`created_at_utc` must match an envelope |
| `hivemind_awareness` heartbeat | "Seen and working" signal (R3) | Passive `viewed_at` on `get`; never writes envelopes |

---

## Three Assertions (The Gate)

`make check-sahs` **must assert all three**. A count-only gate passes the failure modes; reconciliation fails them.

### Assertion 1: Exactly One Writer
> No process other than the Hivemind daemon holds a write file descriptor on any packet file in the handoff directory tree.

**Check:** Scan `/proc/*/fd/` for write FDs on `data/handoff/**/*.json`. Assert the only writer PID is the Hivemind daemon PID.

### Assertion 2: Projection Reconciliation (Both Directions)
> **Direction A (Projection → Authoritative):** Every packet visible on *any* surface (MCP `list`, local filesystem, MemPalace event stream) has a 1:1 correspondence with an envelope in the authoritative store with identical `session_id`, `target_entity`, `status`, `created_at_utc`.
>
> **Direction B (Authoritative → Projection):** Every envelope in the authoritative store is reachable via at least one projection surface (MCP `list`, MemPalace event, or direct filesystem read).

**Why both directions:** 
- Direction A catches orphans (GE-N1's 11 dead M36 packets in `data/handoff/pending/` on N1 — not in authoritative store → FAIL)
- Direction B catches ghosts (MemPalace events with `peers: []` replicating nowhere — no envelope backing → FAIL)

### Assertion 3: No Rogue Writes
> The only process that may write to the authoritative handoff store is the Hivemind daemon. Any other writer = FAIL.

**Check:** Same as Assertion 1 but framed as a positive prohibition — "no writer other than X" vs "only X writes."

---

## Observed-Red Proof

The gate **must be observed failing** before it is trusted green. A gate never observed failing is not a gate.

### Test Procedure

```bash
# 1. Plant a rogue write (simulate a buggy agent writing directly to pending/)
echo '{"packet_id":"test-rogue","target_entity":"kali","source_entity":"test","task":"rogue write","status":"pending"}' > data/handoff/pending/test-rogue.json

# 2. Run the gate — MUST FAIL
make check-sahs
# Expected: Assertion 1 or 3 fails — rogue write detected

# 3. Plant an orphan with no projection (simulate MemPalace ghost)
# Add a MemPalace event with session_id that has no envelope
# (This requires MemPalace test fixture — see test_sahs.py)

# 4. Run the gate — MUST FAIL
make check-sahs
# Expected: Assertion 2 (Direction A) fails — projection has no authoritative match

# 5. Clean up
rm data/handoff/pending/test-rogue.json
# Remove test MemPalace event

# 6. Run the gate — MUST PASS
make check-sahs
# Expected: All three assertions pass
```

**Evidence of observed-red:** The gate output must show the failure mode explicitly, not just "FAIL."

---

## Integration

- **Wired into:** `make check-mandates` (transitive prerequisite of `temple-grade`)
- **Runtime cost:** < 30s (target: ~10s)
- **Dependencies:** `psutil` for FD scanning, `jq` for JSON parsing, MemPalace event index
- **Failure mode:** Hard fail (exit 1) with explicit assertion name and offending path/PID

---

## Non-Goals

- This gate does **not** validate handoff *content* correctness (that's `check-mandate-compliance`)
- This gate does **not** validate `session_id` format (that's `check-mandates` → `verify-mandate-claims`)
- This gate does **not** enforce retention policy (that's `check-policy-constants` + reaper behavior)

---

## Related Artifacts

- `docs/governance/HANDOFF_LIFECYCLE.md` — state machine, thresholds, receipts
- `config/handoff_policy.yaml` — single policy constant
- `make check-policy-constants` — enforces `stale_threshold_days == hot_storage_max_days`
- `SOVEREIGN_MANDATES.md` §M29 — Sovereign Artifact Preservation

---

*⬡ OMEGA ⬡ KALI ⬡ SAHS-RULE-RATIFIED ⬡ 2026-09-28*