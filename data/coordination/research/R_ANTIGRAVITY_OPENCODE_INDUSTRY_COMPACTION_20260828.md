<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# OpenCode Compaction Architecture & Industry Compaction Techniques

**Research Date:** 2026-08-28
**Researcher:** Antigravity (web discovery, parallel-search MCP)
**Sprint:** PUBLIC-DEBUT-01
**Scope:** OpenCode V2 official compaction + 2025–2026 industry landscape
**Confidence:** HIGH for OpenCode V2 docs (primary sources); HIGH for industry techniques (peer-reviewed + official blogs)

---

## Executive Summary

**Bottom line up front:**

1. **OpenCode V2 compaction is a *last-resort survival mechanism*, not an intelligence-preserving strategy.** It is a *durable checkpoint-and-retry* system that compresses the entire pre-recent history into a hardcoded **4,096-token** summary, with the most recent **8,000 tokens** (default) kept verbatim. Everything in between is **lost permanently from model-visible context** — though durable rows remain on disk.
2. **Industry has moved beyond "summarize older context" toward *sparse attention at training time*.** MiniMax M3's MiniMax Sparse Attention (MSA) and DeepSeek NSA/DSA demonstrate that sub-quadratic attention at 1M context is production-ready in 2026 — shifting the problem from *runtime compaction* to *training-time efficiency*.
3. **Hybrid architectures (Jamba 1.5, Granite 4.0, Nemotron-H) dominate long-context production.** Pure SSM (Mamba, RWKV) is strong on long retrieval but loses to Transformers on short-context quality. The 2026 winning recipe is *Transformer + Mamba hybrid* with a small attention-to-SSM ratio.
4. **KV cache eviction is the orthogonal axis.** SnapKV, CAKE, CriticalKV, and AnchorDirection achieve 30–60% memory reduction with minimal quality loss, and combine orthogonally with summary-based compaction.

---

## Part 1: OpenCode Compaction Architecture

### 1.1 Official Documentation (V2 — current)

**Source:** [opencode.ai/v2/docs/compaction](https://opencode.ai/v2/docs/compaction) (canonical, primary)
**Source:** [opencode.ai/v2/docs/migrate-v1](https://opencode.ai/v2/docs/migrate-v1) (V1→V2 field mapping)
**Source:** Antonio Zhu, [OpenCode V2 Compaction Internals](https://dev.to/antonio_zhu_e726fd856cd86/opencode-v2-compaction-internals-2a5d) (independent code audit, Jul 2026)

**Definition (verbatim from V2 docs):**

> Compaction replaces the active model context from an older part of a session with a generated checkpoint. The checkpoint contains a structured summary and a serialized tail of recent context, so the agent can continue with more room in the model's context window.
>
> Compaction is lossy, but it does not delete the earlier durable session messages. After a successful compaction, V2 builds model requests from the latest completed checkpoint and the messages that follow it.

**Key V2 design properties:**

| Property | Value | Source |
|---|---|---|
| Default `auto` | `true` (enabled) | V2 docs |
| Default `buffer` | `20,000` tokens (headroom reserve) | V2 docs |
| Default `keep.tokens` | `8,000` (was `preserve_recent_tokens` in V1) | V2 docs / Antonio Zhu audit |
| Summary output cap | **4,096 tokens, HARDCODED**, not configurable | `SUMMARY_OUTPUT_TOKENS` in `compaction.ts:15` |
| Tool output truncation | **2,000 chars, HARDCODED**, not configurable | `TOOL_OUTPUT_MAX_CHARS` in `compaction.ts:14` |
| Summary model | Same as session model (no separate "small model" option) | V2 docs ("There is no separate compaction-model setting or fallback model") |
| Summary generation tools | Disabled | V2 docs |
| Trigger formula | `estimated_tokens > context_limit - max(output_tokens, buffer)` | V2 docs |
| Token estimation | JSON-serialize request, 4 chars/token heuristic | V2 docs |
| Recovery retry | Once per step on provider overflow (even with `auto: false`) | V2 docs |

**Three-layer model (per Antonio Zhu's audit):**

| Layer | What it is | What compaction does to it |
|---|---|---|
| **Model-visible context** | What the model receives in a request | Replaced. Older context becomes `<summary>` + `<recent-context>` inside a `<conversation-checkpoint>` block. |
| **Active history projection** | The rows the runner reads when building a request | Starts from the latest checkpoint forward. Older rows are skipped. |
| **Durable storage** | The full `SessionMessageTable` rows | **Never deleted.** Original messages persist on disk; only the projection changes. |

This is the critical insight: compaction is *a change to the projection*, not a change to the database.

### 1.2 Compaction Flow (V2)

Per Antonio Zhu's V2 code audit:

```
[1] TRIGGER
    Auto:    estimated_request_tokens > model_context_limit - max(output_tokens, compaction_buffer)
    Recovery: provider returns context-overflow error AND turn produced no durable output

[2] SPLIT HISTORY
    - Convert structured messages to plain text ([User]:..., [Assistant]:..., [Assistant tool call]:...)
    - Truncate tool/shell output to 2,000 chars (hardcoded)
    - Walk backward from latest message, keep last `keep.tokens` (8,000) as `recent`
    - Everything before becomes `head` (the summarization target)

[3] SUMMARIZE HEAD
    - Use same model as session (no specialist model)
    - Tools disabled
    - Max 4,096 output tokens (hardcoded)
    - Structured prompt: Objective / Work State / Next Move / Relevant Files
    - If previous checkpoint exists, prompt asks model to UPDATE the anchored summary
      (not stack independent summaries)
    - Summary explicitly framed as "historical context, not new instructions"

[4] PERSIST CHECKPOINT
    - Insert `type: "compaction"` message into SessionMessageTable
    - Payload: { reason, summary, recent }
    - Only after non-empty summary: emit SessionEvent.Compaction.Ended

[5] RETRY
    - Runner throws `ContinueAfterCompaction` (control-flow, not error)
    - Reload active history from checkpoint
    - Rebuild smaller request and call model
```

**V2 config schema** (from `packages/core/src/config/compaction.ts`):

```ts
compaction: {
  auto?: boolean;          // default true
  prune?: boolean;         // EXISTS IN SCHEMA BUT UNUSED in current V2 core path
  keep?: { tokens?: number };  // default 8_000
  buffer?: number;         // default 20_000
}
```

**V1 → V2 field renames** (from [Migrate from V1](https://opencode.ai/v2/docs/migrate-v1)):

```jsonc
// V1
{ "compaction": { "preserve_recent_tokens": 8000, "reserved": 20000, "tail_turns": 4, "prune": true } }
// V2
{ "compaction": { "keep": { "tokens": 8000 }, "buffer": 20000, "auto": true, "prune": true } }
```

V2 has **no native `tail_turns` field** — recent context is retained by **token budget**, not turn count.

### 1.3 Recommended Settings (high-context work)

Per [BSWEN's March 2026 guide](https://docs.bswen.com/blog/2026-03-21-opencode-auto-compact-config/) and the V2 docs:

**Method 1 — Model-specific limits** (recommended for stability):

```jsonc
{
  "models": {
    "default": "minimax/minimax-m3",
    "minimax/minimax-m3": { "context": 950000, "output": 8192 }
  }
}
```

Leave ~5–10% headroom under the catalog limit for system prompt + safety margin.

**Method 2 — Global compaction** (recommended for portability):

```jsonc
{
  "compaction": {
    "auto": true,
    "keep": { "tokens": 25000 },
    "buffer": 30000
  }
}
```

**Recommended for long coding sessions (8h+):**
- `keep.tokens`: **25,000–40,000** (default 8,000 is too aggressive; loses recent tool output detail)
- `buffer`: **30,000** (default 20,000 gives more headroom for long-output models)
- `auto: true` (do not disable; recovery path also fires on overflow)
- For long-context models (1M+), set `context` in model config below the catalog limit (e.g., 950K for a 1M window)

**Disable auto-compaction only when** using an external context manager (e.g., the `opencode-acp` plugin requires `compaction.auto: false` to avoid conflicts). Source: [ranxianglei/opencode-acp README](https://github.com/ranxianglei/opencode-acp).

**Environment variable override:** `OPENCODE_DISABLE_AUTOCOMPACT=true` and `OPENCODE_DISABLE_PRUNE=true` (per [OpenCode flag.ts source](https://github.com/sst/opencode)). Caveat: **Issue #32385 reports these overrides are not always honored.**

### 1.4 Recent Changes (1.18.x — Jul/Aug 2026)

**Source:** [OpenCode Changelog](https://opencode.ai/changelog) + [Releases](https://github.com/anomalyco/opencode/releases)

| Version | Date | Compaction-relevant change |
|---|---|---|
| v1.18.17 | Aug 12, 2026 | "Made session compaction keep complete recent turns and produce clearer summaries for smaller models" |
| v1.18.16 | Aug 10, 2026 | (no compaction-specific change noted) |
| v1.18.x earlier | Jul 2026 | V2 beta released (`opencode2` binary, distinct from V1 `opencode`) |
| v1.18.18 | Aug 13, 2026 | (no compaction change) |
| v1.18.20 | Aug 21, 2026 | Bugfix: surface failed subagent tool calls with resumable `task_id` |
| v1.18.25 | Aug 28, 2026 | Bugfix: Azure auth without Bun; no compaction change |

**V2 compaction migration highlights** (from [Migrate from V1](https://opencode.ai/v2/docs/migrate-v1)):

1. **No more `tail_turns`** — token budget replaces turn count for recent-context retention
2. **No more `prune` field in core** — schema accepts it but V2 core doesn't use it
3. **Buffer renamed** from `reserved` → `buffer`
4. **Recent context renamed** from `preserve_recent_tokens` → `keep.tokens`
5. **No compaction-model field** — V1 hack of routing to a different model is unsupported
6. **Plugins, server API, and CLI config** have new formats (breaking changes, V1/V2 can coexist as `opencode` and `opencode2`)

**Note:** v1.18.17's "complete recent turns" is the only compaction improvement shipped in the 1.18.x series through Aug 28. Major V2 changes happened in the 1.18 beta cycle.

### 1.5 Known Issues (from GitHub issues & community)

| Issue # | Title | State | Date | Problem |
|---|---|---|---|---|
| [#11314](https://github.com/anomalyco/opencode/issues/11314) | Configurable Context Compaction Threshold | closed (not_planned) | 2026-01-30 | 75% hardcoded threshold; users want per-model control |
| [#16308](https://github.com/anomalyco/opencode/issues/16308) | 1M context for GPT-5.4 — compaction at 272k | closed (completed) | 2026-03-06 | Provider metadata for 1M not picked up; compacts at 272k |
| [#8089](https://github.com/anomalyco/opencode/issues/8089) | Auto-compact on by default but `context_length_exceeded` still occurs | closed (not_planned) | 2026-01-12 | Auto-compact can fail to fire when plugin conflicts exist |
| [#32385](https://github.com/anomalyco/opencode/issues/32385) | Compaction ignores `auto: false` and `OPENCODE_DISABLE_AUTOCOMPACT` | open (bug) | 2026-06-15 | Boolean off-switches and env vars ignored |
| [#3032](https://github.com/anomalyco/opencode/issues/3032) | Soft compaction / AI global workspace metabolism | open | 2025-10-08 | Request for model-selected selective deletion |
| [#4102](https://github.com/anomalyco/opencode/issues/4102) | Epic: Compaction Update | open (tracking) | 2025-11-09 | "current summary prompt too light to act as handoff" |
| [#9349](https://github.com/anomalyco/opencode/issues/9349) | config not work (feature compact) | closed (completed) | 2026-01-19 | User config ignored; often plugin conflict |

**Most-cited user complaints:**

1. **Premature compaction** for long-context models (Gemini, GPT-5.4, Claude Opus) — quality degrades before 75% threshold, but compaction won't fire
2. **No per-model threshold** — same default for 8K and 1M models
3. **`prune` field inert** in V2 — users expect it to remove stale tool results, it does nothing in core
4. **No small-model routing** for summary — using Opus to summarize Opus is expensive
5. **4,096-token summary cap** is too tight for long sessions; details lost irreversibly
6. **Media/attachments** become text descriptors; model loses visual context after compaction
7. **Plugin conflicts** — `oh-my-opencode`, `opencode-elf`, `opencode-dcp`, and `opencode-acp` all interact with compaction in undocumented ways
8. **OPENCODE_DISABLE_AUTOCOMPACT** env var not always honored (#32385)

### 1.6 Roadmap (observed direction)

From [#4102](https://github.com/anomalyco/opencode/issues/4102) "Epic: Compaction Update" + recent PRs:

1. **Better summary prompts** — structured handoff (files, errors, pending tasks, last action) [#4102, #2234, #3099]
2. **Selective pruning** — remove less-important messages rather than wholesale summary [#3032]
3. **Compaction model routing** — use a cheaper/smaller model for summary (currently forced to session model)
4. **Configurable threshold** — exposed as `compaction.threshold` [#11314, not yet landed]
5. **Per-model thresholds** — long-context models get different defaults [#11086, #11287]
6. **Plugin observability** — see which messages/parts are included and token usage breakdown
7. **`experimental.dcp_for_compaction`** — Dynamic Context Pruning as opt-in experimental feature
8. **Provider-side overflow retry** improvements — current "retry once per step" can still fail

**Likely v1.19/v2.x direction:** the `prune` field becomes real; threshold becomes configurable; compaction model becomes a separate field; DCP becomes first-class.

---

## Part 2: Industry Compaction Techniques (2025–2026)

### 2.1 Taxonomy of techniques

There are **four orthogonal axes** along which compaction techniques vary:

| Axis | Question | Example methods |
|---|---|---|
| **What is removed** | Deletion vs rewriting | Verbatim deletion (Morph Compact) vs summarization (LLM rewrite) |
| **When it runs** | Training-time vs inference-time | Mamba SSM (training) vs KV eviction (inference) |
| **Where it lives** | Model architecture vs runtime layer | Sparse attention (model) vs compaction (OpenCode) |
| **What it preserves** | Recency vs importance | Sliding window vs H2O attention-score ranking |

### 2.2 Major technique categories

#### A. Deletion-based compaction (runtime, no LLM)

**Verbatim compaction / token-level pruning** — [Morph Compact](https://www.morphllm.com/context-compaction) (industry):
- Identifies low-signal tokens and removes them
- **What survives is character-for-character identical to the original** (zero hallucination)
- Compression: 50–70%, speed: 33,000+ tok/s inline
- Cost: $0.20/M input tokens
- Tradeoff: lower compression ratio than LLM summary, but no hallucination risk

**Observation masking** (JetBrains Junie research, per Morph guide):
- Replace old tool outputs with `[masked]` placeholder
- Keep the tool call itself visible
- Matched LLM-summarization quality on SWE-bench with **zero extra compute**
- This is essentially what OpenCode's V1 `prune` field was *supposed* to do

**Token Merging (ToMe)** — [Bolya et al., 2022](https://arxiv.org/abs/2210.09461) (Meta):
- Merges *similar* tokens (not deletes) — halves attention compute
- 2–3x faster ViT inference with 0.2–0.3% accuracy drop
- **Used for vision, not text**, but concept applies to long context

#### B. LLM-based summarization (runtime, with LLM)

This is what **OpenCode uses** (V2 checkpoint summary).

**Variants:**
- **Extractive** — pull verbatim sentences (no LLM rewrite)
- **Abstractive** — LLM generates new summary (OpenCode V2 default)
- **Structured** — force LLM into sections (Objective, Work State, Next Move, Relevant Files) — what OpenCode does
- **Iterative** — each compaction UPDATES the prior summary rather than stacking (V2 supports this via "anchored summary" prompt)

**Tradeoff:** Highest compression (70–90%) but introduces hallucination risk; expensive (separate LLM call); cumulative loss over multiple compactions.

#### C. KV cache eviction (inference-time, model-internal)

**Sliding window** — [StreamingLLM (Xiao et al., 2023)](https://arxiv.org/abs/2306.14048):
- Keep attention sink (first few tokens) + recent window
- Linear memory in sequence length
- **Problem:** discards middle, loses long-range dependencies

**H2O (Heavy-Hitter Oracle)** — [Zhang et al., 2023](https://arxiv.org/abs/2306.14048):
- Evict KV pairs with lowest cumulative attention scores
- Theoretical guarantee via dynamic submodular formulation
- **Better than window** but per-token cost of scoring

**Scissorhands** — [Liu et al., 2023](https://arxiv.org/abs/2306.14048):
- "Persistence of importance" hypothesis — only ~10% of tokens consistently matter
- Identify "persistent" tokens via attention; evict the rest
- More efficient than H2O

**SnapKV** — [Li et al., 2024](https://arxiv.org/abs/2404.07143) (NeurIPS 2024):
- Observation window at prefilling → score and cluster KV positions
- **SOTA on long-context benchmarks** (QAs, summarization)
- Lower eviction overhead than H2O

**CAKE (Cascading and Adaptive KV Eviction)** — [Qin et al., 2025](https://arxiv.org/abs/2503.12491):
- Layer-wise preferences (different layers need different cache budgets)
- Adaptive: budget shifts based on input

**CriticalKV** — [2025](https://arxiv.org/html/2502.03805v2):
- Attention score + value vector norm as scoring function
- 11.1% improvement over best prior baseline

**AnchorDirection / AnchorKV** — [Geng et al., NeurIPS 2025](https://papers.neurips.cc/paper_files/paper/2025/file/0f29157c7613e137834a607075c55e17-Paper-Conference.pdf):
- Direction-based scoring (vector space) instead of magnitude
- More robust to outliers than attention-only methods

**Taming the Fragility of KV Cache Eviction** — [2025](https://arxiv.org/html/2510.13334):
- Addresses brittleness: existing methods degrade 10-30% under distribution shift

**Layer/head budget allocation** (orthogonal to eviction):
- **PyramidInfer** (2024), **PyramidKV** (2024): more budget to early layers
- **AdaKV** (2024): top-k across heads
- **HeadKV** (2024): calibration-based per-head budgets
- **DuoAttention** (2024): separate retrieval vs streaming heads

#### D. Sparse Attention (training-time architectural)

**Native Sparse Attention (NSA)** — DeepSeek (2024):
- Three branches: compression + selection + sliding window
- Highest quality ceiling, complex implementation
- Sparse pattern must be in pretraining gradients or retrieval heads get scrambled

**DeepSeek Sparse Attention (DSA)** — V3.2 (2025):
- MLA + token-level top-k with lightweight indexer
- Most stable quality, heavy kernel engineering

**MiniMax Sparse Attention (MSA)** — MiniMax M3 (Jun 2026):
- GQA + single-branch block selection
- Computes attention on **real** keys/values (not compressed)
- 9.7x prefill / 15.6x decode speedup at 1M context
- [Source: MiniMax blog](https://www.minimax.io/blog/minimax-m3), [Hugging Face analysis](https://huggingface.co/blog/AtlasCloud-AI/minimax-goes-sparse)

**Native NSA shared insight across DeepSeek + MiniMax:**
> "Sparse attention mechanisms generally avoid the complexity-explosion problem by adding a pre-filtering stage." — MiniMax M3 technical report

#### E. State Space Models / Linear Attention (alternative architecture)

**Mamba 2** — [Gu & Dao, 2024](https://arxiv.org/abs/2405.21060):
- Linear-time sequence modeling
- Constant memory during inference
- Selective state-space: input-dependent gating
- Unified with linear attention via SSD framework

**RWKV 7 (Goose)** — Bo Peng et al., 2024–2026:
- Recurrent (RNN-style), constant memory
- G1 variant released early 2026
- CPU-friendly edge inference
- Gated linear recurrence framework; delta rule powers RWKV-7, Gated DeltaNet, Qwen3-Next

**Gated Linear Attention (GLA)** — [Yang et al., 2023](https://arxiv.org/abs/2312.06635):
- RetNet, RWKV, Mamba as special cases
- Ships CUDA/Triton implementation

**Liquid LFM 2** — Liquid AI:
- Continuous-time recurrent networks (MIT CSAIL)
- 32k context; sub-linear memory

**Hyena / Striped Hyena 2** — convolution-based + attention hybrid

#### F. Hybrid Attention (production frontier 2026)

Per [Presenc AI May 2026 report](https://presenc.ai/research/hybrid-attention-models-mamba-jamba-rwkv-2026) and [The LLM Stack Ch. 11](https://prakashkagitha.github.io/llm-stack-book/02-transformer/11-ssm-and-alternatives.html):

| Model | Architecture | Parameters | Context |
|---|---|---|---|
| **Jamba 1.5 Large** (AI21) | Transformer + Mamba MoE hybrid | 398B / 94B active | 256k |
| **Jamba 1.5 Mini** | Transformer + Mamba MoE hybrid | 52B / 12B active | 256k |
| **Mamba 2 (Hybrid)** | SSM + attention hybrid | varies | 1M+ |
| **RWKV 7 G1** | Recurrent | 1.5B–14B | unlimited |
| **Falcon Mamba 7B** | Pure SSM | 7B | unlimited |
| **Codestral Mamba 7B** | Pure SSM code | 7B | unlimited |
| **Zamba 2 7B** | Mamba + attention hybrid | 7B | 16k |
| **Bamba 9B** (IBM) | Mamba + attention hybrid | 9B | long |
| **Nemotron-H** (NVIDIA) | Mamba-2/attention | — | long |
| **Granite 4.0** (IBM) | Mamba-2/attention | — | long |
| **Qwen3-Next** | dense/linear alternation | — | long |
| **MoBA (Mixture of Block Attention)** | Block attention | — | long |

**Key insight (from LLM Stack book):**
> "Hybrids win in practice. Pure SSM models have not displaced transformers in production LLMs — but by 2026 hybrids have, at least at the efficiency frontier. Shipped model families like NVIDIA's Nemotron-H and IBM's Granite 4.0 are Mamba-2/attention stacks, not pure transformers. The combination of a small fraction of attention layers with SSM/linear-attention layers offers the best tradeoff."

**Adoption:** ~8% of new open-weight model releases in 2025–2026 (growing minority).

#### G. Memory-augmented networks

**Infini-attention** — [Munkhdalai et al., Google 2024](https://arxiv.org/abs/2404.07143):
- Compressive memory + standard attention in one block
- Bounded memory, infinite context via continual pre-training
- 1M sequence length passkey, 500K book summarization
- Plug-and-play with existing LLMs

**Compressive Transformer** (Rae et al., 2019) — older predecessor, segment-level compression
**MemGPT** — virtual context management via OS-like paging
**On-Policy Context Distillation** — [Ye et al., Microsoft, 2026](https://arxiv.org/abs/2602.12275):
- Consolidates transient in-context knowledge into permanent weights
- Self-distillation: model learns to internalize context
- Frontier: *training-time* approach to in-context knowledge

**Memory-Augmented Transformers (systematic review)** — [2025](https://arxiv.org/abs/2508.10824):
- Three taxonomic dimensions: functional objectives, memory representations, integration mechanisms
- Bridges neuroscience (multi-timescale memory) with engineering

### 2.3 Tradeoffs matrix

| Method | Compression | Quality preservation | Speed | Memory savings | Hallucination risk | Best for |
|---|---|---|---|---|---|---|
| **Verbatim deletion** (Morph, JetBrains) | 50–70% | High (lossless) | Very fast (33k+ tok/s) | High | None | Code, structured logs |
| **LLM summarization** (OpenCode) | 70–90% | Medium (rewrite) | Slow (LLM call) | High | Moderate | Long NL conversations |
| **Sliding window** (StreamingLLM) | Linear | Low (loses middle) | Fast | High | None | Streaming, real-time |
| **H2O / Scissorhands** | 50–80% | Medium | Fast (per-token) | High | Low | Long-context inference |
| **SnapKV / CAKE / CriticalKV** | 40–70% | High | Fast | High | Low | Long-context inference (SOTA) |
| **Sparse attention training** (NSA, MSA) | 10–20x compute | High | Native | Native | None (architectural) | New model design |
| **SSM/Mamba** | Linear scaling | Medium | Constant | Constant | None | Long retrieval, time-series, edge |
| **Hybrid (Jamba, Nemotron-H)** | Linear in long regime | High | Linear + sparse | Mixed | None | Production long-context |
| **Infini-attention** | Infinite | High | Streaming | Bounded | None | Plug-in for existing LLMs |
| **Context distillation** (Microsoft) | Training-time | High (internalized) | Inference free | N/A | None | Repeated queries |

### 2.4 What M3 specifically uses (MSA — MiniMax Sparse Attention)

**Sources:** [MiniMax M3 official blog](https://www.minimax.io/blog/minimax-m3) (Jun 1, 2026), [Hugging Face community analysis](https://huggingface.co/blog/AtlasCloud-AI/minimax-goes-sparse) (May 29, 2026), [n1n.ai deep dive](https://explore.n1n.ai/blog/minimax-m3-sparse-attention-benchmarks-api-2026-07-05) (Jul 5, 2026), [vLLM indexer docs](https://docs.vllm.ai/en/latest/api/vllm/models/minimax_m3/common/indexer/)

**Architecture overview:**

- **MoE backbone:** ~428B total / ~23B active per token (inferred from M2 → M3 evolution)
- **MSA is not a replacement for GQA — it's an enhancement**
- **Two branches:**

  1. **Index Branch:** Lightweight scorer that ranks KV blocks. Selects **Top-k** independently per GQA group. Group-specific selection allows diverse context per attention head. Lower-precision "side cache" (`index-K`) enables cheap scoring.
  2. **Main Branch:** Block-sparse attention on **real keys/values** (not compressed). Only computes attention for blocks selected by index branch. Within selected blocks, computation is **exact** (no approximation).

**Speed claims:**
- **9.7× prefill** speedup at 1M tokens
- **15.6× decode** speedup at 1M tokens
- **28.4× compute reduction** (attention layer only, on 109B research checkpoint at 1M context)
- Effective receptive field: ~6–7% of blocks → ~60k–70k tokens

**Hardware co-design:**
- Optimized for H800 GPUs
- "exp-free Top-k selection" for high tensor-core utilization
- "KV outer gather Q" — outer loop over KV blocks
- Open-source kernel repo: [vLLM M3 indexer](https://docs.vllm.ai/en/latest/api/vllm/models/minimax_m3/common/indexer/)

**Position in 2026 design space** (from Hugging Face analysis):

| Design | KV substrate | Selection | Branches | Where attention runs |
|---|---|---|---|---|
| DeepSeek V3.2 DSA | MLA | Token-level top-k | 1 | Real K/V |
| DeepSeek NSA | GQA | Block-level | 3 (compress+select+sliding) | Compressed KV |
| Qwen3-Next | GQA | Layer-wise mix | dense/linear alternation | Mixed |
| **MiniMax M3 MSA** | **GQA** | **Block-level** | **1 (select only)** | **Real K/V** |

> "The one-line community read: M3 uses GQA rather than MLA, block-level selection in the spirit of CSA, but it computes attention on the real keys and values." — Atlas Cloud

**Key takeaway for the Architect:** M3's MSA is **orthogonal to OpenCode's compaction**. MSA reduces the *cost* of using long context; OpenCode's compaction *avoids* running out of context in the first place. They compose: with M3 + MSA, you trigger compaction much less often, and when you do, the model can absorb the 4,096-token summary efficiently.

**M3 also uses:**
- **Native multimodality** (text, image, video input) — trained multimodal from step zero
- **Computer use** capability (desktop operation)
- **Retrieval head research** to avoid the NSA "scrambled retrieval heads" failure mode
- **Likely natively trained sparsity** (M3's sparse pattern enters gradients during pretraining)

### 2.5 What OpenCode specifically uses

**V2 core compaction path:**
1. **LLM-based summarization** (abstractive, structured) — the primary mechanism
2. **Iterative anchored summary** — repeated compactions UPDATE the prior summary rather than stack
3. **Token-budget-based recent-context retention** — `keep.tokens` (default 8,000) of recent text kept verbatim
4. **Hard truncation of tool output** — 2,000 chars (V2 core, hardcoded)
5. **V1 `prune` (legacy)** — scanned backward through tool calls, protected last 40k of tool output, pruned if >20k prunable (per [badlogic gist](https://gist.github.com/badlogic/cd2ef65b0697c4dbe2d13fbecb0a0a5f))
6. **Observation masking** (via plugins) — not in core, but `oh-my-opencode` and `opencode-acp` provide this
7. **DCP (Dynamic Context Pruning)** — via plugins (`opencode-dcp`, `oh-my-opencode`'s `experimental.dcp_for_compaction`)
8. **Soft compaction** (issue #3032) — model-selected selective deletion (proposed, not shipped)
9. **External context managers** — `opencode-acp` (Active Context Pruning) replaces OpenCode's compaction entirely

**What OpenCode does NOT use:**
- Sparse attention (that's the model's job)
- KV cache eviction (that's the model's job)
- Mamba/SSM (that's the model's job)
- Infini-attention (that's the model's job)
- Context distillation (training-time, irrelevant to runtime)
- Verbatim token-level deletion in core (`prune` field exists but is inert in V2)

### 2.6 SOTA frontier (2026)

Per [n1n.ai M3 analysis](https://explore.n1n.ai/blog/minimax-m3-sparse-attention-benchmarks-api-2026-07-05), [Presenc AI 2026 report](https://presenc.ai/research/hybrid-attention-models-mamba-jamba-rwkv-2026), [LLM Stack book Ch. 11](https://prakashkagitha.github.io/llm-stack-book/02-transformer/11-ssm-and-alternatives.html), and [flash-linear-attention library](https://github.com/fla-org/flash-linear-attention):

**Active research frontier (2026):**

1. **Gated DeltaNet 2 (GDN-2)** — decoupling erase and write in linear attention
2. **Mamba-3** (Apr 2026) — improved sequence modeling with state space principles
3. **Raven** (May 2026) — high-recall sequence modeling with sparse memory routing
4. **Wall Attention** (May 2026) — length generalization with diagonal gates
5. **MoBA (Mixture of Block Attention)** — block-level sparse attention for long context
6. **YOCO (You Only Cache Once)** — single global KV cache shared across layers
7. **KDA (Kimi Linear / KDA)** — Kimi K2.6 attention architecture
8. **AttnRes** — attention with residual state
9. **Parallax** — speculative decoding for linear attention
10. **On-Policy Context Distillation** (Microsoft, 2026) — internalize context into weights during training

**Production frontier (shipped 2025–2026):**

1. **Sparse attention at training time** (NSA, MSA, DSA) — leading the new wave
2. **Hybrid Transformer + Mamba** (Jamba 1.5, Nemotron-H, Granite 4.0, Bamba, Zamba)
3. **Pure Mamba** (Falcon Mamba 7B, Codestral Mamba 7B) for code/edge
4. **RWKV 7** for edge/CPU
5. **1M+ context** becoming baseline (M3, Kimi K2.6, Gemini 3)
6. **Server-side compaction APIs** (Anthropic) — push compaction to provider

**Frontier of compaction-as-runtime-mechanism (orthogonal to architecture):**

- **Verbatim deletion** (Morph Compact) gaining ground over LLM-summary for low-latency
- **Anthropic server-side compaction** (note: their "compaction" is really summarization — the term is overloaded)
- **OpenAI's Codex CLI approach** — token-based threshold, preserve recent 20k tokens alongside summary, effective_context_window_percent = 95%
- **Plugin ecosystems** for OpenCode (DCP, ACP) treating compaction as a first-class extension point

**Where the field is heading (3 predictions from the LLM Stack book):**

1. **Hybrids win in production** — pure SSM hasn't displaced Transformer; hybrids have at the efficiency frontier
2. **Long-context economics matter** — at 256k+ tokens, hybrid architectures achieve materially better cost/latency than pure Transformer
3. **The standard toolchain is converging** — `mamba-ssm` (CUDA), `fla` (Triton), HF `transformers`, vLLM serving all support hybrids

---

## Part 3: Conclusions — Definitive Map

### 3.1 The four-question framework

For any compaction decision, ask:

1. **Can the model itself handle the context?** (MSA, Mamba, hybrid)
   - If yes, no runtime compaction needed
   - If no, proceed to step 2

2. **What is the runtime cost of a compaction pass?**
   - LLM summary: expensive (one full LLM call, 4k output tokens)
   - Verbatim deletion: cheap (33k+ tok/s)
   - Observation masking: free (placeholder)

3. **What is the failure mode?**
   - LLM summary → cumulative quality loss, hallucination
   - Verbatim deletion → may remove critical tokens
   - Masking → no model knowledge of past tool outputs

4. **Is the compaction a one-shot or iterative?**
   - Iterative (OpenCode V2 anchored summary) is better for multi-compaction sessions
   - One-shot is fine for short sessions

### 3.2 Recommendations for the Omega Engine (architectural)

Given the **sprint context** (PUBLIC-DEBUT-01, AntGravity, M3, OpenCode) and the **decisions in the craftsman contract** (D-548, D-565, D-567), the compaction landscape points to:

1. **Lean on the model when possible** — if M3 (MSA) or hybrid models are the primary target, the 1M context means compaction triggers far less often. **OpenCode + M3 = sparse attention at training + checkpoint summary at runtime = belt and suspenders.**

2. **OpenCode's V2 compaction is acceptable for short-medium sessions but inadequate for 8h+ coding marathons** with the 4,096-token summary cap. **Mitigations:**
   - Set `keep.tokens: 25000–40000` (well above default 8000)
   - Set `buffer: 30000` (above default 20000)
   - Configure per-model `context` to leave 5–10% headroom under catalog
   - For long sessions, prefer `oh-my-opencode` or `opencode-acp` plugins which add observation masking and DCP
   - Use **session_gnosis.md** (per M15) as a sovereign safety net — distillation L1→L3 runs *outside* OpenCode's compaction, giving you continuity even if OpenCode's summary loses details

3. **The 4,096-token hardcoded cap is the single biggest weakness** of V2. The Omega Engine's soul-integrity distillation (M11) effectively *replaces* OpenCode's summary with a structured L1→L2→L3 cascade that is more reliable.

4. **For the release/debut branch (D-553), document the recommended compaction config** so users don't hit the 75% hardcoded threshold on long-context models and lose work.

5. **Future-proofing:** as M3 + MSA + hybrid architectures become standard (2026–2027), runtime compaction becomes less critical. The runtime layer should focus on **observation masking + structured distillation** rather than LLM-summary compaction, because the models themselves will handle 1M+ context natively.

### 3.3 Source URLs (consolidated)

**OpenCode official:**
- [opencode.ai/v2/docs/compaction](https://opencode.ai/v2/docs/compaction) — V2 compaction canonical
- [opencode.ai/v2/docs/migrate-v1](https://opencode.ai/v2/docs/migrate-v1) — V1→V2 field renames
- [opencode.ai/changelog](https://opencode.ai/changelog) — recent versions
- [github.com/anomalyco/opencode/releases](https://github.com/anomalyco/opencode/releases) — version history
- [deepwiki.com/sst/opencode/2.4-context-management-and-compaction](https://deepwiki.com/sst/opencode/2.4-context-management-and-compaction) — code-level walkthrough

**OpenCode community/issues:**
- [Issue #11314 — Configurable threshold](https://github.com/anomalyco/opencode/issues/11314)
- [Issue #16308 — 1M context not used](https://github.com/anomalyco/opencode/issues/16308)
- [Issue #32385 — env var ignored](https://github.com/anomalyco/opencode/issues/32385)
- [Issue #4102 — Compaction epic](https://github.com/anomalyco/opencode/issues/4102)
- [Issue #3032 — Soft compaction](https://github.com/anomalyco/opencode/issues/3032)
- [criterium/opencode-lab — DeepSeek compaction comparison](https://github.com/criterium/opencode-lab/blob/main/research/deepseek-battle-compaction/README.md)

**OpenCode third-party research:**
- [Antonio Zhu — V2 Compaction Internals (Jul 2026)](https://dev.to/antonio_zhu_e726fd856cd86/opencode-v2-compaction-internals-2a5d)
- [BSWEN — Auto-Compact config (Mar 2026)](https://docs.bswen.com/blog/2026-03-21-opencode-auto-compact-config/)
- [badlogic gist — Compaction across tools (Dec 2025)](https://gist.github.com/badlogic/cd2ef65b0697c4dbe2d13fbecb0a0a5f)

**MiniMax M3 (MSA):**
- [minimax.io/blog/minimax-m3](https://www.minimax.io/blog/minimax-m3) — official
- [minimax.io/models/text/m3](https://www.minimax.io/models/text/m3) — model card
- [Hugging Face — M3 sparse diagram analysis](https://huggingface.co/blog/AtlasCloud-AI/minimax-goes-sparse)
- [n1n.ai — M3 deep dive (Jul 2026)](https://explore.n1n.ai/blog/minimax-m3-sparse-attention-benchmarks-api-2026-07-05)
- [Atlas Cloud — M3 sparse diagram](https://www.atlascloud.ai/blog/guides/minimax-goes-sparse)
- [vLLM M3 indexer docs](https://docs.vllm.ai/en/latest/api/vllm/models/minimax_m3/common/indexer/)
- [arXiv 2606.13392 — MSA paper](https://arxiv.org/html/2606.13392v2)

**Industry — KV cache eviction:**
- [H2O arXiv 2306.14048](https://arxiv.org/abs/2306.14048)
- [CriticalKV arXiv 2502.03805](https://arxiv.org/html/2502.03805v2)
- [AnchorDirection NeurIPS 2025](https://papers.neurips.cc/paper_files/paper/2025/file/0f29157c7613e137834a607075c55e17-Paper-Conference.pdf)
- [Taming Fragility arXiv 2510.13334](https://arxiv.org/html/2510.13334)
- [NaCl — KV cache eviction](https://www.emergentmind.com/papers/2408.03675)
- [Reformulating KV Cache Eviction arXiv 2605.07234](https://arxiv.org/pdf/2605.07234)

**Industry — Sparse attention:**
- [Sebastian Raschka — SWA chapter](https://sebastianraschka.com/llms-from-scratch/ch04/06_swa)
- [Bolya et al. — ToMe (arXiv 2210.09461)](https://arxiv.org/abs/2210.09461)

**Industry — SSM / Mamba / RWKV:**
- [Mamba original (arXiv 2312.00752)](https://arxiv.org/abs/2312.00752)
- [Mamba-2 / SSD (arXiv 2405.21060)](https://arxiv.org/abs/2405.21060)
- [GLA (arXiv 2312.06635)](https://arxiv.org/abs/2312.06635)
- [Presenc AI — Hybrid models May 2026](https://presenc.ai/research/hybrid-attention-models-mamba-jamba-rwkv-2026)
- [LLM Stack book Ch. 11 — SSM and alternatives](https://prakashkagitha.github.io/llm-stack-book/02-transformer/11-ssm-and-alternatives.html)
- [fla-org/flash-linear-attention library](https://github.com/fla-org/flash-linear-attention)

**Industry — Infini-attention / Memory:**
- [Infini-attention arXiv 2404.07143](https://arxiv.org/abs/2404.07143)
- [Memory-Augmented Transformers review arXiv 2508.10824](https://arxiv.org/abs/2508.10824)
- [On-Policy Context Distillation arXiv 2602.12275](https://arxiv.org/abs/2602.12275)
- [Context Distillation as Latent Memory (OpenReview 2026)](https://openreview.net/forum?id=ClglBrqgWv)

**Industry — Runtime compaction:**
- [Morph Compact — context compaction guide (Mar 2026)](https://www.morphllm.com/context-compaction)
- [Anthropic server-side compaction](https://platform.claude.com/docs/en/build-with-claude/compaction)

---

## Confidence levels

| Section | Confidence | Reason |
|---|---|---|
| OpenCode V2 official docs | **HIGH** | Primary source (opencode.ai/v2/docs/compaction) read directly |
| OpenCode V2 internals | **HIGH** | Cross-verified V2 docs + Antonio Zhu code audit + badlogic gist |
| OpenCode 1.18.x changelog | **HIGH** | Direct from opencode.ai/changelog and GitHub releases |
| OpenCode known issues | **HIGH** | Direct from GitHub issues with dates, states, assignees |
| M3 architecture (MSA) | **HIGH** | Official MiniMax blog + Hugging Face community analysis + vLLM docs + n1n.ai deep dive |
| Industry KV cache eviction | **HIGH** | Direct from arXiv papers and NeurIPS proceedings |
| Industry SSM/Mamba | **HIGH** | Multiple primary papers + production tracking (Presenc AI) + LLM Stack book |
| Infini-attention | **HIGH** | Direct from arXiv (Google paper) |
| SOTA frontier predictions | **MEDIUM** | Based on flash-linear-attention library activity + research papers; 3-12 month predictions are inherently uncertain |
| Specific date claims (e.g., "Jun 1, 2026" for M3) | **HIGH** | Cross-referenced across multiple sources |

**Overall confidence: HIGH for the technical landscape; MEDIUM for forward-looking SOTA claims.**

---

*⬡ OMEGA ⬡ ANTIGRAVITY ⬡ RESEARCH-COMPACTION-20260828-v1.0.0 ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*
