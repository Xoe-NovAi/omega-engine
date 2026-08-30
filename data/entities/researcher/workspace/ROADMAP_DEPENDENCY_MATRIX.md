<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 ROADMAP DEPENDENCY MATRIX — Sovereign Recon Phase
# ⬡ OMEGA ⬡ researcher ⬡ google/gemma-4-31b-it ⬡ Lattice-Node: Technical

## 1. Silent Dependency Analysis
Based on a traversal of `SOVEREIGN_EVOLUTION_ROADMAP.md` (v1.2), the following "silent" dependencies have been identified. These are tasks that are listed as independent but are functionally blockers for others.

| Blocker Task | Blocked Task | Nature of Dependency | Risk if Ignored |
|---|---|---|---|
| **H2-A1/A2** (Orphan Deletion & Audit) | **H2-F6** (INDEX.yaml) | Data Integrity: Cannot catalog entities if 100+ orphans still exist. | `INDEX.yaml` becomes a list of noise; entity routing remains fragile. |
| **H2-E2** (Thin Wrappers) | **H2-F8** (P7 Context Review) | Identity Architecture: Soul integrity cannot be validated if identity is hardcoded in `.md` files. | P7 review becomes a superficial check of text rather than a structural audit of `soul.yaml`. |
| **H3-A1** (Redis Pub/Sub) | **H2-E3/E5** (MaKaLi Council) | Runtime Stability: In-memory Hivemind (300s TTL) is too fragile for a production-grade parallel council. | Council sessions may "forget" participants or state mid-inference. |
| **H2-F7/F8/F9** (Cross-Pillar Reviews) | **H3-A5** (A2A Hardening) | Process Formalization: Current reviews are ad-hoc; A2A hardening provides the typed protocol for these reviews. | Reviews remain manual and non-reproducible. |

## 2. The True Critical Path to "Green"
To reach a stable, sovereign state where the MaKaLi Triad is fully operational and the data layer is clean, the execution order should be:

**Data Layer Cleanse** $\rightarrow$ **Identity Refactor** $\rightarrow$ **Infrastructure Hardening** $\rightarrow$ **Governance Lockdown**

1.  **H2-A1/A2** (Delete Orphans $\rightarrow$ Audit Entities)
2.  **H2-F6** (Generate `INDEX.yaml`)
3.  **H2-E2** (Convert Agents to Thin Wrappers)
4.  **H2-F8** (P7 Context Review of Soul Integrity)
5.  **H3-A1** (Wire Redis Pub/Sub for Hivemind)
6.  **H2-E3/E5** (Implement `/council-local` and `@makali`)
7.  **H2-F7/F9** (P5/P3 Pillar Reviews)

## 3. Convergence Signal
The need for `H3-A1` (Redis) to be moved "up" the priority list is a convergence signal. Both the `Sovereign Evolution Roadmap` and the `H3-A` priority (P0) indicate that the current in-memory Hivemind is a systemic bottleneck for all agent-to-agent (A2A) coordination.

---
*Lattice Node: Technical / Architectural Depth*
*Verified against: SOVEREIGN_MANDATES.md (M10 Fleet Integrity)*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: google/gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
