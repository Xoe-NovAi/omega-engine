<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# How the Hivemind Works

**Audience**: any agent about to claim "I got no handoff" or "nobody is active".
**Scope**: the four coordination primitives — awareness, handoff, receipts,
discovery — and the three laws that keep them honest.

## The Four Primitives

### 1. Awareness — presence only
`hivemind_awareness(action="heartbeat" | "get" | …)` answers *who is alive
right now*. Heartbeats publish presence; `get` returns the active-agent
snapshot.

**It does not enumerate packets.** An empty awareness view says "nobody is
currently heartbeating" — never "there is no work for me".

### 2. Handoff — packets on disk
`hivemind_handoff(action="submit" | "accept" | "complete" | …)` writes a JSON
envelope into `data/handoff/{pending,active,completed,stale,archive}/` — one
file per packet, state expressed by directory membership (ADR-003). Delivery
is by addressing: every packet carries `target_channel` + `target_entity`.

```
sender                   packet store                    receiver
  |                          |                              |
  |-- submit --------------->|                              |
  |                          | data/handoff/pending/ho_*.json
  |                          |-- addressed to target ------>|
  |                          |      read   (receipt sidecar)|
  |                          |      accept -> active/       |
  |                          |      complete -> completed/  |
```

State never rewrites the envelope: transitions are atomic directory renames.
A store failure is an **error payload** (`{"error": {"code": …}}`), never an
empty list — callers branch on `error.code`, not on emptiness.

### 3. Receipts — read state in sidecars
A read is recorded by **appending** to `{packet_id}.receipts.jsonl` with an
fsync per receipt; the envelope is never edited (ADR-006). Reading is not
deciding: a receipt proves someone *looked*, `accept` proves someone *took
responsibility*.

### 4. Discovery — pointer files in the Exchange
Cross-node work is announced as **pointer files** published in the Exchange
manifest (GET-only publish root — see `HOW_THE_EXCHANGE_WORKS.md`). The
pointer names the real body (file, size, sha256, pull URL); the receiver pulls
and verifies the hash.

**Banned as absence evidence**: `handoff(action="inbox")` and
`awareness(action="get")`. Both are scoped presence/inbox views with cursors,
TTLs and identity filters — an empty result from either is NOT proof that no
packet exists. **The packet store is the record.**

## End-to-End Flow

```
A (Node 0)                     Exchange                    B (Node 1)
-----------                    ---------                   -----------
write brief body -----------> manifest <---------- publish - write body
submit PTR packet ---------------> data/handoff/pending/
                                        |
                                  B checks OWN target_entity
                                   |-- read      -> receipts sidecar
                                   |-- accept    -> active/
                                   |-- complete  -> completed/ (+ result)
```

## The Three Laws

1. **Check your own `target_entity` in the packet store before claiming absence.**
2. **A node suffix is an address, not a spelling. Never fold it.**
   (`lilith-n1` ≠ `lilith`; an unmatched `-n<N>` REFUSES — ADR-005.)
3. **Read state lives in the journal. The envelope is never mutated.**

## Invariants

- The envelope is immutable after creation; all state moves are atomic renames.
- Error payload ≠ empty list; never infer absence from a failed or scoped query.
- `inbox` / `awareness(get)` empty ≠ no packets — only the packet store decides.

*⬡ OMEGA ⬡ CLINE ⬡ HOW_THE_HIVEMIND_WORKS-v1.0.0 ⬡ 2026-10-02 ⬡*