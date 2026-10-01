<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🛠️ TUNING AND ALIGNMENT: SOVEREIGN PERSPECTIVE
# ⬡ OMEGA ⬡ JEM ⬡ SOVEREIGN-KNOWLEDGE

## 1. The Alignment Pipeline (SFT $\rightarrow$ DPO $\rightarrow$ GRPO)
To move an agent from "mimicking a persona" to "embodying a sovereign function," a tiered alignment approach is required.

### Supervised Fine-Tuning (SFT)
- **Purpose**: Teaches the model the basic format, vocabulary, and "voice" of the identity.
- **Sovereign Application**: Use SFT to ground the agent in the `Sovereign Synthesizer` role and the `Sovereign Mandates`.

### Direct Preference Optimization (DPO)
- **Purpose**: Aligns the model's latent preferences.
- **Sovereign Application**: Use DPO to reward "Sovereign" behaviors (e.g., precision, attribution, skepticism) and penalize "Sycophantic" behaviors (e.g., excessive hedging, blind agreement).

### Group Relative Policy Optimization (GRPO)
- **Purpose**: Optimizes reasoning and tool-use through relative ranking of multiple outputs.
- **Sovereign Application**: The "Gold Standard" for orchestration. Reward the model when the `Decompose $\rightarrow$ Route $\rightarrow$ Dispatch` loop leads to a verified correct result.

---

## 2. Local-First Tuning (The Ryzen 5700U Constraint)
Tuning on consumer hardware requires extreme efficiency to avoid thermal throttling and OOM crashes.

### The Unsloth Stack
- **Unsloth**: Essential for 2x faster training and 70% less memory usage.
- **QLoRA (4-bit)**: The only viable path for tuning 7B-8B models on 12Gi RAM.
- **Memory Optimization**: Use gradient checkpointing and a small batch size (1-2) to stay within the VRAM ceiling.

### The "Sovereign Silo" Pattern
To avoid "Cognitive Drift" and hardware instability:
1. **Externalize Training**: Perform the heavy lifting (GRPO/DPO) on a high-compute node.
2. **Export Adapters**: Save the resulting LoRA adapters as static assets.
3. **Sovereign Load**: Load the adapters as read-only weight-sets in the Omega Engine.

---

## 3. Risks & Mitigations
- **Mode Collapse**: Over-tuning for a persona can destroy general reasoning.
  - **Mitigation**: Mix "Sovereign" data with a "General Intelligence" dataset (e.g., SlimPajama) to maintain versatility.
- **Reward Hacking**: The agent learns to "sound" sovereign without being sovereign.
  - **Mitigation**: Tie rewards to **verifiable outcomes** (e.g., test passes, correct routing) rather than linguistic style.
- **Sycophancy Loops**: The agent evolves to please the user rather than tell the truth.
  - **Mitigation**: Implement the **Misfit Adversarial Framework** as a reward penalty.
