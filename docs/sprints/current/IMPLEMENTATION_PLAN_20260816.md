---
schema_version: "1.0"
document_type: sprint_plan
document_id: impl-plan-20260816
title: Omega Engine — Implementation Plan
status: ACTIVE
version: "1.0.0"
date: "2026-08-16"
owner: kali
tags: [sprint, implementation, omega-engine, phase-0]
priority: P0
depends_on: []
blocks: []
acceptance_gates:
  - "Phase 0 critical fixes verified"
  - "make test passes with honest counts"
cross_references:
  - docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md
  - docs/decisions/PIVOT_LOG.md
llm_metadata:
  token_budget: 8000
  chunk_strategy: section_per_ticket
  answer_first_sections: true
  self_contained_code: false
---

# 🔱 Omega Engine — Implementation Plan
**AP Token**: `AP-IMPL-PLAN-20260816`
**Date**: 2026-08-16
**Status**: ACTIVE — Ready for execution
**Owner**: Kali (sprint coordination) · Ma'at/N3 (build execution)

---

## 🎯 Executive Summary

This plan consolidates all findings from the F821 Crucible run, Qdrant migration research, and Sonnet/Gemini strategic reviews.

**Core Principle**: Qdrant is the primary vector store for high-performance deployments. `SQLiteVecAdapter` remains in the codebase as a zero-infra community fallback, but this deployment will execute a **hard cutover** to Qdrant to eliminate technical debt.

---

## 📋 Phase 0: Critical Fixes & Foundation

| # | Task | File | Effort | Impact |
|---|------|------|--------|--------|
| **0.1** | Fix query-aware L3 retrieval | `src/omega/oracle.py:313-316` | 15 min | **Critical** — L3 principles retrieved by entity_name, not query |
| **0.2** | Create `config/jit_rag.yaml` | New file | 30 min | **Critical** — No config exists; all hardcoded |
| **0.3** | Provider Chain Fix | `src/omega/oracle/providers.py` | 1 hr | **Critical** — Unified signatures |
| **0.3** | DPO Augmentation Script | `scripts/augment_dpo.py` | 2 hrs | **High** — Expand 14 pairs to ~150 |

### 0.1 Fix Query-Aware L3 Retrieval
```python
# src/omega/oracle.py line 313-316 (via context_builder.py)
# BEFORE:
principles = await self._selective_hydration.hydrate(
    query=entity_name,  # WRONG
    entity_name=entity_name,
)

# AFTER:
principles = await self._selective_hydration.hydrate(
    query=query,  # CORRECT - actual user query
    entity_name=entity_name,
)
```

### 0.2 Create `config/jit_rag.yaml`
Optimized, latency-aware config written (see `config/jit_rag.yaml`). Key decisions:
- **Fast Centroid Trigger** (replaces slow TARG)
- **Knapsack Token Budgeting** (VITAL-RAG style)
- **ONNX Reranker** (`jina-reranker-v1-tiny-en`)
- **Poison Pill Security** (quarantine at ingestion)
- **Semantic Cache** (0.98 threshold, 24hr TTL)

### 0.3 Provider Chain Fix
Unified all provider `generate()` signatures to accept `top_p` and `**kwargs`:
- BaseProvider, GoogleAIProvider, LocallmsterProvider, OllamaProvider, MockProvider ✅
- NativeGGUFProvider already correct ✅
- RemoteProvider already had `**kwargs` ✅

### 0.3 DPO Augmentation Script
Created `scripts/augment_dpo.py` — expands 14 pairs to ~150 via local LLM variations.

**Quality Note**: Using qwen3-1.7b for augmentation is acceptable for retrieval surface expansion:
- Only `prompt` field varies (situation description)
- `chosen`/`rejected` remain Opus/Hybrid quality
- Risk: noisy variations → slightly lower recall; original 14 pairs protected
- **Recommendation**: Use best available local model (qwen3-8b, llama3.1-8b) if available

---

## 📋 Phase 1: Qdrant Adapter Implementation

| # | Task | Effort | Notes |
|---|------|--------|-------|
| **1.1** | Implement `QdrantAdapter` (`IVectorStoreAdapter`) | 8 hrs | Full async gRPC support |
| **1.2** | Scalar int8 quantization config | 2 hrs | 4x RAM savings |
| **1.3** | Payload indexes | 2 hrs | entity_name, session_id, type, tags |
| **1.4** | Hybrid search via Qdrant native RRF | 4 hrs | prefetch + FusionQuery |

---

## 📋 Phase 2: Qdrant Infrastructure & Hard Cutover

| # | Task | Effort | Notes |
|---|------|--------|-------|
| **2.1** | Podman quadlet deployment | 30 min | 4GB limit, 70% CPU, telemetry disabled |
| **2.2** | Add `vector_store.type` toggle | 30 min | Set to `qdrant` |
| **2.3** | One-time Migration Script | 2 hrs | sqlite-vec → Qdrant (batch 1000, gRPC) |
| **2.4** | Parity test & Snapshot | 1 hr | Verify recall, then abandon sqlite-vec for this deployment |

---

## 📋 Phase 3: Shift-Left Observability & Advanced Routing

| # | Task | Effort | Notes |
|---|------|--------|-------|
| **3.1** | Node 0 Command Bridge (TUI) | 12 hrs | `textual` dashboard for Crucible, DPO, CI/CD monitoring |
| **3.2** | Cross-Entity Retrieval | 2 hrs | Allow MaKaLi to retrieve peer principles |
| **3.3** | ONNX-Optimized Reranker | 4 hrs | `jina-reranker-v1-tiny-en` via ONNX (sub-50ms latency) |

---

## 📋 Phase 4: Horizons (Strategic Builds)

| Horizon | Task | Effort | Priority |
|---------|------|--------|----------|
| **1. JIT Cognitive Scaffolding** | RAG for DPO: retrieve failure_mode_tag at dispatch | 4 hrs | P0 |
| **2. Shadow Mode Router** | Local plan vs DPO database → confidence → route | 6 hrs | P1 |
| **3. Autodidactic CI/CD** | Patch-First Epoch: Skeptical Verifier writes `.patch` files | 8 hrs | P1 |
| **4. Federated Gnosis** | Promotion by vote (3+ agents) | 4 hrs | P2 |

---

## 🚀 Execution Order

```
Week 1: Phase 0 (Complete) + Phase 1 (QdrantAdapter)
Week 2: Phase 2 (Infra + Hard Cutover)
Week 3: Phase 3 (Node 0 TUI + ONNX Reranker)
Week 4: Phase 4 (JIT RAG + Shadow Router)
Week 5: Phase 4 (Autodidactic CI/CD Patch-First + Federated Gnosis)
```

---

## 🔍 Success Criteria

| Metric | Target |
|--------|--------|
| L3 query-aware retrieval | ✅ Working (Phase 0) |
| JIT RAG config exists | ✅ `config/jit_rag.yaml` |
| DPO pairs vectorized | ✅ 150 pairs in `omega_vec_gemma_768` |
| QdrantAdapter implements IVectorStoreAdapter | ✅ All methods + hybrid search |
| Qdrant deployed & healthy | ✅ Podman quadlet, 4GB limit |
| Primary collection migrated | ✅ `omega_vec_gemma_768` ≥95% recall |
| Config toggle works | ✅ `vector_store.type: qdrant` |
| Cross-entity retrieval | ✅ MaKaLi council can retrieve peer principles |
| Parity tests pass | ✅ All 7 collections ≥95% recall |

---

## ⚠️ Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Qdrant OOM on 4GB | Medium | Scalar int8 (4x savings), `on_disk_payload=true`, `max_search_threads=4` |
| Recall regression | Low | Parity test per collection, fallback to sqlite-vec |
| gRPC connection exhaustion | Medium | `pool_size=20`, connection reuse, monitor metrics |
| MRL truncation unsupported | Medium | Verify embeddinggemma supports MRL; fallback to 768-dim |
| Snapshot restore failure | Low | Test restore weekly, keep sqlite-vec hot standby 30 days |

---

## 📌 Immediate Next Action

**Run DPO Augmentation** — Execute `scripts/augment_dpo.py` using best available local model.

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-16*
