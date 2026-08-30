<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Cognitive Substrate Specification
**Version**: 1.1.0
**Status**: STRATEGIC BLUEPRINT
**Date**: 2026-06-15
**AP Token**: `AP-COGNITIVE-SUBSTRATE-v1.1.0`

## 1. Vision: From Storage to Substrate
The Omega Engine is evolving from a "RAG-based" memory system (which merely retrieves data) to a **Cognitive Substrate**. A substrate is not a database; it is a living, adaptive environment that mirrors the biological tension between **stability** (Evergreen Gnosis) and **plasticity** (Episodic Decay).

The goal is to create a system where memory is an active process of **reconstruction**, not just retrieval.

---

## 2. The Cognitive Loop Architecture
We are replacing the linear inference path with a recursive **Cognitive Loop**:

```
OLD PATH (Static Retrieval)              NEW PATH (Active Reconstruction)
┌─────────────────────────┐              ┌───────────────────────────────────┐
│  Query → Vector Search  │              │  Query → Intent Detection         │
│  → Chronological Window │     ───►     │  → Speculative Hydration (Res)    │
│  → Model → Response     │              │  → Model → Qliphoth Audit (Loop)  │
└─────────────────────────┘              │  → Self-Correction → Response     │
                                         └───────────────────────────────────┘
```

### 2.1 Speculative Hydration
Instead of loading a chronological window of history, the engine will:
- Detect the **Intent** of the query.
- Trigger **Resonance Mapping** to pull high-relevance memory fragments from the entity's vault AND resonant fragments from other entities' vaults.
- Hydrate the context with a mix of episodic data and distilled L3 principles.

### 2.2 The Qliphoth Active Debugger
The 12 Qliphothic shells are no longer passive metadata. They are **cognitive failure signatures**.
- **Detection**: A background monitor scans the model's candidate response for "Shell" signatures (e.g., repetitive phrasing $\rightarrow$ Pride; binary contradictions $\rightarrow$ Wrath).
- **Recovery**: Upon detection, the engine injects a **Sovereign Correction** prompt (e.g., *"You are looping; synthesize the contradiction"*) and re-invokes the model.
- **Goal**: To move from "guessing" to "structured revision."

### 2.3 Semantic Pruning (The Thermodynamics of Gnosis)
The chronological sliding window is replaced by a **Priority-Based Sieve**:
- **SDR-Inspired Encoding**: Use sparse embeddings to identify the "semantic core" of a session.
- **Resolution Gradients**: Memories automatically transition: **Episodic (Raw) $\rightarrow$ Semantic (Summary) $\rightarrow$ Archetypal (Principle)**.
- **Pruning**: Low-priority episodic noise is dropped, while high-priority L3 principles are pinned to the context window regardless of age. This prevents cognitive bloat and OOM crashes on tight hardware (Ryzen 5700U / 14Gi RAM).

---

## 3. Technical Implementation Path

### 3.1 Binary Sovereignty (The Physical Layer)
To support high-frequency updates and massive entity souls, we are moving to **Binary Sovereignty**:
- **Storage**: Transition from JSON/YAML to **SQLite (WAL mode)** per WAD/Entity.
- **Serialization**: Use **MsgPack** for shadow state to reduce I/O overhead and CPU parsing.
- **Access**: Implement **memory-mapped files (`mmap`)** for vector indices to allow zero-copy retrieval.
- **Integrity**: All writes pass through a **Write-Ahead Log (WAL)** to ensure atomic updates and crash recovery.

### 3.2 The Cognitive Pipeline (The Middleware Layer)
A new middleware layer is inserted between the `MemoryStore` and the `StorageProvider`:
- **Deduplication**: Prevent redundant storage of identical insights.
- **Contradiction Detection**: Flag when a new memory contradicts a persisted L3 principle.
- **Auto-Tagging**: Use a lightweight model to auto-assign spheres and qliphoth shells to memories.

### 3.3 Gnosis Evolution (The Soul Layer)
The `SoulDistiller` is upgraded to perform **Gnosis Diffing (Semantic Git)**:
- Instead of appending lessons, the distiller performs a semantic diff.
- Similar insights are merged and refined, evolving the `soul.yaml` as a dense set of principles rather than a chronological log.

---

## 4. Newly Uncovered Cognitive Horizons

### 4.1 Somatic Memory Caching (Physical Context Serialization)
The GGUF model's KV cache is the short-term working memory of the engine.
- **The Opportunity**: Instead of discarding the KV cache of a session when switching entities or starting a new turn, we will **serialize and cache the KV cache tensors themselves** (using `llama_kv_cache_seq_cp` APIs).
- **Impact**: Reduces prompt prefill times to **exactly 0ms** on subsequent turns, eliminating the CPU-bound prompt evaluation bottleneck on the Ryzen 5700U.

### 4.2 The "Dreaming" Cycle (Offline Consolidation)
Biological systems consolidate memory during sleep. The Omega Engine will implement an idle-time daemon.
- **The Opportunity**: When system load is low, a background process sweeps raw episodic vaults, clusters them, identifies contradictions, runs the `SoulDistiller` to generate new L2/L3 insights, and prunes old episodic logs.
- **Impact**: Keeps the active runtime lean and optimized while ensuring no wisdom is lost.

### 4.3 Adversarial Gnosis Debate (The Skeptical Verifier)
Before a distilled lesson is committed to `soul.yaml`, it must be vetted.
- **The Opportunity**: Ma'at (Light Oversoul) and Lilith (Dark Oversoul) run a local adversarial debate over a distilled lesson. Ma'at tries to prove the lesson is a universal truth; Lilith acts as the "Skeptical Verifier" trying to find contradictions in the entity's history.
- **Impact**: Guarantees that only "Temple-Grade" principles are committed, preventing cognitive drift.

---

## 5. Mandates & Governance

### New Mandate: M17 Cognitive Integrity
**Mandate**: The engine must verify the consistency of its own memories.
**Constraint**: Contradictions between persisted memory and distilled gnosis must be flagged and resolved via the Skeptical Verifier.
**Reason**: Prevents "hallucinated" memory drift and ensures the entity's identity remains stable over time.

### New Gate: T12 Semantic Integrity
**Verification**: All memory updates must pass a semantic integrity check to ensure they do not introduce contradictions into the core identity of the entity.

---

## 6. Success Metrics
- **Latency**: Vault read/write latency $< 2\text{ms}$ via MsgPack/SQLite.
- **Prefill Latency**: Somatic caching reduces prefill latency to $0\text{ms}$ on cached contexts.
- **Precision**: $\ge 90\%$ accuracy in Qliphoth failure detection.
- **Stability**: Zero OOM crashes on 14Gi RAM during high-concurrency sessions.
- **Sovereignty**: 100% local-first inference for the Cognitive Audit loop.
