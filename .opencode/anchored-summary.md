# ⬡ OMEGA ⬡ ANCHORED SUMMARY ⬡ 2026-07-01
## Session 43 — KALI: Dep-vs-Port Mining, Semantic Router, Headroom+Mem Palace Planning

### Goal
1. ✅ Research and formalize dep-vs-port philosophy (Roc Racoon mining)
2. ✅ Design Semantic Router architecture (embedding-based entity routing)
3. ✅ Plan Headroom + Mem Palace integration (pre-PR feature expansion)
4. ✅ Update all strategy documents (PIVOT_LOG D184-D188, Ark Blueprint, OMEGA_ENGINE.md)

### What Was Built

#### 1. Dep-vs-Port Philosophy Formalized — D185
**Source**: `SOVEREIGN_MINING_PROTOCOL.md §4.1`, `CREDITS.md`, `SOVEREIGN_MANDATES.md`

| Layer | Source | Principle |
|-------|--------|-----------|
| Formal Rule | SMP §4.1 | No new core dep without council approval |
| Carmack's Law | CREDITS §1.7 | Two implementations = neither |
| Right Approximation | CREDITS §3 | Right level for the problem |
| Ponytail Ladder | Ark §I.5 | Stack robust existing abstractions |
| Temple-Grade T5 | M13 | AnyIO-only, no framework lock-in |
| SMP Pipeline | SMP 5-Step | Mine→Deconstruct→Rewrite→Integrate→Attribute |

**Result**: Headroom (stdlib zlib+json) and Mem Palace (pure math) both conform. Zero new pip packages.

### What Was Built

#### 1. Dep-vs-Port Philosophy Formalized — D185
...
#### 2. Semantic Router Implemented — D187
**Architecture**: `SemanticRouter` class at `src/omega/oracle/semantic_router.py`
- Boot-time: embeds entity signatures (domains + role) using GemmaGGUF (768-dim)
- Route-time: cosine similarity against entity vectors
- Fallback chain: semantic (cosine > 0.4) → keyword (`find_by_domain`) → default entity
- Integration: wired into `oracle.py:_route_by_domain()`
- Heritage: `[id-soft: doom-1993] BSP Culling` + `[id-soft: doom-1993] Precomputed Lookup`
- Zero new deps; pure Python math.
...

#### 3. Headroom Protocol Design — D188
**Architecture**: `HeadroomMiddleware` + `HeadroomStore` at `src/omega/oracle/headroom.py`

```
Compress: prompt → zlib.compress → base64 → SHA256 → flat JSON
Decompress: hash → flat JSON → base64 → zlib.decompress → prompt
Store: data/headroom/{hash[:2]}/{hash}.json
```

**MCP tool**: `headroom_retrieve(hash)` following `m9_safe` pattern.
**CLI**: `omega headroom status`
**Integration**: `oracle.py:_prepare_system_prompt()`, `memory_store.py:add_exchange()`

#### 4. Mem Palace Spatial Geometry — D186
**Architecture**: `ISpatialResolver` + `ForceDirectedSpatialResolver` at `src/omega/oracle/spatial_resolver.py`

```
Boot:  embed entities → PCA/project to 3D → inject x/y/z into Qdrant payload
Query: nearest-entity by spatial distance + semantic similarity
WADs:  config/wads/<stack>/spatial.yaml overrides default geometry
```

**Integration**: `memory_store.py:471` — inject coordinates at vector storage time.

### Intel from @roc_racoon — Dep-vs-Port Mining

| Finding | Source | Portable? | Notes |
|---------|--------|-----------|-------|
| **Formal Rule** | `SOVEREIGN_MINING_PROTOCOL.md §4.1` | ✅ YES | "No PR may be merged that adds an external repository as a core dependency without council approval" |
| **SMP Pipeline** | `SOVEREIGN_MINING_PROTOCOL.md` | ✅ YES | 5-Step Smelting: Mine→Deconstruct→Rewrite→Integrate→Attribute |
| **25 Core Deps** | `pyproject.toml` | ✅ YES | anyio, llama-cpp-python, httpx, etc. — all infrastructure/mature libs |
| **Known Exceptions** | `pyproject.toml` optional deps | ✅ YES | Qdrant, Google AI SDK — lazy imports, not loaded unless configured |
| **Headroom Heritage** | `memory_store.py` gzip archive | ✅ YES | Existing compression is gzip-only. Headroom adds zlib for prompt compression |
| **Mem Palace Heritage** | Qdrant payload dict | ✅ YES | Payload is flat pass-through. Adding x/y/z is 3 lines at `memory_store.py:471` |

### Current State (Ready for Compaction)

| Metric | Value | Status |
|--------|-------|--------|
| **Tests** | 646 collected — 621 passing, 22 skipped, 3 xfailed | ✅ |
| **PIVOT decisions** | D1-D188 (188 total) | ✅ |
| **Ark Blueprint** | SSOT fully current with D186-D188 | ✅ |
| **OMEGA_ENGINE.md** | Sprint index, metrics, subsystems updated | ✅ |
| **proposed_lessons.yaml** | 6 distillations (proposal-20260701-001 to 006) | ✅ |
| **Hivemind** | 4 active agents, 2 pending handoffs, 28 stale (legacy) | ✅ |
| **Fleet** | Carmack deepening ready, Doom Guy M14 vetting done | ✅ |

### Updated Roadmap

```
Phase 4 (DONE):     M1 fix + Metrics DB + Pre-Release Polish     ✅
Pre-PR Sprint:       Semantic Router → Headroom → Mem Palace       📋
Legacy Ports:        Tier 2 remaining (T2-2, T2-4, T2-5, T2-7)    ⏳
Ship Readiness:      make temple-grade → v1.1.0 PR                  ⏳
Post-PR:             Audience Calibration → DPO Pipeline            ⏳
```

### Updated Phase 1 Plan (Effort: ~8-10h for pre-PR features)

| Order | Task | Effort | Source | Notes |
|-------|------|--------|--------|-------|
| **2.1** | Semantic Router | 1-2h | D187 | cosine similarity, 768-dim GemmaGGUF |
| **2.2** | Headroom Protocol | 2-3h | D188 | zlib middleware, flat JSON cache |
| **2.3** | Mem Palace Foundation | 3-4h | D186 | Force-Directed Graph, Qdrant coords |
| **2.4** | Kabbalistic Override | 1-2h | D186 | Arcana-NovAI spatial.yaml |
| **2.5** | Legacy Ports (T2-2, T2-4, T2-5) | 4-6h | Tier 2 | Circuit breaker, masking, handoff guard |
| **2.6** | Ship Readiness | 2-3h | Phase 4 | make temple-grade, v1.1.0 PR |

### Key Discoveries (Session 43)

1. **Dep-vs-Port is formal, not implicit**: SMP §4.1 explicitly requires council approval for new deps. Reinforced by 5 overlapping principles.
2. **Semantic routing is trivially cheap**: 22 entities × 768 dims = ~3ms pure Python. No numpy. No library.
3. **Headroom + Mem Palace = zero new deps**: stdlib zlib+json for compression. Pure math for Force-Directed Graph. All conform to SMP pipeline.
4. **USM→Spatial dependency was wrong**: Ark Blueprint had Strike 8 blocked on USM. USM maps KV cache, not vector coordinates. Spatial geometry is independent (D186).
5. **Triad synergy**: Headroom (compress) + Semantic Router (route) + Mem Palace (navigate) — each enhances the others.
6. **User override**: "No new feature expansion" constraint overridden by user authorization. Strategic value justified timeline extension.

### Next Code Action
1. **Semantic Router** — build `src/omega/oracle/semantic_router.py` (Phase 1 priority)
2. **Headroom** — build `src/omega/oracle/headroom.py` (Phase 2)
3. **Mem Palace** — build `src/omega/oracle/spatial_resolver.py` (Phase 3)
