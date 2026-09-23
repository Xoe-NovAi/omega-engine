# Deep Dive — Model Fetch Stack: Xet, systemd, GGUF, Ollama, Gemma 4

**Date**: 2026-09-23 | **Trigger**: Gemma 4 12B QAT ingest + background-download
investigation | **Sources**: HF docs, xet-core, freedesktop man pages, arXiv
2607.02770 (Gemma 4 tech report), arXiv 2601.14277 (GGUF quant study),
llama.cpp docs, Ollama tracker, Unsloth docs, community guides (full URLs in §9)

This is the expertise-expansion companion to
`docs/federation/NODE0_ACTION_BRIEFING_FAST_DOWNLOAD_LAYER.md` (the N0 handoff)
and `scripts/fetch_model.sh` (the working primitive). Everything below was
either measured live on Node 1 or verified against primary sources same-day.

---

## 1. Xet / hf_xet — the transfer backend that replaced everything

**What it is**: Xet is Hugging Face's content-addressed storage layer. Files are
split into immutable ~64KB chunks; collections of chunks ("blocks"/"xorbs")
live in a CAS (content-addressed store). Download = query CAS with the file's
LFS SHA256 → receive reconstruction metadata (which xorb ranges assemble the
file) + presigned URLs → fetch xorb ranges → reassemble on disk. All Hub repos
are now Xet-enabled; `hf_xet` (Rust `xet-core` bindings) ships inside
`huggingface_hub≥0.32` and is the **default** path. `hf_transfer` is deprecated.

**Local layout** (`~/.cache/huggingface/xet/`):
- `chunk_cache/` — download-path chunk store. **DISABLED by default**
  (hf_xet≥1.2.0); enable with `HF_XET_CHUNK_CACHE_SIZE_BYTES=<bytes>`.
  Consulted before issuing CAS requests → this is the resume mechanism.
  Random eviction when full.
- `shard_cache/*.mdb` — file→chunk mapping databases.
- `staging/` — upload-side assembly area.
- `logs/xet_<ts>_<pid>.log` — JSONL per-process logs including the adaptive
  concurrency controller (concurrency level, predicted bandwidth, success
  ratio, bytes sent, completed transmissions). **Read these first** when a
  download misbehaves — they report ground truth while progress bars lie.

**Environment variables that matter**:
| Var | Effect |
|---|---|
| `HF_XET_HIGH_PERFORMANCE=1` | Enables the fast Xet path (replaces deprecated `HF_HUB_ENABLE_HF_TRANSFER`). Bake into every fetch. |
| `HF_XET_CHUNK_CACHE_SIZE_BYTES` | Enables + sizes the chunk cache. **Set 10GB on real disk** — without it, every process restart re-downloads from 0%. |
| `HF_HUB_DISABLE_XET=1` | Forces plain-HTTP path. Diagnostic only (blocked for files >50GB). |
| `HF_XET_RECONSTRUCT_WRITE_SEQUENTIALLY=1` | Sequential assembly for HDDs (Xet parallel writes assume SSD/NVMe). |
| `HF_HUB_DISABLE_TELEMETRY=1` | Silences phone-home in automated fetches. |

**Resume semantics (the traps)**:
- v1.0 removed the `resume_download` param — resume is "automatic when possible".
- Reality: **HTTP path resumes via file cache; Xet path resumes via chunk
  cache.** No chunk cache = no resume. Each restart mints a new `.incomplete`
  token (Xet signed-URL ETags rotate) and starts a fresh file; old partials
  are orphaned (live-verified: 3 restarts → 3 tokens → 3× re-download).
- **Progress-bar lie**: the Xet downloader initializes its bar with
  `initial=0` even when prior bytes are reused — a resumed transfer *looks*
  like a restart. Trust byte counters (`stat`, Xet logs), not bars.
- `206 Partial Content` in Xet logs = normal xorb range fetching, NOT proof
  of file-level resume.
- Post-download trust: `hf cache verify` checks local files vs Hub checksums;
  we additionally gate on `sha256sum` vs `HfApi().model_info(..., files_metadata=True).siblings[].lfs.sha256`.

**Performance profile (measured)**: ~4.3 MiB/s sustained on flaky WiFi with
adaptive concurrency (ramps 4→10 connections, success_ratio 1.0). Failure
mode observed: controller wedges at floor concurrency ("decreased from 4 to
4", "connection struggling") after link contention — fresh process ramps
better than a wedged one recovers. With chunk cache on, wedges cost nothing.

---

## 2. Keeping agent-launched work alive — the survival ladder

Agent harnesses run each tool call in a managed context and **reap the child
process group on call end** (timeout, completion, or abort). Documented
precedent: Codex CLI issue #10860 — "nohup killed at turn end, setsid
survives". We reproduced it: `nohup … &` froze dead at 68MB.

| Method | Mechanism | Survives? |
|---|---|---|
| `cmd &` | Same group/session | ❌ |
| `nohup … &` (+redirs) | Ignores SIGHUP only | ❌ group SIGTERM still kills |
| `disown` / double-fork | Detaches from shell job table | ⚠️ survives shell exit, NOT group reap |
| `tmux`/`screen` | Separate session under multiplexer server | ✅ but server itself must outlive harness |
| `setsid …` (pid=pgid=sid) | **New session** — escapes group kill | ✅ proven (23+ min ingest survived) |
| **`systemd-run --user --unit=NAME`** | Reparented to user manager; cgroup-owned | ✅✅ definitive — survives everything incl. logout (`Linger=yes`) |

**`systemd-run --user` essentials**: `--unit=` names it (else `run-*.service`);
`--collect` unloads after completion; `-p MemoryMax=…` caps RAM (use for
Xet RAM-staging!); `--wait` blocks (don't use for fire-and-forget);
`--remain-after-exit` keeps results inspectable; status via
`systemctl --user status/is-active/show`; logs via `journalctl --user -u`;
stop via `systemctl --user stop`. Requires the user manager (`systemctl
--user is-system-running` → `running`) and D-Bus (`XDG_RUNTIME_DIR` set) —
both true on Node 1. Our wrapper: `scripts/fetch_model.sh`.

---

## 3. aria2c — the fallback, and when it wins

Segmented downloader: `-x N` connections/server, `-s N` splits, `-k <size>`
chunk size, `-j N` parallel files, `-c` resume via `.aria2` control file.
Measured 0.7→3 MiB/s (x8) on this link vs Xet's 4.3 — Xet wins here because
its adaptive concurrency + CAS range requests tolerate the flaky WiFi better
than fixed splits. aria2c wins when: the URL is static (true resume across
runs), the server throttles per-connection (more splits help), or Xet is
wedged. Our blueprint fallback had a **broken URL builder** (omitted repo
path) — fixed pattern:
`https://huggingface.co/<repo>/resolve/main/<file>` with `-c -x16 -s16 -k1M`.

---

## 4. GGUF quantization — picking the right file before downloading

**Families**: legacy (`Q4_0/Q5_0/Q8_0` — one scale/block, kept for compat) →
**K-quants** (`Q3_K_*`/`Q4_K_*`/`Q5_K_*`/`Q6_K` — 256-weight super-blocks,
hierarchical scales; a "4-bit" K-quant averages ~4.5 bits with metadata) →
**IQ-quants** (importance-matrix guided, best at ≤3 bits) →
**UD (Unsloth Dynamic)** — per-layer intelligent bit allocation; v2.0/v3.0
claim >10% top-1 accuracy gains at equal size by spending bits where layers
are sensitive. `UD-Q4_K_XL` ≈ Q4_K_M size, better quality.

**Rules that prevent pain** (arXiv 2601.14277 + llama.cpp docs + community):
- `Q4_K_M` is the default sweet spot; `Q5_K_M`/`Q6_K` for code/math-heavy use;
  `Q8_0` near-lossless but ~2× the size — test Q4 first.
- **QAT beats PTQ**: quantization-aware-trained models (like Google's
  `qat-q4_0`, trained with quantization in the loop) hold quality far better
  at low bits than post-training quants. Prefer official QAT when offered.
- Never quantize from an already-quantized file (stacked precision loss);
  always start from F16. IQ2/IQ3 without imatrix → repetition loops.
- Calibration corpus must match the workload domain (code needs code).
- Budget 3–4× final size in scratch during conversion pipelines.
- Log the producing llama.cpp build hash with every quant (GGUF metadata
  drifts across versions).

---

## 5. Ollama architecture pinning — why the import probe matters

Ollama vendors **one pinned llama.cpp build** (`LLAMA_CPP_VERSION`). A model
architecture merged upstream *after* that pin is invisible to your Ollama:
`unknown model architecture: '<arch>'` — regardless of version number.
Library pulls usually work (Ollama curates them); **imported GGUFs are where
this bites**. Upgrades can even *remove* architectures (v0.30.0 rebuilt
loading on llama.cpp and dropped `mllama`/vision — still unrecovered).
Pre-download check: find your Ollama's pin, confirm the arch string (e.g.
`gemma4`) exists in that llama.cpp's `llama-arch.cpp`. Our import probe
(`ollama create` on the QAT GGUF) is exactly this check, executed.

---

## 6. Gemma 4 12B architecture — what we're actually about to run

(Tech report arXiv 2607.02770 + HF card + visual guides.)
- **12B Unified, encoder-free**: no separate vision/audio encoders — raw
  48×48×3 image patches via a 35M matmul, raw 16kHz/40ms audio chunks
  projected straight into embedding space. (Why our `mmproj` is tiny/optional
  here, unlike encoder-based VL models.)
- **Hybrid attention**: interleaved local sliding-window (512-token window in
  v4, down from 1024) + global layers; **last layer always global**. KV cache
  stays small → fits 16GB RAM better than full-attention 12Bs.
- **262K vocabulary** (large embedder ~1B params), **256K context** (we'll use
  8192 per harness convention), RoPE 1M global / 10k local, RMSNorm +
  pre/post-norm + QKNorm, 48 layers, 11.95B params, Apache 2.0.
- **MTP drafter head** (400M): speculative decoding built in — draft tokens
  via a 4-layer head cross-attending the main KV cache (no prefill, any draft
  length), top-k vocab clustering cuts the LM-head matmul 262K→4K. Relevance:
  real latency wins IF the runtime enables speculative decoding (Ollama: check
  support; llama.cpp: `--speculative-*` flags).
- Family context: 26B-A4B MoE (3.8B active) exists — a future candidate if 12B
  dense proves too slow on CPU.

---

## 7. Link layer — WiFi power_save on bursty transfers

`wlo1` reports `Power save: on`. Power-save dozes the radio between beacons;
fine for interactive use, but on bursty bulk transfers (Xet's fill→flush
cycles) each wake adds latency and sharpens BTOP's stop/start appearance.
Mitigation: `iw dev wlo1 set power_save off` for the fetch window (needs
CAP_NET_ADMIN — we have passwordless sudo; persist via NetworkManager
`wifi.powersave=2` or a udev rule if adopted permanently). Status: measured,
not yet applied — N0 call.

---

## 8. Verification chain (the gate before `ollama create`)

1. Sizes + SHA256 from HF API **before** downloading (tree endpoint for sizes;
   `model_info(files_metadata=True)` → `siblings[].lfs.sha256`).
2. `sha256sum` after download — reject on mismatch (the Qwen3-0.6B corrupt-file
   incident is why this gate exists).
3. GGUF sanity: `gguf-dump` header parse (magic `GGUF`, version, tensor count)
   catches truncation before the import probe burns time.
4. `ollama create` = architecture-support probe (see §5).
5. Single 512-cap telemetry run = performance probe (see screening harness).

---

## 9. Sources

- HF download guide + Xet: huggingface.co/docs/huggingface_hub/en/guides/download ·
  huggingface.co/docs/hub/xet · manage-cache · env vars reference
- HF forum: "Is hf download really auto resume" (175105) · xet-core#358 ·
  huggingface_hub#3036
- man systemd-run · ArchWiki systemd/User · RHEL cgroup docs · Codex #10860
- arXiv 2607.02770 (Gemma 4) · arXiv 2601.14277 (GGUF quants) ·
  llama.cpp quantize README · Qwen llama.cpp docs · Unsloth Dynamic 2.0/3.0
  docs · Grootendorst Gemma 4 visual guide · Local AI Master Ollama-arch table
- r/LocalLLaMA (GGUF methods; UD naming) · CachyOS wifi-powersave tip

*Companion artifacts: `scripts/fetch_model.sh`, N0 briefing FED-BRIEF-NODE0-FDL-001,
live ingest logs `/home/xnai/ollama-install/hf-gemma4-qat*.log`,
`~/.cache/huggingface/xet/logs/`.*
