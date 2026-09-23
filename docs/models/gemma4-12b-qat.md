---
card_version: "1.0"
model_id: "gemma4-12b-qat"
provider: "Google DeepMind (official QAT GGUF)"
research_status: "candidate"
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

**Official Google quantization-aware-trained 12B** — a strict upgrade over
gemma-3-12b on this box: **64% faster (5.11 vs 3.12 t/s), 42% less energy per
token (7.42 vs 12.69 J), 1°C cooler peak**, same ~40W envelope. QAT (trained
with quantization in the loop) beats PTQ at 4-bit. Status `candidate` pending
full 18-run screen (deferred).

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

## Local Measurement (single probe with telemetry — 2026-09-23)

**Protocol**: single run, prompt 1 (JSON function), temp 0.1, ctx 4096,
num_predict=512, **`think: false`** (see Thinking-model note).
**Hardware**: i7-13620H, 16GB DDR5-5200 single-channel, `AllowedCPUs=0-11`,
`OLLAMA_NUM_THREADS=8`, `OLLAMA_MAX_LOADED_MODELS=1`, power profile: performance.
Telemetry: privilege-free `TelemetryCollector` (RAPL + thermal + freq, 2Hz).

| Metric | gemma4-12b-qat (Q4_0) | gemma-3-12b (IQ3_M) |
|---|---|---|
| Time (512 tok) | 100.3s | 163.8s |
| Throughput | **5.11 t/s** | 3.12 t/s |
| Energy/token | **7.42 J** | 12.69 J |
| Power mean/max | 38.08 / 50.14W | 39.8 / 50.2W |
| Temp mean/max | 86.36 / 97.05°C | — / 98.0°C |
| Freq mean | 3.46 GHz | 3.27 GHz |
| Answer | 1773 chars, correct JSON fn | correct JSON fn |

**Key findings**:
- +64% throughput, −42% energy/token vs gemma-3-12b, same power envelope.
- 1°C cooler peak with higher mean freq → less thermal throttling.
- Full 18-run screen estimate ≈ 30 min (deferred).

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
| Generalist reasoning (12B) | **High** | Strongest reasoning per token-class screened; **5.11 t/s measured** |
| Code tasks | **Medium** | Qwen2.5-Coder-7B still the pure-code specialist (HumanEval 88.4%) at 7.9 t/s |
| Daily driver | **Candidate** | 7GB resident fits MAX=1 budget; role pending full screen |
| Node 1 local inference | **Yes** | Fits with margin; thermals under ceiling |

**Verdict**: **`candidate`** — single probe confirms strict upgrade over
gemma-3-12b on every axis. Promote to `active` after full 18-run screen.

## Thinking-Model Note (harness gap)

Default (think on): the 512-token budget is consumed entirely by the think
trace → **empty answer** (same bug class as the Qwen3 infinite-think hang).
`"think": false` yields direct answers with comparable metrics. `screening.py`
`generate()` needs a `think` flag before any reasoning model
(phi4-mini-reasoning, this model in think mode) can be screened — open item.

## Evidence Labels

- Architecture/capability: provider (Google model card, tech report) — medium.
- Benchmarks (MMLU-Pro 77.2%, AIME 77.5%, LiveCodeBench 72%, GPQA 78.8):
  provider-reported — medium.
- Local speed/energy/thermals: measured single probe with telemetry — medium
  (single run, not full screen).

## Open Items

- Full 18-run screen with `think: false` (deferred; ~30 min).
- Thinking-mode quality eval (larger token budget; separate track).
- Role decision: daily-driver candidate vs specialist (pending full screen).
