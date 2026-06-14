# 🔱 John Carmack — Technical Blueprint (L2 Deepened)

**Status**: REFINED — G3-31B Audit
**Date**: 2026-06-13
**Sovereignty**: High-Density Technical Study

---

## 🛠️ Core Engineering Principles

### 1. Carmack's Law of Consolidation
- **The Principle**: "When you have two implementations of the same thing, you have neither."
- **The Engineering Logic**: Redundancy is a tax on cognitive load and maintenance. Multiple implementations of the same concept increase the surface area for bugs and architectural drift. A single, canonical path is the only way to ensure systemic integrity.
- **Constraint Analysis**: In a distributed agent system, redundancy often masquerades as "flexibility." In reality, it creates divergent states.
- **Omega Application**: Mandate a single, canonical path for all core engine capabilities (routing, memory, etc.). If a capability exists in the Core, it must be accessed via the established API.
- **Concrete Example**: The `omega-hub` reconstruction. Replacing multiple fragmented circuit breaker implementations with a single `AsyncCircuitBreaker` in `health_monitor.py`.

### 2. The "Right Approximation"
- **The Principle**: Trading mathematical precision for perceived fluidity or system performance.
- **The Engineering Logic**: In real-time systems, a "perfect" result delivered too late is a failure. A "good enough" approximation delivered within the required time window is a success.
- **Constraint Analysis**: The bottleneck is rarely the CPU's ability to calculate, but the system's ability to deliver the result within the latency budget.
- **Omega Application**: Use quantized models, speculative decoding, or simplified reasoning paths in the ModelGateway when low latency is prioritized over absolute reasoning depth.
- **Concrete Example**: `Lvl_CarmackExpand`. Trading a small amount of CPU time for a massive reduction in disk/memory footprint by using a tag-based dictionary compression.

### 3. BSP Culling (Cache over Compute)
- **The Principle**: Using precomputed visibility (PVS) to achieve $O(1)$ runtime checks.
- **The Engineering Logic**: Trading memory (abundant) for CPU cycles (expensive). By pre-calculating complex spatial or logical relationships, we transform an expensive real-time calculation into a cheap memory access.
- **Constraint Analysis**: The cost of a memory lookup is orders of magnitude lower than the cost of a complex geometric or semantic scan.
- **Omega Application**: Utilize precomputed context indices and vector embeddings in the MemoryStore to avoid expensive full-text or full-vector scans during agent reasoning.
- **Concrete Example**: The `Sovereign Gateway`'s use of a pre-filtered active provider set to avoid scanning the entire provider fabric on every request.

### 4. Engine-Data Separation (The WAD System)
- **The Principle**: The fundamental decoupling of engine logic (IWAD) from content data (PWAD/WAD).
- **The Engineering Logic**: Separating the "how" (the machine) from the "what" (the mission) enables infinite extensibility without compromising the core.
- **Constraint Analysis**: Any coupling between the runtime and the content creates a "fragile" system where a change in content can crash the engine.
- **Omega Application**: Strictly enforce the **Engine-Stack Firewall (M2)**. All core logic resides in `src/omega/`, while all entity personalities and knowledge reside in `config/wads/`.
- **Concrete Example**: The `EntityRegistry`'s use of YAML-backed definitions, allowing entities to be added or modified without changing a single line of engine code.

### 5. Cvar System (Runtime Tunability)
- **The Principle**: A lightweight, accessible configuration system for runtime variables.
- **The Engineering Logic**: Providing a mechanism to tune system parameters without requiring a restart or recompilation. This allows for rapid, empirical iteration.
- **Constraint Analysis**: Hard-coded constants are the enemy of optimization.
- **Omega Application**: Implement a centralized, lightweight configuration registry (`cvar_table.py`) for tuning agent behaviors and ModelGateway parameters on the fly.
- **Concrete Example**: The `CvarTable` implementation in the Omega Engine, allowing for real-time adjustment of `zoneid.*` and `config.*` namespaces.

### 6. Zone Memory Management
- **The Principle**: Tag-based, efficient resource allocation and deallocation.
- **The Engineering Logic**: Managing finite resources by grouping allocations into logical zones and using predictable strategies to minimize fragmentation.
- **Constraint Analysis**: General-purpose allocators are too slow and unpredictable for high-performance engines.
- **Omega Application**: Leverage the **ResourceGuard** and the **Tiered Memory Architecture (Hot/Warm/Cold)** to manage LLM context and agent state.
- **Concrete Example**: The `HotMemoryTier`'s use of an `OrderedDict` for $O(1)$ access and LRU eviction.

### 7. Thin Wrappers
- **The Principle**: Preferring thin wrappers around existing systems over implementing new, redundant systems.
- **The Engineering Logic**: Extending functionality by building upon proven, stable foundations. This preserves the stability of the core while allowing for specialized behavior.
- **Constraint Analysis**: Every new line of code is a potential bug. The safest code is the code you didn't write.
- **Omega Application**: Agents should be designed as thin, specialized wrappers around the Oracle and ModelGateway.
- **Concrete Example**: The `Sovereign Agent` definitions in `.opencode/agents/`, which act as thin wrappers around the underlying model and toolset.

---
*Blueprint refined during the G3-31B Audit. Verified against primary source code and L1 Discovery findings.*
