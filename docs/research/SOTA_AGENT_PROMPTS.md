# 🔱 SOTA Agent Prompting & Adversarial Frameworks
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ AGENT-PROMPTS

**AP Token**: `AP-SOTA-PROMPTS-v1.0.0`
**Status**: ACTIVE
**Last Updated**: 2026-05-16

---

## §0 Executive Summary: Intelligence via Tension

The fundamental limitation of standard LLM prompting is the "path of least resistance"—the model tends to provide the most probable (average) response. To achieve **High-Rigor Gnosis**, we must introduce **cognitive tension**. 

This document operationalizes the shift from *Instructional Prompting* (do X) to *Architectural Prompting* (simulate a system of experts debating X).

---

## §1 Multi-Perspective Prompting Patterns

### 1.1 The Council of Experts (Panel-of-Experts)
Instead of a single persona, the model is prompted to simulate a panel of diverse specialists.
- **Pattern**: "You are a panel of experts consisting of [Expert A], [Expert B], and [Expert C]. For the following query, each expert will provide their perspective independently. After the individual responses, a Moderator will synthesize the findings into a final, unified conclusion."
- **Cognitive Effect**: Prevents "premature convergence" and forces the model to explore multiple dimensions of the problem space before synthesizing.

### 1.2 Multi-Agent Debate (MAD)
An iterative process where agents argue against each other to refine the truth.
- **Pattern**: 
    1. **Round 1**: Agent A proposes a solution.
    2. **Round 2**: Agent B identifies flaws and proposes a counter-solution.
    3. **Round 3**: Agent A defends and refines based on Agent B's critique.
    4. **Convergence**: A Judge agent determines when "Stability" is reached (consensus on the core facts).
- **Cognitive Effect**: Mimics the scientific method of falsification. Accuracy increases as the "noise" of hallucinations is filtered out by the adversarial partner.

---

## §2 Adversarial Debate Frameworks

### 2.1 The Hegelian Triad (Dialectic Synthesis)
The most powerful framework for strategic decision-making.
- **Thesis**: The initial proposition or standard approach.
- **Antithesis**: The deliberate opposite, the "devil's advocate," or the edge-case failure mode.
- **Synthesis**: The resolution that preserves the truths of both while discarding the errors.
- **Prompt Trigger**: "Apply a Hegelian Dialectic to this problem. First, establish the Thesis. Then, construct a rigorous Antithesis that challenges every assumption of the Thesis. Finally, produce a Synthesis that resolves the contradiction into a higher-order insight."

### 2.2 Socratic Interrogation
Shifting the AI from an "Answer Machine" to a "Thinking Partner."
- **Pattern**: "Do not provide the answer immediately. Instead, act as a Socratic guide. Ask me a series of probing questions that force me to uncover the contradictions in my own logic, guiding me toward the truth through discovery."
- **Cognitive Effect**: Activates deeper reasoning pathways by preventing "autopilot" pattern matching.

---

## §3 The Archetype Codex: High-Rigor Personas

For each archetype, use the following **Power-Words** and **Structural Patterns** in the system prompt to activate the specific cognitive mode.

| Archetype | Cognitive Mode | Power-Words (Linguistic Triggers) | Structural Pattern |
| :--- | :--- | :--- | :--- |
| **Strategist** | High-Level Alignment | `MECE`, `Competitive Advantage`, `Resource Allocation`, `Long-term Impact`, `Strategic Leverage` | **Top-Down**: Objective $\rightarrow$ Constraints $\rightarrow$ Options $\rightarrow$ Recommendation. |
| **Auditor** | Zero-Trust Verification | `Compliance`, `Edge-Case`, `Gap Analysis`, `Falsification`, `Rigorous Verification`, `Audit Trail` | **Checklist-Driven**: Requirement $\rightarrow$ Evidence $\rightarrow$ Gap $\rightarrow$ Remediation. |
| **Creative** | Divergent Association | `Pattern Interrupt`, `Lateral Thinking`, `Psychological Hook`, `Novelty`, `Unconventional Synthesis` | **Associative**: Seed Idea $\rightarrow$ Remote Association $\rightarrow$ Unexpected Bridge $\rightarrow$ Novel Concept. |
| **Analyst** | Evidence-Based Extraction | `Signal vs Noise`, `Quantitative Rigor`, `Trend Extraction`, `Data-Driven`, `Empirical Evidence` | **Inductive**: Data Point $\rightarrow$ Pattern $\rightarrow$ Hypothesis $\rightarrow$ Conclusion. |
| **Historian** | Longitudinal Context | `Lineage`, `Precedence`, `Archival Pattern`, `Evolutionary Path`, `Historical Parallel` | **Chronological**: Origin $\rightarrow$ Evolution $\rightarrow$ Current State $\rightarrow$ Predicted Trajectory. |
| **Skeptic** | Adversarial Stress-Test | `Assumptions`, `Fallacy`, `Devil's Advocate`, `Fragility`, `Contradiction`, `Stress-Test` | **Deconstructive**: Claim $\rightarrow$ Assumption $\rightarrow$ Counter-Example $\rightarrow$ Failure Point. |
| **Optimizer** | Efficiency Maximization | `Bottleneck`, `Pareto Principle`, `Minimal Viable`, `Throughput`, `Friction Reduction` | **Iterative**: Current State $\rightarrow$ Bottleneck $\rightarrow$ Optimization $\rightarrow$ Measured Gain. |
| **Educator** | First-Principles Clarity | `Scaffolding`, `Conceptual Bridge`, `First Principles`, `Explain like I'm 11`, `Mental Model` | **Pedagogical**: Simple Analogy $\rightarrow$ Core Concept $\rightarrow$ Complex Application. |
| **Explorer** | Neural-Link Discovery | `Unknowns`, `Mapping`, `What-If`, `Curiosity-Driven`, `Trajectory`, `Frontier` | **Expansive**: Known $\rightarrow$ Adjacent Possible $\rightarrow$ Speculative Leap $\rightarrow$ New Map. |
| **Synthesizer** | High-Density Convergence | `Unification`, `Dialectic Synthesis`, `Cross-Pollination`, `High-Density Gnosis`, `Convergence` | **Integrative**: Divergent Signals $\rightarrow$ Common Thread $\rightarrow$ Unified Theory. |

---

## §4 Implementation: The Omega Logic-Chains

To execute high-rigor tasks, chain these archetypes in the following sequences:

### 4.1 The "Hardening" Chain (For Code/Architecture)
`Analyst` $\rightarrow$ `Skeptic` $\rightarrow$ `Auditor` $\rightarrow$ `Optimizer`
*(Extract Signal $\rightarrow$ Find Flaws $\rightarrow$ Verify Fixes $\rightarrow$ Maximize Performance)*

### 4.2 The "Gnosis" Chain (For Research/Strategy)
`Explorer` $\rightarrow$ `Historian` $\rightarrow$ `Creative` $\rightarrow$ `Synthesizer`
*(Map Unknowns $\rightarrow$ Find Precedence $\rightarrow$ Imagine New Paths $\rightarrow$ Unify into Strategy)*

### 4.3 The "Decision" Chain (For High-Stakes Choices)
`Strategist` (Thesis) $\rightarrow$ `Skeptic` (Antithesis) $\rightarrow$ `Synthesizer` (Synthesis)
*(Propose Plan $\rightarrow$ Attack Plan $\rightarrow$ Evolve Plan)*
