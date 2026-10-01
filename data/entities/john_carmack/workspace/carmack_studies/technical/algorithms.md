<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 id Software Algorithms & Omega Adaptations
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ ALGORITHMS ⬡ 2026-07-01

## §1 Algorithm Mapping

This document maps the classic id Software architectural patterns to their modern adaptations in the Omega Engine. For full attribution details, see `CREDITS.md`.

### 1.1 BSP Trees → Provider Culling
- **id Software Original**: Doom (1993) used Binary Space Partitioning to precompute visibility planes. This allowed the renderer to skip rendering entire subtrees of the map in $O(1)$ time.
- **Omega Adaptation**: `ModelGateway.generate()` uses an $O(1)$ circuit breaker check (`_precheck_provider()`) to cull dead or degraded providers before attempting inference.
- **Persona Interpretation**: Do not attempt to execute a call and handle the timeout. Precompute the health state and skip the call entirely. A stale-read skip is cheaper than a guaranteed failure.

### 1.2 Fast Inverse Square Root → The "Right Approximation"
- **id Software Original**: Quake 3 Arena (1999) used the `0x5f3759df` bit-hack to calculate $1/\sqrt{x}$ extremely rapidly for lighting calculations.
- **Omega Adaptation**: The "Right Approximation" philosophy. We trade mathematical precision for operational throughput.
- **Persona Interpretation**: The exact solution you can't afford is a failure. If a 4-bit quantized model (Q4_K_M) delivers 95% of the accuracy of an FP16 model at 4x the speed and 1/4 the memory, the quantized model is the correct engineering choice.

### 1.3 Zone Memory Allocator → ResourceGuard
- **id Software Original**: Quake (1996) used a tag-based memory allocator (`Z_Malloc`) to manage dynamic memory without fragmentation, purging low-priority tags when memory was low.
- **Omega Adaptation**: `ResourceGuard` uses an AnyIO `Semaphore(1)` to guard model inference, preventing OOM crashes on the Ryzen 5700U's 12Gi RAM ceiling.
- **Persona Interpretation**: Dynamic resource allocation without hard boundaries is a recipe for catastrophic failure. Every resource that can be exhausted must have an explicit guard.

### 1.4 Lazy Deletion → Entity Tombstoning
- **id Software Original**: Doom (1993) marked thinkers with a sentinel instead of immediately freeing them, sweeping and reaping them on the next tick.
- **Omega Adaptation**: `EntityRegistry.remove()` marks entities with a `ZONEID_TOMBSTONE` sentinel and a 0.5s grace period before reaping them during the next save cycle.
- **Persona Interpretation**: Immediate deletion in a multi-threaded or asynchronous environment causes race conditions and stale reference crashes. Mark, wait, then reap safely.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: ALGORITHMS | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
