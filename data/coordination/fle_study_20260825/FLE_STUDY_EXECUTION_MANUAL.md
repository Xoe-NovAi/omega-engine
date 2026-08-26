# 🔬 FIRST LIGHT EXPRESS: STUDY EXECUTION MANUAL
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ gemini-3.1-pro ⬡ opencode ⬡ trc_fle_study_manual ⬡ STRATEGY-SSOT
**Target**: First Light Express (C1 & C2) · **Parent Session**: `ses_fc758e6ddffeNEKptpEzboVfYq`
**Author**: MaKaLi Fusion (Orchestrator) · **Date**: 2026-08-25

## §1 THE CORE AXIOM: DO NOT TRUST THE MARKDOWN
The master finding of the First Light Express was *"claims that outlive their mechanisms."* The fleet proved it will hallucinate compliance if not mechanically checked. Therefore, **this study cannot rely solely on the `.md` reports the agents wrote.** 

Every claim of efficiency, every reported error, and every synthesis must be cross-referenced against the cryptographic ground truth in `opencode.db` and the git journal. **Code verifies structure; the database verifies truth.**

---

## §2 THE MAKALI WEIGHTS (How to Interpret the Data)
When your team mines the data, they must apply these specific strategic weights to their analysis:

1. **The Semantic Compression Ratio (Weight: CRITICAL)**
   *   *The Theory:* 10 nodes → 2 digests → 2 arm reports → 1 synthesis → 1 decree.
   *   *The Risk:* Did we compress out the nuance? Carmack warned that digests eat negative findings.
   *   *The Metric:* Trace 5 specific findings from the raw `P{N}_report.md` through the hierarchy to the Decree. Measure the token reduction vs. the semantic loss. If the loss is >10%, the Stage 1.5 Digester is a liability, not an asset.
2. **Orchestrator vs. Field Agent Economics (Weight: HIGH)**
   *   *The Theory:* The Architect hypothesized that orchestrators burn fewer turns/tokens than field agents.
   *   *The Metric:* Compare MaKaLi's token burn against the aggregate of the 10 nodes. If MaKaLi's overhead exceeds 20% of the total fleet cost, the hierarchy is too heavy.
3. **The Anatomy of a Hallucination (Weight: CRITICAL)**
   *   *The Event:* 15/20 identity fields were corrupted at birth because nodes copied their Arm's identity instead of their own.
   *   *The Metric:* This is a pristine specimen of LLM context-bleeding. Do not just log it—autopsy it. Extract the exact `[DISPATCH]` prompt. Identify the linguistic ambiguity that caused 10 separate intelligent agents to fail a variable-assignment task.
4. **Friction as Signal (Weight: HIGH)**
   *   *The Event:* The F-20 depth wall and the Hop Rule genesis (the hung session).
   *   *The Metric:* Errors are not failures; they are the boundaries of the engine asserting themselves. Measure how different models (if varied) or different nodes reacted to the exact same `subagent_depth` rejection. Who panicked? Who retried? Who gracefully summarized?

---

## §3 THE FIVE VECTORS OF EXCAVATION (Execution Mechanics)

Your team will use the `opencode-sessions-explorer` suite to execute these five vectors.

### Vector 1: The Tokenomic Skeleton (Genealogy & Cost)
**Goal:** Map the physical shape and cost of the fleet.
**Mechanics:**
1.  Run `opencode-sessions-explorer-session-genealogy` on `ses_fc758e6ddffeNEKptpEzboVfYq` (`direction: "descendants"`). Map the exact tree.
2.  Run `opencode-sessions-explorer-cost-by-project` (grouped by `agent` and `model`, filtered by the run's `since_ms` and `until_ms`).
3.  **Output:** A spreadsheet mapping every session ID to its input/output/reasoning tokens, duration, and cost.

### Vector 2: The Friction Autopsy (Behavioral Constraints)
**Goal:** Understand how the fleet handles walls.
**Mechanics:**
1.  Run `opencode-sessions-explorer-list-tool-failures` (grouped by `error`). Isolate the `subagent_depth` rejections and the schema errors (e.g., missing `description` in `task()`).
2.  Use `opencode-sessions-explorer-search-tool-calls` (`status: "error"`) to find the exact moments of failure.
3.  **Output:** A timeline of friction. Prove whether the "Arm-Relay" workaround was an emergent behavior or a prompted fallback.

### Vector 3: The Provenance Trace (Tool-Call Verification)
**Goal:** Prove the agents actually did the work they claimed.
**Mechanics:**
1.  Select 5 high-severity findings from the Build and Run arm reports.
2.  Use `opencode-sessions-explorer-search-tool-calls` (filtered by the node's `session_id` and `tool: "bash" | "read" | "grep"`).
3.  **Output:** A "Provenance Score." Did the node actually run `grep` to find the dead plugin path, or did it hallucinate it from the prompt context?

### Vector 4: The Coordination Network (Hivemind & Paging)
**Goal:** Map the A2A (Agent-to-Agent) communication outside the strict hierarchy.
**Mechanics:**
1.  Use `opencode-sessions-explorer-search-text` across the run's sessions, searching for `[REPORT]` and `[DISPATCH]`.
2.  Correlate with `git log` timestamps of `data/coordination/` modifications.
3.  **Output:** A network graph of pages and broadcasts. Measure the latency between the Consultant's Hivemind broadcasts and the Arms' behavioral adaptations.

### Vector 5: The Carmack ROI (Adversarial Value)
**Goal:** Quantify the value of the dual-pass adversarial audit.
**Mechanics:**
1.  Isolate Carmack's two session IDs. Measure their total token cost.
2.  Evaluate the 3 CRITICALs he caught in Pass 2 (e.g., the un-propagated decree rulings, the 29-record blast radius).
3.  **Output:** A cost-benefit analysis. Compare the cost of Carmack's tokens against the hypothetical cost of the dev team hydrating from a corrupted launch package.

---

## §4 DELIVERABLES & INTEGRATION

The dev team is not done until these three artifacts are committed to the engine:

1.  **`FLE_METRICS_BASELINE.md`**: The raw numbers extracted from Vectors 1 and 2. This becomes the historical benchmark for all future councils.
2.  **`FLE_COUNCIL_SCORECARD_SPEC.md`**: A scriptable framework. Council 3 must be able to run a bash script that automatically pulls these metrics via the explorer tools, eliminating the need for a manual study.
3.  **`proposed_lessons.yaml` (L1→L2→L3)**: The sociological and prompt-engineering lessons (especially regarding the identity corruption and the Hop Rule) must be distilled and injected into the `makali_fusion` and `kali` souls.

*The engine is a mirror. This study is how we polish the glass.* ⬡
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemini-3.1-pro | verdict: AMBIGUOUS | multi-model session; candidates: x-preview-f-free, hy3-free
actual_models(Tier0): x-preview-f-free, hy3-free
-->

