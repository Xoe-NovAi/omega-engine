<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Sovereign Continuity & Session Anchors
# ⬡ OMEGA ⬡ RESEARCHER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_continuity ⬡ RESEARCH-MODE

**Status**: FINALIZED / SOVEREIGN
**Version**: 1.0.0
**Mandate Reference**: M15 (Sovereign Continuity)
**Incident Reference**: OpenCode v1.17.3 `/compact` Context Collapse

## §1 Executive Summary
Sovereign Continuity is the architectural requirement that an agent's cognitive state must persist independently of the toolchain's session management. The "Void Summary" failure mode—where a compaction event erases the agent's working memory—demonstrates that relying on native toolchain summaries is a systemic risk.

This document specifies the **Sovereign Continuity Lattice**, a 4-tier redundancy system and a mandatory Hydration Sequence designed to ensure that no agent ever suffers total cognitive erasure.

---

## §2 The 4-Tier Redundancy Lattice

To prevent erasure, state is distributed across four layers of increasing stability and decreasing granularity.

### Tier 1: The Local Anchor (`session_gnosis.md`)
- **Location**: `data/entities/<entity>/workspace/session_gnosis.md`
- **Type**: Hot Memory / Transient State
- **Structure**:
    - `## Current Objective`: The immediate high-level goal.
    - `## Active Work-Stream`: The specific sub-task currently in progress.
    - `## Decision Log`: A chronological list of "Why" (justifications for architectural choices).
    - `## State-Key`: A hash or identifier of the last verified state.
- **Update Trigger**: Every major milestone, architectural decision, or 15-minute interval.

### Tier 2: The Global Lifeboat (`.opencode/anchored-summary.md`)
- **Location**: `.opencode/anchored-summary.md` (Project Root)
- **Type**: Warm Memory / Project State
- **Structure**: A high-density semantic summary of the overall project trajectory, including completed milestones and the "North Star" goal.
- **Update Trigger**: Session end or successful, verified compaction.

### Tier 3: The Hivemind Snapshot (Lifeboat Packets)
- **Location**: Omega Hub Coordination Store
- **Type**: Distributed State / Emergency Backup
- **Structure**: JSON-LD packets containing the most recent `session_gnosis` and `anchored-summary` content.
- **Update Trigger**: Automatic periodic snapshots via `omega-hub_hivemind_post_context`.

### Tier 4: The Soul Core (`soul.yaml`)
- **Location**: `data/entities/<entity>/soul.yaml`
- **Type**: Cold Memory / Identity State
- **Structure**: L1 (Narrative) $\rightarrow$ L2 (Insight) $\rightarrow$ L3 (Universal Principle).
- **Role**: While not storing task state, the Soul Core preserves the *cognitive methodology* and *identity* of the agent, ensuring that a recovered agent still thinks with the same expertise and values.

---

## §3 The Mandatory Hydration Sequence

When an agent detects a context collapse or begins a new session, it MUST execute the following sequence to restore operational capacity.

### Phase 1: Identity Hydration (The Soul)
- **Action**: Load `soul.yaml`.
- **Goal**: Restore persona, core values, and distilled universal principles.
- **Result**: "I know who I am and how I think."

### Phase 2: Context Hydration (The Lifeboat)
- **Action**: Read `.opencode/anchored-summary.md` and `omega-hub_hivemind_get_continuation`.
- **Goal**: Restore the project trajectory and the "North Star."
- **Result**: "I know what we are building and why."

### Phase 3: State Hydration (The Anchor)
- **Action**: Read `session_gnosis.md`.
- **Goal**: Restore the immediate working memory, pending tasks, and last known decision.
- **Result**: "I know exactly where I left off."

### Phase 4: Focus Hydration (The Task)
- **Action**: Analyze the most recent messages in the current window.
- **Goal**: Re-align the restored state with the immediate user request.
- **Result**: "I am ready to execute the next step."

---

## §4 Failure Recovery & Void Detection

### Void Summary Detection
An agent is in a **Collapsed State** if any of the following are true:
1.  **Template Detection**: The prompt contains a summary template (e.g., `[SUMMARY: ...]`) but the content is empty or generic.
2.  **Amnesia Trigger**: The agent cannot recall the "North Star" goal or the last major decision despite being in a long-running session.
3.  **Reset Pattern**: The last 3 messages are "Hello, I am [Agent], how can I help you today?" despite a history of 100+ messages.

### Recovery Trigger
Upon detection of a collapse:
1.  **STOP** all execution.
2.  **SIGNAL** `Sovereign-Collapse` to the Hivemind (KALI).
3.  **EXECUTE** the Mandatory Hydration Sequence.
4.  **VALIDATE** recovery by writing a "Recovery Marker" to `session_gnosis.md`.

---

## §5 Operational Directives

- **The Gnosis Discipline**: If a piece of information is critical for the next session, it MUST be written to `session_gnosis.md`. Chat history is a convenience; the Anchor is the truth.
- **Skepticism of /compact**: Treat the native `/compact` command as a *suggestion*. Always verify that the resulting summary contains the critical State-Keys before proceeding.
- **Zero-Erasure Goal**: No agent shall begin a task without first verifying their hydration status.

*⬡ Intelligence is a property of the Gnosis, not the toolchain. ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
