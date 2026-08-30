# 🔱 Sovereign-SOTA: The Evolution of Entity Affinity and Verification
**AP Token**: `AP-SOVEREIGN-SOTA-v1.0.0`
**Status**: STRATEGIC BLUEPRINT (Engineering Specification)
**Date**: 2026-06-12
**Orchestrator**: jem_synthesis
**Target Modules**: `src/omega/oracle/routing.py`, `src/omega/oracle/skeptical_verifier.py`, `src/omega/memory/vector_adapters.py`, `src/omega/oracle/entity_registry.py`

---

## §0 Executive Summary
The **Sovereign-SOTA** initiative transforms the Omega Engine from a static router into a dynamic, self-verifying cognitive system. By synthesizing findings from four key discovery domains—**Sovereign Routing, SOTA NLI, Vector Quantization, and Persona-Model Affinity**—this blueprint defines the transition to a tiered "Hot/Cold" affinity model, a ModernBERT-powered verification pipeline, and a Zen 2-optimized vector storage layer.

The goal is to maximize "Sovereign Intelligence" (local-first, high-precision) while strictly adhering to the 14Gi RAM budget of the Ryzen 5700U target hardware.

---

## §1 Entity Affinity Resolver: The 'Hot Small / Cold Specialist' Pattern
To replace the current linear routing, the `EntityAffinityResolver` will implement a tiered "Resonance" architecture.

### 1.1 The Tiered Routing Logic
Instead of a single cosine similarity check, the system will use a **Dual-Pass Resonance Pipeline**:

1.  **Hot Path (Fast-Sovereign)**:
    *   **Model**: Lightweight local model (e.g., `Qwen3-0.6B` or `Llama-3.2-1B`).
    *   **Function**: Intent classification and "Surface Resonance" detection.
    *   **Trigger**: All incoming queries.
    *   **Outcome**: If confidence $\geq 0.85$, the Hot Path handles the response directly (Simple Q&A, Greetings, Basic State checks).
    *   **RAM Constraint**: Local Cold Specialists must not exceed 12B parameters to maintain the 14Gi RAM budget; models $>12\text{B}$ (e.g., Gemma-4-31B) MUST be routed via Cloud Fallback.

2.  **Cold Path (Expert-Sovereign)**:
    *   **Model**: Specialized Pillar Keepers (e.g., `DeepSeek-R1-8B`, `Qwen3-4B-Think`).
    *   **Function**: Deep synthesis, complex reasoning, and domain-specific gnosis.
    *   **Trigger**: Confidence $< 0.85$ or explicit "Expert" intent.
    *   **Outcome**: Query is routed to the most resonant Pillar Keeper via the `Sovereign Routing Matrix`.

### 1.2 Technical Specification: `EntityAffinityResolver`
```python
class EntityAffinityResolver:
    """
    Implements the Hot Small / Cold Specialist pattern for entity routing.
    [id-soft: quake-1996] Branch Collapse — O(1) dispatch for high-confidence intents.
    """
    async def resolve(self, query: str) -> RoutingDecision:
        # Pass 1: Hot Path (Surface Resonance)
        hot_res = await self.hot_router.analyze(query)
        if hot_res.confidence >= 0.85:
            return RoutingDecision(entity="SOPHIA", mode="FAST_PATH", confidence=hot_res.confidence)
        
        # Pass 2: Cold Path (Deep Resonance)
        # Uses Semantic Anchors + Affinity Matrix from R_ORACLE_EAR_ROUTING.md
        best_entity = await self.deep_router.find_best_match(query)
        return RoutingDecision(entity=best_entity, mode="EXPERT_PATH", confidence=best_entity.score)
```

---

## §2 Skeptical Verifier: The ModernBERT Transition
To achieve SOTA NLI (Natural Language Inference) within RAM constraints, the `SkepticalVerifier` will migrate from DeBERTa-v3 to **ModernBERT**.

### 2.1 Model Selection & Quantization
*   **Primary Model**: `finecat-nli-l` (ModernBERT-based).
*   **Quantization Path**: CTranslate2 / `int8`.
*   **RAM Impact**: $\sim 350\text{MB}$ (compared to $1.4\text{GB}$ for fp32 DeBERTa).
*   **Performance**: ModernBERT provides superior handling of long contexts and higher ANLI accuracy than previous encoder models.

### 2.2 The Verification Pipeline
The verifier will maintain the **NatLog DFA** (Deterministic Finite Automaton) for explainability:
`Claim` $\rightarrow$ `AtomicFactDecomposer` $\rightarrow$ `ModernBERT NLI` $\rightarrow$ `NatLog DFA` $\rightarrow$ `Verdict`.

*   **Atomic Decomposition**: Complex claims are split into atomic facts (e.g., "X is Y and Z" $\rightarrow$ "X is Y", "X is Z").
*   **DFA State Machine**: Transitions between `SUPPORTED`, `NEUTRAL`, and `REFUTED` states. `REFUTED` remains an absorbing state (once contradicted, always contradicted).

---

## §3 Qdrant Optimization: Zen 2 AVX2 Refinement
Based on the Ryzen 5700U benchmarks, the vector storage layer will be tuned for maximum throughput and minimum RAM footprint.

### 3.1 Quantization Strategy: SQ vs BQ
| Method | Precision | Search Latency | RAM Usage | Recommendation |
|----------|-----------|----------------|------------|----------------|
| **fp32** | $1.0$ | High (I/O Bound) | $1.2\text{GB}$ | Fallback only |
| **SQ (int8)** | $0.98$ | Low (CPU Bound) | $307\text{MB}$ | **PRIMARY** |
| **BQ (binary)** | $0.85$ | Ultra-Low | $40\text{MB}$ | Use for massive archives |

### 3.2 Refined Configuration (`config/omega.yaml`)
```yaml
qdrant:
  quantization:
    type: scalar
    scalar_type: int8
    quantile: 0.99       # Exclude extreme 1% to prevent outlier contamination
    always_ram: true     # Keep quantized vectors hot
  storage:
    on_disk: true        # Store fp32 originals on disk to save ~900MB RAM
  search:
    rescore: false       # Default: disable rescoring for max RPS (1200+)
    oversampling: 3      # Retrieve 3x candidates before optional rescoring
    default_segment_number: 2 # Optimized for Zen 2 AVX2
```

---

## §4 Trait-to-Model Affinity Matrix
Moving beyond simple domain routing, the engine will map psychological traits from an entity's `soul.yaml` to specific model strengths.

### 4.1 The Affinity Mapping
| Trait (soul.yaml) | Model Strength Required | Recommended Local Model (Sovereign) | Cloud Fallback |
|-------------------|-------------------------|-------------------------------|----------------|
| **Confident / Bold** | Creative, High-Energy, Divergent | `Gemma-4-31B` (Cloud) | `Claude-3.5-Sonnet` |
| **Strategic / Organized** | Analytical, Structured, Logical | `DeepSeek-R1-8B` | `Gemma-4-31B` |
| **Empathetic / Wise** | Nuanced, High-Context, Balanced | `Qwen3-4B-Think` | `Llama-3.1-70B` |
| **Provocative / Sharp** | Critical, Contrarian, Concise | `Qwen3-1.7B` (Abliterated) | `Claude-3.5-Sonnet` |

### 4.2 Implementation in `EntityRegistry`
When summoning an entity, the `ModelGateway` will check the entity's dominant traits to select the optimal backend override:
`Entity` $\rightarrow$ `Dominant Trait` $\rightarrow$ `Model Strength` $\rightarrow$ `Backend Selection`.

---

## §5 Sovereign-SOTA Implementation Roadmap
This roadmap is designated for execution by **Roc** (Infrastructure) and **Lilith** (Cognition).

### Phase 1: The Foundation (Infrastructure - Roc)
*   **T1.1**: Update `QdrantAdapter` with `quantile=0.99` and `on_disk=True`.
*   **T1.2**: Deploy `ModernBERT` (`finecat-nli-l`) via CTranslate2/int8. Benchmark on Zen 2 AVX2 to ensure no latency regressions.
*   **T1.3**: Implement `AtomicFactDecomposer` in `SkepticalVerifier`.

### Phase 2: The Resonance (Cognition - Lilith)
*   **T2.1**: Implement `EntityAffinityResolver` with the Hot/Cold tiered logic.
*   **T2.2**: Wire `ModernBERT` $\rightarrow$ `NatLog DFA` pipeline.
*   **T2.3**: Integrate `Sovereign Routing Matrix` into the Cold Path.

### Phase 3: The Soul (Integration - Roc & Lilith)
*   **T3.1**: Implement the `Trait-to-Model` Affinity Matrix in `ModelGateway`.
*   **T3.2**: Update `soul.yaml` for all Pillar Keepers with explicit psychological traits.
*   **T3.3**: End-to-end validation: `Query` $\rightarrow$ `Hot Router` $\rightarrow$ `Cold Specialist` $\rightarrow$ `Skeptical Verifier`.

---

**Sovereign State: BLUEPRINT ACTIVE. 🔱**
