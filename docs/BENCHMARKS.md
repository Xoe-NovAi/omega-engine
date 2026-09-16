# Benchmarks

Harness: opencode interactive agent + `make bench` (`scripts/bench.py`).
Host: i7-13620H CPU-only, 16GB single-channel DDR5-5200. See `docs/HARDWARE.md`.
Config at time of measurement: `AllowedCPUs=0-11`, `OLLAMA_NUM_THREADS=8`,
`OLLAMA_CONTEXT_LENGTH=8192`, `OLLAMA_KV_CACHE_TYPE=q8_0`, `OLLAMA_FLASH_ATTENTION=1`,
`OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_KEEP_ALIVE=30m`.

## 2026-09-08 — Head-to-head (2 prompts, warm)

| Model            | Prompt | Tokens | Time   | t/s  | Note |
| ---------------- | ------ | ------ | ------ | ---- | ---- |
| phi4-mini        | 1      | 27     | 2.1s   | 13.0 | —    |
| phi4-mini        | 2      | 530    | 39.3s  | 13.5 | —    |
| **phi4-mini avg**|        | 278    | 20.7s  | **13.5** | |
| qwen2.5-coder:7b | 1      | 32     | 9.9s   | 3.2  | cold load (t/s skews low) |
| qwen2.5-coder:7b | 2      | 368    | 46.4s  | 7.9  | steady state |
| **qwen2.5-coder:7b avg**|  | 200 | 28.1s  | **7.1** | |
| deepseek-r1:8b   | 1      | 353    | 54.2s  | 6.5  | reasoning tokens count |
| deepseek-r1:8b   | 2      | 364    | 51.2s  | 7.1  | steady state |
| **deepseek-r1:8b avg** |   | 358    | 52.7s  | **6.8** | |

Notes:
- phi4-mini still the fastest on this box (~2× qwen2.5-coder, ~2× deepseek-r1).
- Post-run RAM tight: 12Gi used, ~2.0Gi available, swap climbed to 1.4Gi — a
  clue the 2-model resident window (phi4-mini + deepseek) exceeds single-channel
  headroom. See memory headroom tests below.

## 2026-09-08 — Memory headroom: MAX_LOADED_MODELS 1 vs 2

| Config | phi4-mini t/s | Resident | Available | Swap |
| ------ | ------------- | -------- | --------- | ---- |
| MAX=2 (2 models resident) | 13.5 | 11.3GB (qwen+deepseek) | 1.9Gi | 1.4Gi (thrash) |
| MAX=1 (1 model resident)  | 13.4 | 3.2GB (phi4-mini) | 9.2Gi | ~0 |

**Decision: keep `OLLAMA_MAX_LOADED_MODELS=1`.** Single-channel 16GB can't hold
two residents with OS headroom; the swap thrash under MAX=2 (visible as cold-load
t/s dips: qwen prompt-1 3.2 t/s, deepseek prompt-1 6.5 t/s) outweighs the model-
switch reload cost of MAX=1. phi4-mini steady-state unchanged (13.4 vs 13.5).

## Quantization comparison (7B models, CPU inference)

| Quant | Size | RAM Needed | Quality (ppl Δ) | Speed vs FP16 | Best For |
|-------|------|------------|-----------------|---------------|----------|
| **Q4_K_M** | ~4.1 GB | 7 GB | +0.05 | Baseline | **General purpose — sweet spot** |
| **Q5_K_M** | ~4.8 GB | 8 GB | +0.014 | ~same | Code, reasoning (better tool calls) |
| **Q6_K** | ~5.5 GB | 9 GB | +0.007 | ~same | High-accuracy needs |
| **Q8_0** | ~7.0 GB | 11 GB | +0.0004 | ~same | Near-lossless reference |
| Q3_K_M | ~3.3 GB | 6 GB | +0.15 | Faster | Draft generation, edge |

Sources: arXiv:2601.14277 (unified eval Llama-3.1-8B), ggml #2094, Qwen3 quantization guide, OmniCoder benchmarks.

**Installed models:** phi4-mini (Q4_K_M), qwen2.5-coder:7b (Q4_K_M), deepseek-r1:8b (Q4_K_M) — all at sweet spot.
**Candidate:** deepseek-r1:8b → Q5_K_M for tool-call reliability in agentic coding.

## KV Cache quantization impact (phi4-mini, 8k ctx)

| KV Type | Resident Size | Throughput | Notes |
|---------|---------------|------------|-------|
| f16 (baseline) | 3.7 GB | 13.3 t/s | Default |
| q8_0 | 3.2 GB | 13.4 t/s | **~0.5GB freed, no regression** |
| q4_k (future) | ~2.8 GB est. | TBD | ~75% KV RAM, <0.1 ppl Δ (awaits upstream) |

## Regression checks (tuning)

- 2026-09-08, phi4-mini, 3 prompts warm: **13.4 t/s** w/ KV `q8_0` + flash-attn
  vs **13.3 t/s** baseline f16 KV — no throughput regression, and resident size
  dropped 3.7 → 3.2GB at 8k ctx.

## CPU thread sweep (ground truth)

| Threads | AllowedCPUs | phi4-mini t/s | Notes |
|---------|-------------|---------------|-------|
| 6 | 0-11 | 14.0 | Physical P-cores only |
| **8** | **0-11** | **14.4** | **Peak (P-cores + HT siblings)** |
| 10 | 0-11 | 14.17 | Includes 2 E-core threads |
| 12 | 0-11 | 13.88 | All HT threads |
| 6 | 0,2,4,6,8,10 | ~0.5 | **TRAP — spin-wait convoy (ollama #17916)** |

### Why 8 Threads Wins (Scheduler + Barrier Analysis)

| Threads | Scheduler Behavior | Barrier Dynamics |
|---------|-------------------|------------------|
| **6** | All 6 physical P-cores busy | No HT elasticity; all threads hit barrier simultaneously → stall |
| **8** | 6 P-cores + 2 HT siblings free | **Optimal** — waiters absorb on HT siblings; workers on physical; OS headroom |
| **10–12** | E-core threads enter | E-cores lack AVX2/VNNI → slower GEMM; or all HT → convoy risk |
| **>12** | E-cores active | Memory contention, no AVX2 benefit |

**Kernel context:** Linux ≥ 5.16 correctly schedules P→E→HT (not P→HT→E). Your kernel 7.0 has full ITD/HFI support — the scheduler places AVX2-heavy llama.cpp threads on P-cores automatically when mask allows.

## Older ground truth

- `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8` → **14.4 t/s** (swept 6→14.0/8→14.4/10→14.17/12→13.88).
- P-core-only pin (`0,2,4,6,8,10`) → ~0.5 t/s barrier convoy. DO NOT REGRESS.

## Pending benchmarks

- [ ] `bench-all` full sweep across all 8 installed models
- [ ] 10-min sustained phi4-mini + `turbostat` / `sensors` log (thermal validation)
- [ ] Q5_K_M vs Q4_K_M deepseek-r1:8b (tool-call quality vs speed)
- [ ] ZRAM 8GB vs 4GB swap.img (memory pressure test)
- [ ] THP `madvise` vs `always` (latency spike measurement)