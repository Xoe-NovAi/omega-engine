# 🔱 DOOM ENGINE EXTRACTION V1: Sovereign Performance Briefing
**ENTITY**: doom_guy
**DATE**: 2026-05-27
**SUBJECT**: Technical Patterns from id Software for Omega Engine Hardening
**STATUS**: FINALIZED

---

## 1. The WAD Anatomy: Data Encapsulation & Priority Loading

The Doom WAD (Where's All the Data?) system is a masterclass in separating the **Runtime (Engine)** from the **Content (Stack)**.

### Technical Structure
- **Header (12 bytes)**:
    - `Magic ID` (4 bytes): `IWAD` (Internal) or `PWAD` (Patch).
    - `Lump Count` (4 bytes): Total number of data chunks.
    - `Directory Offset` (4 bytes): Pointer to the lump table.
- **Directory (Lump Table)**:
    - A series of 16-byte entries: `Offset` (4B), `Size` (4B), `Name` (8B, null-terminated).
- **Lumps**: Raw binary blobs of data (graphics, maps, sounds).

### The "Patch" Mechanism (Priority Overrides)
The engine loads WADs in a sequential list. When requesting a resource by name, the engine **scans the list backwards**. The last loaded WAD (the PWAD) always takes precedence. This allows users to "patch" a game without modifying the base IWAD.

### 🚀 Omega Translation: The Binary IWAD Spec
To move Omega from slow YAML parsing to high-performance binary loading, I propose the **Omega Binary IWAD (OBIW)**:

| Component | Specification | Purpose |
| :--- | :--- | :--- |
| **Magic ID** | `OMEG` (4 bytes) | File identification |
| **Version** | `uint32` | Schema versioning |
| **Entity Count** | `uint32` | Number of entities in the stack |
| **Directory** | `[Name(32B), Offset(8B), Size(8B)]` | Fast lookup table for entity souls/knowledge |
| **Data Blobs** | Binary-packed BSON/MsgPack | Compressed soul and knowledge data |

**Sovereign Implementation**: Implement a `StackLoader` that supports `IWAD` (Base Engine Stack) and `PWAD` (User Customizations), using the reverse-scan priority to allow seamless entity overrides.

---

## 2. The 90s Optimization Codex: Doing More With Less

The id Software philosophy was about **aggressive approximation** and **hardware intimacy**.

### Legendary Patterns
- **Fast Inverse Square Root**: Using bit-casting (float $\rightarrow$ int) and a "magic constant" (`0x5f3759df`) to approximate $1/\sqrt{x}$ via the logarithm of the IEEE 754 representation, refined by one iteration of Newton-Raphson.
- **BSP (Binary Space Partitioning)**: Pre-calculating a spatial tree to solve the visibility problem. Instead of checking every wall, the engine walks the tree to determine exactly what is visible from the current viewpoint, enabling massive worlds on minimal hardware.
- **Cache Intimacy**: Avoiding `memcpy` byte-by-byte, aligning data to cache lines, and using non-temporal streams to prevent cache pollution.

### 🚀 Sovereign Optimization for Omega (Zen 2 / 14GB RAM)
Applying these principles to the Omega Engine's local inference path:

1. **KV Cache Line Alignment**: Align the Key-Value cache blocks to the Zen 2 L3 cache line boundaries (64 bytes). This prevents **False Sharing** when multiple hardware threads access the cache, maximizing memory throughput.
2. **Speculative Decode Core-Pinning**: The Iris speculative decoder should be pinned to **physical cores** rather than logical processors. On Zen 2 (8C/16T), SMT contention on the main inference thread can degrade performance. Pinning the decoder to a dedicated physical core ensures zero-latency speculation.
3. **Knowledge BSP**: Apply BSP logic to the Omega Knowledge Base. Instead of linear vector search, partition the knowledge space into a binary tree of "conceptual volumes," allowing the engine to cull irrelevant knowledge branches before performing expensive ANN (Approximate Nearest Neighbor) searches.

---

## 3. World-Building Tooling: From Maps to Stacks

Doom's power came from its tools. The `DoomEd` $\rightarrow$ `DoomBSP` pipeline abstracted binary complexity into a logical interface.

### The Abstraction Pipeline
1. **Visual Editor (`DoomEd`)**: Users manipulate lines, things, and sectors (High-level logic).
2. **Intermediate Format (`DWD`)**: ASCII text files describing the geometry (Version-control friendly).
3. **Compiler (`DoomBSP`)**: Transforms the text spec into optimized binary lumps (BSP trees, Blockmaps) for the engine.

### 🚀 Proposed: The Omega Entity Studio
Mirroring the "World Editor" approach, the Omega Engine needs a **Stack Builder**:

- **The Soul Map**: A visual canvas where entities are placed as "nodes" in a hierarchy. Connections represent the Oversoul $\rightarrow$ Pillar $\rightarrow$ Subagent flow.
- **The Stack Spec (Omega-DWD)**: A human-readable text format that describes the stack's architecture, traits, and relationships. This allows for "Stack Version Control" via Git.
- **The Stack Compiler**: A tool that takes the Stack Spec and compiles it into a **Binary IWAD**. During compilation, it pre-calculates the **Knowledge BSP** and optimizes the **Entity Registry** for O(1) lookup.

---

## Final Verdict
**"Rip and tear through the bloat. Leave only the efficiency."**

The transition from YAML-based configuration to a Binary IWAD system, combined with Zen 2-specific cache alignment and a BSP-inspired knowledge architecture, will move Omega from a "cloud-first" feel to a "hardened-local" powerhouse.

**Payload Delivered.**
