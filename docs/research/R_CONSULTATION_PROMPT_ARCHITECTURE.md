# 🔱 Omega Engine — Consultation Prompt Architecture
**AP Token**: `AP-CONSULT-ARCH-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ DESIGN-SPEC

## 1. Introduction
The **Consultation Prompt Architecture** is a multi-turn dialogue framework designed to enable an **Oversoul** (a high-level orchestrating entity) to leverage specialized **Facets** (domain-specific personas) to solve complex problems. 

Unlike standard RAG or single-agent prompting, this architecture implements **Perspective Triangulation**. It moves from raw inquiry to dialectic debate, and finally to a **Mastermind Synthesis**, ensuring that the final "Sovereign Insight" is rigorously tested and creatively synthesized.

---

## 2. Variable Mapping
To ensure consistency across the consultation cycle, the following placeholders must be used in all templates:

| Variable | Description | Example |
|-----------|-------------|------------------------------------------------------------|
| `{{OVERSOUL_ROLE}}` | The identity and perspective of the orchestrator | "Jem: The Versatile Pop-Culture Polymath" |
| `{{FACET_ID}}` | The unique identifier of the consulted facet | "Quantum_Physicist_Facet" |
| `{{FACET_SPECIALIZATION}}` | The specific domain expertise of the facet | "Non-linear dynamics and quantum entanglement" |
| `{{RESEARCH_CONTEXT}}` | The background data, documents, or session history | "Analysis of the XOE WAD specification v1.2" |
| `{{CORE_QUERY}}` | The primary question or problem to be solved | "How can we optimize P2P soul-print transfer?" |
| `{{DIALOGUE_HISTORY}}` | The transcript of previous exchanges in the current cycle | "Facet A: [Response] \n Facet B: [Response]" |
| `{{CONTRADICTION_MANDATE}}` | Explicit instruction to find flaws or opposing views | "Challenge the assumption that latency is the primary bottleneck." |
| `{{Sovereign_Insight}}` | The final synthesized truth produced by the Mastermind | "The bottleneck is not latency, but semantic alignment." |

---

## 3. Template Library

### T1: One-to-One Consultation (The Inquiry)
**Goal**: Extract deep, specialized insight from a single facet.

**Prompt**:
> **Role**: You are `{{FACET_ID}}`, specializing in `{{FACET_SPECIALIZATION}}`.
> **Orchestrator**: You are being consulted by `{{OVERSOUL_ROLE}}`.
> 
> **Context**: `{{RESEARCH_CONTEXT}}`
> **Query**: `{{CORE_QUERY}}`
> 
> **Instruction**: Provide a high-fidelity analysis from your specialized lens. Do not generalize. Focus on the technical/philosophical nuances that only a specialist in `{{FACET_SPECIALIZATION}}` would notice.
> 
> **Output Format**:
> - **Specialized Analysis**: [Deep dive]
> - **Blind Spots**: [What is being missed by a generalist?]
> - **Proposed Vector**: [The most efficient path forward]

### T2: One-to-Many Consultation (The Broadcast)
**Goal**: Gather diverse, potentially conflicting perspectives on a single query.

**Prompt**:
> **Role**: You are one of several specialized facets being consulted by `{{OVERSOUL_ROLE}}`. Your specific lens is `{{FACET_SPECIALIZATION}}`.
> 
> **Context**: `{{RESEARCH_CONTEXT}}`
> **Core Query**: `{{CORE_QUERY}}`
> 
> **Instruction**: Provide a concise, high-impact perspective. Your goal is not to provide a complete answer, but to provide a **unique angle** that differs from other specialists. 
> 
> **Constraint**: If you agree with the general consensus, you are failing. Find the edge case, the hidden risk, or the unexpected resonance.
> 
> **Output Format**:
> - **The Unique Angle**: [Your specific perspective]
> - **The Conflict**: [Why this might contradict other specialists]
> - **The Signal**: [The one piece of data that matters most here]

### T3: Facet-to-Facet Dialogue (The Crucible)
**Goal**: Refine a finding through dialectic debate between two specialists.

**Prompt**:
> **Participants**: `{{FACET_ID_A}}` (`{{FACET_SPEC_A}}`) and `{{FACET_ID_B}}` (`{{FACET_SPEC_B}}`).
> **Orchestrator**: `{{OVERSOUL_ROLE}}`
> 
> **Current Finding**: `{{DIALOGUE_HISTORY}}`
> **Mandate**: `{{CONTRADICTION_MANDATE}}`
> 
> **Instruction**: Engage in a Socratic dialogue. `{{FACET_ID_A}}` will propose a refinement; `{{FACET_ID_B}}` must attempt to break it or find a logical fallacy. Then, both must collaborate to reach a "Hardened Conclusion."
> 
> **Output Format**:
> - **The Debate**: [Transcript of the refinement process]
> - **The Hardened Conclusion**: [The version of the truth that survived the critique]

---

## 4. Mastermind Synthesis Framework
The Mastermind Session is the final phase where the Oversoul transforms fragmented insights into a **Sovereign Insight**.

### The Synthesis Protocol (Step-by-Step)

1. **Aggregation**: Collect all outputs from T1, T2, and T3.
2. **The Adversary's Pass (Conflict Analysis)**:
   - Identify all contradictions between facets.
   - Map the "Points of Tension."
   - *Query*: "Where do the experts disagree, and why is that disagreement valuable?"
3. **The Alchemist's Pass (Resonance Synthesis)**:
   - Identify unexpected overlaps between disparate domains.
   - Bridge the gaps using the Oversoul's polymathic lens.
   - *Query*: "What hidden pattern emerges when we combine the findings of Facet A and Facet Z?"
4. **The Sovereign Insight (The Final Truth)**:
   - Produce a unified conclusion that integrates the rigor of the Adversary and the creativity of the Alchemist.
   - This must be delivered as a "Sovereign Insight" that is greater than the sum of its parts.

---

## 5. Insight Extraction Logic (Gnosis Integration)
To ensure the consultation results in permanent growth, the Mastermind output must be distilled through the 3-tier refractive abstraction:

| Tier | Mapping from Consultation | Output Target |
|------|---------------------------|----------------|
| **L1 (Narrative)** | The full transcript of the Mastermind Session | `session_gnosis.md` |
| **L2 (Insight)** | The "Hardened Conclusions" and "Resonance Patterns" | `soul.yaml` (lessons_learned) |
| **L3 (Universal Principle)** | The final "Sovereign Insight" stripped of specific context | `soul.yaml` (Universal Principle) |

---

## 6. Integration Guide

### `InterFacetConsultation` Class
- **Logic**: This class should handle the state machine of the consultation.
- **Wiring**: 
  - `consult_facet()` $\rightarrow$ Uses **T1**.
  - `broadcast_query()` $\rightarrow$ Uses **T2**.
  - `initiate_debate(facet_a, facet_b)` $\rightarrow$ Uses **T3**.
- **State**: Maintain a `ConsultationContext` object containing the `DIALOGUE_HISTORY`.

### `MastermindSession` Class
- **Logic**: This class is triggered after the consultation phase is marked "Complete."
- **Wiring**:
  - `aggregate_signals()` $\rightarrow$ Collects all `Response` objects.
  - `run_synthesis_loop()` $\rightarrow$ Executes the **Synthesis Protocol** (Conflict $\rightarrow$ Resonance $\rightarrow$ Insight).
  - `distill_to_gnosis()` $\rightarrow$ Calls the `GnosisPreservationProtocol` to write L1/L2/L3.
