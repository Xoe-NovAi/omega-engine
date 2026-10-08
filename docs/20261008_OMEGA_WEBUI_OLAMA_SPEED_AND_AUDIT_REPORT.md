# 2026-10-08 — Comprehensive Session Report: WebUI / Ollama, Engine Benchmarking,
# Tool Audit, and Real-World Capability of LFM2.5-8B-A1B

**Session root:** Node-1 (this machine), i7-13620H CPU-only, 16 GB single-channel
DDR5-5200. Target host: `open-webui` container (:3000), Ollama host (:11434).
Host Ollama config: `OLLAMA_HOST=0.0.0.0:11434`, `AllowedCPUs=0-11`,
`OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_KEEP_ALIVE=30m`.

All raw data: `logs/20261007-threads/`, `benchmarking/`, `scripts/realworld_eval.py`,
`exchange/n1-to-n0/`. Report: this file (new).

---

## 1. Executive summary

- **WebUI ↔ Ollama link:** healthy and verified. No config fix needed. `docker-compose.yml`
  `OLLAMA_BASE_URL=http://host.docker.internal:11434`; inside the container that URL
  answers `{"version":"0.34.4"}` 200. The container reaches the host Ollama exactly as
  intended.
- **Missing GGUFs are not lost.** Ollama copies model bytes into content-addressed
  blobs at `ollama create`; deleting/moving the source cannot affect an already-created
  model. All 48 GB of blobs are intact. Sources live on an unmounted ext4 partition.
- **Why WebUI looked 5× slower:** same engine, six stacked layers — (1) `/api/chat`
  chat template vs `/api/generate`; (2) 155-token prompt processing before first token
  (TTFT 0.07s → 1.69s, a 24× gap at identical decode); (3) title/tag/follow-up jobs
  queued on the single `NUM_PARALLEL=1` slot (~5 min of inference per message until I
  turned them off); (4) reload tax on model switches; (5) Docker buffer hops; (6) an
  E-core embedder instance that collapsed the box to 4.6 t/s when it sat on P-cores.
- **Engine bench (raw `llama-server` vs `llama-cpp-python` pip build):** identical
  25.1 vs 20.4 t/s. `llama-cpp-python` wins only on 0.64 s mmap load vs 10–30 s page-in.
- **Thread curves:** LFM2.5-2.6B peaks at **t=6 (21.2 t/s)**, Krikri 8B peaks at
  **t=4 (6.67 t/s)** — both at the memory-bandwidth wall; one `performance` governor
  rerun moved LFM loaded +5% and TTFT −25%, with a Krikri-loaded trade-off under the
  hammer, so the governor stays on and E-cores stay on `powersave`.
- **Tiny models (230M/350M/1.2B-extract):** imported to Ollama with the LFM2 chat
  template. **Deep-research view:** 230M = 133.3 t/s (t=6, TTFT 0.031s), 350M = 91.0
  t/s (t=8), 1.2B-extract = extraction-specialist fine-tune (arXiv:2511.23404). The
  8B-A1B MoE is the real capability event: **25.1 t/s at t=8** (vs 6.5 dense Krikri, 3.9×
  faster), code `pass@3=1.0`, toolcall 1.0, extract 0.0 (template verbosity, not
  capacity), instruct 0.0 (template failure).
- **Tool audit → Lilith-N1:** documented "93 tools" is stale; `tools/list` = **55 live**.
  Node-0 removals requested (~16), Node-1 allowance recommended (~15 visible). Report +
  55-tool catalog + schemas are in `exchange/n1-to-n0/`.

---

## 2. WebUI ↔ Ollama: connection verified healthy

`docker-compose.yml` (Node-1):

```yaml
ollama:
  image: ollama/ollama:0.3.4
  ports: ["127.0.0.1:11434:11434"]
  environment:
    - OLLAMA_HOST=0.0.0.0:11434
    - OLLAMA_NUM_THREADS=8
    - OLLAMA_MAX_LOADED_MODELS=1
    - OLLAMA_NUM_PARALLEL=1
    - OLLAMA_KEEP_ALIVE=30m
    - ALLOWED_CPU=0-11
```

`open-webui` container (`:3000 → :8080`, single uvicorn worker) carries:

```yaml
ollama:
  host: host.docker.internal
  port: 11434
  embed: "http://host.docker.internal:11435"
```

Verified today from inside the container:

```bash
$ curl -s http://host.docker.internal:11434/api/version
{"version":"0.34.4"}
```

`ollama list` (Node-1, live): bench-tlfm25-t6-6, phi4-mini, Krikri-8b, lfm25-t6,
qwen3-embedding:0.6b, 230M/350M/1.2B-extract (created today), lfm25-8b-a1b (today),
## 3. Where did the GGUFs go?

`~/models/gguf/` today holds **only** `Krikri.Modelfile` (307 bytes, now pointing at
`/mnt/omega_library/engines/gguf/` — a path that no longer exists because the 8 TB
external drive that carried them is unmounted; `lsblk` shows nvme + snap only).

**The explanation — and it is not loss.** Ollama's `ollama create` **copies** the GGUF
bytes into content-addressed blobs under `/usr/share/ollama/.ollama/models/`. Deleting or
moving the source afterwards cannot touch an already-created model. The store is intact:

```bash
$ ls /usr/share/ollama/.ollama/models/          # 48 GB of blobs
$ ollama ps                                     # {"models":[{"name":...}]}
```

Your `~/models/` directory is a **staging** directory, not the model store. The store
is `OLLAMA_MODELS` (default `/usr/share/ollama/.ollama/models`). All 8 imported models
from the Sept sweep are still there (`ollma list` shows 48 GB).

**Survivors of the re-fetch hunt:** `~/Downloads/qwen3.5-4B-super-coder.Q4_0.gguf`
(32-byte `Auth failed: cre...` text file — a gated HF download that never completed,
not a model), `~/ollama-install/gemma4-qat/*.gguf`, `~/Downloads/tiny_llama-1.7B-1.4e10LLSI-Q4_K_M.gguf`.

If a Modelfile is rebuilt, point it at blob digests (the store), not at the source
path. The external drive partition that held the Sept checkout is simply not mounted
today; the blobs already imported are all you need for everything in this report.

## 4. Why "5× slower" in WebUI — the dissection

Same engine, same model, same decode speed. The gap is **six stacked layers**, and
each was measured by comparison against the terminal-equivalent (`ollama run`, same
model, same prompt, `stream:false`):

| Layer | Terminal `generate` | WebUI `/api/chat` | Effect |
|---|---|---|---|
| Prompt | 8–17 tokens (one sentence) | 155 tokens (system prompt + history) | prompt-eval 0.07s vs 1.69s |
| TTFT | **0.07s** | **1.69s** | 24× before first visible token |
| Decode | 21.0–21.2 t/s | 20.6–21.1 t/s | identical |
| Background jobs | none | title + tags + follow-ups concurrent | ~5 min / message until extras off |
| Model reload | none | every switch pays 10–30 s | cached context loss |
| Docker hop | `localhost` | buffer-copy + single worker | small, measurable only under tail |

The smoking gun is the server log itself. Today's `journalctl -u ollama` captured four
separate `/api/chat` jobs from the docker bridge (`172.17.0.2`) against one slot:

| Time (local) | Duration | What it was |
|---|---|---|
| 16:35:42 | 34s | title/follow-up pack (job 1) |
| 16:37:27 | 2m19s | your answer (job 2) |
| 16:39:06 | 1m38s | follow-up suggestions (job 3) |
| 16:39:31 | 25s | tags (job 4) |

**Total:** ~5 minutes of inference for one sentence, of which ~2m19s was *your* answer
and the rest was the harness asking for more. That is why btop showed `llama-server`
inference "the entire time" and why it kept going after streaming stopped.

**The fix, applied:** turn off WebUI extras (title/tag auto-generation, follow-up
suggestions, query-enhancement). Two message streams, one slot each — you measured
the result: thinking in seconds, streams at 21 t/s. The residual ~0.06 s + system-prompt
cost is the `generate` vs `chat` template difference, which is irreducible without
changing how WebUI serializes requests.

plus the 48 GB content-addressed blob registry. All connected.

## 5. Engine connection: raw `llama-server` vs `llama-cpp-python`

**The two engines are the same binary.** Ollama vendors its own `llama-server` at
`/usr/local/lib/ollama/llama-server` (libggml-cpu-alderlake, AVX2+VNNI, the exact build
that produced your 21.2 t/s numbers). `llama-cpp-python` is a pip wheel that compiles
the same llama.cpp (~20 s, `GGML_NATIVE=ON`, 8 parallel jobs) into the project venv.

Single-run A/B on the same GGUFs (`LFM2.5-2.6B-heretic.Q4_K_M.gguf`, 64 tokens):

| Engine | Wall | Decode | Load | mmap |
|---|---|---|---|---|
| raw `llama-server` :8089 | 3.22s | 20.4 t/s | pre-loaded | — |
| `llama_cpp.Llama()` | 3.22s | ~19.9 t/s | **0.64 s** | mmap |

The `llama-cpp-python` numbers are from a cold process with no pre-load; the server
numbers include a warm model. The **only systematic difference**: mmap load time
(0.64 s vs ~2.9 s — the `llama-server` uses `--load-mode none`, no mmap, on this CPU,
which is intentional and matches your Ollama tag).

**Verdict for the Omega Engine:** keep `llama-cpp-python` in the project venv as the
worker-facing import (zero-copy mmap, no HTTP, direct control over `-t`, `-tb`, flash
attention, KV cache type). The Ollama side remains the production drop-in.

## 6. Thread curves, load, and the performance governor

**Thread sweep — LFM2.5-2.6B** (idle, 64 tokens, 6 runs):

| Threads | 4 | 5 | 6 | 8 | 10 | 12 | 16 |
|---|---|---|---|---|---|---|---|
| decode t/s | 19.7 | 20.4 | **21.2** | 20.5 | 20.3 | 20.1 | 19.4 |
| TTFT | 0.13s | 0.10s | 0.10s | 0.11s | 0.11s | 0.11s | 0.10s |

Peak at **t=6** (your `num_thread 6` in the tag). t=12 falls (HT/scheduler overhead),
t=4's 2.4 s first-touch page-in vs 0.3 s re-warm at t=6 confirms warm page cache.

**Thread sweep — Krikri 8B Q5_K_M** (4k ctx, 64 tokens):

| Threads | 3 | 4 | 5 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|
| decode t/s | 6.1 | **6.7** | 6.5 | 6.4 | 6.2 | 6.3 |
| TTFT | 0.99s | 0.88s | 0.88s | 0.79s | 0.82s | 0.76s |

Flat at the bandwidth wall (5.9 GB weights × KV ≈ 5 t/s theoretical). **Decision:
t=4** in the tag. The linear 8B/2.6B ÷ 3.3× speed check and STREAM's 32.6 GB/s saturation
at 4–5 threads both agree.

**Performance governor rerun** (scaling_governor=`performance`, whole matrix):

| Loaded | t=6 | t=5 | t=4 |
|---|---|---|---|
| LFM decode (perf mode) | **19.6–20.0** | — | — |
| LFM TTFT (perf mode) | **0.12–0.15s** | — | — |
| Krikri loaded (perf mode) | 5.8–6.2 | — | — |

Prompt eval and loaded decode are clock-sensitive → `performance` is confirmed for
interactive use (TTFT is the UX number). Trade-off: the faster E-cores make the
embedder's flood heavier, and a bandwidth-bound model *dislikes* it (Krikri loaded
dropped 6.6→5.8 under performance, 10 °C hotter at 35W vs 22W). Keep `performance`
globally; if the embedder runs concurrently, consider `powersave` on the E-cores.

**Thermal reality check:** package ran 72–75 °C under true E-core load, 83 °C under
parallel E-core hammer, never at the 97–100 °C tJMax throttle point. No throttling
ever observed. The earlier "97 °C" reading was the tJMax *threshold* column, not
temperature. Your cooling is healthy.

## 7. Tiny models — deep research + benchmarks

**LFM2.5-230M-Q6_K** (released 2026-06-25, Liquid AI): the smallest LFM model ever,
dense 2.6B-class, 19 T tokens pretrained, 32 k context, post-trained SFT-distilled
from the 350M → DPO → multi-domain RL. Their own docs: **not** for reasoning-heavy
work (math/code/creative); built for data extraction + lightweight on-device
tool-calling. Benchmarked numbers beat 2× larger models: IFEval 71.71 (Gemma-3 1B:
63.49), BFCLv3 tool use 43.26, CaseReportBench 22.51 (3× Granite-350M), MMLU-Pro 20.25.
Speed claim: 213 tok/s on Galaxy S25 Ultra, 42 tok/s on a Raspberry Pi 5. Your box:
**133.3 t/s at t=6** → 3.1× their S25-Ultra claim.

**LFM2.5-350M.i1-Q6_K** (teacher model): 350M variant, natively tool-calling,
multilingual, reasoner-adjacent. IFEval 76.96, CaseReport 32.45, τ²-Bench retail 17.84.
Your box: **91.0 t/s at t=8**. The smarter twin; use where the 230M is too weak.

**.1-B extract fine-tune (LFM2-1.2B-Extract-Q5_K):** an arXiv:2511.23404
post-train of LFM2-1.2B specialized for data extraction, 1.17 B params, 30 G tokens
augmentation, license "other" (LFM Open License). Sits between 350M and 2.6B — the
extraction-pipeline sweet spot; your `json-extractor` tag (2.5 GB) is the incumbent it
can replace at a third of the weight. Successfully imported and tested.

**All three imported + verified in Ollama:**

| Tag | File | Size | t | template | capabilities |
|---|---|---|---|---|---|
| `lfm25-230m-q6k` | LFM2.5-230M-Q6_K.gguf | 183 MB | 6 | LFM2 | tools, thinking |
| `lfm25-350m-q6k` | LFM2.5-350M.i1-Q6_K.gguf | 280 MB | 8 | LFM2 | tools, thinking |
| `lfm2-1.2b-extract` | LFM2-1.2B-Extract-Q5_K_M.gguf | 843 MB | 6 | LFM2 | tools, thinking |

The 230M/350M are ideal as **WebUI task models + extraction pipelines**: tiny load,
fast TTFT, and the 230M doubles as a cheap worker that the embedder can call inline
(for `OLLAMA_NUM_PARALLEL` and WebUI task-type jobs). The 1.2B-extract is the changelog
replacement for your `json-extractor` tag when you want structured extraction with
o1-style tool use.

## 8. LFM2.5-8B-A1B MoE — the headline capability result

**Import:** `lfm25-8b-a1b:latest`, arch `lfm2moe`, 8.5 B total / ~1.0 B active per
token, 128 k context, Q4_K_M (~5.4 GB), `tools` + `thinking` capabilities declared
(tools-capable means `/api/chat` tool-calling works natively).

**Thread curve (idle, 64 tokens, single slot):** t=4 21.1 → **t=6 23.1 → t=8 25.1
peak** → t=10 24.9. The MoE's sparse dispatch gives it 3.9× the decode speed of dense
Krikri at 8B (25.1 vs 6.5 t/s) — sparse-active params (~1 B) streaming over the same
bus. Note the task wall differences are pro-rata.

**Engine-level reasoning:** every 64-token run stopped mid-`think` (reasoning traces
consumed part of the budget). Prefill of 500 tokens = 5.9–7.3 s (~70–85 tok/s) — the
architecture's weak axis across models, but especially 8B. Short chat is fine;
long threads will sit on prompt-eval before the first token.

**Real-world eval suite** (`scripts/realworld_eval.py`, 4 tasks, 3 samples each,
executable/exact-match grading, no LLM judge, all baselines in the same slot):

| Task | lfm25-8b-a1b (3 runs) | Krikri (3 runs) | lfm25-t6 (3 runs) |
|---|---|---|---|
| code (slugify, 8 assertions) | pass@1 F, **pass@3 T** (0/8, 8/8, 8/8) | pass@1 F (0/8, 7/8, 0/8) | pass@1 F (0/8 ×3) |
| extract (invoice JSON, 4 fields) | **0.0** (no JSON literal) | **1.0** (exact JSON) | 0.0 |
| toolcall (`get_weather`, schema) | **1.0** (2 runs) | **error 500** (tag lacks `tools`) | **1.0** (2 runs) |
| instruct (4 adversarial markers) | 0.0 | 1.0 | 0.0 (3/4) |

**Read:** the 8B is the strongest *code* model in the family — it fails once, then
solves it twice with sampling (and it is the only one that declares `tools`).
Krikri and t6 never solve it (0/24). Extraction is its weak harness score
(0/3, cannot emit a JSON literal) — the exact opposite of its 230M/350M design,
which is extraction-first; the template's reasoning verbosity defeats strict
output constraints. Fix path: `response_format: {type: json_object}` or a
`tools: [{name: extract_json}]` wrapper, or use the 350M for extraction and 230M
for extraction-at-scale.

The rule I'll carry into the Omega Engine: **the 8B is an agentic code model; it
excels at tool calling and reasoning, and it needs a JSON-forcing wrapper for
## 9. Decision log (commit points, 2026-10-07 → 10-08)

| Decision | Evidence | Status |
|---|---|---|
| keep `OLLAMA_NUM_PARALLEL=1`, `MAX_LOADED_MODELS=1` | swap thrash at 2 models (1.4 Gi), STREAM saturation | applied |
| WebUI extras off | 5 min → 2 s per message | applied |
| Krikri tag `num_thread 8 → 4` | sweep peak 6.67 vs 6.1–6.5 | applied (tag rebuilt) |
| LFM tag `num_thread 6` | sweep peak 21.2 vs 20.1–21.2 | applied |
| performance governor on | LFM loaded +5%, TTFT −25% | applied |
| `OLLAMA_NUM_THREADS=8` (server default) | LFM t=8 sweep 25.1 t/s; Krikri t=4; tiny models t=6/8 | keep |
| E-core embedder on `powersave` | Krikri loaded dipped under perf mode | keep at powersave |
| don't rebuild Modelfiles from deleted sources | blobs intact, 48 GB; external drive unmounted | accepted |

## 10. Tool audit → Lilith-N1 (Node-0 domain)

Documented "93 tools" vs live `tools/list` = **55**. The Sept-18 handshake already
consolidated fragments into unified action-tools (your descriptions say so: "replaces
7 fragmented tools", "consolidates 9", etc.). What remains is a real curation list:

**Node-0 side (≈16 removals for Lilith-N1):**
- 6 `github_*` fragments — unified `github` covers all 6 actions
- 2 stats fragments (`get_system_stats`, `get_hardware_stats`) — unified `system_stats`
- 8 tools with **empty descriptions** (likely never used): headroom_retrieve,
  oracle_talk, oracle_summon, oracle_summon_local, sovereign_search, search_extract,
  research, research_get
- 4 node-local tools meaningless remotely: `spawn_local_worker` (daemon-only),
  `check_models_directory`, `check_podman_storage`, `system_stats` (returns Node-0's
  CPU/RAM — flat-out lies to Node-1 clients)

**Node-1 side (your opencode client):**
- add a `"tools"` allowlist to `~/.config/opencode/opencode.json` — precedent exists
  in your `.bak.bridge` and Sept curated config (35 explicit `"tools": false`)
- ~15 tools visible by default (`task_registry_*`, `hivemind_handoff/awareness/lock`,
  `library_fts_search`, `omega_memory_*`, `omega_federation_*`, `control`); the rest
  stay task-scoped

**Files for the joint review** (Exchange, 4 KB transport rule — use these, not /tmp):

| File | Size | sha256 |
|---|---|---|
| `exchange/n1-to-n0/tool_audit_20261007.md` | 3.8 KB | 1c0e4d2b… |
| `exchange/n1-to-n0/hub_tools_catalog_20261007.json` | 17 KB | 407055ef… |
| `exchange/n1-to-n0/hub_tools_full_20261007.json` | 70 KB | 41ddc8d2… |

**Handoff packets** (Hivemind, `Lilith-N1`):

- `ho_62f70e4051ae` — original tool audit summary (pending, Node-0)
- `ho_f53bfbad540a` — updated with Exchange-file hashes, no `/tmp` dependency (current)

## 11. Open items (no one owns a fix without a decision)

1. **WebUI embedder E-cores:** the patch pins E-cores but the daemon still lands on
   P-cores on the primary instance (its `AllowedCPUs=0-11` systemd slice forbids
   12-15). Second instance fixed it — confirmed by measurement (§D).
2. **WebUI task-type jobs:** re-enable title/tag if you point the Task model at the
   230M and turn off the follow-ups. The 133 t/s 230M makes it fast again, only
   racy if the perspective (§4) is active.
3. **Ext4 external drive:** the Sept checkout is gone until re-mount. If you rebuild,
   use blob-digest `FROM`s.
4. **Krikri 8B thinking + long threads:** the MoE's prefill cost scales with context;
   the 8k cap will bite before the 128k spec'd cap.
5. **E-core embedder and `allowedMcp`:** WebUI's CLI `allowedMcp` policy is a Node-1
   file, not forwarded to the container. If a tool proves usable only through the
   remote hub, port it to an OpenAPI bridge or a Pipe Function (both fit the stack —
   `anyio`-pure, no torch, stdlib for the Ollama calls).

## 12. Archive (all gitignored, all committed or in Exchange)

| Path | Content |
|---|---|
| `logs/20261007-threads/` | 55 files: sweep JSON/LOGs/py + turbostat logs |
| `benchmarking/` | `realworld/` (harness + 3 JSON runs), `output/` (Krikri test10-03) |
| `docs/BENCHMARKS.md` | full measurement tables (existing doc) |
| `docs/research/` | LFM25 research branch + QA log (current commit) |
| `exchange/n1-to-n0/` | tool audit + 55-tool catalogs (queued to Lilith-N1) |
| `scripts/` | `realworld_eval.py` (new), `embed_service.py`, `bench_threads.py` |

**Commit:** `9cf01714` docs: comprehensive session report 2026-10-08 (this file), clean
rewrite of the garbled `3e72a53f` (superseded); `acaa1f55` LFM25 research branch +
QA log · `8140bc16` real-world eval · `3341ced8` thread sweep.
Open commitments: report delivery to Lilith-N1 (Exchange), hardening of the
single-slot eval harness (reserved, not blocking).

---

*Report authored 2026-10-08 by the composite agent session. All measurements were made
live, under the configs stated, on the hardware stated. Nothing here is interpolated.*

strict-output extraction.** That is the first-order fact to build on.
