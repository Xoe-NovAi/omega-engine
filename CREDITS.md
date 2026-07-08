# 🔱 id Software Architectural Heritage — Attribution Framework
# ⬡ OMEGA ⬡ CREDITS ⬡ v1.1.0 ⬡ 2026-07-08
**Full Archive**: `docs/archive/coordination/CREDITS-full-20260708.md`

## Mandate: Full Attribution Required

Every Omega Engine pattern derived from id Software's innovations MUST credit the original source.
> *"A people that no longer remembers has lost its soul."*

---

## §1 Heritage Registry (Compact)

| # | Pattern | Source | Status | Tag |
|---|---------|--------|--------|-----|
| 1.1 | WAD System | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] WAD System` |
| 1.2 | BSP Trees | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] BSP Culling` |
| 1.3 | Fast Inverse Square Root | Quake 1999 | ✅ EVOLVED → "Right Approximation" | `[id-soft: quake3-1999] FISR` |
| 1.4 | Zone Memory Allocator | Quake 1996 | ✅ PROMOTED | `[id-soft: quake-1996] Zone Memory` |
| 1.5 | Surface/Edge Cache | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] Surface Cache` |
| 1.6 | Worse is Better | Gabriel 1991 | ✅ ADOPTED | `[Worse is Better: Gabriel 1991]` |
| 1.7 | Carmack's Law | id Software | ✅ ADOPTED | `[Carmack's Law: id Software]` |
| 1.8 | Circuit Breaker Consolidation | id Software 2026 | ✅ PROMOTED | `[id-soft: doom-1993] Circuit Breaker` |
| 1.9 | ZONEID Pattern | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] ZONEID` |
| 1.10 | Lazy Deletion + Grace Period | Doom 1993 + Quake 1996 | ✅ PROMOTED | `[id-soft: doom-1993] Lazy Deletion` |
| 1.11 | Heritage Inline Tag Protocol | Omega 2026 | ✅ NEW | `[id-soft: GAME YEAR] Pattern` |
| 1.12 | 8-Char Name Caps | Doom 1993 | ❌ REJECTED | N/A — cargo-cult |
| 1.13 | cvar Table | Quake 1996/1999 | ✅ PROMOTED | `[id-soft: quake-1996] cvar` |
| 1.14 | 4-Tier Memory | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] 4-Tier Memory` |
| 1.15 | Multi-Index Entity | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Dual-Linking` |
| 1.16 | QuakeC Flat-Field Entity | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] Flat Entity` |
| 1.17 | Hard-Boundary Struct | Quake 1999 | ✅ PROMOTED | `[id-soft: quake3-1999] Hard-Boundary` |
| 1.18 | 4-Path VFS | Quake 1999 | ✅ MAPPED | `[id-soft: quake3-1999] VFS` |
| 1.19 | High-Bit Leaf Trick | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] High-Bit Trick` |
| 1.20 | Fixed-Size Active Set | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Active Set` |
| 1.21 | Network Channel (netchan) | Quake 1999 | ✅ MAPPED | `[id-soft: quake3-1999] netchan` |
| 1.22 | Unified Memory (idHeap) | DOOM 3 2004 | ✅ MAPPED | `[id-soft: doom3-2004] idHeap` |
| 1.23 | Fixed-Point Math | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Fixed-Point` |
| 1.24 | Hivemind Message Types | Quake 1999 | ✅ MAPPED | `[id-soft: quake3-1999] netchan` |
| 1.25 | Sovereign-Siloing | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] WAD System` |
| 1.26 | Lattice-Culling | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] BSP Culling` |
| 1.27 | Sovereign-Symmetry | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] cvar` |
| 1.28 | In-Flight Pipeline | Quake 1996 | ❌ REJECTED | N/A — no pipeline overlap |
| 1.29 | Branch Collapse | Quake 1996 | ❌ REJECTED | N/A — Python dict dispatch |
| 1.30 | Symmetric Range Guard | Quake 1996 | ❌ REJECTED | N/A — Python chained compare |
| 1.31 | Job-Worker Queue | DOOM 3 BFG 2012 | ✅ APPROVED | `[id-soft: doom3bfg-2012] Job-Worker` |
| 1.32 | Prompt Baking | Quake 1996 | ❌ REJECTED | N/A — soul.yaml handles this |
| 1.33 | Knowledge Leak Detection | DOOM 3 2004 | ✅ APPROVED | `[id-soft: doom3-2004] Leak Detection` |
| 1.34 | Precomputed Lookup Table | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] Precomputed Lookup` |

**Total**: 34 mapped, 5 REJECTED, 29 active

---

## §2 Attribution Enforcement Rules

### Rule 1: R-docs Must Have Heritage Section
```markdown
### Heritage
This pattern derives from: [id Software Concept: Year]
```

### Rule 2: Code Must Credit in Comments
```python
# ── BSP-style provider culling [BSP Culling: id Software 1993] ──
```

### Rule 2a: Inline `[id-soft:]` Tag Protocol
**Format**: `# [id-soft: GAME YEAR] Pattern Name — why this code exists`

**Game codes**: `doom-1993`, `quake-1996`, `quake2-1997`, `quake3-1999`, `doom3-2004`, `doom3bfg-2012`, `wolf3d-2012`

**Enforcement**: `grep -rn "\[id-soft:" src/omega/` — CI gate via `make heritage-map`

### Rule 3: Decisions Must Cite Source
```markdown
- **Decision XX**: Chose X per [Carmack's Law: id Software].
```

### Rule 4: Evolution Must Be Explicit
Show: (1) original (2) what changed (3) why

### Rule 5: No Erasure
Credit stays even if pattern is refactored. Heritage is gratitude, not IP.

---

## §3 The "Right Approximation" Principle

> **"The right approximation for the problem is better than the exact solution you can't afford."**

| Tier | Domain | Approximation | Why |
|------|--------|---------------|-----|
| 1 | Provider health | BSP culling: O(1) breaker check | Stale-read skip cheaper than guaranteed failure |
| 2 | Memory | Tiered hot/warm/cold | Not all entities need full vector context |
| 3 | Entity dispatch | Domain matching, not perfect | Route to closest, re-route if wrong |
| 4 | Model inference | Local-first, cloud-fallback | Local "good enough" for 90% of queries |

---

## §4 User's Own Technology (No Attribution Required)

These patterns are the user's OWN IP — evolved through ANAi → XNAi → omega-stack → omega-engine:

| Pattern | First Appearance | Current Location |
|---------|-----------------|------------------|
| 3-Tier Memory (Hot/Warm/Cold) | ANAi Aug 2025 | `memory_store.py` |
| Provider Chain (Redis→File→InMemory) | ANAi Sep 2025 | `memory/providers.py` |
| Intent Detection | ANAi Aug 2025 | `oracle.py` |
| Entity Registry (YAML CRUD) | ANAi Oct 2025 | `entity_registry.py` |
| ResourceGuard (OOM protection) | omega-stack May 2026 | `resource_guard.py` |
| MCP Hub (47 tools) | omega-stack May 2026 | `omega_hub/server.py` |
| Hivemind Protocol | omega-engine Jun 2026 | `omega_hub/server.py` |
| Soul Distiller (L1→L2→L3) | omega-engine Jun 2026 | `soul_distiller.py` |
| MaKaLi Triad | omega-engine Jun 2026 | `makali.md` |
| Sovereign Mandates | omega-engine Jun 2026 | `SOVEREIGN_MANDATES.md` |

---

## §5 How to Add New Mapping

```markdown
### N.x [Concept Name] (Game, Year)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | Creator — description | Omega implementation |
| **Core idea** | What it did | What we do |
| **Omega evolution** | How we changed it | Why we changed it |

**Attribution format**: `[Tag: source]`
```

---

**Full detailed tables**: `docs/archive/coordination/CREDITS-full-20260708.md`

*Last Updated: 2026-07-08 | 34 Heritage Mappings | 29 Active Tags*
