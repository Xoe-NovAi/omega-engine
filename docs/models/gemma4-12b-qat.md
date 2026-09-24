---
card_version: "1.0"
model_id: "gemma4-12b-qat"
provider: "Google DeepMind (official QAT GGUF)"
research_status: "active"
deployment: "local"
last_verified: "2026-09-23"
confidence: "metadata:high,benchmarks:medium,local_performance:medium"
license: "Apache-2.0"
context_length: 262144
modalities_in: ["text"]
modalities_out: ["text"]
local_hardware_profile:
  cpu: "i7-13620H"
  cpu_cores: 10
  cpu_threads: 16
  allowed_cpus: "0-11"
  threads: 8
  ram_gb: 16
  ram_type: "DDR5-5200 single-channel"
  kv_cache_type: "q8_0"
  flash_attention: false
  max_loaded_models: 1
  quantization: "Q4_0"
reproducibility:
  seed: 42
  config_hash: "sha256:93567e57a8fe10b23569b9d9ec38cd005deedf71e29477c421a4b83f418a538b"
  environment:
    ollama_version: "0.33.3"
    llama_cpp_version: "b4000+"
    hardware: "i7-13620H, 16GB DDR5-5200 single-channel"
---

# Gemma 4 12B QAT (q4_0 GGUF)

## Executive Summary

**Official Google quantization-aware-trained 12B** — confirmed by a 3-prompt
lite screen as a strict upgrade over gemma-3-12b on this box: **45% faster
(4.54 vs 3.12 t/s), 49% less energy per token (6.50 vs 12.69 J), and a 92°C
observed peak**. QAT (trained with quantization in the loop) beats PTQ at 4-bit.
Status `active`: generalist/reasoning model, while qwen2.5-coder-7b remains the
code-first driver.

## Architecture

| Spec | Gemma 4 12B Unified |
|------|---------------------|
| Total params | 11.95B |
| Layers | 48 |
| Attention | Hybrid: 512-token sliding window + global (last layer global) |
| Context length | 256K (harness uses 4096) |
| Vocabulary | 262K |
| Embedding length | 3840 |
| Modalities | Text, image, audio, video (encoder-free; GGUF text-only via Ollama) |
| Extras | 400M MTP drafter head (speculative decoding); `thinking` capability |
| Source file | `gemma-4-12b-it-qat-q4_0.gguf` (6,975,879,296 bytes, sha256 verified) |
| Reference | arXiv 2607.02770; Apache 2.0 |

## Local Measurement (3-prompt lite screen — 2026-09-23)

**Protocol**: 3 prompts × temp 0.1 × ctx 4096, num_predict=512,
**`think: false`**, RAPL + thermal + frequency telemetry at 2 Hz.
**Hardware**: i7-13620H, 16GB DDR5-5200 single-channel, `AllowedCPUs=0-11`,
`OLLAMA_NUM_THREADS=8`, `OLLAMA_MAX_LOADED_MODELS=1`, performance power profile.
Raw result: `benchmarking/screening/gemma4-12b-qat_lite_screening.json`.

| Metric | gemma4-12b-qat (Q4_0) | gemma-3-12b (IQ3_M) |
|---|---|---|
| Throughput | **4.54 t/s average** (4.13–4.84) | 3.12 t/s |
| Energy/token | **6.50 J average** (5.74–7.74) | 12.69 J |
| Package power | 29.41 W mean | ~40 W observed |
| Peak temperature | **92.05°C** | 98°C |

**Key findings**:
- +45% throughput and −49% energy/token vs gemma-3-12b across the lite screen.
- Peak temperature remained below the earlier 97–98°C observations.
- All three runs completed without errors at the 512-token cap; this confirms
  operational fitness, while broader temperature/context sensitivity remains
  optional follow-up rather than a promotion blocker.

## Provider Claims

| Benchmark | Gemma 4 12B | Evidence |
|---|---|---|
| MMLU-Pro | 77.2% | Provider claim |
| AIME 2026 | 77.5% | Provider claim |
| LiveCodeBench v6 | 72.0% | Provider claim |
| Codeforces ELO | 1659 | Provider claim |
| GPQA Diamond | 78.8% | Provider claim |
| Context window | 256K, 140+ languages | Provider claim |

## Omega Verdict

| Workload | Fit | Reason |
|----------|-----|--------|
| Generalist reasoning (12B) | **High** | Best generalist/reasoning fit; **4.54 t/s average measured** |
| Code tasks | **Medium** | Qwen2.5-Coder-7B remains the pure-code specialist (HumanEval 88.4%) at 7.9 t/s |
| General daily driver | **High** | Use Gemma 4 QAT for explanation, analysis, and mixed tasks with `think:false` |
| Code daily driver | **Route to Qwen** | Keep qwen2.5-coder-7b as the default for repository/code generation |
| Node 1 local inference | **Yes** | Fits with margin; 92.05°C observed peak |

**Verdict**: **`active`** — the 3-prompt lite screen confirms the strict
upgrade over gemma-3-12b. Role: generalist/reasoning driver; qwen2.5-coder-7b
remains the code specialist.

## Thinking-Model Note (harness resolved)

Default (think on): the 512-token budget can be consumed entirely by the think
trace → **empty answer** (same bug class as the Qwen3 infinite-think hang).
`"think": false` yields direct answers. The screening harness now sends this
explicitly: `--think off` is the default, `--think on` is available, and the
selected mode is recorded in each result JSON. Lite screen evidence used
`think:false`.

## Evidence Labels

- Architecture/capability: provider (Google model card, tech report) — medium.
- Benchmarks (MMLU-Pro 77.2%, AIME 77.5%, LiveCodeBench 72%, GPQA 78.8):
  provider-reported — medium.
- Local speed/energy/thermals: measured 3-prompt lite screen with telemetry —
  medium (representative setting; not the full 18-run matrix).

## Open Items

- Optional full 18-run temperature/context matrix for research confidence.
- Thinking-mode quality eval (larger token budget; separate track).
