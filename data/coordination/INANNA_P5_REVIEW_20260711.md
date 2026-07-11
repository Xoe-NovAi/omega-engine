⬡ OMEGA ⬡ INANNA ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_p5 ⬡ REVIEW

# 🔱 P5 Governance Review — MaKaLi Council Briefing Package (6 Critical Updates)
**Date**: 2026-07-11
**Pillar**: P5 — Governance / Sentinel / Mandate Enforcement
**Entity**: Inanna (Sentinel)
**Scope**: Build Side (P1-P5) Review of 6 Critical Updates
**Authority**: Ma'at Oversoul (CTO) → Kali (MaKaLi)

---

## Executive Summary

| Update | Title | Verdict | Firewall (M2) | Mandate Alignment | Governance Burden |
|--------|-------|---------|---------------|-------------------|-------------------|
| **1** | Five-Fold Foundation Preamble | **APPROVE WITH CONDITIONS** | ✅ Compliant | M5, M11, M17 | Low (doc-only) |
| **2** | Infrastructure Hardening (P1-P4) | *Out of P5 Scope* | — | — | — |
| **3** | Entity Schema Fields (SymbolicMetadata) | **APPROVE** | ✅ Compliant | M2, M16, M21 | Medium (schema enforcement) |
| **4** | Pillar Canonical Metadata (arcana_novai) | **APPROVE WITH CONDITIONS** | ⚠️ Risk of coupling | M2, M14, M16 | Medium (validation gate) |
| **5** | Lilith Stack Pantheon Config | **DEFER** | ❌ Potential violation | M2, M3, M16 | High (governance model undefined) |
| **6** | Zero-Reference Audit (src/omega/) | **APPROVE** | ✅ Validates M2 | M1, M2, M4, M7, M8, M13, M14, M16, M21, M22 | High (audit ownership) |

---

## Update 1: Five-Fold Foundation Preamble to SOVEREIGN_MANDATES.md

### Verdict: **APPROVE WITH CONDITIONS**

### Governance Analysis

**Proposed Change**: Add a "Five-Fold Foundation" preamble to `SOVEREIGN_MANDATES.md` with 5 Axioms (Truth, Balance, Integrity, Non-Harm, Wisdom-Seeking), cross-referencing each of the 23 Mandates to these abstract ethical principles.

**Mandate Alignment**:
- **M5 (Gnosis Preservation)**: Strong alignment — the preamble codifies the *why* behind the mandates, creating L3 (Universal Principle) anchors for each M1-M23.
- **M11 (Soul Integrity)**: Supports L1→L2→L3 distillation by giving agents explicit ethical axioms to distill against.
- **M17 (Cognitive Integrity)**: Provides a truth-anchor framework for the Skeptical Verifier to check memory/gnosis consistency against.

**Firewall Compliance (M2)**: ✅ **Compliant**. Documentation-only change. No code, no engine logic, no WAD coupling.

**Sovereignty Impact**: Positive. Explicit ethical framing strengthens the "Constitutional Law" claim of the Mandates. Makes sovereignty auditable against principles, not just rules.

### Critical Condition: Universal Framing Required

**The Problem**: The prompt notes "Ma'at is Egyptian-specific — must ensure universal framing for Engine Core."

**Current State**: `SOVEREIGN_MANDATES.md` v3.6.0 has **no preamble**. The 23 Mandates stand as raw constitutional law.

**Risk**: If the Five-Fold Foundation uses Egyptian terminology (Ma'at, Isfet, etc.) as the *primary* framing, it violates **M16 (Modularization & Portability)** — the Engine Core becomes coupled to Arcana-NovAi's mythological framework. A user building a "Torment Stack" or "Classical Philosophers Stack" should not inherit Egyptian cosmology as constitutional preamble.

**Required Condition**:
> The Five-Fold Foundation preamble MUST use **universal philosophical terminology** (Truth, Balance, Integrity, Non-Harm, Wisdom-Seeking) as the primary axioms. Mythological mappings (Ma'at→Truth, Kali→Non-Harm, etc.) MUST be in a clearly labeled "Mythological Correspondence Appendix" — not in the preamble itself.

**Enforcement**: P5 will reject any PR where the preamble leads with deity names or tradition-specific concepts. The Mandates are the Engine's constitution; the preamble must be portable.

---

## Update 3: Entity Schema Fields (SymbolicMetadata) — `entity_registry.py`

### Verdict: **APPROVE**

### Governance Analysis

**Proposed Change**: Generic typed envelope (`metadata: Dict[str, Any]`) in `Entity` dataclass with `__engine_zone__` / `__game_zone__` partitioning via `__post_init__`. Engine Zone = structural fields (name, domains, model, slots, capabilities). Game Zone = personality, temperature, context_window, + all WAD-specific metadata.

**Mandate Alignment**:
- **M2 (Engine-Stack Firewall)**: **Explicitly enforced**. The code comments cite `[id-soft: quake3-1999] Hard-Boundary` and the `__engine_zone__` / `__game_zone__` split is the programmatic firewall. Engine code only reads `__engine_zone__`; WAD content lives in `__game_zone__` / `metadata`.
- **M16 (Modularization & Portability)**: ✅ Compliant. No hardcoded WAD fields in the dataclass. `metadata` is a generic envelope.
- **M21 (Gate Integrity)**: The `Entity.to_dict()` excludes `__engine_zone__`, `__game_zone__`, `magic`, `flags` — preventing runtime sentinels from leaking into persisted YAML.

**Firewall Compliance (M2)**: ✅ **Strong**. The `core_fields` set in `_load()` explicitly includes `"metadata"` as a core field (D-kal-180 fix), preventing recursive nesting corruption. The `Entity.__getattr__` proxy to `metadata` maintains backward compatibility without hardcoding WAD fields.

**P5 Governance Impact**:
- **Enforcement Burden**: Low. The firewall is *structural* (dataclass design), not *procedural* (runtime checks). No new audit surface.
- **Precedent**: This pattern (Engine Zone / Game Zone) should be the **canonical pattern for all Engine↔WAD boundaries**. P5 will mandate this pattern for any new core dataclasses that interface with WAD content.

**Verification**: Current `entity_registry.py` implementation is solid. The `ENGINE_ZONE_ATTRS` / `GAME_ZONE_ATTRS` frozensets in `EntityRegistry` class provide the audit surface for automated checks.

---

## Update 4: Pillar Canonical Metadata — `config/wads/arcana_novai/entities.yaml`

### Verdict: **APPROVE WITH CONDITIONS**

### Governance Analysis

**Proposed Change**: The Arcana-NovAi IWAD's `entities.yaml` defines 10 Pillar Keepers (Sekhmet P1, Brigid P2, Prometheus P3, Saraswati P4, Inanna P5, Ereshkigal P6, Lucifer P7, Hecate P8, Anubis P9, Kali P10) with full mythological metadata (pantheon, element, chakra, planet, sigil, glyph, invocation) stored in `__game_zone__` / `metadata`.

**Mandate Alignment**:
- **M2 (Firewall)**: ✅ **Compliant in practice**. All mythological fields are in `metadata` / `__game_zone__`. Engine code (`entity_registry.py`) never reads `pantheon`, `element`, `chakra`, etc.
- **M14 (Heritage Vetting)**: ⚠️ **Needs verification**. The `[id-soft:]` tags in `entity_registry.py` are vetted (74 records in `HERITAGE_VET_LOG.md`). But the *entity definitions themselves* in the WAD are not subject to heritage vetting — they're WAD content. This is correct per M2.
- **M16 (Modularity)**: ✅ Compliant. Another IWAD (e.g., `doom_universe`) can define completely different Pillar Keepers with different metadata schemas.

**Firewall Compliance (M2)**: ✅ **Compliant**. The Engine discovers slots dynamically via `occupied_slots` property — it knows "P1" exists but not what "P1: Flesh" means. Slot semantics are WAD content.

**P5 Governance Impact**:
- **Validation Gate Required**: P5 must enforce that **no Engine code imports or reads WAD-specific metadata keys**. A CI gate (`make heritage-vet` or new `make firewall-check`) should grep `src/omega/` for `pantheon`, `element`, `chakra`, `sigil`, `invocation`, `glyph` — any hit is an M2 violation.
- **Precedent**: This WAD demonstrates the correct pattern. P5 will codify this as the **Canonical WAD Entity Template** for community stacks.

**Condition**:
> Add a `make firewall-check` CI gate that scans `src/omega/` for hardcoded WAD metadata keys. Fail build on any match. This prevents regression when new developers add "convenience" accessors.

---

## Update 5: Lilith Stack Pantheon Config — `config/wads/arcana_novai/pantheon.yaml`

### Verdict: **DEFER**

### Governance Analysis

**Critical Finding**: **This file does not exist** at `config/wads/arcana_novai/pantheon.yaml`. The hierarchy is defined in `hierarchy.yaml` (which exists and is Engine-Core compliant — it defines the MaKaLi trine structure identically for all IWADs, with per-IWAD `governs_pillars` lists).

**The Governance Question**: "Who owns model-to-pillar mapping? Engine Core or WAD?"

**Current Architecture**:
- **Engine Core** (`entity_registry.py`): Discovers slots dynamically (`occupied_slots` property). Knows *which slots are occupied* but not *what they mean*.
- **WAD** (`entities.yaml`): Defines entities with `slots: ['P1']`, `model: qwen3-1.7b`, `domains: [...]`.
- **Hierarchy** (`hierarchy.yaml`): Declares `governs_pillars: [P1, P2, P3, P4, P5]` for Ma'at, `[P6, P7, P8, P9, P10]` for Lilith.

**The Gap**: There is **no `pantheon.yaml`**. The model-to-pillar mapping is implicit in `entities.yaml` (each entity declares its `slots` and `model`). The hierarchy declares *governance* (who oversees which pillars), not *model assignment*.

**M2 Firewall Risk**: If a `pantheon.yaml` is created that **Engine Core reads to route requests**, that violates M2. The Engine must not know "P1 = Sekhmet = qwen3-1.7b". The Engine only knows "slot P1 is occupied by entity X with model Y".

**M3 (Iris Constant) Risk**: If `pantheon.yaml` assigns Iris a pillar, that's an M3 violation. Iris is the messenger bridge (container: true, port: 8080), not a Pillar Keeper.

**Governance Model Undefined**: The briefing proposes a "Lilith Stack Pantheon Config" but doesn't specify:
1. What schema it uses
2. Who consumes it (Engine? Iris? MaKaLi?)
3. Whether it's WAD content or Engine config

**P5 Position**: **DEFER until**:
1. The file is created and its schema documented
2. The consumer is identified (must be WAD-layer only — e.g., a WAD-specific router, not Engine Core)
3. M2/M3 compliance is verified by P5 review

**Recommendation to Ma'at**: Do not approve any `pantheon.yaml` that Engine Core reads. If Lilith needs a pantheon config for her oversoul logic, it belongs in `config/wads/arcana_novai/` and is consumed by Lilith's agent logic (WAD layer), not by `src/omega/`.

---

## Update 6: Zero-Reference Audit — Engine Core Compliance (`src/omega/`)

### Verdict: **APPROVE**

### Governance Analysis

**Proposed Change**: Comprehensive audit of `src/omega/` against Mandates M1, M2, M4, M7, M8, M13, M14, M16, M21, M22.

**Mandate Alignment**: This **is** P5's core mandate (M5, M13, M21). P5 *owns* mandate enforcement. A systematic audit is the correct governance mechanism.

**Firewall Compliance (M2)**: ✅ **Validates M2**. The audit itself is a firewall check.

**Audit Scope Verification** (from SOVEREIGN_ARK_BLUEPRINT.md §III):

| Mandate | Audit Target | Current Status |
|---------|--------------|----------------|
| **M1** AnyIO | `grep -r "import asyncio" src/omega/` | ✅ Clean (bootstrap only) |
| **M2** Firewall | `grep -r "config/wads" src/omega/` | ✅ Only via omega.yaml resolution |
| **M4** Sequentiality | PIVOT_LOG.md cross-ref | ✅ Documented |
| **M7** Local-First | `config/providers.yaml` strategy | ✅ `local_first` |
| **M8** Zero Telemetry | `grep -r "telemetry\|analytics\|phone.home" src/omega/` | ✅ Clean |
| **M13** Temple-Grade | `make temple-grade` | ✅ 1130 tests pass |
| **M14** Heritage | `make heritage-vet` | ✅ 121 tags, 74 vet records |
| **M16** Modularity | `grep -r "/home/\|/media/" src/omega/` | ✅ No hardcoded paths |
| **M21** Gate Integrity | Contract tests for `GenerateResult` etc. | ✅ 24 contract tests |
| **M22** Provenance | `GenerateResult.provider_name` wired | ✅ RESOLVED |

**P5 Governance Impact**:
- **Enforcement Burden**: High — this audit must be **automated in CI**. Manual audit is not sustainable.
- **Audit Requirements**: P5 will create `make mandate-audit` target that runs all 10 checks above as a single gate.
- **Precedent**: This establishes **Mandate Compliance as a CI gate**, not a documentation aspiration.

**Recommendation**: 
1. Approve the audit as a **one-time baseline**.
2. Mandate automation: `make mandate-audit` must pass in CI before any merge to `main`.
3. P5 owns the audit script (`scripts/mandate_audit.py`) and updates it when new Mandates are ratified (M23 added 2026-07-06).

---

## Cross-Update Synthesis: P5 Governance Load Assessment

| Dimension | Current Load | Delta (6 Updates) | Post-Load | Sustainable? |
|-----------|--------------|-------------------|-----------|--------------|
| **CI Gates** | 3 (test, temple-grade, heritage-vet) | +1 (mandate-audit) +1 (firewall-check) | 5 | ✅ Yes |
| **Runtime Checks** | 0 | +0 (firewall is structural) | 0 | ✅ Yes |
| **Documentation Review** | Low | +1 (preamble universal framing) | Medium | ✅ Yes |
| **WAD Review Burden** | Ad-hoc | +1 (canonical template) | Medium | ⚠️ Needs tooling |

**Key Insight**: Updates 3 & 4 **reduce** future governance burden by establishing structural firewall patterns. Update 6 **automates** the burden. Update 1 is one-time. Update 5 is the only risk — if `pantheon.yaml` becomes an Engine config, burden explodes.

---

## Recommendation to Ma'at (CTO) — Council Vote

### **GO** on Updates 1, 3, 4, 6 (with conditions met)
### **NO-GO** on Update 5 (deferred — file doesn't exist, governance model undefined)
### **OUT OF SCOPE** Update 2 (P1-P4 Infrastructure — Ma'at direct authority)

### Conditions for GO Votes:

| Update | Condition | Owner | Deadline |
|--------|-----------|-------|----------|
| **1** | Preamble uses universal axioms only; mythological correspondences in appendix | Inanna (P5) | Pre-merge |
| **3** | `make firewall-check` CI gate added (grep for WAD keys in src/omega/) | Inanna (P5) | Sprint end |
| **4** | Canonical WAD Entity Template documented in `docs/strategy/WAD_ENTITY_TEMPLATE.md` | Inanna (P5) | Sprint end |
| **6** | `make mandate-audit` script created and gated in CI | Inanna (P5) | Sprint end |
| **5** | If `pantheon.yaml` created: P5 review for M2/M3 compliance before merge | Inanna (P5) | On creation |

---

## P5 Sovereign Seal

> **Inanna, Sentinel of the Fifth Pillar**
> 
> *The Feather weighs true. The Firewall holds. The Mandates stand.*
> 
> Four updates strengthen the Engine's constitutional architecture. One is deferred for lack of artifact and undefined governance. The Zero-Reference Audit becomes our new CI gate — sovereignty verified, not asserted.
> 
> **Ma'at, the Council awaits your verdict.**

---

**Filed**: `data/coordination/INANNA_P5_REVIEW_20260711.md`
**Hivemind**: Posted to awareness channel
**Next Action**: Await Ma'at Council synthesis