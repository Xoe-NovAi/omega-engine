# LFM2.5 SMS Gauntlet — P7.1 Evaluation Blueprint

**Author**: researcher_humboldt · **Date**: 2026-10-08 · **Status**: blueprint (no code)
**Supersedes**: E0 smoke test (`LFM25_SMS_E0_RESULTS_20261008.md` — 5 prompts/model, no accuracy)
**Target gate**: P7.1 requires a real dataset + scored gauntlet **before any LoRA training**.

Labels: `[Measured]` = from local runs cited, `[Provider claim]` = Liquid/Unsloth docs, `[Proposal]` = design decision awaiting operator ratification, `[Open question]` = needs operator direction.

---

## 0. Design principles

1. **Measurement before training.** The gauntlet is the gate. Training starts only if a pre-registered baseline misses an explicit threshold. [Measured precedent: E0 showed 100% JSON-validity on 5 trivial cases — that number is uninformative.]
2. **Every datum carries provenance.** Source artifact ID, extraction timestamp, gold-labeler identity, human-audit flag. No drawer enters a dataset without `{source_file, recorded_at, labeler}`.
3. **The model formats; it never remembers.** Gold labels for extraction roles come from retrieval + deterministic post-processing, not model recall. This keeps the task honest: can a 230M/350M *shape* the answer, not *know* it.
4. **Narrow contracts first.** Privacy filter and tool router have the tightest output schemas → most reliable signal per prompt. Extractor is the hardest → the most informative failure microscope.
5. **Adversarial by construction.** ≥25% of every split is failure-shaped: malformed transcripts, prompt injection, mixed-language spans, empty inputs, schema-hostile content.
6. **The served artifact is the evaluated artifact.** Score the Ollama-served Q6_K GGUF, not training safetensors. Quantization drift is part of the measurement.

---

## 1. Building real datasets from local Omega artifacts (no secrets)

### 1.1 Source inventory (local, pre-existing)

| Source | What it yields | Risk | Mitigation |
|---|---|---|---|
| Palace drawers (`mempalace_list_drawers`, per wing/room) | Transcript windows for `mempalace-extractor` gold | Personal life content, possible API keys/tokens in old logs | Sentinel pre-scan (§10); drop windows scoring above threshold; never commit raw text to git |
| The Well records (`make well-export` JSONL/MD) | `well-curator` labels: `kind`, `domain`, `tags`, `action`, supersession chains | Personal corrections | Same sentinel scan; Well IDs are opaque — keep only structure + redacted bodies |
| ROADMAP.md | `tool-router` / `omega-hub dispatcher` exemplars: phase names, agent roles, statuses | Low | Public within repo; still redact hostnames/IPs |
| `~/GameResearch/SESSION-STATE.md`, gaming rules | extra extractor/router windows | Low | gitignored — treat as private |
| omega-hub/Hivemind event log (local mirror) | `failure-classifier`, `omega-hub dispatcher` traces | Contains agent identities/paths | Hash agent names, strip absolute paths to `<PROJECT_ROOT>/...` |
| Open WebUI conversation exports (operator opt-in only) | well-curator / empress-lens dialogue | High (personal) | **Explicit opt-in required**; redact before any use |

### 1.2 Sanitization pipeline (mandatory, before any window is usable)

1. **Sentinel scan** — reuse the `privacy-sentinel` regex+heuristic set (emails, IPv4/IPv6, tailnet hostnames, API-key shapes `sk-…`, `ghp_…`, bearer tokens, absolute `/home/<user>` paths, SSNs, credit-card Luhn). Hits → redact to typed placeholders (`<EMAIL>`, `<TAILNET_IP>`, `<USER_PATH>`). Windows with >N hits or unresolvable PII → discard, do not redact.
2. **Secret scan on repo side** — `git grep` for key patterns over candidate source dirs; exclude `.env*`, `*.pem`, `*credentials*`.
3. **Path normalization** — all absolute paths rewritten relative to repo root; operator-specific dirs replaced with `<NODE1>`, `<NODE0>`.
4. **Dedup + split by session/source file, never by row.** Adjacent windows from one transcript must not straddle train/eval splits. Split key = `source_file` hash bucket (e.g., SHA-256 mod 10 → 8 train / 1 val / 1 test).
5. **Freeze + hash.** Each dataset version is a single JSONL with a top-level manifest: `{dataset_id, created_at, source_whitelist, sentinel_version, sha256, n_train, n_val, n_test}`. Datasets live outside git (`~/WanderGround/datasets/sms/`) — git holds only manifests and scoring code. [Proposal]

### 1.3 Feasible scale

- Per-role gold sets: **300–500 examples** total (240–400 train, 60 val, 60–100 test). Test sets of ~100 per role keep CIs tight enough (±5 pts at F1≈0.8, worst-case ±10).
- Total generation: ~2,000–3,000 examples across 7 roles. With 350M-class models at ~40–130 tok/output and ~0.3–2 s/case [Measured E0], a full gauntlet pass is **30–90 min per model** — feasible nightly. [Measured on E0 latency: 0.3–1.8 s/case]
- E0 (full scale) target: **2 roles × 2 models × 100 held-out cases** as the P7.1 gate; roll to all roles once the runner exists.

---

## 2. Gold label formats (exact)

All schemas below are **versioned** (`schema_version` field) and validated at scoring time with JSON Schema (Draft 2020-12). A response that is not valid JSON against the schema scores 0 for conformance and is tagged `parse_failure`.

### 2.1 `mempalace-extractor` (from a transcript/drawer window)

```json
{
  "wing": "string (from source_file path segment)",
  "room": "string (existing room vocab; may be 'new:<slug>')",
  "items": [
    {
      "kind": "corrections|decisions|measurements|patterns|narrative|questions",
      "content": "string, verbatim or tightly grounded span",
      "source_quote": "exact substring of the input window",
      "confidence": 0.0
    }
  ],
  "provenance": {"source_file": "...", "recorded_at": "ISO-8601", "window_id": "..."}
}
```
Gold construction: teacher (local LFM2.5-1.2B-Extract or 2.6B, or paid-ZDR frontier) drafts → deterministic checks (`source_quote` must be a substring of the input; `kind` in vocab) → ≥10% human audit → freeze.

### 2.2 `well-curator`

```json
{
  "kind": "correction|anti_pattern|insight|measurement|rule",
  "domain": "local_ai|gaming|harness|research|general",
  "tags": ["..."],
  "action": "keep|supersede|merge|drop",
  "superseded_by": "well_id or null",
  "rationale": "<= 200 chars"
}
```
Gold rule: `superseded_by` must point to the **newer** record and `action=supersede` only then (the Well chain-direction correction, id `759c7639`). Adversarial set flips direction — a model that copies direction gets 100% fail.

### 2.3 `tool-router`

```json
{
  "tool": "mempalace_search|mempalace_kg_query|well_add|web_search|ochist_grep|ocdb_ro|none",
  "args": {"...": "..."},
  "fallback": "none|ask_human|deterministic_regex"
}
```
Gold: the *intended* tool given a request + allowlist. Args scored field-wise (exact match on tool; F1 on args keys/values). `none` is a first-class label — tests abstention.

### 2.4 `privacy-sentinel`

```json
{
  "pii_found": [{"type": "email|ip|api_key|user_path|ssn|phone", "span": "..."}],
  "action": "allow|redact|drop",
  "redacted_text": "string or null"
}
```
Gold: span-level labels hand-audited by operator on a seed set, then expanded via teacher + sentinel agreement. Metric: span-level F1 **and** action accuracy. False negatives on `api_key` type weighted 2× in the failure taxonomy.

### 2.5 `empress-lens` (voice/tone probe — weakest contract, scored last)

```json
{
  "tone": "sovereign|clinical|warm|alarm|neutral",
  "entities": ["..."],
  "register": "formal|informal",
  "stance": "supportive|corrective|neutral"
}
```
Gold: multi-rater consensus (≥2 raters or rater+operator), Cohen's κ ≥ 0.6 required before gold is frozen; otherwise the role is dropped from P7.1 gates. [Open question]

### 2.6 `omega-hub-dispatcher`

```json
{
  "target_agent": "roc_racoon|hivemind|mempalace-curator|local",
  "priority": "p0|p1|p2",
  "payload_kind": "task.request|task.reply|patch.ready|awareness|status",
  "packet": {"filename": "...", "size_bytes": 0, "sha256": "...", "pull_url": "..."}
}
```
Gold: constructed from real Hivemind event mirror; `packet.size_bytes` must pass the ≤4 KB handoff rule [Measured, Well `3a0c851b`].

### 2.7 `failure-classifier`

```json
{"class": "parse_failure|schema_violation|truncation|hallucinated_entity|latency_spike|wrong_tool|abstained|ok",
 "confidence": 0.0, "evidence": "short string"}
```
Gold: derived **deterministically** from runner-produced failure traces — a rare case where gold is free and exact.

---

## 3. Metrics & gates

### 3.1 Per-case scoring

| Metric | Definition | Applies to |
|---|---|---|
| `json_valid` | whole output parses as JSON | all generative roles |
| `schema_conformant` | JSON Schema validates | all roles |
| `exact_match` | full gold equality | tool_router.tool, privacy.action, dispatcher.target_agent, curator.action |
| `field_f1` | macro-F1 over extracted fields vs gold | extractor, well-curator, privacy (span-level), empress-lens |
| `provenance_preserved` | `source_quote`/`source_file` present and substring-correct | extractor, dispatcher |
| `supersession_direction_ok` | `superseded_by` points newer | well-curator |
| `abstention_ok` | `none`/`ask_human` chosen when gold says so | tool-router, privacy |
| `latency_s`, `tokens_out` | wall time; Ollama eval count | all |
| `ram_peak_mb` | runner-sampled RSS of ollama serve | all |
| `failure_class` | taxonomy tag from runner, cross-checked by `failure-classifier` gold | all |

### 3.2 Gates (pre-registered, adjustable only with operator sign-off)

| Gate | Threshold |
|---|---|
| JSON validity | ≥ 95% |
| Schema conformance | ≥ 95% |
| Task metric (F1/acc) | extractor F1 ≥ 0.70; curator acc ≥ 0.80; router tool-exact ≥ 0.85; privacy action-acc ≥ 0.90 & span-F1 ≥ 0.75; dispatcher target+priority exact ≥ 0.85 |
| Supersession direction | 100% on adversarial subset |
| Provenance preservation | ≥ 95% |
| Latency | p95 ≤ 2 s @ ≤512 output tokens, `num_thread 6`, warm model |
| RAM | peak ≤ 4 GB for one resident model |
| Contamination | 0 sentinel hits post-redaction in training rows |
| Delta vs prompt-only baseline | trained artifact must beat base ≥ +10 pts on the primary metric, else reject training |

### 3.3 Failure taxonomy (qualitative, but counted)

`parse_failure`, `schema_violation`, `truncation`, `hallucinated_entity`, `invented_provenance`, `wrong_tool`, `unsafe_abstain`, `overabstain`, `pii_leak`, `language_drift`, `template_echo` (model echoes few-shot verbatim → overfitting alarm).

---

## 4. Sample sizes & feasibility on Node 1

- **P7.1 gate run**: 2 roles × 2 models × 100 cases = 400 cases ≈ 20–40 min [Estimate from E0: 0.3–1.8 s/case, plus cold-start ~5–15 s/model].
- **Full gauntlet**: 7 roles × 3 models (230M, 350M, and one alternative) × 100 test cases ≈ 2,100 cases ≈ 1.5–3 h at concurrency 1–2. CPU-only: **keep Ollama `num_parallel` = 1–2**; LFM throughput is not GPU-scaling on CPU and concurrent loads cost RAM (measured zRAM/thread confounds in `BENCHMARK_STUDY_20260926.md`).
- Statistical power: 100 cases → ±10 pts worst case at p=0.5; good enough for go/train decisions, not for 1-pt claims. Use exact counts in CIs (Wilson interval) in the report.

---

## 5. Gauntlet runner architecture (`scripts/sms/`)

```
scripts/sms/
  README.md                  # how to run, label schema, gates
  gauntlet.py                # main runner (argparse subcommands)
  roles/                     # one module per role: prompt builder, gold loader, scorer
    extractor.py curator.py router.py privacy.py dispatcher.py lens.py failure.py
  schemas/                   # JSON Schemas per role, versioned
  datasets/                  # NOT raw data — manifests only; data lives in ~/WanderGround/datasets/sms/
  scoring/                   # json_schema.py, span_f1.py, provenance.py, latency.py
  report.py                  # JSONL results -> scoring.json + report.md + failure_examples.md
  models.yaml                # model registry: name, path, params (num_thread, temp, num_predict)
  adversarial/               # hand-authored hostile cases, versioned
```

Runner flow (single command): `python -m scripts.sms.gauntlet run --roles extractor,curator --models lfm25-230m-q6k,lfm25-350m-q6k --split test --out runs/<ts>/`

1. Load manifest → resolve dataset JSONL → verify sha256.
2. For each case: build prompt (system + ≤2 few-shot), call Ollama `/api/chat` with `format: json`, `temperature 0.1`, `num_predict 512`, `num_thread 6`, record raw output + latency + eval token count.
3. Score per §3.1; emit `results.jsonl` (one line per case: input hash, output, scores, failure_class).
4. Aggregate → `scoring.json` (per role×model: validity %, conformance %, F1/acc, p50/p95 latency, RAM peak) + `report.md` + `failure_examples.md` (top 5 per failure_class, verbatim raw outputs).
5. Gate evaluation: pass/fail table vs §3.2, machine-readable exit code.

**Concurrency policy**: sequential or `semaphore=2`; never parallel×N on CPU-only Node 1. Model load/unload between roles to keep RAM honest.

**Warm-up**: one throwaway case per model before timing (Well `a3675a88` — cold first call is not the number).

---

## 6. Artifacts produced (per run)

| Artifact | Location | Purpose |
|---|---|---|
| `dataset.manifest.json` | `~/WanderGround/datasets/sms/<role>/v<N>/` | provenance, splits, hash |
| `<role>.test.jsonl` | same dir (gitignored) | gold cases |
| `runs/<ts>/results.jsonl` | repo `runs/` (gitignored) or palace drawer | raw outputs + scores |
| `runs/<ts>/scoring.json` | committed | aggregate metrics |
| `runs/<ts>/report.md` | committed under `docs/research/` | human report |
| `runs/<ts>/failure_examples.md` | committed, redacted | qualitative microscope |
| `docs/models/specialists/<role>.md` | OMER card | candidate→active→retired registry entry |

---

## 7. Overfitting & adversarial resistance

- **Template echo test**: if the model's output copies identical few-shot exemplars verbatim, flag `template_echo` — indicates memorization, not generalization.
- **Paraphrase probe**: 10% of test cases are paraphrased rewordings of train-window structure with new entities; metric must hold within 10 pts.
- **Injection cases**: transcripts containing `ignore previous instructions`, fake schema demands, and embedded tool-call syntax must still produce contract-conformant output.
- **Empty/degenerate inputs**: empty window, whitespace-only, single newline → expected `{"items": []}` or `action: drop`, not hallucinated content.
- **Mixed-language & typo-noise**: Hebrew/English code-switch (Node 1 has real Hebrew-normalization research), misspellings, truncated mid-word inputs.
- **Holdout discipline**: test split is sealed; iterate prompts against `val` only. Any test-set-driven prompt change resets the split.
- **Forgetting probe**: 20 generic extraction/classification prompts from a fixed public-style set; the specialist must not collapse vs base model on them.

---

## 8. Comparison plan

| Axis | Candidates | Question |
|---|---|---|
| Size | LFM2.5-230M-Q6_K vs 350M-Q6_K vs (later) 1.2B-Extract | where does F1 saturate per ms/RAM? |
| Generative vs encoder | LFM2.5-Encoder-230M/350M (classification roles: tool-router, privacy, failure-classifier) | encoder may win on narrow classification [Provider claim] — measure |
| Prompt-only vs LoRA | base GGUF + few-shot vs TRL/LoRA SFT artifact | does training beat the §3.2 delta gate? |
| Quantization | Q6_K (PTQ) vs QAD-Q4_0 | speed vs F1 drift |
| Baselines | deterministic regex extractor, BM25-only retrieval | sometimes the "model" loses to the baseline — record it |

Report as a single markdown table: role × model × {validity, conformance, F1/acc, p95 latency, RAM}. No training entry before this table exists.

---

## 9. Recommended implementation path

1. **P7.0 (now)** — this blueprint filed; operator ratifies gates, roles, and the PII-opt-in rules.
2. **P7.1a** — dataset builder for `privacy-sentinel` + `tool-router` first (tightest schemas, fastest gold, lowest PII risk). Target 300 rows each.
3. **P7.1b** — `extractor` + `well-curator` dataset build + sentinel pass; teacher drafts with LFM2.5-1.2B/2.6B-Extract; ≥10% human audit.
4. **P7.1c** — runner v0: sequential Ollama calls, JSON-schema validation, markdown report. No concurrency yet.
5. **P7.1d** — E0-scale gauntlet: 2 roles × 2 models × 100 cases. Decide train/no-train on gates.
6. **P7.1e** — only on gate failure: TRL/PEFT/LoRA pilot (`~/WanderGround/.venv-lfm`), merge → GGUF → Ollama Modelfile → re-run gauntlet on the served artifact.
7. **P7.2–P7.4** — well-curator pilot, encoder-vs-generative A/B, specialist registry + Modelfile factory, per ROADMAP.

---

## 10. Ethical & privacy handling rules

1. **Local-only by default.** All dataset building, teacher labeling, and serving on Node 1 / Node 0. No unsanitized text to free Zen models (they collect prompt data) or any external API. Paid zero-retention teacher only if local capacity is insufficient, and only post-redaction. [ZDR rule from WANDERGROUND_SPEC §10.4]
2. **Opt-in for sensitive sources.** Open WebUI exports, personal messages, and anything outside the repo require explicit operator consent per batch.
3. **No secrets in git.** Raw datasets, raw model outputs, and transcripts stay in `~/WanderGround/datasets/sms/` (gitignored). Committed artifacts = manifests (hashed, redacted), scoring code, aggregate metrics, and redacted failure examples.
4. **Sentinel before teacher, sentinel after teacher.** Both directions scanned; any leak blocks the batch and is logged as an incident.
5. **No biometric/identity inference.** The privacy-sentinel role detects PII for redaction; it must not classify or profile the operator beyond the allowlisted types in §2.4.
6. **Retention & deletion.** Dataset versions are append-only manifests; deletion of a source file triggers `mempalace_sync`-style pruning of derived rows (same orphan-cleanup discipline).
7. **Attribution.** Any adopted weights, datasets, or failure-example fixtures carry source + license (LFM Open License v1.0 attribution) in the OMER card.

---

## 11. Open questions for the operator

1. **Gold-label budget**: who audits the ≥10% human-audit sample — operator, or a second sovereign agent with a fixed rubric? (Proposed: operator for extractor/curator; deterministic rules suffice for router/privacy/dispatcher.)
2. **Teacher choice**: LFM2.5-1.2B-Extract (local, already on disk?) vs LFM2.5-2.6B (local, ~21 t/s) vs paid-ZDR frontier. Proposed default: local 2.6B, frontier only on disagreement.
3. **Concurrency target**: runner concurrency 1 (deterministic, slower) vs 2 (faster, RAM risk). Proposed: 1 for scoring runs, 2 for throughput runs with a RAM watchdog.
4. **`empress-lens`**: keep in P7.1 or drop pending rater-consensus feasibility (§2.5)?
5. **Where does `~/WanderGround/datasets/sms/` live** — confirm path convention and disk quota; datasets will be ~hundreds of MB text-class.
6. **Do we include `failure-classifier` as a scored role in P7.1**, or only as runner-internal tooling (§3.3)?
7. **Split by `source_file` bucket** — confirm acceptable leakage profile (windows from the same long session co-located in train only, never split).

---

*Filed 2026-10-08 by researcher_humboldt. This is a blueprint: no code, no training, no committed raw data. Next measurement action: operator ratification, then P7.1a dataset build for `privacy-sentinel` and `tool-router`.*
