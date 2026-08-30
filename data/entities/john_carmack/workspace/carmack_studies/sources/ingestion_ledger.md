---
id: il-ledger-001
title: "John Carmack Entity — Ingestion Ledger"
generated_at: "2026-07-01T16:05:00Z"
total_sources: 3
total_artifacts: 0
pipeline_version: "1.0.0"
status: "fetching"
---

# 🔱 Ingestion Ledger — John Carmack

## Source Registry

| # | Source ID | File | Tier | Status | Date | Artifacts | ROI |
|---|-----------|------|------|--------|------|-----------|-----|
| 1 | `int-2009-wolf-001` | `knowledge/gdc/supplementary/2009_wolfenstein_iphone_letter.md` | 2 | ingested | 2009-03-26 | 0 | - |
| 2 | `int-2011-rage-001` | `knowledge/gdc/supplementary/2011_carmack_on_rage_interview.md` | 2 | ingested | 2011-08-19 | 0 | - |
| 3 | `int-2022-lex-001` | `knowledge/interviews/2022_lex_fridman_309_carmack.md` | 2 | processing | 2022-08-04 | 0 | - |

## Artifact Count per Dimension

| Dimension | Location | Artifact Count |
|-----------|----------|---------------:|
| 1 - Text Analytics | `carmack_studies/personality/text_analytics/` | 0 |
| 2 - Voice Baseline | `carmack_studies/personality/voice_baseline/` | 0 |
| 3 - Knowledge Graph | `carmack_studies/gnosis/knowledge_graph/` | 0 |
| 4 - Source Gnosis | `carmack_studies/gnosis/` (enriched laws) | 0 |
| 5 - DPO Training | `data/training/entities/john_carmack/` | 0 |
| **Total** | | **0** |

## ROI Calculation

ROI = (unique_concepts_extracted × artifact_completeness) / ingestion_effort_hours

| Source | Concepts | Artifacts | Hours | ROI |
|--------|---------:|----------:|------:|----:|

## Batch History

| Batch | Date | Sources | Artifacts | Commit |
|-------|------|---------|-----------|--------|
| 1 | 2026-07-01 | 3 | 0 | pending |

---
*Pipeline initialized: 2026-07-01. Phase 1 in progress.*
