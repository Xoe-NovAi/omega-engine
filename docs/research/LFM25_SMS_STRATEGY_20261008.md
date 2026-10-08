# Omega Engine v1.6.1-alpha — Small Model Specialist Strategy

**Status**: strategy record (2026-10-08)
**Owner**: Node 1
**Scope**: P7 — Local Specialist Small-Model Modules

## The hidden power

Omega Engine was always meant to be a strictly local, CPU-only, neuro-optimized stack. What was missing was the recognition that **tiny, fine-tuned specialists** — not one big model — are the natural organ system of such a stack.

The strategy is now:

> Use LFM2.5-class sub-1B models as a fleet of single-turn, schema-constrained, locally trained reflexes that make the whole engine faster, cheaper, and more private.

This is the hidden power. The engine becomes a nervous system, not just a brain.

## Why 350M, not 230M

The 230M model is demoted to an ablation / latency-control baseline. It remains useful for cheap sanity checks and control experiments, but it is not the default specialist.

The 350M model is the primary SMS model because:

- nearly the same compute cost;
- materially stronger at the two things we care about most: **tool calling** and **structured extraction**;
- published evidence shows fine-tuned 350M can hit 96–98% tool-call equivalence on narrow tasks;
- our own gauntlet already shows 350M at 100% schema conformance on `failure_classifier` and `privacy_sentinel`.

## The role that matters most

The highest-value single use of LFM2.5-350M in Omega Engine is:

> A fine-tuned, local, single-turn tool-call executor that reliably turns intent into validated JSON for the entire Omega stack — MemPalace, The Well, gnosis-lock, omega-hub, and privacy routing.

It is not a chatbot. It is not an oracle. It is a reflex layer.

## Role matrix

| Slot | Use 350M? | Notes |
|---|---|---|
| `omega-hub-dispatcher` | yes | top priority |
| `tool-router` | yes | schema-constrained |
| `failure-classifier` | yes | our gauntlet: 100% schema conformance |
| `well-curator` | yes | strict supersession schema |
| `mempalace-extractor` | yes, hardest | schema fidelity is the bottleneck |
| `empress-lens` | yes, single-turn only | question generation, not dialogue |
| `entity-voice` | careful | 350M can lose the thread in multi-turn conversation |
| `privacy-sentinel` | use the encoder instead | `LFM2.5-Encoder-350M-PII-Detector` is the right tool for PII |
| math / code / creative writing | no | Liquid explicitly says not recommended |
| open-ended chat | no | use 1.2B or larger |

## The bottleneck is schema fidelity, not intelligence

Independent structured-output testing (IFStruct) puts base LFM2.5-350M at only ~22.6% on generic schema tasks; a small GRPO run lifted JSON conformance by ~14 points.

That means the model already has the capability — it lacks shape discipline. Fine-tuning on our own schemas is the fix.

## Training recipe

Copy the Distil Labs / TRL pipeline:

1. Define the exact tool/JSON schema.
2. Generate 20–100 seed examples per specialist.
3. Have a strong teacher produce validated traces.
4. Filter and validate.
5. LoRA fine-tune the 350M.
6. Export to GGUF and load into Ollama.
7. Re-run through the gauntlet.

LoRA targets for LFM2.5:

- `q_proj`, `k_proj`, `v_proj`, `out_proj`, `in_proj`, `w1`, `w2`, `w3`
- rank 16, alpha 32, dropout 0.05
- lr ~2e-4 to 5e-4
- batch 4, grad accum 2
- 1–3 epochs (Distil Labs saw most gain in epoch 1; resolve empirically)

## Quantization

Our current file is Q6_K, which is the right default at this size.

- Q4_K_M — 229MB
- Q5_K_M — 260MB
- Q6_K — 293MB
- Q8_0 — 379MB
- BF16 — 712MB

A/B Q4_K_M vs Q6_K in the gauntlet, but default to Q6_K for quality.

## Immediate next moves

1. Demote 230M to ablation-only.
2. Make 350M the primary SMS model.
3. Build a 350M-only gauntlet variant for the top four roles.
4. Run an encoder A/B for privacy/PII (encoder, not generative).
5. Generate distillation traces from gnosis-lock and MemPalace data.
6. LoRA the 350M on our schemas.
7. Re-run the gauntlet; promote only if it beats the prompt-only baseline by ≥10 points.

## Related records

- `docs/research/LFM25_SPECIALIST_MODULES_HUMBOLDT_20261008.md` — deep research brief
- `docs/research/P7_SMS_GAUNTLET_BLUEPRINT_20261008.md` — gauntlet blueprint
- `docs/research/LFM25_SMS_GAUNTLET_SMOKE_20261008.md` — first gauntlet run
- `docs/research/LFM25_SMS_E0_RESULTS_20261008.md` — first smoke results
- `docs/ROADMAP.md` — P7 — Local Specialist Small-Model Modules