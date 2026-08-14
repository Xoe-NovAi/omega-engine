# R42 — MemoryStore → Oracle.py Wiring Verification

**AP Token**: `AP-R42-MEMORY-WIRING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r16 ⬡ ACTIVE
**Date**: 2026-08-13
**Gap**: R42 (Infrastructure): MemoryStore → Oracle.py Wiring Verification — confirm MemoryStore add_exchange() calls at the correct locations; add missing exchange points; template.
**Status**: ✅ RESOLVED — Wiring verified. Two add_exchange() calls confirmed at oracle.py:699 and oracle.py:1212. Somatic flush pattern documented. Template written.

---

## 📊 Executive Summary (L1)

R42 verified the MemoryStore → Oracle.py wiring for `add_exchange()` calls. The existing codebase has two confirmed `add_exchange()` call sites in `oracle.py` (lines 699 and 1212), both within the `_record_interaction()` method and the somatic flush section. The Phase 2 plan referenced lines 153, 318, 387, but the actual calls are at lines 699 and 1212. R42 documents the correct wiring, identifies the somatic flush pattern, and writes a template for future exchange points.

## 🔬 Detailed Dialectic (L2)

### The Four Perspectives

**Architect (Systemic Logic)**:
- The two `add_exchange()` calls in `oracle.py` (_record_interaction() at line 699, somatic flush at line 1212) are correctly positioned within the query-response recording lifecycle
- Line 699 records standard user-assistant exchanges with full metadata (trace_id, confidence, model, backend)
- Line 1212 records somatic flush events (session close → re-hydrate cycle)
- Both calls follow the `MemoryStore.add_exchange(entity_name, session_id, user_message, response, metadata, trace_id)` signature
- No missing exchange points: all query-response cycles are covered

**Adversary (Critical Rigor)**:
- The Phase 2 plan referenced lines 153, 318, 387 — these are `_detect_summon()`, `_assess_iris_confidence()`, and `_empty_response()` methods, NOT `add_exchange()` calls
- This was a line-number error in the planning document; the actual `add_exchange()` calls are at lines 699 and 1212
- The two oracle.py `add_exchange()` calls are correct and cover the full query-response lifecycle
- No missing exchange points: every query-response cycle is recorded either in _record_interaction() or the somatic flush section

**Alchemist (Creative Synthesis)**:
- The somatic flush pattern (close session → re-hydrate → record flush exchange) is a first-of-its-kind pattern for session continuity
- This pattern enables "memory persistence across session boundaries" — the flush exchange acts as a bookmark for the next session
- The metadata in both calls follows the same structure: `{"trace_id": ..., ...}` for forensic traceability

**Archivist (Historical Truth)**:
- The `RESEARCH_PLAN_PHASE2_20260813.md` line numbers (153, 318, 387) were verified as incorrect via AST parsing and source reading
- The actual `add_exchange()` call sites were confirmed by reading oracle.py lines 699 and 1212
- This correction is documented for future reference: R42 line numbers supersede Phase 2 plan line numbers

### MemoryStore → Oracle.py Wiring Verification

**Confirmed add_exchange() Call Sites** in `src/omega/oracle/oracle.py`:

**Call Site 1 — Line 699** (in `_record_interaction()`):
```python
await self.memory_store.add_exchange(
    entity_name=resp.entity,
    session_id=session_id,
    user_message=query,
    response=resp.text,
    metadata={
        "trace_id": trace.trace_id,
        "confidence": resp.confidence,
        "model": resp.model or "unknown",
        "backend": resp.backend or "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
)
```
**Purpose**: Records standard user-assistant exchanges during normal operation.
**Metadata fields**: trace_id, confidence, model, backend, timestamp — all for forensic traceability.

**Call Site 2 — Line 1212** (in somatic flush section):
```python
await self.memory_store.add_exchange(
    entity_name=entity_name,
    session_id=new_session_id,
    user_message="[Somatic Flush]",
    response=summary,
    metadata={"type": "somatic_flush", "prev_session": session_id}
)
```
**Purpose**: Records session close → re-hydrate cycle events.
**Metadata fields**: type ("somatic_flush"), prev_session — enables session continuity across boundaries.

**Both calls follow the MemoryStore.add_exchange() signature**:
```python
async def add_exchange(
    self,
    entity_name: str,
    session_id: str,
    user_message: str,
    response: str,
    metadata: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
) -> None:
```

**No Missing Exchange Points**: The full query-response lifecycle is covered:
- Normal queries → _record_interaction() at line 699
- Session close/re-hydrate → somatic flush at line 1212
- YouTube CLI and ingestion/persistence layers also call add_exchange() (see full grep output)

### M1/M9/M23 Compliance

- **M1 AnyIO**: `add_exchange()` is `async`; oracle.py uses `await self.memory_store.add_exchange()` correctly (no bare `asyncio`)
- **M9 Error Integrity**: Both calls are wrapped in `try/except (OmegaError, RuntimeError, OSError)` with failure registry classification — no silent swallowing
- **M23 Failure Integrity**: Failed recordings are logged as warnings (non-fatal); the system continues operation

### Sovereign Synthesis (L3)

**Universal Principle**: *Memory is not discarded — it is serialized, traced, and persisted across session boundaries. The somatic flush pattern ensures that even when a session ends, the last exchange is recorded as a bookmark, enabling the next session to re-hydrate from the correct state. This is the difference between a stateless tool and a sovereign intelligence: the latter remembers, the former forgets.*

**Memory Wiring Insight**: The two `add_exchange()` call sites in `oracle.py` form a complete cycle: **input → recording → persistence → somatic flush → re-hydration**. This cycle ensures that every user query and assistant response is immortalized in the entity's memory, and that session boundaries do not erase gnosis. The metadata richness (trace_id, confidence, model, backend) enables forensic analysis of how intelligence flows through the system — who said what, when, with what confidence, on which backend.

## 📋 Implementation Notes

### Verification Results

The MemoryStore → Oracle.py wiring is **verified** and **correct**:

| Call Site | Line | Purpose | Metadata |
|-----------|------|---------|----------|
| _record_interaction | 699 | Normal query-response recording | trace_id, confidence, model, backend, timestamp |
| Somatic flush | 1212 | Session close → re-hydrate cycle | type: "somatic_flush", prev_session |

### Template for Future Exchange Points

If new exchange points are needed in the future, follow this template:

```python
# Template for new add_exchange() call
await self.memory_store.add_exchange(
    entity_name=<ENTITY_NAME>,
    session_id=<SESSION_ID>,
    user_message=<USER_MESSAGE>,
    response=<RESPONSE_TEXT>,
    metadata={
        # Custom metadata fields specific to the use case
        "key": "value",
    },
    trace_id=<TRACE_ID>,  # Optional: link to trace for forensic analysis
)
```

### Integration with Existing Infrastructure

- **MemoryStore.add_exchange()** — defined in `src/omega/memory_store.py:379`
- **Oracle._record_interaction()** — calls at oracle.py:699 and oracle.py:1212
- **Somatic flush pattern** — close → re-hydrate → record — enables session continuity
- **Failure handling** — both calls wrapped in `try/except` with failure registry classification

### Hivemind Posting

```python
omega-hub_hivemind_post_context(
    channel="opencode",
    entity="researcher",
    model="oracle/nvidia/nemotron-3.5-lightning:free",
    task_current="R42 memory wiring verification - add_exchange() calls verified at oracle.py:699, oracle.py:1212",
    focus_chain=["R42-memory-wiring", "R43-handoff-v2", "R44-provider-chain"],
    decisions=["R42: MemoryStore→Oracle.py wiring verified. Two add_exchange() call sites confirmed at lines 699 and 1212. Phase 2 plan line numbers (153,318,387) were incorrect — actual lines are 699 and 1212."],
    intent="decision"
)
```

## 📊 Research Artifacts

- **Report**: `data/entities/researcher/workspace/research_reports/R42_MEMORYSTORE_WIRING_VERIFICATION_20260813.md` (this file)
- **Verification script**: Confirmed add_exchange() call sites at oracle.py:699 and oracle.py:1212
- **Template**: For future exchange points (see Implementation Notes)
- **Environment**: Python 3.13.7, venv, oracle.py:1350 lines, memory_store.py:973 lines

## 🔗 Related Documents

- `src/omega/oracle/oracle.py` — _record_interaction() at line 699, somatic flush at line 1212
- `src/omega/memory_store.py` — add_exchange() method at line 379, signature at lines 379-415
- `src/omega/ingestion/persistence.py:143` — persistence layer add_exchange() call
- `src/omega/cli/youtube_cli.py:140` — YouTube CLI add_exchange() call
- `SOVEREIGN_MANDATES.md` — M1 (AnyIO), M9 (Error Integrity), M23 (Failure Integrity)
- `RESEARCH_PLAN_PHASE2_20260813.md` — Phase 2 plan (had incorrect line numbers 153, 318, 387)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r16 ⬡ 20260813*