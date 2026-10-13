# Encoder Baseline Results — P7.3 pre-LoRA (2026-10-13)

First measured results on the encoder pivot. Companion to
`ENCODER_SPECIALIST_EVAL_20261009.md`. Harness: `scripts/sms/encoder_eval.py`.
Raw: `runs/encoder_baseline_20261013/{lfm25_enc_350m,modernbert_base}.json`.

## Method

Frozen encoder (no fine-tune, no task head) → attention-mask-weighted mean
pooling of `last_hidden_state` → `LogisticRegression` probe (fixed seed
20261013) → holdout scoring. Majority floor computed from the **train**
distribution. Per-case latency = tokenize + forward + predict, single
text, CPU. This is the spec's "baseline few-shot eval (no training)"
milestone — the honest floor of what the architecture buys for free.

## Headline: failure_classifier — the pivot question, answered

| System | Source | Acc | Macro-F1 | Note |
|---|---|---|---|---|
| **LFM2.5-Encoder-350M (frozen + probe)** | this run | **0.9643** | **0.9545** | no training |
| **ModernBERT-base (frozen + probe)** | this run | **0.9643** | **0.9545** | no training |
| LFM2.5-350M generative, 5 SFT steps | Phase 3 analysis | 0.111 | — | majority floor 0.444 |
| LFM2.5-350M generative, zero-shot | Phase 3 | 0.056 | — | floor 0.444 |
| Majority floor (this holdout) | computed | 0.7143 | — | 20/28 keep |

**Both frozen encoders beat the generative SFT model by 8.7× with no
training at all.** Identical scores (both 27/28 holdout) — the task is
linear-separable in either encoder's space; the generative architecture,
not the parameters or the data, was the failure. The pivot verdict is
now measurement-backed, not just mechanism-backed.

## tool_router — inconclusive by construction

| System | Acc | Macro-F1 | Floor | Flag |
|---|---|---|---|---|
| ModernBERT | 0.1667 | 0.1786 | 0.0833 | above floor, `insufficient_data` |
| LFM2.5-Encoder | 0.0833 | 0.0260 | 0.0833 | AT floor |

7-way classification with **1–2 shots per class in train** (8 train cases
total). The spec's dataset-preparation milestone (500 held-out prompts,
2026-10-11) never happened; the real-data capture is what exists. This
role needs ≥20/class before it discriminates anything. Logged as a data
gap, not a model gap.

## Latency — the one failing gate

| Encoder | FC p50 | FC p95 | Gate (≤50ms) |
|---|---|---|---|
| ModernBERT-base | — | 176.8 ms | ❌ FAIL |
| LFM2.5-Encoder-350M | — | 398.6 ms | ❌ FAIL |

fp32 single-text forward on CPU, no quantization, no batching, no thread
pinning. The spec's own risk table anticipated exactly this: "ModernBERT
too large → Quantize to INT8/INT4". ModernBERT's 176ms vs LFM's 398ms
(the `causal_conv1d` fallback is the LFM tax) — order-of-magnitude close
after quantization, expected. **Quantized re-measure is the next gate.**
(For reference, the embed-sidecar route already runs the same class of
model at 89 ms/query on E-cores with INT8.)

## Verdict

1. **Pivot validated.** Encoder + linear probe ≥ generative + LoRA by a
   wide margin on the one task with enough data. Proceed with P7.3.
2. **ModernBERT ≈ LFM2.5-Encoder on quality** (identical scores); LFM
   pays 2.2× latency until quantized. No basis yet to prefer either —
   the tie is one task deep.
3. **Next in spec order:** INT8/INT4 quantization + latency re-measure
   (gate), then LoRA on the encoders, then privacy_sentinel (token
   classification) and mempalace_extractor (span extraction) which the
   current probe harness does not yet cover.
4. **tool_router dataset gap** carried into the open-items list.
