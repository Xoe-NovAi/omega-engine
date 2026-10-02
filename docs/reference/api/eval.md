# 🔱 Eval — Sovereign Evaluation Pipeline
**AP Token**: `AP-EVAL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Eval package — RAGAS + calibrated LLM-as-Judge evaluation pipeline (S2).
**Tags**: eval, ragas, llm-as-judge, calibration, evaluation, sovereignty
**Cross-references**: src/omega/eval/check.py, src/omega/eval/runner.py, src/omega/eval/calibrate.py, src/omega/research/schema.py

---

## Overview

The `eval` package implements the **Sovereign Eval Pipeline** — a two-component evaluation system:

1. **RAGAS** — Reference-free RAG evaluation (faithfulness, answer relevance, context precision/recall)
2. **Calibrated LLM-as-Judge (S2)** — Isotonic regression calibrated judge for CLEAR scoring (ECE 0.18 → 0.06)

This is the **S2** (Sovereign Tier 2) evaluation layer in the Omega Engine's validation stack.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Eval Package                            │
├─────────────────────────────────────────────────────────────┤
│  check.py            │  RAGAS metric implementations        │
│  runner.py           │  Evaluation orchestration            │
│  calibrate.py        │  Isotonic regression calibration     │
│  __init__.py         │  Package exports                     │
└─────────────────────────────────────────────────────────────┘
```

**Integration**: Used by `AMFOEvaluator` (research) and `CalibratedJudge` (schema) for tiered fidelity evaluation.

---

## Components

### 1. RAGAS Metrics (check.py)

Reference-free RAG evaluation metrics.

#### Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| `faithfulness` | Answer grounded in context | 0.0-1.0 |
| `answer_relevance` | Answer addresses query | 0.0-1.0 |
| `context_precision` | Relevant context ranked high | 0.0-1.0 |
| `context_recall` | All relevant context retrieved | 0.0-1.0 |

#### Usage

```python
from omega.eval.check import (
    faithfulness_score,
    answer_relevance_score,
    context_precision_score,
    context_recall_score
)

# Faithfulness: does answer contradict context?
score = faithfulness_score(
    question="What is the Engine-Stack Firewall?",
    answer="It separates engine core from stack content.",
    contexts=["The Engine-Stack Firewall (M2) prevents stack logic in src/omega/..."]
)

# Answer relevance
score = answer_relevance_score(
    question="What is a WAD?",
    answer="A WAD is a content package format from id Software.",
    contexts=["WAD stands for Where's All Data..."]
)
```

---

### 2. Evaluation Runner (runner.py)

Orchestrates evaluation runs across datasets.

#### EvaluationRunner

```python
from omega.eval.runner import EvaluationRunner

runner = EvaluationRunner(
    metrics=["faithfulness", "answer_relevance", "context_precision", "context_recall"],
    judge_model="qwen3-4b-thinking-q4_k_m",  # Local judge
    batch_size=10
)

# Run on dataset
results = await runner.run(dataset_path="data/eval/rag_testset.jsonl")

# Results
print(f"Faithfulness: {results['faithfulness']['mean']:.3f}")
print(f"Answer Relevance: {results['answer_relevance']['mean']:.3f}")
```

#### Dataset Format (JSONL)

```jsonl
{"question": "What is M2?", "answer": "Engine-Stack Firewall", "contexts": ["M2 prevents..."], "ground_truth": "M2 separates engine from stacks"}
{"question": "What is a WAD?", "answer": "Content package", "contexts": ["WAD system from id Software..."], "ground_truth": "WAD = Where's All Data"}
```

---

### 3. Calibration (calibrate.py)

Isotonic regression calibration for LLM judge scores.

#### CalibratedJudge

```python
from omega.eval.calibrate import CalibratedJudge
from omega.research.schema import CLEARScore

judge = CalibratedJudge(model="qwen3-4b-thinking-q4_k_m")

# Calibrate with oracle labels (raw_score, oracle_score)
oracle_labels = [
    (0.9, 0.95), (0.7, 0.72), (0.5, 0.55), (0.3, 0.35), (0.1, 0.15)
]
judge.calibrate(oracle_labels)

# Apply calibration
raw = CLEARScore(0.8, 0.7, 0.6, 0.5, 0.4)
calibrated = judge.judge(raw)
# Each dimension calibrated independently
```

#### Calibration Process

1. Collect **250 oracle labels** (raw judge score, oracle score)
2. Fit `sklearn.isotonic.IsotonicRegression(out_of_bounds="clip")`
3. Apply to each CLEAR dimension independently
4. **Result**: ECE reduced from 0.18 → 0.06

#### Judge Model

- **Model**: `qwen3-4b-thinking-q4_k_m` (local, M7)
- **Prompt**: Structured CLEAR dimension scoring
- **Output**: JSON with 5 dimension scores (0.0-1.0)

---

## CLEAR Scorecard Integration

The eval package feeds the **CLEAR-Pareto Sovereignty Scorecard** (5 dimensions):

| Dimension | Eval Source | Description |
|-----------|-------------|-------------|
| **C**ost Efficiency | RAGAS + token tracking | USD per insight (lower better) |
| **L**ocal-First Ratio | Provider provenance (M22) | Local inference % |
| **E**pistemic Rigor | RAGAS faithfulness + citations | Verification depth |
| **A**dversarial Robustness | Red-team survival rate | Attack resistance |
| **R**eproducibility | Deterministic re-run success | Consistency |

---

## Usage Example

```python
from omega.eval import EvaluationRunner
from omega.eval.calibrate import CalibratedJudge
from omega.research.schema import CLEARScore, AMFOEvaluator

# 1. Run RAGAS evaluation
runner = EvaluationRunner(
    metrics=["faithfulness", "answer_relevance", "context_precision", "context_recall"],
    judge_model="qwen3-4b-thinking-q4_k_m"
)
ragas_results = await runner.run("data/eval/rag_testset.jsonl")

# 2. Calibrate judge
judge = CalibratedJudge(model="qwen3-4b-thinking-q4_k_m")
judge.calibrate(oracle_labels)  # 250 labels

# 3. Use in AMFO evaluation
amfo = AMFOEvaluator(oracle_summon=oracle_summon, judge=judge)
eval_result = await amfo.evaluate(proposal)

# 4. Access calibrated CLEAR scores
print(f"Final CLEAR: {eval_result.final_clear}")
# CLEARScore(C=0.82, L=0.91, E=0.78, A=0.65, R=0.88)
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async via `anyio` |
| **M7 Local-First** | Judge model runs locally (`qwen3-4b-thinking-q4_k_m`) |
| **M11 Soul Integrity** | Calibration labels from oracle sessions |
| **M13 Temple-Grade** | Calibration reduces ECE; deterministic re-runs |
| **M17 Cognitive Integrity** | Causal trace IDs on all eval runs |
| **M21 Contract Tests** | `assert_*` helpers for type validation |
| **M22 Response Provenance** | Judge `provider_name` recorded |
| **M23 Failure Integrity** | Timeouts = hard failures; no soft-failures |

---

## Testing

```bash
pytest tests/test_eval_check.py tests/test_eval_runner.py tests/test_eval_calibrate.py -v
```

Key test scenarios:
- RAGAS metric accuracy on known datasets
- Calibration reduces ECE
- Judge output parsing
- AMFO tier integration
- Contract test helpers

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ EVAL-v1.0.0 ⬡ 2026-10-02 ⬡*