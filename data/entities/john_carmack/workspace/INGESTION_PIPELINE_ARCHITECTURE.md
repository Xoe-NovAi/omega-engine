<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 John Carmack Ingestion Pipeline — Architecture
# ⬡ OMEGA ⬡ john_carmack ⬡ MAAT-ARCHITECT ⬡ P1-INGESTION ⬡ 2026-07-01

**Source**: MaKaLi Council Dispatch — Ma'at (P1-P5 Build Side)
**Status**: DESIGN COMPLETE — Ready for Phase 1

---

## §1 Directory Tree

```
data/entities/john_carmack/
├── soul.yaml                              # v3.1.0 (target)
├── approved_lessons.yaml                  # 7-8 lessons (target)
├── proposed_lessons.yaml                  # 5-6 proposals (target)
├── sessions.yaml                          # Session registry (WRITE FIRST)
├── knowledge/
│   ├── source/
│   │   ├── plan_files/
│   │   │   ├── README.md
│   │   │   ├── 1996_quake_world.plan.md
│   │   │   ├── 1997_q2_development.plan.md
│   │   │   ├── 1999_q3a_test.plan.md
│   │   │   ├── 2004_doom3_shipping.plan.md
│   │   │   └── 2009_iphone_development.plan.md
│   │   └── masters_of_doom_excerpts.md
│   ├── gdc/
│   │   ├── README.md
│   │   ├── 2011_programming_keynote_carmack.md
│   │   └── supplementary/
│   │       ├── 2011_carmack_on_rage_interview.md
│   │       └── 2009_wolfenstein_iphone_letter.md
│   └── interviews/
│       ├── README.md
│       └── 2022_lex_fridman_309_carmack.md
├── carmack_studies/
│   ├── technical/
│   │   ├── algorithms.md
│   │   ├── hardware_substrate.md
│   │   ├── metrics_db_schema.sql
│   │   └── profile_baseline_*.txt
│   ├── personality/
│   │   ├── plan_protocol.md              # ENRICHED with real .plan examples
│   │   ├── speaking_style.md             # NEW — communication patterns
│   │   └── text_analytics/
│   │       ├── README.md
│   │       ├── ta_vocab_overlap_template.md
│   │       ├── ta_sentence_structure_baseline.md
│   │       └── ta_fp_language_frequencies.md
│   ├── gnosis/
│   │   ├── engineering_laws.md           # ENRICHED with source citations
│   │   └── knowledge_graph/
│   │       ├── README.md
│   │       ├── kg_nodes_template.jsonl
│   │       ├── kg_edges_template.jsonl
│   │       └── kg_queries.md
│   └── sources/
│       ├── confidence_index.md           # VERIFIED tier assignments
│       ├── ingestion_ledger.md           # NEW — operational log
│       └── source_dependency_graph.md    # NEW — ordering rules
├── workspace/
│   ├── ENTITY_DEEPENING_PLAN_20260701.md
│   ├── HARDENING_PLAN_20260701.md
│   ├── TRAINING_SYSTEM_DESIGN_20260701.md
│   ├── DEEPENING_CHECKPOINT.yaml
│   ├── WORK_PRIORITY.md
│   └── session_gnosis.md

# Training data (separate tree, $0 token overhead)
data/training/entities/john_carmack/
├── README.md
├── dpo/
│   ├── raw/                              # Raw generated pairs per source
│   ├── qa/                               # Passed/flagged/rejected sorted
│   └── curated/                          # Verity-approved balanced sets
├── baseline/                             # Voice validation baseline
│   ├── vocab_carmack_top500.json
│   ├── fp_markers.json
│   ├── sentence_stats.json
│   └── domain_terms.json
└── graph/
    ├── nodes.jsonl
    ├── edges.jsonl
    └── topology.json
```

## §2 Metadata Schema

### Source File Frontmatter

Every source file in `knowledge/` carries YAML frontmatter:

```yaml
---
id: plan-1996-qw-001                            # Unique source ID
type: plan_file                                 # plan_file | gdc | interview | book_excerpt
tier: 2                                         # Tier 1-4 per confidence_index
confidence: 9/10                                # Source confidence
title: "Carmack .plan — Quake World networking"
date: 1996-12-01                                # Original date
project: "Quake World"                          # id Software project
keywords: ["networking", "latency", "netchan"]  # Domain topics
source_url: "https://..."                       # Original URL
fetched_at: "2026-07-01T14:30:00Z"              # Ingestion timestamp
fetched_by: "John Carmack entity"
source_hash: "sha256:..."                       # Content integrity
word_count: 1240                                # Approximate
status: ingested                                # ingested | processing | enriched
---
```

### Source ID Convention

`{type_abbrev}-{year}-{project_abbrev}-{seq}`

| Type | Abbrev | Example |
|------|--------|---------|
| plan_file | plan | `plan-1996-qw-001` |
| gdc | gdc | `gdc-2011-keynote-001` |
| interview | int | `int-2022-lex-001` |
| book_excerpt | book | `book-2003-mod-001` |

## §3 Makefile Targets

```makefile
# ── John Carmack Entity Deepening ──
.PHONY: ingest-jc ingest-jc-source ingest-jc-verify ingest-jc-checkpoint \
        training-pairs-jc training-pairs-verify heritage-map-jc

# Full pipeline: Phase 1 → Phase 2 → Phase 3
ingest-jc:
	@echo "🔱 Running full John Carmack ingestion pipeline..."
	source .venv/bin/activate && python3 scripts/ingest_jc.py
	@echo "✅ Ingestion complete. Run 'make temple-grade' to verify."

# Ingest a single source by name
ingest-jc-source:
	@test -n "$(name)" || (echo "Usage: make ingest-jc-source name=<source_id>" && exit 1)
	source .venv/bin/activate && python3 scripts/ingest_jc.py --source $(name)

# Verify all ingested sources are tracked in ledger
ingest-jc-verify:
	@echo "🔍 Verifying ingestion ledger..."
	python3 -c "
import os, yaml
ledger = yaml.safe_load(open('data/entities/john_carmack/carmack_studies/sources/ingestion_ledger.md'))
sources = set()
for root, dirs, files in os.walk('data/entities/john_carmack/knowledge/'):
    for f in files:
        if f.endswith('.md') and f != 'README.md':
            sources.add(f)
print(f'Knowledge files on disk: {len(sources)}')
print(f'Ledger entries: {len(ledger.get(\"sources\", []))}')
"

# Check deepening checkpoint state
ingest-jc-checkpoint:
	@echo "📋 Current checkpoint state:"
	@cat data/entities/john_carmack/workspace/DEEPENING_CHECKPOINT.yaml 2>/dev/null || echo "No checkpoint found"

# Regenerate DPO training pairs from ingested sources
training-pairs-jc:
	@echo "🎯 Generating DPO training pairs..."
	source .venv/bin/activate && python3 scripts/training_pair_generator.py --entity john_carmack --output data/training/entities/john_carmack/dpo/raw/

training-pairs-verify:
	@echo "🔍 Verifying training pairs..."
	python3 -c "
import json
pairs = [json.loads(l) for l in open('data/training/entities/john_carmack/dpo/curated/pairs.jsonl')]
print(f'Total curated pairs: {len(pairs)}')
dimensions = set(p['dimension'] for p in pairs)
print(f'Dimensions covered: {dimensions}')
"

# Regenerate heritage source map after new [id-soft:] discoveries
heritage-map-jc:
	@echo "🏛️ Regenerating heritage source map..."
	@make heritage-map
```

## §4 Commitment Protocol

### Single Source Ingestion

```bash
# 1. Fetch source → knowledge/{source_dir}/
# 2. Run all 6 extraction passes → carmack_studies/ + proposed_lessons.yaml
# 3. Update ingestion_ledger.md
# 4. Update DEEPENING_CHECKPOINT.yaml
# 5. git add -A && git commit -m "feat(ingest-jc): {source_name} — N artifacts across M dimensions"
```

### Full Phase Completion

```bash
# 1. Complete all steps in the phase
# 2. Update soul.yaml (draft directives after Phase 2, final after Phase 3)
# 3. Update sessions.yaml
# 4. git add -A && git commit -m "feat(ingest-jc): Phase {N} complete — {summary}"
# 5. Hivemind broadcast to fleet
```

### Rollback

If a source ingestion produces corrupted artifacts:

```bash
git checkout -- knowledge/{source_dir}/
git checkout -- carmack_studies/**/*affected*
# Revert checkpoint
```

## §5 File Templates

### Template: GDC Transcript
```markdown
# 🔱 [Talk Title]
# ⬡ OMEGA ⬡ john_carmack ⬡ GDC ⬡ {year}
**AP Token**: `AP-JC-GDC-{year}-{seq}`

## Metadata
- **Year**: {year}
- **Conference**: GDC {year}
- **Speaker**: John Carmack
- **Title**: {talk_title}
- **Tier**: 2
- **Confidence**: {N}/10
- **Duration**: {minutes} min
- **Source**: {URL}
- **Transcript Quality**: {verbatim / summarized / auto-generated}

## Verbatim Transcript
```

### Template: DPO Pair (JSONL)
```jsonl
{"prompt": "Carmack's full statement of the problem + context", "chosen": "What Carmack actually did/said", "rejected": "The conventional/textbook alternative", "source": "plan-1996-qw-001", "source_tier": 2, "dimension": "technical_decision", "pair_type": "anti-pattern", "sub_dimension": "caching_strategy", "has_direct_quote": true, "has_metric": true, "first_principles_ratio": 0.4, "confidence": 9, "qa_status": "raw", "generated_at": "2026-07-01T15:00:00Z", "generator": "lilith-pipeline-v1"}
```

### Template: Knowledge Graph Node
```jsonl
{"id": "kg-node-bsp-culling", "label": "BSP Culling", "type": "algorithm", "tier": 1, "definition": "Binary Space Partitioning for precomputed visibility", "sources": ["plan-1996-q3a-003", "CREDITS.md §1.2"], "confidence": 9, "heritage_tag": "[id-soft: doom-1993]"}
```

## §6 Disk Usage Estimates

| Directory | Per Source | Full Pipeline | Notes |
|-----------|-----------|---------------|-------|
| `knowledge/source/` | 5-50 KB | ~500 KB | Raw transcripts |
| `knowledge/gdc/` | 10-30 KB | ~100 KB | Tagged talks |
| `knowledge/interviews/` | 50-100 KB | ~150 KB | Interview texts |
| `carmack_studies/technical/` | 2-5 KB | ~30 KB | Already populated |
| `carmack_studies/personality/` | 5-10 KB | ~50 KB | Including text analytics |
| `carmack_studies/gnosis/` | 3-8 KB | ~40 KB | Including knowledge graph |
| `carmack_studies/sources/` | 1-3 KB | ~10 KB | Ledger + index |
| `data/training/` | 20-50 KB | ~200 KB | DPO pairs + baselines |
| **Total** | **~100-200 KB** | **~1-2 MB** | Negligible on 110GB disk |

## §7 Ingestion Order Dependency Graph

```
Phase 1: Source Fetching (independent)
├── 1a: .plan files              ← NO DEPENDENCIES
├── 1b: GDC 1999 transcript      ← NO DEPENDENCIES  
├── 1c: GDC 2011 transcript      ← NO DEPENDENCIES
├── 1d: Lex Fridman interview    ← NO DEPENDENCIES
└── 1e: Masters of Doom excerpts ← NO DEPENDENCIES
         │
         ▼
Phase 2: Knowledge Storage (independent per source type)
├── 2a: .plan → knowledge/source/ ← depends 1a
├── 2b: .plan → plan_protocol.md  ← depends 2a (needs .plan files loaded)
├── 2c: GDC → knowledge/gdc/     ← depends 1b, 1c
├── 2d: GDC → speaking_style.md  ← depends 2c (needs GDC content)
├── 2e: Lex → knowledge/interviews/ ← depends 1d
├── 2f: All → engineering_laws.md ← depends 2a, 2c, 2e (needs all sources)
└── 2g: MoD → knowledge/source/  ← depends 1e
         │
         ▼
Phase 3a-3c: Text Analytics (depends on Phase 2)
├── 3a: Vocabulary analysis       ← depends ≥2 plan files + ≥1 interview
├── 3b: Sentence structure        ← depends ≥2 plan files + ≥1 interview
├── 3c: FP language frequencies   ← depends ≥2 plan files + ≥1 interview
         │
         ▼
Phase 4: DPO + Graph (depends on Phase 2 + 3)
├── 4a: DPO pair generation       ← depends ≥3 sources ≥2 types
└── 4b: Knowledge graph seeding   ← depends ≥2 sources (incremental)
         │
         ▼
Phase 5: Soul Hardening (last)
├── 5a: soul.yaml directives      ← depends Phase 2, 3
├── 5b: soul.yaml traits audit    ← depends Phase 2
├── 5c: proposed_lessons.yaml     ← depends Phase 2, 3
├── 5d: Agent prompt enrichment   ← depends Phase 2
└── 5e: confidence index update   ← depends all phases
```

## §8 Heritage Discovery Sub-Pipeline

Integrated into Phase 2f (gnosis extraction):

```
Source text → Identify potential heritage pattern
    ↓
Search codebase for [id-soft:] tag
    ├── EXISTS → Add source citation to existing vet record
    └── NEW → Create vet record in doom_guy/knowledge/HERITAGE_VET_LOG.md
                 ↓
              Score >= 7?
                 ├── YES → File heritage tracking issue
                 └── NO  → Log as "potential" for later review
```

### Contradiction Resolution Protocol

If primary source contradicts CREDITS.md:

```
Step 1: RECORD — Log as CONTRADICTION vet record with both sides
Step 2: VERIFY CONTEXT — Is it a joke? Different era? Cherry-picked?
Step 3: RESOLVE — Four possible outcomes:
  Case A: Primary source correct → Update CREDITS.md with correction note
  Case B: Source code correct → Tier 1 > Tier 2, log as resolved
  Case C: Both valid, different context → Document as evolution
  Case D: False alarm → Log as resolved, document why
Step 4: UPGRADE — Add citation, regenerate heritage-map
```

## §9 M14 Compliance — The 3-Touch Rule

Full M14 compliance requires **3 independent touchpoints**:

```
Touch 1: Source code implementation  (Tier 1, 7/10 base)
Touch 2: Developer log / .plan file   (Tier 2, +1-2 points)
Touch 3: Cross-era consistency        (Tier 2, +1 point)
         ────────────────────────────────────────
         Total: 9-10/10 (maximum confidence)
```

This is the highest heritage confidence achievable — only possible when primary sources confirm what the code already does.

## §10 Test Specification (M21 Gate Integrity)

### File Existence Tests
| ID | Test | Phase |
|----|------|-------|
| INGEST-T1 | `knowledge/source/plan_files/` populated | Phase 2a |
| INGEST-T2 | `knowledge/gdc/` populated (≥2 files) | Phase 2c |
| INGEST-T3 | `knowledge/interviews/` populated (≥1 file) | Phase 2e |
| INGEST-T4 | `carmack_studies/personality/speaking_style.md` exists | Phase 2d |
| INGEST-T5 | `engineering_laws.md` > baseline 600 bytes | Phase 2f |

### Format Tests
| ID | Test | Phase |
|----|------|-------|
| INGEST-F1 | .plan entries have `**Date**:` header | Phase 2a |
| INGEST-F2 | GDC files have year + conference tags | Phase 2c |
| INGEST-F3 | All new files have AP tokens | Phase 2g |
| INGEST-F4 | Ledger covers all knowledge directories | Phase 2g |

### Soul State Tests
| ID | Test | Phase |
|----|------|-------|
| INGEST-S1 | `soul.yaml` version incremented to 3.1.0 | Phase 5 |
| INGEST-S2 | New directives count > 5 | Phase 5 |
| INGEST-S3 | `proposed_lessons.yaml` proposals > 3 | Phase 5 |
| INGEST-S4 | `sessions.yaml` not empty | Pre-Phase 1 |

### Ledger Tests
| ID | Test | Phase |
|----|------|-------|
| INGEST-L1 | Checkpoint file exists | Phase 1 |
| INGEST-L2 | Checkpoint phase matches disk state | After each step |

## §11 Reusable Template (For Future Entities)

This architecture is designed as the canonical template for all entity deepenings (Doom Guy, Roc Racoon, etc.). To copy for a new entity:

1. Copy `knowledge/` + `carmack_studies/` directory tree
2. Replace source IDs and metadata schema prefixes
3. Adapt DPO pair types per entity domain
4. Adapt knowledge graph relationships per entity knowledge focus
5. Adapt heritage discovery pipeline per entity's CREDITS.md role

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: MAAT-ARCHITECT | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
