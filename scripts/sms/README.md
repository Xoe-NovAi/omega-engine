# scripts/sms — Small-model Specialist gauntlet

Real scored evaluation of LFM2.5 ≤350M Ollama models as narrow specialists
(extractor, well-curator, tool-router, privacy-sentinel, failure-classifier).
Blueprint: `docs/research/P7_SMS_GAUNTLET_BLUEPRINT_20261008.md`.

## Layout

- `gauntlet.py` — main runner (argparse flags below)
- `roles.py` — per-role system prompts, prompt builders, scorers
- `schemas/` — versioned JSON Schemas (Draft 2020-12) per role
- `scoring/` — `json_schema.py` (parse + conformance), `span_f1.py`
  (exact/F1 approximations), `provenance.py` (quote grounding),
  `latency.py` (p50/p95), `echo.py` (exemplar-echo metrics)
- `paraphrase_probe.py` — well_curator verbatim-vs-paraphrase probe
- `capture_phase2_dataset.py` — scaled `tool_router` + real failure-probe gold
- `decomposition/` — flat single-purpose contracts, derived gold, comparison
- `datasets/sms_smoke_dataset.jsonl` — synthetic, sanitized smoke set
  (adversarial: injection, empty, malformed, privacy-synthetic, normal)
- `datasets/sms_real_manifest.json` — provenance + hashes for `sms_real_v1`
  (paths scrubbed to `<HOME_PATH>`)
- `datasets/sms_real_preview.jsonl` — 25 redacted sample rows, 5 per role
- `make_smoke_dataset.py` — regenerates the smoke dataset
- `capture_real_dataset.py` — builds the real (redacted) gold set from the Well
  corpus, the MemPalace palace, live gauntlet traces and documented rules

## Real dataset (`sms_real_v1`)

Raw gold never enters git. The capture script writes redacted rows to
`~/WanderGround/datasets/sms/` and only a manifest + preview into the repo:

```bash
python3 scripts/sms/capture_real_dataset.py
```

Every row passes a sentinel scan (`<EMAIL> <IP> <API_KEY> <TOKEN> <HANDOFF_ID>
<HOME_PATH>`) before writing; a row that still trips the scanner afterwards is
dropped. `privacy_sentinel` rows are synthetic dummies and are allowlist-checked
instead of redacted, because the gold spans *are* the dummies. Splits are by
`source_group` so no source appears in both train and holdout.

Run the holdout with 2 exemplars per role drawn from the TRAIN split:

```bash
python3 scripts/sms/gauntlet.py \
  --models lfm25-350m-q6k \
  --roles well_curator,mempalace_extractor,failure_classifier,tool_router,privacy_sentinel \
  --dataset ~/WanderGround/datasets/sms/sms_real_v1_holdout.jsonl \
  --limit 20 --concurrency 2 --warmup 2 --few-shot 2 \
  --out-dir runs/sms_real_350m_20261008
```

`--few-shot 0` (the default, and the flag's absence) is byte-identical to the
previous behavior. `--few-shot-source` defaults to the `_train` split beside
`--dataset`; a `_holdout` dataset never resolves to itself as the exemplar pool.

## Run

```bash
python3 scripts/sms/gauntlet.py \
  --models lfm25-230m-q6k,lfm25-350m-q6k \
  --roles mempalace_extractor,well_curator,tool_router,privacy_sentinel,failure_classifier \
  --limit 10 --concurrency 1 --out-dir runs/sms_smoke --warmup 1
```

Flags: `--models`, `--roles`, `--limit` (per role), `--concurrency` (keep 1–2
on CPU-only Node 1), `--out-dir`, `--warmup`, `--dataset`, `--host`,
`--few-shot N`, `--few-shot-source PATH`, `--num-predict`, `--num-thread`,
`--inject-failure`, `--injected-timeout-s`.

Model settings (fixed unless overridden): Ollama `/api/chat`, `format: "json"`,
`temperature: 0.1`, `num_thread: 6`, `num_predict: 512`.

## Exemplar-echo metrics (always reported)

Every aggregate and every `report.md` carries `distinct_output_ratio`,
`modal_output_share`, `copy_suspect_n` and `copy_suspect`
(`distinct_output_ratio < 0.35 and n >= 8`). A high exact-match with
`copy_suspect = true` is prior-dominated, not capability — see
`docs/research/LFM25_SMS_PHASE2_ECHO_DECOMPOSITION_20261008.md` §1.

## Deliberate failure probes

`failure_classifier` gold can only contain classes the runner produces. To get
real `parse_failure` / `latency_spike` / `schema_violation` traces:

```bash
python3 scripts/sms/gauntlet.py \
  --models lfm25-350m-q6k \
  --roles well_curator,tool_router,privacy_sentinel,failure_classifier,mempalace_extractor \
  --dataset ~/WanderGround/datasets/sms/sms_real_v1_holdout.jsonl \
  --limit 12 --concurrency 2 --warmup 2 --inject-failure auto \
  --out-dir runs/sms_inject_probe_20261008

python3 scripts/sms/capture_phase2_dataset.py \
  --probe-run runs/sms_inject_probe_20261008/results.jsonl
```

`auto` rotates `none` / `truncate` / `malformed_json` / `timeout` /
`schema_violation` deterministically; the `timeout` probe is a real client-side
HTTP timeout. Gold is the runner's own `failure_class_for()` verdict — nothing is
hand-labelled.

## Paraphrase probe

```bash
python3 scripts/sms/paraphrase_probe.py \
  --model lfm25-350m-q6k --few-shot 2 --limit 20 \
  --out-dir runs/sms_paraphrase_350m_20261008
```

Deterministic, offline rewrites of the record's prose fields. Gold is identical
across arms; a rewrite that could change the label is dropped. The verdict has
three outcomes, not two: accuracy invariant to paraphrase because the output
does not depend on the input is **not** evidence of inference.

## Contract decomposition

Four flat single-purpose contracts split off the complex v1 roles. Gold is
derived from the existing holdout — no new labelling:

```bash
python3 scripts/sms/decomposition/build_derived.py
python3 scripts/sms/gauntlet.py --models lfm25-350m-q6k \
  --roles place_classifier,quote_extractor,pii_action,supersede_decider \
  --dataset ~/WanderGround/datasets/sms/derived/all_flat_holdout.jsonl \
  --few-shot 2 --concurrency 2 --warmup 2 \
  --out-dir runs/sms_p2_flat_20261008
python3 scripts/sms/decomposition/compare.py \
  --baseline runs/sms_p2_baseline_20261008 --flat runs/sms_p2_flat_20261008 \
  --baseline-dataset ~/WanderGround/datasets/sms/sms_real_v1_holdout.jsonl \
  --flat-dataset ~/WanderGround/datasets/sms/derived/all_flat_holdout.jsonl
```

`compare.py` also scores two constant predictors (the model's own modal output,
and the majority gold) so "prior-dominated" is computed rather than asserted.
A flat contract counts as a win only if it beats its complex parent on the
primary metric **and** does not collapse into echo.

## Outputs (per run, under `--out-dir`)

- `results.jsonl` — per case: raw output, latency, tokens, validity,
  conformance, role metrics, failure_class, injected_failure
- `scoring.json` — aggregates per model×role (incl. echo metrics, `per_metric_mean`,
  `num_predict`, `num_thread`)
- `report.md` — markdown table, with a dedicated exemplar-echo section
- `failure_examples.md` — top 5 per failure class (raw outputs, local only)

## Privacy

Smoke data is synthetic. Never point `--dataset` at raw private transcripts;
sanitize per blueprint §1.2 (sentinel pre-scan, path normalization, hash
splits). Commit `scoring.json` / `report.md` (redacted) only — raw outputs
stay local (gitignored `runs/`).
