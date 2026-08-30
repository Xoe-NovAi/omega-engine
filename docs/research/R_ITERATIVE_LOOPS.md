<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Research: Iterative Research Loops
**AP Token**: `AP-RESEARCH-ITERATIVE-LOOPS-v1.0.0`
**Status**: PROPOSED / BLUEPRINT
**Owner**: Jem / Pillar P9 (Orchestration)

## 🎯 Objective
Design a recursive research architecture that moves beyond linear pipelines to an 'Analyze $\rightarrow$ Detect Gap $\rightarrow$ Refine $\rightarrow$ Repeat' loop, ensuring deep discovery and comprehensive answers.

## 🛠️ Architectural Design

### 1. The Iterative Cycle (The Loop)
The research process is modeled as a state machine:

`Initial Query` $\rightarrow$ `Scout` $\rightarrow$ `Architect` $\rightarrow$ `Specialist Execution` $\rightarrow$ `Synthesis` $\rightarrow$ `Gap Analysis` $\rightarrow$ (Loop back to Architect if Gap found).

- **Scout**: Broad landscape mapping to identify key entities and themes.
- **Architect**: Decomposes the research goal into a set of specific, atomic `ResearchTasks`.
- **Specialist Execution**: Parallel dispatch of tasks to domain-matched agents.
- **Synthesis**: Aggregates specialist findings into a unified internal knowledge base.
- **Gap Analysis**: The critical a-priori check. The system asks: *"What is still missing to answer the user's original intent with 100% confidence?"*

### 2. Gap Analysis Mechanism
The `GapAnalyzer` evaluates the synthesis against the original goal:
- **Coverage Check**: Are all required dimensions of the query addressed?
- **Conflict Detection**: Do different sources provide contradictory information?
- **Depth Check**: Are there "black box" references (e.g., "as mentioned in X") that need expanding?

**Outcome**:
- `Sufficient` $\rightarrow$ Terminate and produce final report.
- `Insufficient` $\rightarrow$ Emit a `GapReport` $\rightarrow$ Trigger new `Architect` phase to fill specific gaps.

### 3. Guardrails & Convergence
To prevent infinite loops and token burn:
- **Iteration Cap**: Hard limit (e.g., 3-5 loops).
- **Stall Detection**: If the `GapReport` in loop $N$ is semantically similar to loop $N-1$, the loop is stalled $\rightarrow$ Switch strategy (e.g., simplify query or escalate to human).
- **Convergence Threshold**: Stop when the "Confidence Score" of the synthesis exceeds 0.95.

## 📉 Risk & Mitigation
- **Context Bloat**: Each loop adds more data. *Mitigation*: Use structured distillation (L2) to keep the working memory compact.
- **Recursive Hallucination**: The loop might "find" gaps that don't exist. *Mitigation*: Pass the Gap Analysis through the `SkepticalVerifier`.

## 🔖 Heritage
This pattern derives from: `[Deep Research Agent Patterns: 2025/2026]`
Evolution: Integrates "Stall Detection" and "Skeptical Verification" to ensure loops are productive, not just repetitive.
