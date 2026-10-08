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

## 2026-10-07 — Thread curves, E-core isolation, engine parity (LFM + Krikri)

Raw data: `logs/20261007-threads/` (JSON runs, turbostat logs, harness scripts).
Host: i7-13620H (6P+4E/16T, AVX2+AVX-VNNI ceiling — no AVX-512; fused off on
Raptor Lake-H), 16GB single-channel DDR5-5200, CPU-only. Engine: raw
`llama-server` (Ollama 0.34.4 build, ggml `libggml-cpu-alderlake`) vs
`llama-cpp-python 0.3.36` (venv, `CMAKE_ARGS=-DGGML_NATIVE=ON`).

### Engine parity (no difference)

Same LFM2.5-2.6B-heretic Q4_K_M file, same prompt, 64 tokens, matched settings
(c=8192, t=6, b=1024/ub=512, FA on, KV q8_0):

| Engine | Wall | Decode | Load |
|---|---|---|---|
| raw `llama-server` :8089 | 3.22s | 20.4 t/s (server timings) | pre-loaded |
| `llama-cpp-python` 0.3.36 | 3.22s | ~19.9 t/s | 0.64s (mmap) |

**The Python binding is free** — in-process `Llama()` matches the HTTP server to
the third decimal. mmap load (0.6s) beats Ollama's `--load-mode none` (~2.5s) for
load/unload worker patterns.

### LFM thread curve (idle, isolated) — peak at t=6

| t | 4 | 5 | **6** | 8 | 10 | 12 | 16 |
|---|---|---|---|---|---|---|---|
| dec t/s | 19.7 | 20.4–20.7 | **21.2** | 20.5 | 20.3 | 20.1 | 19.4 |

Beyond 6, decode *falls* — single-channel bandwidth saturates; extra threads
fight the bus and the OS. Matches the tag: `lfm25-t6` keeps `num_thread 6`.

### The embedder misplacement (root cause of "WebUI is 5x slower" residuals)

`qwen3-embedding:0.6b` auto-loaded by the **primary** Ollama can only use CPUs
0-11 (`AllowedCPUs`) — its 10 runner threads squatted on the P-cores and LFM
collapsed **21.2 → 4.6 t/s (−78%)** with 5-vs-6 thread differences lost in the
noise. Fix deployed and verified: `scripts/embed_service.py install` →
`ollama-embed.service` (second instance, `:11435`, `AllowedCPUs=12-15`,
`OMP_NUM_THREADS=4`); runner affinity confirmed `12-15` at runtime. This is the
design already documented in that script's docstring — Intel Thread Director is
not available on Linux, explicit pinning is the mechanism.

### LFM under true E-core load — keep t=6

| Loaded (E-hammer active) | t=4 | t=5 | **t=6** |
|---|---|---|---|
| decode t/s | 18.0 | 18.7–18.8 | **18.6–18.9** |
| TTFT | 0.18–0.21s | 0.16–0.18s | 0.17s |

**Decision: LFM tag stays `num_thread 6`.** Isolated E-core load costs only
~11% (vs 78% unisolated).

### Performance-mode rerun (scaling governor `performance`, whole matrix)

| t=6, E-hammer | governor=powersave | governor=performance |
|---|---|---|
| LFM loaded | 18.8 | **19.6–20.0 (+5%)** |
| LFM loaded TTFT | 0.17s | **0.12–0.15s (−25%)** |
| Krikri loaded | 6.6–6.7 | 5.8–6.2 |

Prompt eval and loaded decode are clock-sensitive → performance governor kept.
Krikri's loaded dip under performance mode: faster E-cores consume more memory
bandwidth — on a bandwidth-bound model the hammer itself gets heavier.

### Krikri thread curve → **decision: `num_thread 4`**

| t | 3 | **4** | 6 | 8 |
|---|---|---|---|---|
| idle t/s | 6.27 | **6.67** | 6.50 | ~6.2 |
| loaded t/s | 6.10 | **6.27** | 5.97 | — |

- Peak at exactly **t=4**, corroborated by STREAM (32.6 GB/s saturates at 4–5
  threads) and by params/speed linearity: 8B÷2.6B = 3.1× params, 21.2÷6.5 =
  3.3× slower — pure bandwidth wall, thread count is secondary.
- **Decision applied 2026-10-07**: Krikri tag rebuilt via `ollama create`
  (`num_thread 8 → 4`, verified `ollama show --parameters`: `num_thread 4`;
  blob/template/stops unchanged, no re-download). Server-level
  `OLLAMA_NUM_THREADS=8` default is a separate fallback — untouched.
- Thermals: no throttling in any run (max 86°C heat-soaked vs 97–100°C
  threshold; 18–35W package).

### LFM2.5 tiny models (230M / 350M) — bonus sweep

Imported to Ollama 2026-10-08: `lfm25-230m-q6k` (t=6), `lfm25-350m-q6k` (t=8),
`lfm2-1.2b-extract` (t=6) — all with LFM2 chat template (`system/user/assistant`
roles), ctx 8192, temp 0.1. Raw data: `logs/20261007-threads/tiny_sweep.*`.

| Model | peak t | decode | TTFT | ~500-tok prefill | load |
|---|---|---|---|---|---|
| LFM2.5-230M Q6_K (183MB) | 6 | **133.3 t/s** | 0.031s | 0.80s | 0.10s |
| LFM2.5-350M i1-Q6_K (280MB) | 8 | **91.0 t/s** | 0.040s | 1.16s | 0.09s |

t=12 always falls (HT/scheduler overhead); 11.6W / 57°C package. 230M = 3.1×
their Raspberry Pi claim. Use cases per Liquid: extraction/tool-calling/task
models — **not** reasoning/code. Decision: use as WebUI task models and
extraction pipelines.

## Pending benchmarks

- [ ] `bench-all` full sweep across all 8 installed models
- [ ] 10-min sustained phi4-mini thermal validation — now privilege-free: `scripts/screening.py` TelemetryCollector (RAPL + thermal + freq sysfs, no sudo); turbostat optional for forensic runs (see `docs/TELEMETRY_PLAN.md`)
- [ ] Q5_K_M vs Q4_K_M deepseek-r1:8b (tool-call quality vs speed)
- [x] ZRAM 8GB active; NVMe-backed `/swap.img` disabled and retained for rollback (2026-09-23)
- [ ] THP `madvise` vs `always` (latency spike measurement)