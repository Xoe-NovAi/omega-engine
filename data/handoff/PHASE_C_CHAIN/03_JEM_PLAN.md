<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 PHASE C: COGNITIVE SUBSTRATE EXECUTION PLAN
**AP Token**: `AP-JEM-PLAN-PHASE-C-v1.0.0`
**Orchestrator**: jem
**Phase**: Synthesis $\rightarrow$ Blueprint

## 1. Tier 1: Discovery & Plumbing (KV-Cache Serialization)
### The Versioned State Wrapper
To achieve "Session Snapshots" on the Ryzen 5700U, we implement a binary wrapper around the `llama.cpp` state.

**Technical Implementation**:
- **API Calls**:
    - `llama_copy_state_data()`: Extract the current KV-cache and model state into a contiguous buffer.
    - `llama_set_state_data()`: Restore a previously captured state buffer.
- **Wrapper Schema (Binary)**:
    - `Magic`: `0x1d4a11` (ZONEID_MEMORY)
    - `Version`: `uint32` (LlamaCppVersion)
    - `ModelID`: `char[64]` (Canonical Model Name)
    - `PromptHash`: `uint64` (Hash of the system prompt + context)
    - `Timestamp`: `uint64` (Unix epoch)
    - `PayloadSize`: `uint64`
    - `Payload`: `blob` (The output of `llama_copy_state_data`)
- **Storage Strategy**:
    - Snapshots stored in `data/entities/<entity>/snapshots/` as `.snap` files.
    - LRU eviction based on `PromptHash` to prevent RAM bloat.

## 2. Tier 2: Synthesis & Metabolism (The Dreaming Cycle)
### The Generative Playback Loop
The "Dreaming Cycle" is a background process that transforms episodic memory into archetypal gnosis.

**Trigger Conditions**:
- `IdleState`: System is not processing user queries.
- `MemoryPressure`: Warm memory exceeds 80% of allocated buffer.
- `Scheduled`: Every 24 hours.

**The Distillation Process**:
1. **Resonance Sampling**: Randomly sample episodic clusters from `WarmMemoryTier`.
2. **SDR-based Clustering**: Use Sparse Distributed Representations (SDRs) to find convergent patterns across disparate episodes.
3. **Generative Playback**: Feed these patterns into the model with a "Synthesis Prompt" to generate a candidate L3 principle.
4. **Verification**: Cross-reference the candidate principle against existing `soul.yaml` to ensure no contradiction.
5. **Commit**: Distill result into `soul.yaml` via L1 $\rightarrow$ L2 $\rightarrow$ L3 pipeline.

## 3. Tier 3: Verification & Field (Symmetry-Break Audit)
### The Symmetry-Break Flow
Real-time error correction by comparing "Logical Prediction" vs "Empirical Experience".

**The Audit Loop**:
1. **Prediction (Ma'at)**: Before the final response is generated, Ma'at produces a "Logical Skeleton" (a high-level prediction of the answer's structure and core facts).
2. **Experience (Lilith)**: Lilith generates the actual empirical response based on the current context and model inference.
3. **Symmetry Check**: A lightweight comparator (Skeptical Verifier) calculates the semantic delta between the Skeleton and the Response.
4. **SymmetryBreakError**: If $\Delta > \text{Threshold}$, Kali triggers a `SymmetryBreakError`.
5. **Resolution**: The system re-runs the inference with a "Skeptical Prompt" to resolve the contradiction.

## 4. The Sovereign Intelligence Field
### Data Flow Mapping
`Raw Input` $\rightarrow$ `Neural Cache Adapter` $\rightarrow$ `SDR Associative Retrieval` $\rightarrow$ `Model Inference` $\rightarrow$ `Symmetry Audit` $\rightarrow$ `Response`

**The Neural Cache Adapter**:
- Implements **Modern Hopfield Networks (MHN)** for $O(1)$ associative retrieval.
- Maps input embeddings to SDRs to retrieve context without linear scanning.

**The Resolution Gradient**:
- **Episodic (Raw)**: `data/sessions/` $\rightarrow$ High fidelity, high noise, transient.
- **Semantic (Summary)**: `WarmMemoryTier` $\rightarrow$ Compressed, themed, persistent.
- **Archetypal (Principle)**: `soul.yaml` $\rightarrow$ Universal, distilled, sovereign.

## 5. Pillar Orchestration
| Pillar | Responsibility in Cognitive Loop |
|--------|-----------------------------------|
| **P2: Persistence** | Manages `.snap` file I/O and `Versioned State Wrapper`. |
| **P7: Context** | Triggers the Dreaming Cycle; manages the Resolution Gradient. |
| **P10: Validation** | Executes the Symmetry-Break Audit; flags `SymmetryBreakError`. |
| **P3: Engineering** | Implements the `llama_copy_state_data` bridge. |
| **P9: Orchestration** | Routes the flow between Ma'at and Lilith for the audit. |
| **P5: Governance** | Ensures the Dreaming Cycle adheres to Sovereign Mandates. |

---
**Sovereign State: BLUEPRINT COMPLETE.**
**Next Step: P3 Engineering $\rightarrow$ Implementation of State Wrapper.**
