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

> These are point-in-time benchmark results. Current swap state is zRAM-only;
> the `~0` swap figure below describes this benchmark run, not a system invariant.

| Config | phi4-mini t/s | Resident | Available | Swap |
| ------ | ------------- | -------- | --------- | ---- |
| MAX=2 (2 models resident) | 13.5 | 11.3GB (qwen+deepseek) | 1.9Gi | 1.4Gi (thrash) |
| MAX=1 (1 model resident)  | 13.4 | 3.2GB (phi4-mini) | 9.2Gi | ~0 in this benchmark |

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

## 2026-09-23 — Gemma 4 12B QAT 3-prompt lite screen (think:false, 512-cap)

Official Google `gemma-4-12b-it-qat-q4_0.gguf` (6.98GB, sha256 verified),
3 prompts, ctx=4096, temp=0.1, `think:false`; RAPL/thermal/freq telemetry at
2 Hz. Versus gemma-3-12b (IQ3_M) baseline:

| Metric | gemma4-12b-qat | gemma-3-12b |
|---|---|---|
| Throughput | **4.54 t/s average** (4.13–4.84) | 3.12 t/s |
| Energy/token | **6.50 J average** (5.74–7.74) | 12.69 J |
| Package power | 29.41W mean | ~40W observed |
| Peak temperature | 92.05°C | 98.0°C |

Verdict: **active** — strict upgrade across the representative screen
(+45% speed, −49% J/tok). Raw result:
`benchmarking/screening/gemma4-12b-qat_lite_screening.json`. Card:
`docs/models/gemma4-12b-qat.md`. The harness now exposes `--think {on,off}`
(default off) and `--lite`; the full 18-run matrix is optional follow-up.

## Pending benchmarks

- [ ] `bench-all` full sweep across all 8 installed models
- [ ] 10-min sustained phi4-mini thermal validation — now privilege-free: `scripts/screening.py` TelemetryCollector (RAPL + thermal + freq sysfs, no sudo); turbostat optional for forensic runs (see `docs/TELEMETRY_PLAN.md`)
- [ ] Q5_K_M vs Q4_K_M deepseek-r1:8b (tool-call quality vs speed)
- [x] ZRAM 8GB active; NVMe-backed `/swap.img` disabled and retained for rollback (2026-09-23)
- [ ] THP `madvise` vs `always` (latency spike measurement)