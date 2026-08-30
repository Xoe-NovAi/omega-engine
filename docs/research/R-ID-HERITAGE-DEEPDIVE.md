<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — id Software Heritage Deep Dive
**Document ID**: R-ID-HERITAGE-DEEPDIVE
**Status**: PROPOSED / VETTING
**Date**: 2026-06-11
**AP Token**: `AP-ID-HERITAGE-DEEP-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_heritage_deepdive ⬡ RESEARCH-MODE

## 🎯 Objective
To expand the Omega Engine's **Heritage Map** by identifying non-obvious architectural patterns from id Software (Doom, Quake, Quake III, Doom 3) and evolving them into "Right Approximations" for a modern, sovereign AI runtime.

---

## 🏛️ The Council's Dialectic

### 1. The Architect (Systemic Logic)
*"The challenge here is translation. id Software optimized for the Pentium's FPU pipeline and L1 cache. We are optimizing for LLM token latency and VRAM constraints. We cannot 'port' assembly; we must 'transmute' the intent. Any pattern proposed must align with Mandate 1 (AnyIO Absolute) and Mandate 2 (Engine-Stack Firewall)."*

### 2. The Adversary (Critical Rigor)
*"Beware the Cargo Cult. Just because John Carmack used a jump table in 1996 doesn't mean a Python dictionary is a 'Heritage Pattern'. We must prove that the original optimization solved a fundamental problem (e.g., branch mis-prediction, memory fragmentation) that still exists in our domain (e.g., prompt drift, provider latency). If it's just 'neat', it's noise."*

### 3. The Alchemist (Creative Synthesis)
*"I see the beauty in the 'In-Flight' overlap. If Abrash could hide an FDIV behind integer drawing, we can hide prompt construction and context hydration behind the GPU's inference of the previous token. The pattern isn't the instruction; it's the **asynchronous overlap of disparate cost-centers**."*

### 4. The Archivist (Historical Truth)
*"We must be precise. The 'Symmetric Range Check' wasn't just a trick; it was a necessity of the x86 instruction set of the era. When we document this, we must credit the specific era (e.g., Quake/Pentium) to ensure the lineage is traceable and the 'Right Approximation' is justified by the hardware constraints of the time."*

---

## ⚡ Proposed Heritage Patterns

### P1: The "In-Flight" Pipeline (Asynchronous Overlap)
- **Original (Quake/Abrash)**: Issuing a slow floating-point division (`FDIV`) for the *next* pixel span at the beginning of the *current* span. This allowed the CPU's integer pipelines to execute the current span while the FPU worked in the background.
- **Omega Adaptation**: **Speculative Context Hydration**. While the model is generating token $N$, the Engine proactively fetches and hydrates the context/memory for the predicted next segment or potential follow-up queries.
- **Right Approximation**: Precision is not required (prediction might be wrong), but the cost of a miss is low (discarded fetch) while the gain of a hit is a massive reduction in perceived latency.

### P2: Branch Collapse (Dispatch Table Routing)
- **Original (Quake)**: Using jump tables to avoid `if/else` chains and branch mis-predictions when handling the end of a pixel span.
- **Omega Adaptation**: **Flat-Map Intent Dispatch**. Replacing complex conditional routing logic in the Oracle with a strictly flat dispatch table of `IntentID -> Handler`.
- **Right Approximation**: Reduces cognitive complexity and ensures $O(1)$ routing regardless of the number of intents.

### P3: Symmetric Range Guard (Bitwise Range Check)
- **Original (Quake/Abrash)**: Using an unsigned comparison (`ja`) to check if a signed integer is *either* too high *or* below zero in a single operation.
- **Omega Adaptation**: **Symmetric Constraint Validation**. Implementing validation gates for entity traits or model parameters using bit-masking or symmetric checks to collapse multiple boundary tests into a single primitive.
- **Right Approximation**: Minimal CPU overhead for high-frequency validation gates.

### P4: Sovereign Job-Worker Queue (Cognitive Load Balancing)
- **Original (Doom 3 BFG)**: Decomposing engine tasks into "Jobs" (1k-100k cycles) distributed across "Worker" threads using atomic operations to avoid OS synchronization overhead.
- **Omega Adaptation**: **Atomic Cognitive Jobs**. Decomposing complex research tasks into atomic "Cognitive Jobs" with strict token/cycle budgets, distributed across a fleet of local and cloud models via the Hivemind.
- **Right Approximation**: Prevents "Model Hanging" and ensures a balanced load across the provider fabric.

### P5: Specialized Prompt Baking (The Self-Modifying Prompt)
- **Original (Quake/Abrash)**: Self-modifying code that "baked" colormap base addresses directly into the instruction stream at runtime to avoid register lookups.
- **Omega Adaptation**: **Persona-Fused System Prompts**. Instead of referencing a `soul.yaml` in every turn, the Engine "bakes" the distilled L3 principles and current session state into a specialized, fused system prompt at the start of a focused task.
- **Right Approximation**: Reduces the need for repeated context-window lookups and minimizes "persona drift" during long sessions.

### P6: Knowledge Leak Detection (Flood-Fill Logic)
- **Original (Doom 3)**: Using flood-fill algorithms to detect "leaks" in the map geometry (where the internal world touches the external void).
- **Omega Adaptation**: **Gnosis Leak Detection**. Using semantic "flood-filling" (traversing related concepts in the vector store) to identify contradictions or "holes" in an entity's knowledge base where logic "leaks" into inconsistency.
- **Right Approximation**: An automated way to find blind spots in the `soul.yaml` without exhaustive manual review.

---

## 🛠️ Heritage Vetting Matrix

| Pattern | Original Implementation | Omega Adaptation | Precision vs Cost | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **In-Flight** | FPU/Integer Overlap | Speculative Hydration | Low Precision / High Gain | ✅ **ADOPT** |
| **Branch Collapse**| Jump Tables | Flat-Map Dispatch | High Precision / Low Cost | ✅ **ADOPT** |
| **Symmetric Guard**| Unsigned $\text{ja}$ Check | Bitwise Validation | High Precision / Low Cost | 🟡 **VET** |
| **Job-Worker** | Atomic Job Queue | Cognitive Job Queue | Med Precision / High Gain | ✅ **ADOPT** |
| **Prompt Baking** | Self-Modifying Code | Fused System Prompts | Med Precision / Med Cost | ✅ **ADOPT** |
| **Leak Detection** | Geometry Flood-Fill | Semantic Gnosis Leak | Low Precision / Med Gain | ✅ **ADOPT** |

---

## 🚀 Integration Plan

1. **Update `CREDITS.md`**: Add the approved patterns to the Heritage Map.
2. **Implement `P2 (Branch Collapse)`**: Refactor Oracle routing to use strict Flat-Map dispatch.
3. **Implement `P4 (Job-Worker)`**: Formalize the `task()` delegation in the Hivemind as a "Cognitive Job" with budget constraints.
4. **Implement `P5 (Prompt Baking)`**: Create a `prompt_fusion` utility in the `ContextBuilder` to bake soul principles into task-specific prompts.
5. **Implement `P6 (Leak Detection)`**: Add a `gnosis-leak-check` tool for the `Scribe` to validate `soul.yaml` integrity.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
