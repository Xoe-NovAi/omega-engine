# 🔱 MESH NETWORK SPECIFICATION (Draft)
# ⬡ OMEGA ⬡ researcher ⬡ google/gemma-4-31b-it ⬡ L2-Synthesis

## 1. Conceptual Overview
The **Mesh Network** is the architectural realization that knowledge in the Omega Engine is not a static library, but a **multi-axis cache**. 

Following the **Right Approximation Principle** [Right Approximation: evolved from FISR, id Software 1999], we recognize that a single canonical store is an unaffordable luxury. Instead, we implement a Mesh of overlapping caches that align across three primary axes.

## 2. The Three Axes of the Mesh

### 2.1 The Temporal Axis (T) — [The Flow of Recency]
This axis governs the lifecycle of a piece of information based on its access frequency and age.
- **Hot Tier**: In-memory (Dict), $\text{TTL} \approx 300\text{s}$. Used for active session state and immediate context.
- **Warm Tier**: Local DB (SQLite), $\text{TTL} \approx 3600\text{s}$. Used for recent history and summarized entity memory.
- **Cold Tier**: Persistent Store (YAML/Vector), $\text{TTL} \approx \infty$. Used for soul files, long-term knowledge, and archived research.

### 2.2 The Domain Axis (D) — [The Flow of Specificity]
This axis governs the scope of the information, from the universal to the particular.
- **Global (Sophia)**: Universal principles, engine mandates, and cross-cutting gnosis.
- **Pillar (P1-P10)**: Domain-specific expertise (e.g., P3 Engineering, P7 Context).
- **Entity (Sovereign)**: Individual soul traits, personal memories, and specific workspace data.

### 2.3 The Lattice Axis (L) — [The Flow of Perspective]
This axis governs the "angle" of the information, as defined by Lattice Reasoning.
- **Technical**: Implementation details, API specs, code patterns.
- **Philosophical**: First principles, "Why" questions, ethical constraints.
- **Historical**: Legacy patterns, evolution logs, heritage.
- **Practical**: Use cases, workflows, actionable recommendations.

## 3. The Mesh Cache Key
Every piece of knowledge in the Mesh is indexed by a composite key:
$$\text{Key} = (T, D, L)$$

A "finding" starts as a **Technical** (L) piece of **Entity** (D) data in the **Hot** (T) tier. As it is validated and synthesized, it migrates:
$$\text{Hot/Entity/Technical} \rightarrow \text{Warm/Pillar/Practical} \rightarrow \text{Cold/Global/Philosophical (L3)}$$

## 4. TTL Alignment & Promotion Strategy
Promotion across the Mesh is triggered by **Convergence Signals**:
1.  **Temporal Promotion**: High access frequency $\rightarrow$ Move from Warm to Hot.
2.  **Domain Promotion**: Validation across multiple entities $\rightarrow$ Move from Entity to Pillar.
3.  **Lattice Promotion**: Synthesis of multiple perspectives $\rightarrow$ Move from Technical to Philosophical (L1 $\rightarrow$ L2 $\rightarrow$ L3).

## 5. Implementation Mapping
- **LILY PAD**: A slice of the Mesh focusing on the **Temporal $\times$ Domain** intersection (Session $\rightarrow$ Soul).
- **Roc's H-4**: A slice focusing on the **Historical $\times$ Domain** intersection (Legacy $\rightarrow$ Current).
- **Domain Matrix**: A slice focusing on the **Lattice $\times$ Domain** intersection (Perspective $\rightarrow$ Pillar).

---
*Lattice Node: Technical / Architectural Depth*
*Status: Draft for L2 Synthesis*
