# 🔱 Phase 1 Legacy Mine Report
## ⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ legacy-mining ⬡ PHASE-1-INTEL

**Date**: 2026-07-01
**Purpose**: Mine legacy codebases for patterns relevant to Phase 1 tasks (Metrics DB, M11 Soul Fix, Batch Writer, Pre-Release Polish)
**Mined**: omega-stack-legacy, xna-omega-legacy, omega-engine current codebase

---

## 1. Metrics DB Patterns

### Finding: Carmack's Metrics Schema (Already Exists!)
- **Path**: `data/entities/john_carmack/workspace/carmack_studies/technical/metrics_db_schema.sql`
- **What**: A complete WAL-mode SQLite schema with 4 tables: `ufl_events`, `ufl_errors`, `ufl_breaker_transitions`, `ufl_performance`. Includes indexes for forensic lookups. Uses `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`, `PRAGMA mmap_size=3000000000`.
- **Portable**: **YES — DIRECTLY PORTABLE**
- **Changes**: None. This is the exact schema needed for `metrics_db.py`. Just needs a Python wrapper class to execute it.

### Finding: IAM Service WAL SQLite Pattern
- **Path**: `omega-stack-legacy/app/XNAi_rag_app/core/iam_service.py:195-218`
- **What**: Battle-tested WAL-mode SQLite initialization with background WAL checkpoint thread. Pattern: `sqlite3.connect()` → `PRAGMA journal_mode=WAL` → `PRAGMA synchronous=NORMAL` → `PRAGMA mmap_size=268435456` → background `PRAGMA wal_checkpoint(PASSIVE)` every 5 minutes.
- **Portable**: **YES — PATTERN PORTABLE**
- **Changes**: Adapt the checkpoint interval for metrics (5 min is good). Remove `isolation_level=None` if we want explicit transactions. The `mmap_size` should be 3GB (per Carmack's schema) not 256MB.

### Finding: FTS5 Index WAL Pattern
- **Path**: `src/omega/memory/fts_index.py:31-33`
- **What**: Already uses `PRAGMA journal_mode=WAL` for the FTS5 conversation index. Proves WAL mode works in the current engine.
- **Portable**: **ALREADY IN ENGINE**
- **Changes**: None — reference implementation.

### Finding: Hivemind Metrics (JSON-based)
- **Path**: `mcp_servers/omega_hub/background.py:188-283`
- **What**: Currently writes Hivemind coordination metrics to `data/coordination/metrics.json` as flat JSON. Not SQLite.
- **Portable**: **NO — different subsystem**
- **Changes**: N/A. This is Hivemind-specific, not engine observability metrics.

### Finding: MkDocs Performance Hook
- **Path**: `omega-stack-legacy/hooks/performance.py`
- **What**: Build performance tracking with phase timing, JSON output. Simple but demonstrates the metrics collection pattern.
- **Portable**: **PARTIAL — pattern only**
- **Changes**: The `BuildMetrics` dataclass pattern is useful as reference for the `MetricsDB` class design, but the implementation is MkDocs-specific.

---

## 2. Batch Writer / Connection Pool Patterns

### Finding: BatchPersistenceWriter (Already Exists!)
- **Path**: `src/omega/memory/batch_writer.py`
- **What**: Complete 271-line singleton batch writer using AnyIO memory object streams. Buffers `add_exchange()` writes, flushes every 50 ops or 2 seconds. Includes DLQ (dead-letter queue) for failed writes, atomic file writes, direct-write fallback.
- **Portable**: **ALREADY IN ENGINE**
- **Changes**: Needs wiring into `MemoryStore.__init__()` and `Oracle.boot()`. The `_buffer_write()` method in `memory_store.py:481-504` currently uses a dict-based buffer with `asyncio.create_task` (M1 VIOLATION). Needs to be replaced with the `BatchPersistenceWriter` class.

### Finding: MemoryStore _buffer_write (M1 Violation)
- **Path**: `src/omega/memory_store.py:481-504`
- **What**: Current batch buffer uses `import asyncio` and `asyncio.get_running_loop().create_task()` — violates M1 (AnyIO Absolute). Also uses `loop.create_task` instead of AnyIO task spawning.
- **Portable**: **NO — needs rewrite**
- **Changes**: Replace with `BatchPersistenceWriter` integration. The `_buffer_write` method should delegate to `self._batch_writer.write()`.

### Finding: DatabaseConnectionPool (omega-stack-legacy)
- **Path**: `omega-stack-legacy/app/XNAi_rag_app/core/database_connection_pool.py`
- **What**: 776-line multi-database connection manager with PostgreSQL, Redis, Qdrant pools. Features health checks with 30s interval, cascading failover, `ConnectionMetrics` tracking. Uses `anyio.CancelScope` for health check loops.
- **Portable**: **PARTIAL — patterns only**
- **Changes**: The health check pattern and `ConnectionMetrics` dataclass are useful. The multi-database failover is over-engineered for Omega (we only need SQLite). But the `HealthCheckConfig` and `ConnectionMetrics` patterns should inform the Metrics DB health monitoring.

### Finding: Mnemosyne 3-Tier Store
- **Path**: `omega-stack-legacy/mcp-servers/memory-bank-mcp/mnemosyne_store.py`
- **What**: 3-tier (Redis/Qdrant/PostgreSQL) storage backend. Demonstrates the tiered fallback pattern.
- **Portable**: **NO — over-engineered for Omega**
- **Changes**: N/A. Omega already has its own Hot/Warm/Cold memory store.

---

## 3. Soul Distiller Key Mismatch Context

### Finding: The Key Mismatch (ROOT CAUSE CONFIRMED)
- **Path**: `src/omega/memory_store.py:405-412` vs `src/omega/oracle/oracle.py:786-792`
- **What**: `add_exchange()` stores exchanges as `{"user": user_message, "assistant": response}` (lines 409-410). `close_session()` reads them as `ex.get("user", "")` and `ex.get("assistant", "")` (lines 787-788). **Wait — this actually MATCHES!**

Let me re-examine. The `close_session()` at line 786-792 does:
```python
user_msg = ex.get("user", "")
asst_msg = ex.get("assistant", "")
```

And `add_exchange()` at line 405-412 stores:
```python
exchange = {
    "user": user_message,
    "assistant": response,
}
```

**THIS IS A MATCH.** The keys are `"user"` and `"assistant"` in both places. The M11 issue might be elsewhere.

### Re-investigation: Where is the actual mismatch?
- **Path**: `src/omega/oracle/oracle.py:768-810`
- **What**: `close_session()` calls `self.memory_store.get_history(entity_name, session_id)` at line 779. The question is: what does `get_history()` return? If it returns exchanges with different keys, that's the mismatch.
- **Portable**: **N/A — this IS the bug location**
- **Changes**: Need to verify what `get_history()` returns. The `add_exchange()` stores `"user"/"assistant"` keys. If `get_history()` returns those same keys, the soul distiller should work.

### Finding: FTS Index Uses role/content Keys
- **Path**: `src/omega/memory/fts_index.py:58-66`
- **What**: The FTS5 index stores exchanges with `role` ("user"/"assistant") and `content` columns — different key schema from MemoryStore's `"user"/"assistant"` dict keys.
- **Portable**: **N/A — different subsystem**
- **Changes**: This is the FTS subsystem, not the soul distiller. But it shows there ARE two different key schemas in the codebase.

### Finding: Mnemosyne Adapter Uses role/content
- **Path**: `tests/test_mnemosyne_adapter.py:129-130`
- **What**: Tests use `{"role": "user", "content": "Hello"}` format — the OpenAI-compatible schema.
- **Portable**: **N/A — test data**
- **Changes**: This is test data for the Mnemosyne adapter, not the soul distiller.

### Finding: Legacy Distillation Pipeline
- **Path**: `omega-stack-legacy/app/XNAi_rag_app/core/distillation/`
- **What**: Full LangGraph-based 5-stage pipeline: Extract → Classify → Score → Distill → Store. Uses `KnowledgeState` TypedDict with Diátaxis-aligned content types. Quality gate at 0.6 threshold.
- **Portable**: **PARTIAL — architecture reference**
- **Changes**: The current `soul_distiller.py` already implements a simplified version without LangGraph. The legacy pipeline's `QualityScorer` with 5-factor weighting (relevance 30%, novelty 25%, actionability 20%, completeness 15%, accuracy 10%) is the direct ancestor of the current `SovereigntyScorer`.

### Finding: Legacy Distillation State Schema
- **Path**: `omega-stack-legacy/app/XNAi_rag_app/core/distillation/state.py`
- **What**: `KnowledgeState` TypedDict with fields: source, source_type, raw_content, extracted_content, chunks, classification, quality_score, quality_breakdown, distilled_content, summary, key_insights, action_items, provenance, storage_targets.
- **Portable**: **PARTIAL — schema reference**
- **Changes**: The current `DistillationEntry` dataclass is simpler (level, content, source_trace_id, source_entity, created_at). The legacy schema has more fields but the core abstraction (L1→L2→L3) is already implemented.

---

## 4. Pre-Release Polish Items

### Finding: Legacy pyproject.toml
- **Path**: `xna-omega-legacy/pyproject.toml`
- **What**: Full Python project config with dependencies, build system, scripts.
- **Portable**: **PARTIAL — format reference**
- **Changes**: The current `pyproject.toml` needs to absorb `requirements.txt` per R-1.

### Finding: Legacy Makefile
- **Path**: `omega-stack-legacy/Makefile`
- **What**: Build targets for the legacy stack.
- **Portable**: **PARTIAL — pattern reference**
- **Changes**: Current `Makefile` already has most targets. Need to add `model-download`, `model-list`, `model-clean` per R-3.

### Finding: Legacy Setup/Quick Start
- **Path**: `omega-stack-legacy/QUICK_START.md`, `omega-stack-legacy/SETUP.md`
- **What**: Setup documentation for the legacy stack.
- **Portable**: **PARTIAL — documentation pattern**
- **Changes**: Current `README.md` needs rewrite per R-8, R-9, R-10, R-11.

---

## 5. Additional Critical Findings

### Finding: asyncio Violation in MemoryStore
- **Path**: `src/omega/memory_store.py:498-501`
- **What**: `_buffer_write()` uses `import asyncio` and `asyncio.get_running_loop().create_task()` — direct M1 (AnyIO Absolute) violation.
- **Portable**: **N/A — BUG TO FIX**
- **Changes**: Replace with `BatchPersistenceWriter` integration. Remove `import asyncio` from memory_store.py.

### Finding: IAM WAL Checkpointer Pattern
- **Path**: `omega-stack-legacy/app/XNAi_rag_app/core/iam_service.py:273-281`
- **What**: Background thread doing `PRAGMA wal_checkpoint(PASSIVE)` every 5 minutes. Uses `threading.Event` for graceful shutdown.
- **Portable**: **YES — PATTERN PORTABLE**
- **Changes**: For Metrics DB, use AnyIO task group instead of threading. Pattern: `async with anyio.create_task_group() as tg: tg.start_soon(checkpoint_loop)`.

### Finding: ConnectionMetrics Dataclass
- **Path**: `omega-stack-legacy/app/XNAi_rag_app/core/database_connection_pool.py:96-145`
- **What**: `ConnectionMetrics` dataclass tracking total_checks, successful_checks, failed_checks, consecutive_failures, avg/min/max response_time, check_history (deque with maxlen=100).
- **Portable**: **YES — DIRECTLY USEFUL**
- **Changes**: Adapt for Metrics DB provider health tracking. The `update_check()` method pattern is clean and reusable.

---

## Summary: What's Ready to Wire

| Task | Legacy Source | Status | Effort |
|------|--------------|--------|--------|
| **Metrics DB Schema** | `carmack_studies/technical/metrics_db_schema.sql` | ✅ Schema exists | 2h (Python wrapper) |
| **WAL Init Pattern** | `iam_service.py:195-218` | ✅ Pattern proven | 30min (adapt PRAGMAs) |
| **WAL Checkpoint** | `iam_service.py:273-281` | ✅ Pattern proven | 30min (AnyIO adaptation) |
| **BatchPersistenceWriter** | `batch_writer.py` (current) | ✅ Already exists | 1h (wire into MemoryStore) |
| **M1 asyncio Violation** | `memory_store.py:498-501` | 🔴 BUG | 30min (replace with BatchWriter) |
| **M11 Soul Fix** | `oracle.py:786-792` | 🟡 Keys match — investigate further | 1h (verify get_history output) |
| **ConnectionMetrics** | `database_connection_pool.py:96-145` | ✅ Pattern useful | 30min (adapt for MetricsDB) |

**Total estimated effort for findings**: ~6h (matches Phase 1 estimate)

---

*🔱 OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ legacy-mining ⬡ PHASE-1-INTEL*
