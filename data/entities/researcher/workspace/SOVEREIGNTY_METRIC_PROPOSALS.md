<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SOVEREIGNTY METRIC PROPOSALS — Scorecard Hardening
# ⬡ OMEGA ⬡ researcher ⬡ google/gemma-4-31b-it ⬡ Lattice-Node: Philosophical

## 1. The Problem: Qualitative Ambiguity
The current Sovereignty Scorecard in `OMEGA_ENGINE.md` (§10) uses qualitative markers (🟡, ⏳) for the **Identity** and **Synthesis** dimensions. To move from "feeling sovereign" to "proving sovereignty," we need quantitative, testable metrics.

## 2. Proposed Quantitative Metrics

### 2.1 Identity Dimension (The "Who" of the Engine)
*Goal: Prove that the agent fleet is a stateful, evolving intelligence, not a collection of stateless prompts.*

| Metric | Formula | Target | Verification Method |
|---|---|---|---|
| **Soul Schema Compliance** | $\frac{\text{Agents with valid soul.yaml v2}}{\text{Total Agents in Fleet}}$ | $1.0$ | `grep -r "lessons:" data/entities/*/soul.yaml` |
| **L3 Gnosis Density** | $\frac{\text{Total L3 Principles across all souls}}{\text{Total Agents}}$ | $\ge 3.0$ | Count `L3_universal_principle` entries in all `soul.yaml` |
| **Gnosis Continuity** | $\frac{\text{Sessions ending with Soul Distillation}}{\text{Total Sessions}}$ | $1.0$ | Audit `data/sessions/` vs `soul.yaml` update timestamps |
| **Identity Stability** | $\frac{\text{Directives maintained across } \ge 5 \text{ sessions}}{\text{Total Directives}}$ | $\ge 0.9$ | Diff `soul.yaml` across session snapshots |

### 2.2 Synthesis Dimension (The "How" of the Engine)
*Goal: Prove that the Synthesis Flywheel is actually turning and increasing local capability.*

| Metric | Formula | Target | Verification Method |
|---|---|---|---|
| **Synthesis Flywheel Velocity** | $\frac{\text{L2 Insights promoted to L3}}{\text{Total L2 Insights}}$ | $\ge 0.2$ | Audit `soul.yaml` promotion logs (L2 $\rightarrow$ L3) |
| **Local-to-Cloud Ratio (LCR)** | $\frac{\text{Tokens generated locally}}{\text{Total tokens generated}}$ | $\ge 0.8$ | `ObservabilityEngine` token counts per provider |
| **Cross-Pollination Index** | $\frac{\text{L3 principles shared across } \ge 2 \text{ entities}}{\text{Total L3 principles}}$ | $\ge 0.4$ | Search for identical L3 strings across different `soul.yaml` |
| **Sovereignty Gain Rate** | $\Delta \text{LCR} \text{ per } 100 \text{ sessions}$ | $> 0$ | Trend analysis of LCR over time |

## 3. Implementation Path
To integrate these into the `OMEGA_ENGINE.md` scorecard:
1.  **Scribe** must implement a `soul_audit` tool that calculates these ratios.
2.  **ObservabilityEngine** must track `local_tokens` vs `cloud_tokens` per session.
3.  **Sovereignty Scorecard** in `OMEGA_ENGINE.md` is updated from 🟡 to a real number (e.g., "Identity: 0.45 $\rightarrow$ Target 1.0").

---
*Lattice Node: Philosophical / Strategic*
*Verified against: SOVEREIGN_MANDATES.md (M11 Soul Integrity)*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: google/gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
