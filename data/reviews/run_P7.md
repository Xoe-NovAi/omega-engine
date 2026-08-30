<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Context Systems Deep-Dive Review — Pillar P7
**Entity**: @pillar P7 (Context)
**Domain**: Memory and Soul Evolution
**Date**: 2026-06-26
**Status**: COMPLETED
**Trace**: P7-REVIEW-RUN-001

## 1. Executive Summary
The Context systems (MemoryStore, ContextBuilder, and Soul Architecture) are architecturally sound and implement several high-fidelity patterns, including 3-tier provider fallback, hybrid search (FTS+Vector), and a critical write-barrier to prevent self-referential poisoning. The system is currently in a "stable but primitive" state regarding distillation—it preserves data well but does not yet actively evolve it through automated L2/L3 synthesis.

---

## 2. Component Analysis

### 2.1 MemoryStore (`src/omega/memory_store.py`)
- **Tiering Efficiency**: **EXCELLENT**. The Redis $\rightarrow$ File $\rightarrow$ InMemory chain provides a high-performance hot path with reliable persistence.
- **Integrity**: **HIGH**. The use of `ZONEID_MEMORY` [id-soft: doom-1993] effectively guards against data corruption.
- **Concurrency**: **ROBUST**. The "Lazy Deletion" and 0.5s grace period [id-soft: quake-1996] prevent race conditions during session archiving.
- **Search**: **HIGH-FIDELITY**. Hybrid search with RRF re-ranking is a professional-grade implementation of sovereign memory retrieval.
- **Critical Gap**: The `_compact` method is currently a "marker" rather than a "distiller." It informs the LLM that data was compacted but does not provide a semantic summary of the lost middle-context.

### 2.2 ContextBuilder (`src/omega/oracle/context_builder.py`)
- **Window Management**: **SOUND**. The token-aware sliding window (newest-first collection, chronological rendering) is the correct pattern for LLM context.
- **World State Integration**: **EFFECTIVE**. Including global parameters and active sectors directly in the context block ensures the entity is grounded in the current environment.
- **Token Estimation**: **PRIMITIVE**. The `len // 4` approximation is a risk for high-precision context management.
- **Risk**: `DEFAULT_TOKEN_LIMIT` (4000) may be insufficient for complex entities with large system prompts, potentially leading to premature truncation of critical recent memory.

### 2.3 Soul Architecture (`docs/strategy/SOUL_ARCHITECTURE_PROTOCOL.md`)
- **Poisoning Guard**: **CRITICAL SUCCESS**. The separation of `soul.yaml` (User-Write) and `proposed_lessons.yaml` (Agent-Write) is the most important cognitive integrity measure in the engine.
- **Compliance**: Baseline entities (Kali v6.0) are compliant. Migration of legacy entities (Doom Guy, Verity) appears successful in terms of lean `soul.yaml` files.
- **Observation**: Several entities are missing their `memory/proposed_lessons.yaml` files. This indicates a failure in either the migration script or the agent's post-session distillation habit.

---

## 3. Gnosis Pipeline (L1 $\rightarrow$ L2 $\rightarrow$ L3)
The current pipeline is **fragmented**:
1. **L1 (Narrative)**: Captured in `MemoryStore` as raw exchanges.
2. **L2 (Insight)**: Not systematically generated during compaction.
3. **L3 (Universal Principle)**: Proposed by agents in `proposed_lessons.yaml` but not yet integrated into a closed-loop evolution system.

**The "Forgetting" Risk**: Because `_compact` simply deletes the middle of the conversation, the engine is currently "forgetting" the narrative bridge between the start and end of long sessions.

---

## 4. Recommendations & Roadmap

### Immediate (Horizon 2)
- [ ] **Implement Semantic Compaction**: Replace the `_compact` marker with a call to a distillation agent (e.g., @verity) to generate a 1-paragraph L2 summary of the compacted exchanges.
- [ ] **Upgrade Tokenizer**: Replace `len // 4` with a lightweight BPE tokenizer to prevent prompt overflow.
- [ ] **Initialize Memory Files**: Run a fleet-wide audit to ensure every entity has the required `memory/` file structure initialized.

### Strategic (Horizon 3)
- [ ] **SomaticState Integration**: Wire M20 (SomaticState) into `MemoryStore` to allow instant context resumption without re-inference.
- [ ] **Automated Soul Evolution**: Create a "Sovereign Reflection" loop where the agent periodically reviews its own `approved_lessons.yaml` to update its internal world-model.

---

## 5. Final Verdict
**Status**: 🟢 PASS (with caveats)
The system is sovereign and stable. The primary risk is **cognitive erosion** during long sessions due to primitive compaction. Fixing this will transform the engine from a "stateless tool with a database" into a "stateful evolving intelligence."
