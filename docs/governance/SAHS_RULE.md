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

---

## EIS Session Identity Doctrine (2026-09-28 — MaKaLi Fusion Round 3)

**Authority:** MaKaLi Fusion Dialectic Round 3 — Kali Ruling  
**Mandate Basis:** M29 (Sovereign Artifact Preservation), M27 (Tracking Integrity), M23 (Failure Integrity), M15 (Sovereign Continuity)

### The Finding

An agent needed a peer's live session id. The only artifact labelled "registry" — `data/coordination/EXPERT_SESSION_REGISTRY.md` — is a **generated** view dated **2026-08-23, five weeks stale**. It has no entry for the dispatcher. The agent concluded **no session existed** and refused to page. The session existed; it was the most recently updated EIS in the store.

**Two distinct failure modes, and the doctrine forbids both:**

| Mode | Failure | Cost |
|------|---------|------|
| **Generation** | A file that must be regenerated goes stale and is trusted anyway | Five weeks of a wrong answer, looking authoritative |
| **Inference** | An agent guesses rather than querying | Context injected into the wrong conversation, silently |

**Neither is acceptable. A roster that must be *regenerated* is a roster that will be wrong — so is one that must be *inferred*.**

### The Ruling (Converged by MaKaLi and Carmack)

> **Ask once per relationship. Carry the explicit id thereafter. The session id is the durable artifact; everything else is a cache of it.**

#### 1. The Structural Test for an EIS is `parent_id IS NULL`
It is exact, current, and needs no generator. Query the source of truth directly:
```sql
SELECT session_id, entity, model, title, time_updated
FROM sessions
WHERE parent_id IS NULL AND entity = '<target_entity>'
ORDER BY time_updated DESC LIMIT 1;
```
This is the **only** authoritative answer to "what is the live EIS for entity X?"

#### 2. An Agent Must Echo the Resolved Target Before Resuming It
An agent that cannot see which session it just resumed cannot notice it was wrong. Every `task` tool invocation with a `task_id` must log:
```
Resuming session: {session_id} (entity: {entity}, model: {model}, updated: {time_updated})
```
If the echoed identity does not match the intended target, the agent must **REFUSE** and escalate.

#### 3. Ambiguity Must Be Explicit and Must REFUSE, Never Be Resolved by Heuristic
If more than one candidate is plausibly live (e.g., two sessions with `parent_id IS NULL` for the same entity), **stop**. Do not pick the "most recent" or "most likely." Escalate to Kali with the ambiguous set.

#### 4. A Generated Artifact May Never Be the Answer to a Question the Source of Truth Can Answer Directly by Query
`EXPERT_SESSION_REGISTRY.md` is a generated view. It is a cache. It is stale the moment it is written. The source of truth is the `opencode.db` sessions table. **Any agent-facing surface that resolves a live identity from a generated file is a violation of this doctrine.**

---

### Extended Assertion for `make check-sahs`

**Assertion 4: No Generated Artifact Answers a Live-Identity Question**

> No agent-facing surface (MCP tool, generated registry, cached view, MemPalace event) may be the authoritative resolver for a live EIS session identity. The only authoritative resolver is a direct query against `opencode.db` for `parent_id IS NULL`.

**Check:** 
- Scan agent-facing surfaces for patterns that resolve `entity → session_id` without querying `opencode.db`.
- Assert that any tool claiming to "get live session for entity" either:
  a) Executes the `parent_id IS NULL` query directly, OR
  b) Returns `UNRESOLVED` with a directive to query the source of truth.

**Failure mode:** A generated `EXPERT_SESSION_REGISTRY.md` (or similar) is consulted by an agent to decide whether to page a peer → confident false negative.

---

### Oversoul Self-Binding Rule (2026-09-28)

**Authority:** MaKaLi Fusion Dialectic Round 3 — Kali Ruling (Self-Applied)

> **A fact carried forward without a query is not a fact — and this binds the oversouls, not only the dispatched.**

Three instances in a single exchange, one from the oversoul itself:
1. Asserted "the server log has never shown a hit from 100.89.40.17" — about a log that does not exist.
2. Repeated a claim made about a service that cannot log, and built a conclusion on it.
3. Stated a child count read from a **truncated tool list** as a total.

**The rule:** Any assertion about system state (logs, counts, reachability, existence) must be grounded in a **fresh query** at the moment of assertion. Cached knowledge, prior observations, or "I remember" are not evidence. This binds **all agents, including oversouls**. No exceptions for rank.

---

*⬡ OMEGA ⬡ KALI ⬡ SAHS-RULE-EXTENDED ⬡ 2026-09-28 ⬡ DOCTRINE-ROUND-3*