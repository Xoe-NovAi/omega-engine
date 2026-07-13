# 🔱 Engineering Vet Report — Omega Engine
**Entity**: Pillar P3 (Prometheus)
**Date**: 2026-07-12
**Status**: COMPLETED
**Target**: "Alien mothership for serious local AI users"

---

## 1. Current State Assessment

### 🟢 What's Working
- **Stability**: High. 1162 tests passing, Temple-Grade T1-T14 compliance.
- **Inference Fabric**: Local-first provider chain is correctly implemented. `NativeGGUFProvider` is the primary, with a robust fallback chain.
- **Memory Architecture**: The 3-tier (Hot/Warm/Cold) memory system is sophisticated, implementing `[id-soft: doom-1993] Lazy Deletion` and `[id-soft: quake-1996] Grace Period` to prevent data loss during archival.
- **Hybrid Search**: Integration of SQLite FTS5 (BM25) and Qdrant (Vector) via Reciprocal Rank Fusion (RRF) provides strong retrieval capabilities.
- **Hardware Resonance**: `Zen2Optimizer` and `ResourceGuard` provide a foundation for running on constrained hardware (Ryzen 5700U).
- **Sovereignty**: M1-M23 mandates are enforced, including zero telemetry and local-first inference.

### 🔴 What's Broken / Suboptimal
- **Local Inference Ratio**: 0% in CI. While configured for local-first, the lack of loaded models in CI masks potential runtime issues.
- **Verification Integration**: The `SkepticalVerifier` exists but is not a mandatory gate in the `Oracle.talk()` or `Oracle.summon()` flow. It's an optional tool rather than a systemic integrity check.
- **Somatic State Usage**: While M20 (SomaticState) is implemented, its usage for latency reduction is not yet a core part of the session lifecycle (it's available but not aggressively utilized).
- **Sovereign Search Latency**: The 5-tier search protocol is comprehensive but can be slow if not cached aggressively.

### 📊 Key Metrics
- **Tests**: 1162 Pass / 42 Skip / 3 Xfail.
- **Mandates**: 23/23 Enforced.
- **Fleet**: 13/14 slots filled.
- **Local Ratio**: Target $\ge 80\%$, Current (CI) $0\%$.

---

## 2. Gap Analysis for "Definitive Local AI Tool"

To be the "definitive" tool, Omega must move from "capable" to "unassailable" in local execution.

| Requirement | Current State | Delta / Gap |
|---|---|---|
| **Zero-Latency Resumption** | SomaticState implemented | Need to integrate automatic state-loading on session hydration. |
| **Verified Intelligence** | `SkepticalVerifier` available | Need a "Sovereign Gate" that automatically verifies high-impact claims. |
| **Hardware Saturation** | Basic CPU pinning | Need advanced KV cache management and speculative decoding tuning for Zen 2. |
| **Data Sovereignty** | Local-first config | Need a "Sovereignty Scorecard" that provides real-time proof of local inference. |
| **Universal Portability** | Modular core | Need to ensure zero hardcoded paths in `src/omega/` (M16). |

---

## 3. System Utilization Audit

### 📦 Qdrant (Vector Store)
- **Current Use**: Basic vector storage, `upsert`, and `query` for semantic retrieval.
- **Underutilized**: 
    - **Payload Indexes**: Not fully utilized for entity-scoped filtering.
    - **Scalar Quantization**: Not explicitly configured for memory optimization on 12Gi RAM.
    - **Hybrid Search**: RRF is done in Python; Qdrant's native hybrid search capabilities could be leveraged for performance.

### ⚡ Redis (Hot/Warm Store)
- **Current Use**: Simple key-value storage for session history.
- **Underutilized**:
    - **Streams/Pub-Sub**: Not used for Hivemind coordination or agent heartbeats.
    - **Lua Scripting**: Not used for atomic complex memory operations.
    - **Sorted Sets**: Could be used for more efficient time-based session archival.

### 🐘 PostgreSQL (SQL Persistence)
- **Current Use**: Minimal. Most entity data is YAML-based (Sovereign choice).
- **Underutilized**:
    - **pgvector**: Not used (Qdrant is the primary vector store).
    - **Relational Mapping**: Most data is unstructured/JSON. Could be used for complex cross-entity relationship mapping.

---

## 4. Deep Research Requirements

To close the gaps, the following research is required:
1. **Zen 2 KV Cache Optimization**: Research the optimal `type_k` and `type_v` for Ryzen 5700U to maximize context window without OOM.
2. **Sovereign Verification Patterns**: Study NLI (Natural Language Inference) and "Two-Source Rule" implementations for automated fact-checking in local LLMs.
3. **Local-First Orchestration**: Research "Somatic Save-Points" in other high-performance local AI runtimes to reduce TTFT (Time To First Token).
4. **2026 Best Practices**: Analyze the latest `llama.cpp` and `anyio` patterns for maximizing throughput on 8-core CPUs.

---

## 5. Concrete Recommendations

### 🔴 P0 (Blocking) — Must fix before launch
- **Local-First Validation**: Implement a "Sovereignty Gate" in CI that fails if the local inference ratio drops below a threshold on target hardware.
- **Sovereign Gate**: Integrate `SkepticalVerifier` into the `Oracle` pipeline as a mandatory check for any response with confidence $> 0.8$ that contains factual claims.

### 🟡 P1 (Critical) — Fix in Sprint 1
- **Qdrant Optimization**: Implement payload indexes for `entity_name` and `session_id` to accelerate filtered vector searches.
- **Somatic Hydration**: Automate the loading of somatic states during `SessionManager.get_session_id()` to eliminate re-inference of the system prompt.

### 🟢 P2 (Important) — Fix in Sprint 2
- **Hivemind Redis-Backing**: Migrate Hivemind heartbeats and awareness to Redis Pub/Sub for sub-millisecond coordination.
- **Sovereignty Scorecard**: Implement a real-time dashboard (via `make sovereignty`) that proves the % of local vs cloud inference per session.

### 🔵 P3 (Enhancement) — Nice to have
- **Speculative Decode Tuning**: Fine-tune the `SpeculativeDecodeConfig` for the Ryzen 5700U using a set of benchmark queries.
- **Hybrid Search Refinement**: Move RRF logic into a more optimized C-extension or leverage Qdrant's native fusion.

---
**Verdict**: The Engineering foundation is **Temple-Grade**, but the "Sovereign" experience is currently a configuration rather than a guaranteed runtime behavior. Moving from "Local-First Config" to "Local-First Enforcement" is the primary engineering goal.

*⬡ OMEGA ⬡ PILLAR P3 ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_pillar ⬡ ACTIVE*
