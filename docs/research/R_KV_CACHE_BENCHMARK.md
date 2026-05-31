# R##: KV-Cache Quantization Benchmark — Zen 2 L3 Cache Impact
**AP**: `AP-RESEARCH-EXP004-v1.0.0`
**Status**: EXECUTING | **Date**: 2026-05-14

---

## Objective

Benchmark the impact of KV-cache quantization (f16, q8_0, q4_0) on Zen 2 performance metrics:
- **L3 cache hit rates** (primary hypothesis: lower bit-width → more tokens fit in 8MB L3 → higher hit rate)
- **Tokens per second** (throughput)
- **Memory consumption** (RAM savings vs. quality trade-off)

## Hardware Under Test

| Component | Detail |
|-----------|--------|
| CPU | AMD Ryzen 7 5700U (Zen 2, 8C/16T) |
| L3 Cache | 8MB shared (2× 4MB CCX) |
| RAM | 14Gi total (~12Gi available for AI) |
| GPU | None (CPU-only inference) |

## Hypothesis

> Reducing KV-cache precision from f16 → q8_0 → q4_0 will increase L3 cache hit rates because more tokens' KV representations fit in the 8MB shared L3 cache, reducing DRAM fetches. Expected trade-off: slight perplexity increase at q4_0 for long contexts.

## Test Protocol

### Models
1. **qwen3-1.7b-q6_k** (1.6GB, 32K context) — workhorse
2. **qwen3-4b-thinking-q4_k_m** (2.4GB, 32K context) — reasoning
3. **krikri-8b-q5_k_m** (5.5GB, 32K context) — deep knowledge

### KV Cache Configs
| ID | Key Type | Value Type | Memory/Token | Expected L3 Fit |
|----|----------|------------|-------------|-----------------|
| A | f16 | f16 | 4 bytes | ~2M tokens |
| B | q8_0 | q8_0 | 2 bytes | ~4M tokens |
| C | q4_0 | q4_0 | 1 byte | ~8M tokens |

### Metrics Collected
- `llama-server` performance metrics (t/s, decode time)
- `perf` L3 cache miss rates (if available)
- `/proc/meminfo` memory pressure
- Output token quality (perplexity on held-out set)

## Results

### Model: qwen3-1.7b-q6_k (1.6B params)

| KV Config | t/s | Peak RAM | L3 Miss Rate | Notes |
|-----------|-----|----------|-------------|-------|
| f16/f16 | — | — | — | _pending_ |
| q8_0/q8_0 | — | — | — | _pending (current default)_ |
| q4_0/q4_0 | — | — | — | _pending_ |

### Model: qwen3-4b-thinking-q4_k_m (4B params)

| KV Config | t/s | Peak RAM | L3 Miss Rate | Notes |
|-----------|-----|----------|-------------|-------|
| q4_0/q4_0 | — | — | — | _pending (current default)_ |

### Model: krikri-8b-q5_k_m (8B params)

| KV Config | t/s | Peak RAM | L3 Miss Rate | Notes |
|-----------|-----|----------|-------------|-------|
| q8_0/q8_0 | — | — | — | _pending (current default)_ |

## Analysis

_To be filled after benchmarking._

## Recommendations

_To be determined._