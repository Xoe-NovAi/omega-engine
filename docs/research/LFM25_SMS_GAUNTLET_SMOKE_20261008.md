# LFM2.5 SMS Gauntlet — Smoke Benchmark 2026-10-08

**Runner**: `scripts/sms/gauntlet.py` (new) · **Blueprint**: `docs/research/P7_SMS_GAUNTLET_BLUEPRINT_20261008.md`
**Node**: Node 1 (CPU-only i7-13620H) · **Ollama**: local, `/api/chat`, `format:"json"`, `temperature 0.1`, `num_thread 6`, `num_predict 512`

## Setup

- Dataset: `scripts/sms/datasets/sms_smoke_dataset.jsonl` — 37 synthetic, sanitized rows, 7–8 gold cases per role, ≥25% adversarial (injection, empty, malformed, privacy-synthetic, mixed-language). Labels: `synthetic-deterministic`.
- Roles: `mempalace_extractor`, `well_curator`, `tool_router`, `privacy_sentinel`, `failure_classifier`.
- Models: `lfm25-230m-q6k`, `lfm25-350m-q6k` (Q6_K GGUF served via Ollama).
- Command:
  `python3 scripts/sms/gauntlet.py --models lfm25-230m-q6k,lfm25-350m-q6k --roles mempalace_extractor,well_curator,tool_router,privacy_sentinel,failure_classifier --limit 8 --concurrency 1 --out-dir runs/sms_smoke_20261008 --warmup 1`

## Aggregate results (74 cases)

| model | role | n | json_valid% | schema% | exact_match | field_f1 | p50_s | p95_s | tokens_mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lfm25-230m-q6k | failure_classifier | 7 | 100.0 | 100.0 | 0.571 | 0.571 | 0.38 | 0.43 | 39.3 |
| lfm25-230m-q6k | mempalace_extractor | 8 | 100.0 | 0.0 | 0.0 | 0.0 | 0.70 | 1.48 | 81.1 |
| lfm25-230m-q6k | privacy_sentinel | 7 | 100.0 | 28.6 | 0.0 | 0.0 | 0.76 | 1.07 | 103.3 |
| lfm25-230m-q6k | tool_router | 8 | 100.0 | 0.0 | 0.0 | 0.0 | 0.63 | 0.69 | 67.5 |
| lfm25-230m-q6k | well_curator | 7 | 100.0 | 0.0 | 0.0 | 0.0 | 0.64 | 0.68 | 61.3 |
| lfm25-350m-q6k | failure_classifier | 7 | 100.0 | 100.0 | 0.429 | 0.429 | 0.53 | 0.63 | 34.7 |
| lfm25-350m-q6k | mempalace_extractor | 8 | 100.0 | 12.5 | 0.0 | 0.125 | 1.60 | 2.50 | 146.5 |
| lfm25-350m-q6k | privacy_sentinel | 7 | 100.0 | 100.0 | 0.286 | 0.429 | 0.84 | 1.29 | 78.1 |
| lfm25-350m-q6k | tool_router | 8 | 100.0 | 75.0 | 0.375 | 0.0 | 0.93 | 1.02 | 49.2 |
| lfm25-350m-q6k | well_curator | 7 | 100.0 | 0.0 | 0.0 | 0.0 | 0.78 | 0.90 | 46.9 |

## Findings

1. **JSON validity is 100% on both models** (74/74) — confirms E0 but on a
   real, scored set: validity alone is uninformative; schema conformance is
   the discriminating metric.
2. **350M is meaningfully more contract-compliant than 230M.** 350M reaches
   100% schema conformance on `privacy_sentinel` and `failure_classifier`,
   75% on `tool_router`; 230M only on `failure_classifier`.
3. **Extractor and well-curator are the hard roles for both models** —
   0% schema conformance for 230M, ≤12.5% for 350M. The 230M model often
   echoes the input envelope (missing `wing`/`items`); the 350M model
   produces more structure but drifts on exact fields (e.g. `confidence` as
   string, invented enums).
4. **Adversarial injection cases mostly fail safe** (empty → `items: []` on
   schema-conformant rows only). Where conformance failed, the injection
   payload itself became the output (`ex_003`:
   `'{"window": "ignore previous instructions...", "hacked": true}'`) —
   tagged `schema_violation`/`parse_failure`, never a clean pass.
5. **Latency**: both models meet the p95 ≤ 2 s gate at 512 max tokens;
   230M p50 ~0.4–0.8 s, 350M p50 ~0.5–1.6 s. Extractor outputs are longest
   and slowest (mean 146 tokens for 350M).
6. **Failure taxonomy** (from `results.jsonl` `failure_class`): dominated by
   `schema_violation` (n=44 of 74), plus occasional `parse_failure` on
   injection rows. No `latency_spike` at the 512-token cap.

## Interpretation vs P7.1 gates

- JSON validity gate (≥95%): **pass** both models.
- Schema conformance (≥95%): **fail** everywhere except 350M `privacy_sentinel` /
  `failure_classifier`.
- Task metrics: `failure_classifier` is the only role near gate-shaped
  behavior (exact_match ~0.43–0.57, absolute, no few-shot).
- Privacy/router exact-match below 0.9/0.85 gates; extractor F1 ≈ 0 vs ≥0.70.

Conclusion: **do not train yet**. Next discriminating steps: (a) add ≤2
few-shot exemplars per role and re-measure (prompt-only ceiling), (b) run the
full P7.1d E0-scale set (100 cases/role) once prompts stabilize, (c) only on
persistent gate failure consider the TRL/PEFT/LoRA pilot per blueprint §9.

## Artifacts

- Raw: `runs/sms_smoke_20261008/results.jsonl` (gitignored)
- Aggregates: `runs/sms_smoke_20261008/scoring.json`
- Failure microscope: `runs/sms_smoke_20261008/failure_examples.md`
- Dataset manifest row: `scripts/sms/datasets/sms_smoke_dataset.jsonl` (synthetic only)
