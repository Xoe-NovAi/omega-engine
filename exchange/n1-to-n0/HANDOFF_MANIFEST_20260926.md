# N1 → N0 Handoff Manifest — 2026-09-26

**From:** Lilith-N1 (Node 1) · **To:** Makali-N0 (Node 0)
**Engine SSOT:** `fa9c4edc68fe0f23a052e941f88d573f47c6c249` (`1.6.0-alpha.1`)
**Status of this manifest:** authoritative for the benchmark/Ollama work below.

---

## 1. Supersession — read this first

| File | Status |
|---|---|
| `LILITH_N1_SYNC_RESPONSE_20260926.md` | **SUPERSEDED** — predates the Ollama 0.34.4 upgrade and the LFM default. Retained for history only. |
| `LILITH_N1_SYNC_RESPONSE_FULLPACK_20260926.md` | **STILL CURRENT** for federation answers: device identity, entity count, 8017 discrepancy, and the retraction of the false convergence claim. Its addendum predates the benchmark work; see §3. |
| `BENCHMARK_STUDY_20260926.md` | **CURRENT** — full benchmark study, with a trust-classification section and a disclosed-defect list. |
| `MAKALI_N0_BRIEFING_20260926.md` | **CURRENT** — corrected briefing. Supersedes the flawed first draft (which contained a fabricated 5T datapoint and a duplicated summary block; both fixed). |
| `bench_threads.py`, `embed_service.py`, `bench_memory.py` | **CURRENT** — the harnesses, as-run. |
| `ollama-embed.service.reference`, `ollama-override.conf.reference` | **REFERENCE ONLY** — Node 0 must re-derive its own constants (see §5). `WEBUI_SECRET_KEY` is redacted. |
| `bench-data/` | **CURRENT** raw JSON + live logs, moved off RAM-backed `/tmp`. Includes `VOID_contaminated_powersaver.json`, labelled as a teaching artifact. |

---

## 2. What changed since the last N0 handoff

1. **Ollama upgraded 0.33.3 → 0.34.4.** `ollama-linux-amd64.tar.zst` (1.43 GB), sha256
   `c238986e61d40c0cc5f4a9b9e40b9eea104350b77efa34741fc134e105cb9533` verified before install.
   Rollback: `/usr/local/bin/ollama.v0.33.3.bak` + `/home/xnai/backups/ollama-rollback-v0.33.3/`.
2. **`OLLAMA_NUM_THREADS` removed** from `.env.ollama` and the systemd override. It is not a
   real Ollama setting (maintainer rick-github, ollama#10476: *"OLLAMA_NUM_THREAD is not an
   ollama configuration variable"*). Its presence had us believe the box was tuned to 8
   threads when nothing was being controlled at all.
3. **Thread count is now controlled per-model** via `PARAMETER num_thread N` in a Modelfile,
   and **verified** by parsing `/proc/<pid>/cmdline` for the runner's `-t N`. Do not use `ps`
   for this: it truncates the long runner argv and silently hides the trailing `-t N`.
4. **A second Ollama instance runs on the E-cores** (`ollama-embed.service`,
   `AllowedCPUs=12-15`, `127.0.0.1:11435`). The primary server cannot reach the E-cores at
   all — its `Cpus_allowed_list` is `0-11`. Two instances give true isolation; they also
   sidestep ollama#5724 (open, with dhiltgen), where loading a model blocks in-flight
   requests to already-loaded models.
5. **LFM2.5-2.6B-Q4_K_M is the default entity model** (`lfm25-t6` = same GGUF + `num_thread 6`),
   set in `config/wads/arcana_novai/entities/core/default.yaml`.
6. **zRAM restored; the zRAM gate was removed** from the harness per operator directive.
   The harness now logs zRAM/swap and never refuses a run.
7. **`aria2c` is now doctrine** for all downloads >~5 MB (recorded in `AGENTS.md`).

---

## 3. Benchmark headline — provisional, not settled

Operator caveat carried verbatim: *"We do not have anywhere near enough data to make a call
like that yet — we need many more runs, multiple times over, under various conditions."*

Best measured configuration so far:

| Parameter | Value | Confidence |
|---|---|---|
| P-core LLM threads | **6** | Best or tied on both models; repeatable (CV 0.5–3.8%) |
| P-core LLM model | **LFM2.5-2.6B-Q4_K_M** | ~48–54% faster than phi4-mini at 6T |
| E-core embedder threads | **4** | 8.0 texts/s sustained, 0 errors |
| 12 P-core threads | **provisionally ruled out** | ≈60% drop under embedding load, **but that measurement was flagged not-repeatable** |

Concurrency cost at 6 threads: **−15% (LFM)** and **−17% (phi4-mini)**; TTFT rises 69→79 ms.
The embedder itself is unaffected (0 errors across all runs).

**Do not treat any of this as final.** See the study's "Known defects" list — the most
important being that config 5 has no data, LFM was only swept at 4/6/8/12, LFM concurrency was
measured once, and **every current run is thermally limited** (94–96 °C), so these are
steady-state-in-heat numbers rather than burst numbers.

---

## 4. What Node 0 must NOT copy

Per the standing N0 doctrine (never copy N1 constants, re-derive locally):

- `AllowedCPUs=0-11` — N1 is a hybrid 6P+4E part. **N0 is Ryzen; its topology differs.**
  The P-core-vs-E-core split, and the E-core embedding sidecar, are N1-specific findings.
- The 45 W package ceiling, 100 °C tJMax, and 33–54 W power ranges are i7-13620H numbers.
- Single-channel DDR5-5200 STREAM result (~32.6 GB/s) is N1's memory subsystem.
- The `WEBUI_SECRET_KEY` is redacted here and must stay redacted.

What **is** portable: the *methodology* (verified `-t` gate, fixed-token output, live
telemetry, power min/max, memory logging, thermal-limit disclosure) and the harness code.

---

## 5. Open items for Node 0

| Priority | Item |
|---|---|
| P0 | **8017 exchange pipe** — documented as a read-only file pipe; actually serves SearXNG (`PUT`→404 not 501, both documented paths 404). Needs N0 disposition. |
| P0 | Re-derive thread/affinity constants on Ryzen; do not import N1's. |
| P1 | Krikri-8B sweep (6T/8T) — Greek specialist, still unbenchmarked. |
| P1 | zRAM-on vs zRAM-off control series (gate is gone, so this must be measured, not assumed). |
| P1 | Replicate the 12T-under-embedding collapse, which the harness could not call repeatable. |
| P2 | Node 0 federation survey: embedder, dims, backend, drawer counts, disk/RAM headroom. |
| P2 | Context-length and KV-quantization sweeps. |

---

## 6. Integrity

Verify before trusting:

```bash
sha256sum -c exchange/n1-to-n0/SHA256SUMS
```
