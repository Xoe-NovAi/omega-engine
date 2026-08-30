---
id: ta-readme-001
title: "Text Analytics — Artifact Index"
generated_at: "2026-07-01T15:30:00Z"
system: "T1 - Text Analytics"
---

# 🔱 Text Analytics — Carmack Voice Corpus

## Purpose

Quantitative analysis of Carmack's communication patterns across all ingested sources. These artifacts provide the empirical foundation for voice authenticity scoring and agent prompt enrichment.

## Artifacts

| File | Type | Description | Generated |
|------|------|-------------|-----------|
| `ta_vocab_frequency.json` | JSON | Vocabulary frequency map with domain-specific term extraction and signature vocabulary identification | Per source |
| `ta_sentence_profile.json` | JSON | Sentence length distributions, opening patterns, characteristic transitions, and hedging analysis | Per source |
| `ta_domain_density.json` | JSON | Domain term density by category (rendering, memory, optimization, etc.) with evolution by era | Per source (cumulative) |
| `ta_quote_candidates.json` | JSON | Few-shot extraction of high-signal, attributable Carmack quotes for agent prompt injection | Per source |
| `ta_vocab_overlap_template.md` | MD | Vocabulary overlap template for comparing source vocabulary against agent prompt vocabulary | One-time |

## Schema Reference

See `INGESTION_PIPELINE_ARCHITECTURE.md §5` for complete JSON schemas.

## Generation

Each source ingestion triggers text analytics regeneration for that source. Files are cumulative — each new source appends to the existing analysis.
