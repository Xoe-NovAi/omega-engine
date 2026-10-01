# 🔱 R-ITERATIVE-RESEARCH: Loop Patterns & Gap Analysis
**Status**: FINAL (Temple-Grade)
**Orchestrator**: makali
**Date**: 2026-06-11
**Sovereign Mandate**: M13 (Temple-Grade), M4 (Sequentiality)

## 🎯 Objective
Establish a formal framework for "Deep Research" that moves beyond single-pass RAG into iterative, self-correcting cognitive loops. The goal is to ensure comprehensive coverage of complex queries by explicitly identifying and filling knowledge gaps.

## 🛡️ The Iterative Research Loop (IRL)

### 1. The Core Cycle: Perceive $\rightarrow$ Evaluate $\rightarrow$ Adjust
The research process is a control loop, not a pipeline. Each iteration follows this sequence:
1. **Perceive (Search/Fetch)**: Execute a set of targeted queries. Gather raw evidence from web, local library, and memory.
2. **Evaluate (Gap Analysis)**: Compare the current `Findings` set against the `Initial Goal` and `Sub-questions`.
3. **Adjust (Refine/Pivot)**: Generate new, targeted queries specifically designed to fill the identified gaps.

### 2. Structured Evidence Assessment (SEA)
To prevent "fluent hallucination" (where an LLM creates a narrative that hides gaps), the engine must use a **Checklist-based Assessment**:
- **Decomposition**: Break the main research goal into a checklist of required atomic facts $\{F_1, F_2, \dots, F_n\}$.
- **Mapping**: Map retrieved evidence to the checklist.
- **Gap Identification**: Explicitly list which $F_i$ are:
    - ✅ **Confirmed**: Evidence is sufficient and corroborated.
    - ⚠️ **Partial**: Some information exists, but precision or detail is lacking.
    - ❌ **Missing**: No evidence found.
- **Signal**: The list of `Partial` and `Missing` facts becomes the direct input for the next iteration's query generation.

## 📐 Advanced Loop Patterns

### 1. Breadth vs. Depth Expansion
- **Breadth (Parallel Expansion)**: Spawn multiple parallel sub-agents to explore different facets of a query simultaneously.
- **Depth (Recursive Refinement)**: For a specific gap, recurse deeper into the source (e.g., follow a citation chain or crawl a specific sub-directory).

### 2. Generation-Augmented Retrieval (GAR)
Use the current (potentially incomplete) answer as a "bridge" to find better evidence:
- **Pattern**: $\text{Query}_{t+1} = f(\text{Question}, \text{Answer}_t, \text{Gaps}_t)$.
- **Benefit**: Later queries are informed by the terminology and concepts discovered in earlier rounds, bridging the "semantic gap" between the user's query and the technical evidence.

### 3. Evidence-Based Pruning
To prevent context window pollution:
- **Relevance Grading**: Each retrieved chunk is graded (e.g., 0-3).
- **Pruning**: Only chunks with grade $\ge 2$ are passed to the synthesis stage.
- **Skeptical Filtering**: If a new piece of evidence contradicts a previous one, both are flagged for "Conflict Resolution" (see MaKaLi synthesis role).

## 🚀 Operational Workflow for Omega Agents
1. **Plan**: Decompose the goal into a checklist of atomic requirements.
2. **Loop**:
    - **Search**: Execute queries $\rightarrow$ Fetch content $\rightarrow$ Extract facts.
    - **Evaluate**: Update checklist $\rightarrow$ Identify gaps.
    - **Stop Condition**: Stop when all $F_i$ are `Confirmed` OR `max_iterations` is reached.
3. **Synthesize**: Compile the final report using only the `Confirmed` evidence, explicitly noting any `Missing` facts as "Known Unknowns".

## 🛠️ Implementation Checklist for Omega Engine
- [ ] Implement `ResearchChecklist` class to track atomic fact status.
- [ ] Create `GapAnalyzer` module to generate targeted follow-up queries.
- [ ] Integrate `SkepticalVerifier` (R-SKEPTICAL-VERIFICATION) into the `Evaluate` phase.
- [ ] Add `max_depth` and `max_breadth` configurations to the research agent.
- [ ] Implement a `SovereignResearchReport` template that explicitly lists "Confirmed" vs "Unknown" findings.
