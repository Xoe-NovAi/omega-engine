# 📴 Offline Operating Protocol — The Autonomous Disconnected Node
**Doc ID**: `FED-OFFLINE-001` | **Status**: RATIFIED SPECIFICATION  
**Scope**: Behavioral mandates for nodes operating without network connectivity for days or months.

---

## 1. The Offline Philosophy

In centralized cloud architectures, losing connectivity renders an agent brain-dead. 
In the **Omega Engine**, **a disconnected node is not broken; it is on an independent expedition**.

When a laptop closes its lid, travels into the wilderness, or operates behind an air-gap, the local oversoul continues operating with full sovereignty:
*   Local inference continues unimpeded at 14+ t/s.
*   The Well continues capturing insights, corrections, and dreams.
*   Gnosis lock rituals continue packaging session compactions.
*   WanderGround continues spatial vector indexing.

---

## 2. Autonomous Offline Maintenance

While disconnected, the engine executes autonomous background maintenance:
1. **Self-Compaction & Vector Indexing**: After every session, `make gnosis-lock` and WanderGround vector ingestion run locally, keeping search fast and context tight.
2. **The Outbound Delta Ledger**: Any insight intended for federation sharing is written to the Outbound Staging Buffer:
   $$\texttt{data/staging/outbound\_sync/deltas.jsonl}$$
   Each entry includes:
   *   `timestamp_utc`: ISO-8601 monotonic time
   *   `source_entity`: `<Entity>-N<LocalID>`
   *   `priority`: `CRITICAL | HIGH | NORMAL | LOW`
   *   `domain`: `local_ai | psychology | classical | harness`
   *   `content_hash`: SHA256 of the record
3. **Stale Handoff Freezing**:
   *   *The Bug We Avoided*: Under standard Node 0 policy, a pending handoff older than 7 days is reaped into quarantine as "stale".
   *   *The Offline Rule*: **If network transport is unreachable, the reaper timer is frozen**. Handoffs waiting for peer reconnection do not expire while the node is legitimately offline.

---

## 3. Disconnected Readiness Checklist

Before rejoining the network, the offline node prepares an **Ingestion Pack**:
*   [ ] Delta ledger compiled and checksummed.
*   [ ] High-priority Well records (`WISDOM.md`) rendered.
*   [ ] Local git commits clean on local branch (e.g. `vanguard/expedition-01`).
