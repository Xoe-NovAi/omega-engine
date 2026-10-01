# 🔱 Sovereign Memory Implementation Specification (S-MEM-SPEC-V2)
**Status**: DRAFT — INFRASTRUCTURE-BLOCKED
**Mandate Alignment**: M1 (AnyIO), M2 (Firewall), M7 (Local-First), M6 (Podman Sovereignty)
**Depends On**: MCP Infrastructure fix (see `SOVEREIGN_ARK_BLUEPRINT.md` §XIII.0 Pre-Flight)
**Supersedes**: S-MEM-SPEC-V1 (thin 40-line draft)
**Cross-Reference**: `SOVEREIGN_GUARDRAILS.md` Rules 6-10, `SOVEREIGN_SCHEDULER_SPEC.md` §0.5, `SOVEREIGN_MINING_PROTOCOL.md` §3.2

## 0. Infrastructure Prerequisite

The Sovereign Memory system depends on a stable MCP Hub for cross-agent memory coordination. The 3 critical MCP infrastructure bugs (undefined `get_engine()`, `threading.Lock()` in async context, missing atomic file locking) must be resolved before the memory adapter can safely register with the Hivemind or persist state across agent boundaries.

**Gate**: `omega talk "hello"` + parallel client test must pass before memory adapter development begins.

---

## 1. The "No-Fork" Architecture

To avoid the maintenance burden of a fork and ensure community shareability, the Omega Engine will implement a **Modular Adapter Pattern**. This follows the Sovereign Mining Protocol (SMP, see `SOVEREIGN_MINING_PROTOCOL.md` §2): we mine the pattern, strip dependencies, rewrite to Temple-Grade, and integrate into core.

### 1.1 The Adapter Layer
Instead of modifying the Mem Palace source code, we implement a `SovereignMemoryAdapter` in `src/omega/memory/`. This adapter:
- **Wraps** the Mem Palace logic as a dependency.
- **Translates** Omega's `MemoryStore` requests into Mem Palace `Wing/Room/Drawer` calls.
- **Enforces** the Sovereign Mandates (e.g., wrapping blocking I/O in `anyio.to_thread.run_sync`).
- **Must comply with Guardrails 6-10**: Uses `anyio.Lock()` (R6), atomic file writes (R7), verifiable imports (R8), pre-flight tested (R9), independently testable (R10).

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

### 1.3 Adapter Lifecycle
The adapter follows a strict initialization sequence to prevent race conditions with the MCP Hub:

1. **Registration Phase**: Adapter registers with the Hivemind on startup, acquiring a `WorkspaceLock` for the memory domain.
2. **State Recovery Phase**: Adapter reads persisted state from disk using atomic file locking (Guardrail R7). If the lock file is stale (>30s), it's reclaimed.
3. **Operational Phase**: Adapter handles `MemoryStore` requests with AnyIO threading (Guardrail R6). All file I/O uses atomic `.tmp`→`.json` rename pattern.
4. **Teardown Phase**: Adapter releases the `WorkspaceLock` and flushes pending writes before shutdown.

## 2. Infrastructure vs. Specifics

The Omega Engine is the **Sovereign Runtime**. It provides the infrastructure, not the content.

### 2.1 Engine Layer (Infrastructure)
Provides the core memory machinery:
- **`SovereignTopologyProvider`**: Knows *how* to traverse a graph (force-directed, hierarchical, or Kabbalistic).
- **`SovereignMemoryManager`**: Coordinates the Hot/Warm/Cold provider chain with atomic state transitions.
- **`SaliencyGate`**: Filters fetch results by relevance score before they reach the context builder.
- **`HivemindMemoryBridge`**: Syncs memory state across agents via the MCP Hub, using the newly added Hivemind tools for lock acquisition and live feed updates.

### 2.2 WAD Layer (Specifics)
Defines the *shape* and *meaning* of memory:
- **Topology**: Defines the graph structure (e.g., 15 philosophies of Planescape: Torment, or the 10 Sephiroth of the Kabbalistic tree).
- **Node Weights**: Determines which memories are "hot" vs "cold" based on WAD-specific relevance scoring.
- **Override Mechanism**: WADs can override the default spatial mapping with custom geometry (e.g., Mnemosyne Kabbalistic nodes replacing the force-directed graph).

## 3. Data Flow & Atomicity

Every memory operation must be atomic to prevent corruption:

```
User Query → MemoryStore.get_relevant()
  ├── 1. Acquire anyio.Lock() (per-entity)          [Guardrail R6]
  ├── 2. Hot tier: O(1) dict lookup (no lock needed)
  ├── 3. Warm tier: SQLite read with SHARED lock     [Guardrail R7]
  ├── 4. Cold tier: Qdrant vector search
  ├── 5. SaliencyGate: filter & rank results
  ├── 6. Release lock
  └── 7. Return ranked MemoryExchange list
```

Write operations (add_exchange, prune, migrate) acquire an exclusive lock and use atomic `.tmp`→`.json` writes. If a write fails mid-operation, the `.tmp` file is discarded and the original state is preserved.

## 4. User Control & UI/UX

The "Sovereign Ark" philosophy requires that the user has absolute control.
- **Transparency**: All memory "Drawers" are stored as human-readable files (JSONL/YAML) in the entity's workspace.
- **Direct Edit**: Users can manually edit their "Memory Palace" by editing the WAD topology or the raw verbatim logs.
- **Visualizer**: The system is designed to be compatible with a future "Memory Map" UI that allows users to visually move memories between Rooms and Wings.
- **Privacy**: All memory data is stored locally (M8 Zero Telemetry). No memory data is ever transmitted to external services.

## 5. Implementation Roadmap

### Phase 1: Foundation (Blocked on MCP Infrastructure Fix)
- [ ] Fix 3 critical MCP infrastructure bugs (pre-flight).
- [ ] Verify `omega talk "hello"` + parallel client test pass.
- [ ] Implement `SovereignMemoryAdapter` base class.

### Phase 2: Spatial Adapters
- [ ] Implement `ForceDirectedAdapter` (default topology).
- [ ] Implement `KabbalisticAdapter` (arcana_novai WAD override).
- [ ] Implement `WingRoomDrawerAdapter` (Mem Palace pattern, mined via SMP).

### Phase 3: Hivemind Integration
- [ ] Wire adapter registration with Hivemind awareness.
- [ ] Implement cross-agent memory sync via MCP Hub.
- [ ] Add atomic lock acquisition to adapter lifecycle.

### Phase 4: UI & Tooling
- [ ] Build `omega memory map` CLI command for visualizing topology.
- [ ] Build `omega memory edit` CLI for manual memory manipulation.

## 6. Mandate Compliance

| Mandate | Compliance | How |
|---------|-----------|-----|
| M1 (AnyIO) | ✅ | All async operations use `anyio.Lock()`, `anyio.to_thread.run_sync()` |
| M2 (Firewall) | ✅ | Memory adapters live in `src/omega/memory/`; topology in `config/wads/` |
| M6 (Podman) | ✅ | All storage containers use `UserNS=keep-id` |
| M7 (Local-First) | ✅ | No cloud dependency for memory operations |
| M8 (Zero Telemetry) | ✅ | All memory data stays local |
| M9 (Error Integrity) | ✅ | Typed errors for lock acquisition failure, state corruption |
| M16 (Modularization) | ✅ | Adapters are pluggable; WAD overrides are config-driven |
| M21 (Gate Integrity) ✅ | Contract tests for every adapter method verifying return types |
| M22 (Provenance) | ✅ | All trace_id propagation through memory operations |
