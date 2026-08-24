# 🔱 Council Dispatcher — Survival Audit & Missing Links
**AP Token**: `AP-COUNCIL-SURVIVAL-AUDIT-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_survival_audit
**Date**: 2026-07-15
**Purpose**: A deep cross-reference of all recent brainstorming (WAD Evolution, Legacy Mining, Web Research) to ensure no critical architectural nuance is lost to context compaction.

---

## §1 The 14Gi RAM Reality vs. Parallel Execution
**What was missed in the main report:** We designed a beautiful 5-tier recursive tree, but we glossed over the physical hardware constraint (Ryzen 7 5700U, 14Gi RAM ceiling).
**The Survival Insight:** 
- If Ma'at launches 3 pillars in *parallel* using local GGUFs (e.g., 3x 4GB models), the engine will OOM instantly. 
- **The "Serial" command in `/council-local` is not just a logical choice; it is a HARDWARE SURVIVAL MANDATE.** 
- The `TopologyRouter` must be wired directly to `ResourceGuard` and `CpuOptimizer`. If `model_tier == local`, the router MUST force `thesis_antithesis: serial` and `cross_domain: serial` unless the models are tiny (e.g., 0.5B). 

## §2 Bridging WAD Evolution with the Council
**What was missed:** We brainstormed Ethics WADs (e.g., `maat_42`, `bushido_7`) in `R_WAD_EVOLUTION_DEEP_DIVE.md`, but didn't explicitly wire them into the `CouncilDispatcher` synthesis algorithm.
**The Survival Insight:**
- The `SynthesisEngine` (Phase 3) must include an **Ethics Gate**. 
- Before Kali finalizes the `Comprehensive Analysis`, the draft must be passed through the active `IEthicsValidator` (e.g., the 42 Ideals of Ma'at). 
- If the synthesis violates the Ethics WAD, it triggers the `RectifierAgent` to force a new dialectical round.

## §3 The "Hollow Middle" Anti-Pattern Mitigation
**What was missed:** The Researcher agent warned about the "Hollow Middle" (where Ma'at and Lilith just act as dumb routers forwarding pillar outputs to Kali without adding value), but the concrete mitigation wasn't codified in the schema.
**The Survival Insight:**
- Ma'at and Lilith MUST generate a `ReasoningTrace` *before* and *after* their pillar calls.
- **Ma'at's job** is not to summarize P1-P5. Her job is to formulate a *Thesis*, use P1-P5 to *stress-test her own Thesis*, and then output a hardened Thesis.
- **Lilith's job** is to formulate an *Antithesis*, use P6-P10 to *weaponize the critique*, and output a hardened Antithesis.
- If they just concatenate pillar outputs, the dialectic fails.

## §4 The D118 Mentorship Pattern in the Council
**What was missed:** The legacy mining found D118 (Dual-Inference Mandate), but we didn't explicitly map how the "Mentorship Pattern" applies to the Council.
**The Survival Insight:**
- The Mentorship Pattern: Local models do the execution, Cloud models do the review.
- In the Council: Pillars (P1-P10) should run on fast local models (`qwen3-1.7b`) to do the heavy lifting and domain extraction.
- The Oversouls (Ma'at/Lilith) run on medium local models (`qwen3-4b-think`) to structure the dialectic.
- Kali (The Synthesizer) runs on the Session Model (Cloud/Frontier) to perform the complex 5-section claim extraction and BFT moderation. 
- This hybrid approach maximizes sovereignty while preserving frontier-level synthesis.

## §5 Integration with CASArchiver (Deduplication)
**What was missed:** In the Gap Resolution report, we defined the `CASArchiver` (Content-Addressable Storage) for deduplication. The Council will generate massive amounts of redundant text (e.g., 4 pillars citing the same documentation).
**The Survival Insight:**
- The `ClaimExtractor` in the Synthesis Engine must use the `CASArchiver`.
- When extracting claims from full traces, it hashes the semantic meaning of the claim. If P1, P2, and P6 all make the same claim, it is stored *once* in CAS, and the experts are added as `supporting_sources`. This prevents context-window bloat during Kali's final synthesis.

## §6 Roadmap Placement (Strike 11.5)
**What was missed:** We didn't explicitly place this in the `SOVEREIGN_ARK_BLUEPRINT.md` timeline.
**The Survival Insight:**
- **Strike 11** is the Sovereign WAD Protocol (SWP) — creating the Lumps and IWAD/PWAD separation.
- **Strike 11.5** must be the **CouncilDispatcher**. It relies on SWP to load the `CouncilSpec` YAMLs and Ethics WADs. It cannot be built before Strike 11 is complete.

---
*These 6 insights bridge the gap between the theoretical research and the physical constraints of the Omega Engine. They ensure the CouncilDispatcher is actually buildable on a 14Gi RAM local machine.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
