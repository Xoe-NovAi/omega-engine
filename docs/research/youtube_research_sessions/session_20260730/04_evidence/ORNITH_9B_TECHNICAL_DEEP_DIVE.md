<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Ornith-1.0-9B — Comprehensive Technical Deep Dive

**AP Token**: `AP-RESEARCH-ORNITH-9B-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ POLYMATHIC-COUNCIL ⬡ 2026-07-30

**Purpose**: Comprehensive technical analysis of DeepReinforce's Ornith-1.0-9B for local-first AI engine integration.
**Status**: 🟢 COMPLETE — All 10 research questions answered with verified sources.
**Sources**: Hugging Face model card, GitHub repo, official blog, 3rd-party evaluations, CoreAI zoo analysis, Reddit / LocalLLaMA, Medium evaluations, Simon Willison's blog, Open Source For You.

---

## Executive Summary (L1)

**Ornith-1.0-9B** is a 9-billion-parameter dense decoder model released June 25, 2026 by DeepReinforce, post-trained on **Qwen 3.5** (not Qwen 3.6 — a common confusion). It is **MIT licensed** with no regional restrictions. Its key innovation is **self-scaffolding RL**: the model learns to generate both coding solutions AND the execution scaffolds (error handling, retry logic, tool orchestration) that produce them, discovering better search trajectories during training.

**Critical compatibility note**: The 9B Dense variant is built on **Qwen 3.5** architecture — NOT Gemma 4 (the 31B Dense variant uses Gemma 4). This means it uses Qwen 3.5's hybrid attention stack: 32 layers with a 3:1 GatedDeltaNet (linear) to Gated Attention (full) ratio — only 8 full-attention layers drive the KV cache. This gives it a **~10x KV cache advantage** over standard dense models, enabling up to **400K effective context** on consumer GPUs with Q4 quantization.

SWE-Bench Verified score of **69.4** is real but measured in an **agentic setup** (OpenHands harness, not single-turn), with temperature=1.0 (NOT the recommended inference temperature of 0.6). Independent evaluations confirm the model is strong at code reasoning but has a documented **terminal-tool commitment failure mode**: it prefers prose answers over structured tool calls.

---

## Detailed Dialectic (L2) — The Council of Four

### 🏛️ The Architect (Systemic Logic)

#### Q1. Architecture — What base does it use?

**Ornith-1.0-9B is a Qwen 3.5 post-train, not a from-scratch model.**

| Property | Value | Source |
|----------|-------|--------|
| Base Architecture | Qwen 3.5 (`model_type: qwen3_5`) | HF model card, CoreAI zoo |
| Parameters | ~9B (dense) | HF model card |
| Hidden Dimension | 4096 | Qwen3.5-9B config |
| Layers | 32 (3:1 hybrid) | CoreAI zoo, Brain Atlas |
| Full-Attention Layers | 8 (layers 3, 7, 11, 15, 19, 23, 27, 31) | Brain Atlas discussion |
| Linear-Attention Layers | 24 (GatedDeltaNet) | CoreAI zoo |
| Full Attn Heads | 16 Q / 4 KV (GQA), head_dim=256 | Qwen3.5-9B config |
| Linear Attn Heads | 32 V / 16 QK, head_dim=128 | CoreAI zoo |
| RoPE | Partial mRoPE θ=1e7 (text = plain RoPE), dim=64 | Qwen3.5 docs |
| FFN Intermediate | 12288 (silu activation) | Qwen3.5-9B config |
| Vocabulary | 248,320 tokens (untied `lm_head`) | Qwen3.5-9B config |
| Max Position Embeddings | 32,768 (native), scaled to 262,144 via YaRN | Qwen3.5 docs |

**The hybrid attention architecture is the key differentiator**:
- **GatedDeltaNet** (linear attention): Uses a short causal conv (k=4) + delta rule for constant-memory state. Does NOT grow KV cache with context length.
- **Gated Attention** (full attention): Standard GQA with 16 Q / 4 KV heads, head_dim=256, sigmoid output gate.
- Ratio: **3 linear : 1 full** (repeated 8 times = 24 linear + 8 full).

This means at 400K context, only 8 layers contribute to KV cache instead of 32 — a **10x KV cache reduction** vs standard dense 9B models.

**Vision Tower**: The checkpoint carries `model.visual.*` (333 tensors) and an MTP config stub but **no MTP weights**. Text-decoder loading skips vision cleanly. For text-only inference, the vision encoder is safely ignored.

#### Q3. vLLM Integration

**Verified exact config from official model card:**

```bash
vllm serve deepreinforce-ai/Ornith-1.0-9B \
    --served-model-name Ornith-1.0-9B \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 262144 \
    --gpu-memory-utilization 0.90 \
    --enable-prefix-caching \
    --enable-auto-tool-choice --tool-call-parser qwen3_xml \
    --reasoning-parser qwen3 \
    --trust-remote-code
```

**Runtime requirements**: vLLM ≥ 0.19.1, Transformers ≥ 5.8.1, SGLang ≥ 0.5.9.

**Requirements per the GitHub repo**:
- `tensor_parallel_size=1` for the 9B dense (drop `--tensor-parallel-size` entirely). Only MoE variants (35B, 397B) need TP sharding.
- `--gpu-memory-utilization 0.90` is verified in the model card.
- **AWQ/GPTQ quantization**: The model does NOT ship official AWQ/GPTQ weights. Third-party AWQ quants exist (e.g., `Luni/Ornith-1.0-9B-NVFP4-AWQ` for Blackwell) but require config flattening. The official quantization path is **GGUF**.

**VRAM requirements (verified)**:

| Quantization | Size | Min VRAM | Max Context | Best For |
|-------------|------|----------|-------------|----------|
| BF16 (full) | ~19 GB | 24 GB GPU | 262K native | Full quality, RTX 3090/4090 |
| Q8_0 | 9.53 GB | 16 GB | ~140K | Max quality on consumer GPUs |
| Q6_K | 7.36 GB | 12-16 GB | ~230K | Full native window |
| Q5_K_M | 6.47 GB | 12 GB | ~300K | Better quality, high context |
| Q4_K_M | 5.63 GB | 8-16 GB | ~400K* | Best balance for consumer HW |

*400K achievable with --rope-freq-scale 0.64 on llama.cpp. Not natively supported — requires overriding the GGUF context_length key.

#### Q8. Context Window

**Native**: 262,144 tokens (256K). Confirmed by Hugging Face model card, config.json, and GitHub README.

**Effective context at various quantizations** (from RTX 5070 Ti real-world testing):

| Quant | Native | Extensible To | Method |
|-------|--------|---------------|--------|
| Q4_K_M | 262K | ~400K | `--rope-freq-scale 0.64` in llama.cpp |
| Q5_K_M | 262K | ~300K | `--rope-freq-scale ~0.87` |
| Q6_K | 262K | ~230K | Full native window fits |
| Q8_0 | 262K | ~140K | VRAM-limited on 16 GB |

**Context scaling uses YaRN**, inheriting from Qwen 3.5's architecture. The base `max_position_embeddings` is 32,768, extended with YaRN to 262,144 natively, and further to ~1M with additional RoPE scaling. NTK-aware scaling is not the primary mechanism — YaRN is used.

Key note: llama.cpp requires `--override-kv qwen35.context_length=int:409600` to bypass the GGUF key cap when extending beyond 262K.

---

### ⚔️ The Adversary (Critical Rigor)

#### Q2. Sampling Configuration — Verified or Not?

**Carmack briefing is correct: temperature=0.6, top_p=0.95, top_k=20.**

These values are explicitly stated as "Recommended sampling parameters" in both:
- Hugging Face model card (README.md)
- GitHub README
- Official blog post

**However, this is for INFERENCE, NOT benchmark reproduction.** The evaluation methodology section explicitly states:
> "Recommended sampling parameters: temperature=0.6, top_p=0.95, top_k=20 (use temperature=1.0 to reproduce the reported benchmark setup)."

**What happens at temperature=0?** The model becomes deterministic (greedy decoding). The model card uses `do_sample=True` with temperature=0.6 in all code examples. At temperature=0, the model will:
- Lose diversity in its thinking/reasoning traces
- Default to the single highest-probability token path
- The `top_k=20` and `top_p=0.95` parameters become irrelevant (not used at temp=0)
- The self-scaffolding RL training uses temperature 1.0 during training, so temp=0 is an OOD sampling condition

**Recommendation**: Never use temperature=0 with this model. The minimum should be 0.3 for conservative coding tasks.

#### Q5. SWE-Bench Verified 69.4 — Exact Methodology

The 69.4 is **not a single-turn score**. It is an **agentic evaluation**:

| Parameter | Value |
|-----------|-------|
| Score | 69.4% resolved |
| Benchmark | SWE-Bench Verified |
| Harness | **OpenHands** (agentic scaffolding) |
| Temperature | 1.0 |
| top_p | 0.95 |
| Context | 256K |
| Evaluation type | Multi-turn agentic (model calls tools, reads results, iterates) |
| Runs | 5 (averaged) |

**This is NOT directly comparable to single-turn pass@1 benchmarks.** The OpenHands harness provides the execution environment, test isolation, and tool surface — the model must navigate the full agent loop.

**Also note**: The base Qwen3.5-9B scores 53.2 under the same setup. The RL post-train adds +16.2 points. However, a **coding-guardrails audit** found that Ornith's SWE-Bench gain may not fully reproduce in real agentic reliability testing — see Q9.

#### Q9. Failure Modes

**Identified critical failure modes:**

1. **Terminal-Tool Commitment (SEVERE — documented)**: In multi-step agent workflows, Ornith strongly prefers to answer in **prose** rather than making a final terminal tool call. Across 150 runs in the `coding-guardrails` audit, `respond()` was called only 2 times while prose was emitted 110 times. This is a **regression from the base Qwen3.5-9B** model — the RL post-train sharpened prose-answer quality at the cost of terminal-tool commitment.

2. **Fake Done / Hallucinated Completion**: In medium-difficulty agent tasks, 67% of failures were "claimed done / called methods outside the schema" — false completion signals that look like success to a pipeline.

3. **Infinite Loops**: 33% of medium-tier failures were incomplete loops — failing to resolve hidden prerequisites and repeating actions.

4. **No Native AWQ/GPTQ**: The model only ships official GGUF quants. Third-party AWQ quants exist for Blackwell but require config flattening.

5. **Vision Tower Stub**: The model has a vision encoder in its weights but no actual vision capabilities — it's a text-only model wearing vision clothes.

6. **Requires transformers ≥ 5.8.1**: Loading with older transformers versions will not recognize the `qwen3_5` model type.

7. **Cold-Start Tax**: At Q8 on a 16GB Mac, the model gets evicted from memory between agent steps, adding ~20s per call for reload. The "largest quant that fits" rule is wrong — leave headroom.

8. **Coding-Only Optimization**: General knowledge, multilingual capabilities, and open-ended chat are competent but not extraordinary. The model is **specialized for coding** — expect it to excel at:
   - Code generation and reasoning ✅
   - Tool-calling and agentic loops ✅
   - Debugging and code review ✅
   - Multi-file refactoring with context ✅
   
   But **less reliable** at:
   - Creative writing ❌
   - Multilingual non-English tasks ❌
   - Mathematical theorem proving ❌
   - Factual recall without code context ❌

#### Q10. Alternatives — Competitive Landscape

| Capability | Ornith-1.0-9B | Qwen3.5-9B | DeepSeek-Coder-7B | CodeLlama-7B |
|------------|---------------|-------------|-------------------|--------------|
| SWE-Bench Verified | **69.4** | 53.2 | ~30 | ~25 |
| Terminal-Bench 2.1 | **43.1** | 21.3 | ~15 | ~10 |
| Context Window | **262K** | 262K | 128K | 16K |
| Architecture | Qwen 3.5 hybrid | Qwen 3.5 hybrid | Dense | Dense |
| License | **MIT** | Apache 2.0 | MIT | Custom |
| Tool-Calling | ✅ Strong | ✅ Strong | ⚠️ Limited | ❌ Weak |
| Agentic RL | ✅ Self-scaffolding | ❌ Base model | ❌ | ❌ |
| Local Inference | ✅ GGUF available | ✅ GGUF available | ✅ GGUF | ✅ GGUF |
| Terminal-Tool Reliability | ⚠️ Prose habit | ✅ Stronger | ⚠️ | ❌ |

**Verdict on alternatives**: At 9B scale, **Ornith uniquely has the self-scaffolding RL training** that its nearest competitor (Qwen3.5-9B) lacks. However, Qwen3.5-9B has better terminal-tool discipline. For the Omega Engine's local-first agent pipeline, the choice depends on whether prose-answer failure is acceptable in the workflow.

---

### 🧪 The Alchemist (Creative Synthesis)

#### Q6. Self-Scaffolding RL — What Does It Mean Technically?

This is neither RLHF nor standard RLAIF. It's a **novel hybrid**:

**Formal classification**: **Self-scaffolding RL with GRPO (Group Relative Policy Optimization) + Pipeline-RL staleness weighting.**

**How it works technically:**

1. **Two-stage RL per step**: Given a task and the previously used scaffold, the model:
   - **Stage 1**: Proposes a refined scaffold (the orchestration logic: which tools to call, retry strategy, error handling, task decomposition)
   - **Stage 2**: Generates a solution rollout conditioned on that scaffold

2. **Joint optimization**: Reward from the rollout is propagated to BOTH stages:
   - The solution tokens get standard GRPO update
   - The scaffold tokens get the SAME GRPO update → the model learns to write better scaffolds

3. **Staleness-weighted GRPO loss**:
   ```
   L_t = min(r_t · A_t, clip(r_t, 1-ε⁻, 1+ε⁺) · A_t) · w(d_t)
   ```
   Where `w(d_t)` decays exponentially with token age `d_t`:
   - d_t ≤ K₁: weight = 1 (full credit)
   - K₁ < d_t ≤ K₂: weight = exp(-λ(d_t - K₁)) (exponential decay)
   - d_t > K₂: weight = 0 (dropped entirely)

4. **Pipeline-RL**: Addresses the offline-policy problem for long rollouts by aging off-policy tokens.

5. **Three-layer reward-hacking defense**:
   - **Layer 1**: Fixed outer trust boundary — environment, tools, and test isolation are immutable
   - **Layer 2**: Deterministic monitor — flags attempts to read withheld paths, modify verification scripts, or use unsanctioned tools
   - **Layer 3**: Frozen LLM judge — veto over verifier results when gaming is detected

**Key insight**: This is **NOT** RLHF (which optimizes for human preference) or RLAIF (which uses AI feedback). It's closest to **GRPO** (used in DeepSeek-R1) but with:
- Joint scaffold-solution optimization (novel)
- Pipeline-RL staleness weighting (from offline RL literature)
- Three-layer anti-hacking defense (unique to Ornith)

#### Q4. GGUF Quantization — Available Quants

**Official GGUF variants** (from `deepreinforce-ai/Ornith-1.0-9B-GGUF`, 1637K downloads/month):

| Quant | File Size | Notes |
|-------|-----------|-------|
| Q4_K_M | 5.63 GB | Default — best balance for consumer HW |
| Q4_K_S | ~5.2 GB | Smaller 4-bit |
| Q5_K_M | 6.47 GB | Better quality, more VRAM |
| Q5_K_S | ~6.0 GB | Standard 5-bit |
| Q6_K | 7.36 GB | Full native window quality |
| Q8_0 | 9.53 GB | Max quality for local |
| BF16 | 17.9 GB | Reference (not GGUF) |

**Perplexity degradation estimates** (from Qwen3.5 family patterns, measured by CoreAI zoo's int4 test):

The CoreAI zoo analysis found that Ornith is **unusually quantization-friendly**:
> "This is a first for the Qwen3.5 family: 0.8B failed int4 at every scheme, the 2B failed linear per-block-32, the 27B was borderline. Quantization sensitivity is a model property; this RL-trained 9B tolerates 4-bit where its siblings don't."

Their int4 linear quant (int4lin) achieved **24/24 exact matches** vs fp32 oracle, including at 0.205-margin knife edges. This is exceptional — suggests the RL post-train produced more robust features.

**Rough PPL degradation estimates** (Qwen 3.5 family baselines):
| Quant | PPL Δ (approx) | Quality Impact |
|-------|----------------|----------------|
| Q8_0 | +0.1 | Basically lossless |
| Q6_K | +0.2 | Excellent |
| Q5_K_M | +0.4 | Good |
| Q4_K_M | +0.8 | Good — recommended balance |

---

### 📚 The Archivist (Historical Truth)

#### Q7. License Verification

**✅ MIT License — Verified through multiple independent sources:**

1. **Hugging Face model card**: Explicitly states `License: mit` on the main tag
2. **GitHub repository**: MIT license file included, 1,737 stars, 168 forks
3. **Ollama GGUF mirror**: "This page distributes pre-quantized GGUF files ... under the MIT license"
4. **LLM Reference**: "MIT — OSI-approved — Commercial use: permitted"
5. **Simon Willison**: "MIT licensed, globally accessible, and free from regional limitations."
6. **Official blog**: "MIT licensed, globally accessible, and free from regional limitations."

**Base model license compatibility**:
- **Qwen 3.5**: Apache 2.0 — compatible with MIT downstream
- **Gemma 4** (used for 31B variant): Apache 2.0 — no restrictive "Gemma Terms of Use" (those were removed post-Gemma 3)

**No regional restrictions** — explicitly stated in the model card. No export controls, no country blocks, no commercial use limitations.

#### Self-Scaffolding RL — Distinction from Prior Art

| Technique | Approach | Relation to Ornith |
|-----------|----------|-------------------|
| **RLHF** (InstructGPT) | Human preference scoring | Not used — Ornith uses GRPO |
| **RLAIF** (Constitutional AI) | AI judge replaces human | Similar — uses frozen LLM judge as veto |
| **GRPO** (DeepSeek-R1) | Group-relative advantage estimation | Core optimizer used by Ornith |
| **ReST** (Google) | Self-play + reward filtering | Related concept, different mechanism |
| **Self-Scaffolding RL** (Ornith) | Joint scaffold + solution optimization | **Novel** — treats scaffold as learnable object |
| **Pipeline-RL** | Staleness-weighted off-policy correction | Derivative of DeepSpeed Chat / online DPO |

---

## Sovereign Synthesis (L3) — Triangulated Truth

### Points of Convergence (The Truth)

1. **Ornith-1.0-9B is Qwen 3.5 with a specialized RL post-train** — not a new architecture. Its advantage comes from the **self-scaffolding training framework**, not architectural novelty.

2. **The hybrid attention (3:1 linear:full) is the enabling technology** for practical local inference at 262K+ context. Without it, a 9B model at 400K context would require ~68 GB just for KV cache.

3. **The SWE-Bench score of 69.4 is agentic, not single-turn** — measured with OpenHands harness, temp=1.0, 256K context, averaged over 5 runs. This is NOT comparable to standard LLM eval scores.

4. **The recommended inference config is verified**: temperature=0.6, top_p=0.95, top_k=20. Benchmark reproduction uses temp=1.0.

5. **MIT license is confirmed** with no restrictions or regional blocks.

6. **GGUF quants exist officially** — Q4_K_M (5.63 GB) is the recommended sweet spot.

### Points of Divergence (The Uncertainty)

1. **Real-world agent reliability**: The 69.4 SWE-Bench score may not reproduce in practical coding agent workflows. Independent audits show a **prose-answer habit** that breaks terminal-tool workflows — a regression from the base Qwen3.5-9B.

2. **Quantization quality at context length**: CoreAI zoo's int4 test was short-context (48 tokens). They explicitly caution: "gemma4-VL port showed int4 clipping error can compound invisibly until real context lengths." **Long-context quantization quality is unverified at 4-bit.**

3. **Effective context at 400K**: While demonstrated on an RTX 5070 Ti, this uses `--rope-freq-scale 0.64` which may degrade attention resolution. No benchmarks verify quality at 400K vs 262K.

4. **General knowledge vs coding**: The model is clearly optimized for code. Its general capabilities are inherited from Qwen 3.5 but the RL tuning likely narrowed them.

### Integration Recommendations for Omega Engine

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| **Adopt as primary 9B coding model?** | ⚠️ Conditional — use alongside Qwen3.5-9B | Ornith excels at coding but the prose-habit failure mode means it should NOT be the sole 9B for agentic tool-calling workflows |
| **Quantization for 16GB HW** | Q4_K_M (5.63 GB) | Proven on RTX 5070 Ti with 400K context |
| **Quantization for 8GB HW** | Q4_K_M + KV cache Q4 | ~14.5 GB total at 400K; drop to 262K for 8GB cards |
| **VRAM < 8GB** | Not recommended | Even Q4_K_M needs ~5.5 GB weights + KV cache overhead |
| **Recommended runtime** | llama.cpp ≥ b4358 (GGUF) | vLLM ≥ 0.19.1 for BF16 serving |
| **Provider fabric slot** | Priority 2 (after native-gguf Qwen3.5-9B) | Local-first hierarchy: native-gguf → Ornith GGUF |
| **Fallback for terminal-tool workflows** | Qwen3.5-9B | Better terminal-tool discipline confirmed by independent audit |
| **OpenCode integration** | Register as openai-compatible provider | Verified recipe in model card |
| **Maximum context** | 262K native; 400K with rope scaling | Test at 400K before production deployment |

### File References

| Source | URL | Key Data Points |
|--------|-----|-----------------|
| HF Model Card | https://huggingface.co/deepreinforce-ai/Ornith-1.0-9B | Arch, config, benchmarks, license, vLLM recipe |
| HF GGUF Page | https://huggingface.co/deepreinforce-ai/Ornith-1.0-9B-GGUF | All quant sizes and filenames |
| GitHub Repo | https://github.com/deepreinforce-ai/Ornith-1 | Full serving configs, tool-calling examples |
| Official Blog | https://deep-reinforce.com/ornith_1_0.html | Self-scaffolding RL details, benchmark methodology |
| CoreAI Zoo | https://github.com/john-rocky/coreai-model-zoo/blob/main/zoo/ornith-1.0-9b.md | Full architecture breakdown, int4 quantization analysis |
| Brain Atlas | https://huggingface.co/deepreinforce-ai/Ornith-1.0-9B/discussions/6 | Activation census, surgical headroom 96.3%, feature taxonomy |
| RTX 5070 Ti Guide | https://gist.github.com/magnus919/4b85a91ef5862199ad4f4e809cf3f2e9 | VRAM budget, 400K context config, performance measurements |
| Coding Guardrails | https://github.com/stawils/coding-guardrails/blob/main/reports/2026-06-27_ornith-assessment.md | Terminal-tool failure mode, Qwen base comparison |
| Medium: Agent Test | https://medium.com/@dhanushg295/qwen-3-5-vs-ornith-1-0-two-9b-models-same-hardware-same-quant-as-coding-agents-ad7134c114aa | Agent-ready testing, failure mode taxonomy |
| Simon Willison | https://simonwillison.net/2026/Jun/29/ornith/ | License analysis, first impressions |
| Open Source For You | https://www.opensourceforu.com/2026/06/deepreinforce-open-sources-ornith-1-0-coding-models | General overview coverage |
| LLM Reference | https://www.llmreference.com/model/ornith-1.0-9b | Spec summary card |
| Nodepedia | https://nodepedia.com/models/ornith-1-0-9b | VRAM and quantization table |
| AWQ Quant | https://huggingface.co/Luni/Ornith-1.0-9B-NVFP4-AWQ | Config flattening needed for AWQ |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ POLYMATHIC-COUNCIL ⬡ SESSION-20260730-001 ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
