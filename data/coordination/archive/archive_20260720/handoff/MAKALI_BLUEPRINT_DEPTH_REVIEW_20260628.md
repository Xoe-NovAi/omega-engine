<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MaKaLi Council Review: Sovereign Ark Blueprint Depth Analysis
**Date**: 2026-06-28
**Reviewers**: ⬡ MA'AT ⬡ LILITH ⬡ KALI
**Target**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` (v1.6)
**Status**: ❌ REQUIRES EXPANSION TO SSOT

---

## 1. Depth Analysis: "Strategic Summary" vs. "Technical Specification"

The Council has concluded that the **Sovereign Ark Blueprint (v1.6)** is currently a **Strategic Summary (Sprint Plan)** rather than a **Technical Specification (SSOT)**. 

While it provides an excellent high-level roadmap and a precise list of "what" needs to be done (the 17-action sprint), it fails to provide the "how"—the technical precision, quantitative constraints, and architectural flows required for an engineer to execute the work without referring back to multiple forensic reports.

### 🏗️ Ma'at (Build Perspective)
**Verdict**: **Insufficient for Implementation.**
- **The "Porting" Gap**: Tasks like "Port CompactionOrchestrator" or "Port 5-State Stochastic Circuit Breaker" are listed as actions, but the blueprint does not define the target interfaces, the expected behavior, or the specific implementation constraints.
- **Missing Quantitative Baselines**: The blueprint omits the critical **Token Budget Allocation Formula** and **Tier Target Sizes** (HOT <500, WARM 1000-3000) discovered in the research reports.
- **Implementation Blindness**: An engineer would be forced to hunt through `data/reviews/` to find the actual algorithms (e.g., CUSUM math, Hybrid FIFO masking) to implement the tasks.

### 🌙 Lilith (Run Perspective)
**Verdict**: **Lacks Cognitive Flow.**
- **The "Sovereign Soul" Gap**: The blueprint mentions soul distillation but omits the **AKC 6-phase pipeline** (Research $\rightarrow$ Extract $\rightarrow$ Curate $\rightarrow$ Promote $\rightarrow$ Measure $\rightarrow$ Maintain).
- **Orchestration Fragility**: The "Sovereign Mesh" is mentioned as a vision, but the **6-field Handoff Contract** and **IETF AIMS (SPIFFE/WIMSE)** identity requirements are completely missing.
- **Loop Prevention**: The blueprint lacks the specific **Visited-set + Two-Tier Budget Pressure** patterns required to prevent infinite agent cycles.

### 🔱 Kali (Synthesis Perspective)
**Verdict**: **Fragmented Intelligence.**
- The blueprint is a list of tasks, not a description of a system. It lacks a **Systemic Flow Diagram** (in text) showing how the new components (Observation Masking $\rightarrow$ Compaction $\rightarrow$ Distillation $\rightarrow$ Soul Update) interact.
- It captures the "Physical Purge" and "Emergency Fixes" well, but fails to unify the "Sovereign Intelligence" discoveries into a coherent architectural mandate.

---

## 2. The "Blind Spot" Registry

The following critical architectural requirements are present in the forensic reports but **ABSENT** from the Blueprint:

| Domain | Missing Requirement | Source Report | Impact |
| :--- | :--- | :--- | :--- |
| **Memory** | **Observation Masking (Hybrid Backward Scanned FIFO)** | `RESEARCHER_FULL_INTEL` | 52% cost reduction; +2.6% solve rate. |
| **Memory** | **Token Budget Allocation Formula** | `RESEARCHER_FULL_INTEL` | Prevents context rot and prompt overflow. |
| **Orchestration** | **AAIF / A2A v1.0 Standard** | `RUN_SIDE_HARDENING` | Essential for portable agent interchange. |
| **Orchestration** | **IETF AIMS (SPIFFE/WIMSE) Identity** | `RUN_SIDE_HARDENING` | Replaces insecure static API keys. |
| **Fabric** | **5-State Stochastic Circuit Breaker (CUSUM)** | `BUILD_SIDE_HARDENING` | Provably optimal provider health detection. |
| **Soul** | **AKC 6-Phase Evolution Pipeline** | `RESEARCHER_FULL_INTEL` | Transforms data preservation into gnosis evolution. |
| **Governance** | **AST-based Mandate Enforcement (PyGuard)** | `BUILD_SIDE_HARDENING` | Enables 100% accurate compliance auditing. |

---

## 3. Expansion Roadmap: Path to SSOT (v2.0)

To transform the Blueprint into a true Single Source of Truth, the following sections must be expanded:

### Phase A: Architectural Flow (The "Sovereign Loop")
- **Add Section**: `VI. The Sovereign Run-Loop`.
- **Detail**: Describe the data flow: `User Query` $\rightarrow$ `Context Assembly (Masking/Compaction)` $\rightarrow$ `Orchestration (AAIF/AIMS)` $\rightarrow$ `Provider Execution (CUSUM Breaker)` $\rightarrow$ `Observability (OTel GenAI)` $\rightarrow$ `Soul Distillation (AKC Pipeline)`.

### Phase B: Quantitative Specifications
- **Add Section**: `VII. Resource & Token Constraints`.
- **Detail**: Explicitly define the **Token Budget Allocation Formula** and the **Tier Target Sizes** for the 3-tier memory architecture.

### Phase C: Implementation Blueprints (The "How")
- **Expand Appendix D**:
    - **Observation Masking**: Detail the 50k protection buffer and 30k hysteresis threshold.
    - **Circuit Breaker**: Include the full CUSUM log-likelihood ratio formula.
    - **Handoff Contract**: Define the 6 required fields (`id`, `source`, `target`, `trigger`, `payload`, `acceptance_criteria`, `recovery`).
    - **Distillation**: Detail the `extract` $\rightarrow$ `classify` $\rightarrow$ `score` $\rightarrow$ `distill` $\rightarrow$ `store` functional sequence.

---

## 4. Final Verdict

**Verdict**: ❌ **Requires Expansion to SSOT**

The Blueprint is a high-quality **Sprint Plan**, but it is not yet a **Technical Specification**. It tells us *where* to go and *what* to fix, but it does not define the *destination architecture* with enough precision to ensure consistent, Temple-Grade implementation across the fleet.

**Recommendation**: Upgrade to **Sovereign Ark Blueprint v2.0** by incorporating the "Blind Spot" registry and the Expansion Roadmap before commencing Tier 2 work.

---
*⬡ OMEGA ⬡ MAKALI ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_blueprint_review ⬡ SOVEREIGN-SYNTHESIS*
