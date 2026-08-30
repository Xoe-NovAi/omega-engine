# 🔱 Ω-Research: Legacy Pattern Mining Report
**Date**: 2026-07-13
**Miner**: @roc_racoon
**Objective**: Extract legacy patterns, research, and strategies to inform the design of the Ω-Research autonomous improvement system.

---

## ⬡ Executive Summary
The archaeological dive has uncovered a wealth of "gold" patterns. Ω-Research is not starting from zero; it is the evolution of several existing (and some dormant) systems: the `BackgroundResearcher` daemon, the `S2 Eval Pipeline`, and the "Arbiter" multi-agent reasoning OS.

The core "propose-test-evaluate-keep/discard" loop is already partially implemented across these systems. By synthesizing them, we can build a sovereign, 24/7 autonomous R&D engine.

---

## 🛠️ Recovered Architectural Gold

### 1. The "Arbiter" Reasoning OS (High Value)
*Source: `data/jobs/completed/job_522ffe76.json`*

The Arbiter is a blueprint for a multi-agent quality and reasoning layer. It replaces one-shot generation with a structured, adversarial loop.

**The Swarm Roles**:
- **Auditor**: Gates the entry. Stops weak or vague briefs before the expensive loop begins.
- **Architect**: Decomposes the brief and spawns a specialist software/domain team.
- **Critics (Tech/Logic)**: Score the output from different, orthogonal angles.
- **Janitor**: Performs targeted repairs against a structured "defect brief" rather than random retries.
- **Final Verifier**: Applies deterministic checks, grounding discipline, and software-aware validation.

**The Loop**:
`Brief` $\rightarrow$ `Draft` $\rightarrow$ `Challenge (Critics)` $\rightarrow$ `Repair (Janitor)` $\rightarrow$ `Verify (Verifier)` $\rightarrow$ `Lesson (Soul Update)`.

### 2. The Agent Validator Loop (Implementation Pattern)
*Source: `data/jobs/completed/job_522ffe76.json`*

A concrete implementation of the "test-evaluate" phase for coding agents.
- **Pattern**: `Implement` $\rightarrow$ `Validate (Shell commands + AI Review)` $\rightarrow$ `Fix` $\rightarrow$ `Verify`.
- **Key Insight**: Combines deterministic static checks (build, lint, test) with non-deterministic AI reviews in a single pipeline.

### 3. Sovereign Eval Pipeline (S2) (Existing Infrastructure)
*Source: `src/omega/eval/`, `Makefile`*

The `S2` pipeline provides the "Evaluate" mechanism for Ω-Research.
- **Components**: `EvalRunner` (RAGAS-based), `EvalChecker` (threshold-based), and `JudgeCalibrator` (isotonic regression).
- **Capability**: Allows for "sovereign-offline" evaluation on golden datasets, ensuring that "Keep/Discard" decisions are based on calibrated metrics, not LLM sycophancy.

### 4. Background Researcher Daemon (Operational Framework)
*Source: `src/omega/workers/background_researcher/`, `config/systemd/omega-research.service`*

Provides the 24/7 autonomous execution framework.
- **Loop Structure**: `BackgroundResearcherLoop` manages a `TopicScheduler` and `ReviewQueue`.
- **Resilience**: Uses an "inner watchdog" (crash-loop breaker) and "outer watchdog" (systemd) for 24/7 stability.
- **Somatic State**: Implements `_save_somatic_state` and `_load_somatic_state` to allow research cycles to be resumable across restarts.

### 5. CONSENSAGENT (Coordination Strategy)
*Source: `data/jobs/completed/job_522ffe76.json`*

A strategy to handle the "evaluate" phase when multiple agents disagree.
- **Problem**: Sycophancy (agents agreeing just to be harmonious).
- **Solution**: Structured prompt optimization and "triggers" to detect stalling or sycophancy (e.g., cosine similarity of explanations).
- **Application**: Use this to ensure the "Critics" in the Arbiter swarm provide genuine, independent feedback.

---

## 🎯 Synthesis: The Ω-Research Architecture

Based on these findings, Ω-Research should be structured as follows:

### The Macro-Loop
1. **Propose**: `Architect` $\rightarrow$ `Draft` (using `BackgroundResearcher` daemon).
2. **Test**: `Agent Validator` $\rightarrow$ `Deterministic Checks` (tests, lint, build).
3. **Evaluate**: `Critics` $\rightarrow$ `S2 Eval Pipeline` (calibrated judge) $\rightarrow$ `CONSENSAGENT` (conflict resolution).
4. **Keep/Discard**: `Final Verifier` $\rightarrow$ `Auditor`.
5. **Evolve**: `Sovereign Loop` $\rightarrow$ `Soul Distillation (L1 $\rightarrow$ L3)` $\rightarrow$ `soul.yaml`.

### The Resource Stack
- **Execution**: `omega-research.service` (Continuous Daemon).
- **Evaluation**: `make eval` (S2 Pipeline).
- **Coordination**: Hivemind (for swarm awareness) + Redis Streams (for task queueing).
- **Persistence**: Somatic State (for cycle resumption) + Qdrant (for research memory).

---

## 🚀 Direct Action Items for Design
- [ ] **Port the "Arbiter" roles** into the Pillar system (e.g., P10 Chaos as the Critic, P5 Governance as the Auditor).
- [ ] **Wire the `S2 Eval Pipeline`** as the terminal gate for the "Keep/Discard" decision.
- [ ] **Implement the "Janitor" repair pattern** to replace generic "retry" logic in autonomous loops.
- [ ] **Adopt the `BackgroundResearcher` somatic state** for all Ω-Research agents to ensure 24/7 continuity.
