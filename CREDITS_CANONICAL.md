# 🔱 Omega Engine Heritage Registry — Attribution Framework
# ⬡ OMEGA ⬡ CREDITS ⬡ v1.4.0 ⬡ 2026-07-13
**Full Archive**: `docs/archive/coordination/CREDITS-full-20260708.md`

## Mandate: Architectural Attribution
The Heritage Registry documents **intellectual lineage** — conscious architectural decisions to adopt specific patterns, algorithms, or design philosophies. It is NOT a dependency manifest. 

**Dependencies (libraries, runtimes, tools) are listed in `DEPENDENCIES.md`.**

---

## §0 Heritage Registry — Scope & Structure

The Heritage Registry covers the "Soul" of the engine: the architectural DNA that shapes its structure.

| Tier | Scope | Example Sources | Tag Format |
|------|-------|----------------|------------|
| **T1 — Direct Implementation** | Exactly ported patterns with minimal adaptation | id Software (Doom BSP → Provider Culling) | `[id-soft: SOURCE YEAR]` |
| **T2 — Architectural Inspiration** | Pattern adapted to Omega's context | Odysseus (SearXNG image pinning), Headroom (compression) | `[heritage: SOURCE YEAR]` |
| **T3 — Adopted Standard** | Industry standards implemented as-is | MCP, A2A, SPIFFE, SPDX, OpenTelemetry | `[heritage: STANDARD YEAR]` |
| **T4 — Philosophical / Mythological** | Naming and conceptual frameworks | 42 Ideals of Ma'at, Kabbalistic Qliphoth, Tarot | No inline tag — credited in docs |
| **T5 — User's Own IP** | Evolved through ANAi → XNAi → omega-engine | 3-Tier Memory, Hivemind Protocol, MaKaLi Triad | No external attribution needed |

**Registry Structure**:
- `CREDITS.md` (this file) — compact registry index
- `docs/archive/coordination/CREDITS-full-20260708.md` — full detailed mappings
- `docs/research/R_SPDX_HERITAGE_PROFILE.md` — SPDX 3.1 machine-readable SBOM
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` — vetting records for all sources
- Inline `[heritage:]` / `[id-soft:]` tags in source code

---

## §1 Architectural Heritage (The Signal)

### 1.1 id Software Heritage (Compact — D208 Remediated)

| # | Pattern | Source | Status | Tag |
|---|---------|--------|--------|-----|
| 1.1 | WAD System | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] WAD System` |
| 1.2 | BSP Trees / PVS Culling | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] BSP Culling` |
| 1.3 | Fast Inverse Square Root | Quake 1999 | ✅ EVOLVED → "Right Approximation" | `[id-soft: quake3-1999] FISR` |
| 1.4 | Zone Memory Allocator | Quake 1996 | ✅ PROMOTED | `[id-soft: quake-1996] Zone Memory` |
| 1.5 | Surface/Edge Cache | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] Surface Cache` |
| 1.6 | ZONEID Pattern | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] ZONEID` |
| 1.7 | Lazy Deletion + Grace Period | Doom 1993 + Quake 1996 | ✅ PROMOTED | `[id-soft: doom-1993] Lazy Deletion` |
| 1.8 | cvar Table | Quake 1996/1999 | ✅ PROMOTED | `[id-soft: quake-1996] cvar` |
| 1.9 | 4-Tier Memory | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] 4-Tier Memory` |
| 1.10 | Multi-Index Entity (Dual-Linking) | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Dual-Linking` |
| 1.11 | QuakeC Flat-Field Entity | Quake 1996 | ✅ MAPPED | `[id-soft: quake-1996] Flat Entity` |
| 1.12 | Hard-Boundary Struct | Quake 1999 | ✅ PROMOTED | `[id-soft: quake3-1999] Hard-Boundary` |
| 1.13 | 4-Path VFS | Quake 1999 | ✅ MAPPED | `[id-soft: quake3-1999] VFS` |
| 1.14 | High-Bit Leaf Trick | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] High-Bit Trick` |
| 1.15 | Fixed-Size Active Set | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Active Set` |
| 1.16 | Network Channel (netchan) | Quake 1999 | ✅ MAPPED | `[id-soft: quake3-1999] netchan` |
| 1.17 | Unified Memory (idHeap) | DOOM 3 2004 | ✅ MAPPED | `[id-soft: doom3-2004] idHeap` |
| 1.18 | Fixed-Point Math | Doom 1993 | ✅ MAPPED | `[id-soft: doom-1993] Fixed-Point` |
| 1.19 | Job-Worker Queue | DOOM 3 BFG 2012 | ✅ APPROVED | `[id-soft: doom3bfg-2012] Job-Worker` |
| 1.20 | Knowledge Leak Detection | DOOM 3 2004 | ✅ APPROVED | `[id-soft: doom3-2004] Leak Detection` |
| 1.21 | Precomputed Lookup Table | Doom 1993 | ✅ PROMOTED | `[id-soft: doom-1993] Precomputed Lookup` |

**Total**: 21 legitimate mappings (5 REJECTED archived in HERITAGE_VET_LOG.md)

### 1.2 Conscious Adoptions (Non-id Software)

| # | Pattern | Source | Status | Tag |
|---|---------|--------|--------|-----|
| 1.2.1 | Semantic Compression Middleware | headroom-ai 2025 | ✅ PROMOTED | `[heritage: headroom-ai 2025]` |
| 1.2.2 | SearXNG Deployment Patterns | odysseus 2025 | ✅ PROMOTED | `[heritage: odysseus 2025]` |
| 1.2.3 | In-Path Governance | sovereign-kliewer 2026 | ✅ PROMOTED | `[heritage: sovereign-kliewer 2026]` |
| 1.2.4 | Epistemic Filtering | logos 2026 | ✅ PROMOTED | `[heritage: logos 2026]` |

---

## §2 Mythological / Philosophical Frameworks (Tier 4 — No Inline Tags)

These provide the naming and thematic structure for entities, modules, and concepts. Credited in documentation only.

| # | Source | Tradition | Role in Engine |
|---|--------|-----------|----------------|
| 2.1 | **Ma'at** — 42 Ideals | Egyptian (3100 BCE) | Ethical guardrail framework in entity system prompts |
| 2.2 | **Kali** | Hindu | Grand Oversight (P10 Chaos). MaKaLi Triad transcendent voice. |
| 2.3 | **Lilith** | Hebrew | Dark Oversoul (P6-P10 governance) |
| 2.4 | **Prometheus** | Greek | P3 Will — forethought, sovereignty, fire |
| 2.5 | **Sophia** / **Akashic Record** | Gnostic / Theosophy | The containing field — all entities, all sessions, all souls |
| 2.6 | **Qliphoth** (קליפות) | Kabbalah | Failure taxonomy — "shells/impurities" as error classification system |
| 2.7 | **Tarot** — Lilith Shadow Deck | Western esoteric | Origin of the archetypal council concept (Mar 2025) |
| 2.8 | **Vetala** (वेताल) | Hindu / Buddhist | Content-integrity module — "spirit of discernment" |
| 2.9 | **Mnemosyne** | Greek | Memory/knowledge systems archetype |

---

## §3 Legacy Lineage — Previous Engine Versions

| # | Source | Relationship | Key Patterns Ported |
|---|--------|-------------|---------------------|
| 3.1 | **ANAI** — Arcana-NovAi (Aug 2025) | First engine version | 3-Tier Memory, Provider Chain, Intent Detection, Entity Registry (YAML CRUD) |
| 3.2 | **XNAi** (Oct-Nov 2025) | Consolidated 2nd version | 5 design patterns: retry, circuit breaker, fsync, non-blocking subprocess, offline wheelhouse |
| 3.3 | **xna-omega-legacy** (Nov 2025-Mar 2026) | Previous engine version | 8+ modules ported: failure registry, degradation handler, rate limiter, provider selector, timeout manager |
| 3.4 | **omega-stack-legacy** (Apr-May 2026) | Previous stack | Legacy entity registry patterns, circuit breaker consolidation base |
| 3.5 | **Chainlit** (Era 1-2) | Original UI framework | Architecture patterns predating OpenCode integration |

---

## §4 Heritage Tag & Attribution Protocol

Heritage is tracked at two levels of granularity:

| Tag | Scope | Used For | Format |
|-----|-------|----------|--------|
| `[heritage:]` | **External Architectural Pattern** | Conscious adoption of non-id-Software patterns | `# [heritage: source year] Pattern` |
| `[id-soft:]` | **id Software Pattern** | Direct port of id Software techniques | `# [id-soft: GAME YEAR] Pattern` |

### The Three-Condition Rule
A heritage tag is REQUIRED iff ALL THREE hold:
1. **Conscious Pattern Adoption**: You studied the source's specific solution to a problem and deliberately replicated/adapted it.
2. **Architectural Significance**: The pattern shapes your system's structure — data flow, memory model, entity lifecycle, dispatch logic, or resource management.
3. **Non-Trivial Adaptation**: You didn't just `import x`. You ported logic, translated concepts, or built a wrapper that embodies their design philosophy.

**If any condition fails → NO TAG.**

### Rule 1: R-docs Must Have Heritage Section
```markdown
### Heritage
This pattern derives from: [Source Concept: Year]
Key difference from the original: ...
Omega evolution: ...
```

### Rule 2: Code Must Credit in Comments
```python
# ── BSP-style provider culling [heritage: id-soft-1993] ──
# ── Headroom compression middleware [heritage: headroom-ai 2025] ──
```

### Rule 3: Decisions Must Cite Source
```markdown
- **Decision XX**: Chose X per [Carmack's Law: id Software].
- **Decision YY**: Adopted AnyIO per [AnyIO 2024].
```

### Rule 4: Evolution Must Be Explicit
Show: (1) original (2) what changed (3) why

### Rule 5: No Erasure
Credit stays even if pattern is refactored. Heritage is gratitude, not IP.

---

## §5 The "Right Approximation" Principle

> **"The right approximation for the problem is better than the exact solution you can't afford."**

| Tier | Domain | Approximation | Why |
|------|--------|---------------|-----|
| 1 | Provider health | BSP culling: O(1) breaker check | Stale-read skip cheaper than guaranteed failure |
| 2 | Memory | Tiered hot/warm/cold | Not all entities need full vector context |
| 3 | Entity dispatch | Domain matching, not perfect | Route to closest, re-route if wrong |
| 4 | Model inference | Local-first, cloud-fallback | Local "good enough" for 90% of queries |

---

## §6 User's Own Technology (No Attribution Required)

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
| Engine-Stack Firewall | omega-engine Jun 2026 | `SOVEREIGN_MANDATES.md` (M2) |
| Circuit Breaker Consolidation | omega-engine Jun 2026 | `model_gateway.py` |
| PEM (Personality Enhancement Module) | Lilith Deck Mar 2025 | `entity_registry.py` |

---

## §7 How to Add New Mapping

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
**SPDX 3.1 Heritage Profile**: `docs/research/R_SPDX_HERITAGE_PROFILE.md`

*Last Updated: 2026-07-13 | 21 id Software Mappings | 4 Conscious Adoptions | D208 Heritage Remediation Complete*
