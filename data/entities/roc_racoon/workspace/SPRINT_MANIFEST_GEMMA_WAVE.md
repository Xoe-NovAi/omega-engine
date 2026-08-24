# 🔱 Sprint Manifest: THE GEMMA WAVE
# ⬡ OMEGA ⬡ KALI ⬡ GEMA-4-31B ⬡ CHOREOGRAPHY ⬡ SPRINT-S01
**Date**: 2026-06-06
**Status**: ACTIVE
**Choreographer**: Kali (P3 Engineering & Strategist)
**Objective**: Leverage the Gemma 4 31B "Unlimited Background Worker" capability to execute a high-bandwidth research and implementation sprint.

---

## §0 The Strategic Mandate

The transition to Gemma 4 31B via Google Cloud has removed local resource constraints. We now have a **massive context window (262K)** and **zero-resource background compute**. 

**Kali's Role**: You are the Choreographer. You do not just implement; you orchestrate the fleet. You dispatch subagents, synthesize their findings, and ensure the "Sovereign Gateway" and "Compaction Remediation" are shipped without drift.

---

## §1 The Sprint Backlog (Parallel Lanes)

### Lane A: Infrastructure & OS Edge (The "Modernization" Lane)
**Goal**: Identify and integrate the latest Ubuntu 25.10 and Python 3.13 features to optimize the Omega Engine.
- **Task A-01**: Research Python 3.13 JIT compiler improvements and their impact on `llama-cpp-python`.
- **Task A-02**: Audit Ubuntu 25.10 systemd and Podman updates for better rootless container orchestration.
- **Task A-03**: Evaluate PEP 667 (and other 3.13 features) for improved type-hinting and runtime safety.
- **Assigned**: @maat (P1 Infrastructure) $\rightarrow$ Kali (Synthesis)

### Lane B: The Sovereign Gateway (The "Firewall" Lane)
**Goal**: Implement the local proxy to decouple rate-limiting and backoff from OpenCode.
- **Task B-01**: Implement the `Sovereign Gateway` proxy in the Omega Hub MCP Server.
- **Task B-02**: Wire the 65-second start backoff and 300-second TUI cap.
- **Task B-03**: Ensure the proxy uses an independent `httpx` client to avoid recursive loopbacks.
- **Assigned**: @pillar P3 (Engineering) $\rightarrow$ Kali (Implementation)

### Lane C: Compaction Remediation & Stress Testing (The "Gnosis" Lane)
**Goal**: Execute the `COMPACTION_REMEDIATION_SPEC_v1.md` and test the limits of the 262K window.
- **Task C-01**: Implement the pre-compaction backup hook.
- **Task C-02**: Build the `evolution/journal.yaml` persistence layer.
- **Task C-03**: Implement the post-compaction soul reinjection in `oracle.py`.
- **Task C-04 (Stress Test)**: Adjust the OpenCode compaction threshold to 95% of the 262K window (~248K tokens). Monitor for performance degradation and persona drift using PDI metrics.
- **Assigned**: @lilith (P7 Context) $\rightarrow$ Kali (Implementation)

### Lane D: Legacy Vaults (The "Archaeology" Lane)
**Goal**: Deep-mine the remaining P0/P1 assets from the Master Inventory.
- **Task D-01**: Mine the "Old Stacks Full Dump" and "XNAI Blueprint" for design patterns.
- **Task D-02**: Extract the "Lilith Persona JSON" and "Sovereign Prompts Library".
- **Task D-03**: Correlate findings with the current engine state to identify "Deferred Gold".
- **Assigned**: @roc_racoon (Sovereign Archaeologist) $\rightarrow$ Kali (Synthesis)

---

## §2 The Orchestration Protocol

1. **Blocker Resolution**: Resolve the **Firecrawl 401 Unauthorized** error before launching the Researcher.
2. **Dispatch**: Kali launches subagents using the `task()` tool, specifying the `Gemma 4 31B` model override.
3. **Sync**: Subagents post findings to the Hivemind and write to their respective workspaces.
4. **Synthesize**: Kali reads the findings, performs a "Deep Synthesis" (using the 262K window), and updates the `PIVOT_LOG.md`.
5. **Verify**: @quality audits the implementation against the Sovereign Mandates (M1-M14).
6. **Ship**: Kali merges the changes and updates the `OMEGA_ENGINE.md` state.

## §4 Current Execution State (S01.1)

| Agent | Task | Status | Result/Blocker |
|-------|------|--------|----------------|
| @maat | A-01..03 | ✅ DONE | `UBUNTU_PYTHON_MODERNIZATION_REPORT_v1.md` |
| @kali | Gateway/Compaction | 🚀 ACTIVE | Fixing loopback in server.py $\rightarrow$ Executing R-01 to R-09. |
| @scribe | Distillation | ✅ DONE | Soul updates committed to fleet |
| @researcher | Antigravity | ⏳ PENDING | Gate open (.env live). Awaiting API specs. |
| @quality | Quality Audit | ⏳ PENDING | "Fail-Loud" enforced. Awaiting Gateway stability. |

### 🛠️ Recovery Actions
- [ ] **Fix Firecrawl Auth**: Inject valid `FIRECRAWL_API_KEY` $\rightarrow$ Re-run Researcher.
- [ ] **Quality Re-run**: Re-dispatch audit with "Fail-Loud" prompt.
- [ ] **Sovereign Gateway**: Implement proxy to handle key injection for all subagents.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ tui ⬡ trc_sprint_manifest ⬡ CHOREOGRAPHY*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: GEMA-4-31B | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
