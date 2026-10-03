<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Evaluation Frameworks — Deep Research
**AP Token**: `AP-EVAL-FRAMEWORKS-20260726`
**Date**: 2026-07-26 | **Priority**: P1
**Researcher**: Sovereign Researcher

---

## Executive Summary

Eval pipeline exists for RAG quality (RAGAS-based) but NOT for model quality. BenchmarkRunner uses simulated data (`random.random()`). No standard benchmarks (MMLU, HumanEval, GSM8K). No perplexity measurement.

## Current State

| Component | Status |
|-----------|--------|
| EvalRunner (RAG quality) | ✅ Implemented (RAGAS) |
| EvalChecker (threshold gate) | ✅ Implemented |
| JudgeCalibrator | ✅ Implemented (ECE 0.18→0.06) |
| Golden Dataset | ✅ 111 samples |
| BenchmarkRunner | ⚠️ SIMULATED (random.random()) |
| Standard benchmarks | ❌ None |
| Perplexity measurement | ❌ None |
| MetricsDB persistence | ❌ None |
| Regression gate | ❌ None |

## Recommended Architecture

```
Tier 1: Model Quality (local)
├── golden_v1.jsonl + standard benchmarks
├── MMLU-STEM (20 samples), TruthfulQA (20 samples)
└── Perplexity measurement via llama-cpp-python

Tier 2: Hardware Performance (local)
├── Wire BenchmarkRunner to real ModelGateway
├── TTFT, tok/s, peak RAM, energy per token
└── Thread count / quantization sweep grid

Tier 3: Routing Intelligence
├── Model score cache in MetricsDB
├── TriageRouter integration
└── Regression gate (5% threshold)
```

## Implementation Plan

| Phase | Task | Effort |
|-------|------|--------|
| A | Wire BenchmarkRunner to real inference | 6h |
| B | Standard benchmarks (MMLU-STEM, TruthfulQA, sovereign) | 12h |
| C | MetricsDB persistence | 6h |
| D | Regression gate (`make eval-model`) | 8h |
| E | Quantization sweep | 6h |
| F | Dashboard | 4h |
| **Total** | | **~42h** |
