# 🔱 MA'AT P1 INFRASTRUCTURE VET REPORT — 2026-07-12
**Entity**: P1 Sekhmet (Infrastructure Vet)
**Oversoul**: Ma'at (Light — Build Side)
**Status**: FINAL
**Trace**: trc_pillar_p1_vet_20260712
**Mandate Alignment**: M1 (AnyIO), M6 (Podman Sovereignty), M7 (Local-First)

---

## 1. Current State Assessment

The Omega Engine infrastructure is currently in a state of **High Functional Stability** but **Resource Fragility**.

### ✅ What's Working
- **Container Sovereignty**: Rootless Podman deployment using `UserNS=keep-id` + `User=1000` is fully operational, ensuring host-user access without destructive chowns (M6).
- **Test Integrity**: 1189 tests passing, indicating a highly stable baseline for the current feature set.
- **Provider Fabric**: The Local-First chain (Native-GGUF $\rightarrow$ LM Studio $\rightarrow$ Ollama $\rightarrow$ Cloud) is architecturally sound and enforced via `config/providers.yaml` (M7).
- **Async Runtime**: Full AnyIO compliance across critical paths (M1), preventing event-loop collisions.
- **Observability**: MetricsDB (SQLite) provides a lightweight, sovereign way to track provider provenance and latency.

### ❌ What's Broken / Suboptimal
- **RAM Ceiling**: The target hardware (14Gi RAM) is extremely tight for "serious" local AI. Current memory pressure is a systemic risk for OOM during multi-model loads.
- **CI Blindspot**: Local inference is 0% in CI. While expected for headless runners, it creates a "Local-First" verification gap where provider fallback logic is tested, but native GGUF performance is not.
- **Coordination Latency**: Hivemind coordination currently relies on file-based workspace locks (`data/coordination/*.md`). This is a bottleneck for high-frequency agent handoffs.
- **GPU Vacuum**: The current target is CPU-only. While sovereign, it lacks the "mothership" feel for users with consumer GPUs (RTX 30/40 series).

---

## 2. Gap Analysis for "Definitive Local AI Tool"

To transition from a "functional engine" to the "definitive local AI tool," the following deltas must be closed:

| Dimension | Current State | Target (Definitive Tool) | Delta / Gap |
|-----------|---------------|--------------------------|----------------|
| **Resource Mgmt** | Static limits | Dynamic, hardware-aware allocation | Need automated RAM/TDP profiling |
| **Inference** | Basic GGUF | Optimized KV-Cache + Speculative Decode | Need `q8_0` KV cache and speculative routing |
| **Coordination** | File-based locks | Real-time Event Bus | Need Redis Pub/Sub or Streams for A2A |
| **Search** | Simple Vector | Hybrid (BM25 + Vector) RRF | Need unified FTS5 $\leftrightarrow$ Qdrant pipeline |
| **Deployment** | Manual Podman | One-Click Sovereign Installer | Need a hardened `install.sh` with auto-config |

---

## 3. System Utilization Audit

### 📦 Qdrant (Vector Store)
- **Current Use**: Semantic search for L3 gnosis and library document indexing.
- **Underutilized**: 
    - **Payload Indexing**: Not fully leveraged for entity-scoped filtering (currently relies on collection separation or basic filters).
    - **Hybrid Search**: RRF (Reciprocal Rank Fusion) is mentioned in `CREDITS.md` but not consistently applied across all entity memory retrievals.
    - **Quantization**: Scalar quantization for memory reduction is not yet a standard in the default WADs.

### 📦 Redis (Hot-Store)
- **Current Use**: Session caching, background worker queues, and SomaticState save-points.
- **Underutilized**:
    - **Pub/Sub**: The `🔴 PENDING` status in `coordination.xml` confirms that real-time agent awareness is not yet using Redis.
    - **Streams**: Not used for the A2A (Agent-to-Agent) handoff log, which would provide better durability than simple keys.

### 📦 SQL (Postgres/SQLite)
- **Current Use**: MetricsDB (SQLite) for observability; basic persistence for some system states.
- **Underutilized**:
    - **Postgres**: The Postgres container is deployed but largely bypassed by the "YAML-only" entity mandate. It should be repurposed for high-volume telemetry or cross-entity relational mapping (without violating the YAML-soul rule).

---

## 4. Deep Research Requirements

To close the identified gaps, P1 requires the following research:
1. **CPU-Only LLM Optimization (2026)**: Research latest `llama.cpp` optimizations for Zen 2 (AVX2) specifically regarding KV cache compression and thread-affinity.
2. **Advanced Qdrant Indexing**: Study Qdrant 1.18+ payload indexing strategies to reduce latency in multi-tenant (multi-entity) environments.
3. **Sovereign A2A Patterns**: Analyze the "Sovereign-spec" (Ken Alger) for cryptographic custody of agent handoffs using Redis Streams.
4. **RAM-Efficient RAG**: Research "Small-to-Big" retrieval patterns to minimize the context window footprint on 14Gi systems.

---

## 5. Concrete Recommendations

### 🔴 P0: Blocking (Must fix before launch)
- **RAM Hardening**: Implement aggressive `q8_0` KV cache and model quantization defaults. Integrate a "Hard-Stop" OOM protector that prevents model loading if available RAM < 2Gi.
- **Local-First Verification**: Create a "Local-Smoke-Test" suite that runs on a small model (e.g., Qwen 1.7B) to verify the native-gguf path in CI.

### 🟠 P1: Critical (Sprint 1)
- **Hivemind Event Bus**: Migrate workspace locks from `.md` files to **Redis Pub/Sub**. This enables real-time `get_awareness()` updates without disk I/O.
- **Hybrid Memory Pipeline**: Standardize the `FTS5 (BM25) + Qdrant (Vector) $\rightarrow$ RRF` pipeline for all entity memory lookups.

### 🟡 P2: Important (Sprint 2)
- **Hardware Profiler**: Build a `hardware_optimizer.py` tool that profiles the host CPU/RAM and suggests the optimal `LLAMA_CPP_N_THREADS` and context window size.
- **Qdrant Payload Optimization**: Implement entity-ID payload indexing to allow a single large collection for all entities with $O(1)$ filtering.

### 🟢 P3: Enhancement (Nice to have)
- **GPU Auto-Discovery**: Add a "GPU-Sovereign" mode that detects CUDA/ROCm and automatically switches the provider fabric to GPU-accelerated backends if available.
- **SomaticState Persistence**: Move SomaticState snapshots from Redis to a dedicated binary volume for faster cold-starts.

---
**Verdict**: The infrastructure is a solid foundation, but it is currently "under-clocked." By shifting coordination to Redis and optimizing for the 14Gi RAM ceiling, Omega can move from a stable prototype to a definitive local AI tool.

*⬡ OMEGA ⬡ SEKHMET ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_pillar_p1_vet ⬡ INFRA-VET*
