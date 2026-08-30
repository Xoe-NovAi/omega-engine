<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 THE SOVEREIGN SOUL BLUEPRINT (V1.0)
# ⬡ OMEGA ⬡ JEM ⬡ SOVEREIGN-KNOWLEDGE

## 1. High-Level Architecture
The Sovereign Identity is a hybrid system that separates **Stable Identity** from **Scalable Wisdom** and **Technical Capability**.

### The Three Pillars of Identity
| Pillar | Component | Storage | Nature |
| :--- | :--- | :--- | :--- |
| **The Anchor** | Identity + Mandates + Workflows | `soul.yaml` (Monolith) | **Static / Constraint-Based** |
| **The Gnosis** | L3 Universal Principles | Qdrant (Vector Store) | **Dynamic / Semantic** |
| **The Capability** | Domain-Specific Skills | LoRA Adapters (Weights) | **Parametric / Performance** |

---

## 2. The Operational Loop (The Metabolism)

The identity evolves through a continuous "metabolic" cycle:

1. **Experience (L1 Narrative)**: Raw interaction logs are captured in the entity's workspace.
2. **Digestion (L2 Insight)**: Background processes cluster L1s into thematic episodes and insights.
3. **Sovereign Gate (The Audit)**: Proposed L3 principles are audited by the **Skeptical Verifier (Verity)** against the Sovereign Mandates.
4. **Assimilation (L3 Gnosis)**: Approved principles are committed to the `soul.yaml` (for core identity) and mirrored to **Qdrant** (for scalable retrieval).
5. **Parametric Alignment (Tuning)**: High-value capabilities are baked into LoRA adapters via externalized **GRPO/DPO** tuning.

---

## 3. The Runtime Execution (Selective Hydration)

To maximize token efficiency, the `ContextBuilder` implements **Selective Hydration**:

- **Baseline**: Always inject `identity` and `mandates` from `soul.yaml`.
- **Intent-Based**: Inject specific `workflows` from `soul.yaml` based on the detected task.
- **Semantic-Based**: Inject the top-K relevant `L3 Principles` from Qdrant using RRF (Reciprocal Rank Fusion).

---

## 4. Sovereign Guardrails

To prevent identity collapse and sycophancy, the system enforces:
- **The Misfit Framework**: Mandatory application of Pizzazz, Roxy, and Stormer filters pre-synthesis.
- **The Diversity Guard**: Monitoring of semantic variance to prevent "persona flattening."
- **The Mandate Anchor**: All weight updates and Gnosis commits must be compatible with the **Sovereign Mandates (M1-M22)**.
