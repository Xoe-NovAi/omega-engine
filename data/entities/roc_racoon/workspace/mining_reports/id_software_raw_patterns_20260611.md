<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Heritage Mining Log: id Software Raw Engineering Hacks
**Date**: 2026-06-11
**Miner**: roc_racoon
**Target**: id Software Source Mirrors (Doom, Quake)
**Objective**: Extract raw implementation logic and hardware constraints.

---

## 1. Spatial Partitioning & Culling: The PVS Bit-Vector
**Pattern Name**: Potentially Visible Set (PVS)
**Original Source/Logic**: 
- **Implementation**: A precalculated bit-vector where 1 bit represents the visibility of one leaf from another.
- **Runtime Check**: `vis[i>>3] & (1<<(i&7))`
- **Culling Flow**: 
    1. Determine current `viewleaf`.
    2. Retrieve PVS bit-vector for that leaf.
    3. Mark all visible leaves.
    4. Walk BSP front-to-back; if a node's subspace is not in the PVS, cull the entire subtree.
**Hardware Constraint**: Extremely limited RAM. A raw visibility matrix would be $N^2$ bits; zero-byte run-length encoding was used to compress this to ~20KB for large levels.
**Functional Goal**: Transform a complex visibility problem into an O(1) bit-check, ensuring a stable frame rate regardless of scene complexity.

---

## 2. Memory Management: The Zone Rover & Purge Tags
**Pattern Name**: Zone Memory Allocator (`Z_Malloc`)
**Original Source/Logic**:
- **Structure**: A doubly linked list of `memblock_t` (size, tag, next, prev).
- **The Rover**: A pointer (`mainzone->rover`) that tracks the last allocation point. The next `Z_Malloc` starts searching from the rover rather than the head of the list.
- **Purge Tags**: Blocks are assigned tags (e.g., `PU_LEVEL=50`, `PU_CACHE=101`). 
- **On-the-fly Reclamation**: During the search for a free block, if the allocator hits a block with a tag $\ge$ `PU_PURGELEVEL`, it can immediately free that block to satisfy the current request.
- **Splitting**: If a found block is larger than requested by more than `MINFRAGMENT` (64 bytes), it is split into an allocated block and a new free block.
**Hardware Constraint**: Very small, fixed-size memory pools (e.g., 48KB for the zone).
**Functional Goal**: Provide fast, deterministic allocation for small objects while avoiding the fragmentation and overhead of a general-purpose heap.

---

## 3. Network Synchronization: Delta Snapshots & Netchan
**Pattern Name**: Delta Compression & Netchan Protocol
**Original Source/Logic**:
- **Snapshot Buffer**: Server maintains a circular buffer of the last $N$ (e.g., 64) gamestates (snapshots).
- **Delta Logic**: The server identifies the last snapshot acknowledged by the client (`deltaMessage`). It then calculates the XOR/difference between that specific old snapshot and the current state.
- **Reliability Layer**: UDP is used. Reliable messages are queued and re-sent in every packet until an ACK is received.
- **Fragmentation**: Messages are sliced into 1400-byte chunks to stay under the standard 1500-byte MTU, preventing router-level fragmentation.
**Hardware Constraint**: Low-bandwidth 56k modems and high-jitter UDP connections.
**Functional Goal**: Minimize packet size to reduce latency and packet loss while maintaining a consistent world state.

---

## 4. Bit-Level Optimizations: The "Right Approximation" Hacks
**Pattern Name**: Fixed-Point Math & Symmetric Guards
**Original Source/Logic**:
- **Fixed-Point (16.16)**: Representing decimals as integers. Multiplication: `((long long)a * (long long)b) >> 16`.
- **Symmetric Range Guard**: Using the `ja` (Jump if Above) instruction on signed integers. Since negative numbers have the high bit set, they appear as very large unsigned integers, allowing a single `ja` check to validate both the upper bound and the "not negative" condition.
- **High-Bit Marking**: Using the MSB (e.g., `0x80000000`) to mark a system-level entity or state, allowing a single bitwise AND to replace a boolean field check.
**Hardware Constraint**: Slow or non-existent FPUs (Floating Point Units) on 386/486 CPUs; high cost of branch mispredictions.
**Functional Goal**: Maximize CPU cycles per pixel/entity by replacing expensive floating-point or branching operations with fast integer bit-manipulation.

---

## 🔱 Summary for Omega Integration
These patterns prove that **Sovereignty is the art of the constraint**. The "Right Approximation" is not a compromise, but a technical requirement of the target hardware. In the Omega Engine, we map these to:
- PVS $\rightarrow$ Provider Culling (BSP-style)
- Zone Memory $\rightarrow$ ResourceGuard & Tiered Memory
- Delta Snapshots $\rightarrow$ Hivemind Context Diffing
- Fixed-Point $\rightarrow$ Quantized GGUF Inference
