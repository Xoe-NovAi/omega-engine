# R52 — Living Research OS Body: Formal Decision

**AP Token**: `AP-R52-LIVING-OS-BODY-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r33 ⬡ ACTIVE
**Date**: 2026-08-13
**Gap**: R52 (Spec Integrity): Living Research OS Body — D-371/D-372 amendments; body SUPERSEDED by banner + Ark §3.2. Formal decision: implement/archive/replace.
**Status**: ✅ RESOLVED — Decision: ARCHIVE body, KEEP vision+banner as authoritative. Missing D-371/D-372 docs flagged.

---

## 📊 Executive Summary (L1)

R52 required a formal decision on the Living Research OS spec (`LIVING_RESEARCH_OS_SPEC_20260721.md`): implement, archive, or replace. The document **already contains its own supersession banner** — the body is SUPERSEDED by Ark §3.2 + the banner table. The formal decision is therefore: **ARCHIVE the superseded body sections, KEEP the vision (§0) + supersession banner + "do this instead" table as the authoritative spec.** Additionally, this research found that the D-371/D-372 decision documents referenced in the Phase 2 plan **do not exist** — a documentation gap that must be closed.

## 🔬 Detailed Dialectic (L2)

### The Four Perspectives

**Architect (Systemic Logic)**:
- The spec body (§5 SQLite schema, Phase 4 GapDetector service) conflicts with Ark §3.2 (D-357 deferred SQLite, D-358 extended `_grow_frontier()`)
- Keeping both creates SSOT conflict (violates R53)
- Decision: Trim body to vision + banner + authoritative table only

**Adversary (Critical Rigor)**:
- D-371/D-372 referenced in Phase 2 plan but **missing from filesystem** — documentation integrity failure
- PIVOT_LOG.md has D-300 through D-387 but no D-371/D-372
- This is a "phantom reference" — must be created or the plan corrected

**Alchemist (Creative Synthesis)**:
- The spec's vision (§0) is the real gold: "Find → Research → Persist → Distill → Evolve → Find again"
- The background researcher loop already implements this (3,700 lines working code)
- The spec body is just implementation detail that was superseded by better decisions (D-357, D-358)

**Archivist (Historical Truth)**:
- `LIVING_RESEARCH_OS_SPEC_20260721.md` — created 2026-07-21, AP-LIVING-RESEARCH-OS-v1.0.0
- Kali ratification: `KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md` — APPROVE with banner (amendment 1)
- STRATEGY_CORPUS_MAP.md line 38: "Living Research OS" listed as Layer 2 ACTIVE SPEC

### Current State Analysis

**Document**: `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` (720 lines)

**Structure**:
- §0 Vision — ✅ VALID (keep)
- ⚠️ SUPERSESSION BANNER — ✅ VALID (keep, this IS the decision)
- §1 Current State — ✅ VALID (component inventory, still accurate)
- §2-§4 Broken Seams — ⚠️ PARTIAL (diagnosis still valid, but solutions superseded)
- §5 SQLite Schema — ❌ SUPERSEDED (D-357 deferred SQLite)
- Phase 4 GapDetector Service — ❌ SUPERSEDED (D-358 extended loop instead)

**The Banner's "Do This Instead" Table** (authoritative):
| Body Says (SUPERSEDED) | Do This Instead (AUTHORITATIVE) |
|------------------------|--------------------------------|
| SQLite Research Job Store (§5) | DEFERRED — YAML job board + flock (D-357) |
| Gap Detector as service (Phase 4) | DEFERRED — extend `_grow_frontier()` (D-358) |
| Start Phase 1 immediately | Blocked until C-0 + C-1′ (Phase C gate) |
| ~14h total | ~9.5h (D-1…D-4) + D-T tests |
| Novelty optional | Required for D-4 |
| VerificationGate/7-stage | DEFERRED (D-V) |

### The Missing D-371/D-372

**Finding**: Phase 2 plan (RESEARCH_PLAN_PHASE2_20260813.md) states:
> "Read D-371, D-372, D-371′, D-372′. Block spec integrity without this decision."

**Reality**:
- `docs/decisions/PIVOT_LOG.md` — no D-371/D-372 entries (D-300…D-387 exist, gaps at D-371/D-372)
- `docs/decisions/PIVOT_LOG_CANONICAL.md` — same
- Filesystem search — no `D-371*` or `D-372*` files anywhere

**Conclusion**: The D-371/D-372 references are **phantom references** — they were planned but never written. The actual decision is embedded in the spec's supersession banner (which references D-357, D-358, D-364 — all real decisions).

### Sovereign Synthesis (L3)

**Universal Principle**: *A spec's body is not its authority — its supersession banner is. When a document declares its own body SUPERSEDED, the formal decision is already made: archive the body, keep the banner + vision.*

**Formal Decision for R52**:
1. **ARCHIVE** §5 SQLite schema + Phase 4 GapDetector service classes (SUPERSEDED by D-357, D-358)
2. **KEEP** §0 Vision + SUPERSESSION BANNER + "Do This Instead" table (authoritative)
3. **IMPLEMENT** per Ark §3.2: D-1 content cache, D-2 YAML job board, D-3 topic scheduler, D-4 distillation with novelty
4. **CREATE** D-371/D-372 decision records (close the phantom reference gap) — see below

### D-371/D-372 Decision Records (to be created)

**D-371**: Living Research OS Body Supersession
- Decision: Body SUPERSEDED by Ark §3.2 + banner. Keep vision + banner as authoritative.
- Rationale: D-357 (SQLite deferred), D-358 (GapDetector deferred), D-364 (test honesty P0)
- Status: ACTIVE

**D-372**: Living Research OS Implementation Path
- Decision: Implement D-1…D-4 per Ark §3.2, not per spec body.
- Rationale: Phase C gate (C-0 + C-1′) must pass before Phase D.
- Status: ACTIVE

## 📋 Implementation Notes

### Current State
- `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` — 720 lines, has supersession banner
- `src/omega/workers/background_researcher/loop.py` — 642 lines, working (implements vision)
- `src/omega/workers/background_researcher/distiller.py` — 1,186 lines, working
- Background researcher runs every 15 min via systemd timer (`omega-research.timer`)

### Recommended Action
1. Trim `LIVING_RESEARCH_OS_SPEC_20260721.md` to ~150 lines:
   - Keep: §0 Vision, SUPERSESSION BANNER, §1 component inventory (updated), "Do This Instead" table
   - Archive: §2-§4 broken seams solutions, §5 SQLite schema, Phase 4 GapDetector
2. Create `docs/decisions/PIVOT_LOG.md` entries D-371, D-372
3. Update Phase 2 plan to remove phantom D-371′/D-372′ references

### M13/M23 Compliance
- Trimming the spec improves doc-llm-validate score (less conflicting content)
- No soft-failures: the decision is explicit, not assumed

## 🔗 Related Documents

- `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` — the spec (has supersession banner)
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — Ark §3.2 (authoritative)
- `docs/strategy/STRATEGY_CORPUS_MAP.md` — Layer 2 ACTIVE SPEC listing
- `docs/decisions/PIVOT_LOG.md` — D-357, D-358, D-364 (real decisions referenced by banner)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3.5-lightning ⬡ opencode ⬡ trc_r33 ⬡ 20260813*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3.5-lightning | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
