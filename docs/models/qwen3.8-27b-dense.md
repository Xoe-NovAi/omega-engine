---
card_version: "1.0"
model_id: "qwen3.8-27b-dense"
provider: "Alibaba / Qwen Team"
research_status: "rejected"
deployment: "not_deployed"
last_verified: "2026-09-22"
confidence: "metadata:high,architecture:high,performance:medium"
license: "Apache-2.0"
context_length: 262144
modalities_in: ["text", "image", "video"]
modalities_out: ["text"]
reproducibility:
  seed: 42
  config_hash: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  environment:
    ollama_version: "0.33.3"
    llama_cpp_version: "b4000+"
    hardware: "i7-13620H, 16GB DDR5-5200 single-channel"
---

# Qwen3.8-27B Dense Architecture Analysis

## Executive Summary

**Qwen3.8-27B is a DENSE model, NOT a Mixture-of-Experts (MoE) model.** All 27.8 billion parameters are active on every forward pass. This is confirmed by multiple authoritative sources.

## Architecture Confirmation

| Source | Verdict | Evidence |
|--------|---------|----------|
| NVIDIA Developer Blog (2026) | "Qwen3.8-27B: Dense; hybrid linear/full attention; MTP head; multimodal. **Active params: 27B**" | Independent eval |
| Kingy AI Specs | "Checkpoint type: **Post-trained dense causal VLM**" | Community benchmark |
| Sebastian Raschka | "Difference between dense Qwen and MoE Qwen is mainly in the feed-forward part" | Independent eval |
| Qwen Blog | Benchmarks table lists "Dense200" category | Provider claim |

## Implications for Local Inference (16GB RAM)

### Why Expert Offloading Does NOT Work

- **`--cpu-moe` / `--n-cpu-moe` / `-ot "exps=CPU"`** — These flags only apply to MoE models with routed experts
- **Dense models have no router, no experts** — Every FFN layer is a monolithic matrix that must be fully loaded
- **GGUF file size ≈ RAM footprint** — Q4_K_M = 18.5GB, UD-Q2_K_XL = 9.8GB

### MoE Offloading Reality Check

| Flag | Actual Effect |
|------|---------------|
| `--cpu-moe` | Moves ALL routed experts from VRAM → system RAM |
| `--n-cpu-moe N` | Moves first N layers' experts to RAM |
| **Does NOT do** | Stream inactive experts from NVMe on-demand |

True on-demand expert paging from disk exists only in `solid.cpp` fork (private, Apple Metal, 0.12 tok/s — unusable on Linux/CPU).

## Quantization Options for 16GB RAM

| Quant | Size | Total RAM (est.) | Quality | Fits? |
|-------|------|------------------|---------|-------|
| UD-Q2_K_XL | 9.83 GB | ~13 GB | Quality floor for coding | ✅ Tight |
| UD-Q3_K_XL | 13.1 GB | ~16 GB | Near Q4 quality | ⚠️ Tight |
| UD-Q4_K_M | 16.5 GB | ~19 GB | Best quality | ❌ No |

**UD-Q2_K_XL (9.83 GB)** is the quality floor for coding/agentic work per Unsloth benchmarks.

## MoE Alternatives That Fit 16GB RAM

| Model | Total / Active | Best Quant | Size | Quality Signal |
|-------|----------------|------------|------|----------------|
| Devstral Small 2505 | 23.6B / ~8B | Q4_K_M | 13.4 GB | 46.8% SWE-Verified, agentic design |
| gpt-oss-20b | 20B / ~4B | Q4 | 12.8 GB | o3-mini reasoning |
| Qwen3.5-35B-A3B | 35B / 3B | UD-Q2_K_XL | 12.2 GB | 69.2% SWE-Verified |

## Strategic Decision

**Pivot to Qwen2.5-Coder 7B/14B (dense, Apache-2.0, fit comfortably on 16GB)**

| Model | Quant | Model Size | Total RAM (est.) | Use Case |
|-------|-------|------------|------------------|----------|
| Qwen2.5-Coder-7B | Q4_K_M | 4.68 GB | ~8.2 GB | Daily driver, long context headroom |
| Qwen2.5-Coder-7B | Q5_K_M | 5.44 GB | ~9.0 GB | Higher quality, less headroom |
| Qwen2.5-Coder-14B | Q4_K_M | 7.34 GB | ~10.8 GB | Complex tasks, when 32GB arrives |

**Evidence**: Qwen2.5-Coder-7B beats GPT-4 on HumanEval (88.4% vs 87.1%), 69.6% SWE-Bench Verified (surpasses Claude/GPT-4). Apache-2.0 license on all.

## Key Takeaway

**MoE saves compute (FLOPs/token), NOT storage.** Total parameters determine RAM footprint, not active parameters. There is no free lunch — dense backbone + expert pool must fully reside in RAM.

## Local Measurement

*No local measurements available.* Model rejected for local inference on 16GB Node 1 due to RAM constraints even at minimum quality quantization.

## Provider Claims

| Claim | Evidence |
|-------|----------|
| 27B active parameters (dense) | Provider claim |
| Hybrid linear/full attention | Provider claim |
| Multimodal (text, image, video) | Provider claim |
| 262K context length | Provider claim |

## Omega Verdict

| Workload | Fit | Reason |
|----------|-----|--------|
| Node 1 local inference (16GB) | **No** | Minimum quality quant (UD-Q2_K_XL) needs ~13GB RAM; tight with headroom |
| Coding/agentic work | **Rejected** | UD-Q2_K_XL is quality floor; below this quality degrades unacceptably |
| Future 32GB upgrade | **Candidate** | UD-Q4_K_M would fit comfortably with headroom |
| Cloud/hosted inference | **Possible** | 262K context + multimodal could be valuable via API |

**Verdict**: `rejected` for Node 1 local inference; pivot to Qwen2.5-Coder 7B/14B.

## Operating recipe

*Not applicable for local deployment on Node 1.*

## Sources

All sources accessed 2026-09-22:

- [NVIDIA Developer Blog: Dense vs MoE Models](https://developer.nvidia.com/blog/dense-vs-moe-models-active-parameters-throughput-and-when-to-choose-each/)
- [Kingy AI: Qwen3.8-27B Specs](https://kingy.ai/blog/qwen3-8-27b-specs-benchmarks-local-hardware/)
- [Sebastian Raschka: Dense vs MoE Qwen](https://sebastianraschka.com/faq/docs/dense-qwen-vs-moe-qwen.html)
- [Qwen Blog: Qwen3.8-Max](https://qwen.ai/blog?id=qwen3.8)
- [Unsloth Qwen3.8-27B GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF)
- [Local AI Zone: Qwen3.8-27B Analysis](https://local-ai-zone.github.io/blog/qwen3-8-27b-comprehensive-analysis.html)

## Reproducibility

```yaml
reproducibility:
  seed: 42
  config_hash: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  environment:
    ollama_version: "0.33.3"
    llama_cpp_version: "b4000+"
    hardware: "i7-13620H, 16GB DDR5-5200 single-channel"
```