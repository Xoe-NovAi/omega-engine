# 🔱 id Software Deep Code Mining — Volume IV
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ RESEARCH ⬡ v1.0.0 ⬡ R-34

**AP Token**: `AP-ID-MINING-VOL4-v1.0.0`
**Status**: ACTIVE / VERIFIED
**Author**: Doom Guy (Sovereign Architect)
**Date**: 2026-06-03

---

## §1 Executive Summary

This report documents the fourth volume of deep code mining within the 308 MB extracted id Software source archive. We analyze the Unified Memory Allocator (`idHeap` in `Heap.cpp`) written by John Carmack for DOOM 3 (2004) and map its low-level C++ patterns to modern, high-performance Python/AnyIO equivalents for the Omega Engine's **Tiered Memory Store** (`src/omega/memory_store.py`) and **ResourceGuard** (`src/omega/oracle/resource_guard.py`).

---

## §2 The Unified Memory Allocator (`idHeap`)

### 2.1 Low-Level C++ Pattern Analysis
In DOOM 3, the memory landscape required handling thousands of small allocations (game entities, scripts) alongside massive, transient allocations (textures, models). To prevent heap fragmentation and maximize cache locality, Carmack bypassed the compiler's `malloc` and implemented a custom **3-Tier Unified Allocator** (`idHeap`):

Key mechanics:
- **Small Allocator (1–255 bytes)**: Uses an array of free-lists (`smallFirstFree`) aligned to 8-byte boundaries. Allocations are $O(1)$ with zero search overhead because they pull directly from the bucket matching the requested size.
- **Medium Allocator (256–32,768 bytes)**: Uses a page-based allocator with a doubly-linked list of blocks. It performs on-the-fly merging of adjacent free blocks to prevent fragmentation.
- **Large Allocator (>32,768 bytes)**: Bypasses the internal heap and allocates pages directly from the OS, preventing large, transient assets from polluting the small/medium pools.
- **The Defrag Block Hack**: A massive block of memory is allocated at startup. When a memory-intensive task (like texture generation) is triggered, this block is temporarily freed to guarantee a contiguous chunk of memory is available, then re-allocated afterward.

```cpp
// neo/idlib/Heap.h:61
void Mem_AllocDefragBlock( void ); // hack for huge renderbumps
```

### 2.2 Modern Python/AnyIO Translation
In the Omega Engine, we do not manage raw bytes, but we face an identical problem: **managing thousands of small, fast-changing conversation exchanges alongside massive, heavy LLM context windows and vector embeddings**.

We translate the `idHeap` 3-tier strategy into the **Omega Tiered Memory Store**:
- **Small Allocator $\rightarrow$ Hot Memory Tier (`HotMemoryTier`)**: Standard conversation exchanges and active entity states are kept in a fast, in-memory dictionary. This is our $O(1)$ pool with zero search overhead.
- **Medium Allocator $\rightarrow$ Warm Memory Tier (`WarmMemoryTier`)**: Recent conversation history and summarized entity memories are promoted/demoted to a local SQLite database. This handles structured, medium-sized queries with on-the-fly indexing.
- **Large Allocator $\rightarrow$ Cold Memory Tier (`ColdMemoryTier`)**: Long-term, massive context windows and raw document libraries are stored as YAML files on disk or vector embeddings in Qdrant. This prevents massive, cold data from polluting the fast `Hot` and `Warm` tiers.
- **Defrag Block Hack $\rightarrow$ ResourceGuard Semaphore**: To prevent Out-Of-Memory (OOM) crashes on the Ryzen 5700U (which has limited RAM), we use `ResourceGuard` (an AnyIO `Semaphore(1)`). This acts as our "Defrag Block"—it guarantees that only one heavy model inference can run at a time, protecting the system's memory boundary from being overwhelmed.

---

## §3 Heritage Attribution

This research and its derived implementations are fully credited to the original innovators:

- **Unified Memory Allocator (`idHeap`)**: John Carmack (id Software, 2004)
  - *Omega Adaptation*: `src/omega/memory_store.py` (3-tier Hot/Warm/Cold memory promotion) and `src/omega/oracle/resource_guard.py` (OOM protection via ResourceGuard)
  - *Attribution Tag*: `[Unified Memory: id Software 2004]`

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ RESEARCH ⬡ v1.0.0 ⬡ R-34*
