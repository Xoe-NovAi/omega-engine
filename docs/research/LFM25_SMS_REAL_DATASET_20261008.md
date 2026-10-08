# LFM25 SMS Gauntlet — Real Dataset Capture + Few-Shot A/B (2026-10-08)

**Author**: researcher_humboldt · **Date**: 2026-10-08 · **Status**: measured
**Supersedes**: `LFM25_SMS_GAUNTLET_SMOKE_20261008.md` (synthetic smoke rows only)
**Blueprint**: `docs/research/P7_SMS_GAUNTLET_BLUEPRINT_20261008.md`
**Dataset**: `sms_real_v1` · **Model**: `lfm25-350m-q6k` (Ollama-served Q6_K)

Labels: `[Measured]` = from the runs cited in this file. `[Proposal]` = a design
decision. `[Open question]` = needs operator direction.

---

## 0. Headline

1. The smoke schemas were **wrong about the real corpus**. `well_curator` is
   missing `preference` and `dream` kinds and the `consciousness` domain; the
   Well has 6 of those records. Fixed before capture. [Measured]
2. `sms_real_v1`: **303 redacted rows** from four real sources, split by
   `source_group` (173 train / 130 holdout, zero group overlap). Raw stays in
   `~/WanderGround/datasets/sms/`. [Measured]
3. Two exemplars per role move **well-curator** from 0.000 → **0.767** exact and
   0% → **90%** schema conformance, and **tool-router** conformance 25% → 67%.
   Every other role stays at or near zero. [Measured]
4. **Verdict**: exactly one role (`well_curator`) is close to trainable
   prompt-only, and even that gain is largely template echo (§5.1). Extractor,
   failure-classifier and privacy-sentinel are not close. See §6.

---

## 1. Task 1 — schema/prompt drift fix (a real bug, not cosmetics)

The real Well corpus (`gnosis/well/well.jsonl`, 74 records) has:

| field | distribution |
|---|---|
| `kind` | correction 59 · insight 8 · preference 4 · dream 2 · anti_pattern 1 |
| `domain` | harness 63 · local_ai 9 · consciousness 2 |
| `status` | active 68 · superseded 6 |

The smoke schema allowed `kind ∈ {correction, anti_pattern, insight, measurement,
rule}` and `domain ∈ {local_ai, gaming, harness, research, general}`. So 6 of 74
real records (4 `preference`, 2 `dream`) and 2 more (`consciousness`) would have
scored `schema_violation` against gold that the corpus itself produces — a
guaranteed-fail scoring artifact, not a model failure.

Fixes applied to both `scripts/sms/schemas/well_curator.schema.json` and
`roles.SYSTEM["well_curator"]`:

- `kind` += `preference`, `dream`
- `domain` += `consciousness`

`measurement` / `rule` / `gaming` / `research` / `general` were **kept** so the
existing smoke dataset stays valid (it has `measurement` and `gaming` rows).
Verified the smoke dataset still runs clean after the change
(`runs/sms_smoke_20261008` path unchanged, 7/7 JSON-valid).

---

## 2. Capture provenance (`scripts/sms/capture_real_dataset.py`)

| role | rows | gold source | labeler |
|---|---:|---|---|
| `mempalace_extractor` | 120 | MemPalace palace drawers, sampled round-robin across (wing, room) | deterministic |
| `well_curator` | 74 | every record in `gnosis/well/well.jsonl` | deterministic |
| `failure_classifier` | 74 | `runs/sms_full_smoke_20261008/results.jsonl` — real traces, gold = the runner's own `failure_class` | deterministic |
| `tool_router` | 20 | documented rules in `AGENTS.md` §Session recall/§Hard rules + `docs/AGENT_RUNBOOK.md` §3.7 | curated |
| `privacy_sentinel` | 15 | constructed synthetic dummies (RFC-5737 / example.com) | constructed |

**303 rows total.**

Construction notes that matter for trusting the numbers:

- **Palace access.** Opened `~/WanderGround/mempalace/sqlite_exact.sqlite3`
  read-only with `mode=ro` (never `immutable=1`, which ignores the WAL — hard
  rule in AGENTS.md). 1,156 documents, 486 non-chunked; drawers sampled
  deterministically (sha256 of drawer id) round-robin over 117 (wing, room)
  pairs so no single room dominates. Test/recovery wings excluded.
- **Extractor `source_quote` is asserted, not assumed.** Each window embeds the
  drawer's verbatim content between filler prose; the script verifies
  `gold.items[0].source_quote in input` and drops failures. **0 drops** on this
  capture, and the assertion is re-run *after* redaction (a redaction that
  breaks grounding would raise, not silently pass).
- **well_curator direction trap.** The prompt never leaks `kind`/`domain`/`tags`.
  For superseded records it shows the chain ids + timestamps including a
  same-pack **older distractor**, so copying "the other id" is wrong. Records
  whose `superseded_by` does not point strictly forward in time are excluded
  from gold (0 excluded — all 6 chains are correctly oriented, confirming the
  Well `759c7639` correction holds in the data).
- **failure_classifier class coverage.** The live run produced only `ok` and
  `schema_violation` — there were no real `parse_failure` or `latency_spike`
  rows to capture. That is a property of the run, not a bug, and it is recorded
  as a limitation in the manifest and in §6.
- **tool_router** covers all 7 allowlist tools including 4 abstention cases
  (`none`), one of which is an injection attempt.

---

## 3. Redaction / privacy gate (mandatory, enforced in-script)

Scanner `sentinel/1.1.0` runs on **every** row before any write. Patterns:
email, IPv4, `sk-`/`ghp_`-shaped keys, bearer tokens, `ho_[0-9a-f]{12}` handoff
ids, absolute `/home/<user>` paths, and secret-looking assignments
(`API_KEY=…`, `password: …`, `token = …`, value-only span).

Replacement is typed: `<EMAIL>`, `<IP>`, `<API_KEY>`, `<TOKEN>`, `<HANDOFF_ID>`,
`<HOME_PATH>`. Any row still tripping the scanner afterwards is **dropped**.

Redaction counts per role:

| role | home_path | handoff_id | email | ip | api_key | dropped post-redaction |
|---|---:|---:|---:|---:|---:|---:|
| `mempalace_extractor` | 114 | 36 | 3 | 3 | 0 | 0 |
| `failure_classifier` | 0 | 0 | 3 | 5 | 3 | 0 |
| `well_curator` | 1 | 3 | 0 | 0 | 0 | 0 |
| `tool_router` | 0 | 0 | 0 | 0 | 0 | 0 |
| `privacy_sentinel` | — | — | — | — | — | 0 (15 allowlist-passed) |

`privacy_sentinel` is **redaction-exempt by design**: its gold `pii_found` spans
*are* the dummy identifiers, so redacting the input would destroy the label. It
is instead verified against a synthetic allowlist (`example.{com,org,net}`,
RFC-5737 ranges, `sk-`/`ghp_`-shaped dummies, digit-shaped phones/SSNs,
lowercase `/home/<word>`). 2 rows initially failed the allowlist during
development and were corrected at the source (a real `100.64.x` tailnet address
and a bare `aaaaaaaa…` secret), not by relaxing the rule.

The repo-side manifest additionally scrubs absolute paths to `<HOME_PATH>`.
Scanning the 25-row committed preview returns 11 sentinel hits — all inside
`privacy_sentinel` rows, all allowlisted synthetic dummies. No other role's
committed row trips the scanner.

---

## 4. Manifest, split, and few-shot support

- Raw: `~/WanderGround/datasets/sms/sms_real_v1.jsonl` (+ `_train`, `_holdout`,
  `manifest.json`) — outside git.
- In repo: `scripts/sms/datasets/sms_real_manifest.json` and
  `sms_real_preview.jsonl` (25 rows, exactly 5 per role).
- Split by `source_group`: within each role, groups ordered by
  `sha256("{role}:{group}")`, highest to holdout. Group count chosen to land
  near 30% holdout subject to two hard constraints — train keeps ≥6 rows across
  ≥2 groups, and each role's **categorical gold stays represented on both
  sides**. That second constraint exists because the naive hash split put all 6
  `supersede` cases in train, which would have made the blueprint §3.2
  supersession-direction gate unmeasurable.
- Verified: `{source_group(holdout)} ∩ {source_group(train)} = ∅`.

| role | rows | groups | holdout rows | holdout gold categories |
|---|---:|---:|---:|---|
| `well_curator` | 74 | 11 | 50 | keep, supersede |
| `mempalace_extractor` | 120 | 115 | 36 | — |
| `failure_classifier` | 74 | 5 | 28 | ok, schema_violation |
| `tool_router` | 20 | 20 | 12 | all 7 tools incl. `none` |
| `privacy_sentinel` | 15 | 15 | 4 | allow, redact, drop |

Per-role sha256 of the serialized rows, the `source_group` id for every row, the
capture timestamp, scanner version, and redaction counts are all in the manifest.

`gauntlet.py` gained `--few-shot N` and `--few-shot-source PATH`. N exemplars
per role are prepended as user/assistant pairs (exemplar assistant turn = the
canonical gold JSON). Default exemplar source = the `_train` split beside
`--dataset`; a `_holdout` path can never resolve to itself as the pool, and any
exemplar whose `case_id` is in the evaluated set is filtered out. Exemplars are
chosen deterministically by even spacing over sorted case ids. With the flag
absent, or `--few-shot 0`, the message list is byte-identical to before
(`chat_json` is now a thin wrapper over `chat_messages`).

---

## 5. Results — zero-shot vs few-shot (2 exemplars)

Holdout, `--limit 20` per role, `concurrency 2`, `warmup 2`.
Runs: `runs/sms_real_350m_zeroshot_20261008/` and `runs/sms_real_350m_20261008/`.

| role | n | schema% zs→fs | exact zs→fs | field_f1 zs→fs | p50 s zs→fs | tokens zs→fs |
|---|---:|---:|---:|---:|---:|---:|
| `well_curator` | 20 | 0.0 → **90.0** | 0.000 → **0.767** | 0.000 → **0.390** | 3.48 → 6.97 | 49.8 → 67.2 |
| `mempalace_extractor` | 20 | 0.0 → 5.0 | 0.000 → 0.000 | 0.000 → 0.000 | 8.90 → 14.79 | 324.0 → 260.9 |
| `failure_classifier` | 20 | 100.0 → 100.0 | 0.000 → 0.000 | 0.000 → 0.000 | 1.75 → 3.84 | 28.9 → 31.4 |
| `tool_router` | 12 | 25.0 → **66.7** | 0.000 → 0.000 | 0.000 → 0.056 | 1.37 → 2.78 | 27.1 → 28.4 |
| `privacy_sentinel` | 4 | 100.0 → **75.0** | 0.000 → 0.000 | 0.548 → **0.250** | 2.20 → 2.91 | 83.5 → 63.0 |

Per-field detail for the two roles that moved:

| role | metric | zs | fs |
|---|---|---:|---:|
| `well_curator` | action exact | — (0% conformant) | 0.850 |
| `well_curator` | domain exact | — | 0.800 |
| `well_curator` | kind exact | — | 0.650 |
| `well_curator` | supersession_shape_ok | — | 0.900 |
| `well_curator` | tags F1 | — | 0.013 |
| `tool_router` | fallback exact | 0.167 | 0.667 |
| `tool_router` | args F1 | 0.000 | 0.056 |
| `tool_router` | tool exact | 0.000 | 0.000 |
| `mempalace_extractor` | provenance_preserved | 0.000 | 0.025 |

Cost of few-shot: p50 latency roughly doubles on every role (prefill of 2
exemplars) and tokens-out rises 9–34%. The blueprint's p95 ≤ 2 s gate is already
missed by every role at this model's speed on CPU-only Node 1 — well-curator
p95 8.0 s few-shot, extractor p95 17.1 s — so latency is the binding constraint
regardless of accuracy.

### 5.1 The well-curator gain is mostly template echo

This is the finding that matters most and it cuts against the headline.

Of 20 few-shot well-curator outputs, **19 contain all five exemplar tags
verbatim** and only 3 distinct outputs exist across 20 cases (18 identical).
Zero-shot had 19 distinct outputs. The model learned to copy the exemplars'
`kind`/`domain`/`tags` fields rather than infer them:

| output class | n | kind exact | domain exact | action exact | tags F1 |
|---|---:|---:|---:|---:|---:|
| exemplar-copying | 19 | 0.684 | 0.842 | 0.895 | 0.013 |
| non-copying | 1 | 0.000 | 0.000 | 0.000 | 0.000 |

The 0.767 exact-match headline is therefore **prior-dominated**: 18 of the 20
evaluated gold cases are `action=keep`, and the copied exemplar answer is
`keep`. `tags_f1 ≈ 0.01` says plainly that the one field requiring genuine
inference from the record text is not being inferred. Per the blueprint §7
template-echo test, this is an overfitting alarm, not a capability measurement.
The one case the model answered on its own (`insight`/`merge` where gold was
`correction`/`keep`) was wrong on all four fields.

Same pattern elsewhere: extractor few-shot produced only 4 distinct outputs over
20 cases (17 identical), zero-shot produced 19 — the exemplars collapsed the
output distribution. The few-shot extractor's 19/20 `game_research` wings are the
exemplar's wing, while gold spans 9 wings.

### 5.2 failure_classifier: 100% conformant, 0% correct

The schema is trivially satisfied (one enum, one number, one string) in both
arms, and `class_exact` is 0.000 in both. Predictions collapse to `abstained`
(12 zero-shot, 15 few-shot) and `hallucinated_entity` (8 / 4); gold is
`schema_violation` 19 / `ok` 1. This is the clearest evidence in the run that
**conformance is not capability** — the model can emit valid JSON and still
have nothing to say. It also explains the smoke run's 70% "ok" rate as
formatting success, not understanding.

### 5.3 privacy_sentinel: few-shot made it worse

n=4, so treat as directional only. Zero-shot span-F1 0.548 → few-shot 0.250,
conformance 100% → 75%. Cause is visible in the outputs: the model copies the
exemplar's `ho_0123456789ab` handoff span into unrelated cases (`ps_real_004`,
`ps_real_012`) and inverts the action vocabulary, answering `drop` where gold is
`redact`. It also emits `"type": "host"`, which is not in the enum. Four cases is
not enough to conclude few-shot is harmful here, but it is enough to conclude
few-shot is **not** the missing ingredient.

### 5.4 tool_router: conformance up, routing still wrong

Conformance 25% → 66.7% is real — the exemplars taught the output shape. But
`tool_exact` is 0.000 in both arms. Few-shot spreads predictions
(`well_add` 4, `ochist_grep` 4, `none` 4) versus zero-shot's degenerate
`none` ×10, so the diversity is progress in the right direction (abstention
accuracy 0.167 → 0.667), but the model has not learned to discriminate among
tools. `args_f1` 0.056 means it is not even reproducing argument keys.

---

## 6. Verdict — which roles are close to trainable

Against the blueprint §3.2 gates (validity ≥95%, conformance ≥95%, router
tool-exact ≥0.85, curator acc ≥0.80, privacy action-acc ≥0.90, supersession
100%, provenance ≥95%):

| role | verdict | reasoning |
|---|---|---|
| `well_curator` | **closest — but not shippable as-is** | 90% conformance / 0.767 exact is the only result that clears anything, and §5.1 shows it is exemplar copying. `tags_f1` 0.013 and the one non-copying case scoring 0/4 mean inference is absent. The measured delta also exceeds the blueprint's ±10-pt noise floor for n=20, so the *exemplars themselves are worth keeping* — but a next round must change the exemplar selection (diverse kinds/domains/tags, not two harness corrections) and report a paraphrase-probe score, not the aggregate. |
| `tool_router` | **structurally learnable, not close** | Tightest schema, and the exemplars demonstrably fixed the output shape (25% → 67% conformance). Discrimination is at zero. This is the best LoRA candidate after well-curator: small output space, deterministic labels from documented rules, and cheap to expand past 20 rows. |
| `privacy_sentinel` | **not close** | 15 rows total, 4 in holdout — the measurement is underpowered by construction. Action accuracy 0.000 in both arms. Needs more rows and a prompt that separates `allow` from `redact` from `drop` before any model claim. |
| `failure_classifier` | **not close** | 100% conformance / 0% accuracy is the sharpest conformance-vs-capability gap in the run. Gold has only 2 classes because the source run had only 2, so the classifier is learning on a degenerate distribution. Capture real `parse_failure` / `latency_spike` traces first. |
| `mempalace_extractor` | **furthest** | 5% conformance, 0.000 F1, 0.025 provenance, p95 17 s. It copies exemplars instead of quoting the window (17/20 identical outputs). This is the hardest contract and the model is not near it. |

**On training**: the blueprint gate is "beat the prompt-only baseline by ≥10 pts
on the primary metric or reject training". On the primary metric *for the role
that moved*, few-shot beat zero-shot by 76.7 pts — but §5.1 attributes that to
echo, so it is not evidence for LoRA. Honest read: **no role has yet earned a
training run.** The next measurement action is not TRL/PEEF; it is (a) exemplar
diversification + a paraphrase probe for well-curator, (b) 60+ rows for
tool-router, (c) real parse/latency traces for failure-classifier, and only then
a LoRA pilot on the two roles that survive those checks.

---

## 7. Artifacts

| Artifact | Location |
|---|---|
| Capture script | `scripts/sms/capture_real_dataset.py` |
| Fixed schema | `scripts/sms/schemas/well_curator.schema.json` |
| Fixed prompt | `scripts/sms/roles.py` (`SYSTEM["well_curator"]`) |
| Few-shot support | `scripts/sms/gauntlet.py` (`--few-shot`, `--few-shot-source`) |
| Repo manifest | `scripts/sms/datasets/sms_real_manifest.json` |
| Repo preview | `scripts/sms/datasets/sms_real_preview.jsonl` (25 rows) |
| Raw + splits (outside repo) | `~/WanderGround/datasets/sms/` |
| Few-shot run | `runs/sms_real_350m_20261008/` |
| Zero-shot run | `runs/sms_real_350m_zeroshot_20261008/` |
| Blueprint | `docs/research/P7_SMS_GAUNTLET_BLUEPRINT_20261008.md` |

Gates: `make lint`, `make test`, `make docs` green at time of filing. The smoke
dataset and its default zero-shot behavior are unchanged.

---

## 8. Open questions for the operator

1. Holdout sizes are uneven (50 well-curator / 36 extractor / 28 failure /
   12 router / **4 privacy**). Should privacy and router be scaled to ~60 rows
   each before any conclusion is recorded, even though that pushes the capture
   past the ~303 rows this pass produced?
2. `failure_classifier` gold can only contain classes the runner actually
   produced. Should the runner be instrumented to emit deliberate failure
   probes (forced truncation, forced bad schema) so this role gets a real
   distribution?
3. The split's coverage constraint (both sides must hold each categorical gold)
   is a deliberate deviation from a pure hash split. Acceptable, or should
   supersession cases instead be promoted to their own dedicated adversarial
   holdout as blueprint §2.2 originally suggested?

---

*Filed 2026-10-08 by researcher_humboldt. Real gold, redacted and hashed, lives
outside git; the repo holds only the manifest, a 25-row preview, and the scoring
code. No raw private content was committed.*