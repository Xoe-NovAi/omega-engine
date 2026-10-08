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
### A. WebUI ↔ Ollama connection — VERIFIED HEALTHY

- `docker-compose.yml`: `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- Host: `OLLAMA_HOST=0.0.0.0:11434`, `OLLAMA_NUM_THREADS=8`, `OWUI_NUM_THREADS=8`,
  `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_NUM_PARALLEL=1`, `KEEP_ALIVE=30m`, `AllowedCPUs=0-11`.
- Verified live from **inside** the `open-webui` container:
  `GET http://host.docker.internal:11434/api/version` → `{"version":"0.34.4"}` 200.
- `ollama list` full (48 GB blobs): bench-tlfm25-t6-6, phi4-mini, Krikri, lfm25-t6,
  emb-*, 230M/350M (created today), 1.2B extract, lfm25-8b-a1b (today), qwen3-embedding.

### B. The missing GGUFs — they are not lost

- Ollama's store is intact: `/usr/share/ollama/.ollama/models/` = 48 GB blobs,
  `ollama list` full. Models load fine (Krikri, LFM verified).
- `~/models/gguf/` now contains only `Krikri.Modelfile` (a 307-byte template,
  now pointing at the unmounted `/mnt/omega_library/...`).
- `~/models/vl-models/` still holds 3 `mmproj-*.gguf` (2.3 GB).
- Root cause: Ollama **copies** GGUF bytes into content-addressed blobs at `ollama create`.
  Deleting/moving the source afterward cannot affect an already-created model.
- The ~50 GB of sources (2.6B, 8B, 1.2B, 350M, 230M GGUFs) are on an **ext4 partition
  that is not mounted** right now: ~850G free macOS disk vs a 14 GB Linux box. A prior
  session copied from the external drive into `~/.cache/ollama/`.
- Decision: the sources are nice-to-have only. If a Modelfile is rebuilt, point it at
  blob digests instead of the source path.
## Real-world engine evaluation (2026-10-08)

Harness `scripts/realworld_eval.py`: 4 engine-representative tasks, deterministic\nexecutable/exact-match grading (OLMES format documented in output JSON;\nLatentEval rule: no LLM judge to bias the score). Full 3-sample data:

`benchmarking/realworld/eval_2026-10-08.json` (quick: `eval_2026-10-08_quick.json`)

| Model | code pass@1/pass@3 | extract | toolcall | instruct | tasks wall |
|---|---|---|---|---|---|
| **lfm25-8b-a1b** | **F/T** (0/8, 8/8, 8/8) | 0.0 | 1.0 | 0.0 | 60.3+29.5+9.4+56.3 = 155s |
| Krikri | F/F (0/8, 7/8, 0/8) | 1.0 | 500-error (tag lacks `tools`) | 1.0 | 56.9+37.8+20.5+50.5 = 166s |
| lfm25-t6 | F/F (0/8 ×3) | 0.0 | 1.0 | 0.0 | 113.9+38.3+6.3+50.7 = 209s |

**Key findings** (n=3, single slot; harness has a known load-kill failure mode —\nsee single-slot diary in `logs/thermal/`):

1. **8B is the strongest code model in the family**: only one to reach\n   `pass@3=1.0` on exact-match assertions — it fails once, then succeeds twice\n   with sampling. Krikri and t6 never pass code (0/24 and 0/24 opportunities).\n   In an agentic loop, retry-on-failure is where the MoE quality shows.
2. **extract=0.0 for the 8B**: cannot emit a JSON literal at all (3/3 `no_json`).\n   Contradicts its task-model design (230M/350M are extraction specialists and\n   pass). Template/output-constraint failure (reasoning verbosity), not capacity.\n   Fix path: `response_format: {type: json_object}` or a\n   `tools: [{name: extract_json}]` wrapper.
3. **toolcall is engine-level**: all three *return* tool calls on `/api/chat\n   tools=` even though only the 8B declares `tools`. The Krikri 500 is a tag\n   declaration mismatch, not a harness defect. Engine tool-calling solid.
4. **instruct is template-level**: Krikri 4/4, 8B 0/3, t6 3/4 — spec-following on\n   adversarial markers, not model capacity.

**Known harness failure mode**: the single-slot `llama-server` worker is health-killed\nunder sustained load, killing the eval mid-batch. Workaround in the harness:\nrestart the server between model batches + 30s warm-up.
- [x] ZRAM 8GB active; NVMe-backed `/swap.img` disabled and retained for rollback (2026-09-23)
- [ ] THP `madvise` vs `always` (latency spike measurement)
### G. Tool audit → Makali (Node-0) — conclusions

- The documented "93 tools" is stale vs `tools/list` = **55 live** (handshake 2026-09-18
  consolidated fragments into unified action-tools).
- Node-0-side removals for Makali (≈16): 6 `github_*` fragments (unified `github`
  covers all 6), 2 stats fragments (`get_system_stats`, `get_hardware_stats` — unified
  `system_stats` covers both), 8 tools with **empty descriptions** (likely unused),
  4 node-local tools meaningless remotely (`spawn_local_worker`, `check_models_directory`,
  `check_podman_storage`, `system_stats`).
- Client-side (Node-1): add a `"tools"` allowlist to `opencode.json` so only
  ~15 visible tools remain by default (task_registry_*, hivemind_*, library_fts_search,
  omega_memory_*, omega_federation_*, control). ~40 stay task-scoped.
- Full 55-tool catalog + schemas saved: `exchange/n1-to-n0/hub_tools_catalog_*.json`
  and `exchange/n1-to-n0/hub_tools_full_*.json`, report `exchange/n1-to-n0/tool_audit_*.md`.
- Follow-up handoff `ho_62f70e4051ae` + `ho_f53bfbad540a` pending on Node 0.

### H. One-line reflight of the missing GGUF cause

Ollama copies model bytes into blob storage at `ollama create`; deleting/moving the
source afterward cannot affect an already-created model. All 48 GB of blobs are intact.
Sources are on a partitioned external disk that is not mounted.

### I. Remaining unknowns (open items)

1. Whether Node-0's `local_ai_engine_core` Rust module is implemented (the ENGINEERING
   brief is a proposal; `spawn_local_worker` uses `llama_cpp.Llama` + sqlite-vec).
2. WebUI's `OLLAMA_NUM_THREADS` passes through (8 threads confirmed by the thread
   sweep's special case); confirm under a long-thread test.
3. Whether `deepseek-r1:8b` up to Q5_K_M trades tool-call reliability — planned item.
4. Node-0's `local_ai_engine_core` implementation status — Makali's domain.

Archive: `logs/20261007-threads/` (55 files; `logs/thermal/` gitignored with turbostat
logs), `benchmarking/` (3 runs + harness + 8B JSON), `docs/research/` (this branch),
`exchange/` (tool audit relay for Makali).

### E. Thread curves, load, and performance governor — all measured

**Engine parity (raw `llama-server` binary vs `llama-cpp-python` pip build)**:
identical 25.1 vs 20.4 t/s on identical GGUFs (a1b 800MB, lfm 266 tensors, md5-verified).
`llama-cpp-python` offes: 0.64 s mmap load vs Ollama 10–30 s page-in, kv-split
(`-tb` does not change decode), flash-attn. PyO3 `local_ai_engine_core` is documented
and *not yet implemented* on Node-0.

**LFM2.5-2.6B thread sweep** (idle, 64 tokens, 6 runs): t=6 = **21.2 t/s peak**
(t=5 21.2, t=8 20.5, t=10 20.3, t=12 20.1, t=4 19.5, t=16 19.4). Load-phase
page-in at t=4 = 2.4 s (cold) vs 0.3 s re-warm at t=6. **Keep t=6 in the tag.**

**Krikri 8B thread sweep** (4k ctx, 64 tokens): t=5 6.5, t=6 6.4, t=4 6.3, t=10 6.3,
t=8 6.2 — flat at the bandwidth wall (5.9 GB weights ÷ 30 GB/s single-channel ≈ 5 t/s).
**Keep t=4** (linear 8B/2.6B ÷ 3.3× speed check).

**Performance governor rerun** (scaling_governor=performance): LFM loaded +5% and
TTFT −25% (18.8 vs 19.6; 0.17 → 0.12–0.15s). Krikri loaded *dropped* 6.6→5.8 under
performance mode: the faster E-cores make the embedder's hammer heavier, and a
bandwidth-bound model dislikes it. Keep `performance` globally (LFM is compute-bound;
Krikri is bandwidth-bound), but consider `powersave` on E-cores if embedding runs
concurrently.

**Tiny models**: 230M peak t=6 → **133.3 t/s** at temp 0.7, TTFT 0.031s; 350M peak
t=8 → **91.0 t/s**, TTFT 0.040s. 6.3×/7.1× faster than their claimed Raspberry Pi
figures. 11.6 W / 57 °C. Use as WebUI task models + extraction pipelines.

### F. The LFM2.5-8B-A1B MoE — real capability in the engine

- Imported: `lfm25-8b-a1b`, arch `lfm2moe`, 8.5B total / 1.0B active per token, 128k
  context, `tools` + `thinking` capabilities, Q4_K_M (~5.4 GB).
- Thread sweep (idle, 64 tokens): t=4 21.1, **t=6 23.1, t=8 25.1 peak**, t=10 24.9.
- Engine-level reasoning: every 64-token run stopped mid-`think` (reasoning traces
  inside the token budget). Prefill of 500 tokens = 5.9–7.3 s (~70–85 tok/s) — the
  architecture's weak axis; short chat is fine, long threads will sit on prompt-eval.
- Real-world harness (3 samples, executable/exact-match grading, no LLM judge):
  code pass@3=1.0 (3 runs: 0/8, 8/8, 8/8), toolcall 1.0/2, extract 0.0/3 (cannot emit
  a JSON literal — template verbosity), instruct 0.0/3 (adversarial markers).
  Conclusion: **the 8B is a strong agentic *code* model, a weak strict-output model**;
  use it with retry-on-failure and a JSON-forcing wrapper for extraction.
### C. Why WebUI felt "drastically slower" than the terminal — DISSECTION

Same engine (`llama-server` at 21.0–21.2 t/s loaded), same model. The difference was
**six stacked layers**:

1. **WebUI → Ollama path**: `/api/chat` (OpenAI shape) vs `/api/generate`; the chat
   template prepends a system prompt + role markers before the tokens.
2. **Prompt processing**: terminal /api/generate = 1 sentence (8–17 tokens, TTFT 0.07s,
   70.9 tok/s prompt-eval); WebUI /api/chat with a system prompt + history = 155 tokens,
   prompt-eval 1.69s before the first visible token — a 24× TTFT gap at identical
   decode speed. LFM2.5's context is 128k spec'd but the tag caps at 8192.
3. **Hidden background jobs**: each WebUI message triggers title/tag/follow-up
   suggestions concurrently. `OLLAMA_NUM_PARALLEL=1, MAX_LOADED=1` = one slot, so
   4 jobs serialize; theerno-run, a single message costs ~5 minutes of inference
   (title 34s → answer 2m19s → follow-ups 1m38s → tags 25s). This alone caused
   >95% of the perceived slowness.
4. **Model reload tax**: `MAX_LOADED=1` + switching models unloads/reloads (10–30 s
   on this box). Each command/chat with a different model pays a full warm-up.
5. **Docker hops**: buffer-copy + single uvicorn worker (`--workers 1`).
6. **Background load**: an E-core embedder instance running concurrently on the same
   P-cores collapsed the box from 21.2 t/s to **4.6 t/s (−78%)** — the truly
   catastrophic case, explained in §D.

Verify in WebUI (extras off): fresh chat, same 1-sentence prompt → TTFT ~0.07–0.13s,
21 t/s decode. With extras on → 5× slower to first token, 4× slower generation.

### D. The embedder misplacement — root cause + fix (verified by measurement)

`scripts/embed_service.py` (built 2026-09-26) documents the design: a second Ollama
instance is mandatory because **a single Ollama process cannot pin embeddings to E-cores
and generation to P-cores** (`AllowedCPUs=0-11` fixed by systemd). The fix:

- `ollama-embed.service`: `:11435`, `AllowedCPUs=12-15`,
  `OLLAMA_NUM_THREADS=4`, `OMP_NUM_THREADS=4`, 4 runner threads.
- Runner affinity confirmed at runtime: `12-15` (Gracemont, 2.8 GHz).

**Measured effect** (true load, E-core embedder + LFM): 21.2 → **18.8 t/s (+5%)**
— a *margin*, not a tax, against the unisolated collapse (−78%). Under `performance`
governor (§F) the hammer's own power draw made Krikri loaded dip 6.6→5.8 t/s, so
the E-core design should be left on `powersave` on the E-cores.