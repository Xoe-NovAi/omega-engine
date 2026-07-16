# 🔱 PWAD Capability Lattice
# ⬡ OMEGA ⬡ MA'AT ⬡ pwad-capability-lattice ⬡ v1.0

**AP Token**: AP-PWAD-CAPABILITY-v1.0.0
**Date**: 2026-07-15
**Status**: RATIFIED
**Enforcement Gate**: `make capability-check`

---

## §1 The Active Code Problem

DOOM WADs were passive content (textures, maps). Omega PWADs contain active code (workflows, tools, entities). This requires a strict security boundary to prevent a community PWAD from compromising the core engine or other dimensions.

## §2 The Capability Matrix

Every PWAD must declare its required capabilities in `dimension.yaml`. The `SovereignDimensionValidator` enforces these at runtime.

| Capability | Allowed? | Rationale |
|---|---|---|
| Read own entity memory | Yes | Required for operation |
| Read other PWAD entity memory | No | Strict isolation |
| Call own MCP tools | Yes | Required for operation |
| Call other PWAD MCP tools | Yes (bridged) | Cross-dimension collaboration via SovereignBus |
| Modify own dimension config | Yes | Self-tuning |
| Modify core engine config | No | M2 Firewall protection |
| Access cloud APIs | No (without consent) | M7 Local-First enforcement |
| Modify `soul.yaml` | No | Soul Architecture — user-only writes |
| Read `proposed_lessons.yaml` | No | Blind-write principle |

## §3 SovereignDimensionValidator Schema

```python
class PWADCapabilityLattice(BaseModel):
    network_access: bool = False
    allowed_domains: List[str] = []
    cross_dimension_rpc: bool = False
    fs_write_paths: List[str] = []
    requires_cloud_inference: bool = False
```

## §4 Atomic Enforcement

**CI Gate**: `make capability-check`
**Mechanism**: 
- Statically analyzes PWAD tool source code (AST parsing) to ensure no `os.system`, `subprocess`, or unauthorized `open()` calls exist outside declared `fs_write_paths`.
- Validates all `dimension.yaml` manifests against the `PWADCapabilityLattice` schema.
