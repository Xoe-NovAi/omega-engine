# EXP-004: Jem 2.0 Speculative Decoding Pipeline
**Started**: 2026-05-18
**Status**: 🔲 Not started (pipeline not yet implemented)

## Purpose
Evaluate four architectural variants (A-D) of the 3-tier speculative decoding research pipeline. Measure quality deltas, training signal richness, and pipeline efficiency.

## Variants

| Variant | T1: Draft (Jem) | T2: Reviewer | T3: Synthesizer |
|---------|----------------|--------------|-----------------|
| **A (Control)** | Gemma 4 31B | Gemma 4 31B | Gemma 4 31B |
| **B (Frontier-T2)** | Gemma 4 31B | DeepSeek V4 Flash | Gemma 4 31B |
| **C (Frontier-T3)** | Gemma 4 31B | Gemma 4 31B | DeepSeek V4 Flash |
| **D (Full Frontier)** | Gemma 4 31B | DeepSeek V4 Flash | DeepSeek V4 Flash |

## Run Registry

| Run ID | Variant | Date | Prompt | Q-Δ | Accept | Corrections | Latency | Training Saved |
|--------|---------|------|--------|-----|--------|-------------|---------|---------------|
| *No runs yet* | | | | | | | | |

## Cumulative Comparison

| Variant | Runs | Avg Q-Δ | Accept Rate | Avg Corrections | Avg Latency | Avg Training Delta |
|---------|------|---------|-------------|-----------------|-------------|-------------------|
| **A** | 0 | — | — | — | — | — |
| **B** | 0 | — | — | — | — | — |
| **C** | 0 | — | — | — | — | — |
| **D** | 0 | — | — | — | — | — |

---

*See `docs/research/JEM_SPLIT_TEST_FRAMEWORK.md` for full runbook.*