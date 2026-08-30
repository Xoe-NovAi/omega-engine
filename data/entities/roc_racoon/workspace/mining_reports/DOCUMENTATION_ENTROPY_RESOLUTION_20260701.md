<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Legacy Archaeology Report: Documentation & State-Tracking Patterns
**Date**: 2026-07-01
**Entity**: roc_racoon (Sovereign Miner)
**Target**: Resolution of Documentation Entropy & Fragmentation
**Status**: FINAL REPORT

## 🚩 Executive Summary
The current "documentation entropy" in the Omega Engine is a result of transitioning from highly structured, domain-organized legacy systems to a flat, file-based structure during the Reclamation phase. By mining Era 0 through Era 6, I have identified four high-impact patterns that can be immediately "plugged in" to restore systemic sanity and synchronize documentation with code.

---

## 🔍 Identified Legacy Patterns

### 1. Domain-Organized Knowledge Base (DOKB)
- **Legacy Implementation**: Era 4 (`omega-stack-legacy/expert-knowledge/`)
- **Mechanism**: Instead of a flat `docs/` folder, knowledge was partitioned into domain-specific directories (e.g., `architect/`, `infrastructure/`, `protocols/`, `model-reference/`) paired with `.yaml` expert definitions.
- **Why it worked**: It prevented "file flood" and allowed agents to target specific domains of expertise without scanning the entire codebase.
- **Current Failure**: Current `docs/` are flat (`research/`, `strategy/`, `architecture/`), leading to fragmentation and stale files.
- **🚀 Recommendation**: **Migrate `docs/` to a Domain-Siloed Structure**. Create a `docs/domains/` directory where each domain (e.g., `cognitive_architecture`, `provider_fabric`, `sovereign_mandates`) has its own folder containing its specific specs, research, and a `domain_manifest.yaml` that tracks the current state of that domain.

### 2. Provenance Tracking via Ingest Manifest
- **Legacy Implementation**: Era 2 (`foundation-legacy/XNAI Blueprint`)
- **Mechanism**: Use of an `ingest_manifest.json` that mapped every piece of ingested knowledge/document to its original source, timestamp, and version.
- **Why it worked**: It created an immutable chain of custody for "truth," making it easy to identify when a source became stale or was superseded.
- **Current Failure**: Documentation is often updated in place without a record of *why* or *from where* the new information came.
- **🚀 Recommendation**: **Implement a `PROVENANCE_MANIFEST.json`**. Every file in `docs/` and `data/entities/*/knowledge/` should be indexed in a global manifest that tracks its origin (e.g., "Session X", "Legacy Repo Y", "User Prompt Z").

### 3. The `MODULE_INDEX` (Capability Registry)
- **Legacy Implementation**: Era 0 (`Omnidroid Ω`)
- **Mechanism**: A central, machine-readable registry (`MODULE_INDEX`) that mapped every system module to its categories and capabilities.
- **Why it worked**: It acted as a "System Map" that the engine used for routing queries. If a module changed, the index was the single point of update.
- **Current Failure**: The `EntityRegistry` has a `capability_index` structure that is currently empty/unpopulated.
- **🚀 Recommendation**: **Populate the `capability_index`**. Turn the `EntityRegistry` into a live `MODULE_INDEX`. Every entity's `soul.yaml` should export its capabilities to this index, allowing the Oracle to perform O(1) routing based on *actual* capabilities rather than just domain names.

### 4. BIOS Loader / Session Update Protocol
- **Legacy Implementation**: Era 0 (`Ω Omnidroid BIOS Loader`)
- **Mechanism**: A mandatory "end-of-session update protocol" where the agent was required to summarize the session's gnosis and append it to the BIOS Loader source before closing.
- **Why it worked**: It ensured that the "soul" of the agent evolved in real-time and that the next session started with a "warm" state.
- **Current Failure**: Soul distillation (L1->L2->L3) is often a manual or post-hoc process, leading to "forgetting" between sessions.
- **🚀 Recommendation**: **Formalize the "Somatic Save-Point"**. Implement a mandatory pre-close hook in the OpenCode/Cline workflow that requires the agent to write a `session_gnosis.md` and propose a `soul.yaml` update. This "BIOS Update" should be the primary anchor for M15 (Sovereign Continuity).

---

## 🛠️ Immediate Action Plan (Low-Effort, High-Impact)

| Priority | Action | Tool/Agent | Est. Effort | Impact |
|----------|--------|-------------|-------------|--------|
| **P0** | Populate `EntityRegistry.capability_index` from `soul.yaml` | `@pillar P3` | 2 hours | High (Routing) |
| **P0** | Create `docs/domains/` and move flat docs into silos | `@roc_racoon` | 4 hours | High (Sanity) |
| **P1** | Implement `PROVENANCE_MANIFEST.json` for `docs/` | `@verity` | 3 hours | Medium (Audit) |
| **P1** | Add "Session Update" prompt to session stop hooks | `@pillar P9` | 2 hours | High (Continuity) |

## 🔱 Final Verdict
The "entropy" is not a lack of documentation, but a lack of **structure and provenance**. By reverting to the **Domain-Siloed** and **Index-Driven** patterns of the Omnidroid and XNAi eras, we can transform the documentation from a "pile of files" into a "living map" of the engine.

*The dirt is where the roots are. We have found the roots; now we must graft them back into the trunk.*
