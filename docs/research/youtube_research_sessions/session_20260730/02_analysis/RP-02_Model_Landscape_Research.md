<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Research Project RP-02: Model Landscape & Strategic Usage
**Session**: 2026-07-30 | **Status**: COMPLETE | **Priority**: P0 (HIGH)

---

## Executive Summary (L1)

This research project covers the strategic model landscape for Omega Engine, focusing on four high-value models with free/accessible tiers: **GLM 5.2**, **Ornith 1.0 9B**, **MiniCPM5-1B**, and **Agnes AI**. Each offers unique strategic advantages for local-first sovereign AI infrastructure.

---

## 1. GLM 5.2 (Z.ai / Zhipu AI)

### Source
- **Hugging Face**: https://huggingface.co/zai-org/GLM-5.2
- **Blog**: https://z.ai/blog/glm-5.2
- **GitHub**: https://github.com/zai-org/GLM-5

### Key Specifications
| Attribute | Value |
|-----------|-------|
| **Architecture** | MoE (744B total, 40B active) |
| **Context Window** | **1M tokens** (solid, not theoretical) |
| **License** | MIT (fully open, no regional limits) |
| **MTP** | Speculative decoding layer (+20% acceptance length) |
| **IndexShare** | Shared indexer across 4 sparse attention layers (2.9× FLOPs reduction at 1M) |

### Deployment Options
| Framework | Version | Notes |
|-----------|---------|-------|
| SGLang | v0.5.13.post1+ | Cookbook available |
| vLLM | v0.23.0+ | Recipes available |
| Transformers | v0.5.12+ | Native support |
| KTransformers | v0.5.12+ | Tutorial available |
| Unsloth | v0.1.47-beta+ | Guide available |
| Ascend NPU | vLLM-Ascend, xLLM, SGLang | Hardware-specific |

### Free Tier Access (Strategic)
- **Z.ai Coding Plan**: GLM-5.2 rolled out to all subscribers
- **Model name**: `"GLM-5.2"` or `"GLM-5.2[1m]"` for 1M context
- **Thinking effort**: High or Max (configurable)
- **Quota**: 3× peak (14:00-18:00 UTC+8), 2× off-peak
- **Promotion**: Off-peak billed at 1× through Sept 2026
- **ZCode Desktop**: 1.5× effective quota with Coding Plan

### Benchmarks (Reported)
| Benchmark | GLM-5.2 | Comparison |
|-----------|---------|------------|
| Terminal-Bench 2.1 | 81.0 | > Opus 4.7 (70.3), < Opus 4.8 (85) |
| SWE-Bench Verified | 82.4 | ≈ Opus 4.7 (80.8), < Opus 4.8 (87.6) |
| SWE-Bench Pro | 62.2 | Competitive |
| NL2Repo | 48.9 | Strong |

### Strategic Value for Omega
| Dimension | Assessment |
|-----------|------------|
| **Context** | 1M tokens = entire codebase + docs + history in context |
| **Local Deployment** | ✅ Multiple frameworks; MoE = efficient for active params |
| **Sovereignty** | ✅ MIT license, no regional restrictions |
| **Agentic Coding** | ✅ Top-tier on Terminal-Bench, SWE-Bench |
| **Cost** | Free tier generous; local deployment = zero marginal cost |

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "1M context changes everything for agentic workflows. No more RAG for codebase context — full repo in context. MoE means 40B active fits on 2×A100 or 1×H100." |
| **Adversary** | "744B total params = massive VRAM for full weights. Quantized FP8 = ~150GB. Still needs serious hardware. Free tier has peak/off-peak complexity." |
| **Alchemist** | "GLM-5.2 + 1M context = perfect for our 'full codebase in context' agent loops. Pair with Ornith-9B for fast local iteration, GLM for heavy synthesis." |
| **Archivist** | "Precedent: GLM-5.1 was strong. 5.2 adds 1M context + MTP. Z.ai's MIT license is rare for Chinese lab — strategic openness." |

---

## 2. Ornith 1.0 (DeepReinforce AI)

### Source
- **Hugging Face**: https://huggingface.co/deepreinforce-ai/Ornith-1.0-9B
- **Blog**: https://deep-reinforce.com/ornith_1_0.html
- **Benchmarks**: https://benchlm.ai/compare/gemma-4-31b-vs-ornith-1-0-9b

### Key Specifications
| Attribute | Value |
|-----------|-------|
| **Architecture** | Dense 9B (also 31B, 35B MoE, 397B MoE variants) |
| **Base Models** | Post-trained on Gemma 4 + Qwen 3.5 |
| **License** | MIT (globally accessible) |
| **Context** | 256K tokens |
| **Specialization** | **Agentic coding** — self-improving RL scaffolds |

### The Innovation: Self-Scaffolding RL
> Instead of human-designed harnesses, Ornith learns to generate its own scaffolding (prompts, tool chains, verification steps) during RL training. Joint optimization of scaffold + solution.

### Benchmark Results (9B Dense)
| Benchmark | Ornith-9B | Gemma 4 31B | Qwen 3.5-9B | Qwen 3.5-35B |
|-----------|-----------|-------------|-------------|--------------|
| **Terminal-Bench 2.1** | **43.1** | 42.1 | 21.3 | 41.4 |
| **SWE-Bench Verified** | **69.4** | 52.0 | 53.2 | 70.0 |
| **SWE-Bench Pro** | **42.9** | 35.7 | 31.3 | 44.6 |
| **ClawEval Avg** | **63.1** | 48.5 | 53.2 | 65.4 |
| **NL2Repo** | **27.2** | 15.5 | 16.2 | 20.5 |

### Key Finding
> **Ornith-1.0-9B BEATS Gemma 4 31B on coding benchmarks** while being 3.4× smaller.

### Deployment
```bash
# vLLM
vllm serve deepreinforce-ai/Ornith-1.0-9B \
    --served-model-name Ornith-1.0-9B \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 262144 \
    --gpu-memory-utilization 0.90 \
    --enable-prefix-caching

# SGLang
python3 -m sglang.launch_server \
    --model-path deepreinforce-ai/Ornith-1.0-9B \
    --host 0.0.0.0 --port 30000 \
    --max-model-len 262144

# OpenCode Config
# ~/.config/opencode/opencode.json
{
  "provider": {
    "ornith": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ornith (local)",
      "options": { "baseURL": "http://localhost:8000/v1", "apiKey": "EMPTY" },
      "models": { "deepreinforce-ai/Ornith-1.0-9B": { "name": "Ornith-1.0-9B" } }
    }
  }
}
```

### Recommended Sampling
```python
temperature=0.6, top_p=0.95, top_k=20  # Benchmark reproduction
temperature=1.0  # For benchmark parity
```

### Strategic Value for Omega
| Dimension | Assessment |
|-----------|------------|
| **Size/Performance** | 9B beating 31B = massive efficiency win |
| **Local-First** | ✅ Single 24GB GPU (BF16) or 8GB (quantized) |
| **Agentic Coding** | ✅ Purpose-built for terminal-based agents |
| **Self-Improving** | ✅ Learns its own scaffolds — aligns with our Dream Cycle |
| **License** | ✅ MIT — fully sovereign |

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "Ornith-9B is the *local coding agent* model. Deploy on 1×RTX 3090/4090 or Mac M-series. Beats Gemma 4 31B on our hardware." |
| **Adversary** | "Only 9B/31B/35B/397B sizes. No 12B/27B sweet spot. 397B MoE needs 8×H100. Benchmark coverage still thin vs Gemma." |
| **Alchemist** | "Self-scaffolding RL = our Dream Cycle made native. Ornith generates its own verification harnesses. Could seed our Gnosis Graph." |
| **Archivist** | "Built on Gemma 4 + Qwen 3.5 — heritage traceable. MIT license = no [id-soft:] tags needed. DeepReinforce is new lab (2026)." |

---

## 3. MiniCPM5-1B (OpenBMB / Tsinghua)

### Source
- **GitHub**: https://github.com/OpenBMB/MiniCPM
- **Hugging Face**: https://huggingface.co/openbmb/MiniCPM5-1B
- **Ollama**: https://ollama.com/openbmb/minicpm5

### Key Specifications
| Attribute | Value |
|-----------|-------|
| **Parameters** | **1B** (not 51B — user note corrected) |
| **Context** | **128K tokens** |
| **License** | Apache 2.0 (open) |
| **Reasoning** | Hybrid: built-in `thinking` chat template, toggle via `enable_thinking` |
| **Deployment** | SGLang, vLLM, Ollama, MLX, llama.cpp, Unsloth |

### Agentic Tool Use (Core Differentiator)
| Capability | Details |
|------------|---------|
| **Function Calling** | Native, reliable at 1B scale |
| **Multi-step Tool Chains** | Plans → executes → evaluates → iterates |
| **Structured Output** | JSON schema compliance |
| **Error Recovery** | Handles tool failures gracefully |

### Benchmark Positioning
- **1B-class SOTA** for tool use, code generation, reasoning
- Beats Qwen3-0.6B/think, Qwen3.5-0.8B/think, LFM2.5-1.2B-thinking
- **Not** a frontier model replacement — specialized for *constrained agentic workflows*

### Deployment Matrix
| Platform | Command |
|----------|---------|
| **Ollama** | `ollama pull minicpm5` |
| **LM Studio** | Search "MiniCPM5-1B" (GGUF + MLX) |
| **SGLang** | `python -m sglang.launch_server --model-path openbmb/MiniCPM5-1B` |
| **vLLM** | `vllm serve openbmb/MiniCPM5-1B` |
| **llama.cpp** | Quantized GGUF available on HF |

### Strategic Value for Omega
| Dimension | Assessment |
|-----------|------------|
| **Edge Deployment** | ✅ Runs on phone, Raspberry Pi, laptop CPU |
| **Privacy-First** | ✅ Fully local, no data leaves device |
| **Agentic Loops** | ✅ Reliable tool calling at 1B = edge agents |
| **Cost** | ✅ Zero marginal cost, minimal hardware |
| **Limitation** | ❌ Not for complex reasoning / broad knowledge |

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "Perfect for P6 (Cognition) edge agents — sensor processing, local tool execution, privacy-sensitive workflows. Not for P3 (Engineering) heavy lifting." |
| **Adversary** | "1B model = hard ceiling on reasoning. Will hallucinate on complex tasks. Must sandbox with strict tool schemas and verification gates." |
| **Alchemist** | "MiniCPM5-1B + Ornith-9B + GLM-5.2 = full spectrum. Edge → Workstation → Cloud. Each tier handles its complexity class." |
| **Archivist** | "OpenBMB lineage: MiniCPM → MiniCPM-V → MiniCPM-o → MiniCPM5. Consistent 'small but mighty' thesis. Tsinghua NLP lab credibility." |

---

## 4. Agnes AI (Singapore-based Frontier Lab)

### Source
- **Platform**: https://agnes-ai.com / https://platform.agnes-ai.com
- **Hugging Face**: https://huggingface.co/Agnes-AI
- **GitHub**: https://github.com/lcy362/agnes-video-generator

### Model Suite (All Free Tier)
| Model | Modality | Benchmark Highlights |
|-------|----------|---------------------|
| **Agnes-2.0-Flash** | Text | ClawEval: **70.8%** (beats Opus 4.6 62.7%, GLM 5.1 60.2%) |
| **Agnes-2.5-Pro-Alpha** | Text + Image + Video → Text | Terminal-Bench 2.1: **67%** (beats Kimi K3 78%, GLM-5.2 85%) |
| **Agnes-Image-2.0** | Image | AA Image Editing Elo: **1250** (beats GPT Image 2 1240) |
| **Agnes-Video-V2.0** | Video | AA Image-to-Video Elo: **1066** (beats Kling 3.0 1000) |
| **Agnes-SeaLLM-8B** | Text (SEA languages) | SeaExam: **75.32** (beats Llama-Sea-Lion-v2 55.86) |

### Free API Access
- **Platform**: https://platform.agnes-ai.com
- **Cost**: **Completely free** — no trial, no watermarks, no usage limits
- **API Key**: Free registration
- **Rate Limits**: Generous (3M+ users, 2.97M MAU)

### Agnes Video Generator (Open Source)
- **Repo**: https://github.com/lcy362/agnes-video-generator
- **Stack**: Flask + ViMax (HKUDS) + Agnes AI APIs
- **Features**: Text-to-video, image-to-video, multi-scene, narration, subtitles, digital anchor
- **Deploy**: Docker, zero GPU required (cloud inference)

### Strategic Value for Omega
| Dimension | Assessment |
|-----------|------------|
| **Multimodal** | ✅ Text, Image, Video generation — all free |
| **Coding** | ✅ Agnes-2.5-Pro-Alpha: 67% Terminal-Bench |
| **Sovereignty** | ⚠️ Cloud API only (no local weights released yet) |
| **Cost** | ✅ Zero — generous free tier |
| **Risk** | 🔴 Single provider, no local fallback, Singapore jurisdiction |

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "Incredible multimodal free tier. But M7 violation if we depend on it. Use as *teacher* for distillation, not production dependency." |
| **Adversary** | "No local weights = single point of failure. Singapore jurisdiction = data sovereignty questions. Free tier could evaporate." |
| **Alchemist** | "Agnes-2.5-Pro-Alpha + 1M context GLM-5.2 = multimodal agent with huge context. Distill Agnes video understanding into local model?" |
| **Archivist** | "Bruce Yang (Berkeley Math/CS) founder. 'AI parity for the 99%' mission aligns with ours. But they're a *service*, not a *model release*." |

---

## Strategic Model Portfolio for Omega Engine

### Recommended Tiered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    OMEGA MODEL FABRIC                            │
├──────────────────┬──────────────────┬───────────────────────────┤
│     EDGE         │   WORKSTATION    │         CLOUD             │
│   (P6/P7/P10)    │   (P3/P4/P9)     │      (Fallback/Teacher)   │
├──────────────────┼──────────────────┼───────────────────────────┤
│ MiniCPM5-1B      │ Ornith-1.0-9B    │ GLM-5.2 (1M ctx)          │
│ 128K ctx         │ 256K ctx         │ 1M ctx                    │
│ Tool use         │ Agentic coding   │ Heavy synthesis           │
│ Edge/Phone       │ 24GB GPU / Mac   │ Free tier / Local MoE     │
├──────────────────┼──────────────────┼───────────────────────────┤
│ Agnes-2.5-Pro    │ Agnes-2.5-Pro    │ Agnes (multimodal)        │
│ (API)            │ (API)            │ (API - teacher only)      │
└──────────────────┴──────────────────┴───────────────────────────┘
```

### Routing Logic (ModelGateway Integration)
```python
# src/omega/oracle/model_routing.py
ROUTING_RULES = [
    # Edge: privacy, latency, offline
    {"task": "sensor_processing", "model": "minicpm5-1b", "tier": "edge"},
    {"task": "quick_tool_call", "model": "minicpm5-1b", "tier": "edge"},
    
    # Workstation: coding, agentic loops, local-first
    {"task": "coding_agent", "model": "ornith-1.0-9b", "tier": "workstation"},
    {"task": "code_review", "model": "ornith-1.0-9b", "tier": "workstation"},
    {"task": "refactoring", "model": "ornith-1.0-9b", "tier": "workstation"},
    
    # Cloud: heavy synthesis, multimodal, 1M context
    {"task": "full_repo_analysis", "model": "glm-5.2", "tier": "cloud", "context": "1M"},
    {"task": "multimodal_synthesis", "model": "agnes-2.5-pro", "tier": "cloud"},
    {"task": "video_understanding", "model": "agnes-video", "tier": "cloud"},
]
```

### Free Tier Sustainability Assessment

| Model | Free Tier Risk | Mitigation |
|-------|----------------|------------|
| **GLM-5.2** | Medium (promo ends Sept 2026) | Local MoE deployment viable |
| **Ornith-1.0** | Low (MIT license, weights released) | Fully local — zero risk |
| **MiniCPM5-1B** | Low (Apache 2.0, weights released) | Fully local — zero risk |
| **Agnes AI** | **High** (cloud-only, single provider) | Use as teacher only; distill locally |

---

## Proposals Generated

| Proposal ID | Title | Status |
|-------------|-------|--------|
| **PROP-RP02-001** | Add Ornith-1.0-9B to Provider Fabric (Workstation Tier) | 🟡 READY FOR REVIEW |
| **PROP-RP02-002** | Add MiniCPM5-1B to Provider Fabric (Edge Tier) | 🟡 READY FOR REVIEW |
| **PROP-RP02-003** | GLM-5.2 Integration with 1M Context Routing | 🟡 READY FOR REVIEW |
| **PROP-RP02-004** | Agnes AI as Teacher Model for Distillation Pipeline | 🟡 READY FOR REVIEW |
| **PROP-RP02-005** | Tiered Model Routing Policy (Edge/Workstation/Cloud) | 🟡 READY FOR REVIEW |

---

## L3 Universal Principles Extracted

1. **Model Specialization > Model Size** — Ornith-9B beats Gemma-31B on coding because it's *specialized*, not because it's bigger.

2. **Local Weights = Sovereign Optionality** — Any model without released weights (Agnes) is a service dependency, not a sovereign asset.

3. **Context Window as Architecture** — 1M context (GLM-5.2) eliminates RAG for codebase-scale tasks; changes agent loop design fundamentally.

4. **Tiered Deployment Matches Hardware Reality** — Edge (1B), Workstation (9B), Cloud (MoE 40B active) maps to actual user hardware distribution.

---

*⬡ OMEGA ⬡ SOVEREIGN-RESEARCHER ⬡ laguna-s-2.1-free ⬡ opencode ⬡ trc_research ⬡ RP-02-COMPLETE*