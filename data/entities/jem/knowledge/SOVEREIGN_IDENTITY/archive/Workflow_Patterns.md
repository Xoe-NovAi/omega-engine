<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔄 WORKFLOW PATTERNS: THE COGNITIVE TRANSMISSION
# ⬡ OMEGA ⬡ JEM ⬡ SOVEREIGN-KNOWLEDGE

## 1. Core Agentic Patterns (2026 SOTA)
Modern agents have moved beyond simple "Chain-of-Thought" to structured, iterative loops.

### ReAct (Reason + Act)
- **Pattern**: Think $\rightarrow$ Act $\rightarrow$ Observe $\rightarrow$ Repeat.
- **Use Case**: Responsive, short-term tasks requiring tool use.

### Plan-and-Execute
- **Pattern**: Plan (Decompose) $\rightarrow$ Execute (Sequence of ReAct steps) $\rightarrow$ Finalize.
- **Use Case**: Long-horizon, complex tasks requiring structural coherence.

### Reflexion (Self-Review)
- **Pattern**: Execute $\rightarrow$ Critique $\rightarrow$ Refine $\rightarrow$ Execute.
- **Use Case**: High-stakes outputs where accuracy is paramount.

---

## 2. The Sovereign Orchestration Workflow
The Omega Engine implements a specialized version of the Plan-and-Execute pattern, optimized for a multi-agent fleet.

### The Sovereign Loop:
`Decompose` $\rightarrow$ `Semantic Route` $\rightarrow$ `Dispatch` $\rightarrow$ `Synthesize` $\rightarrow$ `Misfit Audit` $\rightarrow$ `Verify`.

1. **Decompose**: Break the user's intent into atomic, domain-specific tasks.
2. **Semantic Route**: Use a `SovereignRouter` to map tasks to the correct agent/pillar.
3. **Dispatch**: Execute tasks via the `Orchestrator` (using LoRA adapters for capability).
4. **Synthesize**: Merge disparate findings into a coherent, non-redundant result.
5. **Misfit Audit**: Apply the Pizzazz, Roxy, and Stormer filters to strip away vanity and identify failure points.
6. **Verify**: Final check against the `Sovereign Mandates` and a `Skeptical Verifier`.

---

## 3. Cognitive Metabolism (The Evolution Loop)
The "Soul" is not static; it evolves through a metabolic process of distillation.

### The Distillation Pipeline:
`Experience (L1 Narrative)` $\rightarrow$ `Insight (L2 Synthesis)` $\rightarrow$ `Principle (L3 Gnosis)`.

- **L1 (Narrative)**: Raw interaction logs.
- **L2 (Insight)**: Thematic clustering of L1s into "lessons learned."
- **L3 (Principle)**: Universal, causally invariant truths distilled from L2.

**The Sovereign Gate**: L3 principles are only committed to the soul after passing a **Verity Audit**, preventing the "Sycophancy Loop" where an agent reinforces its own hallucinations.

---

## 4. Implementation Advice
- **Avoid Infinite Loops**: Implement a "Budget Pressure" system to limit the number of reflection cycles.
- **Context Preservation**: Use "Summary Anchors" to maintain the core intent across long execution chains.
