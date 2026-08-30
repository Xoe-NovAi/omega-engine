<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 John Carmack — Architectural Critique of Omega Engine
**AP Token**: `AP-JOHN_CARMACK-AUDIT-20260711`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_arch_audit ⬡ ACTIVE

**Date**: 2026-07-11
**Scope**: Full architectural audit — where we are, where we've been, where we're going
**Method**: First-principles analysis. Right Approximation check. Bloat detection. Confidence scoring (1-10).

---

## 📋 .plan — WHAT I AM AUDITING

**Current Task**: Full architectural critique of Omega Engine v1.4.0 (CHANGELOG) / v1.0.0 (git tag) / v1.1.0 (Ark Blueprint planned)

**What I Tried**: Read all 5 mandated context files (OMEGA_ENGINE.md, SOVEREIGN_ARK_BLUEPRINT.md, PIVOT_LOG.md, SOVEREIGN_MANDATES.md, CREDITS.md), HERITAGE_VET_LOG.md (74 vet records), ran test suite (1104 passed, 42 skipped, 3 xfailed), ran heritage-vet (121 tags, all vetted), ran sovereignty report (99.6% local), inspected provider fabric, WAD loader, entity registry, model gateway.

**What the Data Shows**: Measured, not speculated. See findings below.

**What I'll Flag Next**: Top 3 fix/stop/start items with confidence scores.

---

## 1️⃣ WHERE WE ARE — Current Architecture Health

### Test Reality
| Metric | Value | Verdict |
|--------|-------|---------|
| Tests | 1104 passed, 42 skipped, 3 xfailed | ✅ **Solid** — 0 failures is rare |
| Temple-Grade | T1-T13 all PASS (heritage-vet prerequisite clean) | ✅ **Enforced** |
| Heritage Vet | 121 `[id-soft:]` tags, 74 vet records, 0 unvetted | ✅ **Gate holding** |
| Sovereignty Ratio | 99.6% local (19,160/19,243 inferences) | ✅ **Exceeds 80% target** |
| Source Files | 168 .py, ~36K lines | ⚠️ **Growing** |

### Mandate Compliance — Measured, Not Claimed

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M1 AnyIO Absolute** | ✅ PASS | 0 `import asyncio` in src/omega/ (only 3 comments referencing asyncio compatibility) |
| **M2 Engine-Stack Firewall** | ⚠️ **LEAKAGE** | See §1.1 below |
| **M7 Local-First** | ✅ REAL | Provider chain: native-gguf(0) → lmster(1) → ollama(2) → antigravity(3) → google(4) → openrouter(4) → opencode-zen(5) → cline(6) → mock(99). `antigravity` marked `is_cloud=False` — **questionable** |
| **M9 Error Integrity** | ✅ PASS | 0 bare `except:` in src/omega/ (verified grep). Typed `OmegaError` hierarchy enforced |
| **M11 Soul Integrity** | ⚠️ **PARTIAL** | L1→L2→L3 pipeline exists (`soul_distiller.py`), but `proposed_lessons.yaml` writes not verified per-session |
| **M13 Temple-Grade** | ✅ PASS | All gates green. T3 coverage ≥80% on core (workers excluded by design) |
| **M14 Heritage Vetting** | ✅ PASS | 121 tags → 74 vet records. D208 remediation: 61% over-attributed tags stripped |
| **M15 Sovereign Continuity** | ❓ **UNVERIFIED** | `session_gnosis.md` files exist in entity workspaces but no automated enforcement |
| **M20 SomaticState** | ✅ IMPLEMENTED | `llama_copy_state_data`/`llama_set_state_data` via `anyio.to_thread.run_sync()` — round-trip tests pass |
| **M21 Gate Integrity** | ✅ PASS | Contract tests for `GenerateResult` dataclass (5 call sites fixed in Sprint C) |
| **M22 Response Provenance** | ✅ WIRED | `GenerateResult.provider_name` captured at receipt, not dispatch intent |
| **M23 Failure Integrity** | ✅ ENFORCED | `[TOOL-CHAIN-COLLAPSE]` pattern documented; no soft-fail synthesis observed |

**Confidence**: 9/10 — Mandates are not theater; they have CI gates and measurable enforcement.

---

### 1.1 Engine-Stack Firewall (M2) — **LEAKAGE DETECTED**

**Finding**: The firewall is **architecturally sound but operationally porous**.

**Evidence**:
1. **WAD Loader** (`wad_loader.py:43-46`) has `ADAPTER_MODULE_WHITELIST` restricting WADs to `omega.memory.adapters.*` — **GOOD**
2. **Entity Registry** (`entity_registry.py`) loads entities from `config/wads/*/entities/` — **GOOD separation**
3. **LEAK 1**: `config/wads/arcana_novai/entities.yaml` defines 10 Pillar Keepers with `slots: ["P1"]` etc. — **WAD content leaking pillar semantics into engine**. The engine's `Entity.slots` field is now a WAD concern, not engine concern.
4. **LEAK 2**: `src/omega/oracle/entity_affinity.py:18` has `[id-soft: quake3-1999] Hard-Boundary` tag on `EntityAffinityResolver` — **engine code tagged with WAD-specific heritage**. This is the engine knowing about WAD lore.
5. **LEAK 3**: `src/omega/iris/matcher.py` references "active IWAD" in user-facing strings — **engine UI leaking WAD terminology**.
6. **LEAK 4**: `src/omega/oracle/wad_loader.py:14` imports `from .world_state import world_state, WorldLump` — **engine singleton `world_state` mutated by WAD loader**. This is shared mutable state crossing the firewall.

**Right Approximation Check**: The firewall exists at the *file system* level (src/omega/ vs config/wads/) but not at the *runtime* level. The `world_state` singleton is the breach.

**Confidence**: 8/10 — Measured by grep and runtime inspection.

---

### 1.2 Local-First (M7) — **REAL BUT `antigravity` CLASSIFICATION IS WRONG**

**Finding**: Provider fabric **is** local-first in practice (99.6% local), but `antigravity` provider at priority 3 is marked `is_cloud=False`.

**Evidence**:
- `config/providers.yaml`: `antigravity` priority 3, `base_url: https://api.antigravity.ai/v1` — **this is a cloud endpoint**
- `ModelGateway._is_cloud_provider_name("antigravity")` returns `False` (hardcoded in `_local_active` set)
- `pii_masker.py:28` treats `antigravity` as local (no PII masking) — **data leakage risk**

**Root Cause**: `antigravity` was added as "first-class provider" (D205) but the cloud/local classification wasn't updated. The `google-genai` SDK is used but the endpoint is external.

**Confidence**: 10/10 — Direct config + code inspection.

---

### 1.3 Hardware Floor (Ryzen 5700U, 12Gi AI RAM) — **MOSTLY IGNORED**

**Finding**: Engine designs for "sovereign hardware" but **does not enforce or validate** against the actual floor.

**Evidence**:
- `cpu_optimizer.py` has `Zen2Optimizer` with AVX2/FMA3 tuning — **GOOD**
- `NativeGGUFProvider` pins threads to cores `[0,2,4,6]` — **GOOD**
- **NO** runtime check that model fits in 12Gi RAM before loading
- **NO** OOM guard that prevents loading 8B+ models when 4B already resident
- `ResourceGuard` uses `cvar` for RAM limit but default is 8GiB — **not calibrated to 12Gi**
- `somatic_state.py` captures full model state — **could be 2-4GiB per snapshot** with no disk quota

**Right Approximation**: On 12Gi RAM, you can run ONE 8B model (Q4_K_M ~4.5GiB) + OS + overhead. Running native-gguf + lmster + ollama simultaneously is **fantasy**. The provider chain assumes sequential fallback, not concurrent residency.

**Confidence**: 9/10 — Hardware constraints are physics; code ignores them.

---

### 1.4 Agent Fleet — **11 AGENTS + 1 PARAMETERIZED = RIGHT SIZE (Cap 14)**

**Finding**: Fleet consolidation (D126: 26→14→11) was **correct**. No bloat.

| Agent | Role | Justification |
|-------|------|---------------|
| `kali` | Grand Oversight | Unifies Ma'at+Lilith, destroys drift |
| `maat` | Light Oversoul (P1-P5) | Build-side governance |
| `lilith` | Dark Oversoul (P6-P10) | Run-side governance |
| `makali` | Parallel Council | Explicit decomposition + synthesis |
| `doom_guy` | Heritage Aspect | id Software pattern authority |
| `roc_racoon` | Legacy Aspect | Archaeology & pattern extraction |
| `researcher` | Sovereign Researcher | Deep research, lattice reasoning |
| `jem` | Sovereign Synthesizer | Query→TaskGraph→Result pipeline |
| `john_carmack` | S3 Consultant | Architectural review & performance |
| `verity` | Unified Steward | Compliance + Gnosis distillation |
| `pillar` | Slot-based domain agent | Parameterized by `--slot PX` |

**MaKaLi Triad**: Not overhead. It's a **forced decomposition pattern** that prevents single-agent hallucination. The "council" cost (3 inferences) is the price of adversarial verification.

**Confidence**: 8/10 — Fleet cap enforced by M10; no vacant slots.

---

### 1.5 Versioning Mess — **SYMPTOM OF MISSING RELEASE DISCIPLINE**

| Source | Version | Reality |
|--------|---------|---------|
| Git tag | `v1.0.0` | Only tag in repo |
| CHANGELOG.md | `v1.4.0` (2026-07-07) | Latest documented release |
| Ark Blueprint | `v1.1.0` planned | "Tag when user ready" |
| OMEGA_ENGINE.md | `v1.1.0` | SSOT claims v1.1.0 |

**Root Cause**: No automated release pipeline. `make tag` doesn't exist. Version bump is manual, CHANGELOG is manual, git tag is manual. Three separate manual steps → drift.

**Confidence**: 10/10 — Trivial to verify.

---

## 2️⃣ WHERE WE'VE BEEN — Key Architectural Decisions

### 2.1 Pivot Log Analysis (211 Decisions D1-D211)

**Pattern**: Decisions cluster in **sprints** (Phase 0, MV-IW, Bedrock, Sovereign Hardening, Sessions 52-60). Each sprint fixes the previous sprint's debt.

**Critical Decisions**:
| Decision | Impact | Verdict |
|----------|--------|---------|
| **D55 IWAD Architecture** | Engine/Stack separation via Doom WAD model | ✅ **Foundational** — Right Approximation: WAD system maps 1:1 to engine/content separation |
| **D61 Local-First Reversal** | Superseded D56 (Cloud-First for PR sprint) | ✅ **Correct** — Sovereignty requires local-first; cloud-first was a tactical compromise |
| **D178/D179/D180 Pillar Decoupling** | `pillars`→`slots`, `traits`→`metadata`, WAD fields stripped from engine | ✅ **Essential** — Enforces M2 at schema level |
| **D183 M11 Root Cause** | `anyio.create_task()` → `await` + guard (soul distillation was silently failing) | ✅ **Critical Fix** — 8/10 pillar souls were stale >14 days |
| **D176 Iron Wall IW-2/IW-3** | Round-robin key purge + BLEG/UFL (Silent 200 detection) | ✅ **High Value** — Closed biggest M9 gap |
| **D208 Heritage Remediation** | 247 tags audited, 61% over-attributed stripped, 74 vet records | ✅ **Discipline** — Heritage is now evidence-gated |

**Anti-Patterns Observed**:
- **Decision Reversals**: D56→D61 (cloud-first→local-first), D179→D180 (pillar gate removal) — shows architecture evolving under pressure
- **Decision Density**: 211 decisions in ~14 months = 15/month. High churn. Many are tactical fixes, not strategic.
- **Missing Decisions**: No decision on *release process*, *versioning scheme*, *hardware validation gates*.

**Confidence**: 9/10 — Pivot log is immutable and detailed.

---

### 2.2 Heritage Adoption Quality — **MIXED: 12/21 LEGITIMATE, 9/21 METAPHORICAL/OVER-ATTRIBUTED**

**D208 Audit Results** (Jem, 2026-07-10):
| Classification | Count | Examples |
|----------------|-------|----------|
| **LEGITIMATE** (Direct port, passes Qualification Gate) | 12 | WAD System, BSP Culling, Zone Memory, ZONEID, cvar, Lazy Deletion, High-Bit Trick, Fixed-Size Active Set, Precomputed Lookup, Netchan, idHeap, Job-Worker |
| **METAPHORICAL** (Rhetorical analogy only) | 3 | "Thinker Chain like Quake thinker", "Save-game like Quake save" |
| **OVER-ATTRIBUTED** (User-original, resembles id pattern) | 6 | 3-Tier Memory, Provider Chain, Intent Detection, Entity Registry, ResourceGuard, Circuit Breaker |

**Qualification Gate Test**: "Cannot be justified WITHOUT citing original hardware constraint."
- **WAD System**: Doom 1993 — 4MB RAM, single moddable archive → **PASSES**
- **BSP Culling**: 486 35MHz, avoid traversing invisible geometry → **PASSES**
- **3-Tier Memory**: ANAi 2025 — Python dicts are O(1), no hardware constraint → **FAILS** (correctly stripped)
- **Provider Chain**: ANAi 2025 — Fallback chain is standard resilience pattern → **FAILS** (correctly stripped)

**Right Approximation**: The 12 legitimate mappings are **high-value**. BSP→Provider Culling (O(1) breaker check) is the standout. The 9 stripped tags were **cargo-cult**.

**Confidence**: 9/10 — D208 audit is forensic.

---

## 3️⃣ WHERE WE'RE GOING — Ark Blueprint Viability

### 3.1 Epoch I (Strikes 1-3) — **COMPLETE ✅**
Physical Purge, USM, Staging Gate TUI — done. Verified.

### 3.2 Epoch II (Strikes 4-13) — **IN PROGRESS ⏳ — MIXED VIABILITY**

| Strike | Description | Viability | Risk |
|--------|-------------|-----------|------|
| **4: File-Based A2A** | Agent-to-agent via filesystem | ✅ **Real** — Low tech, high sovereignty | Low |
| **5: Sovereign Vetter** | Automated heritage vetting | ⚠️ **Cargo-cult risk** — Vetting is human judgment; automating it needs LLM-as-judge which violates local-first | Medium |
| **6: Response Provenance** | ✅ DONE | — | — |
| **7: Headroom Protocol** | ✅ DONE (semantic compression) | — | — |
| **7.1: httpx→httpx2** | ✅ DONE (28 files, 0 warnings) | — | — |
| **7.5: Semantic Router** | ✅ DONE (embedding-based entity routing) | — | — |
| **7.6: Sovereign Scholar** | Research agent with verification | ⚠️ **Scope creep** — "Scholar" overlaps `researcher` + `jem` + `verity` | High |
| **10: Module Fabric (OMS + omega-vetala)** | Plugin system | ⚠️ **Over-engineering** — 1 module (`omega-vetala`) after months. Cap at 14 modules (R7) but no module has shipped beyond vetala | High |
| **12: Semantic Resonance Vectoring** | Crisis Matrix + Provenance | 🔮 **Vaporware** — Depends on 7.5, 10, 13 | Critical |
| **13: qwen-embedding + ancient-greek-BERT** | Specialized embeddings | 🔮 **Hardware-blocked** — BERT on 5700U CPU-only is slow; qwen-embedding needs GPU for throughput | Critical |

### 3.3 Epoch III (Strikes 8, 9, 11, 14) — **FUTURE 🔮 — MOSTLY CARGO-CULT**

| Strike | Description | Verdict |
|--------|-------------|---------|
| **8: Spatial-Semantic Geometry** | ✅ Claimed done | Verify: Force-directed graph on CPU? |
| **9: P2P Mesh Traversal** | Depends on Strike 4 | 🔮 **Premature** — No user demand for P2P |
| **11: WASM Polyglot Runtime** | Depends on Strike 10 | 🔮 **Wrong priority** — WASM for *what*? Python is the runtime |
| **14: Ancient Greek BERT + KriKri WASM** | Depends on 11, 13 | 🔮 **Fantasy** — WASM BERT on 5700U? |

**Strategic Assessment**: Ark Blueprint has **3 real strikes** (4, 6, 7), **3 questionable** (5, 7.6, 10), **5 vaporware** (12, 13, 9, 11, 14). The dependency chain (4→9, 7.5→10→12, 11→13→14) creates a **critical path of speculation**.

**Right Approximation Check**: The engine needs **hygiene** (Strikes 4, 6, 7), not **geometry** (Strikes 8, 12, 14). Spatial-semantic geometry is a research project, not a sovereign engine requirement.

**Confidence**: 8/10 — Blueprint reads like a grant proposal, not a sprint plan.

---

### 3.4 Active Tasks — **PRIORITY INVERSION**

| Task | Status | Issue |
|------|--------|-------|
| **4.4 Tag & Ship v1.1.0** | ⏳ PENDING | **Blocker**: Versioning mess (see §1.5) |
| **7.1 httpx2 Migration** | ✅ DONE | Good |
| **6A blitz-tunnel** | 🟡 P0 GAP | **Real need** — WireGuard tunnel for phone→home |
| **6B Air-Gap Extractor** | 🟡 P0 GAP | **Real need** — Per-session network disable |
| **6C Runtime Governance** | 🔮 Next Level | **Vaporware** — "In-path evaluation gate" = M22+M9 on steroids |
| **6D Epistemic Filtering** | 🔮 Next Level | **Vaporware** — Frame-Stripping from Logos (2026-04) |
| **S5 MCP Transport** | 🎯 TARGET | **Real** — SSE→Streamable HTTP for OpenCode compat |
| **S6 Nemotron 3 Ultra Teacher** | 🎯 TARGET | **Real** — Local teacher pipeline for DPO |

**Finding**: P0 gaps (6A, 6B) are **sovereignty-critical** but deferred. Vaporware tasks (6C, 6D) are planned. Priority inversion.

**Confidence**: 9/10 — Task list is explicit.

---

## 4️⃣ CARMACK'S VERDICT — Top 3 Fix / Stop / Start

### 🔴 FIX (Do Now)

| # | Item | Why | Confidence |
|---|------|-----|------------|
| **1** | **Fix `antigravity` cloud classification** — Set `is_cloud=True`, add PII masking, move to priority ≥4 | M7 violation: cloud provider masquerading as local, bypasses PII masker, skews sovereignty metrics | **10/10** |
| **2** | **Enforce hardware floor** — Add `ResourceGuard.check_model_fits(model_size_gb)` before load; calibrate `cvar` RAM limit to 12Gi; add concurrent model residency tracking | 5700U 12Gi RAM is a **hard constraint**. Current code assumes infinite RAM. OOM = sovereignty loss. | **9/10** |
| **3** | **Seal `world_state` firewall breach** — Make `WorldLump` immutable per-WAD; WAD loader returns snapshot, doesn't mutate global singleton | M2 violation at runtime. Shared mutable state = architectural drift vector. | **8/10** |

---

### 🛑 STOP (Waste of Cycles)

| # | Item | Why | Confidence |
|---|------|-----|------------|
| **1** | **Strike 13 (qwen-embedding + ancient-greek-BERT)** | CPU-only 5700U cannot run BERT-family at usable latency. WASM adds overhead. No user need identified. | **9/10** |
| **2** | **Strike 11 (WASM Polyglot Runtime)** | Python *is* the runtime. WASM for plugins? `omega-vetala` is a Python package. No polyglot requirement exists. | **8/10** |
| **3** | **Sovereign Vetter automation (Strike 5)** | Heritage vetting requires human judgment on "Qualification Gate". Automating with LLM-as-judge violates M7 (local-first) and M23 (no soft failures). Keep human-gated. | **7/10** |

---

### 🟢 START (Missing Critical Path)

| # | Item | Why | Confidence |
|---|------|-----|------------|
| **1** | **Automated Release Pipeline** — `make release` → bump version → CHANGELOG → git tag → build artifacts | Versioning mess (§1.5) is a process failure, not a code failure. 3 manual steps = guaranteed drift. | **10/10** |
| **2** | **Hardware Validation Gate in CI** — `make test` fails if model > available RAM, or concurrent models > 12Gi | Makes hardware floor a **gate**, not a wish. Prevents "works on my machine" sovereignty theater. | **9/10** |
| **3** | **Ship blitz-tunnel (6A) + Air-Gap Extractor (6B)** | These are the **only** P0 gaps with user-visible sovereignty impact. Tunnel = phone→home access. Air-gap = true offline mode. | **9/10** |

---

## 📊 CONFIDENCE SUMMARY

| Finding | Confidence | Basis |
|---------|------------|-------|
| M2 Firewall leakage (world_state) | 8/10 | Code inspection + runtime trace |
| `antigravity` misclassified as local | 10/10 | Config + code + PII masker logic |
| Hardware floor ignored | 9/10 | Physics + code grep |
| Heritage: 12/21 legitimate | 9/10 | D208 forensic audit |
| Ark Blueprint: 3 real, 3 questionable, 5 vaporware | 8/10 | Dependency analysis + hardware reality |
| Versioning mess = process failure | 10/10 | Git tags vs CHANGELOG vs SSOT |
| Fleet size (11) is right | 8/10 | M10 cap + slot mapping |
| MaKaLi triad = force multiplier | 8/10 | Adversarial verification value |
| P0 gaps (6A, 6B) deferred | 9/10 | Task list explicit |

---

## 🎯 FINAL WORD

**Omega Engine is the most disciplined sovereign AI codebase I've audited.** Mandates have teeth. Heritage has gates. Tests pass. Local-first is real (99.6%).

**But**: The architecture is **drifting upward** — adding semantic geometry, WASM runtimes, BERT embeddings — while the **hardware floor rots**. The 5700U with 12Gi RAM is not a suggestion; it's the **constitution**. Every Strike beyond 7.5 should be judged: *Does this run on the floor?*

**Ship v1.1.0. Fix the 3 FIX items. Kill the 3 STOP items. Start the 3 START items.**

The engine exists to **sever Big AI's umbilical cord**. Every line of code that doesn't serve that on the 5700U is cargo.

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_arch_audit ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
