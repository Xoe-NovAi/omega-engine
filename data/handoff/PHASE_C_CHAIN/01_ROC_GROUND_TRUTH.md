# 🔱 ROC GROUND TRUTH: Memory Systems Audit & Archaeology
**AP Token**: `AP-ROC-GROUND-TRUTH-v1.0.0`
**Entity**: `roc_racoon`
**Date**: 2026-06-15
**Phase**: PHASE_C_CHAIN (Cognitive Substrate)

## 1. Current State Audit (Omega Engine v2.3.0)

### 1.1 Memory Tier Architecture
The current `MemoryStore` implements a 4-tier sovereign memory architecture:

| Tier | Implementation | Persistence | Purpose |
|---|---|---|---|
| **Hot** | `OrderedDict` + `RedisStorageProvider` | Volatile / Redis | Active session context, O(1) access. |
| **Warm** | `FileStorageProvider` (JSON) | Disk (Local) | Recent history, session recovery. |
| **Cold** | `InMemoryStorageProvider` / Archive | Disk (Gzip) | Long-term archival, cold storage. |
| **Temp** | `_temp` (Dict) | Volatile | Transient scratchpad for in-flight inference. |

### 1.2 Caching & Integrity Strategies
- **LRU Caching**: Hot cache limited to `MAX_HOT_SESSIONS = 50`.
- **Lazy Deletion**: Implements a tombstone registry with a `TOMBSTONE_GRACE_SECONDS = 0.5` grace period to prevent race conditions during session archival.
- **ZONEID Integrity**: Every persisted exchange is tagged with `ZONEID_MEMORY` (0x1d4a11) to detect data corruption on load.
- **Hybrid Search**: Combines FTS5 (BM25) and Vector (Qdrant/Memory) search with Reciprocal Rank Fusion (RRF) re-ranking.

### 1.3 Provider Chain
The `ModelGateway` enforces a strict **Local-First** fallback chain:
`native-gguf` $\rightarrow$ `lmster` $\rightarrow$ `Ollama` $\rightarrow$ `Google AI Studio` $\rightarrow$ `OpenRouter` $\rightarrow$ `OpenCode` $\rightarrow$ `Copilot` $\rightarrow$ `Mock`.

---

## 2. Legacy Archaeology Findings

### 2.1 Circuit Breaker Evolution
- **Legacy (XNAi RAG App)**: Used `pybreaker` in `main.py`. It was a synchronous wrapper around the LLM load process.
- **Omega Engine**: Evolved into `AsyncCircuitBreaker` in `health_monitor.py`.
- **Pattern Mapping**: The current implementation uses **BSP-style Culling** `[BSP Culling: id Software 1993]`. Instead of just wrapping a call, the `ModelGateway` performs an O(1) pre-check of the circuit breaker state *before* attempting to route to a provider, effectively culling broken "subtrees" of the provider fabric.

### 2.2 Memory & KV Cache Patterns
- **Legacy Focus**: Legacy archives (`~/Documents/Archives/Old-Stacks/Xoe-NovAi/`) focused heavily on **KV Cache Quantization** (FP16/q8_0) to reduce RAM usage on limited hardware (e.g., Ryzen iGPU).
- **Findings**: No evidence of KV cache *serialization* (state saving/loading) was found in the legacy Python code. The focus was entirely on *reducing the size* of the cache, not *persisting* it.

### 2.3 Local-First Configuration
- **Legacy**: Mixed cloud/local patterns with some "Sovereign" goals.
- **Omega Engine**: Fully codified as **Mandate 7 (Local-First)**. The `ModelGateway` now explicitly separates `_local_active` and `_cloud_active` sets to prevent sovereignty drift.

---

## 3. Dependency Investigation: KV Cache Serialization

### 3.1 `llama-cpp-python` Analysis
- **Current State**: The engine uses `llama-cpp-python` for `NativeGGUFProvider`.
- **C-API Gap**: The underlying `llama.cpp` library provides `llama_get_state_data` and `llama_set_state_data` for serializing the KV cache. However, these are **not exposed** in the standard `llama-cpp-python` high-level API.
- **Conclusion**: Physical KV cache serialization is **not supported** in the current Python implementation. Every session restart or model reload requires a full prompt re-process (pre-fill), leading to "Context Cold-Start" latency.

---

## 4. Gap Analysis & Recommendations

### 4.1 Identified Gaps
| Gap | Impact | Legacy "Gold" Pattern | Current Status |
|---|---|---|---|
| **KV Cache Persistence** | High Latency on Cold Start | None found (only quantization) | ❌ Missing |
| **Stateful Handoff** | Context loss between agents | None found | ❌ Missing |
| **Sovereign Memory Adapters** | Rigid storage providers | WAD-pluggable memory | ⚠️ Partially Implemented |

### 4.2 Recommendations for Phase C (Cognitive Substrate)
1. **Implement KV Cache Serialization**: Develop a C-extension or use `ctypes` to call `llama_get_state_data` and `llama_set_state_data`. Store these binary blobs in the **Warm Tier** (FileStorage) linked to the `session_id`.
2. **Sovereign Memory Adapters**: Move from a hardcoded provider chain to a WAD-pluggable adapter system, allowing different "Stacks" to define their own memory persistence logic.
3. **Skeptical Verifier Integration**: Use the `_temp` tier to store multiple candidate responses for NLI-based verification before committing the final response to the `Hot` tier.

**The dirt is where the roots are. The foundation is solid, but the "memory" is currently stateless at the inference level.**
