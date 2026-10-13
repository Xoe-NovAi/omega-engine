<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# Encoder Specialist Evaluation Spec — 2026-10-09

**Entity:** Lilith-N1
**Track:** P7.3 — Encoder vs Generative A/B
**Status:** ACTIVE (New Priority)

---

## 1. Background & Rationale

**Pivot Trigger**: Phase 2 (2026-10-08) demonstrated **echo collapse** on generative LFM2.5 230M/350M:
- Few-shot exemplars buy output shape but sell content (`copy_suspect=true`, distinct output ratio 0.083)
- Only 3/20 outputs mutated under paraphrase probe (invariance, not collapse)
- Well-curator exact-match 0.852 < 0.898 constant predictor floor
- Tool-router regressed on more data (0.136 vs 0.242 majority floor)
- Failure-classifier 0.056 vs 0.444 majority floor

**Conclusion**: Autoregressive generative models at ≤350M parameters **cannot** perform extraction/classification/sentinel tasks via few-shot or LoRA. The attention pattern fundamentally mismatches the task structure.

**Solution**: Encoder architectures (bidirectional attention, no autoregressive generation) are native to:
- Sequence classification (`tool_router`, `failure_classifier`)
- Token classification / span extraction (`privacy_sentinel`, `mempalace_extractor`)
- Zero-shot / few-shot without generation collapse

---

## 2. Candidate Models

| Model | Params | Type | Source | Notes |
|-------|--------|------|--------|-------|
| `LFM2.5-Encoder-230M` | 230M | Encoder | Liquid AI | Matryoshka dims, native 1024 |
| `LFM2.5-Encoder-350M` | 350M | Encoder | Liquid AI | Matryoshka dims, native 1024 |
| `ModernBERT-base` | 149M | Encoder | Answer.AI / MLX | SOTA bidirectional, 8192 ctx |
| `ModernBERT-large` | 395M | Encoder | Answer.AI / MLX | Larger capacity |
| `LFM2.5-350M` (generative) | 350M | Generative | Liquid AI | **Control — expected to fail** |

---

## 3. Evaluation Tasks

### 3.1 Tool Router (Sequence Classification)
- **Input**: User prompt + available tool schemas
- **Output**: Tool name + confidence, or `no_tool`
- **Dataset**: 500 held-out prompts from `scripts/sms/datasets/` + synthetic adversarial
- **Metric**: Top-1 accuracy, macro F1, latency (p95)

### 3.2 Privacy Sentinel (Token Classification / Span Extraction)
- **Input**: Raw transcript / text
- **Output**: PII spans (PERSON, EMAIL, PHONE, ADDRESS, API_KEY, SECRET) with BIO tags
- **Dataset**: 200 redacted transcripts from Well + synthetic injection
- **Metric**: Span F1 (exact + partial), entity-level F1, false positive rate

### 3.3 Failure Classifier (Sequence Classification)
- **Input**: Tool execution result + context
- **Output**: Failure class (TRUNCATION, MALFORMED_JSON, HTTP_TIMEOUT, DROPPED_KEY, SUCCESS)
- **Dataset**: 300 deliberate probe runs (from `scripts/sms/gauntlet.py --inject-failure`)
- **Metric**: Per-class F1, macro F1, confusion matrix

### 3.4 MemPalace Extractor (Span Extraction)
- **Input**: Raw session transcript
- **Output**: AAAK memory cards (session, gate, state, lesson, ★ rating)
- **Dataset**: 100 human-annotated sessions from Well corpus
- **Metric**: Card-level exact match, field-level F1, schema conformance

---

## 4. Evaluation Protocol

### 4.1 Data Splits
| Split | Ratio | Purpose |
|-------|-------|---------|
| Train | 60% | Fine-tuning (if LoRA) / few-shot selection |
| Val | 20% | Hyperparameter selection |
| Test | 20% | **Final reported metrics — frozen** |

### 4.2 Fine-Tuning Protocol (if applicable)
| Parameter | Value |
|-----------|-------|
| Method | LoRA (r=16, alpha=32, dropout=0.1) |
| Target modules | `q_proj`, `v_proj`, `k_proj`, `o_proj` |
| Optimizer | AdamW, lr=2e-4, weight_decay=0.01 |
| Scheduler | Cosine with 10% warmup |
| Epochs | 3 (early stopping on val loss) |
| Batch size | 16 (gradient accumulation 4) |
| Precision | BF16 (CPU) / FP16 (if GPU) |

### 4.3 Few-Shot Protocol (prompt-only baseline)
- N=4 exemplars per class (diverse: spanning kinds/domains/tags)
- `copy_suspect` gate: distinct_output_ratio > 0.35 required
- Paraphrase invariance: ≥50% outputs mutate under rewrite

---

## 5. Acceptance Gates

| Task | Metric | Gate | Rationale |
|------|--------|------|-----------|
| Tool Router | Top-1 Acc | ≥ 0.90 | Production routing reliability |
| Tool Router | Macro F1 | ≥ 0.85 | Balanced across tools |
| Privacy Sentinel | Span F1 | ≥ 0.80 | PII detection must be high recall |
| Privacy Sentinel | FP Rate | ≤ 0.05 | Low false alarms |
| Failure Classifier | Macro F1 | ≥ 0.75 | 4-class balanced |
| MemPalace Extractor | Card Exact | ≥ 0.70 | Schema-valid cards |
| All | Latency p95 | ≤ 50ms (CPU) | Real-time requirement |

**Overall Gate**: At least **3 of 4 tasks** must pass gates for model to graduate to `docs/models/specialists/`.

---

## 6. Infrastructure

| Component | Path |
|-----------|------|
| Evaluation harness | `scripts/sms/gauntlet.py` (extended for encoder) |
| Dataset capture | `scripts/sms/capture_real_dataset.py` |
| Paraphrase probe | `scripts/sms/paraphrase_probe.py` |
| Encoder inference | `transformers` + `onnxruntime` (CPU) |
| Results schema | `scripts/sms/schemas/encoder_eval.schema.json` |

---

## 7. Timeline

| Milestone | Target | Status (2026-10-13) |
|-----------|--------|---|
| Encoder models pulled & ONNX exported | 2026-10-10 | **WEIGHTS DONE** (fp32 via direct transformers; ONNX export not done — transformers direct inference used per §8 fallback) |
| Dataset preparation complete | 2026-10-11 | **GAP** — spec's 500-prompt tool_router set never built; real-data capture (8 train/12 holdout) used instead, flagged insufficient |
| Baseline few-shot eval (no training) | 2026-10-12 | **DONE** — see `ENCODER_BASELINE_RESULTS_20261013.md`. FC: both encoders 0.964 acc / 0.955 macro-F1 vs generative 0.111. Pivot validated. Latency gate FAILS at fp32 (176.8 / 398.6 ms p95 vs ≤50) — quantization is the next gate. |
| LoRA fine-tuning runs | 2026-10-13 to 2026-10-15 | PENDING (blocked on quantized latency measurement) |
| Final test set evaluation | 2026-10-16 | PENDING |
| OMER card + decision | 2026-10-17 | PENDING |

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Encoder models not on Ollama | High | Medium | Use `transformers` + ONNXRuntime direct inference |
| ModernBERT too large for 16GB | Medium | High | Quantize to INT8/INT4; test 230M first |
| Dataset skew (35/36 `keep` in curator) | High | High | Adversarial supersession pairs required |
| LoRA on encoder unstable | Medium | Medium | Use proven PEFT configs; monitor gradient norm |

---

## 9. Archival Note

Generative phase artifacts archived to:
```
archive/sms_phase1_20261008/
├── scripts/sms/ (generative gauntlet)
├── datasets/sms/ (synthetic + real)
├── LFM25_SMS_E0_RESULTS_20261008.md
├── LFM25_SMS_GAUNTLET_SMOKE_20261008.md
├── LFM25_SMS_REAL_DATASET_20261008.md
├── LFM25_SMS_PHASE2_ECHO_DECOMPOSITION_20261008.md
└── README.md (explains echo-collapse findings)
```

---

*⬡ OMEGA ⬡ P7.3-ENCODER-EVAL ⬡ 2026-10-09 ⬡*