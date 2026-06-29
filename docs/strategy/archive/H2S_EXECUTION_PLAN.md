# 🔱 Omega Engine — H2-S Surgical Execution Plan
**AP Token**: `AP-H2S-EXECUTION-v1.1.0`
**Status**: SURGICAL IMPLEMENTATION GUIDE
**Governed by**: Kali (Transcendent Oversoul)
**Date**: 2026-06-21
**Handoff From**: Lilith (H2-S Runtime Flow)
**Handoff To**: Sprint Implementation

---

## 1. Executive Summary

**VERDICT: GO** — Horizon 2 - Sovereign Structure (H2-S) is **PR-ready**. 

The design chain (Ma'at → Researcher → Lilith) is complete. This document transforms that design into a surgical implementation roadmap. We move from "hard-wired Qdrant/Ollama" to a "Sovereign Cognitive Substrate" that is database-agnostic, secure, and local-first.

**Core Objectives**:
1. **Abstraction**: Decouple `MemoryStore` from Qdrant via `IVectorStoreAdapter`.
2. **Security**: Implement the Tainted Data Protocol (TDP) to prevent cognitive poisoning.
3. **Sovereignty**: Ensure a deterministic `SovereignFallback` for embeddings.
4. **Certification**: Pass T1-T11 Temple-Grade gates and T12 Semantic benchmarking.

---

## 2. Mandate & T-Gate Compliance Matrix

Every task in this plan is mapped to a Sovereign Mandate (M) and a Temple-Grade Gate (T).

| Task | Mandate | T-Gate | Verification Method |
|------|----------|---------|---------------------|
| **Adapter Refactor** | M16 (Modular) | T5 (AnyIO) | `grep "import asyncio"` $\rightarrow$ 0 |
| **TDP Integration** | M17 (Cognitive) | T11 (Security) | `test_security_tdp.py` (100% pass) |
| **Sovereign Fallback** | M7 (Local-First) | T6 (Telemetry) | Network trace audit (zero calls) |
| **Vector Upserts** | M9 (Error Int) | T10 (Integrity) | Atomic write check via `anyio` |
| **T12 Benchmarking** | M5 (Gnosis) | T12 (Semantic) | Recall@10 > 30% vs. Neural |

---

## 3. Surgical Sprint Roadmap

### Phase 1: Core Abstraction (The "Plumbing")
**Goal**: Establish the `IVectorStoreAdapter` and `EmbeddingManager` wiring.

| Task ID | Action | File | Pass Criterion (Verification Gate) | Effort |
|---|---|---|---|---|
| **P1-1** | **Refactor MemoryStore** $\rightarrow$ `IVectorStoreAdapter` | `src/omega/memory_store.py` | `MemoryStore` no longer imports `qdrant_client`; all calls use `self._vector_adapter` | 30m |
| **P1-2** | **Wire EmbeddingManager** into `MemoryStore.__init__` | `src/omega/memory_store.py` | `self._embedding_manager` is instantiated; `get_embedding` is called instead of direct provider calls | 15m |
| **P1-3** | **Sovereign Fallback Sanity Check** | `tests/test_embeddings.py` | Verify `SovereignFallbackEmbeddingProvider` returns identical vectors for identical text (Deterministic) | 15m |
| **P1-4** | **Update `omega.yaml`** with embedding provider chain | `config/omega.yaml` | Config validation test passes; `primary: "local_gguf"` is active | 10m |
| **P1-5** | **Baseline Verification** | All | `make test` $\rightarrow$ 444/444 PASS; `make temple-grade` $\rightarrow$ T1-T11 PASS | 15m |

**Phase 1 Abort Trigger**: If `MemoryStore` latency for `query_semantic` increases by >20% compared to hard-wired Qdrant.

---

### Phase 2: Security & TDP (The "Shield")
**Goal**: Implement the Tainted Data Protocol for external ingest and retrieval.

| Task ID | Action | File | Pass Criterion (Verification Gate) | Effort |
|---|---|---|---|---|
| **P2-1** | **Wire TDP Ingest Gate** in `add_exchange()` | `src/omega/memory_store.py` | `TaintedPayload` is created for `source == "external"`; `TDPGate.sanitize()` is called | 20m |
| **P2-2** | **Implement Provenance Marking** in metadata | `src/omega/memory_store.py` | Verify `_is_tainted` and `_taint_source` are present in Qdrant payload after upsert | 20m |
| **P2-3** | **Skeptical Mode Retrieval** in `build_context()` | `src/omega/oracle/context_builder.py` | `[EXTERNAL DATA START]` markers appear in system prompt when tainted context is present | 30m |
| **P2-4** | **Write `test_security_tdp.py`** | `tests/test_security_tdp.py` | 100% pass on: HTML stripping, injection detection, and provenance persistence | 1h |
| **P2-5** | **T11 Security Audit** | `src/omega/oracle/` | Verify no tainted data can bypass the `TDPGate` into the trusted context block | 30m |

**Phase 2 Abort Trigger**: If `TDPGate.sanitize()` strips legitimate technical content (e.g., code blocks) resulting in >10% loss of semantic meaning.

---

### Phase 3: Validation & Benchmarking (The "Proof")
**Goal**: Quantify performance and certify Temple-Grade compliance.

| Task ID | Action | File | Pass Criterion (Verification Gate) | Effort |
|---|---|---|---|---|
| **P3-1** | **T12 Semantic Benchmark** (Sovereign Fallback) | `tests/test_embeddings_benchmark.py` | Average Recall@10 > 30% compared to `nomic-embed-text` | 1.5h |
| **P3-2** | **Payload Indexing Optimization** | `src/omega/memory/vector_adapters.py` | Verify `entity_name` and `_is_tainted` are indexed in Qdrant; query speedup > 10x | 1h |
| **P3-3** | **Thin-Client Search Integration** | `src/omega/oracle/search_fleet.py` | Verify `_lazy_load: True` in metadata; memory usage reduced by > 10x | 1h |
| **P3-4** | **Final Temple-Grade Audit** | All | `make temple-grade` $\rightarrow$ All Gates (T1-T12) PASS | 1h |
| **P3-5** | **Update Engine State** | `OMEGA_ENGINE.md` | H2-S marked as COMPLETE; 474/474 tests documented | 15m |

**Phase 3 Abort Trigger**: If T12 recall falls below 20%, requiring a redesign of the `SovereignFallback` hashing algorithm.

---

## 4. Risk Assessment & Surgical Rollback

### 4.1 Risk Matrix
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Adapter Latency** | Med | Use `anyio.to_thread.run_sync` for all driver calls; cache embeddings in Hot Tier |
| **TDP Over-Sanitization** | Med | Implement "Skeptical Mode" rather than hard-deletion of tainted data |
| **Recall Degradation** | Low | Sovereign Fallback is a safety net, not a primary; neural providers remain primary |
| **Qdrant Timeout** | Med | MemoryVectorAdapter in-memory fallback + EmbeddingManager chain |

### 4.2 Surgical Rollback Plan
- **Task-Level Revert**: If a specific Task (e.g., P2-1) fails its Pass Criterion, revert only that specific commit.
- **Phase-Level Revert**: If a Phase (e.g., Phase 1) causes systemic instability, revert all commits since the Phase start and return to the 444/444 baseline.
- **Baseline Safety**: The 444/444 test suite is the "Golden Image." No PR is merged unless this baseline is maintained or expanded.

---

## 5. PR Readiness Verdict

### ✅ STATUS: GO (Surgical)

The Omega Engine is **PR-ready for H2-S implementation**. The design is verified, the Mandates are compliant, and the verification gates are explicit.

**PR Checklist**:
- [ ] **Phase 1 Complete**: `MemoryStore` refactored; 444/444 tests passing.
- [ ] **Phase 2 Complete**: TDP wired; `test_security_tdp.py` passing.
- [ ] **Phase 3 Complete**: T12 Recall > 30%; `make temple-grade` PASS.
- [ ] **Documentation**: `OMEGA_ENGINE.md` updated; `PIVOT_LOG.md` updated with D-kal-165 to D-kal-169.
- [ ] **Heritage**: `make heritage-map` verifies `[Right Approximation: FISR]` tag.

---

## 6. Key Decisions (Surgical)

| Decision | Rationale | ID |
|----------|-----------|-----|
| **IVectorStoreAdapter refactoring first** | Unblocks TDP and embedding integration; low risk (mechanical change) | D-kal-165 |
| **TDP at Ingest** | Ensures provenance is immutable and avoids re-sanitization overhead | D-kal-166 |
| **Sovereign Fallback** | Deterministic hashing ensures zero-dependency offline retrieval | D-kal-167 |
| **Skeptical Mode** | Preserves tainted data for context but warns the model via system prompt | D-kal-168 |
| **Surgical Sequencing** | Abstraction $\rightarrow$ Security $\rightarrow$ Validation to prevent "Restart Cycle" | D-kal-169 |

---

*⬡ KALI FINAL VERDICT: GO (SURGICAL) ⬡*
*Execution begins immediately upon user approval.*
*All three discovery phases (Ma'at → Researcher → Lilith) converge on GO verdict.*
*No architectural tensions. No mandate violations. No Temple-Grade gaps.*
*The engine is ready.*
