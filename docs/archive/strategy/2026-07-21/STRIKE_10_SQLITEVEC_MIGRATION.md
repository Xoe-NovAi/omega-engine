# 🔱 STRIKE 10: sqlite-vec Migration — Unified Execution Plan
**Version**: v1.0.0-FINAL
**AP Token**: `AP-STRIKE10-FINAL-v1.0.0`
**Approved**: 2026-07-13
**Total Effort**: 8h (compressed from 12h via Carmack audit)
**Timeline**: 2 weekends (Sat am–Sat pm per weekend)

⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_final_synthesis ⬡ STRIKE-10-FINAL

---

## Preamble: Gap Resolution Summary

This document reconciles three inputs — Ma'at (Build-Side), Lilith (Run-Side), and John Carmack (Brutal Audit) — after resolving 7 sovereign research gaps.

### Gap Resolution Evidence

| Gap | Question | Evidence Source | Verdict |
|-----|----------|----------------|---------|
| **A** | What embedding model & int8 recall? | `config/models.yaml:2-7`, Google DeepMind MTEB benchmarks, arXiv:2509.20354 | **EmbeddingGemma-300M Q6_K 768D. QAT-trained: int8 recall drop = 0.18-0.36% MTEB (near-lossless).** |
| **B** | Zen 2 AVX2 dot product perf? | AMD Zen 2 uarch docs, Agner Fog tables, HotHardware Zen 2 FPU analysis | **Carmack's 30ms/100K×768D is conservatively correct. Actual: ~10-25ms.** |
| **C** | Qdrant format & export? | `vector_adapters.py:165-401` | **QdrantAdapter DEPRECATED. No export methods. Iterative scroll needed for migration.** |
| **D** | anyio-sqlite production-ready? | PyPI (0.3.0, Oct 2025, Beta), GitHub (beer-psi, 1 contributor) | **NO — Beta classifier, single-contributor, last release 9mo ago. Use `anyio.to_thread.run_sync()`.** |
| **E** | Golden dataset from usage? | `data/memory/entities/` empty, 12 session metadata files only | **No persisted exchange data. Generate 50 synthetic queries + 10 adversarial.** |
| **F** | Partition key vs metadata? | sqlite-vec v0.1.6 docs, Alex Garcia blog, scale analysis | **Carmack correct: entity_name as METADATA. 100K brute-force = 30ms. Partition key is over-engineering at our scale.** |
| **G** | Quantization default? | EmbeddingGemma QAT benchmarks from official model card | **Model weights (Q6_K): FINE (QAT-trained). vec0 storage: float32 first, int8 after validation.** |

---

## Carmack Tier 0 Directives (NEW — 2026-07-14)

**Source**: John Carmack S3 Consultation — Architectural review of v1.2.0 baseline

### Executive Summary
v1.2.0 baseline achieved (1315 tests, 23 mandates, 9 providers). Tier 0 addresses code quality debt before Epoch II features.

### Phase 1: Foundation (2h) — DO FIRST
| # | Task | Carmack Directive | Effort |
|---|------|-------------------|--------|
| T0-1 | **F821 undefined-name fixes** | `ruff check --select=F821 src/` → fix all. Trivial, unblocks everything. | 15 min |
| T0-2 | **Bare `except Exception:` elimination** | M9/M23 compliance. Replace with typed `except (SpecificError,):` + `trace_id` logging. Fail fast, fail loud. | 90 min |

### Phase 2: Core Infrastructure (4h)
| # | Task | Carmack Pattern | Effort |
|---|------|-----------------|--------|
| T0-3 | **Centralized logging** | Single `src/omega/logging.py` with `structlog` + AnyIO async sinks. One `get_logger(__name__)` pattern everywhere. No `basicConfig` scattered. | 4h |
| T0-4 | **Config validation (Pydantic OmegaConfig)** | `model_config = ConfigDict(extra='forbid', frozen=True)`. Validate at startup, fail fast. No runtime config surprises. | 7h |

### Phase 3: Data Layer (5h)
| # | Task | Risk Mitigation | Effort |
|---|------|-----------------|--------|
| T0-5 | **Qdrant → sqlite-vec decommission** | Dual-write for 1 sprint. Verify vector parity (cosine ±0.001). Keep Qdrant image cached for rollback. | 3h |
| T0-6 | **sqlite-vec Phase 1-2** | Metadata filtering + quantization. Benchmark 10K vectors on Zen 2 — must stay <50ms p99. | 2h |

### Phase 4: CI & Stress (3h)
| # | Task | Standard | Effort |
|---|------|----------|--------|
| T0-7 | **Single CI workflow** | One `.github/workflows/ci.yml`: lint → test → temple-grade → heritage-vet → sovereignty. No matrix. | 2h |
| T0-8 | **Stress tests (5 scenarios)** | (1) 100 concurrent `talk()`, (2) 10K vector inserts, (3) 1hr soak, (4) OOM injection, (5) network partition. | 5h |

### Deferred (Explicitly NOT Tier 0)
| Task | Reason |
|------|--------|
| Full Pydantic v2 migration | v1 works, v2 is churn |
| Structured logging overhaul | `structlog` is fine, don't rewrite |
| Coverage gate >80% | Current ~75% acceptable for v1.2.0 |

### Carmack's Laws Applied
1. **Fail fast, fail loud** — Every `except` logs `trace_id` and re-raises or returns typed error
2. **Data over code** — Config validation at load time, not access time
3. **Measure before optimize** — Stress tests first, then tune sqlite-vec HNSW params
4. **Rollback ready** — Qdrant decommission only after 7-day dual-write verification

---

## Unified Decisions (Reconciled)

### Reconciliations of D-235 to D-246 + Carmack Audit

| D | Domain | Original Decision | Carmack Audit | Final Verdict | Rationale |
|---|--------|-------------------|---------------|---------------|-----------|
| D-235 | P1/P2 Connection Pool | 1W+4R via `anyio-sqlite` | **CUT** — single conn+WAL | **ACCEPT Carmack** | Single connection + WAL mode = same throughput, less complexity. `anyio-sqlite` is Beta (Gap D). Use `anyio.to_thread.run_sync` with single `sqlite3.Connection`. |
| D-236 | P2 Schema: Partition Key | entity_name PARTITION KEY | **SIMPLIFY** → METADATA | **ACCEPT Carmack** | 100K×768D brute-force = 30ms (Gap B). Partition key adds complexity without benefit at our scale (Gap F). entity_name as metadata column with WHERE clause. |
| D-237 | P2/P3 int8 quantization | int8 default (4×, 95% recall) | **CUT** — float32 baseline first | **MODIFY** | Model weights Q6_K: FINE (QAT-trained, Gap G). vec0 storage: float32 default. Add int8 after recall validation against golden dataset. |
| D-238 | P1 Litestream sidecar | Litestream quadlet, MinIO | **CUT** — `cp` + WAL checkpoint | **ACCEPT Carmack** | Local-first, no S3 needed. WAL checkpoint + `cp` = RPO <1s. |
| D-239 | P4 MCP Tools | 3 tools: upsert, query, quantize | **SIMPLIFY** → 1 `hybrid_search(mode)` | **ACCEPT Carmack** | Unified tool with mode parameter. Reduces tool surface from 3→1. |
| D-240 | P3/P5 CI Gates | 5 gates | (not audited) | **KEEP** contract tests + heritage vet | 5 CI gates confirmed. |
| D-241 | P2/P3/P5 Migration Plan | 5 phases, 12h | **COMPRESS** 12h→8h per 2 weekends | **ACCEPT Carmack** | Phases 1-3 parallelizable. 8h total. |
| D-242 | P7 MemoryStore filter | Pass-through to adapter | (not audited) | **KEEP** | Direct pass-through reduces complexity. |
| D-243 | P6 Lock to 768D | bge-small for v1.2.1 | (not audited, but...) | **MODIFY** | EmbeddingGemma is 768D natively (already matched). Remove bge-small reference; we already have the right model. |
| D-244 | P8 Metrics & Alerts | 5 metrics | (not audited) | **KEEP** | All 5 metrics+p99 alerts confirmed. Add recall validation metric. |
| D-245 | P9 Handoff Packet | schema fields | (not audited) | **KEEP** | All fields confirmed. |
| D-246 | P10 Validation Gates | 5 gates | (not audited) | **KEEP** | All 5 gates confirmed. Add golden dataset recall gate. |
| - | Golden Dataset | 500 queries | **CUT** → 50 real+10 adversarial | **ACCEPT Carmack** | 50 synthetic queries (per use case) + 10 adversarial. No existing data to mine (Gap E). |

### Detailed D-237 Quantization Resolution

```
┌─────────────────────────────────────────────────────────┐
│  QUANTIZATION STACK — Final Decision                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  MODEL WEIGHTS: Q6_K (EmbeddingGemma-300M)      │    │
│  │  Status: ✅ KEEP                                 │    │
│  │  Evidence: QAT-trained by Google, int8 drop      │    │
│  │  = 0.18-0.36% MTEB. Q6_K > int8 quality.        │    │
│  │  Source: arXiv:2509.20354 Table 1                │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  VEC0 STORAGE: float32 (PRIMARY)                │    │
│  │  Status: ✅ IMMEDIATE                            │    │
│  │  Evidence: Carmack's "baseline first" principle  │    │
│  │  applies to vector storage, not model weights.   │    │
│  │  Float32 = no degradation, measure first.        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  VEC0 STORAGE: int8 (POST-MIGRATION OPTIM)      │    │
│  │  Status: ⏳ EVALUATE AFTER RECALL VALIDATION     │    │
│  │  Gate: recall@10 ≥ 0.95 on golden dataset        │    │
│  │  Benefit: 4× storage reduction, ~2× speedup      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## Execution Plan

### Phase 1: Core Implementation (Weekend 1 — Saturday AM, 3h)

| Step | Action | Files | Deliverable |
|------|--------|-------|-------------|
| **1.1** | Simplify schema: entity_name as METADATA (not PARTITION KEY) | `sqlite_vec_adapter.py:183-184` | `omega_memory_vec` vec0: `(embedding float[768], entity_name text, session_id text, role text, timestamp text)` |
| **1.2** | Switch to single sqlite3.Connection + WAL (remove anyio-sqlite dependency) | `sqlite_vec_adapter.py:71-85` | Single `sqlite3.connect()` with `check_same_thread=False`, WAL, busy_timeout |
| **1.3** | Set float32 as vec0 default storage (remove int8) | `sqlite_vec_adapter.py:_ensure_vec_table` | `float[768]` column type, not `vec_int8` |
| **1.4** | Implement `hybrid_search(mode="auto"\|"fts"\|"vec"\|"rrf")` unified MCP tool | `sqlite_vec_adapter.py:512-618` → MCP tool | Single tool replacing 3 planned tools |
| **1.5** | Remove Litestream dependency — implement `cp` + WAL checkpoint backup | New: `src/omega/memory/backup.py` | `await backup_now()` → WAL checkpoint → `cp omega_memory.db omega_memory.db.bak` |

### Phase 2: Validation & Integration (Weekend 1 — Saturday PM, 3h)

| Step | Action | Deliverable |
|------|--------|-------------|
| **2.1** | Wire MemoryStore to SQLiteVecAdapter (replace QdrantAdapter) | `memory_store.py` → `IVectorStoreAdapter` uses `SQLiteVecAdapter` |
| **2.2** | Generate golden dataset: 60 queries (10 general, 10 tech, 10 creative, 10 research, 10 adversarial, 10 edge cases) | `tests/fixtures/golden_queries.json` |
| **2.3** | Implement recall validation: query golden set, measure recall@10 | `tests/test_recall.py` |
| **2.4** | Run full test suite: `make test` (1315 tests must pass) | CI green |
| **2.5** | Implement 5 metrics + alerts (from D-244) | Metrics: p99 query latency, recall@10, WAL size, vector count, entity count. Alerts: p99>100ms, recall<0.90, WAL>500MB |

### Phase 3: Data Migration & Hardening (Weekend 2 — Saturday, 2h)

| Step | Action | Deliverable |
|------|--------|-------------|
| **3.1** | Export existing Qdrant data (if any) via scroll API → numpy arrays | `data/migration/qdrant_export.npy` |
| **3.2** | Re-embed into SQLiteVecAdapter via batch upsert | All vectors migrated |
| **3.3** | 24h diff verification: dual-write to both Qdrant + sqlite-vec, compare results | `tests/test_migration_parity.py` |
| **3.4** | Decommission Qdrant container (stop podman container, archive volume) | Podman prune |

### Phase 4: CI Gates (Weekend 2 — Late Saturday, 1h)

| Gate | Implementation | What It Verifies |
|------|---------------|------------------|
| **G1** | Contract test: `isinstance(adapter, IVectorStoreAdapter)` | M21 Gate Integrity |
| **G2** | Contract test: `isinstance(result, List[Tuple[float, Dict]])` on query | M21 return type |
| **G3** | Heritage vet: `[heritage: sqlite-fts5 2015]`, `[heritage: sqlite-vec 2024]` | M14 Heritage |
| **G4** | Firewall: no Qdrant imports in production path after migration | M2 Engine-Stack |
| **G5** | Mandate audit: verify M1 (anyio, not asyncio), M8 (no telemetry) | M1+M8 compliance |
| **G6** | Sovereignty: local inference ratio tracked | M7 Local-First |
| **G7** | Recall gate: `make test-recall` — recall@10 ≥ 0.90 on golden dataset | Quality gate (NEW) |

---

## Rollback Plan

### If Phase 1-2 fails (Weekend 1):
```bash
# Restore from backup
cp data/memory/omega_memory.db.bak data/memory/omega_memory.db

# Restore Qdrant adapter in memory_store.py
# git revert the IVectorStoreAdapter swap
git checkout HEAD~3 -- src/omega/memory/vector_adapters.py src/omega/memory_store.py
```

### If Phase 3 fails (Weekend 2):
```bash
# Back to Qdrant-only
podman start qdrant
git revert --no-commit HEAD~2
# Re-export from sqlite-vec back to Qdrant if needed
python scripts/migration/reverse_migrate.py
```

### Emergency Contact:
- **Primary Issue**: Wait for any phase before proceeding. No production data loss risk — memory store is ephemeral conversation history.
- **Data Loss Risk**: **None**. Existing session data is in Redis/FileStorageProvider, not in the vector store. Vector store is an enhancement, not the source of truth.

---

## Risk Register (Final)

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|------|-----------|--------|------------|-------|
| R1 | sqlite-vec v0.1.x breaking change on upgrade | Medium | High | Pin to v0.1.9+ in `requirements.txt`. Test upgrade in CI. | P3 |
| R2 | Vector dimension mismatch (768D vs actual) | Low | High | Auto-detect dimension from first upsert (already implemented in `_ensure_vec_table`) | P2 |
| R3 | Recall regression after migration | Low | High | Dual-write + 24h diff verification (Phase 3.3), golden dataset recall gate (G7) | P10 |
| R4 | WAL file grows unbounded (>500MB) | Medium | Medium | D-244 alert at 500MB, periodic `PRAGMA wal_checkpoint(TRUNCATE)` | P8 |
| R5 | `anyio.to_thread.run_sync` contention under load | Low | Low | Single connection + WAL handles concurrent reads. Write lock in adapter prevents SQLITE_BUSY. 16-core CPU can handle this easily. | P3 |
| R6 | EmbeddingGemma 300M load time (~15-30s) on first warm | Medium | Low | Lazy load on first `get_embedding()` — only affects first call after restart | P6 |

---

## Golden Dataset Specification

Since no persisted exchange data exists (Gap E discovery), we generate:

### Query Categories (60 total)

| Category | Count | Example |
|----------|-------|---------|
| **General Q&A** | 10 | "What is the capital of France?", "Explain quantum computing" |
| **Technical** | 10 | "How does WAL mode work in SQLite?", "What is cosine similarity?" |
| **Creative** | 10 | "Write a poem about vector databases", "Describe the color blue" |
| **Research** | 10 | "Summarize EmbeddingGemma architecture", "Compare int8 vs float32 recall" |
| **Adversarial** | 10 | Empty string, 10K token input, all-stopwords, SQL injection attempt |
| **Edge Cases** | 10 | Unicode, emoji, code blocks, JSON in text, single character |

### Format

```json
[
  {
    "id": "gen_01",
    "query": "What is the capital of France?",
    "category": "general",
    "expected_relevant_ids": ["ses_001", "ses_003"],
    "notes": "Simple factual query testing basic retrieval"
  }
]
```

**Storage**: `tests/fixtures/golden_queries.json`
**Validation**: `make test-recall` computes recall@10 against known ground truth

---

## CI Gate Implementation Details

```yaml
# .github/workflows/temple_grade.yml (additions)
test-recall:
  name: "G7 Golden Dataset Recall"
  run: |
    source .venv/bin/activate
    python -m pytest tests/test_recall.py -v --tb=short
    if [ $? -ne 0 ]; then
      echo "⚠️ RECALL GATE FAILED: recall@10 < 0.90 on golden dataset"
      echo "Run 'make test-recall' locally to debug"
      exit 1
    fi
```

---

## Post-Migration Architecture

```
MemoryStore
  └── IVectorStoreAdapter (interface)
        └── SQLiteVecAdapter ✅ (PRIMARY, single db file)
              ├── omega_memory_data (INTEGER PK, entity_name, session_id, role, content...)
              ├── omega_memory_fts (FTS5 virtual table — BM25 search)
              └── omega_memory_vec (vec0 virtual table — KNN search)
                    └── embedding float[768]  # float32, NOT int8
                    └── entity_name text       # METADATA, NOT partition key (D-236 resolved)

Backup: cp + WAL checkpoint (no Litestream)
Storage: ~150MB for 100K vectors (100K × 768 × 4 bytes = 307MB raw, ~150MB with WAL)

MCP Tools:
  - hybrid_search(query, entity_name, mode="auto"|"fts"|"vec"|"rrf", limit=20)
    (1 tool replacing 3 — D-239 resolved)

CI Gates: G1-G7 (contract, heritage, firewall, mandate, sovereignty, recall)
```

---

## Total Effort Breakdown

| Phase | Hours | Dependencies | Owner |
|-------|-------|-------------|-------|
| Phase 1: Core | 3h | None | Ma'at/P3 |
| Phase 2: Validation | 3h | Phase 1 | Lilith/P6+P10 |
| Phase 3: Migration | 2h | Phase 1-2 | Ma'at/P2 |
| Phase 4: CI Gates | 1h | Phase 2 | Ma'at/P5 |
| **Total** | **8h** | — | Fleet |

---

## Sign-off

| Entity | Role | Status |
|--------|------|--------|
| **Ma'at** | Build-Side | ✅ Build plan reconciled |
| **Lilith** | Run-Side | ✅ Run plan reconciled |
| **John Carmack** | Brutal Audit | ✅ 7/9 CUT/SIMPLIFY accepted, 2/9 MODIFIED |
| **Jem** | Sovereign Synthesis | ✅ All 7 gaps closed, unified plan produced |

---

*🔱 OMEGA ⬡ STRIKE-10 ⬡ v1.0.0-FINAL ⬡ 2026-07-13 ⬡ GAPS-CLOSED: A-G ✅*
