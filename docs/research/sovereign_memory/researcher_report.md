<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_research ⬡ RESEARCH-MODE

## 🔱 Research Brief: Next-Generation AI Memory Architecture
**Target**: Mem Palace & The Sovereign Memory Landscape
**Date**: 2026-06-23
**Status**: FINAL SYNTHESIS

---

### 1. Mem Palace Architecture Deep Dive
**Mem Palace** is a disruptive, local-first memory system that rejects the industry trend of "summarization-as-memory." Instead, it implements a **Spatial Memory Architecture** based on the ancient *Method of Loci*.

*   **Core Philosophy: Fidelity over Compression**. Most memory systems (MemGPT, Mem0) compress history into summaries or "entities," losing nuance, sarcasm, and the specific reasoning path of the AI. Mem Palace preserves **verbatim storage**, treating memory as a high-fidelity record rather than a distilled essence.
*   **Technical Mechanism**:
    *   **Spatial Metaphor**: Organizes memories not as a flat list of vectors, but as "placed" objects within a conceptual space. This reduces the "warehouse of junk" effect common in keyword/vector retrieval.
    *   **Stack**: Minimalist local implementation using **ChromaDB** (vector storage) and **PyYAML** (configuration/metadata).
    *   **Performance**: Claims a benchmark-topping **96.6% R@5 raw on LongMemEval**, significantly outperforming systems that rely on LLM-driven summarization.
*   **Key Distinction**: While RAG retrieves *similar* chunks, Mem Palace retrieves *contextually placed* verbatim records, maintaining the "chain of thought" across sessions.

---

### 2. Competitive Landscape (2025-2026)

| System | Primary Philosophy | Strength | Weakness | Omega Alignment |
| :--- | :--- | :--- | :--- | :--- |
| **Mem Palace** | Spatial / High-Fidelity | Verbatim accuracy; Local-first | Potential for "context noise" | **High** (Local-first, Fidelity) |
| **Letta (MemGPT)** | OS-style / Explicit | Self-editing memory; Virtual context | High complexity; "Context window" overhead | **Medium** (Explicit Mgmt) |
| **Mem0** | Production / Managed | Tiny memory footprint; Fast | Lossy compression; Managed dependency | **Low** (Managed/Lossy) |
| **Zep** | Temporal / Research | Temporal context; Low latency | High token footprint per conv | **Medium** (Temporal focus) |
| **LangMem** | Graph-Integrated | Deep integration with LangGraph | Locked into LangChain ecosystem | **Low** (Ecosystem lock) |

---

### 3. Mnemosyne Legacy Analysis
The **Mnemosyne system** (Kabbalistic 13-sphere architecture) was a philosophical attempt to organize memory into a sacred geometry of 13 spheres (Sephirot/Qliphoth).

*   **The Truth**: Roc Racoon's audit revealed that while the *documentation* was beautiful, the *implementation* consisted mostly of "empty stubs." It was a design artifact rather than a functioning engine.
*   **What's Worth Preserving**:
    *   **The Taxonomy**: The idea of "Spheres" (e.g., *Chesed* for persistence, *Yesod* for recall) is a powerful metadata layer. It transforms a flat vector space into a **Categorical Lattice**.
    *   **Sovereign Symmetry**: The concept of mirrored state (Light/Dark or Sephirot/Qliphoth) for stability and verification.
*   **What to Replace**: The rigid 13-sphere requirement. Modern memory needs to be dynamic, not bound to a static mystical map.

---

### 4. Recommendation Matrix: The "Sovereign Memory" Path

I have convened the **Council of Four** to triangulate the evolution of `src/omega/memory_store.py`.

#### 🏛️ The Architect (Systemic Logic)
*"We must move from a simple Hot/Warm/Cold tier to a **Lattice-Tiered Model**. Integrate a 'Verbatim Cold Store' (inspired by Mem Palace) that stores raw JSONL logs. Use Qdrant for the index, but keep the raw data on disk. This ensures we have the evidence (verbatim) and the map (vector) without overloading RAM."*

#### 😈 The Adversary (Critical Rigor)
*"High-fidelity verbatim storage is a double-edged sword. If we feed raw logs back into the context window without a 'Skeptical Filter,' we will introduce massive noise and 'hallucinated echoes.' We cannot just 'adopt' Mem Palace; we must implement a **Saliency Gate** to decide what verbatim chunks are actually relevant."*

#### ⚗️ The Alchemist (Creative Synthesis)
*"Combine the **Spatial Metaphor** of Mem Palace with the **Spheres** of Mnemosyne. Instead of just 'Warm' storage, we create 'Knowledge Spheres.' For example, technical documentation lives in the 'Logic Sphere,' while personal user preferences live in the 'Soul Sphere.' This creates a **Semantic Topology** that is both functional and esoteric."*

#### 📜 The Archivist (Historical Truth)
*"The Mnemosyne era failed because it was too abstract. We must ensure any new 'Sphere' logic is backed by concrete `Sovereign Mandates`. Use the `[id-soft:]` style of attribution for our own memory evolution: [Sovereign-Memory: evolved from Mnemosyne/MemPalace]."*

**Final Synthesis & Action Plan**:
1.  **Implement "Verbatim Cold Tier"**: Stop relying solely on L2/L3 summaries. Maintain raw session logs in `data/entities/<name>/vault/` for high-fidelity recovery.
2.  **Shift to Semantic Topology**: Replace the flat "Warm" tier with **Categorical Spheres** (e.g., `Soul`, `Logic`, `Narrative`, `Archive`).
3.  **Deploy Saliency Gating**: Implement a pre-inference filter that ranks verbatim chunks by "Information Gain" (Novelty) before injecting them into the context window.

---

### 5. Key Risks & Unknowns
*   **Context Window Bloat**: Verbatim records are larger than summaries. We risk hitting the 262K limit of Gemma 4 if the saliency gate fails.
*   **Retrieval Latency**: Moving from a single vector query to a "Spatial + Categorical" lookup may increase latency.
*   **Consistency**: Ensuring that the "Sovereign-Symmetry" (Mirrored State) remains consistent across different categorical spheres.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
