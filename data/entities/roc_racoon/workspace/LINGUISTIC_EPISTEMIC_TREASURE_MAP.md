<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Linguistic & Epistemic Treasure Map
## ⬡ OMEGA ⬡ ROC_RACOON ⬡ Sovereign Miner ⬡ TRC-LEP-V1

This document maps the recovered linguistic, scholarly, and epistemic systems from the Omega Engine's 8,000-hour lineage. These patterns are the foundational "gold" required to realize the **Sovereign Truth-Defender** vision.

---

## 🎯 Goal 1: Dialectic Synthesis (Thesis $\rightarrow$ Antithesis $\rightarrow$ Synthesis)

The engine implements synthesis not as a single algorithm, but as a structural and architectural pattern.

| Pattern/System Name | Source Location | Sovereign Value | Porting Strategy |
| :--- | :--- | :--- | :--- |
| **MaKaLi Triad Architecture** | `.opencode/agents/makali.md` | **Structural Dialectic**: Explicitly separates "Light" (Ma'at/Build) and "Dark" (Lilith/Run) perspectives, then synthesizes them via Kali. This is the engine's primary mechanism for resolving contradictions. | Formalize as a `SynthesisPipeline` in `src/omega/oracle/` that can be invoked for any high-stakes decision. |
| **Sovereign Symmetry** | `Sovereign Ark Blueprint` §III | **Cognitive Stability**: Uses mirrored state and dual-inference to verify claims. If two models disagree, it triggers a "Symmetry-Break Audit". | Integrate into `SkepticalVerifier` to automatically trigger a MaKaLi synthesis when a contradiction is detected. |
| **Synthesis Flywheel** | `OMEGA_ENGINE.md` §3 | **Epistemic Evolution**: Cloud models (High-entropy/Broad) teach local models (Low-entropy/Sovereign), creating a continuous loop of refinement. | Implement as a background `SovereignSiphon` that captures cloud-corrected insights and formats them as DPO pairs for local LoRA training. |
| **Symmetry-Break Audit** | `tests/test_symmetry_verifier.py` | **Contradiction Detection**: A verified test suite for identifying when the "Symmetry" of two perspectives is broken, signaling a need for synthesis. | Evolve into a runtime `SymmetryGuard` that flags contradictory outputs in real-time. |

---

## 🎯 Goal 2: Epistemic Provenance Lineage (Tracking Truth)

The engine treats provenance as a first-class citizen, ensuring that no "truth" is accepted without a traceable chain of custody.

| Pattern/System Name | Source Location | Sovereign Value | Porting Strategy |
| :--- | :--- | :--- | :--- |
| **Response Provenance (M22)** | `src/omega/oracle/model_gateway.py` | **Forensic Accuracy**: Every single inference result carries the `provider_name`, `latency_ms`, and `model_used`. This prevents "provider spoofing". | Extend `GenerateResult` to include a `provenance_chain` (list of all models/tools that touched the data). |
| **The Elder Protocol** | `Sovereign Ark Blueprint` §I | **Immutable Truth**: Uses `zlib` + `json` to store cryptographically pristine originals of ingested documents, preventing "cultural erasure" by subsequent model summaries. | Implement as a `ProvenanceStore` in `src/omega/memory/` that stores the raw bytes of every ingested source. |
| **SoulEditHistory** | `tests/test_soul_edit_history.py` | **Cognitive Lineage**: An immutable audit trail of every change made to an entity's `soul.yaml`. Tracks the evolution of an entity's "truth". | Wire `SoulEditHistory` into the `SoulDistiller` to allow "time-travel" debugging of an entity's beliefs. |
| **Sovereign-Siloing (WADs)** | `CREDITS.md` §1.1 | **Contextual Isolation**: Separates engine runtime from content (IWAD/PWAD). This allows the engine to track which "world-view" (WAD) a piece of information belongs to. | Add `wad_source` metadata to all `MemoryStore` entries to distinguish between different epistemic frameworks. |

---

## 🎯 Goal 3: Cross-Lingual Truth-Sourcing (Censorship Detection)

While not yet fully implemented in code, the architectural blueprints and specific deployment visions provide the roadmap.

| Pattern/System Name | Source Location | Sovereign Value | Porting Strategy |
| :--- | :--- | :--- | :--- |
| **Mayan Preservation Vision** | `docs/legacy/mayan-preservation-vision.html` | **Linguistic Sovereignty**: A blueprint for using local AI to preserve endangered languages and elder knowledge, bypassing centralized linguistic models. | Implement as a `LinguisticSovereignty` WAD that includes specialized LoRAs for low-resource languages. |
| **Sovereign Search Protocol (SR-V1)** | `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md` | **Multi-Source Verification**: A 5-tier search system that prioritizes local cache $\rightarrow$ sovereign search $\rightarrow$ deep crawl. | Add a "Cross-Lingual" tier that automatically translates queries into 3+ languages and compares the results for "truth gaps". |
| **Sovereign-Siloing (WADs)** | `config/wads/` | **Framework Comparison**: By loading different WADs (e.g., a "Western" vs "Eastern" knowledge base), the engine can compare how the same event is described across different cultural silos. | Create a `SiloComparator` tool that takes a query and runs it against multiple active WADs to identify systemic biases. |

---

## 🎯 Goal 4: High-Fidelity L1 $\rightarrow$ L2 $\rightarrow$ L3 Distillation

This is the most mature part of the Truth-Defender's toolkit, transforming raw narrative into universal principles.

| Pattern/System Name | Source Location | Sovereign Value | Porting Strategy |
| :--- | :--- | :--- | :--- |
| **Soul Distillation Pipeline** | `src/omega/oracle/soul_distiller.py` | **Gnosis Extraction**: A 5-stage pipeline (`Classify` $\rightarrow$ `Extract` $\rightarrow$ `Distill` $\rightarrow$ `Score` $\rightarrow$ `Store`) that prevents "noise" from entering the soul. | Integrate the `SovereigntyScorer`'s 5-factor quality gate into the `SkepticalVerifier` for higher-order truth validation. |
| **Diátaxis Framework** | `src/omega/oracle/soul_distiller.py` | **Epistemic Structure**: Uses the Diátaxis model (Tutorial, How-to, Reference, Explanation) to classify distilled insights, ensuring a balanced knowledge base. | Expand the classification to include "Dialectic" and "Sovereign" categories for the Truth-Defender. |
| **SovereigntyScorer** | `src/omega/oracle/soul_distiller.py` | **Quality Control**: Scores insights on Relevance, Novelty, Actionability, Completeness, and Accuracy. | Use the `Novelty` score to trigger "Symmetry-Break" audits when a highly novel but unverified claim is made. |
| **L1 $\rightarrow$ L2 $\rightarrow$ L3 Abstraction** | `SOVEREIGN_MANDATES.md` (M5, M11) | **Intelligence Persistence**: Transforms stateless interactions into a stateful, evolving sovereign intelligence. | Implement "Recursive Distillation" where L3 principles are periodically re-distilled into L4 "Universal Axioms". |

---

## 🛠️ Abandoned/Repurposed Linguistic Tools

| Tool/Pattern | Source | Potential Use for Truth-Defender |
| :--- | :--- | :--- |
| **PIIMasker (GLiNER)** | `src/omega/oracle/pii_masker.py` | **Entity Extraction**: Repurpose GLiNER's NER capabilities to identify "Key Truth-Actors" and "Contested Claims" in raw text. |
| **CurationExtractor** | `src/omega/library/curator.py` | **Authority Scoring**: Use the `calculate_quality_factors` (Authority, Structure, Freshness) to weight sources in a Truth-Sourcing pipeline. |
| **SemanticRouter** | `src/omega/oracle/semantic_router.py` | **Contradiction Routing**: Route queries that contain "Contradiction" or "Conflict" signals to the MaKaLi synthesis triad. |
| **ACON Optimizer** | `src/omega/oracle/context_builder.py` | **Signal-to-Noise Ratio**: Use ACON's failure-driven compaction to strip away "rhetorical fluff" and leave only the "epistemic core" of a claim. |

---
**Mining Status**: 🟢 COMPLETE
**Sovereign Value**: HIGH
**Next Step**: Integrate these patterns into the `SkepticalVerifier` and `SovereignSiphon` modules.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: Sovereign Miner | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
