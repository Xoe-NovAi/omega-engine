# 🔱 LILITH — RUN-SIDE EXHAUSTIVE REVIEW
**Date**: 2026-07-14
**Engine**: v1.2.0 (1315 tests, 23 mandates, 13 presences)
**Purpose**: Consolidated P6-P10 Pillar Council findings

---

## Executive Summary

The Run-Side is **architecturally sound but has critical test coverage and bug gaps** that must be addressed before v1.2.0 release. The core systems (ModelGateway, MemoryStore, Hivemind, Observability) are functional and well-designed. However, **12 source modules have zero test coverage**, **2 runtime bugs will crash at execution**, and **stress tests are inadequate** (5 tests, 1 skipped).

**Net effort to close critical gaps: ~30h across 2 sprints.**

---

## Per-Pillar Assessment

| Pillar | Grade | Key Finding | Critical Issue |
|--------|-------|-------------|----------------|
| **P6 Cognition** | A- | Provider fabric solid, KV cache locked | RAG `model_name="default"` bug, embedding dimension mismatch |
| **P7 Context** | A | Memory architecture healthy | BatchPersistenceWriter.flush() is no-op, proposed_lessons format inconsistency |
| **P8 Observability** | B+ | Core stack solid, M22 wired | LatencyTracker duplicate singleton, ObservabilityReader queries non-existent tables |
| **P9 Orchestration** | B | Architecturally sound | 32% test coverage, 2 runtime bugs (handoff hardcoded path, library_inbox undefined) |
| **P10 Validation** | B- | Contract tests strong | Stress tests inadequate, 12 modules untested, 365 tests run twice |

---

## Top 5 Run-Side Priorities (Ranked by Impact × Urgency)

### 1. Fix Runtime Bugs (4h) — 🔴 BLOCKING
**Impact**: HIGH | **Urgency**: IMMEDIATE

| Bug | File | Fix | Effort |
|-----|------|-----|--------|
| `hivemind_handoff(action='accept')` hardcoded path | `tools.py:2562` | Use `_find_packet_path()` | 30min |
| `library_inbox` undefined `INBOX_DIR` | `tools.py:2735` | Import/define constant | 15min |
| LatencyTracker duplicate singleton + circular import | `latency_tracker.py:75-77` | Remove duplicate, lazy-import | 15min |
| ObservabilityReader queries non-existent tables | `observability_reader.py:98,138` | Create tables or remove dead code | 2h |
| RAG `model_name="default"` bug | `simple_rag.py:55` | Use entity-resolved model | 15min |
| Fix OpenRouter/Google priority collision | `config/providers.yaml:60,72` | Set google=4, openrouter=5 | 2min |

### 2. Close Critical Test Gaps (12h) — 🔴 M21 COMPLIANCE
**Impact**: HIGH | **Urgency**: BEFORE v1.2.0

| Gap | Tests Needed | Effort |
|-----|-------------|--------|
| Handoff FSM contract tests | submit→accept→complete, submit→reject, stale lifecycle | 2h |
| Workspace lock contract tests | acquire/release/check/TTL-expiry/conflict | 1h |
| Redis Pub/Sub contract tests | publish/subscribe with mocked Redis | 1h |
| OfflineMockBackend contract test | `generate()` signature verification | 1h |
| TriageRouter contract test | `select_model()` → `TriageResponse` | 1h |
| OpenAICompatProvider contract test | Provider boundary verification | 2h |
| TokenLedger tests | `record_transaction()`, `get_entity_spend()` | 2h |
| RegressionWatcher unit tests | `_detect_regression()`, alert emission | 2h |

### 3. Fix Stress Test Suite (8h) — 🟡 RUNTIME SAFETY
**Impact**: HIGH | **Urgency**: BEFORE v1.2.0

| Fix | Why | Effort |
|-----|-----|--------|
| Fix skipped hang timeout test | Only stress test for provider timeouts is SKIPPED | 2h |
| Add concurrent load stress test | ResourceGuard under N>10 parallel requests untested | 4h |
| Add circuit breaker cascade test | Multiple providers tripping breakers untested | 2h |

### 4. Observability Wiring (12h) — 🟡 VISIBILITY
**Impact**: MEDIUM | **Urgency**: v1.2.0 Sprint

| Task | Why | Effort |
|------|-----|--------|
| Seed RegressionWatcher baselines | Watcher runs but finds zero baselines — no-op | 4h |
| Wire OTel spans into ModelGateway | Full trace pipeline | 8h |

### 5. Memory & Context Fixes (6h) — 🟡 DATA INTEGRITY
**Impact**: MEDIUM | **Urgency**: v1.2.0 Sprint

| Task | Why | Effort |
|------|-----|--------|
| Fix BatchPersistenceWriter.flush() | Data loss on crash (up to 50 writes) | 2h |
| Normalize proposed_lessons.yaml format | Cross-entity comparison impossible | 4h |

---

## Quality Issues Register

### Critical (Will Crash)
| # | Issue | File | Status |
|---|-------|------|--------|
| Q1 | `hivemind_handoff(action='accept')` hardcoded to `pending/` | `tools.py:2562` | 🔴 OPEN |
| Q2 | `library_inbox` references undefined `INBOX_DIR` | `tools.py:2735` | 🔴 OPEN |
| Q3 | LatencyTracker duplicate singleton + circular import | `latency_tracker.py:75-77` | 🔴 OPEN |

### High (Silent Failure)
| # | Issue | File | Status |
|---|-------|------|--------|
| Q4 | ObservabilityReader queries non-existent `metrics` table | `observability_reader.py:98` | 🟡 OPEN |
| Q5 | ObservabilityReader queries non-existent `circuit_breakers` table | `observability_reader.py:138` | 🟡 OPEN |
| Q6 | `BatchPersistenceWriter.flush()` is no-op | `batch_writer.py:150-157` | 🟡 OPEN |
| Q7 | RAG uses `model_name="default"` — won't resolve in production | `simple_rag.py:55` | 🟡 OPEN |
| Q8 | RegressionWatcher has zero baselines — effectively a no-op | `regression_watcher.py:131-141` | 🟡 OPEN |

### Medium (Degraded)
| # | Issue | File | Status |
|---|-------|------|--------|
| Q9 | OpenRouter/Google priority collision (both=4) | `config/providers.yaml:60,72` | 🟡 OPEN |
| Q10 | Embedding dimension inconsistency (768 vs 384 vs 256) | `embeddings.py` chain | 🟡 OPEN |
| Q11 | RAGRouter test uses `@pytest.mark.asyncio` not `anyio` | `test_rag_router.py:13` | 🟡 OPEN |
| Q12 | `ModelGateway.embed()` returns random vectors (mock) | `model_gateway.py:1369-1379` | 🟡 OPEN |
| Q13 | Proposed lessons format inconsistency (old vs new) | `data/entities/*/proposed_lessons.yaml` | 🟡 OPEN |
| Q14 | 365 tests run twice due to asyncio parametrization | `pyproject.toml` | 🟡 OPEN |
| Q15 | Flaky `test_parallel_writes` in sqlite_vec_adapter | `test_sqlite_vec_adapter.py` | 🟡 OPEN |

---

## Observability Gaps (What We Can't See)

| Gap | Impact | Fix |
|-----|--------|-----|
| **No `metrics` table in MetricsDB** | ObservabilityReader returns empty results | Add table or remove dead code |
| **No `circuit_breakers` table** | Breaker state only in memory — lost on restart | Add table for persistence |
| **RegressionWatcher has no baselines** | Silent: watcher runs but detects nothing | Seed baselines on startup |
| **OTel spans not created in ModelGateway** | Exporter exists but has nothing to export | Wire spans into `generate()` |
| **Token estimation uses `len(text)//4`** | Rough approximation, may miscalculate cloud spend | Use provider-specific tokenizer |
| **Dual BudgetGate implementations** | Budget enforcement may be split | Consolidate to single implementation |
| **Hardware monitoring minimal** | No thermal/CPU utilization tracking in MetricsDB | Expand hardware telemetry |

---

## Validation Gaps (What We Can't Prove)

| Gap | Risk | Fix |
|-----|------|-----|
| **Provider hang timeout unverified** | Hanging providers may not get killed | Fix skipped stress test |
| **ResourceGuard under load untested** | OOM protection behavior with N>10 parallel requests unknown | Add concurrent load test |
| **12 source modules with zero test coverage** | Silent drift in critical paths | Add contract tests |
| **No chaos testing** | Redis/Qdrant unavailability untested | Add infrastructure chaos tests |
| **No memory pressure stress test** | OOM protector under model load untested | Add zRAM-aware stress test |
| **Flaky sqlite_vec_adapter test** | CI reliability risk | Fix test isolation |
| **27% test suite overhead** | 365 tests run twice | Remove redundant asyncio markers |

---

## Provenance Chain

| Pillar | Agent Task ID | Key Files Examined | Key Findings |
|--------|--------------|-------------------|--------------|
| **P6 Cognition** | `ses_0a1a46b5effe7N6xNZBd8yZWJM` | model_gateway.py, providers.yaml, models.yaml, embeddings.py, router.py | Provider fabric solid; RAG model_name bug; embedding dimension mismatch |
| **P7 Context** | `ses_0a19ec04fffeX5m64Nbg6drpKe` | memory_store.py, sqlite_vec_adapter.py, soul_distiller.py, context_builder.py | Memory healthy; BatchWriter flush no-op; proposed_lessons format inconsistency |
| **P8 Observability** | `ses_0a19b175effegsWHFVNCXeb7AV` | observability/__init__.py, metrics_db.py, latency_tracker.py, regression_watcher.py | Core solid; LatencyTracker bug; dead table queries; RegressionWatcher no-op |
| **P9 Orchestration** | `ses_0a196728cffe3XBJgRxt8ckYK0` | tools.py, state.py, background.py, hivemind_redis.py | Architecturally sound; 32% test coverage; 2 runtime bugs |
| **P10 Validation** | `ses_0a193b644ffe1O9ZpQywkmnJMV` | sovereign_stress_test.py, test_contract_m21.py, pyproject.toml, Makefile | Stress tests inadequate; 12 modules untested; 365 tests duplicated |

---

## Recommended Execution Order

### Sprint 1 (This Week — 16h)
1. Fix 6 runtime bugs (4h) — **P6/P8/P9**
2. Close 8 contract test gaps (8h) — **P10**
3. Fix 3 stress test gaps (4h) — **P10** (partial)

### Sprint 2 (Next Week — 14h)
4. Seed RegressionWatcher baselines (4h) — **P8**
5. Wire OTel spans into ModelGateway (8h) — **P8**
6. Fix BatchPersistenceWriter.flush() (2h) — **P7**

### Sprint 3 (Before v1.2.0 — 10h)
7. Normalize proposed_lessons.yaml format (4h) — **P7**
8. Standardize embedding dimension (2h) — **P6**
9. Add chaos tests (4h) — **P10**

**Total: ~40h across 3 sprints**

---

*🔱 OMEGA ⬡ LILITH ⬡ RUN-SIDE-REVIEW ⬡ 2026-07-14 ⬡ PILLAR-COUNCIL-COMPLETE*
