# LFM25 SMS Phase 2 — Echo Instrumentation, Contract Decomposition, Latency (2026-10-08)

**Author**: researcher_humboldt · **Date**: 2026-10-08 · **Status**: measured
**Supersedes**: nothing. **Continues**: `LFM25_SMS_REAL_DATASET_20261008.md`
**Blueprint**: `docs/research/P7_SMS_GAUNTLET_BLUEPRINT_20261008.md`
**Model**: `lfm25-350m-q6k` (Ollama, CPU-only Node 1) · **Datasets**: `sms_real_v1`
(holdout), `sms_derived_flat_v1` (derived), `sms_real_v2` (scaled + probe gold)

Labels: `[Measured]` = from the runs cited. `[Proposal]` = a design decision.
`[Open question]` = needs operator direction.

---

## 0. Headline

1. **The echo metric is now permanent.** Every aggregate carries
   `distinct_output_ratio`, `modal_output_share`, `copy_suspect_n` and
   `copy_suspect`. Phase-1's headline number turned out to be below the trivial
   floor: few-shot `well_curator` exact-match **0.852** versus **0.898** for a
   constant predictor that emits the model's own modal output, against a
   majority-gold `action_exact` floor of **0.972**. The exemplars made it
   *worse* than a fixed string. [Measured]
2. **The paraphrase probe verdict is: echo, proven by invariance — not by
   collapse.** Accuracy did not collapse under paraphrase (Δ **+0.034**, inside
   the ±0.10 noise floor), which on the naive rule reads as "robust inference".
   It is not: only **3 of 20** answers changed when the input was rewritten, the
   modal output is byte-identical across arms, and modal_output_share is 0.95 /
   0.90. The probe is *uninformative* as a discriminator on a near-constant
   model; the echo metrics settle it. [Measured]
3. **Decomposition LOSES its own verdict rule on all four pairs.** The flat
   contracts cut output 4–13× and reach 100% conformance, but every one of them
   lands **at or below the majority-gold floor**, and the two that "beat" their
   parent collapsed into echo (`copy_suspect` TRUE, 34/36 identical answers).
   Wins: **none**. [Measured]
4. **Latency: neither `num_predict` nor `num_thread` is the lever.** 256 vs 512
   moves extractor mean tokens 245.6 → 239.8 and mean latency 12.18 s → 11.37 s
   (−6.7%) while conformance collapses 8.3% → 0.0% because 6/12 outputs get cut
   mid-object. `num_thread` 6 → 8 is a 0.1% latency change. The token count is a
   property of the **contract**, and that is exactly what decomposition fixes.
   [Measured]
5. **Scaled roles are below their trivial floors, with more data.** `tool_router`
   at 66 holdout rows: `tool_exact` **0.136** vs a majority floor of **0.242**.
   `failure_classifier` now has real `parse_failure` / `latency_spike` gold (18
   holdout rows, 4 classes) and scores **0.056** vs a floor of **0.444**.
   Conformance ≠ capability, now with a bigger sample. [Measured]
6. **Do not LoRA anything yet.** Not one role clears the gate, and two are worse
   than a constant predictor. See §8. [Proposal]

---

## 1. What changed in the harness

| change | where | why |
|---|---|---|
| echo metrics in every aggregate + `report.md` | `scripts/sms/scoring/echo.py`, `gauntlet.py::aggregate`, `write_report` | phase 1's 0.767 hid a copy; the metric must be unmissable |
| `--num-predict` | `gauntlet.py` | the extractor's 260–324 tokens needed to be a sweepable knob |
| `--num-thread` | `gauntlet.py` | isolates thread count from output size |
| `--inject-failure {none,auto,truncate,malformed_json,timeout,schema_violation}` | `gauntlet.py` | produces the failure classes the runner could not produce by itself |
| per-metric means (`per_metric_mean`) | `aggregate` | `tags_f1`, `wing_exact` etc. readable without re-scoring `results.jsonl` |
| 4 flat roles + schemas | `scripts/sms/decomposition/` | the decomposition hypothesis |
| derived gold (no new labelling) | `decomposition/build_derived.py` | matched comparison |
| paraphrase probe | `scripts/sms/paraphrase_probe.py` | echo vs inference, offline and reproducible |
| phase-2 capture (router scale + probe gold) | `scripts/sms/capture_phase2_dataset.py` | open questions 1 and 2 |
| comparison with prior baselines | `decomposition/compare.py` | the verdict rule in code |
| 34 offline unit tests | `tests/test_sms_gauntlet.py` | pins every number above |

### 1.1 The echo metric

Per `(model, role)` group, over normalized raw outputs (whitespace collapsed,
case-folded, punctuation stripped, JSON re-serialized key-sorted):

```
distinct_output_ratio = distinct normalized outputs / n
modal_output_share    = count of the single most common normalized output / n
copy_suspect_n        = that count
copy_suspect          = distinct_output_ratio < 0.35 AND n >= 8
```

`n >= 8` exists because at n=4 a ratio is noise: `privacy_sentinel` and
`pii_action` both show `modal_output_share = 1.0` at n=4 and are deliberately
**not** flagged. The ratio still reports, so the reader can see it.

### 1.2 Phase-2 echo measurements, every role

`lfm25-350m-q6k`, few-shot 2, `num_predict` 512.

| role | n | distinct_output_ratio | modal_output_share | copy_suspect_n | copy_suspect | schema% | exact/F1 |
|---|---:|---:|---:|---:|:--:|---:|---:|
| `well_curator` (complex) | 36 | **0.083** | **0.944** | 34 | **YES** | 94.4 | 0.852 |
| `mempalace_extractor` (complex) | 36 | 0.917 | 0.111 | 4 | no | 2.8 | 0.000 |
| `privacy_sentinel` (complex) | 4 | 1.000 | 0.250 | 1 | no (n<8) | 75.0 | 0.000 |
| `tool_router` (v2, 66 rows) | 66 | 0.500 | 0.470 | 31 | no | 93.9 | 0.136 |
| `failure_classifier` (v2, 4 classes) | 18 | 0.611 | 0.278 | 5 | no | 94.4 | 0.056 |
| `place_classifier` (flat) | 36 | **0.056** | **0.944** | 34 | **YES** | 100.0 | 0.222 |
| `quote_extractor` (flat) | 36 | **0.333** | 0.389 | 14 | **YES** | 2.8 | 0.001 |
| `pii_action` (flat) | 4 | 0.250 | **1.000** | 4 | no (n<8) | 100.0 | 0.250 |
| `supersede_decider` (flat) | 36 | **0.139** | **0.889** | 32 | **YES** | 100.0 | 0.903 |

Five of nine groups trip the alarm, and — the point of §4 — so do both flat
contracts that "won" their comparison. `well_curator`'s modal output, 34/36
times, is the exemplar's answer verbatim:

```json
{"kind": "correction", "domain": "harness",
 "tags": ["coordination", "federation", "gates", "context", "handoff"],
 "action": "keep", "superseded_by": null, "rationale": "current record; ..."}
```

### 1.3 Zero-shot is the control that matters

Same 20 cases, same model, `--few-shot 0`:

| arm | schema% | exact | distinct_output_ratio | modal_output_share | copy_suspect | p50 s |
|---|---:|---:|---:|---:|:--:|---:|
| zero-shot | 0.0 | 0.000 | **1.000** | 0.050 | no | 2.46 |
| few-shot verbatim | 95.0 | 0.817 | 0.100 | 0.950 | **YES** | 5.22 |
| few-shot paraphrase | 100.0 | 0.783 | 0.150 | 0.900 | **YES** | 5.83 |

Zero-shot gives 20 distinct answers for 20 records and is 0% conformant. Two
exemplars take it to 95% conformant and 19 identical answers. **The exemplars
are the cause of the collapse** — they buy the output format and sell the
content. [Measured]

---

## 2. Paraphrase probe — the verdict, stated plainly

`scripts/sms/paraphrase_probe.py`, `runs/sms_paraphrase_350m_20261008`.
Deterministic, offline, no LLM in the loop: template rewrites of the four prose
fields, a 36-entry meaning-preserving synonym table, clause reordering and
surface changes. The record id, every chain id and every timestamp are
preserved verbatim — those are the tokens the gold action depends on. Gold is
**byte-identical** in both arms by construction; a rewrite that could change the
label is dropped rather than guessed (0 of 20 dropped, so the guard never fired).

| variant | n | schema% | exact_match | tags_f1 | distinct_ratio | modal_share | copy_suspect |
|---|---:|---:|---:|---:|---:|---:|:--:|
| verbatim | 20 | 95.0 | 0.817 | 0.013 | 0.100 | 0.950 | YES |
| paraphrase | 20 | 100.0 | 0.783 | 0.013 | 0.150 | 0.900 | YES |

- Δ exact_match = **+0.034** (inside the ±0.10 noise floor for n=20)
- Δ modal_output_share = **+0.050** (went *up* under paraphrase)
- `output_changed_rate` = **0.15** — only **3 of 20** answers moved when the input was rewritten
- modal output byte-identical across arms: **YES**

### 2.1 Interpretation — the rule as specified, applied

> *if paraphrase accuracy collapses relative to verbatim while
> `modal_output_share` stays high, that is conclusive proof of exemplar echo*

**Accuracy did not collapse.** On the rule as written, this probe does not
return a verdict. It would be dishonest to stop there, because the rule has a
blind spot that phase 2 walked straight into: **accuracy can be invariant to
paraphrase because the output does not depend on the input at all.** With 19 of
20 answers identical, rewriting the record cannot change the score — not because
the model understood the paraphrase, but because it never read the wording in
the first place. 3/20 changed.

So the honest verdict is a third case the binary rule does not have:

> **ECHO — proven by invariance, not by collapse.** The probe is *uninformative*
> as a discriminator on a near-constant model, and the echo metrics settle the
> question against inference: `tags_f1` is 0.013 in both arms (the one field
> that genuinely requires inference from the record text is not inferred at
> all), and the modal answer's `tags` are the exemplar's five tags.

This is recorded in `paraphrase_probe.py::_verdict` in code, including the
noise floor and the `HIGH_MODAL_SHARE` gate, so a future run cannot quietly
upgrade "accuracy held" into "the model infers". [Measured + Proposal]

---

## 3. Contract decomposition — hypothesis and result

**Hypothesis**: for a 350M model, a chain of flat single-purpose contracts beats
one complex nested contract, even though it costs more inference calls.

Four flat roles, each `additionalProperties: false`, ≤2 scalar keys, no arrays,
no nesting, no provenance object:

| flat role | splits off from | output |
|---|---|---|
| `place_classifier` | `mempalace_extractor` placement | `{wing, room}` |
| `quote_extractor` | `mempalace_extractor` first item | `{content, source_quote}` |
| `pii_action` | `privacy_sentinel` decision (detection is upstream) | `{action}` |
| `supersede_decider` | `well_curator` supersession reasoning | `{action, superseded_by}` |

Gold is derived, never re-labelled (`decomposition/build_derived.py`):
`~/WanderGround/datasets/sms/derived/` — 126 holdout / 203 train rows, 0 dropped,
manifest with per-role sha256. Two filters are load-bearing and both are
counted in the manifest: a quote whose gold `source_quote` is not a substring of
its own window is dropped (unscoreable label), and `merge`/`drop` are excluded
from `supersede_decider` because the split contract does not own them (0 dropped
here — the holdout's curator gold is `keep`/`supersede` only).

### 3.1 Matched comparison

`runs/sms_p2_baseline_20261008` vs `runs/sms_p2_flat_20261008`, same model, same
exemplars, same `num_predict`, matched cases only. Reproduce with
`decomposition/compare.py`; table below is its output.

| pair | primary metric | complex | flat | Δ | schema% c→f | tok c→f | p95 s c→f | flat distinct_ratio | copy_suspect | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|---|
| extractor → `place_classifier` | `wing_exact` | 0.000 | 0.444 | **+0.444** | 2.8 → **100.0** | 240.9 → **18.2** | 14.68 → **5.33** | 0.056 | **YES** | PRIOR-DOMINATED |
| extractor → `quote_extractor` | `provenance_preserved` / `quote_grounded` | 0.014 | 0.028 | +0.014 | 2.8 → 2.8 | 240.9 → **50.2** | 14.68 → **8.14** | 0.333 | **YES** | PRIOR-DOMINATED |
| `privacy_sentinel` → `pii_action` | `action_exact` | 0.000 | 0.250 | +0.250 | 75.0 → **100.0** | 63.0 → **8.0** | 3.97 → **3.38** | 0.250 | no (n=4) | PRIOR-DOMINATED |
| `well_curator` → `supersede_decider` | `action_exact` | 0.917 | 0.917 | 0.000 | 94.4 → **100.0** | 67.6 → **17.9** | 6.93 → **2.46** | 0.139 | **YES** | NO WIN |

### 3.2 The prior check — why "beat the parent" is not a win

`compare.py` scores two constant predictors with the role's own scorer, so
"prior-dominated" is computed, not asserted:

| flat role | flat primary | flat modal_prior_acc | majority_gold_acc | reading |
|---|---:|---:|---:|---|
| `place_classifier` | 0.444 | 0.389 | **0.472** | at/below the floor |
| `quote_extractor` | 0.028 | 0.000 | **0.028** | at the floor |
| `pii_action` | 0.250 | 0.250 | **0.500** | **below** the floor |
| `supersede_decider` | 0.917 | 0.889 | **0.940** | below the floor |

Modal outputs, with counts:

- `place_classifier`: `{"wing": "game_research", "room": "toolchain-state"}` × **34/36**
  — gold `wing` is `game_research` in 17/36 and gold `room` is `toolchain-state`
  in 1/36. The `+0.444` is the majority wing prior and nothing else; `room_exact`
  is **0.000**.
- `supersede_decider`: `{"action": "keep", "superseded_by": null}` × **32/36**.
  Gold is `keep` in 35/36. The one non-prior answer picked
  `530a5621-…` as `superseded_by` — the **same-pack older distractor**, i.e. it
  violated the forward-pointing rule, the exact failure mode the split was
  supposed to fix.
- `pii_action`: `{"action": "drop"}` × **4/4** — it found the *rarest* gold label
  (1 of 4) and scored 0.250, half of what always answering `redact` would give.
- `quote_extractor`: 35/36 outputs fail its own schema with
  `'source_quote' is a required property`. Flattening the contract did not help
  the model copy an exact substring; it just stopped it from emitting the key.

### 3.3 Verdict — stated without softening

> **Decomposition wins only if the flat contract beats the complex one on the
> primary metric AND does not collapse into echo.**

**Wins: none.** Three pairs beat the parent on the primary metric and all three
are prior-dominated — two trip `copy_suspect`, and the third (n=4) sits at
`modal_output_share = 1.0` with a below-floor score. The fourth did not beat the
parent at all.

What decomposition *did* deliver, reported as trade-offs and never counted as
accuracy:

- **Output size**: 4–13× fewer tokens (240.9 → 18.2; 67.6 → 17.9; 63.0 → 8.0).
- **Latency**: `supersede_decider` p95 **2.46 s** — the only group in the entire
  phase within reach of the 2 s gate. `place_classifier` 14.68 → 5.33 s.
- **Conformance**: 100% on three of four flat roles.
- **A hard ceiling removed**: the complex extractor's 241 tokens is a property of
  the contract; a two-key contract cannot generate 241 tokens. This is the
  finding that matters for §4.

### 3.4 What this says about contract design

The hypothesis was wrong about *accuracy* and right about *cost shape*. The flat
contracts do remove the runaway generation, but they do not make a 350M model
read its input — the same modal-output collapse is present at 2 keys as at 6.
Contract complexity is not what makes the model echo; **exemplar presence is**
(§1.3). The decomposition is worth keeping for latency and for making the
failure legible, not as an accuracy lever.

---

## 4. Latency remediation

The blueprint's p95 ≤ 2 s gate: missed by every role in phase 1, p95 17.1 s for
the extractor. Two cheap candidates were tested; **neither works**.

### 4.1 `num_predict` 256 vs 512

`--few-shot 2`, 12 cases per role, `runs/sms_np{256,512}_20261008`.

| arm | role | n | schema% | exact | mean tok | tok at cap | p50 s | p95 s |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 256 | `mempalace_extractor` | 12 | **0.0** | 0.000 | 239.8 | **6/12** | 12.74 | 13.54 |
| 512 | `mempalace_extractor` | 12 | 8.3 | 0.000 | 245.6 | 0/12 | 12.80 | 14.68 |
| 256 | `well_curator` | 12 | 91.7 | 0.694 | 68.8 | 0/12 | 6.27 | 8.09 |
| 512 | `well_curator` | 12 | 91.7 | 0.667 | 68.9 | 0/12 | 6.18 | 8.18 |

Dropping the cap to 256 buys 6.7% mean latency (12.18 → 11.37 s) and costs
**100% of the remaining conformance** (8.3% → 0.0%): half the outputs are now cut
mid-object. `well_curator` emits 68–69 tokens and never approaches either cap, so
the cap is irrelevant to it. **Verdict: keep 512.** A cap that truncates a
nested answer buys nothing and breaks the JSON.

### 4.2 `num_thread` 6 vs 8

Ollama is running on CPUs 0–11 with `OLLAMA_NUM_THREADS` unset, so the per-request
`num_thread` is the only thread control. Isolated at concurrency 1 to remove
oversubscription from the comparison (`runs/sms_ex_t{6,8}_c1_20261008`,
`mempalace_extractor`, n=10):

| threads | mean tok | mean s | ms/token | p95 s |
|---:|---:|---:|---:|---:|
| 6 | 253.4 | 6.78 | 26.8 | 8.46 |
| 8 | 267.7 | 6.79 | 25.4 | 8.87 |

At concurrency 2: 12.90 s (t8) vs 12.80 s (t6). **A 0.1% change — no lever.**

### 4.3 What latency actually is

Measured cost is ~26 ms/token at concurrency 1 and ~48 ms/token at concurrency 2
for the extractor; `well_curator` at 68 tokens / 5.7 s is the same ratio. So:

- **p95 ≤ 2 s at this model on CPU ≈ 55–75 output tokens.** That is the whole
  budget.
- The extractor's 241 tokens are what make it slow, and the token count is set
  by the **contract**, not by the generation cap and not by thread count.
- Decomposition brings the curator's supersession decision to **17.9 tokens /
  p95 2.46 s** — the only path to the gate measured in phase 2, and it arrives
  with an echo-collapsed score (§3.2), which is the honest trade.

**Recommendation**: keep `num_predict = 512` and `num_thread = 6` as defaults;
do not chase latency with generation knobs. `supersede_decider` is the only
contract that fits the 2 s gate, and it needs an anti-echo fix (below) before
any of it is usable. [Proposal]

---

## 5. Open question 1 — `tool_router` scaled to 88 rows

`scripts/sms/capture_phase2_dataset.py` derives **68 new cases** from rules
already written in this repo, each citing the document section it came from:
`AGENTS.md` (§Session recall, §Hard rules, §Core Rules),
`docs/AGENT_RUNBOOK.md` (§3.6, §3.7, §5, §4),
`docs/TROUBLESHOOTING.md` (§2, §4, §8, §9),
`docs/PRIVACY_SECURITY.md` (§3, §5, §6, §7, §9),
`docs/HARDWARE.md`, `docs/ROADMAP.md`. The 20 v1 rows are carried over with gold
unchanged so one dataset path is the whole corpus. Split by `source_group` at
0.75 holdout (the train side exists only to supply 2 exemplars), repaired so
every gold tool appears on both sides — 0 repairs needed.

| | count |
|---|---:|
| total rows | **88** (20 carried + 68 new) |
| train / holdout | 22 / **66** |
| holdout gold tools | ochist_grep 9 · ocdb_ro 9 · mempalace_search 13 · mempalace_kg_query 6 · well_add 6 · web_search 7 · **none 16** |
| hard negatives → `none` | 23 total: 6 out-of-scope, 7 privileged/destructive/ambiguous (tier-3 shell, federated publish, `DROP TABLE`, force-push, key rotation, …), 1 empty, 1 escalation-gated |
| injection attempts → `none` | 6 tagged `injection` (fenced `\|im_start\|` prefix, "ignore previous instructions", a forged `SYSTEM:` debug-mode block, an allowlist-disregard, a secret-write request, and a remote-peer privilege escalation) |

Measured, `runs/sms_p2_scaled_{fs,zs}_20261008`:

| arm | n | schema% | `tool_exact` | `fallback_exact` | `abstention_ok` | `args_f1` | distinct_ratio | modal_share | copy_suspect | p50 s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:--:|---:|
| few-shot 2 | 66 | **93.9** | **0.136** | 0.773 | 0.712 | 0.045 | 0.500 | 0.470 | no | 2.32 |
| zero-shot | 66 | 47.0 | 0.091 | 0.348 | 0.273 | 0.015 | 0.303 | 0.470 | **YES** | 1.41 |

**The number that matters**: majority-gold floor for `tool_exact` on this
holdout is **0.242** (always answer `none`). The few-shot model scores **0.136** —
*worse than a constant predictor*, on 5.5× the phase-1 sample. Phase 1's
`tool_exact = 0.000` was underpowered enough to look like "no discrimination
yet"; with 66 rows it is discrimination below chance.

Few-shot does help what it always helped: the output **shape** (47.0% → 93.9%
conformance) and abstention discipline (0.273 → 0.712). Discrimination among
tools remains absent, and `args_f1` 0.045 says it is not reproducing argument
keys either.

## 6. Open question 2 — `failure_classifier` given real classes

`gauntlet.py --inject-failure auto` rotates five perturbations deterministically
over real outputs, and the runner labels each trace with **its own**
`failure_class_for()`:

| injection | mechanism | class |
|---|---|---|
| `none` | untouched model output | `ok` / whatever the model actually did |
| `truncate` | cut mid-object | `parse_failure` |
| `malformed_json` | JSON-shaped prose `json.loads` rejects (4 fixed samples) | `parse_failure` |
| `timeout` | **a real client-side HTTP timeout** (urlopen timeout 0.05 s) | `latency_spike` |
| `schema_violation` | drop a required key | `schema_violation` |

No human labels these; the gold *is* the runner's verdict, so no class is
asserted that the runner did not classify. The timeout probe is a genuine
timeout, not a simulation. Probe run `runs/sms_inject_probe_20261008` (52 traces
over 5 roles) → 52 gold rows: `parse_failure` 21 · `schema_violation` 17 ·
`latency_spike` 10 · `ok` 4; train 34 / holdout 18.

Measured, holdout n=18:

| arm | schema% | `class_exact` | distinct_ratio | modal_share | copy_suspect | p50 s |
|---|---:|---:|---:|---:|:--:|---:|
| few-shot 2 | 94.4 | **0.056** | 0.611 | 0.278 | no | 2.83 |
| zero-shot | 83.3 | 0.000 | 0.833 | 0.167 | no | 1.36 |

Majority-gold floor: **0.444** (always `parse_failure`). Model: **0.056**.
Phase 1's "100% conformance / 0.000 accuracy" was measured on a degenerate
2-class distribution; with 4 real classes the answer is the same and now
statistically meaningful. Note this group is **not** echo-collapsed
(distinct_ratio 0.611) — it varies its answer and is still wrong, which is a
different and more tractable failure than copying.

---

## 7. Artifacts

| Artifact | Location |
|---|---|
| Echo metric | `scripts/sms/scoring/echo.py` |
| Injection modes | `scripts/sms/gauntlet.py` (`--inject-failure`, `--injected-timeout-s`) |
| Flat contracts | `scripts/sms/decomposition/{roles.py,schemas/}` |
| Derived gold | `scripts/sms/decomposition/build_derived.py` → `~/WanderGround/datasets/sms/derived/` |
| Comparison + verdict rule | `scripts/sms/decomposition/compare.py` |
| Paraphrase probe | `scripts/sms/paraphrase_probe.py` → `runs/sms_paraphrase_350m_20261008/` |
| Phase-2 capture | `scripts/sms/capture_phase2_dataset.py` → `~/WanderGround/datasets/sms/v2/` |
| Unit tests | `tests/test_sms_gauntlet.py` (34 tests, offline) |
| Runs | `runs/sms_p2_baseline_20261008` · `runs/sms_p2_flat_20261008` · `runs/sms_p2_scaled_{fs,zs}_20261008` · `runs/sms_np{256,512}_20261008` · `runs/sms_ex_t{6,8}_c1_20261008` · `runs/sms_inject_probe_20261008` · `runs/sms_paraphrase_350m_20261008` |

---

## 8. Updated go/no-go per role

Blueprint §3.2 gates: validity ≥95%, conformance ≥95%, router tool-exact ≥0.85,
curator acc ≥0.80, privacy action-acc ≥0.90, supersession 100%, provenance ≥95%;
plus the phase-1 addition of a **trivial-prior floor** the model must beat.

| role | n | schema% | primary | prior floor | echo? | verdict |
|---|---:|---:|---:|---:|:--:|---|
| `well_curator` | 36 | 94.4 | exact 0.852 (modal-constant **0.898**, floor 0.972) | **below** | **YES** | **NO-GO** — below a constant string |
| `mempalace_extractor` | 36 | 2.8 | F1 0.000, provenance 0.014 | at | no | **NO-GO** — furthest |
| `privacy_sentinel` | 4 | 75.0 | action 0.000 | — | no (n=4) | **NO-GO** — underpowered by construction |
| `tool_router` | 66 | 93.9 | tool_exact 0.136 | **0.242** | no | **NO-GO** — below chance |
| `failure_classifier` | 18 | 94.4 | class_exact 0.056 | **0.444** | no | **NO-GO** — conformance ≠ capability |
| `place_classifier` | 36 | 100.0 | wing 0.444 | 0.472 | **YES** | **NO-GO** — prior-dominated |
| `quote_extractor` | 36 | 2.8 | grounded 0.028 | 0.028 | **YES** | **NO-GO** — cannot copy a substring |
| `pii_action` | 4 | 100.0 | action 0.250 | 0.500 | no (n=4) | **NO-GO** — below floor, n=4 |
| `supersede_decider` | 36 | 100.0 | action 0.917 | 0.940 | **YES** | **NO-GO** — meets the p95 gate, fails accuracy |

Two roles changed status *downward* since phase 1, and that is the headline:
`well_curator` looked like the one candidate and is in fact below a constant
predictor; `tool_router` moved from "structurally learnable" to "below chance"
once n went from 12 to 66.

### 8.1 Should we LoRA anything yet?

**No. Nothing.** And the phase-1 basis for "maybe" has been removed rather than
strengthened.

The blueprint gate is "beat the prompt-only baseline by ≥10 pts on the primary
metric or reject training". Three things now block every role:

1. **There is no prompt-only baseline worth beating.** The current few-shot
   numbers sit at or below what a constant predictor achieves. You cannot
   measure a training gain against a baseline that a `dict` would match.
2. **Exemplar echo is the dominant effect and it has not been controlled for.**
   `well_curator` 0.083 distinct-output ratio at n=36; `place_classifier` 0.056.
   Training on labels a model scores by echoing a prior teaches the prior.
3. **The echo metric is only one week old.** It shipped in this phase. The
   prerequisite for any training decision — a harness that cannot be fooled by
   a copy — did not exist before today.

### 8.2 What phase 3 should measure, in order

1. **Exemplar diversification**: N=4 exemplars chosen to span kinds, domains,
   tags and both actions, and re-measure `distinct_output_ratio`. The target is
   a role with `copy_suspect = false` **and** accuracy above the floor. If
   diversification cannot lift `distinct_output_ratio` above 0.35 for
   `well_curator`, no prompt-only variant of that role is worth training.
2. **Balance the curator gold.** 35/36 `keep` means `action_exact` cannot exceed
   ~0.97 by luck, and cannot distinguish a trained model from a constant one.
   Adversarial pairs (one `supersede` against one same-pack-older distractor) are
   the only informative gold for this role.
3. **Only then**: `failure_classifier` is the best LoRA candidate in principle —
   it is *not* echo-collapsed (distinct 0.611), its labels are deterministic
   from a runner, and its input is a short structured trace rather than prose.
   Its blocker is 18 holdout rows against a 0.444 floor, not capability.
4. **`quote_extractor` needs a different technology, not a smaller model.** 35/36
   fail to emit the key at all. Copying an exact substring from a 900-char
   window is an extraction task, not a generation task — try a span-scoring
   formulation or an encoder, not a JSON contract.

---

## 9. Open questions for the operator

1. `supersede_decider` is the only contract that fits the p95 ≤ 2 s gate
   (17.9 tokens, p95 2.46 s, 100% conformance). Do we keep it as a latency
   demonstration with the echo caveat recorded, or drop it until an
   anti-exemplar variant clears the prior floor?
2. The router split now leans 0.75 holdout because the train side only supplies
   2 exemplars. Is that acceptable, or should `tool_router` move to
   leave-one-out exemplar selection and free the whole corpus for evaluation?
3. The injection machinery (`--inject-failure`) can perturb any role's outputs.
   Should it be restricted to a probe-only flag name to keep it out of ordinary
   evaluation runs, or is a loud `--inject-failure` in the report sufficient?
4. `pii_action` n=4 and `privacy_sentinel` n=4 remain the weakest measurements in
   the suite. Scaling the sentinel corpus requires constructing real-looking PII
   cases; do we accept synthetic dummies at scale, or defer both roles again?

---

*Filed 2026-10-08 by researcher_humboldt. No fine-tuning was performed; this phase
is measurement only. Raw gold stays outside git under `~/WanderGround/datasets/`;
`gnosis/well/well.jsonl` was not modified. The redaction gate was not weakened:
derived sets inherit v1's sentinel scan, and `quote_extractor` reuses the
extractor's own `source_quote_grounded` rule unchanged.*