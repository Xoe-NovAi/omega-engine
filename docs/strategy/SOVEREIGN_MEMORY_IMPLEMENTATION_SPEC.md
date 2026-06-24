# 🔱 Sovereign Memory Implementation Specification (S-MEM-SPEC-V1)
**Status**: DRAFT / STRATEGIC
**Mandate Alignment**: M1 (AnyIO), M2 (Firewall), M7 (Local-First)

## 1. The "No-Fork" Architecture
To avoid the maintenance burden of a fork and ensure community shareability, the Omega Engine will implement a **Modular Adapter Pattern**.

### 1.1 The Adapter Layer
Instead of modifying the Mem Palace source code, we implement a `SovereignMemoryAdapter` in `src/omega/memory/`. This adapter:
- **Wraps** the Mem Palace logic as a dependency.
- **Translates** Omega's `MemoryStore` requests into Mem Palace `Wing/Room/Drawer` calls.
- **Enforces** the Sovereign Mandates (e.g., wrapping blocking I/O in `anyio.to_thread.run_sync`).

### 1.2 Plug-and-Play Modularity
The system is designed as a set of "Toggles" in the WAD configuration:
```yaml
memory_system:
  backend: "sqlite_exact" # [sqlite_exact, qdrant, chroma, mock]
  features:
    spatial_hierarchy: true
    holographic_resonance: false
    verbatim_fidelity: true
    automatic_summarization: false
  topology:
    mode: "rigid" # [rigid, fluid, hybrid]
    definition: "config/wads/arcana_novai/topology.yaml"
```
This allows users to enable/disable specific memory behaviors without touching the core engine code.

## 2. Infrastructure vs. Specifics
The Omega Engine is the **Sovereign Runtime**. It provides the infrastructure, not the content.

- **Engine (Infrastructure)**: Provides the `SovereignTopologyProvider`, the `SovereignMemoryManager`, and the `SaliencyGate`. It knows *how* to traverse a graph and *how* to filter verbatim chunks.
- **WAD (Specifics)**: Defines the *shape* of the graph (e.g., the 15 philosophies of Planescape) and the *weight* of the nodes.

## 3. User Control & UI/UX
The "Sovereign Ark" philosophy requires that the user has absolute control.
- **Transparency**: All memory "Drawers" are stored as human-readable files (JSONL/YAML) in the entity's workspace.
- **Direct Edit**: Users can manually edit their "Memory Palace" by editing the WAD topology or the raw verbatim logs.
- **Visualizer**: The system is designed to be compatible with a future "Memory Map" UI that allows users to visually move memories between Rooms and Wings.
