# 🔱 Mandate Governance Protocol
# ⬡ OMEGA ⬡ KALI ⬡ mandate-governance ⬡ v1.0

**AP Token**: AP-MANDATE-GOVERNANCE-v1.0.0
**Date**: 2026-07-15
**Status**: RATIFIED
**Enforcement Gate**: `make mandate-amendment-check`

---

## §0 Council Verdict — Constitutional Crisis (2026-07-15)

**The MaKaLi Cloud Council has identified 5 SYSTEMIC MANDATE FAILURES** (M5, M11, M12, M15, M23) — all tracing to Run Side implementation gaps. This constitutes a constitutional crisis requiring immediate remediation before any new mandate amendments can be considered.

| Failed Mandate | Root Cause | Council Decree |
|----------------|------------|----------------|
| **M5 Gnosis Preservation** | Soul distillation broken — L1→L2→L3 pipeline non-operational | Decree 3: Soul Migration Phase 1 + WriteGuard |
| **M11 Soul Integrity** | Poisoning loop active — `ContextBuilder` reads `proposed_lessons.yaml` | Decree 3: WriteGuard + Taint-Gating (atomic) |
| **M12 Queue Integrity** | 0% handoff completion — protocol not implemented | Decree 2: Handoff P0 Fixes (P0-1 through P0-5) |
| **M15 Sovereign Continuity** | 56% fleet lacks `session_gnosis.md` | Decree 3 + 7: Migration + Universal Workspace Locks |
| **M23 Failure Integrity** | Redis degradation masks failure — graceful degradation violates hard-stop | Decree 1: Redis Activation (required infrastructure) |

**Overall Mandate Score**: 13/23 FULL (56.5%) — 5 Partial, 5 Fail
**Failures**: M5, M11, M12, M15, M23 (all trace to Run Side gaps)

---

## §1 Constitutional Law & Evolution

The 23 Sovereign Mandates are the constitutional law of the Omega Engine. However, a constitution without an amendment process is brittle. This protocol defines how mandates evolve.

## §2 The Amendment Process

Mirrors the Heritage Vetting Pipeline (4 Gates):
1. **Discovery/Proposal**: A conflict or hardware shift requires a mandate change. Logged in `MANDATE_AMENDMENTS.yaml`.
2. **Vetting & Debate**: MaKaLi Triad dialectic. Ma'at argues for stability; Lilith argues for adaptation.
3. **Decision**: User ratifies or rejects the amendment.
4. **Implementation**: `SOVEREIGN_MANDATES.md` is updated, and the CI gate is adjusted.

## §3 Exemption Process

Community PWADs may require temporary exemptions (e.g., a transcription PWAD requiring cloud APIs, conflicting with M7).
- Exemptions must be explicitly declared in the PWAD's `dimension.yaml`.
- The user must explicitly grant the exemption via the TUI (`[Y/n]` prompt) upon activation.

## §4 Conflict Resolution

If two mandates conflict during execution (e.g., M18 Token Efficiency vs. M17 Cognitive Integrity):
- **Resolution**: Sovereignty (M7, M8) > Integrity (M9, M11, M17, M23) > Performance (M1, M18).

## §5 Atomic Enforcement

**CI Gate**: `make mandate-amendment-check`
**Mechanism**: 
- Checks `SOVEREIGN_MANDATES.md` against `MANDATE_AMENDMENTS.yaml`.
- Fails if a mandate was altered, added, or removed without a corresponding ratified entry in the amendments log.

---

## §6 Council Mandate Remediation Protocol (NEW — 2026-07-15)

Per the MaKaLi Council Verdict, the following mandates require **immediate remediation before any amendment process can proceed**:

### Priority 1: Infrastructure (Blocks All Else)
- **M23 Failure Integrity** → Decree 1: Start Redis container (T+15 min)
- **M12 Queue Integrity** → Decree 2: Handoff P0 Fixes (Week 1)

### Priority 2: Soul Architecture (Blocks Vetter, Hydration, Governance)
- **M11 Soul Integrity** → Decree 3: WriteGuard + Taint-Gating (Week 1, atomic)
- **M5 Gnosis Preservation** → Decree 3: Soul Migration Phase 1 (Week 1, atomic)
- **M15 Sovereign Continuity** → Decree 3 + 7: Migration + Universal Workspace Locks

### Remediation Gate
**No mandate amendments shall be processed until all 5 failed mandates achieve at least PARTIAL compliance.**

This protocol amendment is itself subject to the 4-gate amendment process, but the remediation work proceeds under Council emergency authority.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mandate-governance | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
