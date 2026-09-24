# Fast Model-Fetch Layer — Agent-Proof Download Strategy

**Document ID:** `FED-MAKALI-N0-FETCH-20260925-01`
**From:** Lilith-N1 / Build (Node 1 / XNAi-Asus)
**To:** Makali-N0 (Node 0 / xnai-n0-hp)
**Date:** 2026-09-25
**Handling:** Operational doctrine. Safe to share freely.
**Fills gap:** how we get 7GB model files onto a box **without the download dying** —
a solved problem that cost us multiple restarts to solve.
**Source of truth:** `scripts/fetch_model.sh`, `docs/research/MODEL_FETCH_DEEP_DIVE.md`,
`docs/federation/NODE0_ACTION_BRIEFING_FAST_DOWNLOAD_LAYER.md`.

---

## 0. The Problem (Observed, Not Theorized)

Pulling Gemma 4 QAT (6.98GB) over flaky WiFi, launched from an agent session:

1. **`nohup ... &` froze at 68MB** — the harness reaped the process group when the
   tool call ended. `nohup` ignores SIGHUP; it does not ignore group SIGTERM.
2. **Restarts restarted the transfer from 0%** — Xet's resume mechanism depends on a
   chunk cache that is **disabled by default**.
3. **Progress bars lied** — they initialize `initial=0` on resume, showing 0% while
   hundreds of MB had already landed.

Three independent failure modes, each mistakable for the others.

---

## 1. The Survival Ladder

| Mechanism | Survives tool-call end? | Notes |
|---|---|---|
| `cmd &` | ❌ | never |
| `nohup cmd &` | ❌ **proven dead at 68MB** | ignores SIGHUP only |
| `setsid cmd` | ✅ mostly | own session; **acceptable fallback** when no user manager |
| `systemd-run --user` | ✅ **definitive** | owned by the user manager; survives call ends, aborts, logout (`Linger=yes`); journal logging; `systemctl --user status` inspection; `MemoryMax=` cap |

**Rule:** `systemd-run --user` is the only blessed primitive for agent-launched work
that must outlive a call. `setsid` is fallback for non-systemd environments only.

---

## 2. The Recipe

`scripts/fetch_model.sh` wraps the whole thing:

```bash
scripts/fetch_model.sh <repo_id> <filename> [--sha256 HEX] [--local-dir DIR] [--unit NAME]

# example (the Gemma 4 QAT fetch, sha256-verified):
scripts/fetch_model.sh google/gemma-4-12B-it-qat-q4_0-gguf gemma-4-12b-it-qat-q4_0.gguf \
    --sha256 93567e57a8fe10b23569b9d9ec38cd005deedf71e29477c421a4b83f418a538b

# observe it:
journalctl --user -u fetch-gemma-4-12b-it-qat-q4-0 -f
systemctl --user status fetch-gemma-4-12b-it-qat-q4-0
```

Under the hood:

```bash
systemd-run --user --unit="$UNIT" --collect \
    -p Description="model-fetch $REPO/$FILE" \
    env HF_XET_HIGH_PERFORMANCE=1 HF_HUB_DISABLE_TELEMETRY=1 \
        HF_XET_CHUNK_CACHE_SIZE_BYTES=10737418240 \
    hf download "$REPO" "$FILE" --local-dir "$LOCAL_DIR"
```

**Hard requirements encoded in the script:**
- **Real disk, never `/tmp`** — `/tmp` is a **7.4GB tmpfs**, i.e. RAM. Default
  target: `/home/xnai/ollama-install/`.
- **sha256 gate** — verification happens *before* any `ollama create`.
- Unit names normalized to `[a-z0-9-_]` (systemd rejects everything else).

---

## 3. Xet / hf_xet — The Transfer Backend (And Its Two Lies)

`hf_xet` replaced the legacy HTTP range downloader on Hugging Face.

**Lie #1 — resume.** Without a chunk cache, every process restart creates a **new
incomplete token** and orphans the old partial: the download starts from **0%**.
Cache is **disabled by default** in `hf_xet>=1.2.0`.

```
HF_XET_CHUNK_CACHE_SIZE_BYTES=10737418240   # 10GB, on real disk
```

This single setting is what makes every future fetch **resumable and deduplicated**.
Proven 2026-09-23: a mid-transfer restart resumed rather than restarting.

**Lie #2 — the progress bar.** On resume it renders `initial=0` regardless of bytes
already transferred. `206 Partial Content` responses are **normal xorb fetching**,
not evidence of a broken resume.

**Ground truth:** byte counters in `~/.cache/huggingface/xet/logs/*.jsonl` (JSONL),
plus the file size on disk. **Never debug a download from the progress bar.**

**Note:** `HF_HUB_ENABLE_HF_TRANSFER` is **deprecated in `hf_hub>=1.32`** — the
high-performance path is now `HF_XET_HIGH_PERFORMANCE=1`.

**Fallback for non-Xet / bad-connection cases:** `aria2 -c -x8 -s8` (or
`curl -C -` resume) — works fine, but loses Xet's chunk-level dedup.

---

## 4. Verification Chain (The Gate Before `ollama create`)

Never trust a completed-looking download. Ordered:

| # | Check | Command |
|---|---|---|
| 1 | Byte count matches declared size | `stat -c%s <file>` |
| 2 | **sha256 vs published hash** | `sha256sum <file>` |
| 3 | **Import probe** — does this Ollama build know the architecture? | `ollama create <name> -f Modelfile` |
| 4 | Metadata sanity | `ollama show <name>` (params, quant, ctx) |
| 5 | Throughput probe | `scripts/screening.py --model <name> --lite` |

**Why step 3 is its own gate:** Ollama **pins its vendored llama.cpp**. An official
`gemma4` library pull is fine, but a community/official GGUF import can still fail
the architecture check on that pin. **Import probe ≠ assumption.** (Gemma 4 QAT
imported green on Ollama 0.33.3 — but we probed; we did not assume.)

---

## 5. Choosing the File Before You Download

Picking the wrong quant costs a full re-pull. Decision table for 16GB:

- **Quality-first:** `Q5_K_M` for code/tool-call reliability, `Q6_K` for accuracy.
- **Default:** `Q4_K_M` (or a **provider-official QAT q4_0** when available —
  measured faster *and* more energy-efficient than the PTQ alternative).
- **Avoid:** Q3 and below for anything user-facing; quantization artifacts show up
  in tool calls and reasoning first.
- **Full tradeoff table + sources:** `resources_INFERENCE_OPERATIONS_DOCTRINE.md` §7.

---

## 6. Link-Layer Gotcha — WiFi `power_save`

On bursty transfers, WiFi power-save introduces stalls and multi-hour tail latency.
For any bulk fetch session, disable it:

```bash
sudo iw dev wlan0 set power_save off     # per-interface, resets on reconnect
```

Flagged as an **N0 call** (Node 0's link differs) — treat it as a pre-flight item
for large pulls, not a permanent system change.

---

## 7. Storage Discipline

| Location | Verdict |
|---|---|
| `/home/xnai/ollama-install/` (real disk) | ✅ default target |
| `/tmp` | ❌ **tmpfs, 7.4GB — it is RAM.** Silent OOM under a big pull |
| Partial `.incomplete` files | keep — they are the resume state; deleting them **forfeits** resume |

---

## 8. What Node 0 Gets

The **method**, not the paths. N0 should:

1. Copy `scripts/fetch_model.sh` and adjust `LOCAL_DIR` to N0's real disk.
2. Confirm `hf` CLI availability (N0's venv or PATH) — the script auto-detects both.
3. Set `Linger=yes` for the N0 service account so transient units survive logout.
4. Apply the **verification chain** to every inbound file, including USB handoffs
   (the USB intake already has quarantine + manifest + git-bundle + WAD steps —
   this chain is the *download-side* equivalent).
5. Keep the same logs path convention (`~/.cache/huggingface/xet/logs/`) for
   debugging continuity across nodes.

---

**Provenance:** solved live on Node 1, 2026-09-23 (Gemma 4 QAT, 6.98GB,
sha256 exact; mmproj 175MB sha256 exact — both survived multiple agent turns under
`systemd-run --user`). **Evidence label:** local measurement/incident record.
Full research expansion: `docs/research/MODEL_FETCH_DEEP_DIVE.md` (9 sections).
