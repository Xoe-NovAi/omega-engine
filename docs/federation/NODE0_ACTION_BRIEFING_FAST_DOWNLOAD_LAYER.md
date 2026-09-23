# 🔱 Node 0 Action Briefing — Fast Model Download Layer (Xet / hf_transfer)

**Doc ID**: `FED-BRIEF-NODE0-FDL-001` | **Date**: 2026-09-23
**From**: Node 1 (ASUS ExpertBook / `xnai-n1-asus`)
**To**: Node 0 (HP Pavilion Archival Bastion / `100.123.51.67`)
**Status**: 🔄 IN PROGRESS — model ingest live; integration decision requested from N0

> ## ⚡ Live-verified facts (measured on Node 1, 2026-09-23, during this ingest)
> - **Download target**: `google/gemma-4-12B-it-qat-q4_0-gguf` (official Google QAT)
>   - `gemma-4-12b-it-qat-q4_0.gguf` — **6,975,879,296 bytes (6651 MiB)**,
>     sha256 `93567e57a8fe10b23569b9d9ec38cd005deedf71e29477c421a4b83f418a538b`
>   - `mmproj-gemma-4-12b-it-qat-q4_0.gguf` — 175,115,616 bytes, sha256
>     `cb018338a7538a9814d994bfe54644c71eb7ed54e31eae2f721e45fd3c260da7`
>   - repo commit `29d097773436b69ff9feafd636ab4cf873786537`
> - **Live toolchain**: `huggingface_hub 1.32.0` + **Xet backend** (built into
>   hf_hub ≥1.31). **`HF_HUB_ENABLE_HF_TRANSFER` is DEPRECATED** in 1.32 —
>   the current high-performance toggle is **`HF_XET_HIGH_PERFORMANCE=1`**.
> - **Measured throughput**: ~4.3 MiB/s over WiFi `wlo1` (flaky consumer link;
>   earlier aria2c x8 attempt crawled at 0.7→3 MiB/s with 19h ETA spikes).
> - **RAM-staging behavior (IMPORTANT new invariant)**: Xet does NOT stream
>   straight to disk. It buffers transferred chunks in anonymous process RAM
>   (RSS peaked ~1.3 GiB), then flushes ~18 MiB batches to the `.incomplete`
>   file. Disk growth matched process `write_bytes` 1:1 during observation.
> - **End-to-end expectation**: verify sha256 → `ollama create` import probe →
>   single 512-cap telemetry run. Ollama 0.33.3 gemma4-arch support is the
>   open question (import probe will answer it).

---

## 1. Executive Summary

Node 1 is ingesting the **official Google Gemma 4 12B QAT GGUF** (q4_0) using the
fast parallel download layer. The task has two halves:

1. **One-shot ingest** (this briefing covers it, live) — get the model onto real
   disk, verify integrity, import into Ollama, run a telemetry probe.
2. **Engine integration** (the actual N0 ask) — make fast, resumable, verified
   model fetching a permanent capability of the Engine so agents never again
   hand-type `ollama pull` on a flaky link.

This briefing documents **what the fast-download layer is**, **what we falsified
about the pasted blueprint during the live run**, and the **decision N0 needs to
make** on integration depth.

---

## 2. The Fast Download Layer — Current State of the Art

The user-supplied blueprint proposed `hf_transfer` (Rust-accelerated) with an
aria2c fallback. Our live run on Node 1 (huggingface_hub 1.32.0) **falsified the
primary path**:

| Blueprint claim | Reality (measured) |
|---|---|
| `HF_HUB_ENABLE_HF_TRANSFER=1` is the accelerator | **Deprecated**. hf_hub 1.32 emits `FutureWarning`: hf_transfer is no longer used. Use **`HF_XET_HIGH_PERFORMANCE=1`** — Xet is built into hf_hub now. |
| `python -m huggingface_hub.cli.cli download` | Modern CLI is **`hf download`** (verified working; `huggingface-cli` alias still present) |
| Downloads stream in-place | Xet **stages in RAM, flushes in bursts** (~18 MiB batches). RSS peaked ~1.3 GiB on a 16 GiB box — safe, but a real invariant to document. |
| aria2c `-x8 -s8` as fast path | Measured 0.7→3.0 MiB/s, ETA up to 19h on this link. Xet achieved ~4.3 MiB/s with adaptive concurrency (4 conns, success_ratio 1.0). Xet wins on flaky WiFi. |
| Content-Length via redirect HEAD | Xet CDN redirects to `us.aws.cdn.hf.co/xet-bridge-*`; bandwidth throttling is per-connection, adaptive concurrency compensates |

**Verdict**: the engine's download layer should target **huggingface_hub ≥1.31
with Xet high-performance enabled**, with aria2c as a documented fallback only.

---

## 3. Blueprint Corrections (apply to any engine integration)

1. **`HF_HUB_ENABLE_HF_TRANSFER` → `HF_XET_HIGH_PERFORMANCE`** (env var rename;
   hf_transfer pip package no longer used by hf_hub 1.32).
2. **The blueprint's `_fallback_aria2c` builds a broken URL** —
   `f"https://huggingface.co{output_path.name}"` omits the repo path. Must be
   `https://huggingface.co/{repo_id}/resolve/main/{filename}`.
3. **No `--ngl 99` / GPU assumptions** — Node 1 is CPU-only. The blueprint's
   `launch_server()` with `--ngl 99` and 64K context is N/A on this hardware
   (16 GiB single-channel RAM; 64K ctx would exceed memory; our harness uses
   `OLLAMA_CONTEXT_LENGTH=8192` + `MAX_LOADED_MODELS=1`).
4. **Don't bypass Ollama** — blueprint talks to bare `llama-server`. Node 1's
   stack is Ollama-on-11434 (systemd, `AllowedCPUs=0-11` +
   `OLLAMA_NUM_THREADS=8`, pin-trap doctrine). Integration = a downloader that
   feeds `ollama create` via Modelfile, not a second inference server.
5. **Pins that proved correct**: `aria2c -c` resume, real-disk `/home/xnai/
   ollama-install/` (NOT `/tmp` — 7.4 GiB tmpfs, model is 6.98 GiB), sha256
   verification before import.

---

## 4. Recommended Engine Integration (N0 decision point)

Proposal: add a **`scripts/model_fetch.py`** engine primitive:

```
[Agent trigger] → [capability check: hf_hub≥1.31 + xet] → [hf download --local-dir on real disk]
                → [sha256 verify vs HF API] → [ollama create from GGUF] → [telemetry probe]
```

- **Primary**: `hf download <repo> <file> --local-dir <cache>` with
  `HF_XET_HIGH_PERFORMANCE=1` (Xet = built into hf_hub ≥1.31, no extra dep).
- **Fallback**: aria2c `-x16 -s16 -k1M -c` with **correct repo-path URL**.
- **Verify**: fetch expected sha256 from `HfApi().model_info(..., files_metadata=True)`;
  reject on mismatch (invents the corrupt-file trap from Qwen3-0.6B incident).
- **Import**: `ollama create` with a Modelfile (`FROM <path>.gguf`) —
  grep `num_ctx`, `num_thread 8`, `temperature` from harness conventions.
- **Cache**: default to `/home/xnai/models/` (existing local GGUF library) +
  real-disk scratch `/home/xnai/ollama-install/` for one-shot ingests.
- **Concurrency guard**: `MAX_LOADED_MODELS=1` + single downloader at a time
  (avoid RAM-staging + resident-model collision on 16 GiB).

N0 to decide: (a) implement now as `scripts/model_fetch.py` + ROADMAP entry,
(b) keep as ad-hoc one-shot only (this ingest), or (c) defer pending RAM
upgrade. Recommendation: **(a)**, small surface, high repeat value.

---

## 5. Current Ingest State (Node 1, live)

- ✅ Repo metadata + sha256 captured from HF API (both files listed above).
- ✅ `hf_transfer 0.1.9` installed in project venv (kept for fallback
  compatibility; deprecated for primary path).
- ✅ Xet download running (`setsid`, PID survives shell teardown), writing to
  `/home/xnai/ollama-install/gemma4-qat/`.
- 🔄 1,771 MiB / 6,651 MiB (27%) at last check; ~4.3 MiB/s; ETA ~20 min.
- ⏭ Next: sha256 verify → `ollama create` import probe (gemma4-arch support in
  Ollama 0.33.3 = open question) → single 512-cap telemetry run
  (`screening.py --model gemma-4-12b-it-qat-q4_0 --num-predict 512`).

---

## 6. Open Questions for Node 0

1. **Engine integration depth**: full `scripts/model_fetch.py` primitive vs
   one-shot ingestion (see §4).
2. **Xet RAM-staging policy**: accept ~1.3 GiB transient RSS during fetches,
   or add a memory check before starting a fetch (recommend accept; it frees
   after each flush cycle).
3. **QAT model role**: is `gemma-4-12b-it-qat-q4_0` the interactive/default
   model (replacing gemma-3-12b), or a screening-candidate only?

---

## 7. Definitive Background-Download Solution (PROVEN 2026-09-23)

**Problem**: agent-harness shells kill the child process GROUP when a tool call
ends (timeout/completion/abort). Proven live: a `nohup ... &` hf download
froze dead at 68MB. `nohup` only ignores SIGHUP — it does not survive group
SIGTERM (same finding as Codex CLI issue #10860: "nohup killed at turn end,
setsid survives").

**Solution ladder** (weakest → definitive):

| Method | Survives call end? | Verdict |
|---|---|---|
| `cmd &` / `nohup ... &` | ❌ killed with process group | DO NOT USE for agent downloads |
| `setsid ... &` (own session: pid=pgid=sid) | ✅ survives | Acceptable stopgap (used for main ingest, PID 197041) |
| **`systemd-run --user --unit=NAME`** | ✅✅ owned by user manager; survives call ends, aborts, logout (`Linger=yes`, manager `running`) | **DEFINITIVE. Use this.** Logs via journal, status via `systemctl --user`. |

**Live proof** (this session): `mmproj-gemma-4-12b-it-qat-q4_0.gguf`
(175,115,616 bytes) fetched via `systemd-run --user` unit
`gemma4-mmproj-fetch` — survived multiple agent tool-call gaps (parent =
`systemd --user`, NOT any agent shell), completed, **sha256
`cb018338…0da7` matched exactly**.

**Reusable primitive**: `scripts/fetch_model.sh <repo> <file> [--sha256 HEX]
[--local-dir DIR] [--unit NAME]` — wraps the systemd-run pattern with
machine rules baked in (real disk default `/home/xnai/ollama-install/`,
`HF_XET_HIGH_PERFORMANCE=1`, sha256 gate reminder). Agents must use this
(or raw `systemd-run --user`) for every background download from now on.

**Xet resume finding (CORRECTED 2026-09-23 — earlier copy-trick claim falsified)**:
restarting an `hf download` mints a NEW `.incomplete` token (Xet signed-URL
ETags rotate) and the new process downloads from 0% into the new file —
copying old partial bytes onto the new token name does **NOT** resume (live
test: copied 3.5GB → new process ignored it, minted a third token, downloaded
fresh to 2.4GB). Per HF docs, `huggingface_hub` resumes via the **file cache**
but `hf_xet` resumes via the **chunk cache** — and the chunk cache is
**DISABLED by default** (hf_xet≥1.2.0). The real fix, now baked into
`scripts/fetch_model.sh`: set **`HF_XET_CHUNK_CACHE_SIZE_BYTES=10737418240`**
(10GB) so all future fetches are resumable + deduped. (Also useful:
`HF_HUB_DISABLE_XET=1` forces plain-HTTP path for diagnostics;
`HF_XET_RECONSTRUCT_WRITE_SEQUENTIALLY=1` for HDDs; `hf cache verify`
checks local files against Hub checksums.) (Aria2c `-c` resume does not apply
to hf `.incomplete` files.)

**Secondary finding**: WiFi `wlo1` has `power_save: on`. On bursty transfers
(Xet RAM-stage → flush cycles) this sharpens the troughs BTOP shows. For
sustained bulk fetches consider `iw dev wlo1 set power_save off` (reversible;
re-enable after). Not yet applied — N0 call.

---

*Prepared by Node 1 Build agent during live ingest. Federation context:
`docs/federation/` (master spec + L2 join + NFS briefings). Node 1 model list
and screening results: `docs/BENCHMARKS.md`, `benchmarking/screening/`.*