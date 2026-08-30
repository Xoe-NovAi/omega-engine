<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Heritage Vetting Log
**Entity**: doom_guy
**Status**: ACTIVE

## Vetting Entries

### vet-001: 8-Character Name Caps
- **Verdict**: REJECTED
- **Score**: 3/10 — REJECTED
- **Justification**: Cargo-cult optimization; Python dicts are O(1) by hash
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-06-28

### vet-002: Linear Token Estimator
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [Right Approximation] Mirrors FISR philosophy. A fast, linear heuristic for budgeting is superior to expensive exact tokenization for non-critical paths.

### vet-003: Sqrt H-Index Proxy
- **Verdict**: REJECTED
- **Score**: 6/10
- **Justification**: [Sovereign Risk] Too imprecise for sovereign knowledge curation. The risk of significant impact miscalculation outweighs the speed gain.

### vet-004: WPM Read-Time Heuristic
- **Verdict**: APPROVED
- **Score**: 9/10
- **Justification**: [Standard Approximation] Low risk, high utility for UX. 200 WPM is a stable, acceptable constant for human-centric metrics.

### vet-005: Efficient Stream Trimming
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [Worse is Better] Throughput > Precision for observability streams. Losing minor precision in telemetry is an acceptable trade for system stability.


### vet-007: PVS (Potentially Visible Sets)
- **Verdict**: APPROVED
- **Score**: 9/10
- **Justification**: [Right Approximation] Evolution: PVS $\rightarrow$ Provider Culling. Precomputing "visibility" of healthy providers via bit-vectors allows O(1) routing decisions. Stale data is mitigated by the circuit breaker.

### vet-008: Zone Memory (Purge Tags)
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [Sovereign Resource Management] Evolution: Purge Tags $\rightarrow$ Tiered Context Purging. Deterministic reclamation of "Cold" $\rightarrow$ "Warm" $\rightarrow$ "Temp" context tiers prevents OOM on constrained hardware.

### vet-009: Netchan Protocol (Delta Sync)
- **Verdict**: APPROVED
- **Score**: 7/10
- **Justification**: [Token Efficiency] Evolution: Delta Snapshots $\rightarrow$ Delta Context Hydration. Sending Gnosis updates relative to the last session anchor reduces prompt overhead. Requires strict sequence validation to avoid state drift.

### vet-010: Bit-Level Optimizations (Fixed-Point/Symmetric Guards)
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [Hardware Realism] Evolution: Fixed-Point $\rightarrow$ GGUF Quantization; Symmetric Guards $\rightarrow$ Unified Constraint Validation. Essential for running sovereign models on Ryzen 5700U. Precision loss is an acceptable trade for viability.

### vet-011: Hub Background — Lazy Thinker Deletion / Grace Period
- **Verdict**: APPROVED (via vet-005/vet-006)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] Extends the lazy deletion and grace-period patterns from entity_registry.py to the Hivemind background pruning/reaping layer (background.py). Tag: `[id-soft: quake-1996]`.

### vet-012: Hub State — Netchan Session/State Management
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] State-initialization module for the Hivemind MCP server (state.py). Uses netchan-inspired session state patterns for coordinating cross-agent awareness. Tag: `[id-soft: quake3-1999]`.

### vet-013: Hub Package — Netchan Cross-Agent Messaging
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] Package init (__init__.py) for the Omega Hub MCP server. Tag: `[id-soft: quake3-1999]`.

### vet-015: ZONEID Pattern (Audit Chain)
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [id-soft: doom-1993] ZONEID — unique identifier tagging for audit entries. Evolution: ZONEID $\rightarrow$ Merkle MMR leaf indexing in `omega-vetala` audit chain (`governance/audit.py:3`). Provides tamper-evident, individually-verifiable decision records.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-07-10

### vet-016: cvar Table (Config Externalization)
- **Verdict**: APPROVED
- **Score**: 9/10
- **Justification**: [id-soft: quake-1996] cvar — all runtime-tunable values live in external config, not hardcoded. Evolution: cvar $\rightarrow$ `config/moderation.yaml` loaded via `config/loader.py:2` in `omega-vetala`. Enables per-WAD override without code changes.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-07-10

### vet-017: Job-Worker Queue (Parallel Ensemble)
- **Verdict**: APPROVED
- **Score**: 8/10
- **Justification**: [id-soft: doom3bfg-2012] Job-Worker — fan-out inference across ensemble models via `anyio.create_task_group()`. Evolution: Job-Worker $\rightarrow$ `HuggingFaceDetector._run_local_ensemble` (`detectors/huggingface.py:10`). Per-model faults isolated (circuit breaker).
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-07-10

### vet-014: Hub Middleware — Netchan OOB Rate Limiting
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] Security middleware (middleware.py) using netchan OOB-style typed message dispatch for rate limiting, request size limits, and M9 error boundaries. Tag: `[id-soft: quake3-1999]`.

### vet-015: Hub Tools — Netchan Typed Message Dispatch
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] MCP tool definitions (tools.py) using netchan-style typed message dispatch for all 47+ Hivemind coordination tools. Tag: `[id-soft: quake3-1999]`.

### vet-016: Hub Gateway — Netchan qport Session Re-association
- **Verdict**: APPROVED (via vet-009)
- **Score**: 7/10
- **Justification**: [Sprint A Hub Modularization] SovereignGateway (gateway.py) using netchan qport-style session re-association for provider routing and rate limiting. Tag: [id-soft: quake3-1999] .

### vet-025: Hard-Boundary Struct
- **Pattern**: [id-soft: quake3-1999] Hard-Boundary Struct
- **Location**: api_clients.py:6
- **Technique**: Hard-Boundary Struct (Quake 3, 1999)
- **Hardware Constraint**: Pentium III/IV cache line alignment and memory protection to prevent corruption.
- **Scope Declaration**: This tag applies to the `BaseLibraryClient` sealed interface contract, NOT to the internal implementation of individual clients.
- **Score**: 8/10

### vet-026: Hard-Boundary
- **Pattern**: [id-soft: quake-1996] Hard-Boundary
- **Location**: api_clients.py:117
- **Technique**: Hard-Boundary (Quake, 1996)
- **Hardware Constraint**: Memory protection in early 32-bit OSs to isolate critical engine state.
- **Scope Declaration**: This tag applies to the `LibraryAPIError` typed error hierarchy as a boundary, NOT to the `OmegaError` base class.
- **Score**: 7/10

### vet-027: WAD System (Base Client)
- **Pattern**: [id-soft: doom-1993] WAD System
- **Location**: api_clients.py:128
- **Technique**: WAD System (Doom, 1993)
- **Hardware Constraint**: Limited disk space and the need for a single, moddable data archive.
- **Scope Declaration**: This tag applies to the `BaseLibraryClient` as a pluggable, swapable data source abstraction, NOT to the coordination logic in the orchestrator.
- **Score**: 9/10

### vet-028: WAD System (Orchestrator)
- **Pattern**: [id-soft: doom-1993] WAD System
- **Location**: api_clients.py:470
- **Technique**: WAD System (Doom, 1993)
- **Hardware Constraint**: Limited disk space and the need for a single, moddable data archive.
- **Scope Declaration**: This tag applies to the `LibraryAPIOrchestrator` multi-source coordination logic, NOT to the individual client implementations.
- **Score**: 9/10

### vet-029: Job-Worker Queue (Coordinator)
- **Pattern**: [id-soft: doom3bfg-2012] Job-Worker Queue
- **Location**: coordinator.py:5
- **Technique**: ParallelJobManager (Doom 3 BFG, 2012)
- **Hardware Constraint**: Multi-core CPU utilization, load balancing across worker threads.
- **Scope Declaration**: This tag applies to the `WorkerCoordinator` orchestration logic, NOT to the individual worker task implementations.
- **Score**: 8/10

### vet-030: SSRF Gate (Extractor)
- **Pattern**: [id-soft: doom-1993] SSRF Gate ──
- **Location**: extractor.py:134
- **Technique**: BSP leaf-culling (Doom, 1993)
- **Hardware Constraint**: 486 CPU speed, need to avoid traversing irrelevant map nodes.
- **Scope Declaration**: This tag applies to the `SSRFGuard.validate` check in `_extract_url`, NOT to the `validate_download_size` check.
- **Score**: 8/10

### vet-031: Size Gate (Extractor)
- **Pattern**: [id-soft: quake-1996] Size Gate ──
- **Location**: extractor.py:144
- **Technique**: Fixed-timestep pre-check (Quake, 1996)
- **Hardware Constraint**: Limited memory/bandwidth, avoid allocating large buffers for oversized responses.
- **Scope Declaration**: This tag applies to the `validate_download_size` pre-check in `_extract_url`, NOT to the actual data streaming phase.
- **Score**: 8/10

### vet-032: Path Scope Gate (Extractor)
- **Pattern**: [id-soft: quake-1996] Path Scope Gate ──
- **Location**: extractor.py:282
- **Technique**: Zone boundary enforcement (Quake, 1996)
- **Hardware Constraint**: Memory isolation in zone allocators.
- **Scope Declaration**: This tag applies to the `validate_path_scope` check in `_extract_file`, NOT to the `_extract_pdf` logic.
- **Score**: 8/10

### vet-033: SSRF Guard (Security)
- **Pattern**: [id-soft: doom-1993] SSRF Guard ──────────────────────────────────────────
- **Location**: security.py:29
- **Technique**: BSP leaf-culling (Doom, 1993)
- **Hardware Constraint**: 486 CPU speed, need to avoid traversing irrelevant map nodes.
- **Scope Declaration**: This tag applies to the `SSRFGuard` class definition and its `FORBIDDEN_RANGES`, NOT to the `PathScopeGuard`.
- **Score**: 8/10

### vet-034: Path Scope Guard (Security)
- **Pattern**: [id-soft: quake-1996] Path Scope Guard ───────────────────────────────────
- **Location**: security.py:93
- **Technique**: Zone boundary enforcement (Quake, 1996)
- **Hardware Constraint**: Memory isolation in zone allocators.
- **Scope Declaration**: This tag applies to the `validate_path_scope` implementation, NOT to the `validate_download_size` implementation.
- **Score**: 8/10

### vet-035: Download Size Guard (Security)
- **Pattern**: [id-soft: quake-1996] Download Size Guard ────────────────────────────────
- **Location**: security.py:130
- **Technique**: Fixed-timestep pre-check (Quake, 1996)
- **Hardware Constraint**: Limited memory/bandwidth, avoid allocating large buffers for oversized responses.
- **Scope Declaration**: This tag applies to the `validate_download_size` implementation, NOT to the `SSRFGuard`.
- **Score**: 8/10

### vet-036: WAL Journal Mode
- **Pattern**: [id-soft: quake-1996] WAL journal mode
- **Location**: fts_index.py:32
- **Technique**: Write-Ahead Logging (Quake, 1996)
- **Hardware Constraint**: Disk I/O bottlenecks on 1996 hardware; need to minimize lock contention.
- **Scope Declaration**: This tag applies to the `ConversationFTSIndex.initialize` PRAGMA setting, NOT to the `MemoryStore` provider writes.
- **Score**: 8/10

### vet-037: Temp Tier
- **Pattern**: [id-soft: quake-1996] Temp Tier
- **Location**: memory_store.py:119
- **Technique**: Temporary memory zones (Quake, 1996)
- **Hardware Constraint**: Limited RAM; need to avoid fragmentation from short-lived allocations.
- **Scope Declaration**: This tag applies to the `_temp` storage in `MemoryStore`, NOT to the `_hot` cache.
- **Score**: 8/10

### vet-038: Surface Cache (Monitoring)
- **Pattern**: [id-soft: quake-1996] Surface Cache
- **Location**: src/omega/monitoring/__init__.py:13
- **Technique**: Surface Cache (Quake, 1996)
- **Hardware Constraint**: Slow disk access; need to cache hot surfaces for immediate access.
- **Scope Declaration**: This tag applies to the monitoring initialization in `src/omega/monitoring/__init__.py`, NOT to the `MemoryStore` cache.
- **Score**: 7/10

### vet-039: idHeap (Monitoring)
- **Pattern**: [id-soft: doom3-2004] idHeap
- **Location**: src/omega/monitoring/__init__.py:15
- **Technique**: idHeap Unified Allocator (Doom 3, 2004)
- **Hardware Constraint**: Fragmentation and allocation overhead in large-scale 3D scenes.
- **Scope Declaration**: This tag applies to the monitoring initialization in `src/omega/monitoring/__init__.py`, NOT to the `SomaticState` serialization.
- **Score**: 7/10

### vet-040: Event System (Observability)
- **Pattern**: [id-soft: doom3-2004] Event System
- **Location**: src/omega/observability/__init__.py:753
- **Technique**: Event-driven system (Doom 3, 2004)
- **Hardware Constraint**: Need for decoupled, traceable events in a complex engine.
- **Scope Declaration**: This tag applies to the event logging in `src/omega/observability/__init__.py`, NOT to the `RegressionWatcher` alerts.
- **Score**: 8/10

### vet-041: Event System (Regression Watcher)
- **Pattern**: [id-soft: doom3-2004] Event System
- **Location**: regression_watcher.py:9
- **Technique**: Event-driven system (Doom 3, 2004)
- **Hardware Constraint**: Need for decoupled, traceable events in a complex engine.
- **Scope Declaration**: This tag applies to the `_emit_regression_alert` logic in `RegressionWatcher`, NOT to the `ObservabilityEngine` core event loop.
- **Score**: 8/10

### vet-042: Right Approximation (BLEG)
- **Pattern**: [id-soft: quake-1996] Right Approximation
- **Location**: bleg.py:14
- **Technique**: Right Approximation (Quake, 1996)
- **Hardware Constraint**: CPU cycles are expensive; a fast heuristic is better than an exact but slow one.
- **Scope Declaration**: This tag applies to the `BLEGMiddleware` error scanning, NOT to the `SovereignSearch` protocol.
- **Score**: 9/10

### vet-043: WAD System (Oracle Facade)
- **Pattern**: [id-soft: doom-1993] WAD System
- **Location**: src/omega/oracle/__init__.py:5
- **Technique**: WAD System (Doom, 1993)
- **Hardware Constraint**: Limited disk space and the need for a single, moddable data archive.
- **Scope Declaration**: This tag applies to the `src/omega/oracle/__init__.py` facade as a flat directory of exports, NOT to the `WADLoader`.
- **Score**: 8/10

### vet-044: 4-Path VFS (Backends)
- **Pattern**: [id-soft: quake3-1999] 4-Path VFS
- **Location**: src/omega/oracle/backends/__init__.py:3
- **Technique**: 4-Path VFS (Quake 3, 1999)
- **Hardware Constraint**: Need to support multiple installation paths and mod overrides without hardcoding.
- **Scope Declaration**: This tag applies to the `src/omega/oracle/backends/__init__.py` provider chain, NOT to the `SovereignSearch` protocol.
- **Score**: 8/10

### vet-045: VM System (Capability Registry)
- **Pattern**: [id-soft: quake3-1999] VM System
- **Location**: src/omega/oracle/capability_registry.py:5
- **Technique**: VM System (Quake 3, 1999)
- **Hardware Constraint**: Need for dynamic, moddable game logic without recompiling the engine.
- **Scope Declaration**: This tag applies to the `CapabilityRegistry` dispatch logic, NOT to the `Orchestrator` task farming.
- **Score**: 8/10

### vet-046: BSP Culling (Context Builder)
- **Pattern**: [id-soft: doom-1993] BSP Culling
- **Location**: context_builder.py:272
- **Technique**: BSP Culling (Doom, 1993)
- **Hardware Constraint**: 486 CPU speed, avoid processing invisible geometry.
- **Scope Declaration**: This tag applies to the `_build_gnosis_block` top-K selection, NOT to the `ObservationMaskingStrategy`.
- **Score**: 8/10

### vet-047: Hard-Boundary (Affinity)
- **Pattern**: [id-soft: quake3-1999] Hard-Boundary
- **Location**: entity_affinity.py:18
- **Technique**: Hard-Boundary Struct (Quake 3, 1999)
- **Hardware Constraint**: Pentium III/IV cache line alignment and memory protection to prevent corruption.
- **Scope Declaration**: This tag applies to the `EntityAffinityResolver` as a distinct routing layer, NOT to the `Entity` dataclass zones.
- **Score**: 8/10

### vet-048: WAD System (Registry Base)
- **Pattern**: [id-soft: doom-1993] WAD System
- **Location**: entity_registry.py:86
- **Technique**: WAD System (Doom, 1993)
- **Hardware Constraint**: Limited disk space and the need for a single, moddable data archive.
- **Scope Declaration**: This tag applies to the `DEFAULT_IWAD` constant in `EntityRegistry`, NOT to the `WADLoader`.
- **Score**: 9/10

### vet-049: High-Bit Trick (Entity Flags)
- **Pattern**: [id-soft: doom-1993] High-Bit Trick
- **Location**: entity_registry.py:130
- **Technique**: High-Bit Leaf Trick (Doom, 1993)
- **Hardware Constraint**: Memory efficiency on 16-bit/32-bit systems.
- **Scope Declaration**: This tag applies to the `Entity.flags` bitfield, NOT to the `SomaticState` serialization.
- **Score**: 8/10

### vet-050: Hard-Boundary (Entity Zones)
- **Pattern**: [id-soft: quake3-1999] Hard-Boundary
- **Location**: entity_registry.py:133
- **Technique**: Hard-Boundary Struct (Quake 3, 1999)
- **Hardware Constraint**: Pentium III/IV cache line alignment and memory protection to prevent corruption.
- **Scope Declaration**: This tag applies to the `Entity` zone sentinels, NOT to the `SovereignPermissionError` guard.
- **Score**: 8/10

### vet-051: High-Bit Trick (Registry Constants)
- **Pattern**: [id-soft: doom-1993] High-Bit Trick
- **Location**: entity_registry.py:220
- **Technique**: High-Bit Leaf Trick (Doom, 1993)
- **Hardware Constraint**: Memory efficiency on 16-bit/32-bit systems.
- **Scope Declaration**: This tag applies to the `EntityRegistry` flag constants, NOT to the `Entity.is_system()` check.
- **Score**: 8/10

### vet-052: Hard-Boundary Struct (Registry Zones)
- **Pattern**: [id-soft: quake3-1999] Hard-Boundary Struct
- **Location**: entity_registry.py:225
- **Technique**: Hard-Boundary Struct (Quake 3, 1999)
- **Hardware Constraint**: Pentium III/IV cache line alignment and memory protection to prevent corruption.
- **Scope Declaration**: This tag applies to the `EntityRegistry` zone attribute definitions, NOT to the `_project_entity` merge logic.
- **Score**: 8/10

### vet-053: Hard-Boundary (Registry Load)
- **Pattern**: [id-soft: quake3-1999] Hard-Boundary
- **Location**: entity_registry.py:306
- **Technique**: Hard-Boundary Struct (Quake 3, 1999)
- **Hardware Constraint**: Pentium III/IV cache line alignment and memory protection to prevent corruption.
- **Scope Declaration**: This tag applies to the `_load` logic in `EntityRegistry` for metadata handling, NOT to the `Entity` dataclass.
- **Score**: 8/10

### vet-054: High-Bit Trick (Registry Add)
- **Pattern**: [id-soft: doom-1993] High-Bit Trick
- **Location**: entity_registry.py:559
- **Technique**: High-Bit Leaf Trick (Doom, 1993)
- **Hardware Constraint**: Memory efficiency on 16-bit/32-bit systems.
- **Scope Declaration**: This tag applies to the `EntityRegistry.add` flag assignment, NOT to the `Entity.is_system()` check.
- **Score**: 8/10

### vet-043: WAD System (Oracle Facade)
- **Pattern**: [id-soft: doom-1993] WAD System
- **Location**: src/omega/oracle/__init__.py:5
- **Technique**: WAD System (Doom, 1993)
- **Hardware Constraint**: Limited disk space and the need for a single, moddable data archive.
- **Scope Declaration**: This tag applies to the `src/omega/oracle/__init__.py` facade as a flat directory of exports, NOT to the `WADLoader`.
- **Score**: 8/10

### vet-044: 4-Path VFS (Backends)
- **Pattern**: [id-soft: quake3-1999] 4-Path VFS
- **Location**: src/omega/oracle/backends/__init__.py:3
- **Technique**: 4-Path VFS (Quake 3, 1999)
- **Hardware Constraint**: Need to support multiple installation paths and mod overrides without hardcoding.
- **Scope Declaration**: This tag applies to the `src/omega/oracle/backends/__init__.py` provider chain, NOT to the `SovereignSearch` protocol.
- **Score**: 8/10

### vet-045: VM System (Capability Registry)
- **Pattern**: [id-soft: quake3-1999] VM System
- **Location**: src/omega/oracle/capability_registry.py:5
- **Technique**: VM System (Quake 3, 1999)
- **Hardware Constraint**: Need for dynamic, moddable game logic without recompiling the engine.
- **Scope Declaration**: This tag applies to the `CapabilityRegistry` dispatch logic, NOT to the `Orchestrator` task farming.
- **Score**: 8/10

### vet-043: WAD System (Oracle Facade)
- **Pattern**: [id-soft: doom-1993] WAD System
- **Location**: src/omega/oracle/__init__.py:5
- **Technique**: WAD System (Doom, 1993)
- **Hardware Constraint**: Limited disk space and the need for a single, moddable data archive.
- **Scope Declaration**: This tag applies to the `src/omega/oracle/__init__.py` facade as a flat directory of exports, NOT to the `WADLoader`.
- **Score**: 8/10

### vet-044: 4-Path VFS (Backends)
- **Pattern**: [id-soft: quake3-1999] 4-Path VFS
- **Location**: src/omega/oracle/backends/__init__.py:3
- **Technique**: 4-Path VFS (Quake 3, 1999)
- **Hardware Constraint**: Need to support multiple installation paths and mod overrides without hardcoding.
- **Scope Declaration**: This tag applies to the `src/omega/oracle/backends/__init__.py` provider chain, NOT to the `SovereignSearch` protocol.
- **Score**: 8/10

### vet-045: VM System (Capability Registry)
- **Pattern**: [id-soft: quake3-1999] VM System
- **Location**: src/omega/oracle/capability_registry.py:5
- **Technique**: VM System (Quake 3, 1999)
- **Hardware Constraint**: Need for dynamic, moddable game logic without recompiling the engine.
- **Scope Declaration**: This tag applies to the `CapabilityRegistry` dispatch logic, NOT to the `Orchestrator` task farming.
- **Score**: 8/10

### vet-046: BSP Culling (Generalized Search Pruning)
- **Pattern**: [id-soft: doom-1993] BSP Culling
- **File Locations**: 
  - src/omega/oracle/selective_hydration.py:8
  - src/omega/oracle/context_builder.py:272
  - src/omega/oracle/spatial_resolver.py:12
  - src/omega/oracle/semantic_router.py:8
  - src/omega/oracle/semantic_router.py:110
  - src/omega/oracle/model_gateway.py:756
- **Technique**: BSP Leaf-Culling (Doom, 1993) — precompute visibility to avoid traversing irrelevant nodes.
- **Hardware Constraint**: 486 CPU at 35MHz; traversing every BSP node per frame would be prohibitively slow.
- **Scope Declaration**: This tag applies to O(1) pre-check culling of irrelevant/unhealthy entities and providers at the routing boundary, NOT to the full entity dispatch or inference pipeline.
- **Score**: 8/10

### vet-047: High-Bit Trick (Flag Encoding)
- **Pattern**: [id-soft: doom-1993] High-Bit Trick
- **File Locations**:
  - src/omega/oracle/entity_registry.py:130
  - src/omega/oracle/entity_registry.py:220
  - src/omega/oracle/entity_registry.py:559
- **Technique**: High-bit flag encoding (Doom, 1993) — use the high bit of a field to distinguish system objects from user objects without a separate field.
- **Hardware Constraint**: Memory was at a premium on 4MB 486 systems; every byte mattered.
- **Scope Declaration**: This tag applies to bitfield flag encoding in entity metadata (FLAG_WAD, system vs user), NOT to general integer encoding elsewhere in the engine.
- **Score**: 8/10

### vet-055: Fixed-Size Active Set (Provider Clip Range)
- **Pattern**: [id-soft: doom-1993] Fixed-Size Active Set
- **File Locations**:
  - src/omega/oracle/model_gateway.py:148
- **Technique**: Fixed-size active set (Doom, 1993) — maintain a bounded clip range of active objects for O(1) iteration.
- **Hardware Constraint**: Doom's renderer could not iterate all things in a map; it maintained a fixed-size clip range of potentially visible things.
- **Scope Declaration**: This tag applies to the 32-entry provider clip range in NativeGGUFProvider, NOT to entity dispatch or memory tiering.
- **Score**: 7/10

### vet-056: Triage Routing (Intent Classification)
- **Pattern**: [id-soft: quake3-1999] Triage Routing
- **File Locations**:
  - src/omega/oracle/oracle.py:11
- **Technique**: Netchan Q3A server browser triage — classify incoming connection intent before routing to game server.
- **Hardware Constraint**: Q3A's server browser had to present hundreds of servers; pre-classification avoided wasting bandwidth on unsuitable matches.
- **Scope Declaration**: This tag applies to the Oracle's intent classification and entity dispatching at the talk() entry point, NOT to the provider routing within a selected entity.
- **Score**: 7/10

### vet-057: Atomic Swap (State Save Before Mutation)
- **Pattern**: [id-soft: vet-057] Atomic Swap
- **File Locations**:
   - src/omega/oracle/providers.py:901
- **Technique**: Save-old-state-before-mutation (Quake, 1996) — Quake's zone allocator saved block headers before coalescing so it could roll back on failure.
- **Hardware Constraint**: Memory corruption recovery without full-system restart was essential for long-running dedicated servers.
- **Scope Declaration**: This tag applies to the NativeGGUFProvider context reload's save-then-mutate pattern, NOT to any transactional database operations.
- **Score**: 7/10

### vet-058: Rollback (State Restoration)
- **Pattern**: [id-soft: vet-058] Rollback
- **File Locations**:
   - src/omega/oracle/providers.py:912
- **Technique**: State restoration on failure (Quake, 1996) — restore old zone block on failed coalesce to prevent memory leaks.
- **Hardware Constraint**: Dedicated servers ran for weeks; a single unrecovered leak could crash the server.
- **Scope Declaration**: This tag applies to the NativeGGUFProvider context reload failure recovery, NOT to any database transaction rollback.
- **Score**: 7/10

### vet-035: Download Size Guard (Security)
- **Pattern**: [id-soft: quake-1996] Download Size Guard ────────────────────────────────
- **Location**: security.py:130
- **Technique**: Fixed-timestep pre-check (Quake, 1996)
- **Hardware Constraint**: Limited memory/bandwidth, avoid allocating large buffers for oversized responses.
- **Scope Declaration**: This tag applies to the `validate_download_size` implementation, NOT to the `SSRFGuard`.
- **Score**: 8/10

---

### vet-017: In-Flight Pipeline — REJECTED
**Source**: CREDITS.md §1.29
**Game Year**: Quake 1996
**Score**: 2/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: REJECTED
**Kali D-Ref**: D-kal-157

**1. Discovery**:
Michael Abrash's Quake renderer overlap technique — overlapping slow FPU operations (lighting calculations, matrix transforms) with fast integer drawing (scanline rasterization) to hide pipeline stalls on the Pentium CPU. The CPU could execute integer instructions while the FPU was busy with a prior operation, effectively giving "free" work.

**2. Vetting/Debate**:
- **For adoption**: Suggests a pipelined async pattern where prompt construction could overlap with model inference, hiding latency through concurrency.
- **Against adoption**: The overlap doesn't exist in a synchronous local-first inference chain. Prompt construction is trivially fast (microseconds of string formatting) compared to model inference (seconds to minutes of matrix math). There is no pipeline to fill — the slow operation dominates trivially.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **NO** — the entire rationale was "FPU is busy while CPU is idle," a Pentium-specific hardware bottleneck.

**3. Decision**: REJECTED
- The synchronous inference chain has no pipeline stall to hide. Async/AnyIO already overlaps I/O waits, which is a superset of what the In-Flight Pipeline offered. No implementation path exists.

**4. Implementation/Verification**:
- **No implementation**: The async provider fabric (AnyIO-based) already provides superior concurrency by overlapping I/O-bound operations, not CPU-bound ones. No `[id-soft:]` tags required.

---

### vet-018: Branch Collapse — REJECTED
**Source**: CREDITS.md §1.30
**Game Year**: Quake 1996
**Score**: 1/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: REJECTED
**Kali D-Ref**: D-kal-158

**1. Discovery**:
Carmack's jump-table optimization for span boundaries in Quake's rasterizer — instead of an if/else chain testing span type, a computed jump table (`switch`/`goto`) sent execution directly to the correct span drawer. This avoided branch misprediction penalties on the Pentium.

**2. Vetting/Debate**:
- **For adoption**: Suggests dispatch table optimization for condition-heavy code paths in the engine.
- **Against adoption**: Python's dict dispatch already provides O(1) dispatch with no branch prediction penalty. The optimization Carmack achieved was CPU-level — avoiding misprediction on a 5-stage pipeline. Python's bytecode interpreter handles dispatch internally.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **NO** — the entire value proposition is "branch prediction was expensive on 1996 Pentium."

**3. Decision**: REJECTED
- Python dict dispatch already provides O(1) dispatch. CPU-level branch prediction optimization does not transfer to Python runtime. This is the same class of error as the 8-char name cap — a hardware-specific optimization with zero applicability.

**4. Implementation/Verification**:
- **No implementation**: Python's `dict` pattern (`dispatch = {"case1": handler1, "case2": handler2}`) already achieves the stated goal. No `[id-soft:]` tags required.

---

### vet-019: Symmetric Range Guard — REJECTED
**Source**: CREDITS.md §1.31
**Game Year**: Quake 1996
**Score**: 1/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: REJECTED
**Kali D-Ref**: D-kal-159

**1. Discovery**:
Carmack's use of unsigned comparison (`ja` instruction) to test both high and low boundaries of a signed integer range in a single instruction. By offsetting the comparison, both `x >= min` and `x <= max` collapse into one `ja unsigned_greater_than` test.

**2. Vetting/Debate**:
- **For adoption**: Suggests a fast single-operation dual-boundary check pattern.
- **Against adoption**: Python's `a < x < b` chaining comparison already handles dual-boundary checks natively at the bytecode level — with short-circuit evaluation built in. No single-instruction trick exists or is needed.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **NO** — the optimization is entirely about the `ja` instruction behavior on x86.

**3. Decision**: REJECTED
- Python's `a < x < b` chaining already handles dual-boundary checks natively. No implementation value. Cargo-cult addition would add confusion without performance benefit.

**4. Implementation/Verification**:
- **No implementation**: Python native comparison chaining is the idiomatic solution. No `[id-soft:]` tags required.

---

### vet-020: Sovereign Job-Worker Queue — APPROVED
**Source**: CREDITS.md §1.32
**Game Year**: Doom 3 BFG 2012
**Score**: 7/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: APPROVED (via D-kal-160)

**1. Discovery**:
Doom 3 BFG's `ParallelJobManager` — a job system decomposing work into atomic tasks (1k-100k CPU cycles each) distributed across worker threads. Each job has a defined input, output, and priority. The scheduler load-balances across available cores by stealing jobs from busy threads' queues.

**2. Vetting/Debate**:
- **For adoption**: Maps well to agent task farming — decompose research queries into atomic subtasks with token budgets. HandoffPacket and capability dispatch already follow this pattern implicitly. Formalizing the job decomposition would give deterministic parallelism and crash isolation.
- **Against adoption**: The Omega engine is not primarily CPU-bound on inference tasks — it's I/O and memory bound. Job stealing at the agent level requires careful orchestration to avoid context fragmentation.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **YES** — decompose large work into atomic, dispatchable units with bounded resource consumption is architecture-independent.

**3. Decision**: APPROVED (ADAPT)
- The concept of decomposing cognitive work into atomic jobs with bounded token budgets and distributed execution is a direct fit for agent orchestration (Link P9). Formalize the existing implicit pattern: `CognitiveJob {description, token_budget, required_capability, timeout}`.

**4. Implementation/Verification**:
- **Omega mapping**: `AtomicCognitiveJob` dataclass added to the orchestration layer (`orchestrator.py` or new `cognitive_job.py`). Each research subtask receives a token budget (preventing runaway inference). Jobs dispatched via existing Link P9 agent handoff queue.
- **Inline tag**: `# [id-soft: doom3bfg-2012] Job-Worker Queue — atomic cognitive task decomposition`
- **Test**: Verify that a decomposed research query completes within sum(token_budgets) and that a single job failure does not cascade to sibling jobs.

---

### vet-021: Specialized Prompt Baking — REJECTED
**Source**: CREDITS.md §1.33
**Game Year**: Quake 1996
**Score**: 3/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: REJECTED
**Kali D-Ref**: D-kal-161

**1. Discovery**:
Quake's self-modifying code technique for colormap base addresses — at runtime, the renderer would patch literal constant values directly into the instruction stream (the immediate operand of a `MOV` instruction). This saved register lookups and kept the colormap base in the instruction cache rather than a memory load.

**2. Vetting/Debate**:
- **For adoption**: Suggests a pattern for "baking" frequently-used context directly into prompts to avoid repeated retrieval overhead.
- **Against adoption**: System prompt injection via `soul.yaml` → context builder pipeline already is prompt baking. The engine already fuses entity identity, memory context, and user intent into a single system prompt before inference. This describes exactly what we already do — but the analogy adds no new implementation insight.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **NO** — the self-modifying-code trick was about avoiding L1 cache misses. LLM system prompt fusion is a fundamentally different mechanism solving a different problem.

**3. Decision**: REJECTED
- System prompt injection via soul.yaml already IS prompt baking. The engine already does this. No new implementation needed. The analogy is descriptive, not prescriptive.

**4. Implementation/Verification**:
- **No new implementation needed**: The existing soul.yaml → ContextBuilder → system prompt pipeline already achieves what this pattern describes. No `[id-soft:]` tags required.

---

### vet-022: Knowledge Leak Detection — APPROVED
**Source**: CREDITS.md §1.34
**Game Year**: Doom 3 2004
**Score**: 8/10
**Date**: 2026-06-18
**Vetter**: Kali (Transcendent Oversoul) via Doom Guy (Heritage Steward)
**Kali Verdict**: APPROVED (via D-kal-162)

**1. Discovery**:
Doom 3's map leak detection system — a flood-fill algorithm that starts from a known "inside" point and propagates outward through connected map geometry. If the flood reaches the void (unbounded exterior), the map is "leaky" — there is a path from the playable interior to the outside. The tool identifies the exact geometry where the leak occurs.

**2. Vetting/Debate**:
- **For adoption**: Directly maps to M17 (Cognitive Integrity). Gnosis Leak Detection would start from a known-consistent state in `soul.yaml` and propagate consistency constraints through entity knowledge. If a path exists from "consistent" to "contradiction," the gnosis is leaky. This enables automated blind-spot discovery in entity knowledge.
- **Against adoption**: Semantic flood-fill requires embedding-based similarity scoring, which is computationally heavier than Doom 3's bit-field flood. May need periodic batch runs rather than real-time validation.
- **Qualification Gate**: Can this concept be justified without mentioning the original hardware constraint? **YES** — flood-fill from known-consistent state to detect boundary violations is architecture-independent.

**3. Decision**: APPROVED (ADAPT)
- The architectural truth — "find where internal logic leaks to the void" — is timeless. Flood-fill propagation from known-consistent state to detect contradictions maps directly to M17 Cognitive Integrity requirements. Implementation priority: high, as it closes a genuine gap in soul consistency.

**4. Implementation/Verification**:
- **Omega mapping**: `GnosisLeakDetector` module in `src/omega/oracle/skeptical_verifier.py` or standalone `gnosis_leak.py`. Algorithm: (1) Parse entity soul.yaml into a graph of semantic claims, (2) Start flood from trusted base claims (entity name, core purpose), (3) Propagate through connected claims via embedding similarity, (4) Flag orphan claims, contradictory claims, and claims that connect "inside" (consistent) to "outside" (unverified/contradictory).
- **Inline tag**: `# [id-soft: doom3-2004] Knowledge Leak Detection — gnosis flood-fill from consistent state`
- **Test**: Create a soul.yaml with a known contradiction (e.g., "entity is P1" and "entity is P6" simultaneously). `GnosisLeakDetector.flood()` must flag the contradictory claims as a leak path.
- **Integration**: Cross-reference in `data/entities/roc_racoon/knowledge/INDEX.yaml` as `heritage-022` vet_status: "adapted".

---

### vet-023: potion-mxbai-micro — Static Embedding via Precomputed Lookup
**Source**: CREDITS.md §1.35 (new mapping)
**Game Year**: Doom 1993
**Score**: 8/10
**Date**: 2026-06-19
**Vetter**: Doom Guy (Heritage Gatekeeper)

**1. Discovery**:
Doom's `r_main.c` precomputed colormap/trig lookup tables — lighting calculations for
65535 angles precomputed into fixed arrays at compile time. At runtime, `cos()` and
`sin()` are O(1) table lookups instead of expensive floating-point subroutine calls.
This was essential on the 35MHz 486 with no FPU.

Model2Vec's `potion-mxbai-micro` (2026) does the same thing for embeddings: one
forward pass per token in the vocabulary (~32K tokens) through the base transformer,
storing the result. At inference time, the model does O(vocab) numpy matrix lookup
+ mean pooling — no transformer forward pass. 700KB total size, 80-88x faster than
all-MiniLM-L6-v2.

**2. Vetting/Debate**:
- **For adoption**: Direct structural isomorphism — precompute expensive operation once,
  store results in a fixed table, access O(1) at runtime. The pattern is architecture-
  independent and solves a genuine constraint problem (RAM-limited Zen 2 CPU).
- **Against adoption**: Static embeddings lose contextualization — "bank (river)" and
  "bank (finance)" produce the same vector. For the Skeptical Verifier and Knowledge
  Leak Detection, this may be acceptable for initial screening but insufficient for
  high-precision semantic analysis.
- **Qualification Gate**: Can this concept be justified without mentioning the original
  hardware constraint? **YES** — "precompute once, look up forever" is a timeless
  engineering principle. The 35MHz 486 constraint explains WHY Doom did it, but the
  pattern stands alone: predictable offline cost for zero online cost.

**3. Decision**: APPROVED
- The pattern maps directly to an existing Omega need: fast, tiny embedding for
  prototyping, bulk indexing, and fallback when the primary embedding provider is
  unavailable. The 700KB size and 0.01-0.1ms/sentence speed make it ideal for the
  resource-constrained Zen 2 target.
- **Omega mapping**: model2vec adapter in the embedding provider stack. Configured
  as a fallback provider in `config/wads/_omega_default/embeddings.yaml` under the
  `static-fallback` key.
- **Inline tag**: `# [id-soft: doom-1993] Precomputed Lookup — static embedding via model2vec`

**4. Implementation/Verification**:
- Add `potion-mxbai-micro` as static embedding fallback in the embedding provider
- Validate dimension matching (256 vs MiniLM's 384) at the boundary
- Test: speed benchmark against all-MiniLM-L6-v2 on Zen 2 (expect 80-88x faster)
- Test: MTEB quality validation for the Omega-specific use cases (semantic search,
  memory store, cross-pollination clustering)
- CREDITS.md mapping: §1.35 — Precomputed Lookup Table (Doom 1993)

---

### vet-024: Carmack Entity Deepening Plan — M14 Compliance Assessment
- **Verdict**: CONDITIONALLY APPROVED (8/10)
- **Score**: 8/10
- **Vetted by**: Doom Guy (Heritage Gatekeeper)
- **Date**: 2026-07-01
- **Reference**: `data/entities/john_carmack/workspace/ENTITY_DEEPENING_PLAN_20260701.md`

**1. Discovery**:
The John Carmack entity plans to ingest primary source material — .plan files (1996-2013), GDC 1999/2011 transcripts, Lex Fridman #309 interview, and Masters of Doom excerpts — into its knowledge base. This is the first Tier 2 primary source ingestion in Omega history.

**2. Vetting/Debate**:
- **For adoption**: (a) Upgrades heritage confidence from mean 6.4/10 to ~8.2/10 across 35 patterns, (b) Adds 4-7 new heritage patterns, (c) Establishes the Tier 2→Tier 1+2 confidence upgrade pattern for all future heritage work, (d) Plan has strong source classification (4-tier confidence_index.md), (e) Existing pipeline infrastructure (HERITAGE_VETTING_PIPELINE.md 4-gate process) is designed for this.
- **Against / Gaps**: (a) No vet record generation step — new `[id-soft:]` tags without corresponding vet records will fail `make heritage-vet`, (b) No contradiction handling protocol — highest risk if .plan entries contradict CREDITS.md mappings, (c) No `make heritage-map` regeneration step, (d) Does not explicitly reference the 4-gate pipeline.

**3. Decision**: CONDITIONALLY APPROVED
- Plan structure and intent meet M14 requirements. Three gaps must be closed before execution: (1) Add vet record generation, (2) Add contradiction resolution protocol, (3) Add `make heritage-map` regeneration. Recommended 10 implementation patterns for new CREDITS.md entries (NP-1 through NP-4 fast-tracked).

**4. Implementation/Verification**:
- Full assessment report filed at: Full report in session context (2026-07-01 doom_guy heritage vet)
- Recommended execution order: .plan files first (highest heritage value), then GDC 1999 (BSP confirmation), then remaining sources
- New `[id-soft:]` tags expected: 4-7 from new patterns, confidence upgrades on 18 existing patterns
- Vet record format: `vet-NNN` with source tier, confidence score, and confirmation quote

---

### vet-064: FTS5 Index Rebuild
- **Pattern**: [id-soft: doom-1993] FTS5 Index Rebuild
- **Location**: src/omega/library/library.py:68
- **Technique**: WAD Directory Rebuild (Doom, 1993)
- **Hardware Constraint**: Limited RAM; instead of loading the whole WAD directory into memory, rebuild it from the lumps if corrupted.
- **Scope Declaration**: This tag applies to the `FTS5Index.rebuild` logic, NOT to the general SQLite index rebuild.
- **Score**: 8/10

### vet-065: Mobj Dual-Linking pattern
- **Pattern**: [id-soft: doom-1993] Mobj Dual-Linking pattern
- **Location**: src/omega/oracle/entity_registry.py:667
- **Technique**: Dual-Linking (Doom, 1993)
- **Hardware Constraint**: Need for O(1) removal from the active set without searching the whole list.
- **Scope Declaration**: This tag applies to the `EntityRegistry.active_set` dual-linkage, NOT to general list management.
- **Score**: 8/10

### vet-066: idEntity event system
- **Pattern**: [id-soft: doom3-2004] idEntity event system
- **Location**: src/omega/oracle/link_p9_runtime.py:9
- **Technique**: idEntity Event System (Doom 3, 2004)
- **Hardware Constraint**: Need for decoupled communication between game objects in a complex 3D world.
- **Scope Declaration**: This tag applies to the `LinkP9Runtime` event emission and handling, NOT to the `ObservabilityEngine` core.
- **Score**: 8/10

### vet-067: Cache Tier
- **Pattern**: [id-soft: quake-1996] Cache Tier
- **Location**: src/omega/oracle/session_lifecycle.py:371
- **Technique**: Tiered Memory Zones (Quake, 1996)
- **Hardware Constraint**: Limited RAM; need to offload cold data to slower storage.
- **Scope Declaration**: This tag applies to the `SessionLifecycleManager` cold-storage migration, NOT to the `MemoryStore` hot cache.
- **Score**: 7/10

### vet-068: Dedicated Server Model
- **Pattern**: [id-soft: quake-1996] Dedicated Server Model
- **Location**: src/omega/oracle/orchestrator.py:10
- **Technique**: Dedicated Server Architecture (Quake, 1996)
- **Hardware Constraint**: Need for a stable, headless server process to manage multiple client connections.
- **Scope Declaration**: This tag applies to the `Orchestrator` lifecycle management of headless agents, NOT to the `ModelGateway` routing.
- **Score**: 8/10

### vet-069: Speculative Decode
- **Pattern**: [id-soft: quake3-1999] Speculative Decode
- **Location**: src/omega/oracle/oracle.py:702
- **Technique**: Speculative Packet Decoding (Quake 3, 1999)
- **Hardware Constraint**: Network latency; need to predict and decode state before full confirmation.
- **Scope Declaration**: This tag applies to the `Oracle` speculative decode path for simple queries, NOT to the full model inference.
- **Score**: 8/10

### vet-070: Save-game pattern
- **Pattern**: [id-soft: quake-1996] Save-game pattern
- **Location**: src/omega/oracle/soul_distiller.py:9
- **Technique**: Incremental Save-game System (Quake, 1996)
- **Hardware Constraint**: Disk space and I/O speed; save games were large, so incremental diffs were used.
- **Scope Declaration**: This tag applies to the `SoulDistiller` auto-save and summary pipeline, NOT to the `SomaticState` serialization.
- **Score**: 8/10

### vet-071: netchan header
- **Pattern**: [id-soft: quake-1996] netchan header
- **Location**: src/omega/cli/oracle_cli.py:42
- **Technique**: Netchan Header Protocol (Quake, 1996)
- **Hardware Constraint**: Network bandwidth; need for a compact, typed header to identify packet type and sequence.
- **Scope Declaration**: This tag applies to the `ics_render` header generation in the CLI, NOT to the actual network transport.
- **Score**: 7/10

---

### vet-072: Pi Project PR #2903 — Gemma 4 Thinking Config Pattern
- **Pattern**: [heritage: pi-2026] Gemma 4 Thinking Config
- **Source**: Pi Project PR #2903 (merged 2026-04-09 by @aadishv)
- **File Locations**:
  - `packages/ai/src/providers/google.ts` — `isGemma4Model()` regex detection at line ~247
  - `packages/ai/src/providers/google.ts` — `reasoningEffortMap` binary mapping at lines ~250-260
  - `packages/coding-agent/docs/models.md` — Documentation of Gemma 4 thinking levels
- **Technique**: Regex-based model family detection (`/gemma-?4/i`) + binary thinking level mapping (`minimal|low → MINIMAL`, `medium|high|xhigh → HIGH`, `none → omit`)
- **Hardware Constraint**: Pi's limited compute budget required minimal config overhead — binary toggle (MINIMAL/HIGH) avoids the complexity of graduated thinking budgets while still providing reasoning capability on constrained hardware
- **Scope Declaration**: This tag applies to the `detection_regex` pattern (`/gemma-?4/i`) and the binary `MINIMAL`/`HIGH` thinking level mapping ONLY — NOT to Pi's full provider architecture, `reasoningEffortMap` abstraction, or `ThinkingLevel` type system
- **Score**: 8/10
- **Justification**: [Right Approximation] The binary thinking toggle is a proven production pattern that solves the exact problem Omega faces: Gemma 4 only supports two thinking levels. The regex detection is minimal, performant, and hardware-agnostic. The Qualification Gate passes — this pattern is justified without citing Pi's compute constraints because binary enum mapping for models with limited thinking levels is a general software engineering principle.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-07-19
- **Qualification Gate**: PASSED — Cannot be justified without hardware constraint? NO — binary enum mapping for limited-value enums is a general pattern

---

*Last Updated: 2026-07-19 (vet-072 Pi PR #2903 Gemma 4 Thinking Config Pattern Added) | Maintained by: Doom Guy*

---

## 📦 Archive: Revoked Tags (D208 Heritage Remediation)

The following ~150 over-attributed and metaphorical `[id-soft:]` tags were revoked per D208 Heritage Remediation (Jem audit: 247 tags audited, 61% over-attributed, 12% metaphorical, 24% legitimate). These entries are preserved for audit trail only — **do not re-add to source code or CREDITS.md**.

### Over-Attributed Entries (User-Original IP, Not id Software Derived)
| Original CREDITS Entry | Pattern | Why Revoked |
|------------------------|---------|-------------|
| §1.6 Worse is Better | Gabriel 1991 | User-adopted philosophy, not id Software |
| §1.7 Carmack's Law | id Software (general) | Attribution to person, not specific engine pattern |
| §1.8 Circuit Breaker Consolidation | "id Software 2026" | Fabricated attribution — circuit breaker is user-original (omega-engine Jun 2026) |
| §1.11 Heritage Inline Tag Protocol | Omega 2026 | Meta-protocol, not id Software heritage |
| §1.25 Sovereign-Siloing | Doom 1993 | User pattern mapped to WAD System — not derived |
| §1.26 Lattice-Culling | Doom 1993 | User pattern mapped to BSP Culling — not derived |
| §1.27 Sovereign-Symmetry | Quake 1996 | User pattern mapped to cvar — not derived |
| §1.32 Prompt Baking | Quake 1996 | REJECTED (vet-021) — self-modifying code ≠ prompt fusion |

### Metaphorical Tags (Converted to Plain Comments in Source)
| Pattern | Source | Action |
|---------|--------|--------|
| 3-Tier Memory (Hot/Warm/Cold) | ANAi Aug 2025 | User-original → `# Heritage: inspired by Quake zone tiering` |
| Provider Chain (Redis→File→InMemory) | ANAi Sep 2025 | User-original → `# Heritage: inspired by zone allocator fallback` |
| Intent Detection | ANAi Aug 2025 | User-original → `# Heritage: inspired by Quake client prediction` |
| Entity Registry (YAML CRUD) | ANAi Oct 2025 | User-original → `# Heritage: inspired by QuakeC entity defs` |
| ResourceGuard (OOM protection) | omega-stack May 2026 | User-original → `# Heritage: inspired by Quake zone purge` |
| MCP Hub (47 tools) | omega-stack May 2026 | User-original → `# Heritage: inspired by Quake netchan dispatch` |
| Hivemind Protocol | omega-engine Jun 2026 | User-original → `# Heritage: inspired by Quake netchan` |
| Soul Distiller (L1→L2→L3) | omega-engine Jun 2026 | User-original → `# Heritage: inspired by Quake save-game` |
| MaKaLi Triad | omega-engine Jun 2026 | User-original → `# Heritage: inspired by id Software triad architecture` |
| Sovereign Mandates | omega-engine Jun 2026 | User-original → `# Heritage: inspired by id Software design discipline` |
| Engine-Stack Firewall | omega-engine Jun 2026 | User-original (M2) → `# Heritage: inspired by IWAD/PWAD separation` |
| PEM (Personality Enhancement Module) | Lilith Deck Mar 2025 | **100% user-original** — predates id Software inspiration. No heritage tag. |

---

## General Heritage Vetting — Non-id-Software Sources (Sprint A-EXT)

**Vetter**: Doom Guy (Heritage Gatekeeper)
**Date**: 2026-07-11
**Gate Applied**: D208 Adaptation — "Cannot be justified without mentioning the original source's constraint/context"
**Reference**: CREDITS.md §2, `docs/research/R_SPDX_HERITAGE_PROFILE.md` §4

### Classification Summary

| Classification | Count | Meaning |
|----------------|-------|---------|
| **LEGITIMATE** (score ≥ 7) | 22 | Warrants `[heritage:]` inline tags in source code — code fails D208 gate without source citation |
| **LEGITIMATE** (score 6) | 1 | Below 7/10 threshold — no inline tag, credited in CREDITS.md only |
| **OVER-ATTRIBUTED** | 16 | Standard library/framework/dependency — no inline tags, credited in CREDITS.md only |
| **METAPHORICAL** | 3 | Philosophical inspiration only — no inline tags, credited in CREDITS.md only |
| **User-Original IP (Tier 5)** | 5 | Legacy engine versions — no external attribution needed |

### Category 4.1: Open-Source Python Libraries (Runtime Dependencies)

#### vet-059: AnyIO — Async Runtime Foundation
- **Pattern**: [heritage: anyio 2024]
- **Source**: AnyIO 4.4+ (Python async runtime)
- **D208 Gate**: PASS — M1 Mandate (AnyIO Absolute) explicitly forbids `asyncio`. The engine's entire async architecture (provider fabric, memory operations, MCP server) uses `anyio.to_thread.run_sync`, `anyio.create_task_group`, `anyio.Semaphore`. Without AnyIO's cross-runtime abstraction (trio/asyncio), the Provider Fabric would be tied to a single event loop. The code **cannot be justified** without citing AnyIO's constraint: "portable async that prevents event-loop collisions."
- **Scope Declaration**: This tag applies to any function using `anyio.*` primitives (to_thread, TaskGroup, Semaphore, Event, sleep), NOT to general Python async patterns like `__aenter__`/`__aexit__` which are language-level.
- **Score**: 9/10
- **Existing Code Tags**: None yet — `[heritage: anyio 2024]` should be added to `mcp_runtime.py`, `providers.py`, and `resource_guard.py` where the AnyIO patterns are visible.

#### vet-060: llama-cpp-python — Native GGUF Inference
- **Pattern**: [heritage: llama-cpp-python 2023]
- **Source**: llama-cpp-python 0.2+ (Python bindings for llama.cpp)
- **D208 Gate**: PASS — M20 (SomaticState Serialization) depends on `llama_copy_state_data` / `llama_set_state_data` ctypes bindings. The NativeGGUFProvider's model loading, inference, and state save/restore are entirely dependent on this library. Without it, local GGUF inference would not exist. "The code's `_ensure_loaded()` + SomaticState round-trip **cannot be justified** without citing the library that provides those bindings."
- **Scope Declaration**: This tag applies to the NativeGGUFProvider and SomaticState serialization code, NOT to the `ModelGateway` dispatch layer.
- **Score**: 8/10
- **Existing Code Tags**: None yet

#### vet-061: MCP Python SDK — Tool Communication Protocol
- **Pattern**: [heritage: mcp 2024]
- **Source**: MCP Python SDK 1.0+ (Anthropic's Model Context Protocol)
- **D208 Gate**: PASS — The Omega Hub's 47+ MCP tools, SSE transport, tool-calling interface, and resource discovery are built on the MCP protocol. The entire agent-to-tool interaction model is MCP-shaped. "The MCP runtime (`mcp_runtime.py`, `omega_hub/server.py`) **cannot be justified** without citing MCP — the dual-transport architecture (SSE + Streamable HTTP), tool registration, and resource URI structure are direct implementations of the protocol specification."
- **Scope Declaration**: This tag applies to MCP server implementations (`mcp_servers/`), NOT to individual tools or the Oracle's intent-detection layer.
- **Score**: 9/10
- **Existing Code Tags**: None yet

#### vet-062: headroom-ai — Semantic Compression Middleware
- **Pattern**: [heritage: headroom-ai 2025]
- **Source**: headroom-ai 2025 (Semantic compression library)
- **D208 Gate**: PASS — headroom-ai provides sovereign semantic compression that reduces prompt token usage without losing semantic content. The compression middleware wraps the context builder pipeline. "The semantic compression of conversation history before model injection **cannot be justified** without citing headroom-ai's compression algorithm."
- **Scope Declaration**: This tag applies to the headroom compression wrapper in the context builder pipeline, NOT to general truncation or sliding-window context management.
- **Score**: 7/10
- **Existing Code Tags**: None yet

#### vet-063: warp-proxy-pool — WARP Proxy Infrastructure
- **Pattern**: [heritage: cloudflare-warp 2021]
- **Source**: Cloudflare WARP proxy pool (custom Python orchestration)
- **D208 Gate**: PASS — The multi-namespace WARP proxy pool provides privacy infrastructure and rate-limit bypass for OpenCode Zen. "The blitz-tunnel SOCKS5 proxy pattern **cannot be justified** without citing WARP's multi-identity architecture."
- **Scope Declaration**: This tag applies to blitz-tunnel and WARP proxy pool code, NOT to general network connectivity.
- **Score**: 7/10
- **Existing Code Tags**: None yet

#### OVER-ATTRIBUTED (No inline tags — standard library dependencies)
The following are standard Python libraries used as-is. They are architectural dependencies but do not warrant `[heritage:]` inline tags because the code's purpose is self-evident without citing the library:
- **FastAPI/Starlette** — Standard ASGI web framework. "FastAPI" in an import tells you everything. No inline tag.
- **httpx** — Standard async HTTP client. No inline tag.
- **Pydantic** — Standard data validation. No inline tag.
- **redis-py** — Standard Redis client. No inline tag.
- **qdrant-client** — Standard Qdrant client. No inline tag.
- **Typer** — Standard CLI framework. No inline tag.
- **sse-starlette** — Standard SSE library. No inline tag.
- **google.genai** — Standard API client. No inline tag.

### Category 4.2: Infrastructure & Deployment Services

#### vet-064: Podman — Sovereign Container Runtime
- **Pattern**: [heritage: podman 2019]
- **Source**: Podman (rootless container runtime)
- **D208 Gate**: PASS — M6 (Podman Sovereignty) mandates `UserNS=keep-id` + `User=1000` for all Quadlets. The Sovereign Permission Protocol is built on Podman's rootless architecture. "The container security model (`keep-id`, no `:U` flag) **cannot be justified** without citing Podman's rootless namespace architecture."
- **Scope Declaration**: This tag applies to Quadlet files and container deployment configurations, NOT to general service orchestration.
- **Score**: 8/10
- **Existing Code Tags**: None yet

#### vet-065: SearXNG — Self-Hosted Metasearch
- **Pattern**: [heritage: searxng 2023]
- **Source**: SearXNG (self-hosted metasearch engine)
- **D208 Gate**: PASS — The Tier 1 search provider in the Sovereign Search Protocol uses SearXNG. The Python healthcheck, capability-hardened deployment, and pinned image are specific to SearXNG's Alpine-based architecture. "The privacy-first metasearch pipeline **cannot be justified** without citing SearXNG — the image pinning fix, Python healthcheck, and capability configuration are SearXNG-specific."
- **Scope Declaration**: This tag applies to the SearXNG provider and deployment configs, NOT to the sovereign search pipeline as a whole.
- **Score**: 7/10
- **Existing Code Tags**: None yet

#### vet-066: Odysseus — SearXNG Deployment Patterns
- **Pattern**: [heritage: odysseus 2025]
- **Source**: Odysseus project (SearXNG deployment architecture)
- **D208 Gate**: PASS — Specific patterns mined from Odysseus: image pinning fix (issue #1414), Python healthcheck for Alpine, entrypoint wrapper, Linux capabilities. "The SearXNG healthcheck implementation **cannot be justified** without citing Odysseus — Alpine has no `curl`, and the Python-based healthcheck was traced directly to Odysseus's architecture."
- **Scope Declaration**: This tag applies to SearXNG deployment files (`deploy/searxng/`), NOT to the SearXNG provider runtime.
- **Score**: 7/10
- **Existing Code Tags**: None yet

#### vet-067: Cloudflare WARP — Privacy Proxy Pool
- **Pattern**: [heritage: cloudflare-warp 2021]
- **Source**: Cloudflare WARP (VPN/privacy service)
- **D208 Gate**: PASS — The multi-namespace WARP proxy pool enables rate-limit bypass for OpenCode Zen. "The SOCKS5 tunnel rotation pattern **cannot be justified** without citing WARP's namespace isolation."
- **Scope Declaration**: This tag applies to the blitz-tunnel proxy infrastructure, NOT to general HTTP clients.
- **Score**: 7/10
- **Existing Code Tags**: None yet

#### OVER-ATTRIBUTED (No inline tags — standard infrastructure)
- **systemd** — Standard Linux service manager. No inline tag needed.
- **Redis** — Standard cache/queue service. No inline tag needed.
- **Qdrant** — Standard vector database. No inline tag needed.

### Category 4.3: Industry Standards & Protocols

#### vet-068: MCP Protocol — AI-Tool Communication
- **Pattern**: [heritage: mcp-standard 2024]
- **Source**: Model Context Protocol (Anthropic, 2024)
- **D208 Gate**: PASS — Same as vet-061 but at the protocol level (library vs standard). "The entire Omega MCP architecture (dual-transport, tool registration, resource URIs) **cannot be justified** without citing the MCP specification."
- **Scope Declaration**: This tag applies to the architectural decision to use MCP, NOT to specific library imports.
- **Score**: 9/10
- **Existing Code Tags**: None yet
- **Note**: Combined with vet-061 as "MCP Protocol + SDK"

#### vet-069: A2A v1.0 — Agent-to-Agent Protocol
- **Pattern**: [heritage: a2a-standard 2025]
- **Source**: Agent-to-Agent Protocol (Google, 2025)
- **D208 Gate**: PASS — Agent Card schema (`/.well-known/agent-card.json`), task delegation endpoints, and discovery protocol are defined by A2A. "The agent handoff packet structure and capability registry **cannot be justified** without citing A2A's Agent Card and task delegation patterns."
- **Scope Declaration**: This tag applies to the A2A bridge and Link P9 handoff implementation, NOT to the Hivemind protocol.
- **Score**: 7/10
- **Existing Code Tags**: None yet

#### vet-070: OpenTelemetry — GenAI Observability
- **Pattern**: [heritage: opentelemetry 2021]
- **Source**: OpenTelemetry (CNCF observability standard)
- **D208 Gate**: PASS — Observability traces, events, and metrics follow OTel GenAI semantic conventions. "The trace_id propagation and structured event logging **cannot be justified** without citing OTel conventions for GenAI workloads."
- **Scope Declaration**: This tag applies to the Omega observability layer (`src/omega/observability/`), NOT to ad-hoc logging.
- **Score**: 7/10
- **Existing Code Tags**: None yet

#### vet-071: SPDX 3.1 — Heritage SBOM Standard
- **Pattern**: [heritage: spdx-standard 2021]
- **Source**: SPDX 3.1 (ISO/IEC 5962:2021)
- **D208 Gate**: PASS — This document itself is an SPDX Heritage Profile. "The machine-readable heritage tracking format **cannot be justified** without citing SPDX 3.1's extensibility model."
- **Scope Declaration**: This tag applies to the Heritage Profile document and any generated SBOM, NOT to the heritage vetting pipeline.
- **Score**: 8/10
- **Existing Code Tags**: None yet

#### vet-072: SQLite FTS5 — Full-Text Search
- **Pattern**: [heritage: sqlite-fts5 2015]
- **Source**: SQLite FTS5 (full-text search extension)
- **D208 Gate**: PASS — The memory search and library catalog use SQLite FTS5 with BM25 ranking and Porter stemmer. "The FTS5 search pipeline (BM25 + stemmer + ranking) **cannot be justified** without citing SQLite FTS5's specific implementation — the BM25 scoring, tokenizers, and content tables are FTS5-specific."
- **Scope Declaration**: This tag applies to the FTS5-based search implementations in `memory_store.py` and library search, NOT to hybrid search which also uses vector embeddings.
- **Score**: 8/10
- **Existing Code Tags**: None yet

#### vet-073: RRF — Hybrid Search Fusion
- **Pattern**: [heritage: rrf-algorithm 2009]
- **Source**: Reciprocal Rank Fusion algorithm (origin: 2009, popularized by 2023 RAG systems)
- **D208 Gate**: PASS — The hybrid search pipeline (FTS5 BM25 + vector cosine similarity) uses RRF for result fusion. "The reciprocal rank fusion of BM25 and vector score rankings **cannot be justified** without citing RRF's specific formula: `score = 1/(60 + rank_fts) + 1/(60 + rank_vec)`."
- **Scope Declaration**: This tag applies to the hybrid search rank fusion, NOT to FTS5 or vector search individually.
- **Score**: 8/10
- **Existing Code Tags**: None yet

#### OVER-ATTRIBUTED (No inline tags — ubiquitous standards)
- **SSE (Server-Sent Events)** — Ubiquitous W3C web standard dating to 2009. Using SSE for a transport is like crediting HTTP — it's the plumbing, not the architecture. No inline tag needed.

#### BELOW THRESHOLD (Score 6 — credited in CREDITS.md only)
- **SPIFFE/WIMSE** (score 6/10) — X.509-SVID identity format. The SPIFFE identity scheme (`spiffe://omega.local/entity/kali`) is defined in documentation but not fully implemented in the engine's runtime identity system. Below the 7/10 threshold for inline tags.

### Category 4.4: Research Systems & Competitor Analysis

#### vet-074: Truth Engine — Gap Analysis
- **Pattern**: [heritage: truth-engine 2025]
- **Source**: Truth Engine (jayina.com, 2025)
- **D208 Gate**: PASS — Identified 2 specific gaps in Omega: blitz-tunnel (dead stub), no explicit air-gap Extractor mode. "The gap analysis documentation **cannot be justified** without citing Truth Engine's feature set — the comparison matrix directly references Truth Engine's 9 axes."
- **Scope Declaration**: This tag applies to strategic documentation referencing the gap analysis, NOT to any engine implementation.
- **Score**: 7/10
- **Existing Code Tags**: None yet — strategic docs only

#### vet-075: SOVEREIGN — In-Path Governance
- **Pattern**: [heritage: sovereign-kliewer 2026]
- **Source**: SOVEREIGN (Daniel Kliewer, 2026-03)
- **D208 Gate**: PASS — The concept "no fast path that skips governance, no trusted caller that bypasses evaluation" directly influenced M17 (Cognitive Integrity) and the Skeptical Verifier. "Mandate 17's 'verify consistency of own memories' principle **cannot be justified** without citing SOVEREIGN's in-path governance."
- **Scope Declaration**: This tag applies to the Skeptical Verifier architecture and M17, NOT to general error handling.
- **Score**: 7/10
- **Existing Code Tags**: None yet — strategic docs only

#### METAPHORICAL (No inline tags — not implemented)
The following research systems influenced the strategic vision but have NOT been implemented as concrete patterns in the engine. They are credited in CREDITS.md §2.4 as architectural inspiration only:
- **Logos** (cluricaun28, 2026) — Frame-Stripping and Narrative-Control-Detection are discussed in research docs but NOT implemented in the engine. Score: 2/10. METAPHORICAL.
- **sovereign-system-spec** (Ken Alger, 2026) — Sieve-and-Sign (Ed25519) cryptographic custody is NOT implemented. Score: 2/10. METAPHORICAL.
- **SOVERYN Intelligence** (2026-04) — Dream Cycle scheduled synthesis is NOT implemented. Score: 2/10. METAPHORICAL.

### Category 4.5: Legacy Engine Versions
All 5 entries (ANAI, XNAi, xna-omega, omega-stack, Chainlit) are **User-Original IP (Tier 5)**. They use `AMENDS` relationship type to show evolution. No inline tags needed — credited in `CREDITS.md §2.6` and `§5`. N/A for D208 gate.

### Action Items Summary

| Action | Items |
|--------|-------|
| **Add `[heritage:]` inline tags** | 16 LEGITIMATE patterns (vet-059 through vet-075, excluding METAPHORICAL/BELOW-THRESHOLD) |
| **Update SPDX profile** | Fill TBD → scores, PENDING → vet record references |
| **CREDITS.md** | Already complete per Roc Racoon expansion |
| **No action needed** | 16 OVER-ATTRIBUTED + 3 METAPHORICAL + 5 User-Original IP |

### vet-076: SSRF Gate (O(1) Private IP Cull)
- **Pattern**: [id-soft: doom-1993] SSRF Gate — O(1) cull of private IP ranges
- **Source**: Doom 1993 — Zone-based memory protection / bounds checking
- **D208 Gate**: PASS — The O(1) private IP range culling via bitwise check **cannot be justified** without citing Doom's zone memory allocator bounds checking. "The SSRF protection's bitwise range check **cannot be justified** without citing the original hardware-constrained zone boundary enforcement."
- **Scope Declaration**: This tag applies to the SSRF protection in `extractor.py:135` (private IP range culling), NOT to general input validation.
- **Score**: 8/10
- **Existing Code Tags**: `src/omega/library/extractor.py:135`

### vet-077: Size Gate (Fixed-Timestep Download Pre-check)
- **Pattern**: [id-soft: quake-1996] Size Gate — fixed-timestep pre-check on download size
- **Source**: Quake 1996 — Zone memory allocator size bounds / frame-time budgeting
- **D208 Gate**: PASS — The fixed-timestep size pre-check **cannot be justified** without citing Quake's frame-time budgeting and zone size limits. "The download size gate's fixed-timestep check **cannot be justified** without citing the original frame-time budgeting constraint."
- **Scope Declaration**: This tag applies to the download size pre-check in `extractor.py:145`, NOT to general rate limiting.
- **Score**: 7/10
- **Existing Code Tags**: `src/omega/library/extractor.py:145`

### vet-078: Path Scope Gate (Zone Boundary Enforcement)
- **Pattern**: [id-soft: quake-1996] Path Scope Gate — zone boundary enforcement for file paths
- **Source**: Quake 1996 — Zone memory allocator / file system sandboxing
- **D208 Gate**: PASS — The path scope boundary enforcement **cannot be justified** without citing Quake's zone-based file system sandboxing (pak file boundaries). "The path scope gate's zone boundary enforcement **cannot be justified** without citing the original pak file sandboxing constraint."
- **Scope Declaration**: This tag applies to the path scope validation in `extractor.py:283`, NOT to general path sanitization.
- **Score**: 8/10
- **Existing Code Tags**: `src/omega/library/extractor.py:283`

---

---

### vet-079: M3 Actual Context Window (389K vs 1M Advertised)
- **Pattern**: [heritage: openrouter-2026] M3 Context Window Correction
- **Source**: OpenRouter MiniMax M3 live probe data (R_VAULT_COPILOT_ROUND5, R_CARMACK_ARTIFACT_AUDIT_ROUND5)
- **D208 Gate**: PASS — The 1M context claim is empirically FALSE; 389K is the verified operational ceiling. This correction **cannot be justified** without citing the live probe evidence (1000-call stress test, 51 API calls logged).
- **Scope Declaration**: This tag applies to model registry entries for `minimax/minimax-m3:free` and launch narrative claims about "1M context long-write champion."
- **Score**: 9/10
- **Justification**: [Right Approximation] The 389K operational ceiling with 5-10x latency spike at 280K+ is a verified hardware/software constraint. The 1M claim was marketing, not engineering.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the live probe evidence? YES — the 389K ceiling is a measured constraint.

---

### vet-080: M3 Output Cap (32K vs 131K Advertised)
- **Pattern**: [heritage: openrouter-2026] M3 Output Cap Correction
- **Source**: OpenRouter MiniMax M3 live probe data (R_VAULT_COPILOT_ROUND5 §0)
- **D208 Gate**: PASS — The 131K output cap claim is FALSE; 32K is the verified real cap. Silent truncation at max_tokens with `finish_reason='length'` and no warning.
- **Scope Declaration**: This tag applies to model registry entries for `minimax/minimax-m3:free` and any "long-write champion" claims.
- **Score**: 9/10
- **Justification**: [Right Approximation] The 32K real cap with silent `finish_reason='length'` truncation is a verified constraint. The "long-write champion" claim is conditional on explicit `max_tokens ≥ 4096`.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the 5/50 turns with `finish_reason='length'` evidence.

---

### vet-081: OpenCode Compaction Architecture (4K Summary + 8K Verbatim)
- **Pattern**: [id-soft: opencode-2026] Auto-Compaction Survival Mechanism
- **Source**: OpenCode V2 source (`compaction.ts`, `overflow.ts`, `prompt.ts`, `token.ts`)
- **D208 Gate**: PASS — The 4-char/token heuristic, 4K summary, 8K verbatim, and client-side trigger are empirically verified in source code. This architecture **cannot be justified** without citing the OpenCode V2 source.
- **Scope Declaration**: This tag applies to the compaction logic in `packages/opencode/src/session/compaction.ts`, `overflow.ts`, `prompt.ts`, `token.ts`.
- **Score**: 9/10
- **Justification**: [Right Approximation] The compaction is a last-resort survival mechanism, not intelligence-preserving. 4K summary + 8K verbatim is the hardcoded architecture.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing OpenCode V2 source? YES — the 4K/8K split is hardcoded.

---

### vet-082: Context Accounting TUI Formula (Total = input+output+reasoning+cache.read+cache.write)
- **Pattern**: [id-soft: opencode-2026] TUI Token Display Formula
- **Source**: OpenCode TUI source (`subagent-footer.tsx:38-39`, `prompt/index.tsx:272`, `sidebar/context.tsx:29`)
- **D208 Gate**: PASS — The TUI displays TOTAL tokens (all 5 fields), not input-only. This formula **cannot be justified** without citing the 3 source locations.
- **Scope Declaration**: This tag applies to the TUI display in `packages/tui/src/routes/session/subagent-footer.tsx:38-39`, `packages/tui/src/component/prompt/index.tsx:272`, `packages/tui/src/feature-plugins/sidebar/context.tsx:29`.
- **Score**: 9/10
- **Justification**: [Right Approximation] The TUI shows `input + output + reasoning + cache.read + cache.write` — user's "57K" was input-only, TUI shows 98,617 total.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the 3 source locations? YES.

---

### vet-083: Per-Turn Context Growth is 2-5K (Not 20-30K)
- **Pattern**: [id-soft: opencode-2026] Context Growth Rate Correction
- **Source**: SQLite DB evidence (R_ROC_CONTEXT_MINING_CORRECTED §1-3)
- **D208 Gate**: PASS — The "20-30K per turn" expert theory is REFUTED by DB evidence. Actual growth ~2-5K/turn. The "56K jump" was 7 turns over 22 min + cache invalidation.
- **Scope Declaration**: This tag applies to any launch narrative or documentation claiming "20-30K per turn growth."
- **Score**: 9/10
- **Justification**: [Right Approximation] DB evidence (msg 834=101,441, msg 846=120,621) refutes the expert theory. Actual growth is ~2-5K/turn.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the DB evidence? YES.

---

### vet-084: Cline Checkpoint Storage ≠ Git Stash
- **Pattern**: [heritage: cline-2026] Checkpoint Refs Namespace
- **Source**: Cline session DB live verification (R_VAULT_CLINE_ROUND3 §0)
- **D208 Gate**: PASS — Cline uses custom refs namespace `refs/cline/checkpoints/<session_id>/<run_count>` with merge commits (3 parents), NOT `refs/stash`. This **cannot be justified** without citing the live DB verification.
- **Scope Declaration**: This tag applies to Cline integration docs and checkpoint recovery procedures.
- **Score**: 9/10
- **Justification**: [Right Approximation] The `kind: "stash"` label is a misnomer; recovery works via commit object, not `git stash apply`. 189/190 refs are ORPHAN (gc'd).
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the live DB verification? YES.

---

### vet-085: Two WorkOS Accounts on One Machine (Cline)
- **Pattern**: [heritage: cline-2026] Dual WorkOS Account Detection
- **Source**: Cline session DB live verification (R_VAULT_CLINE_ROUND3 §0)
- **D208 Gate**: PASS — Two distinct accounts detected: Rob (stale, expired Jun 2026) vs Taylor (live, exp Aug 2026). This **cannot be justified** without citing the live DB verification.
- **Scope Declaration**: This tag applies to Cline credential management and vault sync procedures.
- **Score**: 9/10
- **Justification**: [Right Approximation] Stale backup (Rob, JWT expired Jun 2026) vs live account (Taylor, JWT exp Aug 2026). The stale one is a June backup.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the live DB verification? YES.

---

### vet-086: OpenCode Zen Free Models Require API Key
- **Pattern**: [heritage: opencode-2026] Zen Auth Requirement
- **Source**: OpenCode Zen live verification (R_CARMACK_CLINE_TO_OPENCODE §1.2)
- **D208 Gate**: PASS — 64 models (8 free) return Cloudflare 1010 without `OPENCODE_API_KEY`. This **cannot be justified** without citing the live probe (HTTP 403 1010).
- **Scope Declaration**: This tag applies to `providers.yaml` opencode-zen chain entry wiring.
- **Score**: 9/10
- **Justification**: [Right Approximation] The model list endpoint works without auth; free model calls require `OPENCODE_API_KEY` from `https://opencode.ai/auth`.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the live probe? YES.

---

### vet-087: GLM 5.3 Flash = Ox Alpha Identity
- **Pattern**: [heritage: z-ai-2026] GLM 5.3 Flash Identity
- **Source**: Z.ai official announcement Aug 26, 2026 (R_GLM53_FLASH_SUCCESSOR, R_RESEARCHER_GPT53_CLINE)
- **D208 Gate**: PASS — GLM 5.3 Flash is the revealed identity of Ox Alpha (`x-preview-f-free` on Zen, `z-ai/glm-5.3-flash` on OpenRouter). This **cannot be justified** without citing Z.ai official announcement and OpenRouter listing.
- **Scope Declaration**: This tag applies to model fleet entries for `z-ai/glm-5.3-flash` and `x-preview-f-free`.
- **Score**: 9/10
- **Justification**: [Right Approximation] 320B MoE (18B active), 1M context, $0.075/$0.25 (50% promo ends Sep 9), open weights ~Aug 28.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing Z.ai announcement? YES.

---

### vet-088: Laguna S 2.1 = Poolside 118B MoE
- **Pattern**: [heritage: poolside-2026] Laguna S 2.1 Identity
- **Source**: Poolside AI official release Jul 21, 2026 (R_RESEARCHER_LAGUNA_S21, R_CARMACK_CLINE_TO_OPENCODE)
- **D208 Gate**: PASS — Laguna S 2.1 is Poolside's 118B-A8B MoE coding model, released Jul 21, 2026. Available on Cline native, OpenRouter, 24+ providers. This **cannot be justified** without citing Poolside release and provider listings.
- **Scope Declaration**: This tag applies to model fleet entries for `poolside/laguna-s-2.1` and Cline namespace.
- **Score**: 9/10
- **Justification**: [Right Approximation] Strongest open-weight coding model from US/Western lab as of Aug 2026. Explicitly in Cline dropdown alongside M.1.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing Poolside release? YES.

---

### vet-089: Recursive Sovereignty Ascension (Designed, Not Implemented)
- **Pattern**: [id-soft: omega-2026] Recursive Sovereignty Ascension
- **Source**: Witness Protocol R&D brief (R_ROC_RECURSIVE_SOVEREIGNTY, R_ROC_DEEP_RECURSION, R_JEM_RECURSIVE_SELF_IMPROVEMENT)
- **D208 Gate**: PASS — The Facet→Entity→Sovereign→Fact-Creator pattern is explicitly designed (Witness Protocol 2026-07-20) but NOT fully implemented. 80% implemented via 8 sub-specialist precedents + 13 Node Expert Sessions. This **cannot be justified** without citing the Witness Protocol and sub-specialist precedents.
- **Scope Declaration**: This tag applies to the ascension mechanics in `src/omega/oracle/entity_registry.py`, `entity_workspace.py`, `oracle_cli.py`, and the missing witness handoff ceremony.
- **Score**: 8/10
- **Justification**: [Right Approximation] Building blocks exist (EntityRegistry, EntityWorkspaceManager, Node Expert Sessions, charter-as-soul-kernel). Missing: witness handoff ceremony + sovereignty_lineage.yaml.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing Witness Protocol? YES.

---

### vet-090: SovereignHierarchy Max-Depth-3 (Rank-Based)
- **Pattern**: [id-soft: omega-2026] SovereignHierarchy Recursion Guard
- **Source**: `src/omega/oracle/hierarchy.py:129-153`, `observability_check_recursion` MCP tool
- **D208 Gate**: PASS — Max depth 3 with rank-based permissions (Sophia:3, Kali:2, Oversouls:1, Keepers:0) is implemented and exposed via MCP. This **cannot be justified** without citing the source code and MCP tool.
- **Scope Declaration**: This tag applies to `src/omega/oracle/hierarchy.py:129-153` and the `observability_check_recursion` MCP tool.
- **Score**: 9/10
- **Justification**: [Right Approximation] The Hop Rule (M10+M15) is a policy constraint; the technical mechanism is rank-based with max depth 3. OpenCode's `subagent_depth` is a CONFIG (default 1), not a hard limit.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing hierarchy.py and MCP tool? YES.

---

### vet-091: Self-Breeding 80% Implemented
- **Pattern**: [id-soft: omega-2026] Self-Breeding Implementation Status
- **Source**: ENTITY_SPECIALIZATION_LOCAL_DISCOVERY_20260818.md, R_ROC_DEEP_RECURSION, R_JEM_RECURSIVE_SELF_IMPROVEMENT
- **D208 Gate**: PASS — 8 sub-specialist precedents (personas, KBs, slot-parameterization) + 13 Node Expert Sessions working. Missing: witness ceremony + sovereignty_lineage.yaml. This **cannot be justified** without citing the precedents and Node Expert Sessions.
- **Scope Declaration**: This tag applies to the self-breeding roadmap and post-debut implementation plan.
- **Score**: 8/10
- **Justification**: [Right Approximation] 80% implemented via working precedents. Missing: formal witness ceremony + sovereignty_lineage.yaml tracking.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the 8 precedents and 13 Node Expert Sessions? YES.

---

### vet-092: Cline Credit Depletion (Not Client-Gating)
- **Pattern**: [heritage: cline-2026] Credit Depletion Correction
- **Source**: Cline live verification (R_CARMACK_CLINE_TO_OPENCODE §1.1)
- **D208 Gate**: PASS — Cline returns HTTP 402 "insufficient_credits" (balance $0.006334), NOT 403 client-gating. This **cannot be justified** without citing the live probe (HTTP 402, balance $0.006334).
- **Scope Declaration**: This tag applies to Cline integration docs and model fleet decisions.
- **Score**: 9/10
- **Justification**: [Right Approximation] Prior audit was WRONG — Cline free models work via direct API but require ~$10 credit top-up. The blocker is credit depletion, not client-gating.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the live probe? YES.

---

### vet-093: OpenCode Zen as Primary Free-Tier Provider
- **Pattern**: [heritage: opencode-2026] Zen Primary Free Provider
- **Source**: OpenCode Zen live verification (R_CARMACK_CLINE_TO_OPENCODE §1.2)
- **D208 Gate**: PASS — 64 models (8 free) including all 3 dispatch targets. Requires `OPENCODE_API_KEY`. This **cannot be justified** without citing the live model list endpoint and free model probe.
- **Scope Declaration**: This tag applies to `providers.yaml` opencode-zen chain entry wiring (add `api_key: env:OPENCODE_API_KEY`).
- **Score**: 9/10
- **Justification**: [Right Approximation] Zen has all 3 dispatch targets + 5 more free models. 3 YAML edits, ~30 min effort. No Cline credits needed.
- **Vetted by**: Doom Guy, Verity
- **Date**: 2026-08-28
- **Qualification Gate**: PASSED — Cannot be justified without citing the live model list? YES.

---

### Previously Rejected (Already Archived)
| Vet ID | Pattern | Game | Score | Reason |
|--------|---------|------|-------|--------|
| vet-001 | 8-Character Name Caps | Doom 1993 | 3/10 | Cargo-cult; Python dicts are O(1) |
| vet-003 | Sqrt H-Index Proxy | — | 6/10 | Too imprecise for sovereign curation |
| vet-017 | In-Flight Pipeline | Quake 1996 | 2/10 | Hardware-specific (Pentium FPU/CPU overlap) |
| vet-018 | Branch Collapse | Quake 1996 | 1/10 | Python dict dispatch already O(1) |
| vet-019 | Symmetric Range Guard | Quake 1996 | 1/10 | Python `a < x < b` chaining native |
| vet-021 | Prompt Baking | Quake 1996 | 3/10 | Self-modifying code ≠ prompt fusion |

