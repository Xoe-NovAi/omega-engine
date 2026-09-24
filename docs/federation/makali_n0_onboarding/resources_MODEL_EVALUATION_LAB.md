# Model Evaluation Lab — Screening Protocol, Telemetry & Measured Leaderboard

**Document ID:** `FED-MAKALI-N0-EVAL-20260925-01`
**From:** Lilith-N1 / Build (Node 1 / XNAi-Asus)
**To:** Makali-N0 (Node 0 / xnai-n0-hp)
**Date:** 2026-09-25
**Handling:** Operational doctrine + measured reference data.
**Fills gap:** the pack had *split-test findings* (hosted persona models) but **no
local-model evaluation methodology** — the discipline that decides what runs on 16GB.
**Source of truth:** `scripts/screening.py`, `benchmarking/screening/*.json`,
`docs/models/*.md`, `docs/BENCHMARKS.md`.

---

## 0. Why Evaluation Is a Strategy, Not a Hobby

On a 16GB CPU-only box, **every model you install costs RAM you do not have and
time you cannot spare.** Model selection is therefore an empirical question with a
protocol, not a forum opinion. Three disciplines enforce this:

1. **A fixed screening protocol** so numbers are comparable across models and time.
2. **Telemetry alongside throughput** — speed without energy/thermals is half a metric.
3. **Model cards with evidence labels** — provider claims never get to masquerade
   as local measurements.

---

## 1. The GSCA Screening Protocol

`scripts/screening.py` — **3 prompts × 3 temperatures × 2 contexts = 18 runs/model.**

| Dimension | Values | Why |
|---|---|---|
| Prompts | 3 (JSON parsing, async-vs-threading, recursive flatten) | spans instruction-following, explanation, code |
| Temperature | 0.1, 0.5, 0.7 | correctness → balance → diversity |
| Context | 4096, 8192 | measures context-scaling penalty |
| `num_predict` | **512 (bounded)** | see §2 — this guard is mandatory |
| `think` | explicit `off` default | see §3 |

**Lite mode** (added 2026-09-23): `--lite` → 3 prompts × temp 0.1 × ctx 4096 =
**3 runs, ~5 minutes.** Use for verdicts on operating fitness; use the full 18 for
confidence intervals and context/temp sensitivity.

```bash
.venv/bin/python scripts/screening.py --model gemma4-12b-qat --think off --lite
.venv/bin/python scripts/screening.py --model qwen2.5-coder-7b        # full 18
```

**Engineered robustness (all learned the hard way):**
- **Incremental save after every run** — interrupt loses nothing.
- **Auto-resume** from the existing results file (`[RESUME] Found N completed run(s)`).
- **Separate output files** (`_lite_screening.json` vs `_screening.json`) so a lite
  run can never silently contaminate a full matrix.
- **Errors are recorded, not fatal** — a failed run appends an error row and continues.
- **Run configuration is persisted** in the JSON (`num_predict`, `think`,
  temperatures, contexts) — results without their config are not reproducible.

---

## 2. The `num_predict` Guard (Harness Failure Class #1)

**Observed bug:** Ollama's default `num_predict` is **unbounded**. Reasoning models
that never emit EOS (Qwen3 think loops) generate **forever** — the request hangs,
the telemetry thread runs, and the run never returns.

**Fix:** `--num-predict 512` default in `generate()` + CLI override + JSON metadata.

**This is not theoretical.** It was discovered live during Qwen3 screening and
would have hung `phi4-mini-reasoning` (still deferred) on its first run.

**Rule for N0:** never call `/api/generate` against a reasoning model without an
explicit `num_predict`. 512 is our screening budget; raise it only deliberately.

---

## 3. The Thinking-Trap (Harness Failure Class #2)

**Observed bug:** Gemma 4 / Qwen3 default to **thinking on**. Under a 512-token
budget the model spends the *entire* budget on its internal think trace and returns
an **empty answer** — correct-looking telemetry, zero useful output.

```
# default (think on):  512 tokens → all trace   → response: ""  (length)
# think:false:         512 tokens → real answer → response: 1773 chars
```

**Fix (implemented):** `--think {on,off}` on `screening.py`, **default `off`**,
with the chosen mode recorded in result JSON. `generate()` takes an explicit
`think` flag in the payload.

**Corollary:** depth of reasoning is **not** produced by flipping a thinking toggle.
Our hosted split-test proved the same point from the other direction — MiMo on
`OFF` out-deepened Space Bunny on `medium`. Treat **model × thinking as independent
variables**; log the provider's actual behavior per route (some providers impose
server-side floors regardless of the client setting).

---

## 4. TelemetryCollector — Energy & Thermal, Privilege-Free

Reference: `docs/TELEMETRY_PLAN.md`. Runs a background sampler at **2 Hz (~2 ms/tick,
<0.5% CPU)** during each screen, returning aggregated stats on `stop()`.

**Reads:**
- **RAPL** `energy_uj` → package power (W), energy/token (J), tokens/joule.
- **Thermal zones** → package temp mean/max.
- **cpufreq** `scaling_cur_freq` → frequency mean/max across **all** online cores.

**Hard-won correctness rules (do not re-derive):**

| Trap | Correct handling |
|---|---|
| RAPL is `r--------` (root-only) on stock Ubuntu | udev rule + tmpfiles.d chmod `0440 root:xnai`; code **degrades gracefully** if unreadable (power omitted, temp/freq still captured) |
| Counter wraps | `max_energy_range_uj = 262,143,328,850` ≈ 262 kJ → wraps ~87 min @ 40W; **wraparound correction mandatory** |
| First sample artifact | skip power on loop iteration 1 (no valid ΔE yet) |
| `scaling_cur_freq` is **kHz** | divide by 1000 |
| `cpu0` underrepresents boost | read every online core, take the **max** |
| ACPI vs CPU thermal zones | **prefer** `x86_pkg_temp`/`cpu_thermal`/`TCPU`/`intel_powerclamp`; `acpitz` may be skin temp |

**No sudo, no external deps.** Optional `turbostat` for forensic runs only.

---

## 5. Model Card Contract (Evidence Discipline)

Every model decision gets a card at `docs/models/<id>.md`. **Required sections**
(enforced by `scripts/validate_model_cards.py`, runs in `make lint`):

```
## Executive Summary
## Architecture
## Local Measurement
## Provider Claims
## Omega Verdict
```

**Evidence labels are mandatory** and must be one of exactly:

```
Provider claim | Community benchmark | Independent eval | Local measurement | Reproduced
```

**The rule that prevents hype creep:** *a provider claim never becomes a local
measurement by repetition.* MMLU-Pro 77.2% is a **Provider claim**; 4.54 t/s is a
**Local measurement**. The lint gate rejects any other label string — including
variants like `Provider claim (model card)`.

**Frontmatter carries `research_status`**: `candidate` → `active` → (optionally)
`superseded`, plus `confidence`, `last_verified`, and a `config_hash`/`reproducibility`
block (hardware, Ollama/llama.cpp versions, seed).

**Promotion rule (lived):** `candidate` = one decisive probe; `active` = screening
confirms it. Gemma 4 QAT: single probe +64%/−42% → candidate; 3-prompt lite screen
+45%/−49% → **active**. Conflicting evidence **downgrades** rather than averaging.

---

## 6. Measured Leaderboard (Node 1, i7-13620H, 2026-09-23/25)

All runs: `AllowedCPUs=0-11`, `OLLAMA_NUM_THREADS=8`, `MAX_LOADED_MODELS=1`,
ctx 4096/8192, temp 0.1/0.5/0.7, `num_predict=512`.

| Model | Runs | Avg t/s | Range | Energy J/tok | Peak °C | Source (repo-relative) |
|---|---|---|---|---|---|---|
| `qwen3-0.8b-quick` | 18 | **49.45** | 44.5–51.2 | 0.66 | 97.0 | `benchmarking/screening/qwen3-0.8b-quick_screening.json` |
| `rocracoon-3b` | 18 | **11.70** | 10.5–12.4 | 3.14 | 97.0 | `benchmarking/screening/rocracoon-3b_screening.json` |
| `qwen2.5-coder-7b` | 18 | **7.93** | 7.3–8.3 | — | — | `benchmarking/screening/qwen2.5-coder-7b_screening.json` |
| `krikri-8b` | 18 | **6.22** | 4.9–6.6 | — | — | `benchmarking/screening/krikri-8b_screening.json` |
| `gemma4-12b-qat` | 3 (lite) | **4.54** | 4.1–4.8 | **6.50** | **92.1** | `benchmarking/screening/gemma4-12b-qat_lite_screening.json` |
| `qwen2.5-coder-14b` | 18 | **4.06** | 3.8–4.2 | — | — | `benchmarking/screening/qwen2.5-coder-14b_screening.json` |
| `gemma-3-12b` *(baseline)* | probe | 3.12 | — | 12.69 | 98.0 | `docs/models/gemma4-12b-qat.md` |

**Headline result:** Gemma 4 12B **QAT q4_0** vs Gemma 3 12B **PTQ IQ3_M** on the
same chassis — **+45% throughput, −49% energy/token, 6°C cooler peak** at the same
power envelope. This is the empirical case for **preferring official QAT quants
over PTQ at low bit-widths.**

**Role assignment:**
- Generalist/reasoning → `gemma4-12b-qat` (**active**)
- Code → `qwen2.5-coder-7b` (**active**), `-14b` for complex work
- Bench harness / rapid iteration → `qwen3-0.8b-quick` (49 t/s, 0.66 J/tok)
- Superseded → `gemma-3-12b`

**Honest limitations of this table:**
- Only 3 of 7 rows carry telemetry (collected before `TelemetryCollector` landed).
- `gemma4-12b-qat` is a **3-run lite screen**, not an 18-run matrix — throughput
  direction is confirmed, context/temp sensitivity is not.
- Throughput is **not** quality. This table says nothing about *correctness*; that
  is what model cards + provider benchmarks (properly labeled) are for.

---

## 7. What N0 Should Build (Method Transfer)

1. Re-run `scripts/screening.py` on N0 silicon with N0's own thread/mask optimum.
2. Keep the **protocol fixed** so N0 numbers are internally comparable.
3. Re-collect **telemetry** on rows that lack it (the collector now exists).
4. Maintain N0's own `benchmarking/screening/*.json` + `docs/models/*.md` cards.
5. Share results via mesh/USB; reconcile by **reproduced** evidence label, not by
   picking the number you prefer.

---

**Provenance:** protocol + telemetry implemented and validated on Node 1,
2026-09-22/25. Raw results: `benchmarking/screening/*.json`.
**Evidence label:** local measurement (throughput/energy/thermal), provider claim
(external benchmarks — see cards).
