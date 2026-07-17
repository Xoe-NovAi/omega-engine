# D-283 Mnemosyne Phase 2 — Three-Tier Persistence (Advisory Architecture)
**Packet**: `ho_5cc7e45f2210`  
**Author**: `grok-cli/grok` · 2026-07-17  
**Role**: Advisory architecture review — **do not implement**

---

## What exists (Phase 1 footprint)

| Module | State | Notes |
|--------|-------|-------|
| `hybrid_search.py` / `hybrid_search_engine.py` | Present | RRF k=60 path |
| `blocks.py`, `block_tools.py`, `block_store.py` | Present | Core block model + WAL/IMMEDIATE store |
| `archival.py` | **Substantial skeleton** (~15k) | Vector+KV+graph intent; own SQLite PRAGMA stack |
| `sleep_time.py` | **Substantial skeleton** (~14k) | SleepTimeAgent, second-agent review hooks |
| `recall.py` | **Missing** | Phase 2 create |
| `cross_pollination.py` | **Missing** | Phase 2 create |

Phase 2 is not greenfield — it is **completing the middle tier + wiring** and hardening archival/sleep.

---

## Architecture verdict (Letta 2026 + Omega)

### Core (HOT) — mostly green
- Keep Persona/Human/Safety/Decisions as MemoryBlocks with governance levels.  
- Sleep-time = **untrusted** for Persona/Safety → second-agent review (already documented in `sleep_time.py` header).  
- **Risk**: dual writers (primary agent + sleep) without version vectors → require block version + diff surface in trace (comments already claim this — verify on write path).

### Recall (WARM) — design required
Proposed `recall.py` contract:

```
class RecallStore:
    async def append(session_id, turn, quality: float) -> None
    async def window(session_id, token_budget) -> list[Turn]  # quality-weighted
    async def decay_pass(now) -> stats  # power-law
    async def promote_to_core(turn_ids, block_label) -> None  # via BlockTools only
```

**Decay**: `score = base * (1 + age_days)**(-alpha)` with alpha ∈ [0.01, 0.60] — store alpha per entity in block metadata, not hardcode global.  
**Promotion**: only via append-safe BlockTools; never raw SQL into core.  
**Reuse**: ContextBuilder ACON pipeline for quality scores if available — do not invent second quality model.

### Archival (COLD) — extend, don’t fork
- `ArchivalMemory` already targets vector + KV + graph.  
- **Gap**: graph “future” comment — Phase 2 should either ship minimal edge table or cut scope.  
- **TDP bridge**: taint labels must be metadata on insert; search filters must exclude tainted-for-entity.  
- **PRAGMA parity** with sqlite_vec adapter after Strike 10 convergence.

### SleepTime / Da’at
- Triggers (core >85%, archival >500MB, 24h) are product knobs — put in YAML entity config, not constants only.  
- Consolidation: Recall→Core (append) + Recall→Archival (summarize+embed).  
- **AnyIO** only for background task (`anyio.create_task_group`), never asyncio.

### Cross-pollination
- L3 principles only (M5/M11) — never raw Recall/PII.  
- TDP: refuse cross-entity if taint present.  
- Prefer Hivemind post or explicit handoff over silent DB merge.

---

## Sequencing recommendation

1. Freeze PRAGMA/IMMEDIATE SSOT (D-282) before heavy archival write load.  
2. Implement `recall.py` + tests against tmp SQLite.  
3. Wire SleepTimeAgent.consolidate to real RecallStore.  
4. Cross-pollination last (depends on L3 pipeline maturity).

---

## Rejected approaches

| Approach | Why reject |
|----------|------------|
| Three separate DBs without shared PRAGMA policy | Operational nightmare on 5700U |
| Sleep agent writes Persona without review | Letta safety violation |
| Graph DB (Neo4j) for archival | Sovereignty + ops cost — SQLite edge table first |
| Cross-entity raw transcript share | M5/M11 violation |

---

## Verdict

Architecture is **sound and implementable**. Phase 2 gaps are **Recall + cross_pollination + wiring**, not inventing Core/Archival from zero. Grok will not implement under this advisory packet.

*Deliverable for `ho_5cc7e45f2210`.*
