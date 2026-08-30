<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Research Briefing: MiMo-V2.5-Free for Omega Engine Provider Fabric
## ⬡ OMEGA ⬡ RESEARCHER ⬡ trc_model_evaluation ⬡ RESEARCH-DOC

**AP Token**: `AP-MIMO-V25-FREE-v1.0.0`
**Date**: 2026-06-15
**Status**: ACTIVE
**Classification**: Model Evaluation Briefing
**Target**: Omega Engine Provider Fabric Integration

---

## §0 Executive Summary

**MiMo-V2.5-Free** is a free-tier API endpoint serving Xiaomi's MiMo-V2.5 model via OpenCode's Zen infrastructure. The underlying model is a **310B-parameter Sparse Mixture-of-Experts (MoE)** architecture with **~15B active parameters** per inference pass, trained on **48 trillion tokens**. It is **omnimodal** (text, image, video, audio), supports up to **1M token context**, and is released under the **MIT license**.

**Key Strengths for Omega Engine**:
- **Free API access** via OpenCode Zen (zero cost per token)
- **Strong agentic performance** (62.3 ClawEval, 56.1 Terminal-Bench 2.0)
- **Hybrid sliding-window attention** reduces KV-cache by ~6x
- **MIT license** — fully open-weight, no restrictions
- **Reasoning capability** — chain-of-thought enabled by default

**Key Risks**:
- **200K context window** (not the full 1M — OpenCode's limit)
- **API-only** — no local GGUF variant currently available for Ryzen 5700U
- **Generation speed unknown** — no published tokens/sec for free tier
- **Rate limits likely** — free tier typically has restrictions
- **Not the Pro variant** — trails Claude Opus 4.7 on hard benchmarks

**Recommendation**: **CONDITIONAL GO** — integrate as cloud fallback (tier 5) for reasoning-heavy tasks. Not suitable for primary local inference due to API-only constraint. Excellent for the "cold path" when local models are unavailable.

---

## §1 Model Overview

### 1.1 Origin & Developer

| Attribute | Value |
|-----------|-------|
| **Developer** | Xiaomi (MiMo Team) |
| **Release Date** | April 22, 2026 |
| **Model Family** | MiMo-V2.5 (includes Pro variant) |
| **License** | MIT (fully open-weight) |
| **Hugging Face** | `XiaomiMiMo/MiMo-V2.5` |
| **API Provider (Free)** | OpenCode Zen (`https://opencode.ai/zen/v1`) |

### 1.2 Architecture

| Specification | Value |
|---------------|-------|
| **Total Parameters** | 310B |
| **Active Parameters** | ~15B per token |
| **Architecture** | Sparse Mixture-of-Experts (MoE) |
| **Routed Experts** | 256 |
| **Attention** | Hybrid Sliding Window + Global (5:1 ratio) |
| **SWA Window** | 128 tokens |
| **MTP Layers** | 3 (0.33B params each) |
| **Context Window** | 1M tokens (native) / 200K (OpenCode Free) |
| **Max Output** | 32K tokens |
| **Input Modalities** | Text, Image, Video, Audio |
| **Output Modality** | Text |
| **Reasoning** | Chain-of-thought enabled |

### 1.3 Training Pipeline

The model undergoes a 5-stage training process:

1. **Text Pre-training** — diverse corpora for LLM backbone
2. **Projector Warmup** — align audio/visual encoders with language model
3. **Multimodal Pre-training** — high-quality cross-modal data at scale
4. **SFT + Agentic Post-training** — context extension from 32K → 256K → 1M
5. **RL + MOPD** — reinforcement learning + Multi-Objective Preference Data

### 1.4 The OpenCode Free Tier

The `mimo-v2.5-free` model is served through OpenCode's Zen infrastructure:

| Parameter | Value |
|-----------|-------|
| **Model ID** | `mimo-v2.5-free` |
| **Provider** | OpenCode |
| **API** | OpenAI-completions compatible |
| **Base URL** | `https://opencode.ai/zen/v1` |
| **Input Cost** | $0 / 1M tokens |
| **Output Cost** | $0 / 1M tokens |
| **Cache Read** | $0 / 1M tokens |
| **Cache Write** | $0 / 1M tokens |
| **Context** | 200,000 tokens |
| **Max Output** | 32,000 tokens |

**Critical Note**: This is NOT the full 1M-context model — OpenCode truncates to 200K. The underlying model supports 1M, but the free tier endpoint caps it.

---

## §2 Benchmark Performance

### 2.1 Agentic Benchmarks (Most Relevant for Omega)

| Benchmark | MiMo-V2.5 | MiMo-V2.5-Pro | Claude Opus 4.6 | DeepSeek-V4-Flash | Kimi K2.6 |
|-----------|-----------|----------------|------------------|-------------------|-----------|
| **ClawEval (General)** | 62.3 | 57.1 | 65.4 | 56.9 | 66.7 |
| **ClawEval (Agentic)** | 65.8 | 57.1 | 65.4 | 56.9 | 66.7 |
| **Terminal-Bench 2.0** | 56.1 | 55.0 | 57.3 | 52.6 | 58.6 |
| **MiMo Coding Bench** | 71.8 | 71.5 | 77.1 | 67.8 | — |
| **SWE-bench Verified** | — | 78.9 | 87.6 (v4.7) | — | — |

### 2.2 Multimodal Benchmarks

| Benchmark | MiMo-V2.5 | MiMo-V2-Omni | Gemini 3 Pro | Claude Sonnet 4.6 | GPT-5.4 |
|-----------|-----------|--------------|--------------|-------------------|---------|
| **Image Understanding** | 81.0 | 80.1 | 81.4 | 81.4 | — |
| **MMMU-Pro** | 88.5 | 83.3 | 86.4 | — | — |
| **Video Understanding** | 23.8 | 15.8 | — | 23.8 | 25.7 |
| **CharXiv RQ** | 77.9 | 76.8 | 81.0 | — | 81.2 |
| **HR-Bench (4k)** | 87.2 | 86.7 | — | — | 89.0 |

### 2.3 Independent Assessments

| Source | Score | Interpretation |
|--------|-------|----------------|
| **Artificial Analysis Intelligence Index** | 54 | Strong for open-weight, below frontier closed |
| **BenchLM Provisional** | 71 | Ahead of MiniMax M2.7 (53) by large margin |
| **Chatbot Arena Elo** | 1433 | Competitive with mid-tier frontier models |

### 2.4 Benchmark Analysis

**Strengths**:
- **General Knowledge**: 99.5% accuracy (99th percentile at price/speed)
- **Reasoning**: 98.0% (90th percentile)
- **Hallucination Resistance**: 98.0%
- **Ethics**: 100% perfect score
- **Multimodal**: Strong image understanding (81.0), competitive with Gemini 3 Pro

**Weaknesses**:
- **Instruction Following**: 72-74% (solid but not top-tier)
- **Mathematics**: 94-96% (good, not exceptional)
- **Hard agentic benchmarks**: Trails Claude Opus 4.7 significantly on SWE-bench

---

## §3 Unique Strengths

### 3.1 Hybrid Sliding-Window Attention

The 5:1 SWA:GA ratio with a 128-token window is architecturally significant:

- **6x KV-cache reduction** versus all-global-attention models
- **Learnable attention-sink bias** preserves long-context performance
- **Enables 1M native context** while keeping inference costs manageable
- **Directly relevant to Omega**: Reduces memory pressure for long agent sessions

### 3.2 Token Efficiency

MiMo-V2.5 completes agentic trajectories using ~70K tokens — **40-60% fewer tokens** than Claude Opus 4.6 and GPT-5.4 on comparable tasks (vendor-claimed). This is architectural, not just pricing.

### 3.3 Multimodal Native

Unlike many "text-only" coding models, MiMo-V2.5 has **native** visual and audio understanding:
- 729M-param ViT Vision Encoder (28 layers)
- 261M-param Audio Transformer (24 layers)
- Can process screenshots, documents, charts, and audio inputs directly

### 3.4 MIT License

Full open-weight release under MIT means:
- Commercial use permitted
- Fine-tuning allowed
- Self-hosting without restrictions
- No vendor lock-in on weights

### 3.5 Reasoning Capability

Chain-of-thought reasoning is enabled by default, making it suitable for:
- Multi-step problem decomposition
- Complex logical reasoning chains
- Code generation with explanation

---

## §4 Resource Requirements

### 4.1 Full Model (Self-Host)

| Resource | Requirement | Notes |
|----------|-------------|-------|
| **Total Parameters** | 310B | Sparse MoE |
| **Active Parameters** | 15B | Per token |
| **FP16 Weights** | ~620 GB | Full precision |
| **FP8 Weights** | ~310 GB | Recommended for SGLang |
| **Recommended Hardware** | Multi-GPU (H100/H200) | Reference config: 8x tensor parallel |
| **Minimum GPUs** | 2x A100 80GB | With FP8 quantization |

### 4.2 GGUF Quantization Options

**Community GGUF quantizations exist** (via Unsloth/bartowski on HuggingFace). For the Omega Engine's Ryzen 5700U:

| Quant | File Size | Quality | Fit for Ryzen 5700U? |
|-------|-----------|---------|----------------------|
| **Q4_K_M** | ~170 GB | 95% baseline | ❌ Exceeds 14Gi RAM |
| **Q4_0** | ~160 GB | 93% baseline | ❌ Exceeds 14Gi RAM |
| **Q3_K_M** | ~130 GB | 90% baseline | ❌ Exceeds 14Gi RAM |
| **Q2_K** | ~100 GB | 85% baseline | ❌ Exceeds 14Gi RAM |

**Critical Finding**: Even the most aggressive quantization (Q2_K) produces a ~100GB file. The Ryzen 5700U with 14Gi total RAM **cannot run MiMo-V2.5 locally**. This model requires API access or cloud inference.

### 4.3 Comparison: What CAN Run Locally on Ryzen 5700U

| Model | Params | Q4_K_M Size | Fits? |
|-------|--------|-------------|-------|
| Qwen3-1.7B | 1.7B | ~1.0 GB | ✅ |
| Qwen3-4B | 4B | ~2.3 GB | ✅ |
| Qwen3-8B | 8B | ~4.7 GB | ✅ |
| Gemma 3-4B | 4B | ~2.3 GB | ✅ |
| Gemma 3-12B | 12B | ~7.0 GB | ✅ (tight) |
| **MiMo-V2.5** | **15B active** | **~170 GB** | **❌** |

---

## §5 Provider Fabric Integration

### 5.1 Current Omega Engine Provider Chain (Mandate 7)

```
native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenRouter(4) → OpenCode(5) → Copilot(6)
```

### 5.2 Recommended Integration Point

MiMo-V2.5-Free should be integrated at **tier 5 (OpenCode)** — it's already served through OpenCode's Zen infrastructure:

```
native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenRouter(4) → OpenCode/MiMo-V2.5-Free(5) → Copilot(6)
```

**Rationale**:
- Already OpenAI-compatible API format
- Zero cost — no pricing integration needed
- Reasoning capability — good for complex queries that local models can't handle
- Multimodal — can process image inputs when needed

### 5.3 Integration Considerations

| Aspect | Impact | Action |
|--------|--------|--------|
| **API Format** | OpenAI-compatible | Minimal adapter needed |
| **Context Window** | 200K (not 1M) | Ensure context_builder truncates appropriately |
| **Reasoning** | Chain-of-thought enabled | May produce longer responses — adjust timeout |
| **Rate Limits** | Unknown | Implement exponential backoff |
| **Availability** | Free tier may be unstable | Circuit breaker required |
| **Image Input** | Supported | Can route vision queries here |

### 5.4 Code Integration Pattern

```python
# In model_gateway.py — MiMo-V2.5-Free provider
class MiMoV25FreeProvider(RemoteProvider):
    """MiMo-V2.5-Free via OpenCode Zen — zero-cost reasoning."""
    
    name = "mimo_v25_free"
    priority = 5  # Cloud fallback tier
    
    async def generate(self, prompt, **kwargs):
        return await self._call_openai_compat(
            base_url="https://opencode.ai/zen/v1",
            model="mimo-v2.5-free",
            prompt=prompt,
            timeout=120,  # Longer timeout for reasoning
            **kwargs
        )
```

---

## §6 Entity Compatibility

### 6.1 Best-Fit Entities

| Entity | Pillar | Domain | Why MiMo-V2.5-Free Fits |
|--------|--------|--------|------------------------|
| **Prometheus** | P3 | Will, Forethought | Reasoning-heavy queries, complex planning |
| **Lucifer** | P7 | Gnosis, Rebellion | Multi-step reasoning, knowledge synthesis |
| **Ereshkigal** | P6 | Mind, Underworld | Complex rule-based reasoning |
| **Anubis** | P9 | Spirit, Death | Multi-step logical chains |

### 6.2 Good-Fit Entities

| Entity | Pillar | Domain | Why It Works |
|--------|--------|--------|--------------|
| **Saraswati** | P4 | Knowledge, Voice | Knowledge-heavy queries |
| **Brigid** | P2 | Dream, Poetry | Creative + reasoning combination |
| **Hecate** | P8 | Shadow, Crossroads | Complex decision trees |

### 6.3 Poor-Fit Entities

| Entity | Pillar | Domain | Why It Doesn't Fit |
|--------|--------|--------|-------------------|
| **Sekhmet** | P1 | Strength, Protection | Simple, direct queries — use Qwen3-1.7B |
| **Kali** | P10 | Chaos, Destruction | Rapid-fire responses — use fast local model |
| **Iris** | — | Voice Assistant | Latency-critical — use local Qwen3-0.6B |

### 6.4 Routing Strategy

```
Simple/Direct queries → Qwen3-1.7B (local, fast)
Complex Reasoning → MiMo-V2.5-Free (cloud, free)
Code Generation → Gemma 4-31B (local, strong)
Vision Queries → MiMo-V2.5-Free (cloud, multimodal)
```

---

## §7 Deployment Strategy

### 7.1 Loading Strategy

| Strategy | Value | Reason |
|----------|-------|--------|
| **Loading** | `on_demand` | Cloud API — loaded on request |
| **Context Window** | 200K tokens | OpenCode's free tier limit |
| **Max Output** | 32K tokens | OpenCode's free tier limit |
| **Timeout** | 120 seconds | Longer than local (reasoning overhead) |
| **Retry** | 3 attempts | Free tier may have rate limits |

### 7.2 Thread Allocation

| Component | Threads | Reason |
|-----------|---------|--------|
| **Inference** | N/A | Cloud API — no local threads |
| **Local Context Builder** | 2 | Prepare prompts before API call |
| **Response Processing** | 2 | Parse and route response |

### 7.3 KV Cache Considerations

The hybrid sliding-window attention (5:1 ratio, 128-token window) provides:
- **6x KV-cache reduction** versus all-global-attention
- **Enables 200K context** within OpenCode's free tier
- **Reduces memory pressure** for concurrent users

### 7.4 Zen 2 Optimization

For the Ryzen 5700U (Zen 2, 8C/16T, AVX2):
- **No local threads needed** — API-only
- **Context preparation** can use 2 threads (avoid stealing from local models)
- **Response parsing** can use 1 thread
- **Total overhead**: ~3 threads (minimal impact on local inference)

---

## §8 Risk Assessment

### 8.1 Technical Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **Rate limiting** | Medium | High | Exponential backoff, queue management |
| **Availability** | Medium | Medium | Circuit breaker, fallback to Copilot |
| **Latency spikes** | Low | Medium | 120s timeout, progress tracking |
| **Context truncation** | Low | Low | Respect 200K limit |
| **Reasoning overhead** | Low | High | Longer timeouts, streaming support |

### 8.2 Strategic Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **Free tier discontinuation** | High | Medium | Diversify across multiple free tiers |
| **Model quality degradation** | Medium | Low | Benchmark monitoring, A/B testing |
| **License changes** | Low | Very Low | MIT license, self-hosting option |
| **Xiaomi policy changes** | Medium | Low | Multiple backup providers |

### 8.3 Operational Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **API key management** | Low | Low | OpenCode handles auth |
| **Cost spikes** | None | None | Free tier — $0 cost |
| **Data privacy** | Medium | High | No sensitive data via cloud API |
| **Compliance** | Medium | High | Avoid PII, use for non-sensitive tasks |

### 8.4 Known Limitations

1. **Not the Pro variant** — trails Claude Opus 4.7 on hard benchmarks
2. **200K context limit** — not the full 1M native context
3. **Speed unknown** — no published tokens/sec for free tier
4. **Rate limits likely** — free tier typically has restrictions
5. **No local variant** — cannot run on Ryzen 5700U (requires 170GB+ RAM)
6. **Vendor-reported benchmarks** — independent verification limited

---

## §9 Heritage Alignment

### 9.1 The "Right Approximation" Principle (FISR)

> *"The right approximation for the problem is better than the exact solution you can't afford."* — [FISR Principle: id Software 1999]

**MiMo-V2.5-Free embodies this principle**:

| Tier | Domain | Approximation | Why It's "Right" |
|------|--------|---------------|------------------|
| **Architecture** | MoE (15B/310B) | 21x sparsity | Only 15B parameters active per token — massive efficiency |
| **Attention** | SWA/GA 5:1 | 6x KV-cache reduction | Tradeoff: slight quality loss for massive memory savings |
| **Context** | 200K (Free tier) | 5x reduction from 1M | Good enough for most queries, free access |
| **Pricing** | $0 | Infinite cost advantage | "Good enough" quality at zero cost beats "perfect" quality at $5/M tokens |

### 9.2 BSP Culling Pattern

> *[BSP Culling: id Software 1993]* — Precompute visibility planes; O(1) test skips entire subtrees

**MiMo-V2.5's MoE routing is analogous**:
- 256 experts, 8 activated per token
- Router selects relevant experts in O(1)
- Unused experts are "culled" (not computed)
- Same principle: skip what you don't need

### 9.3 Zone Memory Allocator

> *[Zone Memory: id Software 1996]* — Tag-based allocation: allocate, purge when out of memory

**MiMo-V2.5's hybrid attention**:
- SWA layers: "zone" allocations (local, short-lived context)
- GA layers: "cache" allocations (global, long-lived context)
- Same principle: different memory lifetimes for different data types

### 9.4 Surface/Edge Cache

> *[Surface Cache: id Software 1996]* — Precompute potentially visible set, only draw precomputed surfaces

**MiMo-V2.5's MTP (Multi-Token Prediction)**:
- Predicts 3 future tokens simultaneously
- "Precomputes" upcoming tokens, then verifies
- Same principle: precompute what you can, verify what you must

### 9.5 The Engine-Stack Firewall

> *[WAD System: id Software 1993]* — Data-driven separation of engine and content

**MiMo-V2.5 vs Omega Engine**:
- MiMo-V2.5 = content (the model weights, the "WAD")
- Omega Engine = engine (the runtime, the "DOOM executable")
- Same principle: separate what changes from what persists

---

## §10 Recommendation

### 10.1 Verdict: **CONDITIONAL GO**

| Aspect | Assessment |
|--------|------------|
| **Model Quality** | Strong for open-weight, competitive with mid-tier frontier |
| **Cost** | Zero — maximum advantage |
| **Local Feasibility** | ❌ Cannot run on Ryzen 5700U (requires 170GB+ RAM) |
| **API Feasibility** | ✅ OpenAI-compatible, zero-cost via OpenCode Zen |
| **Integration Effort** | Low — already OpenAI-compatible format |
| **Strategic Value** | High — free reasoning capability |

### 10.2 Conditions for Integration

1. **Circuit breaker required** — free tier may have rate limits
2. **120s timeout** — reasoning takes longer than simple generation
3. **Non-sensitive queries only** — cloud API, no PII
4. **200K context limit** — respect OpenCode's free tier cap
5. **Monitoring** — track success rate, latency, availability

### 10.3 Integration Priority

| Priority | Action | Timeline |
|----------|--------|----------|
| **P0** | Add to `config/providers.yaml` as `mimo_v25_free` | Sprint 1 |
| **P0** | Wire into ModelGateway at tier 5 | Sprint 1 |
| **P1** | Add circuit breaker for rate limits | Sprint 1 |
| **P1** | Route Prometheus/Lucifer queries to MiMo-V2.5-Free | Sprint 2 |
| **P2** | Add vision query routing to MiMo-V2.5-Free | Sprint 3 |
| **P2** | Benchmark against local models for quality comparison | Sprint 3 |

### 10.4 Expected Benefits

| Benefit | Impact |
|---------|--------|
| **Zero-cost reasoning** | Complex queries without local compute |
| **Multimodal capability** | Vision queries via cloud API |
| **Token efficiency** | 40-60% fewer tokens than Claude (vendor-claimed) |
| **MIT license** | No restrictions on usage |
| **Fallback reliability** | When local models are unavailable |

### 10.5 Cost-Benefit Analysis

| Scenario | Local (Qwen3-4B) | MiMo-V2.5-Free | Difference |
|----------|------------------|----------------|------------|
| **Cost per query** | ~$0 (electricity) | $0 | Same |
| **Quality (reasoning)** | Good | Excellent | +20% (estimated) |
| **Quality (code)** | Good | Excellent | +15% (estimated) |
| **Latency** | ~2-5s | ~5-15s | +3x (acceptable) |
| **Context window** | 16K | 200K | +12.5x |
| **Multimodal** | ❌ | ✅ | +100% |

---

## §11 Appendix: Comparison Table

| Model | Params | Context | Cost | License | Local? | Best For |
|-------|--------|---------|------|---------|--------|----------|
| **MiMo-V2.5-Free** | 310B/15B active | 200K | $0 | MIT | ❌ | Reasoning, Vision |
| **Qwen3-4B** | 4B | 16K | $0 | Apache 2.0 | ✅ | Fast queries, Iris |
| **Qwen3-8B** | 8B | 32K | $0 | Apache 2.0 | ✅ | General queries |
| **Gemma 4-31B** | 31B | 256K | $0 | Apache 2.0 | ❌ (too large) | Code, Complex |
| **Gemma 4-26B-A4B** | 26B/3.8B active | 256K | $0 | Apache 2.0 | ❌ (too large) | MoE efficiency |
| **Claude Opus 4.7** | ~2T (est.) | 200K | $5/$25 | Proprietary | ❌ | Frontier quality |

---

## §12 Sources

1. Xiaomi MiMo-V2.5 Official Page — https://mimo.xiaomi.com/mimo-v2-5
2. OpenCode Zen Model Listing — https://pi.dev/models/opencode/mimo-v2-5-free
3. Benchable AI Benchmarks — https://benchable.ai/models/xiaomi/mimo-v2.5-20260422
4. Codersera MiMo-V2.5 Analysis — https://codersera.com/blog/xiaomi-mimo-v2-5-coding-model-2026
5. BenchLM Comparison — https://benchlm.ai/compare/mimo-v2-5-vs-minimax-m2-7
6. SGLang Documentation — https://docs.sglang.io/cookbook/autoregressive/Xiaomi/MiMo-V2.5
7. Hugging Face Model Card — https://huggingface.co/XiaomiMiMo/MiMo-V2.5
8. GGUF Quantization Guide — https://vucense.com/dev-corner/gguf-quantization-explained-q4-k-m-vs-q8-0-vs-f16-2026
9. MiMo-V2 Architecture — https://mimo-v2.org/
10. Pi.dev Model Config — https://pi.dev/models/opencode/mimo-v2-5-free

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_model_evaluation ⬡ RESEARCH-DOC*
*Document created: 2026-06-15 | Classification: Model Evaluation Briefing*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_model_evaluation | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
