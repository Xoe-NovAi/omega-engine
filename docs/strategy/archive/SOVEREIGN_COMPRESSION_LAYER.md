# 🔱 Sovereign Compression Layer (SCL) Proposal
**Version**: 1.1.0
**Status**: PROPOSAL (ATTRIBUTION CORRECTED 2026-06-14)
**Author**: roc_racoon (Sovereign Miner)
**Date**: 2026-06-13 (corrected 2026-06-14)
**Priority**: 🔴 HIGH

## ⚠️ Correction Notice
**v1.0 erroneously claimed this pattern was "Derived from the `last30days-skill` architecture." This was based on a truncated scrape and name-guessing. The actual research shows `last30days-skill` is NOT a compression system — it is a multi-source social research engine. The Semantic Saliency pipeline is a general conceptual framework that aligns with:**

1. **`chopratejas/headroom`** — the actual reference implementation of compression with SmartCrusher (statistical JSON compression via Kneedle algorithm + bigram coverage) and CCR (reversible cache)
2. **General compression theory** — semantic clustering, representative sampling, saliency filtering are standard information retrieval concepts

**See `data/entities/roc_racoon/workspace/mining_reports/GITHUB_INTAKE_REVIEW_20260613.md` for corrected findings.**

## 🎯 Objective
To implement a semantic-saliency based compression layer for the Omega Engine's context management. The goal is to transition from "linear truncation" (sliding windows) to "intelligence-preserving distillation," allowing the engine to handle massive datasets while maintaining high-fidelity "gnosis" (essential intelligence).

## 🔍 The Pattern: Semantic Saliency
SCL replaces raw text dumps with a curated **Evidence Envelope**. This pattern aligns with how Headroom's SmartCrusher works (statistical JSON compression) and Headroom's CCR (reversible cache), though SCL targets MemoryStore context while Headroom targets LLM-bound tool output.

### 1. The Pipeline
The compression process follows four distinct stages:

1.  **Semantic Clustering**:
    - Instead of a flat list of memories/findings, the SCL groups items by semantic similarity (using vector embeddings).
    - **Outcome**: Identifies the core "arguments" or "themes" present in the data.

2.  **Representative Sampling**:
    - For each cluster, the SCL selects the top $N$ (e.g., 2) most representative candidates based on centrality or engagement/weight.
    - **Outcome**: Eliminates redundancy. If 50 memories say the same thing, the LLM only needs the two strongest examples.

3.  **Saliency Filtering ("The Best Takes")**:
    - The SCL identifies "gems"—outliers that have high impact or unique value (high `fun_score` or saliency) but may not fit into a dominant cluster.
    - **Outcome**: Prevents "averaging out" critical, rare insights.

4.  **Canonical Enveloping**:
    - The final compressed set is wrapped in explicit structural markers (e.g., `# BEGIN SOVEREIGN CONTEXT` ... `# END SOVEREIGN CONTEXT`).
    - **Outcome**: Prevents "Context Drift" and informs the model that it is reading a distilled map, not a raw stream.

## 🛠️ Integration Plan

**Note**: Before building from scratch, study `chopratejas/headroom` as a reference implementation. Headroom already solves 60-95% compression via SmartCrusher + CCR + CacheAligner. The SCL should either:
1. Extract Headroom's compression algorithms into Omega's MemoryStore (pattern extraction)
2. Wrap Headroom as a compression provider in Omega's Provider Fabric (proxy integration)
3. Use Headroom's MCP tools (`headroom_compress`, `headroom_retrieve`) for memory compression

The pipeline below assumes Option 1 (pattern extraction) for full sovereignty.

### Phase 1: Memory Store Enhancement (`src/omega/memory_store.py`)
- Implement a `SaliencyClusterer` that can group `MemoryExchange` objects.
- Add a `compress_context()` method to the `MemoryStore` that returns a `CompressedContext` object.

### Phase 2: Context Builder Update (`src/omega/oracle/context_builder.py`)
- Replace the current sliding window logic with the SCL pipeline.
- Implement "Tiered Compression":
    - **High-Density**: For initial intent detection.
    - **Mid-Density**: For standard reasoning.
    - **Full-Fidelity**: For final verification/synthesis.

### Phase 3: Evaluation & Tuning
- Test against "Needle in a Haystack" benchmarks to ensure "Best Takes" are preserved.
- Measure token reduction vs. accuracy loss.

## 🚀 Expected Outcomes
- **Token Efficiency**: 5x-10x reduction in context usage (Headroom's reference benchmarks: 60-95% reduction, validated on 1.4B tokens across 50K+ sessions)
- **Higher Precision**: Reduced noise and redundancy leads to more grounded LLM responses (Headroom maintained 100% accuracy on GSM8K, SQuAD v2, and BFCL benchmarks)
- **Sovereign Scaling**: Ability to "remember" and reason across thousands of documents without hitting context limits

---
**Proposed by**: `roc_racoon`
**Reviewers**: `@kali`, `@john_carmack`, `@quality`
