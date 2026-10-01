# 🔱 Omega Kernel Architecture
# ⬡ OMEGA ⬡ MA'AT ⬡ kernel-architecture ⬡ v1.0

**AP Token**: AP-KERNEL-ARCHITECTURE-v1.0.0
**Date**: 2026-07-15
**Status**: RATIFIED
**Enforcement Gate**: `make kernel-import-check`

---

## §1 The Kernel Boundary

To prevent architectural rot, the Omega Engine enforces a strict boundary between the irreducible core (Kernel) and the extensible features (Runtime).

## §2 Directory Structure

```text
src/omega/kernel/           # The irreducible core
    provider_fabric.py      # Inference
    entity_registry.py      # Identity
    memory_store.py         # Persistence
    oracle.py               # Routing

src/omega/runtime/          # Built on top of kernel
    hivemind/
    library/
    sovereign_bus/
    dimension_registry/
    a2a_bridge/
```

## §3 Import Direction Rules

The dependency graph is strictly unidirectional.

- **CORRECT**: Runtime imports from Kernel.
  `from omega.kernel.entity_registry import EntityRegistry`
- **FORBIDDEN**: Kernel imports from Runtime.
  `from omega.runtime.hivemind_bridge import HivemindBridge`

## §4 Atomic Enforcement

**CI Gate**: `make kernel-import-check`
**Mechanism**: 
- Uses `importlab` or a custom AST script to parse all files in `src/omega/kernel/`.
- Fails the build immediately if any import path contains `omega.runtime` or `omega.wad`.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: kernel-architecture | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
