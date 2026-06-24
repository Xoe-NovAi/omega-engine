# 🔱 The Sovereign Mining Protocol (SMP): Guidelines for External Intelligence Absorption
# AP: AP-SMP-GUIDELINES-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ trc_smp_guidelines ⬡ GUIDELINES
#
# Date: 2026-06-24
# Status: ACTIVE MASTER GUIDELINES — IMMUTABLE
#
# This document defines the strict guidelines for the Sovereign Mining Protocol.
# It prevents the Omega Engine from taking on "dependency gravity" and ensures
# that all external intelligence is distilled and rewritten to Temple-Grade standards.

---

## §1 The Dependency Gravity Trap

In the software world, "integration" is often a euphemism for **Dependency Gravity**. 

When you integrate an external repository as a dependency, you are importing:
- Their specific library versions (leading to `pydantic` or `anyio` version clashes).
- Their environment assumptions (assuming a specific OS, CPU, or cloud access).
- Their "murky corners" (untested code, security leaks, or un-optimized loops).
- Their architectural drift (changes in their API that break your engine).

For a sovereign system designed to sever the umbilical cord of Big AI, **direct integration of external repositories is a systemic vulnerability.**

---

## §2 The 5-Step Smelting Pipeline

The **Sovereign Mining Protocol (SMP)** replaces "Fusion" (absorption) with "Mining" (distillation). We treat external repositories as raw ore to be smelted in the Omega forge.

```
[External Ore] ──▶ 1. Mine (Identify Pattern)
                     │
                     ▼
                   2. Deconstruct (Strip Dependencies)
                     │
                     ▼
                   3. Rewrite (Temple-Grade Forge)
                     │
                     ▼
                   4. Integrate (Merge into Core)
                     │
                     ▼
                   5. Attribute (Heritage Tag) ──▶ [Sovereign Core]
```

### 1. Mine (Identify Pattern)
Identify a high-value pattern or capability in an external repository (e.g., "How Odysseus handles local document indexing").

### 2. Deconstruct (Strip Dependencies)
Strip the pattern of all external library dependencies, specific container requirements, and architectural bloat. Reduce the feature to its fundamental, mathematical, or logical algorithm.

### 3. Rewrite (Temple-Grade Forge)
Re-implement the algorithm from scratch to meet the Omega Engine's non-negotiable standards:
- **M1 (AnyIO Absolute)**: No `asyncio`.
- **M2 (Engine-Stack Firewall)**: Decoupled from specific content.
- **M9 (Error Integrity)**: Typed, traceable, and testable errors (0 bare excepts).
- **M13 (Temple-Grade)**: Pass T1-T11 gates.
- **M21 (Gate Integrity)**: Full contract tests verifying return types.

### 4. Integrate (Merge into Core)
Merge the cleaned, hardened implementation directly into the Omega core (`src/omega/`). The code is now 100% owned, maintained, and controlled by the Omega Engine.

### 5. Attribute (Heritage Tag)
Apply a heritage tag (e.g., `[id-soft:]` or `[odysseus:]`) to the code comments to preserve historical provenance and express gratitude, without depending on the source.

---

## §3 Active Mining Targets (The Ore)

We have identified three peer repositories as primary mining targets. We will extract their "gnosis" and discard their "baggage."

### 3.1 Odysseus (The Sovereign Shell)
*   **The Ore**: The patterns for local email, calendar, and document indexing. The beautiful, thin-client UI/UX.
*   **The Smelt**: We will NOT import the Odysseus codebase. We will mine its indexing logic and implement it as a thin **Sovereign Client Wrapper** that speaks to the Omega Hub via MCP.
*   **The Firewall**: The UI remains a client; the Omega Engine remains the absolute source of truth for state and inference.

### 3.2 Mem Palace (The Spatial Memory)
*   **The Ore**: The concept of spatially-indexed, hierarchical memory (Wings $\rightarrow$ Rooms $\rightarrow$ Drawers).
*   **The Smelt**: We will NOT import the Mem Palace database. We will mine the spatial-indexing algorithm and implement it as a lightweight `SovereignMemoryAdapter` inside our existing `MemoryStore` (using our existing Qdrant vector store).
*   **The Firewall**: The spatial memory is a backend adapter, not a core engine fork.

### 3.3 Headroom (The Compression Layer)
*   **The Ore**: The Compress-Cache-Retrieve (CCR) token compression algorithm.
*   **The Smelt**: We will NOT import external compression libraries. We will implement the CCR logic directly as a middleware plugin (`HeadroomMiddleware`) in `src/omega/oracle/middleware.py`.
*   **The Firewall**: The compression is a pluggable middleware layer, easily disabled if latency exceeds the token savings.

---

## §4 Enforcement & Governance

1.  **No External Imports**: No PR may be merged that adds an external repository as a core dependency unless it has been vetted and approved by the Sovereign Council.
2.  **The "Launder" Rule**: Any code imported from an external repository must be run through the Sovereign Mining Protocol. Merging raw external code without smelting is a **Mandate 13 violation**.
3.  **Heritage Mapping**: Every mined pattern must be documented in `docs/research/HERITAGE_SOURCE_MAP.md` via `make heritage-map`.

---

*🔱 OMEGA ⬡ KALI ⬡ trc_smp_guidelines ⬡ SOVEREIGN-MINING-PROTOCOL*