<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# LFM25 SMS Phase 3 — SFT Negative Result Analysis (2026-10-10)

**Author**: researcher_humboldt · **Record date**: 2026-10-10 · **Verification pass**: 2026-10-11
**Status**: analysis + recommendation. No training or inference was run. Nothing committed.
**Subject**: LoRA-SFT of `LiquidAI/LFM2.5-350M` on `failure_classifier` (34/18) and
`place_classifier` (84/36), 1 epoch, r=16/α=32, lr 2e-4, bs 4 × accum 2, CPU fp32.
**Continues**: `LFM25_SMS_PHASE2_ECHO_DECOMPOSITION_20261008.md`,
`LFM25_SMS_REAL_DATASET_20261008.md`, `LFM25_SMS_STRATEGY_20261008.md`.

Labels used throughout:
`[M]` = **measured**, recomputed from on-disk artifacts in this pass.
`[I]` = **inference**, reasoned from measured facts plus cited code/records.
`[X]` = **external**, from a cited public source.

---

## 0. Headline

**The negative result is real and it is not one result. It is two different
failures wearing the same coat, and they need opposite treatments.**

1. **`failure_classifier` failed for a fixable reason.** The task is *provably
   learnable*: a 4-line keyword rule over the input reproduces **18/18 = 1.000**
   of the holdout gold `[M]`. The model reached 0.111 after SFT `[M]`. There is
   no label noise blocking this, no label-space gap, no unseen classes. This is
   pure under-fitting — the model was handed **5 optimizer steps** `[M]`.
2. **`place_classifier` failed because the task is not learnable as
   constructed.** A classifier restricted to emitting only labels that appear in
   its own training set has a joint-exact **ceiling of 2/36 = 0.056** — which is
   *exactly the constant-predictor floor* `[M]`. The measured 0.000 is one row
   from the theoretical maximum. This experiment **cannot distinguish "SFT
   failed" from "the task is impossible"**, and no amount of extra training will
   move it.
3. **Breaking the collapse was never evidence of capability.** `distinct_output_ratio`
   0.056 → 1.000 means the model's *output entropy* rose. It did not mean the
   output became a function of the input. §3 gives the mechanism.
4. **The most likely proximate cause is the loss mask.** Only **14.06%**
   (`failure_classifier`) and **5.82%** (`place_classifier`) of supervised tokens
   are the assistant answer `[M]`. If the rest carried loss, the run was mostly a
   copy-the-input exercise — and the model's out-of-enum outputs are literally the
   `role=` token from the input line `[M]`. §4.

---

## 1. Measured facts

### 1.1 What the two runs actually did

| | failure_classifier | place_classifier |
|---|---:|---:|
| train rows / holdout rows `[M]` | 34 / 18 | 84 / 36 |
| distinct train inputs `[M]` | 34/34 | 84/84 |
| train ∩ holdout input overlap `[M]` | 0 | 0 |
| mean input chars `[M]` | 379 | 898 (train) / 936 (holdout) |
| **optimizer steps @ bs4 × accum2, 1 epoch** `[M]` | **5** | **11** |
| total seq tokens in train set `[M]` | 8,852 | 27,226 |
| assistant-target tokens `[M]` | 1,245 | 1,585 |
| **assistant fraction of supervised tokens** `[M]` | **0.1406** | **0.0582** |
| trainable params `[M]` | 5,996,544 (1.66%) | 5,996,544 (1.66%) |
| mean train loss (`runs/*/train_log.json`) `[M]` | 2.546 | 1.788 |
| loss at first log / final, as reported by operator | 4.707 | 5.416 → 3.415 |
| final `mean_token_accuracy` as reported | 0.378 | 0.417 |
| wall time `[M]` | 61.8 s | 196.9 s |
| LoRA tensors in adapter `[M]` | 184 | 184 |
| layers receiving LoRA `[M]` | 0–15 (all) | 0–15 (all) |
| merge parity fp32 `[M]` | PASS (max_abs_diff 1.11e-4, argmax_agreement 1.0) | PASS (1.04e-4, 1.0) |

Note the two loss figures disagree (`train_log.json` mean 2.546/1.788 vs the
operator-quoted first-log 4.707 / 5.416→3.415). Both are recorded; they are
different statistics (mean over the epoch vs the first and last logged window).
Nothing in this analysis depends on which is which. `[M]`

### 1.2 Predicted label distribution after SFT `[M]`

From `sms-training/sft_eval_{role}.jsonl`.

**failure_classifier** (n=18):

| predicted `class` | n | in 8-value enum? |
|---|---:|:--:|
| `hallucinated_entity` | 3 | yes |
| `ok` | 3 | yes |
| `fallback` | 3 | **no** |
| `latency_spike` | 2 | yes |
| `abstained` | 2 | yes |
| `<invalid JSON>` | 2 | — |
| `parse_failure` | 1 | yes |
| `failure_classifier` | 1 | **no** |
| `mempalace_extractor` | 1 | **no** |

Gold: `parse_failure` 8 · `latency_spike` 5 · `schema_violation` 4 · `ok` 1.
**`schema_violation` was never predicted once, on any of the 4 rows whose gold it
is** — and those are exactly the 4 rows whose input contains a `schema_error=`
field `[M]`.

The three out-of-enum values are `fallback`, `failure_classifier`,
`mempalace_extractor`. Those are **the `role=` field of the input's first line**
(`role=tool_router …`, `role=failure_classifier …`, `role=mempalace_extractor …`)
`[M]`. The model is copying a token out of the prompt and putting it in the
label slot. That is not a decoding artifact; it is what you get when the training
objective rewarded reproducing the prompt.

**place_classifier** (n=36):

| | value |
|---|---:|
| JSON valid | 1.000 |
| joint (wing+room) exact | **0.000** |
| wing exact | 0.0556 |
| room exact | 0.000 |
| distinct outputs | 36/36 |

Predicted `wing` modal values: `main` ×5, `game` ×3, then 30 singletons including
`Kubrow/Kavat Imprints`, `worktree`, `appimage-mangohud`, `gaming-expert`,
`wing_linguistics`. The holdout input for the `Kubrow/Kavat Imprints` prediction
begins with that exact phrase as a Warframe trading doc header `[M]`. The model is
**naming the content it was shown** and putting the name in the label slot.

---

## 2. Label overlap, quantified

### 2.1 failure_classifier — overlap is perfect; insufficiency is not the story `[M]`

| | train (n=34) | holdout (n=18) |
|---|---|---|
| `parse_failure` | 13 (0.382) | 8 (0.444) |
| `schema_violation` | 13 (0.382) | 4 (0.222) |
| `latency_spike` | 5 (0.147) | 5 (0.278) |
| `ok` | 3 (0.088) | 1 (0.056) |
| distinct classes | 4 | 4 |
| majority-class floor | 0.382 | 0.444 |

- class overlap train ∩ holdout: **4/4**. Train-only: **none**. Holdout-only: **none**. `[M]`
- schema enum in the prompt lists **8** classes; only **4** occur. Four declared
  labels (`truncation`, `wrong_tool`, `hallucinated_entity`, `abstained`) have zero
  examples — two of them (`hallucinated_entity`, `abstained`) are nonetheless the
  model's top-2 predictions `[M]`. The model is guessing in the empty part of the
  label space.

**Determinism check** — a 4-line rule over the raw input:

```python
if   "timeout"                        in u: return "latency_spike"
elif "truncated" or "malformed"       in u: return "parse_failure"
elif "schema_error"                   in u: return "schema_violation"
else:                                       return "ok"
```

→ **18/18 = 1.000 on holdout, zero misses** `[M]`. Keyword presence in holdout
inputs: `timeout` 5 (gold `latency_spike` 5), `truncated` 5 + `malformed` 3 (gold
`parse_failure` 8), `schema_error` 4 (gold `schema_violation` 4). The mapping is a
perfect partition of the holdout set `[M]`.

**Conclusion**: label cardinality, label noise (with one exception, §2.3), and
unseen-class risk are all **ruled out** for this role. The task is a 4-way
lexical-keyword classification. It is the easiest thing in the whole suite.

### 2.2 place_classifier — the label space is broken `[M]`

| | train (n=84) | holdout (n=36) |
|---|---|---|
| distinct `wing` values | 11 | 11 |
| distinct `room` values | **73** | **31** |
| distinct `(wing, room)` pairs | 80 | 35 |

| overlap metric | value |
|---|---:|
| `wing` distinct shared | 9 / 11 → **holdout wing coverage 0.818** |
| holdout `wing` values unseen in train | 2 (`inbox`, `wing_space-bunny-free`) |
| **`room` distinct shared** | **7 / 31 → holdout room coverage 0.226** |
| holdout `room` values unseen in train | **24 / 31 (77.4%)** |
| **`(wing, room)` pairs shared** | **2 / 35 → 0.057** |

Holdout rooms never seen in training (24): `alice-2011-state`,
`alice-2011-vorpalfix`, `alice-compatibility`, `benchmark-results`,
`card_correspondences`, `charter`, `general`, `grimoire`, `hudframe-tool`,
`input-hardware`, `model-identity`, `node0_transfer`, `ps-t-ub-exe-patch`,
`safety-incidents`, `sqlite-vec`, `taste-profile-corrections`,
`toolchain-defects`, `verification`, `vnr-trust-order`, `vnr-verified`,
`wad_integration`, `warframe`, `warframe-final-config`, `working-doctrine`.

**The ceiling calculation.** Suppose a perfect oracle classifier that may only
ever emit labels present in its training set:

| metric | holdout n=36 | rate |
|---|---:|---:|
| room-exact ceiling | 10 | 0.278 |
| wing-exact ceiling | 34 | 0.944 |
| both-fields ceiling | 9 | 0.250 |
| **joint-exact ceiling** | **2** | **0.056** |

Constant-predictor floors on the same holdout: wing `game_research` = 0.472,
room `diary` = 0.111, joint (`game_research`,`warframe`) = **0.056** `[M]`.

> **The joint-exact ceiling equals the joint-exact floor, at 0.056.**
> Measured joint-exact is 0.000. The gap between "best possible" and "measured"
> is **one row out of 36**.

**The prompt contains no enum.** The system message for `place_classifier` is
`"Keys: wing (string), room (string)."` — no allowed values `[M]`. The output
space is open-vocabulary over a 73-value train taxonomy the model has never been
told about. The model is being asked to *invent* taxonomy labels, then scored on
exact string match.

**The `wing` labels are not curated.** Train spelling frequencies `[M]`:

| label | n | | label | n |
|---|---:|---|---|---:|
| `game_research` | 41 | | `wing_tarot` | 3 |
| `wing_researcher_humboldt` | 15 | | `omega-engine-alpha` | 3 |
| `wing_lilith` | 9 | | `lilith` | 2 |
| `wing_humboldt` | 4 | | `wanderground` | 2 |
| `wing_game_research` | 3 | | `wing_muse-spark` / `wing_linguistics` | 1 / 1 |

`lilith` and `wing_lilith` coexist. `game_research` and `wing_game_research`
coexist. `wing_humboldt` and `wing_researcher_humboldt` are the same entity under
two labels, and `omega-engine-alpha` and `wanderground` are the same entity under
a third naming convention. These are raw MemPalace directory names passed through
without normalisation. A classification function is not a function when the same
concept has three names.

**Label is not present in input.** The gold `room` string appears literally in
its own input in only **12/84 train (0.143)** and **3/36 holdout (0.083)** `[M]`;
gold `wing` in 3/36. So the mapping is genuinely semantic (topic → taxonomy slot),
which is fine, but it means the model must both recognise the topic and recall
the taxonomy — two capabilities, 84 examples, no enum.

### 2.3 A real label defect in failure_classifier's gold `[M]`

The `evidence` field is a runner-derived template string. Mapping class →
evidence string in the **training** set:

| class | evidence strings observed (n) |
|---|---|
| `schema_violation` | `"…on a unperturbed artifact"` (5), `"…on a schema-broken artifact"` (8) |
| `ok` | `"…on a unperturbed artifact"` (3) |
| `parse_failure` | `"…on a truncated artifact"` (6), `"…on a malformed-json artifact"` (7) |
| `latency_spike` | `"…on a timed-out artifact"` (5) |

**`schema_violation` and `ok` share the identical target string `"…on a
unperturbed artifact"` under two different class labels.** 8 of 34 training rows
(23.5%) contain a target whose text is a verbatim duplicate of another row's
target under a contradictory label. Whatever string a model emits, the loss
pushes toward that string; the class field cannot be inferred from the evidence
field for those 8 rows. `"unperturbed"` is also simply the wrong descriptor for
a schema violation — the runner's `failure_class_for()` assigns the class from
the artifact's nonconformity, and the evidence template was written for the
injection mechanism, not the verdict.

This is a genuine label defect. It is **not** the reason the role scored 0.111
(§2.1 shows the class field alone is perfectly determined by the input), but it
is an irreducible ~24% noise floor on any target that includes `evidence`, and it
should be deleted from the contract.

---

## 3. Why breaking the collapse did not produce capability

This is the central question and it has a precise answer.

### 3.1 `distinct_output_ratio` measures entropy, not conditionality

The metric is `distinct normalized outputs / n`. It says: *how many different
strings did you produce.* It does **not** say: *did your output change when the
input changed.*

Phase 2 already established the discriminator: under paraphrase, only 3 of 20
answers moved, while `modal_output_share` stayed at 0.95 (echo, proven by
invariance). The same logic applies here. Raising output entropy from 0.056 to
1.000 is compatible with:

- (a) the output being a genuine function of the input → real capability, or
- (b) the output being an *unconstrained sample from the label prior* → no
  capability at all.

For `place_classifier` the SFT outputs are literally (b): `Kubrow/Kavat
Imprints`, `main`, `game`, `worktree`, `appimage-mangohud`, `gaming-expert`,
`wing-1`/`room-1` `[M]`. `room-1` / `wing-1` is the signature of a model sampling
from "emit something string-shaped". The distinct ratio went up because the
model stopped emitting one constant. It did not go up because the model learned
anything.

**A conditionality test, not an entropy test, is what the harness needs.** The
paraphrase probe from phase 2 already implements it. It has never been run
against an SFT model. It must be, and the gate is `output_changed_rate ≥ 0.50`
under a meaning-preserving rewrite with the label held constant. Run against the
base model this was the instrument that exposed echo; run against an SFT model it
is the only thing that distinguishes (a) from (b).

### 3.2 The mechanism that raises entropy without adding capability

SFT on 34–84 examples for 5–11 optimizer steps cannot install a mapping. What it
*can* do, and what it demonstrably did, is raise the model's willingness to
continue generating rather than collapse onto the highest-probability
continuation. Base `place_classifier` emitted the modal prior 34/36 times; after
SFT it emitted 36 distinct strings. The SFT shifted probability mass off the
single mode and spread it across the whole plausible-string manifold.

That is exactly what "diverse wrong answers" means. The answers are wrong in a
*new* way rather than an *old* way, and the echo metrics cannot see the
difference because they never measured conditionality.

So the answer to "why did breaking the collapse not produce capability" is:
**they are orthogonal.** The collapse was a decoding-behaviour artifact of
prompt-only inference, removable by any gradient step. Capability is a property of
the learned input→label function, which 5 optimizer steps over a 73-value
open label space cannot create.

### 3.3 `failure_classifier` is the counter-example that proves it

Same recipe, same model, same step budget — but a task with a 4-way closed label
set and a deterministic keyword partition. Base 0.056 → SFT **0.111**: also
"barely moved". So the collapse-breaking produced nothing on either role. The
difference is that on `failure_classifier` the missing thing is *budget and loss
masking* (§4), while on `place_classifier` it is *the task definition itself*
(§2.2). One fix does not address both.

---

## 4. The loss-mask question

`~/WanderGround/sms-training/train_lora.py` is **not** the script that produced
these runs. Three independent mismatches `[M]`:

| | `train_lora.py` on disk | `runs/*/train_log.json` |
|---|---|---|
| train path | `sms-training/roles/{ROLE}_train.jsonl` | `datasets/sms/v2/…` and `datasets/sms/derived/…` |
| `completion_only_loss` | not set (defaults `None`) | `true` |
| `formatting_func` | present | would have been rejected (see below) |
| reported losses | — | 2.546 / 1.788 |

**The harness script that actually ran is not on disk.** That is a provenance
failure independent of everything else and it is Gate 0 of §9.

### 4.1 What TRL 1.14.2 does with `completion_only_loss=True` on a `messages` dataset

From the installed source (`trl/trainer/sft_trainer.py`, venv
`~/WanderGround/.venv-sms-train`, trl 1.14.2) `[M]`:

- `sft_trainer.py:1215-1218` — `completion_only_loss` is taken from the arg.
- `sft_trainer.py:1220-1247` — with `data_collator=None` and a non-vision
  dataset, the collator is `DataCollatorForLanguageModeling`.
- `DataCollatorForLanguageModeling.torch_call` (`:643-653`) routes on the example
  keys: `"messages"` present → `_collate_language_modeling`.
- `_collate_language_modeling` (`:655-691`) ends at:
  ```python
  labels = output["input_ids"].clone()
  labels[output["attention_mask"] == 0] = -100
  ```
  **Only padding is masked.** `self.completion_only_loss` is not read on this
  path — it is consulted only in `_collate_prompt_completion` (`:777`) and in
  the vision collator.
- `_collate_prompt_completion` requires `"prompt"` and `"completion"` keys.
- `sft_trainer.py:1306-1311` — `completion_only_loss=True` **together with a
  `formatting_func` raises `ValueError`**, because a formatter converts the
  dataset to language-modelling type. So a run that logs
  `completion_only_loss: true` cannot have used `formatting_func`.

The on-disk datasets are `{"messages": [...]}` — the language-modelling shape.

### 4.2 The two branches, and why both are bad or undetermined

**Branch A — the harness fed `messages` (the likely case).** Then
`completion_only_loss=True` was recorded but **inert**: the selected collator
masks padding only. Loss was computed over system prompt + user trace +
assistant answer. Given the measured token fractions (§1.1), that means
**85.9%** (`failure_classifier`) and **94.2%** (`place_classifier`) of the
supervised gradient signal was spent learning to reproduce the prompt.

This predicts exactly the observed failure: the model becomes a competent
prompt-reproducer and puts prompt tokens into the label slot. Measured
confirmation: the three out-of-enum `failure_classifier` outputs are the
`role=` field of the input; the `Kubrow/Kavat Imprints` output is the input's
own header `[M]`. **Confidence: high, but not proven** — the decisive artifact
(the mask tensor) was not retained.

**Branch B — the harness built `prompt`/`completion` pairs.** The `parity`
block in `train_log.json` stores a `sample_prompt_tail` ending `…\nassistant\n`
and a `sample_completion`, which is consistent with the harness constructing
prompt/completion itself. If so, masking was correct and the 2.546/1.788 losses
are honest completion-only losses. But then a completion-only loss of **2.55**
and **1.79** on a JSON target with a small closed label set is itself damning: a
model that has learned the output template should be well under 1.0, and one that
has learned the *classes* should be far lower. `[I]`

### 4.3 Either way, `mean_token_accuracy ≈ 0.38–0.42` is not interpretable

If Branch A holds, the metric is dominated by trivially-predictable prompt tokens
(most of the input is a raw JSON blob the model can partly copy), so 0.378 is
consistent with near-total failure on the answer. If Branch B holds, 0.378 means
the model fits roughly a third of answer tokens — also a failure. The number
cannot distinguish "good fit diluted" from "no fit". **Report completion-only
token accuracy, on the assistant span only, from now on.**

### 4.4 The fix is available and was not used

The LFM2.5 chat template **does** carry `{% generation %}` markers `[M]`
(`src/LFM2.5-350M/chat_template.jinja`). TRL's `assistant_only_loss=True` requires
exactly that (`sft_config.py:102-105`, `sft_trainer.py:1265-1267` checks for the
markers and injects them if absent). So the correct, supported, one-line
configuration was available and unused. Note also that
`assistant_only_loss` and `completion_only_loss` are *different* options: the
former is the conversational-dataset one; only the latter is inert on `messages`.

---

## 5. Do the loss numbers make sense?

**Measured**: mean train loss 2.546 / 1.788 (run log), first-log 4.707 / 5.416
→ 3.415 (operator), `mean_token_accuracy` 0.378 / 0.417.

**Reference points:**

- Under Branch A (full-sequence), a mean loss of 1.8–2.5 is roughly what a model
  achieves by learning the input *format* and never getting to the answer, because
  the answer is 6–14% of the tokens. The number is uninformative about capability.
- Under Branch B (completion-only), 2.5 on a JSON object with a 4-value enum is a
  **failed** run. A healthy 350M LoRA at this scale should reach well under 1.0
  on epoch 1 and under 0.5 by epoch 3 on a 4-class task `[I]`.
- `train_samples_per_second` 0.551 / 0.427 `[M]` on this CPU. At bs 4 × accum 2
  that is ~5 and ~11 optimizer steps in 62 s / 197 s. This is the binding fact,
  not the loss value.

**What the numbers imply** `[I]`: the run is consistent with a model that learned
the *shape* of the answer and nothing about its *content*. Under Branch A it is
additionally consistent with a model that spent its budget copying the input.

**The healthy comparison** is not published for this exact task, so the honest
internal control is the next-experiment memorisation gate in §9: if a 350M LoRA
cannot reach >0.95 train-set exact-match on 34 rows it has an optimisation or
objective bug, full stop — and that test costs 3 minutes of CPU.

---

## 6. Published evidence: what sub-1B SFT success actually requires

### 6.1 The 96–98% number, traced to source

The strategy doc (`LFM25_SMS_STRATEGY_20261008.md` §"Why 350M") cites
"published evidence shows fine-tuned 350M can hit 96–98% tool-call equivalence on
narrow tasks". The source is Distil Labs `[X]`:

> "After fine-tuning with distil labs, it reaches 96-98% tool call equivalence
> across three benchmarks… **Teacher model: GPT-OSS-120B**… For the shell command
> task, we generated **5,000 synthetic training examples** from seed data using
> the full distil labs pipeline… LFM2.5-350M was trained independently from
> scratch on each dataset."

| task | base LFM2.5-350M | tuned | dataset |
|---|---:|---:|---|
| shell command (Gorilla) | 61.4% | **98.0%** | 5,000 synthetic from 20–100 seeds |
| smart home | 63.2% | **96.7%** | existing domain dataset |
| banking voice | 34.5% | **95.9%** | existing domain dataset |

Conditions, stated plainly:

1. **Distillation, not gold-only.** The teacher was GPT-OSS-120B. Our pipeline
   has no teacher.
2. **~5,000 examples, not 34.** That is ~150× our `failure_classifier` set and
   ~60× `place_classifier`.
3. **Closed-book, closed-schema tool calling.** A fixed function catalogue, a
   binary exact-match metric ("tool call equivalence"). This is structurally
   identical to a *well-posed* `failure_classifier`, and structurally
   **unrelated** to `place_classifier`'s open taxonomy.
4. **The base model already had most of the capability.** 34.5–63.2% untuned,
   versus our 0.056. Distil fine-tuned a model that was already half-right; we
   tried to install the whole function from scratch. Their "most of the gain
   arrives in a single epoch" claim is about a model starting at 61%.
5. Distil's own documented limits, directly on point: "**Anything you haven't
   trained it on.** This is a specialist. Fine-tuning on a shell command schema
   doesn't transfer to your CRM's schema." and "**Large function catalogues with
   noisy input**" was the one task where tuning fell short of the teacher.

### 6.2 The LFM2.5-350M LoRA recipe we copied is confirmed correct

Hugging Face's own GRPO/IFStruct recipe for `LFM2.5-350M` `[X]`:

```python
LoraConfig(r=16, lora_alpha=32, bias="none", task_type="CAUSAL_LM",
           target_modules=["q_proj","k_proj","v_proj","out_proj","in_proj","w1","w2","w3"])
```

> "This trains **~6M parameters, about 1.66% of the model**."

Measured: **5,996,544 / 360,480,512 = 1.664%** `[M]`. Our LoRA config is
byte-identical to Liquid's published recipe. **The layer targeting is not the
problem.** (§8.)

Same recipe, 500 samples, 100 GRPO steps, lr 5e-5 → IFStruct **22.6% → 29.7%**
(JSON subset 18.0% → 31.9%) `[X]`. Note the magnitude: even the vendor's own
targeted fine-tune of this model on *generic schema following* moved it by 7
points, not to saturation.

### 6.3 Vendor baselines for structured output

From the `LFM2.5-350M` card `[X]`: IFEval 76.96 · IFBench 40.69 · Multi-IF 44.92 ·
IFStruct 21.1 base, **44.9 after RL**. Vendor guidance: "We recommend fine-tuning
LFM2.5 for your specific use case"; recommended decoding `temperature 0.1,
top_k 50, repetition_penalty 1.05`; and explicitly *"not recommended for
knowledge-intensive tasks and programming."*

### 6.4 Consolidated table

| source | model | method | data | teacher | base score | final | epochs/steps |
|---|---|---|---|---|---:|---:|---|
| Distil Labs `[X]` | LFM2.5-350M | distillation SFT | ~5,000 synthetic | GPT-OSS-120B | 61.4% | 98.0% | "most gain in epoch 1" on 5k |
| Distil Labs `[X]` | LFM2.5-350M | distillation SFT | domain dataset | GPT-OSS-120B | 63.2% | 96.7% | not published |
| Distil Labs `[X]` | LFM2.5-350M | distillation SFT | domain dataset | GPT-OSS-120B | 34.5% | 95.9% | not published |
| HF / TRL GRPO `[X]` | LFM2.5-350M | GRPO (LoRA r=16) | 500 samples | n/a (reward) | 22.6% IFStruct | 29.7% | 100 steps |
| Liquid IFStruct `[X]` | LFM2.5-350M | RL | held-out split | n/a (reward) | 21.1% | 44.9% | not published |
| **Ours, failure_classifier** `[M]` | LFM2.5-350M | LoRA r=16 | **34** | **none** | **0.056** | **0.111** | **5 steps** |
| **Ours, place_classifier** `[M]` | LFM2.5-350M | LoRA r=16 | **84** | **none** | **0.222** | **0.000** | **11 steps** |

Every published success has (a) a ≥34.5% starting point, (b) a closed schema, and
(c) either ≥500 examples or 100+ steps. Ours has none of the three.

---

## 7. The encoder alternative

`LiquidAI/LFM2.5-Encoder-350M` `[X]`:

- Bidirectional masked-LM encoder on the same LFM2 hybrid backbone. Same 65,536
  vocab, hidden 1024, 8,192 context. **Requires `trust_remote_code=True`**
  (`auto_map` wired to `Lfm2BidirectionalForMaskedLM`) — unlike the causal model,
  which is native in transformers 5.19.
- **17-task classification benchmark (full supervised fine-tune, avg over 5 fresh
  seeds): 81.02 ±1.00**, rank **4 of 14**, ahead of `mDeBERTa-v3` (280M, 80.37),
  `XLM-R base` (280M, 77.46), `EuroBERT-210M` (76.87) — and within 0.66 of
  `ModernBERT-large` (395M, 81.68).
- **Documented fine-tuning recipe**: "follows standard BERT-style fine-tuning.
  Attach a task head to the encoder body and train end-to-end." lr **1e-5–5e-5**,
  warmup ratio 0.1, weight decay 0.1, **3–20 epochs** with early stopping
  (patience 3), bf16 autocast with fp32 master weights.
- `LiquidAI/LFM2.5-Encoder-350M-PII-Detector` `[X]` ships ready: a **full**
  fine-tune with a token-classification head covering **40 PII types across 16
  languages**, CPU-only HF Space demo.

**Is it the right tool?**

- `failure_classifier`: **yes, unambiguously.** 4-way sequence classification
  with a closed label set is exactly what the encoder card names first among
  recommended uses ("intent/routing, moderation"). We would fine-tune a 350M
  encoder end-to-end at lr 1e-5–5e-5 for 3–20 epochs — a far better-conditioned
  problem than LoRA-SFT of a generative model against a JSON grammar, and the
  output cannot be out-of-schema because there is no generation step.
- `tool_router`: yes, same reasoning, and the encoder card's own zero-shot
  *prompt-routing* demo is the same shape as our router.
- `privacy_sentinel`: **do not train at all.** Adopt the shipped PII-Detector.
  Our 15 synthetic dummies are not worth a training run against a model already
  fine-tuned on 40 PII types in 16 languages.
- `place_classifier`: the encoder does not fix a broken label space. A 117-way
  flat scorer over the palace taxonomy is *possible* (that is literally the
  retrieval/reranking use case), but the taxonomy must first be canonicalised.
- `mempalace_extractor` / `quote_extractor`: token classification / span
  extraction — the right family, and it matches the phase-2 verdict that
  "copying an exact substring is an extraction task, not a generation task".

**Constraints to record**: `trust_remote_code=True` required; 8,192-token context
(our windows are ~300 tokens, so irrelevant); 3–20 epochs on CPU is far more
wall-clock than a 5-step LoRA but the encoder is a single forward pass at
inference — no autoregressive decode, so the p95 ≤ 50 ms gate in
`ENCODER_SPECIALIST_EVAL_20261009.md` §5 is genuinely plausible.

**Note**: `ENCODER_SPECIALIST_EVAL_20261009.md` §1 already reached the right
conclusion ("autoregressive models at ≤350M cannot perform extraction/classification
via few-shot or LoRA") and scheduled the encoder A/B for 2026-10-10…16. That
milestone is still the right next move. What this analysis adds is that
`place_classifier` must be dropped or re-specified before it enters that A/B —
it would consume the schedule and return an uninterpretable null.

---

## 8. LFM2-specific fine-tuning footguns — audit result

| # | suspected footgun | verdict | evidence |
|---|---|---|---|
| 1 | `causal_conv1d_fn` falling back to a slow reference path | **not a correctness bug** | transformers implements `causal_conv1d_fn` in pure PyTorch (`models/lfm2/modeling_lfm2.py:295`); the hub-kernel map for `causal_conv1d_fn` is registered **cuda-only**, so on CPU the local reference path always runs. It is differentiable and correct. It is slow — that is the 0.43–0.55 samples/s, not a correctness issue. |
| 2 | Layer targeting wrong for the hybrid | **no bug** | Adapter inspection: **184 tensors**, LoRA on **all 16 layers**. Conv layers `[0,1,3,4,6,7,9,11,13,15]` receive `conv.in_proj` + `conv.out_proj` + `feed_forward.w1/w2/w3`; attention layers `[2,5,8,10,12,14]` receive `self_attn.q/k/v/out_proj` + `feed_forward.w1/w2/w3`. `out_proj` correctly matches **both** the conv and the attention module (32 tensors = 16 modules × 2). Trainable 5,996,544 = 1.66%, matching Liquid's published recipe exactly. |
| 3 | LoRA on a hybrid conv model trains the wrong submodules | **no** | See #2. `in_proj` is the conv projection and it is adapted. |
| 4 | `lm_head` / embeddings not adapted | correct by design — task is a generation task |
| 5 | **Merge → GGUF → Ollama path unverified** | **REAL GAP** | `parity.json` only checks fp32-HF-merged vs fp32-HF-peft on a **64-token** probe (max_abs_diff ~1e-4, argmax_agreement 1.0). It does **not** check GGUF. The Q6_K/Q4_K_M models are in Ollama (`sms-failure_classifier-350m-q6k` etc.) and were never scored. |
| 6 | **`eval_sft.py` is not the serving harness** | **REAL GAP** | See §8.1. |
| 7 | `prepare_model_for_kbit_training` applied to an fp32 model | harmless here — already fp32; it does enable gradient checkpointing and fp32 norm upcasting |
| 8 | The venv is currently broken | **REAL GAP** | `import trl` fails in `~/WanderGround/.venv-sms-train` today: transformers → `hub_kernels` → `is_kernels_available()` → `import triton` → `ModuleNotFoundError: No module named 'triton'`. The runs completed before this; any follow-up agent starting from a clean shell will hit it immediately. `[M]` |
| 9 | `PARAMETER stop ""` in the Ollama Modelfiles | suspicious — an empty stop string; worth removing before serving `[M]` |

### 8.1 Ollama-vs-transformers (question 7)

Measured, from source:

- **Gauntlet (production path)**: `scripts/sms/gauntlet.py:146` posts
  **`"format": "json"`**, `:149` sets **`"temperature": 0.1`**, plus
  `num_thread 6`, `num_predict 512`.
- **SFT eval path**: `sms-training/eval_sft.py::generate` calls
  `model.generate(..., do_sample=False)` — **pure greedy, no `format` constraint**,
  transformers 5.19 + PEFT, no GGUF, no merge.

Two independent deviations:

1. **No JSON grammar constraint.** Ollama's `format:"json"` compiles a GBNF
   grammar that constrains the decode. Without it, malformed output is possible —
   and indeed 2/18 `failure_classifier` outputs were invalid JSON `[M]`, a failure
   mode the production path would have suppressed mechanically. **The reported
   0.889 conformance is pessimistic relative to what Ollama would deliver.**
2. **Greedy vs temperature 0.1.** Liquid's own recommended decode is
   `temperature 0.1, top_k 50, repetition_penalty 1.05` `[X]`. Greedy removes the
   `top_k 50` truncation. For a model that has learned a closed enum, greedy is
   *probably* fine and arguably better; for `place_classifier`'s open label space
   it removes the sampling that produced the (wrong) diversity. Direction of the
   effect is unknown without measuring.

**The gap is not the explanation** — a grammar constraint cannot create the
input→label mapping. But **the SFT models have never been evaluated in the
harness that will serve them**, and 0.889 vs 100% conformance is exactly the kind
of difference that gets misread as capability. Every future number must come from
`scripts/sms/gauntlet.py` against the merged GGUF loaded in Ollama. Cost: ~1 hour.

---

## 9. Ranked recommendation

Effort estimates assume a competent follow-up agent on Node 1 with the existing
venv (after fixing the triton import, §8 item 8).

### R0 — Recover the training script and prove the loss mask · **DO THIS FIRST**

| | |
|---|---|
| **Effort** | 1 h |
| **Payoff** | Removes the single largest unknown in §4. Every other recommendation's cost/benefit is conditional on it. |
| **Evidence** | `train_lora.py` provably did not produce these runs (§4). `completion_only_loss` is provably inert on a `messages` dataset in trl 1.14.2 (§4.1, cited lines). The 14.06% / 5.82% token fractions `[M]` and the input-token-copying outputs `[M]` are exactly the signature the mask hypothesis predicts. |

Action: locate or rewrite the harness; add an assertion that fails the run if
`labels != -100` for any prompt token; dump the realised label mask for row 0
into `train_log.json` permanently. Also fix the venv triton import and remove the
empty `PARAMETER stop ""`.

### R1 — Fix the objective and spend the budget · **highest payoff per hour**

| | |
|---|---|
| **Effort** | 2–4 h |
| **Payoff** | Turns an uninterpretable result into an interpretable one. This is the difference between "350M is too small" and "we trained it for 5 steps". |
| **Evidence** | 5 and 11 optimizer steps `[M]`. 14.06% / 5.82% target-token fraction `[M]`. LFM2.5's own chat template has `{% generation %}` markers so `assistant_only_loss=True` is supported `[M]`. Distil Labs reached 98.0% on 5,000 examples; HF's GRPO used 500 samples and 100 steps — both are 1–2 orders of magnitude more optimisation than we spent. |

Concrete: `assistant_only_loss=True`; `epochs = 10` (`failure_classifier` ≈ 50
steps, `place_classifier` ≈ 105); `max_length = 512` (inputs are ~300 tokens —
this alone cuts CPU time ~2×); keep r=16/α=32 (validated); keep `max_length`
truncation **above** the longest measured input (max 1369 chars ≈ 350 tokens for
`failure_classifier`, 1565 chars ≈ 400 for `place_classifier` — 512 is safe).

**Decisive cheap control, built in**: after training, score the **train set**.
Gates in §10. If train exact-match < 0.95, the problem is optimisation and
nothing else should be attempted yet.

### R2 — Rebuild `failure_classifier` as a closed-contract task and scale it

| | |
|---|---|
| **Effort** | 1 day |
| **Payoff** | Highest *reachable* accuracy in the suite. The measured ceiling is 1.000. |
| **Evidence** | The keyword rule is **18/18 = 1.000** on holdout `[M]` — the labels are a perfect partition. Class overlap 4/4, no unseen classes `[M]`. The runner already emits these labels deterministically and for free (`--inject-failure`, phase-2 §6), so scaling costs only compute. |

Actions:
1. **Delete the `evidence` field.** It is 8/34 rows (23.5%) label-contradictory
   (§2.3) and it is not in the acceptance metric. Contract becomes
   `{"class": <one of 8 enum values>}`.
2. Scale to **≥1,500 train rows** by running `--inject-failure {none,truncate,malformed_json,timeout,schema_violation}` across all 5 roles × ≥60 seeds each. Labels come from the runner, not from a human.
3. Balance the 4 classes to within ±5 points. Currently train is 38/38/15/9.
4. Add adversarial cases where the *same* role string appears with a different perturbation, so `role=` copying cannot be a winning shortcut.

### R3 — Switch classification roles to `LFM2.5-Encoder-350M`

| | |
|---|---|
| **Effort** | 1 day (model pull + head + 3–20 epoch CPU fine-tune) |
| **Payoff** | Removes JSON-grammar and decode failure modes entirely for `failure_classifier` and `tool_router`; ships `privacy_sentinel` for free via the PII-Detector. |
| **Evidence** | Encoder card: 81.02 ±1.00 mean over 17 tasks, rank 4/14, "standard BERT-style fine-tuning", lr 1e-5–5e-5, 3–20 epochs `[X]`. PII-Detector is a full fine-tune with a token-classification head over 40 types/16 languages `[X]`. Our failure mode is out-of-schema *values* — impossible without a generation step. |

Adopt `ENCODER_SPECIALIST_EVAL_20261009.md`'s protocol. Two corrections to it:
its LoRA recipe (§4.2: `q/v/k/o_proj`, lr 2e-4, 3 epochs) is **encoder-inappropriate** —
`LFM2.5-Encoder-350M` is exposed as `Lfm2BidirectionalModel` and the card
prescribes full end-to-end fine-tuning with a task head, not LoRA on attention
projections. And `o_proj` is not the LFM naming (`out_proj`).

### R4 — Drop or re-specify `place_classifier`

| | |
|---|---|
| **Effort** | 4 h to decide; 2 days to re-specify if option (a) |
| **Payoff** | Avoids spending the rest of the schedule on a task whose ceiling equals its floor. |
| **Evidence** | Joint-exact ceiling **2/36 = 0.056** = constant-predictor floor 0.056 `[M]`. Room coverage 7/31 = 0.226 `[M]`. Uncurated wing spellings — `lilith`/`wing_lilith`, `game_research`/`wing_game_research`, `wing_humboldt`/`wing_researcher_humboldt` `[M]`. |

Two legitimate options, and only two:
- **(a) Closed taxonomy.** Canonicalise wings to a fixed set (≤12). Collapse
  rooms to a curated set of ≤15. **Put the enum in the system prompt.** Target
  ≥0.80 joint exact against a rebuilt floor. Cost: re-label 120 rows + re-score.
- **(b) Encoder as a flat scorer.** One `Lfm2BidirectionalModel` + a
  `(n_wings × n_rooms)` head, scored over the canonicalised taxonomy. This is the
  card's retrieval/reranking use case and it sidesteps generation entirely.

**Do not run another generative LoRA on `place_classifier` as currently
constructed.** It cannot return a result that means anything.

### R5 — Distillation from a local teacher

| | |
|---|---|
| **Effort** | 1–2 days |
| **Payoff** | **Low for our two tested roles. Moderate for `tool_router` and `well_curator`.** |
| **Evidence** | Distil Labs reached 96–98% with a **120B teacher and ~5,000 examples** `[X]`. We have neither. But their own limit list — "large function catalogues with noisy input" was the one task that fell short — is exactly our `place_classifier` shape, so distillation does not rescue it either. |

Node 1 teacher candidates (all resident, verified via `ollama list`) `[M]`:

| model | size | role |
|---|---:|---|
| `lfm25-8b-a1b` | 5.4 GB | **primary** — same LFM2.5 family, closest output distribution to the student |
| `phi4-mini` | 2.5 GB | cheap second opinion; strongest small general model resident |
| `lfm2-1.2b-extract` | 843 MB | extraction-shaped second opinion |
| `qwen2.5-coder:7b` / `gemma-3-12b` | 4.7 / 5.7 GB | cross-family **validators** (agreement-gate, not teachers) |

Trace format: **JSON-only assistant turns matching the role's schema exactly**,
one line, no prose, no markdown fences, no leading "Here is". Use
`"format": "json"` on the teacher call so the trace is schema-valid by
construction. Keep only traces that (a) parse, (b) validate against the role
schema, and (c) whose field values fall inside the declared enum. Reject
traces containing the case's gold-derived `source_quote` verbatim for the
extraction roles — that reintroduces the echo the whole programme exists to
eliminate.

Distillation's honest role here is **generating volume and adversarial coverage**
for `tool_router` (7 tools, 20–100 seeds → thousands of rows, per Distil's
documented path), **not** producing oracle labels for `failure_classifier`,
whose labels are already deterministic and free.

### R6 — Different base model (control only)

| | |
|---|---|
| **Effort** | 4 h |
| **Payoff** | Diagnostic, not shipping. |
| **Evidence** | `LFM2.5-350M` at IFStruct 21.1 / IFBench 40.69 `[X]` is weak but not degenerate, and the encoder sibling does 81.02 on classification `[X]` — the weakness is the *generative* interface, not the backbone. `qwen3-0.8b-quick` (528 MB) is already resident `[M]`. |

Run `failure_classifier` on Qwen3-0.6B under the *identical* R1 config. If it
also lands near 0.11, the problem is our data and objective (which is what §4
already says). If it lands high, LFM2.5's generative interface is the constraint.
One run, one answer, and it closes the question the current suite cannot close.
Do not go past 1B on this CPU — `phi4-mini` at 2.5 GB already benchmarks at
14.4 t/s on this machine.

---

## 10. Next-experiment spec — executable without re-deriving anything

**Name**: `sms_sft_e1` · **Gate 0**: R0 complete (script recovered, mask asserted,
venv importable).

### E1 — the falsification run (do this before anything else)

**Question**: is `failure_classifier`'s failure optimisation or data?

| | |
|---|---|
| base | `LiquidAI/LFM2.5-350M` @ `9e6c6ccf47cd318696e137d381a7ded8fe4df09f` |
| data | `roles/failure_classifier_train.jsonl`, **unchanged**, 34 rows |
| loss | `assistant_only_loss=True` (NOT `completion_only_loss`) |
| LoRA | r=16, α=32, dropout 0.05, targets `[q_proj,k_proj,v_proj,out_proj,in_proj,w1,w2,w3]` (unchanged — validated) |
| | `lr 2e-4`, cosine, warmup_ratio 0.1, bs 4, accum 2, `max_length 512`, fp32 |
| epochs | **10** (≈50 optimizer steps) |
| seed | 42, then 7 (two seeds) |
| eval | `eval_sft.py` **and** `scripts/sms/gauntlet.py` on the merged Q6_K in Ollama |

**Success gates (all required, in order)**

1. **Train-set exact match ≥ 0.95.** 34 rows is memorisable. Failure here ⇒
   optimisation bug; **stop and debug, do not add data.**
2. **Completion-only token accuracy ≥ 0.90** (assistant span only, reported
   explicitly as such).
3. **Holdout `class_exact` ≥ 0.80** (majority floor 0.444; keyword-rule oracle
   1.000; n=18 is underpowered, so also report a 95% Wilson CI).
4. **`distinct_output_ratio` ≥ 0.35** and **`copy_suspect == false`**.
5. **Paraphrase probe `output_changed_rate ≥ 0.50`** (the phase-2 instrument,
   run for the first time against an SFT model — this is the conditionality
   test, and it is the metric that was missing).
6. **Gauntlet conformance ≥ 0.95** on the merged GGUF (already expected from
   `format:"json"`).

**E1 verdict rule**: gates 1–2 pass and gate 3 fails ⇒ data scaling (R2) is the
lever, proceed to E2. Gate 1 fails ⇒ objective bug, return to R0. Gate 5 fails
with gate 4 passing ⇒ you have re-created echo with a different surface; that is
the negative result again, and the role moves to R3.

### E2 — data scale, only if E1 passes gates 1–2

`failure_classifier`: **1,500 train / 500 holdout**, regenerated by
`--inject-failure {none,truncate,malformed_json,timeout,schema_violation}` across
all 5 roles × ≥60 seeds. Contract drops `evidence`. Classes balanced ±5 pts.
Same config as E1, **5 epochs** (≈940 steps). Gates: holdout `class_exact ≥ 0.90`,
macro-F1 ≥ 0.88, plus all of E1's gates 1–2 and 4–6.

### E3 — encoder A/B for classification roles

`LiquidAI/LFM2.5-Encoder-350M` (`trust_remote_code=True`), `Lfm2BidirectionalModel`
body, linear heads, **full end-to-end fine-tune** (not LoRA):
lr 1e-5 (and a 3e-5 arm), warmup_ratio 0.1, weight_decay 0.1, **8 epochs** +
early stopping patience 3, bf16 autocast / fp32 master, bs 16, max_length 512.
Two heads: 4-way `failure_classifier`; 8-way `tool_router`. Adopt
`LFM2.5-Encoder-350M-PII-Detector` as-is for `privacy_sentinel` — no training.
Gates: macro-F1 ≥ 0.85 on the frozen 20% test split; encoder p95 ≤ 50 ms CPU.

### E4 — `place_classifier`, only after taxonomy canonicalisation

Not scheduled. If option (a) in R4 is taken: canonical wings ≤12, rooms ≤15,
enum in the prompt, 120+ rows re-labelled, split by `source_group` with the
constraint that **every room appears on both sides**. Gate: joint exact ≥ 0.80
**against a re-computed floor** — and if the re-computed floor exceeds 0.80, the
role is dropped rather than re-tuned.

### Cross-cutting requirements for every arm

- Eval through `scripts/sms/gauntlet.py` against the merged GGUF in Ollama.
  Greedy transformers numbers are diagnostic only.
- Report `distinct_output_ratio`, `modal_output_share`, `copy_suspect`,
  paraphrase `output_changed_rate`, and the **constant-predictor floor** with
  every headline number. A score below its floor is not a score.
- Report train-set metrics alongside holdout metrics, always.
- Append a `train_log.json` with realised label-mask fraction and per-step loss.
- `make lint`, `make test`, `make docs` green before filing.

---

## 11. Answer to the central question, in one paragraph

Breaking the collapse did not produce capability because **the collapse was a
decoding artifact and capability is a property of a learned conditional, and only
one of the two roles had a learnable conditional to learn.** `place_classifier`
has no learnable conditional — its label space is 94% unseen at the joint level,
its wing labels are uncurated synonyms, its prompt carries no enum, and its
ceiling equals its floor at 0.056, so a score of 0.000 is one row from optimal.
`failure_classifier` does have one (a keyword rule gets 18/18), and it failed for
a mechanical reason: **5 optimizer steps, with only 14% of the supervised tokens
being the answer, and — most likely — no assistant-only loss mask**, which is why
the model learned to reproduce the prompt and then wrote prompt tokens into the
label slot. The `distinct_output_ratio` rise is not a capability signal in either
case: it is the only available measure of output entropy, and the one experiment
that would have separated capability from entropy — the paraphrase probe — was
never run against an SFT model.

---

## 12. Citations

- `[X]` Distil Labs, *Fine-Tuning Liquid's LFM2.5: Accurate Tool Calling at 350M
  Parameters*, 2026-03-30 — <https://www.distillabs.ai/blog/fine-tuning-liquids-lfm25-accurate-tool-calling-at-350m-parameters>
  · companion: <https://www.distillabs.ai/learn/liquid-lfm2-5-350m-tool-calling/> (2026-08-02)
- `[X]` Hugging Face, *Fine-tuning a 350M Model for Better Structured Outputs in
  100 GRPO Steps*, 2026-09-03 — <https://huggingface.co/blog/grpo-with-trl-ifstruct>
  (IFStruct 22.6 → 29.7; the `r=16` LFM2.5 LoRA target-module recipe and its
  "≈6M params, 1.66%" note)
- `[X]` Liquid AI, *IFStruct v1.0*, 2026-06-30 — <https://www.liquid.ai/blog/ifstruct-v1.0>
- `[X]` `LiquidAI/LFM2.5-350M` model card — <https://huggingface.co/LiquidAI/LFM2.5-350M>
  (16 layers: 10 conv + 6 GQA; vocab 65,536; recommended decode
  `temperature 0.1 / top_k 50 / repetition_penalty 1.05`; IFEval 76.96,
  IFBench 40.69, Multi-IF 44.92; IFStruct 21.1 → 44.9 with RL)
- `[X]` `LiquidAI/LFM2.5-Encoder-350M` model card — <https://huggingface.co/LiquidAI/LFM2.5-Encoder-350M>
  (81.02 ±1.00 over 17 tasks, avg@5 seeds; BERT-style fine-tune recipe
  lr 1e-5–5e-5, warmup 0.1, wd 0.1, 3–20 epochs; `trust_remote_code=True`;
  8,192 ctx)
- `[X]` `LiquidAI/LFM2.5-Encoder-350M-PII-Detector` — <https://huggingface.co/LiquidAI/LFM2.5-Encoder-350M-PII-Detector>
  (full fine-tune, token-classification head, 40 PII types / 16 languages)
- `[M]` `huggingface/transformers` `src/transformers/models/lfm2/modeling_lfm2.py`
  (`causal_conv1d_fn` reference implementation, `:295`; `Lfm2ShortConv`, `:318`)
  and `src/transformers/integrations/hub_kernels.py` (`causal_conv1d_fn` kernels
  registered for `cuda`/`xpu` only)
- `[M]` `trl==1.14.2` installed source,
  `~/WanderGround/.venv-sms-train/lib/python3.14/site-packages/trl/trainer/sft_trainer.py`
  (`:643-653`, `:655-691`, `:777`, `:1215-1218`, `:1220-1247`, `:1265-1267`,
  `:1306-1311`) and `sft_config.py` (`:96-105`, `:259-274`)
- `[M]` Local artifacts: `sms-training/runs/*/train_log.json`, `parity.json`,
  `adapter_model.safetensors`, `sft_eval_{failure_classifier,place_classifier}.jsonl`,
  `roles/*.jsonl`, `datasets/sms/{v2,derived}/*.jsonl`, `eval_sft.py`,
  `train_lora.py`, `modelfiles/*`, `src/LFM2.5-350M/{config.json,chat_template.jinja}`;
  `scripts/sms/gauntlet.py:146,149`; `docs/research/ENCODER_SPECIALIST_EVAL_20261009.md`

---

*Filed 2026-10-10 by researcher_humboldt; all measured values recomputed from
on-disk artifacts on 2026-10-11. No training or inference was executed for this
analysis. Raw gold stays outside git under `~/WanderGround/datasets/`. Nothing was
committed. The negative result is reported as measured: `failure_classifier` is
an under-fitting failure that is fixable, and `place_classifier` is a
task-construction failure that is not fixable by training.*