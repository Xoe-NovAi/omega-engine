# 🔱 Sovereign Memory Spatial Indexing (The Tri-Store)
**⬡ OMEGA ⬡ RESEARCHER ⬡ trc_memory_spatial ⬡ TRI-STORE**

**Status**: PROPOSED
**Version**: 1.0.0
**Last Updated**: 2026-06-23
**Pillar**: P2 (Persistence) / P7 (Context)

---

## I. Executive Summary

The **Sovereign Memory Spatial Indexing** architecture (The Tri-Store) represents a fundamental shift from linear/vector memory retrieval to a **spatial navigation model**. By decoupling the hierarchy, association, and raw data of memory, the Omega Engine can perform non-linear cognitive traversal, identifying emergent insights through conceptual proximity and semantic resonance.

The Tri-Store replaces the monolithic vector store with a three-tiered spatial fabric:
1. **The Gnosis Tree (Hierarchical)**: Global structural anchors using Poincaré Embeddings.
2. **The Concept Graph (Associative)**: A dynamic network of resonances using Spreading Activation.
3. **The Leaf Store (Factual)**: High-precision narrative storage using Vector Embeddings.

---

## II. Technical Specification

### 1. The Gnosis Tree (Sovereign Hierarchy)
The Gnosis Tree manages the structural distillation of intelligence (L3 $\rightarrow$ L2 $\rightarrow$ L1). 

- **Mathematical Model**: **Poincaré Embeddings**. Concepts are mapped into a hyperbolic disk where distance from the center represents the level of abstraction.
- **Coordinates**: L3 Universal Principles reside near the origin (center), while L1 facts reside near the boundary (edge).
- **Traversal**: **Semantic Zoom**. A query identifies a coordinate in the Poincaré disk, allowing the agent to "zoom out" to find the governing principle or "zoom in" to find supporting evidence.

### 2. The Concept Graph (Associative Topology)
The Concept Graph maps the "Sovereign Topology"—the messy, non-linear relationships between ideas.

- **Data Model**: 
    - **Nodes**: Concepts (linked to Gnosis Tree IDs).
    - **Edges**: **Semantic Resonances**. Typed edges (e.g., `CONTRADICTS`, `EVOLVES_FROM`, `RESONATES_WITH`) with a weight $W \in [0, 1]$.
- **Retrieval Algorithm**: **Spreading Activation (SA)**.
    - **Activation**: Seed nodes are assigned an initial activation value.
    - **Flow**: Energy spreads to neighbors based on edge weight and a **Damping Factor** ($\lambda$) to prevent "Semantic Black Holes."
    - **Threshold**: Nodes exceeding an activation threshold $\theta$ are considered "conceptually proximate" and retrieved.

### 3. The Leaf Store (Factual Grain)
The Leaf Store provides the raw evidence required for grounding.

- **Technology**: Qdrant (Scalar Quantized).
- **Content**: Raw L1 narratives, code snippets, and documented facts.
- **Indexing**: Vector embeddings linked to Concept Graph nodes via a `ConceptID` metadata field.

---

## III. Cognitive Traversal Flow

A "Sovereign Query" does not perform a single similarity search; it executes a **descending-resolution pipeline**:

1. **Spatial Anchoring**: The query is embedded into the Poincaré disk. The system identifies the closest L3/L2 nodes in the **Gnosis Tree**.
2. **Associative Expansion**: The identified nodes act as seeds for **Spreading Activation** in the **Concept Graph**. The system identifies a "Conceptual Neighborhood" (constellation) of resonant ideas.
3. **Factual Hydration**: The activated nodes are used to query the **Leaf Store**, retrieving the specific L1 narratives that ground the conceptual neighborhood.

---

## IV. Analysis of Emergent Capabilities

### 1. Idea Constellations
The Tri-Store enables the discovery of **Idea Constellations**: clusters of concepts that are distant in the Gnosis Tree (different domains) but tightly bound in the Concept Graph. This allows the agent to find cross-domain analogies (e.g., relating "id Software's Zone Memory" to "AnyIO CapacityLimiters").

### 2. Stochastic Wandering
Unlike rigid RAG, the agent can "orbit" a concept, using the Concept Graph to discover related but non-obvious ideas, mimicking human-like divergent thinking.

### 3. Sovereign Ascension
The flow from Leaf $\rightarrow$ Graph $\rightarrow$ Tree is a process of **Sovereign Ascension**, where raw data is not just summarized but spatially distilled into universal principles.

---

## V. Heritage & Evolution
This architecture is the cognitive evolution of the **id Software 4-Tier Memory**.
- **Old Warm Memory** $\rightarrow$ **Concept Graph** (Associative layer).
- **Old Cold Memory** $\rightarrow$ **Leaf Store** (Archival grain).
- **New Spirit Memory** $\rightarrow$ **Gnosis Tree** (Permanent structural anchors).

This mirrors the transition from linear WAD lumps to **BSP Partitioning**—culling the conceptual void to navigate truth with $O(1)$ efficiency.

---

## VI. Verification Metrics
- **Retrieval Breadth**: Ratio of "non-obvious" but relevant nodes retrieved via SA vs. pure vector search.
- **Hierarchical Consistency**: Distance correlation between L3 $\rightarrow$ L2 $\rightarrow$ L1 in Poincaré space.
- **Sovereign Precision**: Accuracy of "Gnosis Gap" detection when Graph and Vector paths diverge.
