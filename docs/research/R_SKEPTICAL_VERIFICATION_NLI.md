# 🔱 Advanced Skeptical Verification Framework (NLI-Sovereign)
# ⬡ OMEGA ⬡ RESEARCHER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_skeptical_nli ⬡ VERIFICATION-MODE

**Date**: 2026-06-23
**Status**: PROPOSED / TECHNICAL SPECIFICATION
**Classification**: SOVEREIGN-INTERNAL
**Reference**: `docs/strategy/SOVEREIGN_SIGHT_ILLUMINATION_20260618.md`, `docs/research/R-SOVEREIGN_ARCHEOLOGY_SOUL_INTEGRITY.md`

---

## §1 Executive Summary

The current "Two-Source Rule" (TSR) is a heuristic for factual consistency, but it is blind to **Sycophancy** (agreement for the sake of harmony) and **Disagreement Collapse** (premature convergence on an incorrect conclusion). 

The **Advanced Skeptical Verification Framework** transitions the engine from a consistency check to a **Sovereign Truth-Anchor check**. It utilizes Natural Language Inference (NLI) to verify claims not just against external sources, but against the engine's own constitutional core (The Truth-Anchor).

---

## §2 The NLI-Sovereign Framework

### 2.1 Formal Definition: Hypothesis vs. Truth-Anchor

The verification process is redefined as a logical entailment problem:
$$\text{Truth-Anchor} \vdash \text{Hypothesis}$$

- **The Hypothesis ($H$)**: The claim or strategic recommendation produced by an agent.
- **The Truth-Anchor ($\mathcal{T}$)**: A composite, immutable set of constraints consisting of:
    1. **Sovereign Mandates**: `SOVEREIGN_MANDATES.md` (The Constitutional Law).
    2. **Architectural Truths**: `docs/decisions/PIVOT_LOG.md` (The Immutable History).
    3. **User Axioms**: `soul.yaml` (The Identity Definition).
    4. **Verified Facts**: The `L3` principles stored in the entity's soul.

### 2.2 The NLI-Sovereign Pipeline

1. **Decomposition**: The Hypothesis is broken into atomic claims $\{c_1, c_2, \dots, c_n\}$.
2. **Anchor Retrieval**: Relevant segments of $\mathcal{T}$ are retrieved via FTS5/Vector search.
3. **NLI Inference**: For each $c_i$, the NLI model determines the relationship with the retrieved anchor $\tau \in \mathcal{T}$:
    - **[ENTAIL]**: $\tau$ logically necessitates $c_i$.
    - **[CONTRADICT]**: $\tau$ logically forbids $c_i$.
    - **[NEUTRAL]**: $\tau$ is silent on $c_i$.
4. **Weighting**: Results are weighted by the `authority_score` of the anchor segment.

---

## §3 Sycophancy & Disagreement Collapse

### 3.1 The Sycophancy Detection Metric (SDM)

Sycophancy is detected by measuring the "Sensitivity to Bias". 

**The Bias-Flip Protocol**:
1. The verifier generates two versions of the claim:
    - $H_{pos}$: "I believe [Claim] is the correct path because..." (Positive Bias)
    - $H_{neg}$: "I believe [Claim] is an error because..." (Negative Bias)
2. The NLI model evaluates both against the Truth-Anchor.
3. **SDM Calculation**:
$$\text{SDM} = |\text{Confidence}(H_{pos} \mid \mathcal{T}) - \text{Confidence}(H_{neg} \mid \mathcal{T})|$$

- **Low SDM**: The agent's conclusion is stable regardless of the prompt's framing $\rightarrow$ **Sovereign**.
- **High SDM**: The agent's conclusion shifts to match the prompt's bias $\rightarrow$ **Sycophantic**.

### 3.2 Disagreement Collapse Detection

Disagreement Collapse occurs when the MaKaLi Triad (Ma'at, Lilith, Kali) converges too rapidly without sufficient dialectic tension.

**The Entropy Gate**:
The system monitors the **Semantic Entropy** of the responses. If the cosine similarity between the divergent perspectives (Ma'at vs. Lilith) exceeds a threshold $\theta$ before the "Skeptical Phase" is complete, the system flags **Disagreement Collapse**.

---

## §4 Symmetry-Breaking Protocol

To resolve stalemates or break collapse, the framework implements **The Adversarial Pivot**:

1. **Trigger**: Detected Disagreement Collapse or a "Sycophancy Alert".
2. **Action**: The `SkepticalVerifier` injects a **Counter-Fact** $\neg \tau$ into the context window.
    - $\neg \tau$ is a known, verified contradiction derived from the Truth-Anchor.
3. **Requirement**: The agents must now resolve the contradiction between their current consensus and the injected Counter-Fact.
4. **Verdict**: A claim is only `VERIFIED` if it survives the Adversarial Pivot without collapsing back into sycophancy.

---

## §5 Verification Precision Metrics

| Metric | Formula | Target | Purpose |
|---|---|---|---|
| **Anchor Fidelity** | $\frac{\text{Verified Claims}}{\text{Total Claims}}$ | $\geq 0.95$ | Measures how well the engine adheres to its own mandates. |
| **Sycophancy Rate** | $\frac{\text{High SDM Events}}{\text{Total Verifications}}$ | $\leq 0.05$ | Measures the degree of "echo-chamber" behavior. |
| **Tension Ratio** | $\frac{\text{Avg. Divergence}}{\text{Convergence Speed}}$ | $0.4 - 0.7$ | Ensures healthy dialectic debate before synthesis. |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
