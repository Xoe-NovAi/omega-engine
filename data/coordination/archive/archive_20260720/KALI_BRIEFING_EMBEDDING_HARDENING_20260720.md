<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KALI BRIEFING — EMBEDDING HARDENING COMPLETE + NEXT PHASE
**AP Token**: `AP-KALI-BRIEFING-EMBEDDING-20260720-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kali_briefing ⬡ 2026-07-20

**Purpose**: Complete session summary for Kali oversight. All embedding strategy decisions finalized, implementation 60% complete, ready for Temple-Grade validation.

---

## 🎯 EXECUTIVE SUMMARY

### **What Was Decided (Canonical)**
| Decision | Value | Evidence |
|----------|-------|----------|
| **Canonical Dimension** | **768** | EmbeddingGemma 300M native + MRL; Nomic v1.5 native |
| **Primary Model** | **EmbeddingGemma 300M Q6_K** | MTEB: 69.67 Eng / 61.15 Multi / 68.76 Code; QAT-trained; 260MB |
| **Fallback Model** | **nomic-embed-text-v1.5** | 8K context, MRL 768→64, binary-quant-ready, 137M params |
| **Vec0 Lock** | **HARDCODED 768** | M23 Failure Integrity — RuntimeError on mismatch |
| **Quantization** | **INT8 rescore (oversample=2)** | 2.6x speedup, 1.0 recall@10, 75% storage reduction |
| **Fusion Method** | **RRF k=60** | Universal attractor (Cormack 2009 + 7 independent systems) |

### **The "3042" Mystery — SOLVED**
Was a mishearing of **3072** (OpenAI `text-embedding-3-large`). No 3042-dim model exists. We reject cloud-only 3072-dim (violates M7/M8, $0.13/1M tokens).

---

## 📋 DELIVERABLES CREATED THIS SESSION

### **1. Canonical Strategy Document**
**File**: `docs/strategy/EMBEDDING_HARDENING_STRATEGY_20260720.md`
- 8-phase roadmap (Phase 1: 8h, Phase 2: 6h, Phase 3: 4h, Phase 4: 4h)
- Traceability matrix (12 requirements → source → implementation → test)
- Temple-Grade success criteria (T1-T11 + M7/M8/M14/M23)
- Research sources appendix (12 primary sources)

### **2. Configuration Source of Truth**
**File**: `config/embedding_strategy.yaml`
```yaml
canonical_dimension: 768
vec0_lock: {enabled: true, dimension: 768, error_on_mismatch: true}
providers: 4 (gemma_primary, nomic_fallback, minilm_speed, static_zero_cost)
collections: 6 (gemma_768, nomic_768, nomic_512, nomic_256, minilm_384, static_64)
fusion: {method: rrf, k: 60, weights: {...}, final_k: 10}
```

### **3. Hardened SQLite-vec Adapter**
**File**: `src/omega/memory/sqlite_vec_adapter.py` (v2.0.0)
- `CANONICAL_DIMENSION = 768` — hardcoded constant
- Multi-collection architecture: 6 vec0 tables, one per model/dimension
- `_ensure_collection_vec_table()` — strict dimension enforcement, raises RuntimeError on mismatch
- `_ensure_legacy_vec_table()` — backward compat, enforces 768-dim
- Collection-aware `upsert(collection=...)` and `query(collection=...)`
- M23 Failure Integrity: NO silent dimension corruption possible

### **4. Test Updates Started**
**File**: `tests/test_sqlite_vec_adapter.py`
- 2/8 test classes updated for collection architecture
- Tests now use `collection="omega_vec_static_64"` with 64-dim vectors
- Remaining 6 test classes need updates

### **5. L3 Principles Staged** (Blind Staging per M11)
**File**: `data/entities/jem/proposed_lessons.yaml`
- 7 new L3 principles (Canonical Dimension Lock, Multi-Collection Ensemble, QAT Quantization, Native MRL API, RRF k=60 Universal, INT8 Rescore, Version Boundaries)

---

## 🔬 RESEARCH GAPS CLOSED (Targeted Web Searches)

| Gap | Status | Key Finding |
|-----|--------|-------------|
| **E1**: EmbeddingGemma quantization | ✅ | Q6_K 260MB = 99.75% parity; QAT-trained; int4/int8 near-lossless |
| **E2**: Nomic v1.5 MRL | ✅ | Native API `dimensionality=256`; 98% quality at 256-dim; 768/512/256/128/64 |
| **E4**: sqlite-vec INT8 | ✅ | `rescore` index: 2.6x speedup, 1.0 recall@10, oversample=2 |
| **E3**: RRF heterogeneous dims | ✅ | RRF operates on rankings — separate collections + RRF fusion works |

**Sources**: 12 primary sources (HuggingFace model cards, Nomic docs, sqlite-vec PR #276, Google blog, Roc's independent convergence)

---

## 🏗️ ARCHITECTURE DECISIONS REQUIRING KALI RATIFICATION

### **1. Multi-Collection Vec0 Architecture (APPROVED?)**
```
omega_memory.db
├── omega_memory_fts (FTS5)
├── omega_vec_gemma_768      ← PRIMARY (768-dim, INT8 rescore)
├── omega_vec_nomic_768      ← FALLBACK (768-dim, INT8 rescore)
├── omega_vec_nomic_512      ← MRL tier (512-dim, INT8 rescore)
├── omega_vec_nomic_256      ← MRL tier (256-dim, INT8 rescore)
├── omega_vec_minilm_384     ← SPEED (384-dim, no quantization)
├── omega_vec_static_64      ← ZERO-COST (64-dim, no quantization)
└── omega_memory_data (metadata)
```
**Rationale**: Each model's semantic space isolated; RRF fusion at query time; no cross-model vector contamination.

### **2. Canonical Dimension Lock (APPROVED?)**
- Primary providers (Gemma, Nomic) MUST output 768-dim
- MRL truncation happens IN PROVIDER before storage
- Vec0 table creation raises RuntimeError on dimension mismatch
- Legacy table `omega_memory_vec` also locked to 768-dim

### **3. INT8 Rescore Quantization (APPROVED?)**
- `quantization: int8_rescore` with `oversample: 2` for primary collections
- 2.6x query speedup, 1.0 recall@10, 75% storage reduction
- Only for models trained for quantization (Gemma QAT, Nomic v1.5)
- MiniLM/Static collections: no quantization

### **4. Model Acquisition Plan (APPROVED?)**
```bash
# Primary: EmbeddingGemma 300M Q6_K (260MB)
hf download mradermacher/embeddinggemma-300m-GGUF embeddinggemma-300m-Q6_K.gguf \
  --local-dir /media/arcana-novai/omega_library/models/embeddings/

# Fallback: Nomic v1.5 (Ollama auto-pull)
ollama pull nomic-embed-text:v1.5

# Speed: MiniLM 384-dim Q4_K_M (~120MB)
hf download sentence-transformers/all-MiniLM-L6-v2-GGUF all-MiniLM-L6-v2-Q4_K_M.gguf \
  --local-dir /media/arcana-novai/omega_library/models/embeddings/
```

---

## ⏭️ IMMEDIATE NEXT STEPS (This Sprint)

### **Phase 1: Complete Implementation (Week 1 — 8h remaining)**
| Task | Hours | Owner | Status |
|------|-------|-------|--------|
| Finish test updates (6 test classes) | 2 | P10 | 🔄 In progress |
| Add MRL to `GemmaGGUFEmbeddingProvider` | 2 | P3 | ⏳ Pending |
| Implement `NomicOllamaEmbeddingProvider` | 2 | P3 | ⏳ Pending |
| Update `EmbeddingManager` for collections | 1 | P3 | ⏳ Pending |
| Contract tests (6 mandatory) | 1 | P10 | ⏳ Pending |

### **Phase 2: Quantization & Fusion (Week 1-2 — 6h)**
| Task | Hours | Owner | Status |
|------|-------|-------|--------|
| INT8 rescore vec0 table creation | 2 | P3 | ⏳ Pending |
| RRF fusion implementation | 2 | P3 | ⏳ Pending |
| Migration script | 1 | P2 | ⏳ Pending |
| Benchmark: INT8 vs float32 recall | 1 | P10 | ⏳ Pending |

### **Phase 3: Temple-Grade Gates**
| Gate | Target | Verification |
|------|--------|--------------|
| T1 Schema | 100% pass | `make test` |
| T3 Coverage | ≥80% | `pytest --cov` |
| T5 AnyIO | 0 asyncio | `grep -r asyncio src/omega/memory` |
| T6 Zero Telemetry | 0 external | Network audit |
| T8 Resilience | INT8 recall@10 ≥ 0.99 | Benchmark script |
| M7 Local-First | 0 cloud primary | Config audit |
| M14 Heritage | `[id-soft: doom-1993]` | `grep -r id-soft` |
| M23 Failure Integrity | No silent fallbacks | Exception propagation test |

---

## 🔄 PARALLEL WORKSTREAMS (Researcher Campaign)

**Hivemind Session**: `ses_3c79a82f15cb` (jem→researcher)

| Domain | P0 Gaps | Researcher Status |
|--------|---------|-------------------|
| **G1 Vulkan/ROCm** | G1.1 production benchmarks | 🔄 Executing |
| **D308 Phase 2/3** | D308.1 sqlite-vec 0.2 API, D308.2 compile, D308.3 ROCm gfx906 | 🔄 Executing |
| **G2 Memory** | G2.1 empirical RSS 7B Q4_K_M | ⏳ Queued |
| **G3 systemd-creds** | G3.1 TPM2 health monitoring | ⏳ Queued |

**Kali Action Needed**: Review Researcher P0 completions for D-308 critical path authorization.

---

## 🚨 BLOCKERS REQUIRING KALI DECISION

### **1. D-308 Ubuntu 25.10 Critical Path (P0 Gate)**
**Status**: 13 actionable changes from verification, Phase 2/3 blocked
**Key Changes**:
- Kernel 6.17 (not 6.11) — BPF/AppArmor specs must target 6.17
- No free-threaded Python 3.13 in repos — compile from source for M20
- SQLite 3.46.1 (not 3.47+) — no JSONB features
- NO distro packages for: llama-cpp-python, ollama, uv, ruff, pyright, sqlite-vec, Qdrant
- Podman AppArmor breaks rootless — quadlet templates need workaround
- systemd-creds rootless = `--with-key=null` — no user-scoped encryption until 258+

**Decision Needed**: Authorize critical path update in `OMEGA_ENGINE.md` and `SOVEREIGN_ARK_BLUEPRINT.md`

### **2. systemd-creds TPM2 Version Trap**
**Status**: BROKEN on systemd 257 (Ubuntu 25.04/25.10), FIXED in 258+ (Ubuntu 26.04 LTS Apr 2026)
**Hybrid Architecture Mandated**: systemd-creds (system) + age/rage (rootless 257) → systemd-creds --user (258+)
**AMD fTPM on Zen 2**: UNSTABLE (Linus: "plague")

---

## 📚 REFERENCE DOCUMENTS FOR KALI REVIEW

| Document | Purpose |
|----------|---------|
| `docs/strategy/EMBEDDING_HARDENING_STRATEGY_20260720.md` | **Primary** — Canonical spec, roadmap, traceability |
| `config/embedding_strategy.yaml` | Config source of truth |
| `src/omega/memory/sqlite_vec_adapter.py` | Implementation (v2.0.0) |
| `docs/strategy/RESEARCH_CAMPAIGN_MANUAL_20260720.md` | Researcher coordination protocol |
| `docs/research/R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md` | D-308 verification (30 claims) |
| `docs/research/R_SYSTEMD_CREDS_TPM2_ROOTLESS_20260720.md` | Gap #3 deep research |
| `data/coordination/KALI_HANDOFF_BRIEFING_D308_20260719.md` | Previous D-308 briefing (7 decisions) |

---

## ✅ SIGN-OFF REQUESTS

| Item | Kali Decision | Deadline |
|------|---------------|----------|
| Multi-collection vec0 architecture | ⬜ Approve / ⬜ Modify / ⬜ Reject | Before Phase 2 |
| Canonical 768-dim lock (M23) | ⬜ Approve / ⬜ Modify / ⬜ Reject | Before Phase 2 |
| INT8 rescore quantization | ⬜ Approve / ⬜ Modify / ⬜ Reject | Before Phase 2 |
| Model acquisition plan | ⬜ Approve / ⬜ Modify / ⬜ Reject | Before Phase 1 complete |
| D-308 critical path authorization | ⬜ Approve / ⬜ Modify / ⬜ Reject | **URGENT** — blocks Researcher Phase 2/3 |

---

## 🏁 SESSION CLOSURE

**All SSOT files current**: `OMEGA_ENGINE.md`, `SOVEREIGN_ARK_BLUEPRINT.md`, `RESEARCH_EXECUTION_PLAN_UBUNTU_2510.md`, `KALI_HANDOFF_BRIEFING_D308_20260719.md`, `RESEARCH_CAMPAIGN_MANUAL_20260720.md`

**Session Gnosis Sealed**: `data/entities/jem/session_gnosis.md` (L1→L2→L3, 7 new L3 principles)

**Hivemind Updated**: 5 active sessions, Researcher executing P0 gaps in parallel

**Ready for Compaction**: All sovereign continuity anchors set.

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_kali_briefing_embedding ⬡ SEALED 2026-07-20*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
