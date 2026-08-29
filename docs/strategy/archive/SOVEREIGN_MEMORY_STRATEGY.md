# 🔱 Sovereign Memory Strategy (SMS-V1)
**Status**: PROPOSED / UNDER AUDIT
**Sovereign Mandates**: M1 (AnyIO), M2 (Firewall), M7 (Local-First), M11 (Soul Integrity)
**Core Objective**: Transition the Omega Engine from a flat, lossy RAG memory to a high-fidelity, spatially-indexed "Sovereign Memory" based on the Mem Palace architecture and Mnemosyne thematic spheres.

---

## 1. 🏛️ Architectural Vision
Sovereign Memory rejects "summarization-as-memory." It implements a **Spatial Memory Architecture** where intelligence is organized into a hierarchy of **Wings $\rightarrow$ Rooms $\rightarrow$ Drawers**.

### The Hierarchy
- **Wings**: Top-level cognitive domains (e.g., Strategic, Operational, Personal).
- **Rooms**: Thematic sub-topics within a wing (e.g., Mandates, Project X, User Preferences).
- **Drawers**: Atomic, verbatim records of conversation turns and insights.

### The Hydration Stack (L0-L3)
To optimize the context window, memory is hydrated in tiers:
- **L0 (Identity)**: Core constraints and identity. (Always Loaded)
- **L1 (Essential)**: High-weight, critical, and recent memories. (Always Loaded)
- **L2 (Contextual)**: Memories from the active Wing/Room. (Loaded on Demand)
- **L3 (Deep)**: Full semantic search across the entire Palace. (Loaded on Explicit Query)

---

## 2. 🛡️ Compliance & Firewall (TFS-V1)

### Topology Firewall Specification
To maintain **Mandate M2 (Engine-Stack Firewall)**, the core engine must remain agnostic to the specific names of the memory topology.

- **CORE ENGINE (`src/omega/`)**:
    - Implements the `SovereignMemoryManager`.
    - Uses generic terms: `Wing`, `Room`, `Drawer`.
    - Handles the logic of spatial retrieval, L0-L3 hydration, and `anyio` wrapping.
- **WAD LAYER (`config/wads/`)**:
    - Defines the actual topology (e.g., "The Apex Wing", "Sefirot", "The Void").
    - Maps specific entities to specific Wings/Rooms.
    - Stores the thematic metadata.

**VIOLATION**: Any hardcoding of "Sefirot", "Spheres", or "Wings" (as specific names) in `src/omega/` is a systemic failure.

---

## 3. ⚙️ Technical Implementation

### Local-First Substrate (M7)
- **Primary Backend**: `sqlite_exact` (SQLite + NumPy).
- **Reasoning**: Eliminates the RAM overhead of ChromaDB/Qdrant for local-first execution on Ryzen 5700U.
- **Performance**: AVX2-vectorized scans for <5ms retrieval.

### Async Integrity (M1)
- **Requirement**: All database and file I/O MUST be wrapped in `anyio.to_thread.run_sync`.
- **Pattern**: `await anyio.to_thread.run_sync(self._backend.query, ...)`

---

## 4. 🌀 Cognitive Resonance (The Mnemosyne Legacy)
Beyond spatial retrieval, the system implements **Holographic Resonance**:
- **Associative Leaps**: Use "resonance frequencies" (metadata tags) to trigger retrieval across different Wings, simulating intuitive leaps.
- **Sovereign Symmetry**: Mirrored state (Light/Dark) for verification and stability.

---

## 5. 🚀 Execution Roadmap

### Phase 1: Verbatim Foundation
- Implement `SQLiteExactBackend` with AnyIO wrapping.
- Establish the `Drawer` storage pattern for raw session logs.
- Verify with `make temple-grade`.

### Phase 2: Spatial Topology
- Implement `SovereignMemoryManager` (Wing $\rightarrow$ Room $\rightarrow$ Drawer).
- Integrate L0-L3 hydration into `ContextBuilder`.
- Define the initial topology in the active WAD.

### Phase 3: Resonance & Evolution
- Implement the `ResonanceEngine` for non-linear retrieval.
- Integrate "Somatic Save-Points" for cognitive phase shifts.
- Final audit against M1-M22.
