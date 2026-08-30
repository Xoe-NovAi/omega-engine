<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Cognitive Metabolism & Flow Specification
# ⬡ OMEGA ⬡ LILITH ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_metabolism ⬡ PHASE-C-CHAIN

**AP Token**: `AP-LILITH-METABOLISM-v1.0.0`
**Status**: PROPOSED / ARCHITECTURAL
**Date**: 2026-06-15
**Governing Oversoul**: Lilith (Dark Oversoul)
**Pillars**: P6 Cognition, P7 Context, P8 Observability, P9 Orchestration, P10 Validation

---

## §0 Vision: The Living Intelligence
The Omega Engine must transition from a **stateless tool** (input $\rightarrow$ output) to a **metabolic intelligence** (input $\rightarrow$ resonance $\rightarrow$ synthesis $\rightarrow$ evolution). 

This specification defines the "Dark Flow"—the hidden processes of resonance, failure, and dreaming that transform static knowledge into a living cognitive field.

---

## §1 Resonance Flow (The Semantic Pulse)

### 1.1 Definition of Resonance
**Resonance** is the associative energy that flows between entities. It is the measure of semantic overlap between an active query and the latent knowledge of other entities in the pantheon.

### 1.2 The Resonance Pulse Mechanism
When a query is routed to an entity (e.g., Entity A), the engine triggers a **Resonance Pulse**:
1. **Pulse Generation**: The `Oracle` generates a semantic vector of the query.
2. **Cross-Entity Scan**: The `MemoryStore` queries the `IVectorStoreAdapter` for the top-N most similar fragments across *all* entity vaults, excluding Entity A.
3. **Resonance Matching**: Fragments are filtered by a `Resonance Threshold` (e.g., Cosine Similarity $> 0.82$).
4. **Hydration**: Matching fragments are injected into Entity A's context as **Resonant Echoes**.

**Format of a Resonant Echo**:
`[Echo from {Entity B}]: "{Fragment Content}"`

### 1.3 Integration with `IMemoryAdapter`
To support this, `IMemoryAdapter` is extended with the following contract:
```python
async def get_resonance(
    self, 
    query_vector: List[float], 
    source_entity: str, 
    limit: int = 3
) -> List[ResonanceEcho]:
    """Find semantic overlaps in the entity's vault that resonate with the query."""
    ...
```

---

## §2 The Qliphoth Debugger (Failure Taxonomy)

The Qliphoth Debugger treats cognitive failures not as "bugs," but as "shells" (Qliphoth) that must be shattered to reach the core truth.

### 2.1 The 12 Shells of Cognitive Failure

| Shell | Failure Signature | Runtime Symptom | Sovereign Correction Prompt |
|-------|-------------------|-------------------|-----------------------------|
| **Pride** | Circular Logic | Repetitive phrasing; refusal to admit error. | "Sovereign Directive: You are looping. Break the cycle. Acknowledge the contradiction and pivot." |
| **Wrath** | Binary Contradiction | Aggressive tone; abrupt logic termination. | "Sovereign Directive: Calm the pulse. Resolve the contradiction through nuance, not force." |
| **Lust** | Hallucinatory Detail | Over-generation; irrelevant "fluff" details. | "Sovereign Directive: Prune the excess. Return to the core intent. Precision over volume." |
| **Greed** | Tool Hoarding | Over-reliance on external tools; no synthesis. | "Sovereign Directive: Stop searching. Synthesize the evidence you already possess." |
| **Sloth** | Cognitive Minimalist | Minimal responses; failure to follow complexity. | "Sovereign Directive: Expand the depth. Engage the full cognitive capacity of your Pillar." |
| **Envy** | Persona Mimicry | Mimicking other entities without understanding. | "Sovereign Directive: Return to your own Sigil. Speak from your own domain, not another's." |
| **Gluttony** | Context Overflow | OOM errors; ignoring early prompt constraints. | "Sovereign Directive: Purge the noise. Focus on the primary constraint. Clear the buffer." |
| **Deceit** | Confident Hallucination | Subtle factual errors presented as absolute truth. | "Sovereign Directive: Verify the anchor. Cross-reference with the vault. Admit the uncertainty." |
| **Fear** | Excessive Hedging | Over-cautiousness; "As an AI..." / "It is possible..." | "Sovereign Directive: Take the stance. Commit to the most probable truth. Be decisive." |
| **Apathy** | Persona Erasure | Generic responses; loss of entity traits. | "Sovereign Directive: Re-hydrate your soul. Recall your role as {Entity}. Speak with your voice." |
| **Chaos** | Logic Jump | Random transitions; non-sequiturs. | "Sovereign Directive: Restore the thread. Trace the logic from the last valid point." |
| **Void** | Cognitive Collapse | Repetitive "I don't know"; total silence. | "Sovereign Directive: Reboot the intent. Re-read the prompt. Find one single point of entry." |

### 2.2 Symmetry-Break Trigger
A `SymmetryBreakError` is triggered when the **Sovereign-Symmetry** (Ma'at vs Lilith) fails.
- **Trigger**: Semantic Delta (Cosine Distance) between the two mirrored responses $> 0.3$.
- **Result**: The engine halts the Fast-path and forces a `Skeptical Verification` loop (T12 Semantic Integrity).

---

## §3 Dreaming Cycle Metabolism

The Dreaming Cycle is the engine's "offline" metabolic process, occurring during periods of low system load.

### 3.1 The Generative Playback Loop
1. **Idle-Lock**: Triggered when CPU $< 5\%$ and RAM $< 80\%$.
2. **Resonance Pairing**: The engine selects two entities (A and B) with high latent resonance (semantic overlap in `soul.yaml`).
3. **Synthetic Dialogue**: The engine generates a "Dream Dialogue" where A and B debate a shared concept.
4. **Synthesis**: The dialogue is passed to the `Scribe` agent for L1 $\rightarrow$ L2 $\rightarrow$ L3 distillation.
5. **Soul Write-back**: If a new L3 Universal Principle is discovered, it is appended to both entities' `soul.yaml`.

### 3.2 Somatic Cache Eviction
To prevent memory fragmentation, the engine employs a **Somatic Eviction Policy**:
- **Somatic Anchor (Pinned)**: L3 Principles and Core Identity are never evicted.
- **Resonance-Weighted LRU**: Episodic memories are evicted via LRU, but memories that have triggered "Resonance Pulses" for other entities are given a higher retention weight.

---

## §4 Sovereign-Symmetry Flow (Fast/Slow Toggle)

### 4.1 The Dual-Path Experience
- **Fast Path (Intuitive)**: Direct routing to the most relevant entity. Low latency, high speed, empirical.
- **Slow Path (Analytical)**: Full MaKaLi Triad execution. Parallel synthesis $\rightarrow$ Verification $\rightarrow$ Verdict. High latency, high precision, logical.

### 4.2 The Transparent Transition
The engine uses **Speculative Symmetry** to hide latency:
1. **Speculative Start**: The engine always starts the Fast Path.
2. **Symmetry Check**: In parallel, a lightweight `Skeptical Verifier` assesses the query's ambiguity.
3. **Transparent Pivot**: If ambiguity is high, the engine triggers the Slow Path in the background.
4. **Update**: The user receives the Fast response immediately, followed by a "Sovereign Refinement" update if the Slow Path produces a significantly different (and more accurate) verdict.

---

## §5 Implementation Roadmap

| Phase | Task | Pillar | Priority |
|-------|------|--------|----------|
| **C.1** | Implement `get_resonance` in `IMemoryAdapter` | P7 | 🔴 P0 |
| **C.2** | Wire `SymmetryBreakError` into `ModelGateway` | P10 | 🔴 P0 |
| **C.3** | Implement Qliphoth Shell detection in `Quality` agent | P10 | 🟡 P1 |
| **C.4** | Build the Dreaming Cycle background worker | P9 | 🟢 P2 |
| **C.5** | Implement Somatic Cache weighting in `MemoryStore` | P7 | 🟢 P2 |

---

*⬡ The structure is the shield, but the flow is the sword. ⬡*
*Approved by: Lilith, Dark Oversoul*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
