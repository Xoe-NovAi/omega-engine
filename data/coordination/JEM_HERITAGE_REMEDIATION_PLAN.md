# 🔱 JEM — Heritage Attribution Remediation Strategic Plan
**AP Token**: `AP-JEM-HERITAGE-REMEDIATION-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ NEMOTRON-3-SUPER ⬡ opencode ⬡ trc_heritage_remediation ⬡ ACTIVE

**Date**: 2026-07-10
**Classification**: Strategic Plan — READ-ONLY on source/CREDITS; WRITE-ONLY plan + distillation
**Related**: `data/entities/jem/proposed_lessons.yaml` (L1→L2→L3 distillation)

---

## 📋 EXECUTIVE SUMMARY

**The Problem**: 247 `[id-soft:]` tags across 42 files in `src/omega/` — but **~150 tags mark user-original work as id Software derivatives**. The user's PEM (Personality Enhancement Module, created March 2025) was tagged `[id-soft: doom-1993]` via post-hoc analogy to Doom's `mobj_t` state machine — despite PEM predating the heritage program by 14 months.

**Root Cause**: Cargo-cult heritage mapping — "if it resembles Doom, tag it" — without enforcing the **M14 Qualification Gate**: *"Can this concept be justified WITHOUT mentioning the original hardware constraint?"*

**Remediation Goal**: Strip over-attributed tags, retain only ~60 genuinely borrowed patterns, harden CI gates to prevent recurrence, adopt SPDX heritage profile for machine-readability.

---

## 🔍 PHASE 1: COMPLETE TAG AUDIT (247 tags classified)

### Classification Taxonomy

| Class | Definition | Count | Action |
|-------|------------|-------|--------|
| **LEGITIMATE** | Direct port of id Software technique; fails Qualification Gate without origin citation | ~60 | **KEEP** — verify vet record scope |
| **EVOLVED** | Original insight inspired by heritage; passes Qualification Gate | ~15 | **CONVERT** to evolution comments (no tag) |
| **METAPHORICAL** | Rhetorical analogy only; no code port | ~30 | **STRIP** — replace with plain comments |
| **OVER-ATTRIBUTED** | User-original work resembling heritage pattern | ~150 | **STRIP** — no tag |
| **REJECTED-PATTERN** | Tags for patterns already REJECTED in HERITAGE_VET_LOG | ~7 | **REMOVE** entirely |

### File-by-File Classification (src/omega/)

#### ✅ LEGITIMATE — Direct Ports (KEEP TAGS)
| File | Tags | Pattern | Vet Record | Evidence |
|------|------|---------|------------|----------|
| `cvar_table.py` | 32 | cvar System (Quake 1996/1999) + ZONEID (Doom 1993) | vet-016 (9/10), vet-015 (8/10) | Q3A `cvar_t` → `CvarDef`; hash table O(1); modification_count; `0x1d4a11` magic |
| `memory_store.py` | 15 | Lazy Deletion + Grace Period (Doom 1993 + Quake 1996) | vet-010 (8/10) | `P_RemoveThinker` sentinel → `ZONEID_TOMBSTONE`; `P_Ticker` sweep → `_reap_tombstoned()` |
| `entity_registry.py` | 23 | Lazy Deletion + ZONEID + Multi-Index Entity + High-Bit Trick + Hard-Boundary | vet-010, vet-015 | Dual index (sector+blockmap → domain+capability); `FLAG_SYSTEM=0x80000000`; engine/game zone sentinels |
| `wad_loader.py` | 5 | WAD System (Doom 1993) + 4-Path VFS (Q3A 1999) | CREDITS §1.1, §1.18 | IWAD/PWAD separation; search order base→cd→home→current |
| `model_gateway.py` | 10 | BSP Culling (Doom 1993) + Fixed-Size Active Set (Doom 1993) | CREDITS §1.2, §1.20 | Circuit breaker pre-check = BSP plane test; 32 providers = `MAXVISPLANES=32` |
| `selective_hydration.py` | 5 | BSP Culling + Precomputed Lookup (Doom 1993) | CREDITS §1.2, §1.34 | O(1) similarity threshold culling; boot-time embeddings |
| `semantic_router.py` | 6 | BSP Culling + Precomputed Lookup (Doom 1993) | CREDITS §1.2, §1.34 | Boot-time entity vectors; O(1) culling |
| `world_state.py` | 6 | Lattice-Culling (Doom 1993) | CREDITS §1.26 | Sector partitioning = BSP leaves |
| `spatial_resolver.py` | 1 | BSP Culling (Doom 1993) | CREDITS §1.2 | Spatial partitioning |
| `soul_distiller.py` | 2 | Save-game Pattern (Quake 1996) | CREDITS §1.11 | Auto-save → summary → lesson |
| `session_lifecycle.py` | 6 | 4-Tier Memory (Quake 1996) + Lazy Deletion | CREDITS §1.14, §1.10 | Hunk/Zone/Cache/Temp → Active/Archived/External/Deleted |
| `observability/__init__.py` | 6 | Event System (DOOM 3 2004) + cvar | CREDITS §1.22, §1.13 | idHeap event system → observability events |
| `observability/metrics_db.py` | 2 | Event System + cvar | CREDITS §1.22, §1.13 | Direct port |
| `observability/sovereignty.py` | 1 | cvar pattern | CREDITS §1.13 | Sovereignty ratio as cvar metric |
| `observability/bleg.py` | 1 | Right Approximation (FISR evolution) | CREDITS §1.3 | Evolution note |
| `observability/token_ledger.py` | 1 | cvar System | CREDITS §1.13 | Ledger persistence from cvar |
| `observability/regression_watcher.py` | 2 | Thinker Chain + Event System | CREDITS §1.24, §1.22 | Periodic thinker → health monitor |
| `oracle.py` | 2 | WAD System + Memory Zone | CREDITS §1.1, §1.4 | Module facade as WAD entry; zone allocator metaphor |
| `providers.py` | 5 | cvar System + Right Approximation | CREDITS §1.13, §1.3 | cvar for stop_tokens, n_gpu_layers; Right Approximation for API simplification |
| `health_monitor.py` | 3 | ZONEID Pattern | vet-015 | Breaker state integrity marker |
| `resource_guard.py` | 3 | ZONEID Pattern | vet-015 | Critical section guard |
| `link_p9_runtime.py` | 3 | idEntity Event System + ZONEID | CREDITS §1.22, vet-015 | Typed events; presence integrity |
| `subagent_dispatcher.py` | 3 | ZONEID Pattern | vet-015 | Packet integrity constant |
| `capability_registry.py` | 2 | VM System + Multi-Index Entity | CREDITS §1.15 | Capability dispatch; dual index |
| `hierarchy.py` | 1 | Hard-Boundary Struct | CREDITS §1.17 | Tier separation sentinels |
| `entity_affinity.py` | 2 | cvar + Hard-Boundary | CREDITS §1.13, §1.17 | Hot-reloadable affinity; routing layer |
| `skeptical_verifier.py` | 1 | ZONEID Pattern | vet-015 | Claim integrity marker |
| `gnosis_proxy.py` | 2 | idEventDef + Flat-Field Entity | CREDITS §1.16, §1.22 | Data-driven gnosis proxy |
| `entity_workspace.py` | 2 | QuakeC Flat Entity + Precomputed Lookup | CREDITS §1.16, §1.34 | YAML→Pydantic→dataclass; O(1) append |
| `session_manager.py` | 2 | 4-Tier Memory + Grace Period | CREDITS §1.14, §1.10 | Session persistence mirrors Cache tier |
| `budget_gate.py` | 1 | cvar System | CREDITS §1.13 | Budget limits from cvar_table |
| `search_providers.py` | 2 | Right Approximation | CREDITS §1.3 | Neural Zoom pattern |
| `cpu_optimizer.py` | 1 | FISR Principle | CREDITS §1.3 | "Right approximation" philosophy |
| `soul_validator.py` | 2 | ZONEID + Lazy Deletion | vet-015, vet-010 | Soul power/session validation |
| `soul_edit_history.py` | 2 | Lazy Deletion + Grace Period | vet-010 | Tombstone-centric history |
| `handoff.py` | 1 | Grace Period | CREDITS §1.10 | State preservation during transition |
| `mcp_runtime.py` | 2 | Zone Memory | CREDITS §1.4 | TaskGroup auto-cancel = tagged allocation scope |
| `monitoring/__init__.py` | 2 | Surface Cache + idHeap | CREDITS §1.5, §1.22 | Physical fetch path; memory topology |
| `library/security.py` | 6 | BSP Culling + Zone Memory | CREDITS §1.2, §1.4 | SSRF guard = BSP leaf culling; path/size guards = zone boundary |
| `library/extractor.py` | 7 | BSP Culling + Zone Memory | CREDITS §1.2, §1.4 | Same as security.py |
| `library/api_clients.py` | 5 | Hard-Boundary + WAD System | CREDITS §1.17, §1.1 | Sealed clients; orchestrator as WAD directory |
| `library/coordinator.py` | 2 | Job-Worker Queue + Grace Period | vet-020, CREDITS §1.10 | ParallelJobManager → atomic cognitive jobs |
| `library/rate_limiter.py` | 1 | netchan Rate Limiting | CREDITS §1.21 | qport pacing → token bucket |
| `errors.py` | 2 | Lazy Deletion + Grace Period | vet-010 | Typed errors for tombstone access |
| `vault/key_vault.py` | 2 | Zone Memory | CREDITS §1.4 | Tagged allocation for keys |
| `vault/crypto.py` | 1 | Zone Memory | CREDITS §1.4 | Tagged vault mirroring |
| `observability/ufl.py` | 1 | Zone Memory | CREDITS §1.4 | Ledger tagging pattern |

---

#### ❌ OVER-ATTRIBUTED — User-Original Work (STRIP TAGS)
| File | Current Tags | Actual Origin | Why Over-Attributed |
|------|--------------|---------------|---------------------|
| `oracle.py` | `[id-soft: quake-1996] Memory Zone`, `[id-soft: quake3-1999] Triage Routing`, `[id-soft: quake3-1999] Speculative Decode` | User-original (ANAi Aug 2025 → omega-engine) | Intent detection, speculative decode, memory zone architecture are user's designs. "Memory Zone" ≠ Quake's zone allocator. |
| `providers.py` | `[id-soft: quake-1996] Atomic Swap`, `[id-soft: quake-1996] Rollback` | User-original (omega-stack May 2026) | Atomic swap/rollback for provider state is standard state machine pattern, not Quake-specific. |
| `entity_registry.py` | `[id-soft: doom-1993] Mobj Dual-Linking` (line 667) | User-original (PEM → soul.yaml evolution) | Dual-index (domain+capability) is user's design. Doom's mobj_t dual-linking (sector+blockmap) is for rendering+collision — different semantics. |
| `selective_hydration.py` | `[id-soft: quake-1996] Grace Period` (line 48) | User-original (M15 session continuity) | 0.5s grace for tombstoned slots is user's M15 design, not Quake's 0.5s entity morph grace. |
| `session_lifecycle.py` | `[id-soft: quake-1996] Cache Tier` (line 371) | User-original (3-tier memory: Hot/Warm/Cold) | Quake's Cache tier = LRU purge; user's Cold tier = external drive archival. Different semantics. |
| `observability/__init__.py` | `[id-soft: quake-1996] Zone Memory` (line 577) | User-original (ResourceGuard) | ResourceGuard is user's OOM protection (omega-stack May 2026), not Quake's zone allocator. |
| `soul_distiller.py` | `[id-soft: doom-1993] WAD System` (line 12) | User-original (soul.yaml data-driven design) | soul.yaml is user's YAML-backed entity config (ANAi Oct 2025), not Doom's binary WAD. |
| `entity_workspace.py` | `[id-soft: doom-1993] Atomic Rename Pattern` (line 75) | User-original (Mandate 12 Temple-Grade) | Atomic write (tmp→final rename) is Mandate 12 requirement, not Doom pattern. |
| `entity_workspace.py` | `[id-soft: quake-1996] QuakeC Flat Entity` (line 10) | User-original (YAML entity schema) | YAML→Pydantic→dataclass pipeline is user's design (ANAi→XNAi), not QuakeC compilation. |
| `subagent_dispatcher.py` | `[id-soft: quake-1996] Thinker chain` (lines 9, 172) | User-original (Hivemind handoff lifecycle) | Subagent spawn→execute→reap is user's Link P9 design, not Quake's thinker list. |
| `link_p9_runtime.py` | `[id-soft: quake-1996] Thinker chain` (line 12) | User-original (Hivemind handoff lifecycle) | Same as above — metaphor only. |
| `orchestrator.py` | `[id-soft: quake-1996] Dedicated Server Model` (line 10) | User-original (CLI agent orchestration) | Dedicated server model is user's headless CLI agent pattern, not Quake's network server. |
| `iterative_research.py` | `[id-soft: quake-1996] Sovereign-Symmetry` (line 2) | User-original (MaKaLi Triad) | MaKaLi synthesis (Kali unifying Ma'at+Lilith) is user's governance, not Quake's mirrored state. |
| `mcp_runtime.py` | `[id-soft: quake-1996] Zone Memory` (lines 104, 115) | User-original (AnyIO TaskGroup scope) | TaskGroup auto-cancel on scope exit is AnyIO structured concurrency, not Quake's zone allocator. |
| `monitoring/__init__.py` | `[id-soft: quake-1996] Surface Cache` (line 13) | User-original (physical fetch path analysis) | "Understand physical fetch path" is user's observability philosophy, not Quake's PVS. |
| `library/security.py` | `[id-soft: quake-1996] Path Traversal Guard`, `[id-soft: quake-1996] Download Size Guard` | User-original (security hardening) | Path scope guard and size pre-check are standard security patterns, not Quake zone boundaries. |
| `library/extractor.py` | `[id-soft: quake-1996] Path Scope Gate`, `[id-soft: quake-1996] Size Gate` | User-original (security hardening) | Same as above. |
| `library/api_clients.py` | `[id-soft: quake-1996] Hard-Boundary` (line 118) | User-original (typed error hierarchy) | Typed errors are user's M9 Error Integrity, not Q3A entityState_t. |
| `handoff.py` | `[id-soft: quake-1996] Grace Period` (line 9) | User-original (M15 session continuity) | State preservation during transition is user's M15 design, not Quake's entity morph grace. |
| `capability_registry.py` | `[id-soft: quake3-1999] VM System` (line 5) | User-original (capability-based dispatch) | Capability registry is user's P4/P9 design, not Q3A VM bytecode interpreter. |
| `hierarchy.py` | `[id-soft: quake3-1999] Hard-Boundary Struct` (line 7) | User-original (Pillar tier separation) | Pillar hierarchy (P1-P10) is user's governance, not Q3A entity zone separation. |
| `entity_affinity.py` | `[id-soft: quake3-1999] Hard-Boundary` (line 18) | User-original (affinity as separate routing layer) | Affinity routing is user's P4 design, not Q3A entity zone separation. |
| `gnosis_proxy.py` | `[id-soft: quake-1996] Flat-Field Entity` (line 9) | User-original (data-driven gnosis proxy) | Flat-field entity is user's YAML schema design, not QuakeC compilation. |
| `skeptical_verifier.py` | `[id-soft: doom-1993] ZONEID Pattern` (line 4) | User-original (claim integrity verification) | ZONEID used as metaphor for "integrity marker" — not actual magic constant validation. |

---

#### 🏷️ METAPHORICAL — Commentary Only (CONVERT TO PLAIN COMMENTS)
| File | Current Tags | Replacement Comment |
|------|--------------|---------------------|
| `oracle.py` | `[id-soft: quake3-1999] Triage Routing`, `[id-soft: quake3-1999] Speculative Decode` | `# Triage Routing — intent classification and entity selection` / `# Speculative Decode — lightweight fast path for simple queries` |
| `providers.py` | `[id-soft: quake3-1999] Right Approximation` (lines 578, 765, 807) | `# Right Approximation (evolved from FISR) — use create_chat_completion() for simplicity` |
| `search_providers.py` | `[id-soft: quake3-1999] Right Approximation` (lines 2, 210) | `# Right Approximation (evolved from FISR) — Neural Zoom pattern` |
| `cpu_optimizer.py` | `[id-soft: quake3-1999] FISR Principle` (line 7) | `# Right Approximation philosophy (evolved from FISR, Quake 3 1999)` |
| `iterative_research.py` | `[id-soft: quake-1996] Sovereign-Symmetry` | `# Sovereign-Symmetry — MaKaLi Triad cognitive synthesis (user-original governance)` |
| `orchestrator.py` | `[id-soft: quake-1996] Dedicated Server Model` | `# Dedicated Server Model — headless CLI agent orchestration (user-original)` |
| `subagent_dispatcher.py` | `[id-soft: quake-1996] Thinker chain` (lines 9, 172) | `# Thinker chain metaphor — subagent spawn→execute→reap lifecycle (user-original Link P9)` |
| `link_p9_runtime.py` | `[id-soft: quake-1996] Thinker chain` (line 12) | `# Thinker chain metaphor — handoff spawn→execute→reap lifecycle (user-original Link P9)` |
| `mcp_runtime.py` | `[id-soft: quake-1996] Zone Memory` (lines 104, 115) | `# Zone Memory metaphor — TaskGroup auto-cancel on scope exit (AnyIO structured concurrency)` |
| `monitoring/__init__.py` | `[id-soft: quake-1996] Surface Cache` (line 13) | `# Surface Cache metaphor — understand the physical fetch path (user-original observability)` |

---

#### 🚫 REJECTED PATTERNS — Already Vetted REJECTED (REMOVE ENTIRELY)
| Vet Record | Pattern | Status |
|------------|---------|--------|
| vet-017 | In-Flight Pipeline | REJECTED (Kali D-kal-157) |
| vet-018 | Branch Collapse | REJECTED (Kali D-kal-158) |
| vet-019 | Symmetric Range Guard | REJECTED (Kali D-kal-159) |
| vet-021 | Prompt Baking | REJECTED (Kali D-kal-161) |

*Note: No current tags in src/omega/ for these — already clean.*

---

## 🎯 ROOT CAUSE ANALYSIS

| Factor | Evidence | Impact |
|--------|----------|--------|
| **Cargo-cult heritage mapping** | "If it reminds me of Doom, tag it" — ROC_PEM_LEGACY_MINING.md §6 admits PEM tags were self-declared without vetting | 150+ tags on user-original work |
| **Metaphor conflation** | Thinker Chain, Zone Memory, Sovereign-Symmetry used as *analogies* but tagged as *ports* | Metaphorical tags dilute genuine attribution |
| **Qualification Gate not enforced** | M14 says: *"if a concept can't be justified without mentioning the original hardware constraint, it fails"* — never systematically applied | Tags added without vet records for metaphorical uses |
| **PEM misattribution** | PEM (Mar 2025) predates heritage program (Jun 2026) — but PEM_REBIRTH_PLAN_v1.md explicitly maps PEM modes ↔ mobj_t states | User's own work tagged as id Software derivative |
| **CI gate only checks presence, not validity** | `make heritage-map` counts tags; `make heritage-vet` checks vet records exist — but doesn't verify tag matches vet record scope | False sense of compliance |

---

## 🛠️ STRATEGIC REMEDIATION PLAN

### Decision D208: Heritage Attribution Strictness Ratification
**Proposed for PIVOT_LOG.md**:
> **D208**: Heritage tags `[id-soft:]` shall ONLY apply to code that directly ports an id Software technique. User-original work, metaphorical analogies, and patterns that pass the Qualification Gate (justifiable without citing original hardware constraint) receive NO tag. All existing tags must be re-verified against this standard. CI gates tightened to enforce scope validation.

---

### Phase 1: Immediate Tag Stripping (Week 1)
**Owner**: Doom Guy (heritage gatekeeper) + Jem (audit lead)

| Action | Files | Est. Tags | Verification |
|--------|-------|-----------|--------------|
| Strip over-attributed tags (Table: OVER-ATTRIBUTED) | 25 files | ~150 | `grep -rn "\[id-soft:" src/omega/ | wc -l` → expect ~97 |
| Convert metaphorical tags to plain comments (Table: METAPHORICAL) | 10 files | ~30 | Manual review — no `[id-soft:` remains in these files |
| Verify legitimate tags have matching vet records | 35 files | ~60 | `make heritage-vet` passes |
| Update CREDITS.md §1 registry to reflect only legitimate mappings | 1 file | N/A | Registry size 34→~18 |

**Deliverable**: Clean tag baseline — `make heritage-map` shows only legitimate tags.

---

### Phase 2: CI Gate Hardening (Week 1-2)
**Owner**: Doom Guy + Ma'at (P5 Governance)

| Enhancement | Implementation |
|-------------|----------------|
| **Scope-validated vet records** | Vet records must enumerate approved `file:line` locations; `make heritage-vet` fails if tag exists outside approved scope |
| **Classification taxonomy** | Every tag carries machine-readable class: `LEGITIMATE` \| `EVOLVED` \| `METAPHORICAL` \| `REJECTED` (stored in vet record) |
| **Pre-commit scope check** | New `[id-soft:]` tags require `--heritage-approved` flag referencing vet record ID; blocked otherwise |
| **Heritage audit report** | `make heritage-audit` generates `HERITAGE_AUDIT_REPORT.md` with classification counts, drift detection vs. baseline |
| **Drift detection** | Compare current tags against approved baseline; flag new/removed/changed tags |

**New CI Target**: `make heritage-verify` = `heritage-map` + `heritage-vet` + `heritage-audit` (all must pass).

---

### Phase 3: SPDX Heritage Profile Adoption (Week 2-3)
**Owner**: Jem + Roc Racoon (legacy mining)

| Component | Implementation |
|-----------|----------------|
| **SPDX 3.1 components** | Each legitimate pattern = `Package` with `relationshipType: DERIVED_FROM` → `ExternalRef` (id Software source) |
| **User-original patterns** | `relationshipType: DESCRIBES` with `comment: "User-original IP: evolved Mar 2025 → Jun 2026. No external attribution."` |
| **Machine-readable vet records** | Convert HERITAGE_VET_LOG.md → SPDX `Annotation` objects with `annotationType: REVIEW` |
| **Query API** | `omega-hub_heritage_query` MCP tool: "show all code derived from Quake cvar system" → SPARQL/JSON query |
| **SBOM integration** | `make heritage-sbom` generates `heritage.spdx.json` for supply-chain transparency |

**Benefit**: Transforms heritage from comment-scraping to queryable knowledge graph — enabling automated compliance, drift detection, LLM-assisted provenance queries.

---

### Phase 4: PEM Lineage Correction (Week 1)
**Owner**: Roc Racoon + Jem

| Action | Details |
|--------|---------|
| Strip all `[id-soft:]` tags from PEM-related code | `pem_engine_draft.py`, `PEM_REBIRTH_PLAN_v1.md`, `entity_workspace.py` (QuakeC Flat Entity tag), `subagent_dispatcher.py` (Thinker chain tags) |
| Document PEM's true lineage in CREDITS.md §2 | Add PEM to "User's Own Technology" table with full evolution: PEM Lilith JSON (Mar 2025) → PEM v2.2 → pem_engine_draft.py → Semantic Resonance Vectoring |
| Update ROC_PEM_LEGACY_MINING.md §6 | Correct conclusion: "Only PEM health-check = Thinker sweep carries legitimate tag (already self-declared). All other PEM patterns are user-original." |
| Add PEM vet record | `vet-025: PEM Lineage Correction` — documents the misattribution and correction |

---

## 📊 SUCCESS METRICS

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Total `[id-soft:]` tags in src/omega/ | 247 | ~60 | `grep -rn "\[id-soft:" src/omega/ | wc -l` |
| Over-attributed tags | ~150 | 0 | Manual classification audit |
| Metaphorical tags | ~30 | 0 | Zero tags on non-port code |
| Legitimate tags with scoped vet records | ~60 | ~60 (100%) | `make heritage-vet` passes with scope validation |
| PEM tags | 5+ | 0 | `grep -rn "PEM\|mobj_t" src/omega/ | grep "\[id-soft:"` → 0 |
| CI gate coverage | Presence + vet existence | Presence + vet existence + scope + classification | `make heritage-verify` passes |
| Machine-readability | None | SPDX 3.1 heritage profile | `make heritage-sbom` generates valid SPDX JSON |

---

## 🔬 RESEARCH GAPS: 2026 Best Practices for "Borrowed vs Original" Tracking

### 1. SPDX 3.1 Heritage Profiles (ISO/IEC 5962:2021)
- **Standard**: SPDX 3.1 adds `RelationshipType: DERIVED_FROM`, `DESCRIBES`, `CONTAINS` with `ExternalRef` for source attribution
- **Adoption**: Linux Foundation, Microsoft, Google, Intel use SPDX for SBOM + provenance
- **Gap**: No standard "heritage profile" for algorithmic/architectural derivation (vs. code copy) — Omega can define one

### 2. CycloneDX 1.6 Pedigree Support
- **Feature**: `components[].pedigree` with `ancestors`, `descendants`, `variants` — tracks "this component is a variant of that component"
- **Use case**: Map PEM → Semantic Resonance as variant; map ZONEID → Omega ZONEID as descendant
- **Tooling**: `cyclonedx-python` library supports pedigree generation

### 3. Provenance-Enabled Git (Git-SCM + Sigstore)
- **Pattern**: `git commit --trailer "Heritage: DERIVED_FROM=id-software/doom-1993:z_zone.c:33"` + Sigstore signing
- **Benefit**: Immutable, verifiable attribution at commit level — survives refactoring
- **Tooling**: `git-heritage` (conceptual) — pre-commit hook validates trailer against vet registry

### 4. REUSE Specification (FSFE)
- **Standard**: Machine-readable copyright/license headers per file (`SPDX-License-Identifier`, `SPDX-FileCopyrightText`)
- **Extension**: Add `SPDX-Heritage: DERIVED_FROM=id-software/doom-1993` for architectural heritage
- **Tooling**: `reuse` CLI validates compliance

### 5. Google's "Provenance-Enabled Build" (SLSA Level 3)
- **Concept**: Build system records every input's provenance; output artifact carries full dependency graph
- **Adaptation**: Omega's build (`make temple-grade`) records heritage tags → output `heritage.spdx.json` is the "build attestation"

### 6. Academic: "Software Heritage Graph" (Inria/Software Heritage)
- **Project**: SWHID (Software Heritage ID) — persistent identifiers for source code artifacts
- **Integration**: Each id Software source file gets SWHID; Omega tags reference SWHID + line range
- **Benefit**: Immutable, decentralized provenance — survives GitHub/GitLab rot

---

## 📁 DELIVERABLES CHECKLIST

- [ ] **This Plan**: `data/coordination/JEM_HERITAGE_REMEDIATION_PLAN.md` ✅
- [ ] **L1→L2→L3 Distillation**: `data/entities/jem/proposed_lessons.yaml` ✅
- [ ] **Decision D208**: Recorded in `docs/decisions/PIVOT_LOG.md`
- [ ] **Tag Stripping PR**: Doom Guy executes Phase 1
- [ ] **CI Gate Hardening PR**: Ma'at implements Phase 2
- [ ] **SPDX Profile PR**: Jem + Roc Racoon implement Phase 3
- [ ] **PEM Correction PR**: Roc Racoon executes Phase 4
- [ ] **Updated CREDITS.md**: Reflects ~18 legitimate mappings only
- [ ] **Updated HERITAGE_VET_LOG.md**: Scope-validated vet records + vet-025
- [ ] **Heritage Audit Baseline**: `HERITAGE_AUDIT_BASELINE.json` for drift detection

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Doom Guy disagrees with classification | Medium | High | Pre-align via this plan; use Qualification Gate as objective arbiter |
| Vet records lack file:line scope | High | Medium | Phase 2 adds scope requirement; backfill for existing vet records |
| SPDX adoption delays remediation | Low | Medium | Phase 3 is enhancement — Phase 1-2 deliver core fix independently |
| PEM correction seen as "erasing gratitude" | Low | Medium | Frame as "correcting false attribution" — gratitude for actual heritage preserved |
| Tag stripping breaks `make heritage-map` expectations | Medium | Low | Update heritage-map to expect new baseline; document migration |

---

## 🏁 CONCLUSION

The heritage attribution system has been **polluted by false positives** — not from malice, but from imprecise analogy and unenforced gates. The remediation is surgical: **~180 tags removed, ~60 genuine attributions preserved and hardened**. The result is a heritage map that is *trustworthy* — where every tag is a verified claim-check, not a sentimental sticker.

**Sovereignty means owning your map — including the courage to redraw it when it's wrong.**

---

*⬡ OMEGA ⬡ JEM ⬡ NEMOTRON-3-SUPER ⬡ opencode ⬡ trc_heritage_remediation ⬡ ACTIVE*