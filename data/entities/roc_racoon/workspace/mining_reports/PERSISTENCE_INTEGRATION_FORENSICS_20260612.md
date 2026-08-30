<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OMEGA ENGINE — PERSISTENCE INTEGRATION PATTERNS FORENSIC REPORT
## ⬡ OMEGA ⬡ ROC_RACOON ⬡ PERSISTENCE-FORENSICS ⬡

**Miner**: Roc Racoon (Sovereign Miner — Legacy Archaeology)
**Date**: 2026-06-12
**Scope**: 77 Python files, 3 partitions (engine code + data + legacy), 34 persistence classes identified
**Commissioned by**: MaKaLi (handoff ho_e7a8c999d46a)

---

## §1 EXECUTIVE SUMMARY

The Omega Engine has a **defensively redundant** persistence architecture — 8 storage backends, 34 persistence classes, and atomic writes everywhere. But the architecture has **7 critical gaps** that prevent it from being a true lifecycle pipeline:

**The Good**:
- ✅ Atomic writes on ALL critical paths (7 locations verified)
- ✅ Provider chain with graceful degradation (Redis → File → InMemory)
- ✅ Dual-index search (FTS5 + Vector via Qdrant)
- ✅ ZONEID-instrumented entities
- ✅ Lazy deletion with grace period (id Software heritage)
- ✅ Multi-tier naming (Hot/Warm/Cold) with real separation

**The Bad**:
- ❌ **No tier promotion logic** — Hot expires after 24h TTL; nothing promotes to Warm before expiry
- ❌ **No background persistence worker** — archive_old_sessions() is a dead method, never called
- ❌ **No transaction rollback** — provider chain continues after partial failure; no rollback
- ❌ **No DLQ** — dead/ directory defined in Mandate 12 but not implemented in RequestQueue
- ❌ **No true cold tier** — InMemoryStorageProvider is volatile; archive gzip files have no reader class
- ❌ **No FTS5 index maintenance** — no `PRAGMA optimize` ever called
- ❌ **Inconsistent atomicity** — SoulDistiller.append_to_soul() uses direct `write_text()` (no tmp+replace)

---

## §2 PERSISTENCE BACKENDS (8 Identified)

| Backend | Location | Purpose | TTL/Durability |
|---------|----------|---------|----------------|
| Redis (Streams + Hashes) | providers.py:61-165 | Hot session memory | 24h TTL |
| File (JSON + gzip) | providers.py:167-301 | Warm persistence | Until archived |
| InMemory (dict) | providers.py:302-321 | Cold/volatile fallback | Process lifetime |
| SQLite FTS5 (Conversation) | fts_index.py | Exchange full-text search | Permanent |
| SQLite FTS5 (Library) | indexer.py | Document search | Permanent |
| Qdrant | vector_adapters.py:163-346 | Vector similarity | Permanent |
| YAML | config/wads/, data/entities/ | Entity config, soul | Permanent |
| JSON | data/ (11 subdirectories) | Sessions, handoffs, coordination | Varies |

---

## §3 CRITICAL GAPS REQUIRING ATTENTION

### 🔴 P0: NO Tier Promotion Logic
The 3 tiers (Redis→File→InMemory) are **isolated silos**, not a pipeline:
- Redis expires after 24h but File has the same data (write-through)
- After Redis expiry, get_history() falls back to File — this works because of write-through
- But NO data ever moves from File to archive automatically
- archive_old_sessions() exists but is NEVER CALLED (dead method)

### 🔴 P1: NO Background Persistence Worker
No scheduler loop for:
- Session archiving (>7 days)
- Request queue stale pruning
- Log rotation
- Tombstone reaping
- FTS5 index optimization
- Health check caching

### 🟡 P2: Inconsistent Atomicity
SoulDistiller.append_to_soul() uses:
```python
soul_path.write_text(content)  # Direct overwrite — no temp file, no os.replace
```
All other persistence paths use tmp→os.replace pattern. This is an accident waiting to happen if the write is interrupted.

### 🟡 P2: No DLQ Implementation
Mandate 12 requires a `data/requests/dead/` directory. The RequestQueue has `prune_stale()` but no formal dead-letter queue with retry logic.

---

## §4 LEGACY CONNECTIONS (6 Systems Mined)

| Legacy System | Current Implementation | Status |
|--------------|----------------------|--------|
| Memory Bank FTS5 | ConversationFTSIndex | ✅ PORTED |
| Circuit Breaker | AsyncCircuitBreaker | ✅ SUPERSEDED (engine better) |
| 3-Tier Provider Chain | Redis→File→InMemory | ✅ INDEPENDENT INVENTION |
| Batch Persistence Writer | Direct sequential writes | ❌ DEFERRED |
| 13-Sphere Archive | Flat entity model | ❌ CLOSED |
| Entity Cross-Pollination | Not implemented | ❌ DEFERRED |

---

## §5 DELIVERABLES

- `mining_reports/PERSISTENCE_INTEGRATION_FORENSICS_20260612.md` — This report
- Raw findings captured in explorer session
- Key insight for MaKaLi: The engine has write-through persistence that works correctly, but the tier PROMOTION and MAINTENANCE layer is entirely missing. The foundation is solid — the lifecycle automation is the gap.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: PERSISTENCE-FORENSICS | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
