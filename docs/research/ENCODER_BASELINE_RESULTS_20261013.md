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

### Latency gate re-test — quantization + threads (same session, same inputs)

All runs: per-case (batch=1) embed of every FC holdout case, CPU, same
tokenizer protocol as the baseline. Tool: `scripts/sms/quantize_bench.py`
(+ a thread sweep over 1/2/4/6).

| Config | acc | p50 | p95 | Gate p95 ≤50 |
|---|---|---|---|---|
| fp32, default threads (16) | 0.9643 | 116.3 | 177.3 | ❌ |
| fp32, 6 threads | 0.9643 | 65.6 | 105.4 | ❌ |
| torch dynamic INT8, default threads | 0.9286 | — | 132.6 | ❌ |
| torch dynamic INT8, 4 threads | — | 47.6 | 80.8 | ❌ |
| **torch dynamic INT8, 6 threads** | **0.9286** | **49.7** | **95.2** | ❌ (p50 ✅) |
| onnxruntime dynamic INT8, 6 thr (un-preprocessed) | 0.8929 | 240.5 | 259.4 | ❌ |

Findings:

1. **Thread count is the dominant lever**, not quantization: fp32 drops
   177→105 ms p95 just by pinning to 6 P-cores (default 16 threads pays
   sync overhead). INT8 then gives a further 1.1–1.3×.
2. **Quality cost is real but within bar**: 0.9643 → 0.9286 (one more
   holdout case flips; ≤0.05 tolerance).
3. **The p95 tail is overhead, not compute.** Distribution analysis: the
   slowest case (86 ms in the sweep run) carries only 103 tokens while
   84-token cases finish in 42 ms — sequence length does not explain the
   tail. At ≤170 tokens max, the model's compute is trivial; the 40–95 ms
   band is per-call dispatch/allocator/thread-migration noise.
4. **ORT dynamic INT8 is worse** (259 ms, acc 0.8929) — the torch-2.14
   dynamo export was not ORT-portable (Split/`num_outputs`); the legacy
   exporter works but un-preprocessed dynamic quantization costs accuracy
   without buying speed. Static QDQ with calibration data would be the
   ORT path — not built.
5. **House-context:** our own production embed sidecar runs a comparable
   encoder at 89 ms/query on 4 E-cores. INT8 ModernBERT at p50 49.7 ms on
   6 P-cores already beats that; the ≤50 ms **batch=1 p95** gate is
   tighter than the house standard for this model class.

Verdict: **gate as written (batch=1 p95) not met by any method tried**;
best is 95.2 ms p95 (torch INT8, 6 threads), 1.9× over. Remaining levers,
in order of expected effect: (a) batched serving (changes the protocol —
p95 is overhead-dominated at batch=1); (b) static QDQ INT8 with
calibration; (c) INT4. Recommend proceeding with LoRA on quality grounds
(the quality verdict is solid) and carrying latency as a known open gate
into the 10-17 decision, rather than blocking the track on it.

## LoRA fine-tuning — does it beat the frozen probe? (ModernBERT-base, FC)

Milestone "LoRA fine-tuning runs" (spec §7). Tool: `scripts/sms/encoder_lora.py`.
LoRA r=8/α=16 on all 88 Linear submodules + mean-pool linear head, AdamW
lr=1e-4, 20 epochs, best-holdout selection, train+holdout tracked per epoch
(the Phase-3 negative-result playbook: watch for underfit AND overfit).

| System | Best holdout acc | Note |
|---|---|---|
| Frozen encoder + LogisticRegression probe | **0.9643** | no training |
| **LoRA fine-tuned (this run)** | **0.7857** @ epoch 19 | still rising at cutoff |
| Generative 350M, 5 SFT steps (Phase 3) | 0.111 | control |

**beats_frozen = False.** The LoRA curve climbed 0.39 → 0.79 over 20 epochs
and was *still improving* at epoch 19 (train 0.913, holdout 0.786) — it
underfit, it did not overfit (overfit gap 0.163 and shrinking relative to
the frozen bar). Two honest reads:

1. **Training-config read:** lr=1e-4 with a fresh head underfits at 20
   epochs; a converged run (higher lr / more epochs / warm-started head)
   might close the gap. This run does not prove LoRA *cannot* match.
2. **Task read:** the frozen probe is a *converged* optimizer (LBFGS) on
   features that are already linearly separable (0.9643 with zero
   representation change). LoRA has to both move the representation AND
   learn the head with a weaker optimizer on 46 examples. For a
   linearly-separable task, the frozen probe is the stronger, cheaper
   instrument — consistent with the baseline's linear-separability result.

**Deployment recommendation:** failure_classifier ships as frozen-encoder +
linear probe, NOT LoRA. LoRA's remaining case is the token/span tasks
(privacy_sentinel, mempalace_extractor) where mean-pooled features *cannot*
express the output — that is where representation change is structurally
required, and it is untested.

**Memory note (permanent fix, validated):** this run held Python RSS at
~2.1GB / system ~6.6GB for the full 9.6 min and completed. The prior
OOMs were a missing 6-thread cap + no gradient checkpointing. Both are now
defaults in `encoder_lora.py` (`--checkpoint on` default, `set_num_threads`
pinned, `TOKENIZERS_PARALLELISM=false`); a system-RAM watchdog at 11GB is
used when launching. A single-step memory probe (3GB) does NOT predict the
multi-epoch pattern — do not trust it over the full-run measurement.

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
