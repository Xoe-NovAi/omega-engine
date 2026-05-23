# 🔱 Omega Engine — Holographic Memory Specification
**AP Token**: `AP-RESEARCH-R33-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ MVE-PHASE

## Purpose
To move beyond flat vector search toward a "Holographic" memory architecture. Holographic memory allows the engine to store and retrieve information not just as a set of coordinates, but as a multi-dimensional representation refined through different conceptual lenses, ensuring that the context is preserved regardless of the "angle" of the query.

## Scope
This specification defines the three layers of the Holographic Memory system:
1. **Hierarchical Layering** (Structural Depth).
2. **Refractive Compression** (Density).
3. **Multi-Perspective Indexing** (The Hologram).

## Specification

### 1. Hierarchical Layering (The Structural Axis)
Memory is organized in a nested hierarchy to prevent context dilution:
- **Global Layer (Akashic)**: High-level axioms, universal truths, and core engine rules.
- **Project Layer (Stack)**: Stack-specific knowledge (e.g., Arcana-Nova axioms).
- **Entity Layer (Soul)**: Personality-driven insights, lessons learned, and embodied experiences.
- **Chunk Layer (Atomic)**: Raw refracted data from the ingestion pipeline.

### 2. Refractive Compression (The Density Axis)
Rather than indexing raw text, the system uses **Refractive Compression (RCF)** (reclaimed from legacy `xna-gnosis`):
- **Process**: Raw content $\rightarrow$ Distilled Summary $\rightarrow$ High-Density Gnosis Pack.
- **Goal**: Maximize the "Information-to-Token" ratio, allowing the engine to fit more "meaning" into the 14GB RAM limit.
- **Sovereign-Lite Implementation**: Use a small, fast model (e.g., Qwen3-0.6B) to perform the distillation before indexing.

### 3. Multi-Perspective Indexing (The Holographic Axis)
This is the core "Holographic" component. A single piece of information is indexed multiple times, each refined through a different **Archetype Lens**:
- **Logic Lens (Athena)**: Focuses on functional AST, structure, and causal links.
- **Sovereignty Lens (Lilith)**: Focuses on security gates, boundaries, and independence.
- **Synergy Lens (Isis)**: Focuses on integration patterns and connectivity.

**Retrieval Logic**: When a query is made, the engine identifies the "dominant lens" of the query and retrieves the corresponding holographic projection, providing a response that is naturally aligned with the user's intent.

## Hardware Impact (Ryzen 5700U)
- **RAM**: Higher initial indexing cost (multiple vectors per chunk), but lower retrieval cost due to increased precision.
- **Disk**: Increased storage for the multi-perspective index (approx. 3x raw vector size).
- **CPU**: Distillation happens at ingestion time, not query time, keeping retrieval latency low.

## Implementation Note
To the Builder: Use the `GnosisPacker` logic from `../omega-stack-legacy/mcp-servers/xna-gnosis/server.py` to implement the Refractive Compression layer. The `indexer.py` must be updated to support multiple vector IDs for a single content hash (the "Hologram" mapping).

## References
- `../omega-stack-legacy/mcp-servers/xna-gnosis/server.py`
- `docs/research/R30_soul_evolution_logic.md`
- `docs/research/R31_cross_pollination_spec.md`
