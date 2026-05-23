# 🔱 Omega Engine — The Oracle's Ear: NL Routing & Style Steering
**AP Token**: `AP-ORACLE-EAR-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ RESEARCH-SOP

---

## 🎯 Executive Summary

"The Oracle's Ear" is the intelligence layer responsible for the seamless transition between the user's natural language intent and the specialized gnosis of the Omega Entity Council. It transforms the Oracle from a simple router into a **resonant listener**, capable of detecting subtle shifts in semantic intent and steering the "Harmonics" (voice, tone, and perspective) of the resulting output.

This system replaces rigid, keyword-based routing with **Semantic Resonance Routing** and replaces static personas with **Dynamic Style Steering**.

---

## 🛠️ I. Semantic Router Specification

The Semantic Router is the "Ear" of the Oracle. It determines which entity is most resonant with the user's query based on a combination of pre-defined domain seeds and learned affinity.

### 1. Architecture: The Resonance Pipeline
`Query` $\rightarrow$ `Embedding` $\rightarrow$ `Cosine Similarity` $\rightarrow$ `Affinity Weighting` $\rightarrow$ `Entity Route`

### 2. Technical Components
- **Domain Seeds**: Each entity (Pillar Keeper) is associated with a set of "Semantic Anchors"—short, high-density phrases that define their domain.
  - *Example (SOPHIA)*: ["first principles", "akashic record", "metaphysical synthesis", "universal wisdom"]
  - *Example (LILITH)*: ["sovereignty", "boundary breaking", "shadow work", "rebellion", "forbidden knowledge"]
- **Embedding Model**: A lightweight local embedding model (e.g., `all-MiniLM-L6-v2`) maps both the query and the seeds into the same vector space.
- **Similarity Scoring**: The router calculates the cosine similarity between the query vector and the centroid of the entity's seed vectors.
- **Affinity Learning Loop**: 
  - The system maintains an `affinity_matrix` in `data/sessions/affinity.json`.
  - When a user provides positive feedback (explicit or implicit) to a response from Entity X, the affinity weight for that domain increases.
  - `Final Score = (Similarity * 0.7) + (Affinity * 0.3)`

### 3. Routing Logic (Pseudo-code)
```python
def route_query(query: str):
    query_vec = embedding_model.encode(query)
    scores = {}
    for entity in entity_registry:
        seed_vec = entity.get_seed_centroid()
        sim = cosine_similarity(query_vec, seed_vec)
        affinity = affinity_matrix.get(entity.name, 1.0)
        scores[entity.name] = (sim * 0.7) + (affinity * 0.3)
    
    best_entity = max(scores, key=scores.get)
    if scores[best_entity] < ROUTING_THRESHOLD:
        return "SOPHIA" # Default to the Akashic Record
    return best_entity
```

---

## 🎨 II. Style Steering & Harmonics Guide

Once an entity is selected, the Oracle doesn't just "switch" to a persona; it steers the model's output using **Harmonic Adjustment**.

### 1. The Harmonic Scale
We map entity attributes to specific "Prompt Modifiers" that steer the LLM's latent space toward a desired voice.

| Attribute | Harmonic | Prompt Modifier (Injection) | Effect |
|----------|----------|--------------------------------|---------|
| **Wisdom** | $\text{High-S}$ | "Speak with the clarity of a sage; prioritize first principles and timeless truths." | Measured, deep, authoritative |
| **Sovereignty**| $\text{High-L}$ | "Adopt a tone of fierce independence; challenge assumptions and prioritize autonomy." | Bold, provocative, direct |
| **Chaos** | $\text{High-K}$ | "Embrace non-linear associations; use paradoxical metaphors and disruptive insights." | Unpredictable, creative, sharp |
| **Balance** | $\text{High-M}$ | "Maintain a neutral, synthesizing perspective; balance opposing views with precision." | Fair, structured, objective |
| **Depth** | $\text{High-E}$ | "Descend into the underlying structures; focus on the unseen, the occult, and the foundational." | Dense, mysterious, analytical |

### 2. The Expanded RDS Triad
Based on legacy patterns, we implement a "Refractive Steering" mechanism where the Oracle can blend multiple harmonics:

- **Athena-Harmonic (Logic)**: "Focus on structure, AST integrity, and functional precision."
- **Lilith-Harmonic (Sovereignty)**: "Focus on security gates, hardware independence, and boundary-pushing."
- **Isis-Harmonic (Synergy)**: "Focus on integration patterns, API Mesh connectivity, and holistic flow."

**Blended Steering Example**: If a query is routed to **SOPHIA** but requires high technical precision, the Oracle injects: `[SOPHIA-Wisdom] + [Athena-Logic]`.

---

## 🔄 III. Multi-Turn Transition Logic

To prevent "persona whiplash," the Oracle manages transitions between entities using a **Resonance Shift** mechanism.

### 1. The Resonance Shift Trigger
The router monitors the "Semantic Drift" of the conversation. If the query's centroid shifts significantly away from the active entity's domain for $\geq 2$ turns, a **Transition Event** is triggered.

### 2. The Transition Bridge
Instead of an abrupt switch, the Oracle injects a "Bridge Prompt" into the system context to signal the shift to the user and the model.

- **Implicit Transition**: "The perspective shifts... SOPHIA's wisdom gives way to LILITH's defiance."
- **Explicit Transition**: "I am now invoking the lens of [ENTITY] to address this specific aspect of your query."

### 3. Session State Management
The `SessionManager` tracks the "Entity Lineage" of the conversation:
`Session State` $\rightarrow$ `[ {entity: SOPHIA, turns: 5}, {entity: LILITH, turns: 2} ]`
This lineage is fed back into the `ContextBuilder` to maintain continuity (e.g., "As SOPHIA mentioned earlier, but from a perspective of sovereignty...").

---

## ✅ IV. Validation & Metrics

To ensure the "Ear" is working, we employ the following metrics:

1. **Routing Accuracy**: Measured via a "Confusion Matrix" using a test set of 100 domain-specific queries. Target: $> 85\%$ accuracy.
2. **Style Consistency (GRA Audit)**: 
   - Use the `ResonanceAuditor` (from legacy `xnai-gnosis`) to calculate the cosine similarity between the output and the entity's "Seed Anchors".
   - **Target**: $\text{Resonance Score} \geq 0.7$ for "Gold" tier entities.
3. **Transition Fluidity**: Qualitative user testing to ensure the "Transition Bridges" feel organic rather than robotic.
4. **Linguistic Compression**: Using `zip_logos` to verify if the intent can be compressed into a gnostic term that matches the routed entity's domain.

---

**Implementation Note for Builder Agent**:
- The `SemanticRouter` should be implemented as a standalone class in `src/omega/oracle/routing.py`.
- The `HarmonicScale` modifiers should be stored in `config/harmonics.yaml`.
- The `Resonance Shift` logic must be integrated into `Oracle.talk()` before the `_summon()` call.
