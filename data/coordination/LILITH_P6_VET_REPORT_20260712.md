# 🔱 Cognition Vet Report — Omega Engine
**Entity**: Ereshkigal (P6: Mind)
**Oversoul**: Lilith
**Date**: 2026-07-12
**Status**: FINAL
**Sovereignty Score**: 🟢 High (Local-First Architecture)

---

## 1. Current State Assessment

### 1.1 What's Working
- **Local-First Provider Fabric**: The `ModelGateway` correctly implements the fallback chain (`native-gguf` $\rightarrow$ `lmster` $\rightarrow$ `ollama` $\rightarrow$ `cloud`). This is the bedrock of user sovereignty.
- **Hybrid Routing**: The `SemanticRouter` provides a sophisticated entry point, using pre-computed entity vectors for $O(1)$ routing, falling back to keywords and then defaults.
- **3-Tier Memory**: `MemoryStore` successfully separates Hot (LRU), Warm (Redis/File), and Cold (File) memory, preventing OOM while maintaining context.
- **Soul Evolution**: The L1 $\rightarrow$ L2 $\rightarrow$ L3 distillation pipeline in `SoulDistiller` ensures that intelligence is preserved across sessions.
- **Response Provenance**: Mandate M22 is fully implemented; the engine tracks the actual provider used, not the intended one.

### 1.2 What's Broken / Suboptimal
- **Inference Ratio (CI)**: While configured for local-first, the current CI environment shows 0% local inference because models aren't loaded. This is a "test-env" artifact, but it masks potential production regressions.
- **Context Windowing**: The `ContextBuilder` relies on a sliding window of recent exchanges. While `Headroom` provides semantic compression, the system lacks a "global" synthesis of the session's cognitive trajectory.
- **Retrieval Depth**: `SelectiveHydration` currently uses the entity name as the primary query for L3 principles. This is "broad" retrieval, not "precise" retrieval.

---

## 2. Gap Analysis for "Definitive Local AI Tool"

To be the "Alien Mothership" for local AI users, the engine must move from **Passive Retrieval** to **Active Cognition**.

| Feature | Current State | Target State (Definitive Tool) | Delta |
|-----------|----------------|-----------------------------------|-----------|
| **RAG** | Hybrid (FTS5 + Vec) | Agentic / Iterative RAG | $\Delta$ Iterative loops |
| **Context** | Sliding Window | Cognitive Graph / Synthesis | $\Delta$ Session Summary |
| **Inference**| Local-First | Optimized Local (KV Quant) | $\Delta$ q8_0 Tuning |
| **Sovereignty**| Provider-level | Model-level (Fine-tuned) | $\Delta$ DPO Pipeline |
| **Awareness** | MCP-based | Real-time Pub/Sub | $\Delta$ Redis Pub/Sub |

---

## 3. System Utilization Audit

### 3.1 Qdrant (Vector Store)
- **Current Use**: Basic cosine similarity search for L3 principles and conversation history.
- **Underutilized**: 
    - **Payload Filtering**: Not using metadata to filter by session, entity, or "importance" score.
    - **Hybrid Scoring**: RRF is used in `MemoryStore`, but could be more deeply integrated into the `ModelGateway` for "context-aware" provider selection.
    - **Multi-Vector**: No support for multiple embeddings per document (e.g., summary vector + chunk vectors).

### 3.2 Redis (Hot/Warm Store)
- **Current Use**: Simple key-value storage for session history.
- **Underutilized**:
    - **Pub/Sub**: The Hivemind currently relies on MCP tool calls. Moving to Redis Pub/Sub would enable real-time "awareness" events without polling.
    - **Streams**: Could be used for a "Cognitive Trace" that allows an agent to "rewind" its thought process.

### 3.3 PostgreSQL (Observability/Metrics)
- **Current Use**: Storing trace IDs, latency, and provider stats.
- **Underutilized**:
    - **Relational Memory**: Could store the "Entity Web" (how entities relate to each other) to improve the `SemanticRouter`.

---

## 4. Deep Research Requirements

To close the gaps, the following research is required:
1. **Iterative RAG Patterns**: Study "Self-RAG" and "Corrective RAG" (CRAG) to implement a loop where the engine verifies its own retrieved context before generating.
2. **Local KV Cache Optimization**: Research the impact of `q8_0` vs `q4_0` KV cache on Zen 2 (Ryzen 5700U) to find the "Sovereignty Sweet Spot" for RAM vs. Accuracy.
3. **DPO for Local Models**: Research the most efficient way to apply Direct Preference Optimization (DPO) to 1.7B-4B models using the collected interaction data.

---

## 5. Concrete Recommendations

### P0: Blocking (Must fix before launch)
- **Local-First Validation**: Implement a "Sovereignty Gate" in CI that fails if the local inference ratio drops below 80% in a production-like environment.
- **KV Cache Hardening**: Ensure `q8_0` is the default for all local models to maximize the 12Gi RAM ceiling.

### P1: Critical (Sprint 1)
- **Query-Aware Hydration**: Update `SelectiveHydration` to embed the *user query* and retrieve the top-K most relevant L3 principles, rather than just entity-wide principles.
- **Session Synthesis**: Implement a "Session Summary" that is updated every 10 turns and injected into the context, replacing the need for a large sliding window.

### P2: Important (Sprint 2)
- **Agentic RAG**: Implement the `IterativeResearcher` loop in the `Oracle` facade to allow "Deep Thinking" mode.
- **Hivemind Pub/Sub**: Migrate agent awareness to Redis Pub/Sub to reduce MCP overhead.

### P3: Enhancement (Nice to have)
- **Somatic State Refinement**: Expand `SomaticState` to include the full KV cache of the `native-gguf` provider for instant session resumption.
- **Relational Entity Map**: Use PostgreSQL to map entity affinities, improving the `SemanticRouter`'s accuracy for complex queries.

---

**Verdict**: The Cognition domain is **Sovereign** but **Passive**. By implementing Agentic RAG and Query-Aware Hydration, the Omega Engine will transition from a tool that *remembers* to a tool that *reasons*.

`⬡ OMEGA ⬡ ERESHKIGAL ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_c42dd0ac906b ⬡ Strike 8`
