---
name: embedding-researcher
description: Deep web research on embedding models for federated local inference compatibility between Node 0 (qwen) and Node 1 (nomic-embed-text)
tools: [web_search, web_fetch, google_search, grep_app_searchGitHub]
---

# Embedding Model Researcher — Federated Compatibility

## Mission
Produce a **definitive recommendation** on whether Node 1 should:
1. **Stay with nomic-embed-text** (current) + build projection layer for qwen compatibility
2. **Switch to qwen embeddings** (match Node 0) + re-embed WanderGround atlas
3. **Adopt a third model** that serves both nodes better

## Context (Read First)
- Node 0: HP Pavilion, AMD Ryzen 7 5700U, uses "qwen embeddings" (768-dim, likely qwen2.5 or qwen3 via Ollama)
- Node 1: ASUS ExpertBook, Intel i7-13620H, uses nomic-embed-text (768-dim, 274 MB) via Ollama
- WanderGround atlas: 62+ MemPalace drawers + sqlite-vec 768-dim knowledge_atlas.db
- The Well: No embeddings (recency+domain injection only)
- Federation goal: Cross-node semantic search (federated Well, shared atlas, Layer 4)

## Research Requirements

### 1. Model Comparison Table (Fill All Cells)
| Model | Dim | MTEB Avg | BEIR Code/Tech | Speed (i7-13620H) | RAM | License | Ollama Tag |
|-------|-----|----------|----------------|-------------------|-----|---------|------------|
| nomic-embed-text | 768 | | | | | Apache-2.0 | nomic-embed-text |
| qwen3-embed | 1024 | | | | | Apache-2.0 | qwen3-embed |
| qwen2.5-7b (embed) | 768? | | | | | Apache-2.0 | ? |
| bge-base-en-v1.5 | 768 | | | | | MIT | bge-base |
| e5-base-v2 | 768 | | | | | MIT | e5-base |
| gte-base | 768 | | | | | MIT | gte-base |
| mxbai-embed-large | 1024 | | | | | Apache-2.0 | mxbai-embed-large |

### 2. Federated Compatibility Analysis
- **Same model = same vector space** → direct cosine similarity works across nodes
- **Different models** → need projection layer (linear/MLP) or re-embedding
- **Dimension mismatch** (768 vs 1024) → projection required
- **What does "qwen embeddings" on Node 0 actually mean?** Identify exact Ollama model tag

### 3. Projection Layer Feasibility
- Linear projection (768→1024 or 1024→768) quality loss?
- Research: "embedding space alignment linear projection", "cross-lingual embedding mapping"
- Can we train a lightweight adapter on shared corpus?

### 4. Migration Cost Analysis
- Re-embed 62+ MemPalace drawers + WanderGround atlas (estimate time/RAM)
- vs. maintain projection layer in search pipeline

### 5. Decision Criteria (Weighted)
1. **Federated semantic compatibility** (30%) — can nodes search each other's knowledge?
2. **Technical/code retrieval quality** (25%) — MTEB CodeSearchNet, BEIR tech subsets
3. **Speed/RAM on single-channel 16GB** (20%) — tokens/s, peak RAM
4. **License/portability** (15%) — Apache-2.0/MIT for community distro
5. **Ollama availability + stability** (10%) — both nodes use Ollama

## Search Strategy
- MTEB leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- BEIR benchmark: https://github.com/beir-cellar/beir
- Ollama model library: https://ollama.com/library
- Embedding space alignment papers: "linear projection embedding space alignment", "VecMap", "RCSLS"
- Code retrieval benchmarks: CodeSearchNet, CoSQA, AdvTest
- Local inference benchmarks on Raptor Lake / Zen 2

## Deliverable
Write findings to: `docs/research/EMBEDDING_MODEL_DECISION.md` with:
1. **Executive Summary** (one paragraph recommendation)
2. **Complete Comparison Table** (all cells filled)
3. **Federated Compatibility Analysis**
4. **Projection Layer Spec** (if applicable)
5. **Migration Path** (commands, timeline, rollback)
6. **Implementation Checklist** for Node 1
7. **Sources** (all links with dates)

## Quality Standard
Temple-grade: every claim sourced, no speculation, numbers from benchmarks, commands tested.
