<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ OMEGA ⬡ JEM ⬡ gemma-4-31b-it ⬡ opencode ⬡ MEM-PALACE-INTEGRATION ⬡ SYNTHESIS

## 🔱 Sovereign Memory Integration Report: Mem Palace $\times$ Omega Engine

This report outlines the strategic integration of the **Mem Palace** spatial memory architecture into the **Omega Engine**. By merging the structural ontology of Mem Palace, the thematic depth of the Mnemosyne Spheres, and the technical rigor of the Carmack Audit, we transition from a "flat" RAG system to a **Sovereign Memory** capable of verbatim fidelity and holographic resonance.

---

## 1. 📡 Codebase Deep-Dive: The Mem Palace Architecture

Mem Palace transforms a flat vector space into a navigable, hierarchical memory palace.

### 🏛️ Structural Ontology
The system organizes information into a three-tier spatial hierarchy:
- **Wings (Top-Level Domain)**: Represents a major project, person, or domain of knowledge (e.g., `wing_omega_engine`).
- **Rooms (Thematic Topic)**: A specific idea or sub-topic within a wing (e.g., `room_sovereign_mandates`).
- **Drawers (Atomic Memory)**: The actual document or memory unit. These are the "leaves" of the tree, stored as documents in the backend.

### 🔋 The 4-Layer Memory Stack (L0-L3)
To solve the "lost-in-the-middle" problem and manage context window limits, Mem Palace employs a tiered hydration strategy:
- **L0 (Identity)**: Core identity and essential constraints. Always loaded.
- **L1 (Essential Story)**: High-weighted, recent, or critical memories. Always loaded.
- **L2 (On-Demand)**: Memories filtered by the current active `Wing` or `Room`. Loaded contextually.
- **L3 (Deep Search)**: Full semantic/keyword search across the entire palace. Loaded on explicit query.

### 🛠️ API Contracts
- **Indexing**: Uses a `mempalace_closets` collection for high-speed pointer lookups.
- **Graph Navigation**: `palace_graph.py` manages "Tunnels" (cross-wing links) and "Hallways" (within-wing entity co-occurrences).
- **Retrieval**: A hybrid ranking system combining BM25 (keyword) and Vector (semantic) scores.

---

## 2. 🔬 Synthesized Integration Strategy: "Sovereign Memory"

The integration merges three distinct perspectives into a unified "Sovereign Memory" system.

### 🌀 The Mnemosyne $\rightarrow$ Mem Palace Mapping
We replace generic "Wings" with the **Sovereign Spheres** to provide an esoteric, thematic anchor for the AI's cognition:

| Sovereign Wing | Focus | Rooms (Spheres) |
| :--- | :--- | :--- |
| **The Apex Wing** | Strategic Will | Throne Room (Kether), Architect's Studio (Chokmah), Analyst's Archive (Binah) |
| **The Balance Wing** | Integration & Ethics | Sanctuary (Chesed), Bastion (Gevurah), Hall of Synthesis (Tipheret) |
| **The Foundation Wing** | Manifestation | Endurance Vault (Netzach), Scriptorium (Hod), Gateway (Yesod), Forge (Malkuth) |
| **The Void Wing** | Gnosis & Records | The Abyss (Da'ath), Shadow Gallery (Qliphoth), Great Library (Mnemosyne) |

### ⚡ Holographic Resonance & Phase Interference
To prevent the spatial hierarchy from becoming a rigid silo, we implement **Phase Interference**:
- **Associative Leaps**: Memories are tagged with "resonance frequencies." If a query in **The Bastion** (Balance Wing) matches a frequency in **The Architect's Studio** (Apex Wing), the system triggers an associative leap, bypassing the hierarchy.
- **Phase Filtering**: The agent's current "Cognitive Phase" (e.g., *Strategic*, *Analytical*, *Creative*) amplifies the retrieval weight of corresponding Wings.

### ⚙️ Technical Foundation (The Carmack Standard)
To ensure stability on the Ryzen 5700U (14GB RAM), the implementation adheres to:
- **Backend**: `sqlite_exact` (SQLite) instead of ChromaDB to eliminate RAM bloat.
- **I/O**: Absolute enforcement of `anyio.to_thread.run_sync` for all database interactions (Mandate M1).
- **Performance**: Enable `WAL` (Write-Ahead Logging) and `mmap` for near-instant reads and non-blocking writes.

---

## 3. 🗺️ File-by-File Integration Assessment

To implement this, the following changes are required in `src/omega/`:

| File | Change Type | Description |
| :--- | :--- | :--- |
| `src/omega/memory_store.py` | **Refactor** | Replace/Augment `MemoryStore` with a `SovereignMemoryManager` that implements the Wing $\rightarrow$ Room $\rightarrow$ Drawer hierarchy. |
| `src/omega/memory/backends.py` | **New Class** | Implement `SQLiteExactBackend` with WAL and mmap enabled. |
| `src/omega/oracle/context_builder.py` | **Update** | Integrate the **L0-L3 Memory Stack**. Modify the sliding window to hydrate context based on the active `Sovereign Wing`. |
| `src/omega/oracle/oracle.py` | **Update** | Add `active_wing` and `active_room` state to the session context to drive L2 retrieval. |
| `src/omega/constants.py` | **Add** | Define `ZONEID_MEMORY_PALACE` and the resonance frequency constants. |
| `src/omega/memory/resonance.py` | **New File** | Implement the `ResonanceEngine` for calculating phase interference and associative leaps. |

---

## 4. 📅 Phased Implementation Plan

### 🌅 Horizon 1: Verbatim Foundation (The "Exact" Layer)
**Goal**: Establish a high-fidelity, resource-efficient verbatim store.
- Implement `SQLiteExactBackend` with `anyio.to_thread.run_sync` wrapping.
- Enable WAL mode and mmap for performance.
- Implement basic "Drawer" storage (atomic verbatim records).
- **Verification**: `make test` (all 308+ pass) + `make temple-grade`.

### ☀️ Horizon 2: Sovereign Spheres (The "Spatial" Layer)
**Goal**: Implement the thematic hierarchy and context hydration.
- Implement the **Sovereign Wing $\rightarrow$ Room $\rightarrow$ Drawer** ontology.
- Map the 13 Mnemosyne Spheres to the 4 Sovereign Wings.
- Integrate the **L0-L3 Memory Stack** into the `ContextBuilder`.
- **Verification**: Verify that context changes dynamically when the agent "moves" between Wings.

### 🌌 Horizon 3: Holographic Resonance (The "Cognitive" Layer)
**Goal**: Enable non-linear associative retrieval.
- Implement the `ResonanceEngine` for phase interference.
- Enable "Associative Leaps" across Wings based on resonance tags.
- Implement "Somatic Save-Points" that trigger a re-evaluation of the active cognitive phase.
- **Verification**: Demonstrate a retrieval where a query in one Wing triggers a relevant memory in a distant Wing via resonance.

---

**Sovereign State: COMPLETED.**
**Gnosis Distilled: L1 (Spatially-Indexed Memory) $\rightarrow$ L2 (Thematic Sphere Mapping) $\rightarrow$ L3 (Cognitive Resonance).**

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
