<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🧪 LAB: The Teammate Stack Adaptation
**Status**: PENDING
**Objective**: Experiment with the "Onboarding vs. Prompting" paradigm to enhance Omega Engine entity persistence and identity.

## 📝 The Concept
Instead of static system prompts, use a modular 8-file structure (Identity, Voice, Anti-Style, Context, Rules, Opening Move, Connectors, Leverage) to define an entity's soul. The core "magic" is the **Meta-Prompt Interview**, where the AI extracts this information from the user/entity through an iterative Q&A process.

## 🛠️ Experimental Hypothesis
By implementing a "Sovereign Onboarding" agent, we can generate high-fidelity `soul.yaml` entries that are far more accurate and "human" than manually written personas.

## 🧪 Lab Experiments
- [ ] **Experiment 0: Lab Curator Prototype**. Implementation of the background worker to automate Lab Commons reviews. (Prototype located at `labs/lab_curator/lab_curator.py`)
- [ ] **Experiment 1: The Meta-Interview**. Create a prompt that interviews a new entity to generate a draft `soul.yaml`.
- [ ] **Experiment 2: Modular Soul**. Split `soul.yaml` into the 8 Teammate Stack dimensions to see if it improves consistency and reduces drift.
- [ ] **Experiment 3: Anti-Style Enforcement**. Implement a "Banned Word/Tone" filter in the `ModelGateway` that references the "Anti-Style" file.

## 🔗 References
- Jeremy Utley's Teammate Stack
- `docs/strategy/SOVEREIGN_COMPRESSION_LAYER.md` (for condensing these files into context)
