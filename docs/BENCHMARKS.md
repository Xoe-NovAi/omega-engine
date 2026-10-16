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
---

## 2026-10-14 — Embedding placement at NATIVE 1024-d (supersedes the 768-d numbers)

Harness: `benchmarking/embedding/emb_bench_onnx.py` · results:
`benchmarking/embedding/emb_bench_onnx_results.json` · log:
`run_onnx_v3_20261014.log`. Host: i7-13620H (6P+4E/16T, `avx2`+`avx_vnni`, **no
AVX-512 / no FP8**), 16GB single-channel DDR5-5200, CPU-only. Generator: Ollama
`:11434` pinned `0-11`, tag `bench-tlfm25-t6-latest-8` (**num_thread 8**). Embedder:
`scripts/embedding_server.py` (ONNX INT8, 613.5MB) on `:8090`, `TRUNCATE_DIM=1024`,
`num_thread 4`, `allow_spinning=0`, retargetable at runtime because it runs as `xnai`.
n=5 × 96 tokens, temp 0, warm model. Affinity **asserted per arm**, not assumed.

> **Thread-count caveat:** the measured peak for this model family is **t=6**
> (21.2 t/s, 2026-10-07). These rows are **t=8** at the operator's request. Do not
> compare them to the t=6 rows above without stating the tag.

### Headline: LLM decode under embedding load

| Arm | Embedder placement | LLM decode (mean) | Δ vs alone | sd | Embed calls | Embed latency (under load) |
|-----|--------------------|-------------------|-----------|----|-------------|----------------------------|
| **A** | idle @12-15 | **20.47 t/s** | — | 0.02 | 0 | — |
| **B** | **E-cores `12-15`** | **18.37 t/s** | **−10.3%** | 0.07 | 272 | 69.61 ms |
| **C** | **P-cores `0-11`** | **17.86 t/s** | **−12.8%** | 0.23 | 296 | 62.49 ms |

**E-core isolation is worth +2.9%** (18.37 vs 17.86). Real and reproducible
(sd ≤0.23 across n=5), but **small**.

### Isolated embed latency (no LLM running, n=30, post-warm)

| Mask | Mean | Min | p50 |
|---|---|---|---|
| E-cores `12-15` | **38.39 ms** | 36.81 | 38.37 |
| P-cores `0-11` | **30.32 ms** | 28.71 | 29.99 |

1024-d verified at runtime: `dimensions: 1024`, `truncate_dim: 1024`, L2 norm 1.0.

### ⚠️ Two corrections to prior documentation

1. **The 89.24 ms E-core figure does not reproduce.** Measured **38.39 ms** at
   1024-d — 2.3× better. The 2026-09-24 table
   (`docs/research/RAPTOR_LAKE_HARDWARE_RESEARCH_REPORT.md` §4.1) was Matryoshka
   **768-d** with unspecified input length, so it is not like-for-like. The
   E-core *penalty* also shrinks: 1.27× here (38.39 vs 30.32) vs the 2.24×
   (89.24 vs 39.87) that report claims. **Use 38 ms; do not quote 89 ms as current.**
2. **The "−78% collapse" did not reproduce in this configuration.** P-core
   contention cost **−12.8%**, not −78%. The documented −78% (§D above) describes a
   *specific misconfiguration*: the **primary** Ollama auto-loading
   `qwen3-embedding` with ~10 runner threads squatting `0-11`. Here the embedder is a
   separate 4-thread process with spinning disabled. **The architectural lesson
   (isolate, don't share) holds — but −78% is not the general cost of co-locating
   embeddings. Do not quote it as the headline.**

### Harness reliability notes (two silent-failure modes, both now fixed)

- **EPERM affinity no-op.** The Ollama processes run as user `ollama`; `taskset`
  returns `EPERM` and the harness cannot retarget them. v1 discarded this via
  `capture_output=True` and produced a **fake P-core arm** (mask read back `12-15`
  while labelled `0-11`). `emb_bench.py` / `emb_bench_results.json` are retained
  **only** as the record of that failure — its arm C is invalid.
- **Schema 422.** `EmbedRequest.inputs` is `List[str]`, response key is
  `embeddings`. v1 sent `{"input": ...}` → all 572 hammer calls 422'd and both
  load arms again measured *zero* load. Also note `embeddings` is
  `List[List[float]]`: the dimension is `len(v[0])`, not `len(v)`.
- `emb_bench_onnx.py` now **asserts** the affinity it actually got, **refuses to
  record** an arm with zero successful embed calls, and **checks** the returned
  vector length is 1024.

### Model-precision note (this host)

`/proc/cpuinfo` = `avx2 avx_vnni` only — **no AVX-512, no FP8**. `onnx-community/
Qwen3-Embedding-0.6B-ONNX` publishes **no FP8 variant** (fp32, fp16, int8, uint8,
q4, q4f16, bnb4, quantized). An FP8 export would be dequantized at load and run
**slower** than the INT8+VNNI path. Also: `model_fp16.onnx` (0.6MB) is an
**external-data split** graph and is unusable without `model_fp16.onnx_data`
(1199.9MB); INT8 is self-contained. `model_q4f16.onnx` (567.5MB) is the only
published variant *smaller* than INT8.

---

## 2026-10-14 — Controlled sweep: 3 generators × 3 placements (SUPERSEDES the single-model 1024-d table)

Harness: `benchmarking/embedding/sweep.py` (driver) +
`benchmarking/embedding/emb_bench_onnx.py` (arms). Summary:
`benchmarking/embedding/sweep_summary_20261014.json`. Logs `sweep_*.log`.

**Conditions pinned for the whole sweep** (this is what the earlier single-model
run got wrong):
- Power profile **`performance`** for every arm (asserted at start; the driver
  warns and still runs if not).
- **Every resident model unloaded between generators**, waiting for
  `MemAvailable ≥ 3000 MB`. MemAvailable is recorded per arm.
- Generator tags carry an **explicit `num_thread 8`** — necessary because
  `/etc/systemd/system/ollama.service.d/override.conf` does **not** set
  `OLLAMA_NUM_THREADS` (see caveat below), so unpinned models inherit Ollama's
  default and the arms stop being comparable.
- n=5 × 96 tokens, temp 0, warm model. Embedder = ONNX INT8 1024-d on `:8090`,
  4 threads, spinning disabled.

### Results

| Generator | A: alone | B: embed on E `12-15` | C: embed on P `0-11` | ΔB | ΔC | **B vs C** |
|---|---|---|---|---|---|---|
| **phi4-mini** 3.8B Q4_K_M | 14.17 (sd 0.13) | 12.47 (sd 0.13) | 12.47 (sd 0.15) | −12.0% | −12.0% | **0.0%** |
| **qwen2.5-coder:7B** Q4_K_M | 8.22 (sd 0.02) | 7.18 (sd 0.10) | 7.08 (sd 0.09) | −12.7% | −13.9% | **+1.4%** |
| **LFM2.5-2.6B** Q4_K_M | 20.97 (sd 0.20) | 18.27 (sd 0.25) | 18.24 (sd 0.32) | −12.9% | −13.0% | **+0.2%** |

Embed latency under concurrent LLM load (mean, n≈270–440 calls/arm):

| Generator | on E `12-15` | on P `0-11` | E-core penalty |
|---|---|---|---|
| phi4-mini | 69.73 ms | **58.45 ms** | +19.3% |
| qwen2.5-coder:7B | 66.97 ms | **59.15 ms** | +13.2% |
| LFM2.5-2.6B | 64.58 ms | **55.56 ms** | +16.2% |

### ⚠️ Finding: E-core isolation buys no measurable LLM throughput

The load tax is a consistent **−12% to −13% regardless of model size** — the
cost is bandwidth-driven and roughly model-independent. But **placing the
embedder on E-cores instead of P-cores recovers 0.0% / +1.4% / +0.2%**, i.e.
**at or below the ~1 sd run-to-run noise**, while **costing 13–19% on embed
latency**. On this host the isolation argument in
`docs/research/RAPTOR_LAKE_HARDWARE_RESEARCH_REPORT.md` §4.3 and
`docs/BENCHMARKS.md` §D is **not supported by measurement** when the embedder
is a separate 4-thread process with spinning disabled.

What *is* supported: a **separate low-thread-count embedder** is much better
than the documented −78% failure (primary Ollama auto-loading the embedder with
~10 runner threads onto `0-11`). The mitigation is process separation and thread
count, **not** core placement.

### Two configuration defects found

- **`OLLAMA_NUM_THREADS` is not in the override.** `override.conf` sets
  `AllowedCPUs=0-11`, `MAX_LOADED_MODELS=1`, `KV_CACHE_TYPE=q8_0`,
  `CONTEXT_LENGTH=8192`, `FLASH_ATTENTION=1`, `NUM_PARALLEL=1` — but **no
  `OLLAMA_NUM_THREADS`**, contradicting `docs/HARDWARE.md`. Unpinned models
  therefore run at Ollama's default, not the documented 8.
- **`WEBUI_SECRET_KEY` is stored in plaintext** in that same override file.

### Discarded runs (do not cite)

- **phi4-mini run #1** — zRAM-thrashed by the preceding 7B run. Arms at 7.40 t/s
  against a clean 13.4–14.4 baseline, and arm C reported **+65.3%**, i.e.
  embedding load appearing to *speed up* the LLM. Physically impossible →
  invalid.
- **7B run under `balanced`** — arms B/C collapsed to ~3.6–3.8 t/s at
  `MemAvailable` ≈ 3 GB. The apparent "−50.8% / −54.0% tax" was **swap/memory
  thrash, not core contention**. Under clean `performance` conditions the same
  model shows **−12.7% / −13.9%**.
- **phi4-mini run #2** — power profile switched `balanced → performance` mid-run,
  so arm A straddled the switch. B-vs-C (+4.6%) was valid; all deltas were not.
- The single-model LFM 1024-d table earlier in this file is a **`balanced`**
  run and is not comparable to these `performance` rows.

### ONNX model-precision health (this host)

`/proc/cpuinfo` = `avx2 avx_vnni` — **no AVX-512, no FP8**. The
`onnx-community/Qwen3-Embedding-0.6B-ONNX` repo publishes **no FP8 variant**.

| Variant | Size | Downloaded | Loads in ORT | Drivable by `embedding_server.py` |
|---|---|---|---|---|
| `model_int8.onnx` | 613,527,539 | ✅ byte-exact | ✅ 1.5 s | ✅ **HEALTHY** — dim 1024, L2 1.0000, finite |
| `model_fp16.onnx` + `.onnx_data` | 583,522 + 1,199,927,296 | ✅ byte-exact | ✅ 2.0 s | ❌ dtype mismatch |
| `model_q4f16.onnx` | 567,458,583 | ✅ byte-exact | ✅ | ❌ dtype mismatch |

The fp16/q4f16 failures are **not** corruption: their graphs declare
`tensor(float16)` activations while `scripts/embedding_server.py` feeds fp32.
`ONNX_MODEL_NAME` is hardcoded to `model_int8.onnx` (line 60), so the server was
never wired for them. Driving them needs dtype-aware feeding. Given no native
fp16 compute on this CPU, INT8+VNNI remains the correct choice regardless.

Dedicated isolated embed latency (nothing else loaded, n=30): **38.39 ms** on
E-cores, **30.32 ms** on P-cores.

---

## 2026-10-14 — What actually drives the embedding tax: thread count vs duty cycle

Harness: `benchmarking/embedding/embed_knobs.py` · results:
`benchmarking/embedding/embed_knobs_results.json` · log `knobs_v2_20261014.log`.
`performance` profile, `MemAvailable` ≥ 9.5 GB in every cell. Generator fixed at
`bench-tlfm25-t6-latest-8` (num_thread 8). Embedder restarted per row, pinned
E-cores `12-15` (placement shown irrelevant). n=5 × 96 tokens.

| Embedder threads | baseline | 100% duty (~790 calls) | 50% duty (~350 calls) | 25% duty (~162 calls) |
|---|---|---|---|---|
| **1** | 20.33 t/s | 15.83 (**−22.1%**) | 18.18 (**−10.6%**) | 19.08 (**−6.1%**) |
| **2** | 20.51 t/s | 15.81 (**−22.9%**) | 17.75 (**−13.5%**) | 19.34 (**−5.7%**) |
| **4** | 20.45 t/s | 15.73 (**−23.1%**) | 17.85 (**−12.7%**) | 18.81 (**−8.0%**) |

### Conclusions

1. **Embedder thread count does essentially nothing.** At saturation the tax is
   −22.1% / −22.9% / −23.1% for 1 / 2 / 4 threads — a 1.0 pp spread against
   baseline sd of 0.12–0.30 t/s. The obvious tuning knob is a dead end.
2. **Call rate is the whole story.** The tax scales with embed call rate:
   ~790 calls → −22 to −23%, ~350 → −11 to −13.5%, ~162 → −5.7 to −8.0%.
3. **This reconciles the earlier sweep.** The 1024-d sweep above reported
   −12.9% at "4 threads, continuous". Its hammer slept 50 ms *between* calls,
   i.e. ~55 ms work + 50 ms sleep ≈ **~50% duty** — not saturation. The −12.9%
   matches this table's 50%-duty row (−12.7% at 4 threads) almost exactly, which
   cross-validates both harnesses. **True saturated tax is ~−23%, not ~−13%.**
4. **Practical recommendation: rate-limit embeddings, don't shrink them.**
   Dropping to ~160 calls/window costs only −6% LLM throughput while still
   serving several embeddings per second — ample for a memory-palace write
   path. Combined with §sweep above: placement and thread count are both
   irrelevant; **duty cycle is the only lever that moves the number.**

> ⚠️ Ignore the `embed_duty_actual_pct` field in the JSON — its denominator omits
> the hammer ramp and warm-up generation, so it reports ~100% for every row. Use
> `embed_calls` and `embed_lat_ms` to derive real duty.

### Harness bug worth recording

`embed_knobs.py` v1 called `POST /health`, but the endpoint is **GET**, so
`start_embedder` timed out and raised `RuntimeError` while the server was healthy
— and the `finally` restore *also* reported failure even though it had actually
succeeded. Read `/health` with GET.

---

## 2026-10-14 — ⭐ DEFINITIVE: what actually makes this box tick

Harnesses `benchmarking/embedding/tune.py` (phases 1–3) and `tune_p5.py`
(phases A–C). All cells: `performance` profile asserted, resident models unloaded
between blocks with `MemAvailable ≥ 3000 MB`, warm-up discarded, `num_thread` /
`num_ctx` overridden per request. n=4–5 × 64–96 tokens.

### 1. Generator thread curve — "t=6 peak" does NOT reproduce

Isolated, decode t/s:

| Generator | t=4 | t=5 | t=6 | t=8 | t=10 | t=12 |
|---|---|---|---|---|---|---|
| LFM2.5-2.6B | 19.65 | 20.46 | 20.60 | 20.49 | **20.95** | 20.89 |
| phi4-mini 3.8B | 13.52 | 13.67 | 14.10 | 13.95 | **14.24** | 14.21 |
| qwen2.5-coder:7B | 7.59 | 7.75 | 8.03 | 7.93 | **8.09** | 8.05 |

It is a **broad plateau from t=5 to t=12**, best at **t=10** on all three
(+1.7% / +0.7% / +0.7% over t=6). The 2026-10-07 claim that decode *falls* beyond
t=6 does not reproduce under this methodology; the old `t=6` tags leave ~1–2% on
the table. Adopt **`num_thread 10`**.

### 2. ⭐ Prefill (cache-defeated) — the finding that changes model choice

Every sweep above measures *decode*. Real agent turns are prefill-dominated.
**Every prefill request carried a unique nonce** — the first attempt reused an
identical prompt and Ollama's prefix cache served it, yielding a fictional
~13,000 tok/s. Real numbers, 1017-token prompt:

| Generator | t=6 | t=8 | t=10 | t=12 | Tokens | Time |
|---|---|---|---|---|---|---|
| **LFM2.5-2.6B** | 88.6 | 87.0 | 85.8 | **90.4** tok/s | 1017 | **11.3–11.8 s** |
| **qwen2.5-coder:7B** | 1371 | 1425 | 1399 | **1598 tok/s** | 1019 | **0.64–0.75 s** |

**The 7B prefills ~16× faster than the 2.6B LFM** despite being 2.6× *slower* at
decode. LFM's `lfm2` architecture has pathological prefill. Prefill is also
essentially **flat in `num_thread`** for LFM (85.8–90.4 across t=6–12), so extra
threads cannot rescue it.

**Model choice for agentic use:** `qwen2.5-coder:7B` for long system prompts /
history (0.7 s vs 11.5 s per ~1000-token prefill). LFM only wins on pure decode
throughput with short prompts.

### 3. Embedding interaction — more generator threads absorb the load

LFM tax at 25% embed duty: **−7.8% (t=4) → −4.7% (t=12)**. The two knobs
interact; higher `num_thread` gives headroom for the embedder.

### 4. Power profile has NO effect on decode (order-balanced A/B)

Interleaved perf/bal × 3 (drift cancels), `num_thread 10`:

| | performance | balanced |
|---|---|---|
| LFM2.5-2.6B | 19.79 / 19.77 / 19.90 → **19.82** | 19.98 / 19.89 / 20.03 → **19.97** |
| qwen2.5-coder:7B | 7.76 / 7.65 / 7.80 → **7.74** | 7.72 / 7.81 / 7.88 → **7.80** |

Difference ≈ ±0.8%, with balanced marginally *higher*. The earlier
sequential-block reading of "balanced ~10% slower" was **entirely run-order
drift** — sequential blocks are invalid for A/B; interleave them. **`balanced` is
a fine default and thermally preferable.**

### 5. No thermal throttling

90 s sustained decode, sampling `x86_pkg_temp`:

| Model | first | last | peak temp |
|---|---|---|---|
| LFM2.5-2.6B | 20.96 t/s @ 73 °C | 20.93 t/s @ 76 °C | 81 °C |
| qwen2.5-coder:7B | 8.10 t/s @ 76 °C | 8.10 t/s @ 78 °C | 88 °C |

Throughput flat, peak 88 °C vs Tj max 100 °C. The residual drift seen elsewhere is
**not** thermal and remains unexplained (suspect page-cache/memory layout).

### 6. Context length is irrelevant to throughput

2048 / 4096 / 8192 → LFM 20.29/20.24/20.10, phi4 13.67/13.82/13.74,
7B 7.89/7.86/7.89. ≤0.9% spread. It is a **memory** knob only.

### ⭐ Recommended configuration (Node 1, 16 GB single-channel, CPU-only)

| Setting | Value | Evidence |
|---|---|---|
| `num_thread` (generator) | **10** | §1 — best on all 3 models |
| `num_thread` (prefill-heavy) | **12** for 7B | §2 — 1598 tok/s |
| `num_ctx` | 4096–8192 | §6 — no throughput cost, memory only |
| KV cache | `q8_0` | ~0.5 GB freed, no regression (2026-09-08) |
| `MAX_LOADED_MODELS` | 1 | verified; MAX=2 thrashes |
| `AllowedCPUs` | `0-11` | **never** `0,2,4,6,8,10` (−96% convoy) |
| Embedder threads | 4 (any value works) | knobs test — no effect |
| Embedder placement | irrelevant | 0.0% / +1.4% / +0.2% |
| **Embedder duty cycle** | **≤25%** | **the only lever: −23% → −5%** |
| Power profile | `balanced` (or `performance`) | §4 — no difference |
| **MemAvailable floor** | **≥ 3000 MB** | the single biggest real risk |

**The binding constraint is memory, not compute.** Every invalid run this week
traced to `MemAvailable` dropping toward 3 GB. Dual-channel RAM remains the only
change that would materially move these numbers.

---

## 2026-10-16 — ⭐ CORRECTION: placement DOES matter — the sweep's C arm never placed anything

Harnesses: `benchmarking/embedding/prove_placement.py`,
`prove_C_proper.py`, `prove_final.py` (+ `embed_server_nopin.py`, a test copy
with the import-time self-pin neutralized; production file untouched). Logs
`prove_placement.log`, `prove_C_proper.log` (`prove_C_run.log`),
`prove_final.log` (`prove_final_run3.log`).

### What was wrong

The 2026-10-14 sweep reported E-core isolation recovering only
0.0% / +1.4% / +0.2% — "placement irrelevant". **That conclusion is VOID.**
Three stacked methodology failures, found in order:

1. **The retarget never took.** The Ollama embedder runs as user `ollama`;
   `taskset` returned EPERM, swallowed by `capture_output=True`. The "P-core"
   arm measured the E-core configuration twice.
2. **`taskset -p <tgid>` moves only the main thread.** `sched_setaffinity` on a
   thread-group id affects the single thread with that TID. The ONNX intra-op
   pool, born under 12-15, kept its birth masks. Read-backs (`taskset -pc`)
   show only the main thread, so the "verification" was blind to this.
3. **The embedder defeats birth masks itself.** `scripts/embedding_server.py`
   calls `configure_cpu_affinity()` at import, re-pinning main to 12-15 no
   matter what mask it was born under. (Read on day one, then forgotten when
   designing the fix.)

Per-thread `Cpus_allowed_list` (`/proc/<pid>/task/<tid>/status`) plus
per-thread `last_executed_cpu` sampling is the minimum proof. Mask read-back
alone proves nothing.

### Proven-placement result (L1 mask + L2 allowed + L3 executed, all PASS)

Test copy, self-pin neutralized, continuous hammer, LFM `num_thread 8`:

| Arm | L2: every thread allowed | L3: executed union | LLM t/s | Embeds | Embed lat |
|---|---|---|---|---|---|
| **E** (born 12-15) | {12,13,14,15}, 0 off-mask | {12,13,14,15} | **16.60** | 1075 | 43.1 ms |
| **C** (born 0-11) | {0..11}, 0 off-mask | {0..11} all 12 CPUs | **14.18** | 1727 | 29.8 ms |

**Sharing P-cores costs an additional −14.6% versus E-core isolation**
(14.18 vs 16.60), with placement proven at all three levels. The operator's
skepticism is vindicated in substance: the C arm as originally run never
existed, so "0–3%" measured an artifact, not physics.

### Entanglement caveat (read before quoting −14.6%)

The hammer is latency-driven (no pacing), and P-cores serve embeds faster
(29.8 vs 43.1 ms), so the C arm completed **1727 embeds vs 1075** — 60% more
load. Placement and rate effects are entangled in this design; the knobs test
already showed tax scales with call rate. A rate-matched rerun (paced hammer,
equal embeds/window in both arms) is needed for the pure placement number.
Direction is unambiguous; magnitude is not yet isolated.

### What survives from the 2026-10-14 work

- **E-arm numbers stand** (proven clean: born 12-15, union exactly {12..15}).
- **Duty-cycle finding stands** (measured within single-placement designs).
- **Embedder thread-count irrelevance stands** (same design).
- **Generator thread curve, prefill gap, power-profile null, thermal null,
  context null** — all measured on the generator side, unaffected.
- **B-vs-C "placement irrelevant" is retracted in full**, as is the
  "§4.3 verdict not supported" banner added to the research report on 2026-10-14
  (corrected below).

---

## 2026-10-16 — Rate-matched placement: the −14.6% dissolves (mostly rate artifact)

Harness `benchmarking/embedding/rate_match.py` · results
`rate_match_results.json` · log `rate_match_run.log`. Test copy (self-pin
neutralized), birth masks, **L2 verified zero off-mask threads on all 16
starts**, L3 spot-checked per cell, paced hammer at identical rates, order
interleaved E/C within each rate, `performance`, settled memory.

LLM decode t/s (LFM t=10, phi4 t=10, n=5 × 96 tok):

| Model | rate | E (proven 12-15) | C (proven 0-11) | gap | embed counts |
|---|---|---|---|---|---|
| LFM | idle | 20.90 | 20.77 | −0.6% | 0 / 0 |
| LFM | 8/s | 18.76 (353) | 18.68 (356) | **−0.4%** | matched |
| LFM | 16/s | 17.17 (703) | 16.46 (761) | −4.1% | +8% in C |
| LFM | sat | 17.22 (931) | 16.66 (1122) | −3.3% | +20% in C |
| phi4 | idle | 13.74 | 14.27 | **+3.9%** | 0 / 0 |
| phi4 | 8/s | 12.73 (432) | 12.72 (433) | **−0.1%** | matched |
| phi4 | 16/s | 11.77 (819) | 11.47 (871) | −2.5% | +6% in C |
| phi4 | sat | 11.72 (1069) | 11.54 (1278) | −1.5% | +20% in C |

### Reading

1. **At perfectly matched embed volumes (@8/s cells: 353/356 and 432/433),
   the placement gap is −0.4% and −0.1%: zero.** The −14.6% from the
   proven-placement run was ~entirely a rate artifact (1727 vs 1075 embeds)
   under a latency-driven hammer — P-cores serve each embed faster, so an
   unpaced hammer does more of them, and the extra load (not the placement)
   did most of the damage.
2. **The idle cells measure the noise floor, not placement.** With ZERO embed
   load, E vs C reads −0.6% and **+3.9%**. Nothing differs between those cells
   except a full process restart between them — so **cross-restart drift is
   ~±4%**, and any loaded gap inside ±4% is indistinguishable from it.
3. **Best estimate of pure placement effect at equal load: ~0%, bounded above
   by ~2–3%.** The physically coherent story: one shared single-channel bus
   (~35 GB/s) is the bottleneck, and bus contention is identical whichever
   cores do the embedding math. Core choice moves *embed latency* (P-cores
   10–30% faster per call, consistently) but not LLM throughput.
4. **Status of every prior claim:**
   - Sweep "0–3%, placement irrelevant": right magnitude, **void method**
     (C arm never placed). Re-established here on solid method.
   - prove_final "−14.6%": **retracted as a placement number** — rate artifact.
     Kept as proof that unpaced hammer comparisons lie.
   - Duty-cycle finding (−23% sat → −5% at 25%): stands, and is now the
     *entire* story. Rate is the only lever; placement is not one.
5. **Harness bug fixed at source:** `run_cell` derived `arm` as
   `label.split()[0]`, which yields the model tag — every summary matched
   nothing and printed empty tables while the JSON held all 16 cells. Arm is
   now parsed from the `arm-<E|C>` suffix; the shipped JSON had its arm field
   repaired by loop order (verified 8 cells/model).
