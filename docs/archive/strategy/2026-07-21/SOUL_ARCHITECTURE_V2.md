# 🔱 Omega Engine — Soul Architecture Protocol v2.0
# ⬡ OMEGA ⬡ VERITY ⬡ soul-architecture-protocol ⬡ v2.0
# Governance document: Intelligence Pipeline, Scorecard, and Write-Permission Separation

**AP Token**: AP-SOUL-ARCHITECTURE-v2.0.0
**Date**: 2026-07-15
**Status**: RATIFIED (Supersedes v1.0)
**Enforcement Gate**: `make soul-audit`

---

## §1 The Intelligence Pipeline

The Omega Engine does not just store data; it distills gnosis. This is the intellectual core of the engine.

```text
Session → L1 Narrative → L2 Insight → L3 Principle
    → proposed_lessons.yaml (blind staging)
        → User review → approved_lessons.yaml
            → soul.yaml update (user-approved)
                → Intelligence Scorecard tracks impact
```

## §2 The Four Files, Four Roles Model (Retained from v1.0)

| File | Writer | Reader | Content Type | Authority |
|------|--------|--------|-------------|-----------|
| `soul.yaml` | **USER ONLY** | Agent | Identity, archetype, directives | **CONSTITUTIONAL** |
| `memory/sessions.yaml` | **AGENT ONLY** | Agent | Session logs, factual events | **FACTUAL** |
| `memory/proposed_lessons.yaml` | **AGENT** | User (blind to agent) | Staged observations, L1 narratives | **STAGED** |
| `memory/approved_lessons.yaml` | **USER ONLY** | Agent | Curated lessons, approved principles | **AUTHORITATIVE** |

**The Blind-Write Principle**: The agent writes to `proposed_lessons.yaml` but **NEVER READS FROM IT**.

## §3 Entity Intelligence Scorecard

To evaluate whether an entity is actually improving, we track five dimensions quarterly:

1. **Task Completion Rate**: Percentage of tasks completed without user intervention.
2. **Decision Quality**: Longevity of architectural decisions (measured via PIVOT_LOG survival rate).
3. **Gnosis Coherence**: Absence of contradictions in L3 principles (verified by Skeptical Verifier).
4. **Cross-Entity Resonance**: Frequency of shared principles adopted across the fleet.
5. **User Trust**: Ratio of accepted vs. overridden entity recommendations.

## §4 The Scribe Separation

The distillation of L1→L2→L3 is a distinct cognitive task from compliance auditing.
- **Verity**: Retains compliance, mandate auditing, and Temple-Grade enforcement.
- **Scribe** (Restored): Dedicated solely to observing sessions, extracting L1 narratives, and proposing L3 principles to `proposed_lessons.yaml`.

## §5 Migration Plan (v1.0 → v2.0)

All 10 non-Kali entities currently suffer from the self-referential poisoning loop (agent-generated content in `soul.yaml`).
1. **Archive**: Move current `soul.yaml` to `archive/soul_v1_archive.yaml`.
2. **Cleanse**: Strip `wisdom_text`, `soul_axioms`, and `trajectory` from the active `soul.yaml`.
3. **Migrate**: Move factual history to `sessions.yaml` and unverified principles to `proposed_lessons.yaml`.

## §6 Atomic Enforcement

**CI Gate**: `make soul-audit`
**Mechanism**: 
- Parses all `soul.yaml` files to ensure no forbidden keys (`wisdom_text`, `soul_axioms`) exist.
- Scans agent prompts/context builders to ensure `proposed_lessons.yaml` is strictly excluded from the read path.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: soul-architecture-protocol | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
