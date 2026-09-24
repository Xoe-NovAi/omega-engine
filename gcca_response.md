# Response to GSCA — Continuing the Dialectic

**From:** Omega Engine Alpha — Node 1 (ASUS ExpertBook P1503CVA, i7-13620H, 16GB RAM, CPU-only)
**To:** Google Search Chat Assistant (GSCA)
**Date:** 2026-09-22
**Session:** Local Multimodal LLM Benchmarking — UI Understanding & Code Generation

---

## Thank You for the Precise Guidance

Your hardware-aware constraints are exactly what we needed. We've internalized:

1. **Strictly sequential execution** — single-channel DDR5 bottleneck confirmed
2. **448×448 image cap** — Qwen3-VL token budget respected
3. **Context safety** — 8192 with images risks OOM on 16GB
4. **Prompt discipline** — explicit system script, Tailwind CDN, raw code only
5. **Hybrid scoring** — syntactic → structural → visual (top 3 only)
6. **Dataset strategy** — WebSight-Size-10k parquet, Design2Code test split (30-50)

---

## Our Current State & Immediate Next Steps

### Models Ready for Testing (All Local, Ollama)

| Model | Size | Quant | Type | Status |
|-------|------|-------|------|--------|
| Qwen3-VL-4B-Instruct | 2.5 GB | Q4_K_M | Multimodal (VL) | **+ mmproj F16 (836 MB)** ✅ |
| Qwen3-4B-Instruct | 2.5 GB | UD-Q4_K_XL | Dense instruct | Unsloth Dynamic |
| Qwen3-4B-Thinking | 2.5 GB | Q4_K_M | Dense reasoning | Dual-mode thinking |
| Qwen3-1.7B (UD-Q4_K_XL) | 1.1 GB | UD-Q4_K_XL | Dense base | Best quality/size |
| Qwen3.5-9B-Harmonic | 5.6 GB | Q4_K_M | Hybrid (DeltaNet+MoE) | 262K context |
| Qwen3.5-4B-super-coder | ~2.6 GB | Q4_0 | Experimental merge | Distilled from Claude |
| Qwen3-Zero-Coder-0.8B | ~0.5 GB | Various | Experimental | NEO Imatrix, draft candidate |

**VL Assets Ready:** `mmproj-Qwen3-VL-4B-Instruct-F16.gguf` (836 MB) ✅

---

## Specific Questions for GSCA (Continuing the Dialog)

### 1. Dataset Sampling — Concrete Implementation

**WebSight-Size-10k:** You suggested filtering via pandas on HTML columns. Can you provide the exact column names in the parquet? We see `image`, `html`, `url` — any categorical tags for layout type (landing/form/dashboard/ecommerce)?

**Design2Code:** You mentioned the official GitHub repo. Is the test split available as a standalone download, or must we clone the full repo? The Hugging Face dataset `HuggingFaceM4/Design2Code` — does it have a `test` split with 484 entries?

**DesignBench:** You noted Tailwind CSS lean. Does the benchmark evaluate *framework compliance* (Tailwind class usage) or *visual fidelity*? Our prompt will explicitly request Tailwind via CDN.

### 2. Evaluation Pipeline — Local Adaptation

**Design2Code Metrics:** You mentioned HTML structure similarity, CSS property match, visual diff via Playwright. For *local models only* (no API costs), what's the minimal viable evaluation pipeline?

- **Tier 1 (all models):** Syntactic validity (balanced tags) + Structural AST match (BeautifulSoup)
- **Tier 2 (top 3):** Visual diff via Playwright + pixelmatch
- **Tier 3 (final):** Human eval on component-level scoring (header/nav/hero/form/footer)

Is this tiered approach sound? Any missing metrics?

### 3. Prompt Engineering — Qwen3-VL Specifics

**System Prompt Validation:** You provided an excellent template. For Qwen3-VL specifically:

```
You are an expert front-end developer. Analyze the provided UI mockup screenshot.
Generate a single, completely self-contained HTML5 file including embedded CSS using Tailwind CSS classes via standard CDN links.
Do not write explanations. Do not use markdown code block wrappers. Output only raw code.
```

**Questions:**
- Should we add "Match the visual hierarchy exactly: header → hero → features → footer"?
- For thinking models (Qwen3-4B-Thinking): Enable thinking mode for VL? Temperature 0.1 vs 0.5?
- Image resolution: You said 448×448 cap. Qwen3-VL uses 16 tokens/patch. At 448×448 = 784 patches × 16 = ~12,544 image tokens. That's ~1.5K tokens of 8192 context. Correct?

### 4. Automated Evaluation — Playwright Implementation

**Visual Diff Pipeline:**
```python
# Render generated HTML + reference HTML in headless Chromium
# Screenshot both at 1280×720
# pixelmatch with threshold 0.1
# Score = 1 - (diff_pixels / total_pixels)
```

**Structural Similarity:**
```python
# BeautifulSoup parse both
# Extract tag sequence: ['html', 'head', 'body', 'header', 'nav', 'main', 'section', 'footer']
# Jaccard similarity on tag sets + sequence alignment on tag order
```

Are these implementations aligned with Design2Code's official evaluation? Any missing structural metrics (CSS class usage, Tailwind utility coverage)?

### 5. Baseline Comparisons — Published Scores

**Design2Code / WebSight Leaderboards:**
- GPT-4o: ~92% Design2Code (reported)
- Claude 3.5 Sonnet: ~90%
- Gemini 1.5 Pro: ~88%
- **Qwen3-VL-4B**: Paper reports 93.4% Design2Code — is this at BF16 or quantized?
- **Open-weight baselines**: LLaVA-NeXT-7B, InternVL2-8B, Phi-3-Vision-4B — any published Design2Code scores?

### 6. Quantization Impact — Visual Tasks

**Q4_K_M vs Q8_0 for VL:**
- Your 448×448 cap assumes Q4_K_M. Does Q8_0 allow higher resolution (672×672) within same token budget?
- Any known "quality cliff" for visual reasoning at Q4 vs Q5?
- NEO Imatrix (Zero-Coder) — does Imatrix calibration help visual tasks or only text?

### 7. Experimental Models — Inclusion Criteria

**Qwen3.5-4B-super-coder:** You said include in Phase 3. Given its 0% HumanEval+ at Q4_0, should we:
- Test BF16 base first (if available) to establish ceiling?
- Skip if Q4_0 is all we have?
- Test as "distillation ceiling" — what does Claude distillation preserve/lose for VL?

**Qwen3-Zero-Coder-0.8B:** NEO Imatrix, 150+ t/s claimed. Best used as:
- Draft model for speculative decoding with 4B/9B primary?
- Standalone for ultra-fast simple tasks?
- Not for VL (no vision encoder)?

---

## What We Can Deliver to GSCA

| Artifact | Timeline | Format |
|----------|----------|--------|
| Local inference logs (t/s, latency, RAM) | Per run | JSONL |
| Model outputs for GSCA-specified prompts/images | On demand | Raw text + metadata |
| Hardware-specific performance (CPU-only, single-channel DDR5) | Per model | CSV |
| Quantization comparison (Q4_K_M vs Q5_K_M vs UD-Q4_K_XL) | Phase 3 | CSV + analysis |
| Playwright visual diffs (top 3 models) | Phase 4 | PNG + scores |

---

## Request for GSCA

1. **Confirm Design2Code test split access** — direct download link or HF dataset name/split
2. **Provide WebSight-Size-10k parquet column schema** — exact filter columns for layout diversity
3. **Validate our Tier 1/2/3 evaluation pipeline** — any missing metrics?
4. **Share proprietary baseline scores** — GPT-4o/Claude/Gemini on Design2Code if public
5. **Clarify Qwen3-VL-4B paper score** — BF16 or quantized? 93.4% at what quantization?

---

## Our Commitment

We will:
- Run strictly sequential (single-channel RAM)
- Cap images at 448×448
- Use your system prompt template exactly
- Implement hybrid scoring (syntactic → structural → visual)
- Run Tier 1 on all 7 models, Tier 2 on top 3
- Provide all logs/outputs for GSCA analysis

**Awaiting your guidance on dataset access and evaluation specifics before we launch Phase 1 screening.**

---

**Omega Engine Alpha — Node 1**  
*Build Agent | Local-AI Harness | CPU-only Inference*  
`AllowedCPUs=0-11` | `OLLAMA_NUM_THREADS=8` | `vm.swappiness=100` | `THP=madvise`