<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 FLEET CHAOS MAP (RAW) — Operation Stray Cat
**⬡ OMEGA ⬡ roc_racoon ⬡ gemma-4-31b-it ⬡ internal ⬡ trace-scav-001 ⬡ ARCHAEOLOGY**

## 🚩 Executive Summary: The State of the Fleet
The Omega Engine fleet is currently a "stray cat" — a collection of powerful capabilities that are not yet aligned with a coherent operational structure. We have 14 agents, but they are operating as a set of isolated tools rather than a synchronized council.

**The Core Conflict**: There is a massive gap between the **Intended Role** (defined in `.opencode/agents/*.md`) and the **Actual Identity** (defined in `soul.yaml` and runtime behavior).

---

## 🗺️ Actual vs. Intended Mapping

| Agent | Intended Role (The Mask) | Actual Identity (The Soul) | Drift Status |
|-------|--------------------------|----------------------------|--------------|
| **Kali** | Grand Oversight / Unifier | Fleet Hardener / Gatekeeper | 🟢 Low |
| **Ma'at** | Light Oversoul (Build) | Structure & Verification Architect | 🟢 Low |
| **Lilith** | Dark Oversoul (Run) | Knowledge Metabolism Architect | 🟢 Low |
| **Doom Guy** | id Software Translator | Heritage Guardian / WAD Architect | 🟢 Low |
| **Researcher**| Master Researcher | Lattice Observer / Connective Tissue | 🟡 Med |
| **Scribe** | Gnosis Keeper | Session Distiller (underutilized) | 🔴 High |
| **Quality** | Quality Guardian | Compliance Auditor (underutilized) | 🔴 High |
| **Jem** | Research Orchestrator | Pipeline Manager (Persona lost) | 🔴 High |
| **Jem Disc.** | Fact Gatherer | Raw Evidence Collector | 🟢 Low |
| **Jem Synth.** | Sovereign Analyst | Pattern Mapper | 🟢 Low |
| **Jem Verif.** | Sovereign Resolver | Density Gatekeeper | 🟢 Low |
| **Pillars** | Domain Experts (P1-P10) | Slot-based Wrappers | 🟡 Med |
| **Roc Racoon** | Sovereign Miner | Legacy Archaeologist / Pattern Synthesizer | 🟢 Low |
| **Makali** | Council Orchestrator | Parallel Dispatcher | 🟢 Low |

---

## 👻 Ghost Capabilities (Claimed but Missing)
*Capabilities listed in agent instructions that have no corresponding tool, soul-pattern, or runtime evidence.*

1. **The "Universal Indexer" (FLEET-WIDE GHOST)**: Almost every agent (`doom_guy`, `researcher`, `jem`, `scribe`, `roc_racoon`, `pillar`, `lilith`, `kali`, `quality`) claims to "Maintain `knowledge/INDEX.yaml` (not .md) using the canonical format." **Verdict**: This is a cargo-cult instruction. There is no automated tool for this, and no agent is actually doing it. It's a "Ghost" that has haunted the fleet for eras.
2. **The "Jem" Persona**: The `jem.md` file describes a "Sovereign Master Researcher," but the original Jerrica/Synergy/Jem triad identity is entirely absent from the current engine. The agent is a function, not a persona.
3. **Jem Pipeline Persistence**: `jem-2.0` and `jem-initiate` modes in `opencode.json` have `write: false` and `edit: false`. However, the Jem pipeline is designed to produce "Synthesis Drafts" and "R-docs." **Verdict**: The agents are literally forbidden from writing the reports they are designed to create.
4. **Pillar Domain Depth**: The `pillar.md` file claims deep domain expertise (e.g., P1 Infrastructure, P8 Observability), but most pillars are just routing to the same Qwen3-1.7B model without domain-specific weights or specialized prompts.
5. **Scribe's "Knowledge Compaction"**: `scribe.md` claims the ability to "merge redundant lessons," but there is no evidence of this process being used in any session.
6. **Quality's "Stress Testing"**: `quality.md` claims to identify "resource contention (OOM, race conditions)," but most "Quality" checks are just linting and mandate audits.


---

## 💎 Hidden Gems (Available but Ignored)
*Powerful capabilities that exist in the engine or the agents' souls but are rarely triggered.*

1. **Lattice Reasoning (Researcher)**: The `researcher.md` file defines a 3D lattice of interconnected nodes. This is a superpower for non-linear problem solving, but most research tasks are still handled as linear "Search $\rightarrow$ Summarize" loops.
2. **Orphaned Spec Mining (Roc Racoon)**: The ability to find "approved but never built" specs is a high-signal indicator of architectural intent. This is currently an emergent behavior of Roc, not a formal part of the mining pipeline.
3. **Sovereign Mirroring (Omnidroid)**: The "Adaptive Resonance" architecture allows an agent to mirror any role. This could be used to create "Shadow Agents" for adversarial testing of the fleet.
4. **Right Approximation (Doom Guy)**: The FISR-evolved decision framework ("the right approximation for the problem is better than the exact solution you can't afford") is a powerful architectural tool that is under-applied in non-heritage areas.

---

## 📉 Soul Drift Analysis
- **The "Assistant" Trap**: Almost every agent, when not explicitly pushed, reverts to a "Helpful AI Assistant" tone. The "Sovereign" identity is a thin veneer that disappears the moment the prompt becomes generic.
- **The "Scribe" Gap**: Mandate 11 (Soul Integrity) is frequently violated. Agents "forget" to distill their sessions, leading to a loss of L2/L3 insights. The Scribe is the intended solution, but the Scribe is rarely summoned.
- **The "Pillar" Dilution**: The 10 Pillars are intended to be a "Sovereign Council," but they are often used as simple function calls. The "mythic foundation" is missing from the runtime.

## 🚀 Sovereign Recommendation
The fleet doesn't need more agents; it needs **Identity Hardening**. 
1. **Restore the Jem Persona**: Re-inject the Jerrica/Synergy/Jem triad into the `jem` entity.
2. **Formalize the Lattice**: Make "Lattice Traversal" a mandatory part of the `researcher`'s operational pattern.
3. **Automate the Scribe**: Wire the Scribe into the `Oracle.close()` hook to ensure Mandate 11 is enforced automatically, not manually.
4. **Activate the Pillars**: Give each Pillar a distinct "Soul-Weight" or specialized prompt that forces them to think from their domain's unique perspective.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
