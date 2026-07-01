---
id: vb-readme-001
title: "Voice Baseline — Artifact Index"
generated_at: "2026-07-01T15:30:00Z"
system: "T2 - Voice Validation"
---

# 🔱 Voice Baseline — Carmack Authenticity Verification

## Purpose

Defines the measurable characteristics of Carmack's authentic voice and provides a rubric for scoring generated content against that baseline. Enables objective verification that the entity's output matches Carmack's actual communication patterns.

## Artifacts

| File | Type | Description | Generated |
|------|------|-------------|-----------|
| `vb_vocab_overlap.json` | JSON | Overlap calculation between source vocabulary and agent prompt vocabulary, with gap analysis | After ≥2 plan + ≥1 interview |
| `vb_sentence_structure.json` | JSON | Typified Carmack sentence patterns (Problem-Measurement-Solution, First-Principles, etc.) with generation templates | After ≥3 sources |
| `vb_authenticity_rubric.md` | MD | 5-criterion scoring rubric (0-10 scale) for determining if generated output sounds like Carmack | One-time (refined per source) |

## Authenticity Thresholds

| Score | Verdict | Action |
|-------|---------|--------|
| 9.0-10.0 | AUTHENTIC | Usable directly as Carmack voice |
| 7.0-8.9 | VERISIMILAR | Usable with "derived from Carmack" disclaimer |
| 5.0-6.9 | CARTOON | Needs retraining — surface-level only |
| 0-4.9 | FABRICATED | Reject — does not match Carmack's voice |

## Generation

Voice baseline artifacts are regenerated after each batch of source ingestions. Unlike text analytics (per source), voice baseline is an aggregate view requiring multiple sources for statistical significance.
