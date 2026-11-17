# WAD Enhancement Plan

> **Status:** PROPOSED
> **Date:** 2026-11-17
> **Author:** Node 1 (build)
> **Branch:** `node1/v2-migration` (official repo, private)
> **Source Review:** Deep review of WAD system (wad_loader.py, entity_registry.py, dispatch_registry.py, manifests, tests)

---

## 1. Executive Summary

The Omega Engine WAD (Where's All Data) system is a well-designed IWAD/PWAD architecture inspired by DOOM's WAD format. It supports entity loading, voice registration, hierarchy resolution, world state, and memory adapter registration. However, the deep review identified 20+ weaknesses and opportunities across 7 categories.

This plan prioritizes the most impactful items and organizes them into 4 phases.

---

## 2. Current State

### What works well
- IWAD/PWAD separation with topological sort (DOOM-inspired backward scan)
- Shadow-Stacking entity layers (priority-based override)
- Engine-version compatibility enforcement (semver via packaging)
- Path traversal guards on WAD loading
- File size limits on manifests and entity files
- Extra="forbid" manifest validation (prevents silent typos)
- Entity field type validation and range checks
- Environment override (OMEGA_WADS_DIR) for isolation
- Both OED and ANAi WADs load successfully together (19 entities)

### What needs improvement
- No WAD validation CLI (errors only caught at load time)
- No runtime WAD switching (requires restart)
- dispatch.yaml missing from ANAi WAD
- dispatch_registry cache not WAD-aware
- No WAD unloading mechanism
- Voice loading fragile (no schema validation, missing files)
- Adapter whitelist hardcoded in source
- No WAD development guide or scaffold tool
- Limited test coverage for voice/world/adapter loading
- No hot-reload or WAD composition

---

## 3. Phase Plan

### Phase 1: Critical Fixes (P0) — Immediate

| # | Item | File(s) | Effort | Description |
|---|------|---------|--------|-------------|
| 1.1 | Add dispatch.yaml to ANAi WAD | `config/wads/arcana_novai/entities/dispatch.yaml` | Low | Create dispatch config for ANAi entities (avgn, researcher_humboldt, sophia, etc.) with proper roles, capabilities, and slots |
| 1.2 | dispatch_registry fallback | `src/omega/governance/dispatch_registry.py` | Low | Fall back to IWAD's dispatch.yaml when PWAD doesn't have one |
| 1.3 | dispatch_registry WAD-aware cache | `src/omega/governance/dispatch_registry.py` | Low | Key cache by (iwad_name, mtime) instead of just mtime |
| 1.4 | WAD validation CLI | `scripts/validate_wad.py` (new) | Medium | Pre-load validation: manifest schema, entity files, voice refs, hierarchy, adapters, engine compat |

### Phase 2: Robustness (P1) — Next

| # | Item | File(s) | Effort | Description |
|---|------|---------|--------|-------------|
| 2.1 | Voice schema validation | `src/omega/oracle/wad_loader.py` | Low | Validate voice YAML structure; check referenced files exist; use model_recommendation as default model |
| 2.2 | WAD unloading | `src/omega/oracle/wad_loader.py`, `entity_registry.py` | Medium | Add `unload_wad(stack_name)` that removes entities, voices, and resets hierarchy |
| 2.3 | Hierarchy path validation | `src/omega/oracle/wad_loader.py` | Low | Add path traversal guard and YAML validation for hierarchy files |
| 2.4 | World state validation | `src/omega/oracle/wad_loader.py` | Low | Add size limits and schema validation for world lumps |
| 2.5 | Entity field validation consolidation | `src/omega/oracle/wad_loader.py`, `entity_registry.py` | Medium | Single schema definition using pydantic or jsonschema; consistent type/range validation |
| 2.6 | Batch entity save | `src/omega/oracle/entity_registry.py` | Low | Add `batch_add()` that saves once after all entities loaded |

### Phase 3: Developer Experience (P2) — Soon

| # | Item | File(s) | Effort | Description |
|---|------|---------|--------|-------------|
| 3.1 | WAD development guide | `docs/guides/HOW_TO_CREATE_WAD.md` (new) | Medium | Step-by-step tutorial with examples |
| 3.2 | WAD scaffold command | `scripts/create_wad.py` (new) | Medium | `omega wad create <name>` scaffolds correct structure |
| 3.3 | WAD linting | `scripts/lint_wad.py` (new) | Medium | Automated checks: unknown fields, missing voices, broken hierarchy refs, invalid models |
| 3.4 | Manifest schema doc | `docs/WAD_MANIFEST_SCHEMA.md` (new) | Low | Single reference for all manifest fields |
| 3.5 | Runtime WAD switching API | `src/omega/oracle/wad_loader.py` + MCP | High | `wad_switch(stack_name)` endpoint for hot-switching without restart |

### Phase 4: Advanced (P3) — Future

| # | Item | File(s) | Effort | Description |
|---|------|---------|--------|-------------|
| 4.1 | WAD hot-reload | `src/omega/oracle/wad_loader.py` | High | File watcher for WAD directory changes |
| 4.2 | WAD composition (multi-WAD) | `config/omega.yaml`, `wad_loader.py` | Medium | Load multiple PWADs simultaneously |
| 4.3 | Adapter whitelist config | `config/adapter_whitelist.yaml` (new) | Low | Move whitelist from hardcoded set to config file |
| 4.4 | WAD diffing tool | `scripts/wad_diff.py` (new) | Low | Compare two WADs structurally |
| 4.5 | WAD marketplace/registry | `config/wad_registry.yaml` (new) | High | Discover, install, update WADs |

---

## 4. Testing Plan

### New tests needed

| Test | File | What it covers |
|------|------|----------------|
| WAD validation | `tests/test_wad_validation.py` | Manifest schema, entity files, voice refs, hierarchy |
| Voice loading | `tests/test_wad_voices.py` | Voice schema, missing files, entity creation |
| World state loading | `tests/test_wad_world.py` | VR lump loading, sector iteration, error handling |
| Adapter registration | `tests/test_wad_adapters.py` | Whitelist enforcement, dynamic import, init |
| WAD switching | `tests/test_wad_switching.py` | Load → switch → verify override → restore |
| WAD unloading | `tests/test_wad_unloading.py` | Remove entities, voices, hierarchy reset |
| dispatch_registry | `tests/test_dispatch_registry.py` | WAD-aware cache, fallback, mtime invalidation |

### Existing tests to update

| Test | Change |
|------|--------|
| `test_wad_loader.py` | Add tests for unknown fields → metadata capture |
| `test_wad_auto_loading.py` | Add tests for load_all_wads with mixed IWAD/PWAD |

---

## 5. Recommended Execution Order

### Immediate (this session)
1. **Phase 1.1**: Create dispatch.yaml for ANAi WAD
2. **Phase 1.2**: Add fallback to dispatch_registry
3. **Phase 1.3**: Make dispatch_registry cache WAD-aware
4. **Phase 1.4**: Create validate_wad.py

### Next session
5. **Phase 2.1**: Voice schema validation
6. **Phase 2.2**: WAD unloading
7. **Phase 2.5**: Entity field validation consolidation

### Future sessions
8. **Phase 3**: Developer experience tools
9. **Phase 4**: Advanced features

---

## 6. Success Criteria

- [ ] All WADs (OED + ANAi) pass validation
- [ ] dispatch.yaml exists for all WADs (or fallback works)
- [ ] WAD switching tested end-to-end
- [ ] No hardcoded models in any WAD entity
- [ ] Voice files validated at load time
- [ ] WAD development guide published
- [ ] All new tests pass
- [ ] `make lint && make test && make docs` green

---

## 7. Risks

| Risk | Mitigation |
|------|------------|
| Breaking existing WAD tests | Run full test suite after each change |
| ANAi WAD has rich entity fields that don't fit standard schema | Use metadata capture (already implemented) |
| Adapter whitelist too restrictive for ANAi | Config-based whitelist (Phase 4.3) |
| Performance regression from validation | Batch validation, cache results |

---

## 8. References

- `src/omega/oracle/wad_loader.py` — WAD loader implementation
- `src/omega/oracle/entity_registry.py` — Entity registry with Shadow-Stacking
- `src/omega/governance/dispatch_registry.py` — Dispatch config loader
- `src/omega/governance/config_resolver.py` — Config path resolution
- `docs/governance/WAD_ENGINE_BOUNDARY_FIRST_PRINCIPLES.md` — Engine/WAD boundary
- `docs/tutorials/how-to-create-wad.md` — WAD creation tutorial
- `docs/federation/PERSONA_WAD_ARCHITECTURE.md` — WAD architecture
- `tests/test_wad_loader.py` — WAD loader tests
- `tests/test_wad_auto_loading.py` — WAD auto-loading tests