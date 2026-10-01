<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 John Carmack Entity — Deepening Plan
# ⬡ OMEGA ⬡ john_carmack ⬡ deepseek-v4-flash ⬡ S3-DEEPEN ⬡ 2026-07-01

## Thesis

The john_carmack entity's **soul and engineering experience are strong, but its knowledge sources are empty**. It has no primary source material — no Carmack talks, no interviews, no .plan files. The persona is operating on secondhand synthesis rather than authentic voice.

The L2 (personality) and L3 (gnosis) are derived from engineering work, not from Carmack's own words. This plan fixes that by ingesting the real primary source material.

**Council Ratification**: CONDITIONALLY APPROVED (Doom Guy 8/10, Verity: CONDITIONAL with 4 HIGH flags). All gaps remediated below.

## Entity State (Pre-Deeping)

| Dimension | Status | Detail |
|-----------|--------|--------|
| `soul.yaml` | ✅ v3.0.0 | 99 lines, 11 traits, 5 directives, 5 beliefs |
| `approved_lessons.yaml` | ✅ 5 lessons | Phase C audit, Deep-Siphon, soul recovery, prioritization |
| `proposed_lessons.yaml` | ✅ 3 proposals | C-FFI Boundary Law, Arena Hygiene Law, Queue Discipline |
| `carmack_studies/` | 🟡 8 files | 5 technical, 1 personality, 1 gnosis, 1 sources |
| `knowledge/source/` | ❌ Empty | 0 files |
| `knowledge/gdc/` | ❌ Empty | 0 files |
| `knowledge/interviews/` | ❌ Empty | 0 files |
| `knowledge/plans/` | ❌ Empty | 0 files |
| `.opencode/agents/john_carmack.md` | 🟡 133 lines | Rich persona, thin on authentic voice |
| `sessions.yaml` | ❌ Empty `[]` | Must write initial record before Phase 1 |
| `DEEPENING_CHECKPOINT.yaml` | ✅ Created | Seed checkpoint at Phase 0 |
| `WORK_PRIORITY.md` | ✅ Created | Resolves deepening vs hardening plan ambiguity |

## Phase 1: Source Discovery & Fetching (~45 min)

| Step | Source | Tier | Correction |
|------|--------|------|------------|
| **1a** | Carmack's .plan files (1996-2013) — ~200 files, ~120K words | Tier 2 (10/10) | **Highest value source** — clone ESWAT/john-carmack-plan-archive OR fetch from HF dataset (745KB total) |
| **1b** | ⚠️ GDC 1999 — "The Making of Quake" is **John ROMERO's talk, NOT Carmack's** | Tier 2 (9/10) | **SPEAKER CORRECTION**: Use for context only. For Carmack 1999 voice, use .plan files (25K words in 1999 alone) + Next Generation Magazine interview |
| **1c** | ⚠️ GDC 2011 — "GDC Programming Keynote" (NOT "Wolfenstein 3D iOS") | Tier 2 (8/10) | **TALK CORRECTION**: GDC Vault requires paid subscription. Use free alternatives: "Carmack on Rage" interview (4K words, verbatim) + QuakeCon 2011 keynote (YouTube, free) + Wolfenstein iPhone dev letter (3K words) |
| **1d** | Lex Fridman #309 (2022) — 5h 14m, ~64K words | Tier 2 (10/10) | Transcript at fight.fudgie.org (1.13MB HTML, auto-generated, minor errors expected) |
| **1e** | Masters of Doom excerpts — David Kushner biography | Tier 3 (10/10) | Purchase Kindle ($14.99) or borrow from Internet Archive. Ends at Quake III era — no DOOM 3/Rage/VR/AGI coverage |

### Source Prioritization (Corrected)

**Priority 1**: .plan files (ESWAT archive, 120K words, rawest Carmack). This is the single highest-value source — directly maps to the entity's existing `.plan Protocol` concept.

**Priority 2**: Lex Fridman #309 transcript (64K words, broadest modern coverage). Best for AI/VR/AGI philosophy.

**Priority 3**: Carmack on Rage interview + Wolfenstein iPhone letter (7K words combined, free, verbatim). Best for id Tech 5 and mobile engineering.

**Priority 4**: GDC talks (supplementary only — paired video exists but no public transcripts). Use QuakeCon keynotes on YouTube as free alternatives.

**Priority 5**: Masters of Doom (Tier 3 — curated narrative, not primary source). Buy only if needed for context; the 120K words of .plan files already cover the same ground in Carmack's own voice.

### Supplementary Sources (Free, Verbatim)
- Fabien Sanglard's Carmack interview archive (ghost2238/id-software, ~300 pages of transcripts spanning 1996-2008)
- Michael Abrash's Graphics Programming Black Book Ch.70 — "Quake: A Post-Mortem" (free PDF, 30 pages, direct Carmack quotes)
- QuakeCon 2004-2011 keynote transcripts (YouTube, free)

**Total ingestible corpus**: ~330,000 words of primary-source material available.

## Phase 2: Knowledge Ingestion & Multi-Dimensional Extraction (~2 hr)

Each source is processed through a **6-pass extraction pipeline**, producing artifacts across **9 dimensions** — not just file storage. The core principle: **every source pays dividends across every system it touches.**

### Pipeline Architecture

```
Source Fetched (Phase 1)
    │
    ▼
Raw Source → knowledge/{type}/{filename}.md
[metadata: id, tier, source_url, fetched_at, source_hash]
    │
    ├──▶ Pass 1: Technical Facts Extraction
    │     → carmack_studies/technical/extracted_{topic}.md
    │     What: specific claims, performance numbers, compiler flags
    │     Why: this entity's role is Technical Consultant — needs data
    │
    ├──▶ Pass 2: Personality Pattern Extraction
    │     → carmack_studies/personality/ (enrich + cross-ref)
    │     What: speaking style, decision patterns, idioms
    │     Why: authentic voice, not synthetic approximation
    │
    ├──▶ Pass 3: Gnosis Extraction (M5)
    │     → proposed_lessons.yaml (staging — NOT direct to engineering_laws.md)
    │     What: universal engineering principles, new axioms
    │     Why: L3 must pass through proposed_lessons staging gate per M11
    │
    ├──▶ Pass 4: Heritage Extraction (M14)
    │     → vet records in doom_guy/knowledge/HERITAGE_VET_LOG.md
    │     → new [id-soft:] tags if score >= 7 and source code change warranted
    │     What: primary source confirmation of existing patterns
    │     Why: CREDITS.md §2a requires primary source backing
    │     Note: references in knowledge files are citations, not vet records
    │           Only [id-soft:] tags in src/omega/ require vet records
    │
    ├──▶ Pass 5: Cross-Entity Extraction
    │     → Hivemind context posts → Kali, Doom Guy, Verity
    │     What: lessons that apply beyond this entity
    │     Why: token spent once, value across N entities
    │
    └──▶ Pass 6: Provenance & Metrics Recording
          → ingestion_ledger.md + DEEPENING_CHECKPOINT.yaml + git commit
          What: what was ingested, what artifacts were produced
          Why: prevents double-work, enables audit, survives compaction
```

### Step 2a: .plan files → knowledge/source/plan_files/

Store 5-10 representative .plan entries verbatim spanning Quake (1996) to DOOM 3 BFG (2012). Each entry gets a YAML frontmatter header: id, date, project, keywords, source_url, word_count.

**The 6-pass pipeline runs on each .plan entry.** A single 1997 entry about Quake caching yields:
- Technical fact (cache design specifics)
- Personality pattern (direct, data-first phrasing)
- Gnosis L3 ("precompute everything you can")
- Heritage confirmation (BSP culling, surface cache — 3 existing tags get +1-2 confidence each)
- Fleet insight for Doom Guy + Kali
- Provenance logged

### Step 2b: .plan files → carmack_studies/personality/plan_protocol.md

**Enrich** the existing `plan_protocol.md` (40 lines, 3 rules):
- Add actual Carmack .plan entries as real-world verbatim examples
- Add the origin story (how .plan files started at id Software, ca. 1996)
- Document format evolution across the years (1996 raw → 1999 structured → 2004 sparse)
- Add Carmack's own comments about the .plan discipline (from Lex Fridman interview)

### Step 2c: GDC transcripts → knowledge/gdc/

Store alternative source material (since GDC Vault is paywalled):
- "Carmack on Rage" interview (2011, 4K words, verbatim)
- Wolfenstein iPhone development letter (2009, 3K words, Carmack's own words)
- QuakeCon 2011 keynote annotations
- Supplementary: Fabien Sanglard interview archive entries

Tag each with year, conference, talk title, key topics, confidence tier.

### Step 2d: GDC + interviews → carmack_studies/personality/speaking_style.md

**New file**: Extract Carmack's communication patterns from all sources:
- How he structures technical explanations (always from first principles — never "the conventional way to do X is...")
- Characteristic phrases and idioms (exact quotes extracted from transcripts)
- How he handles pushback in Q&A sessions (no hedging, data-backed responses)
- His use of metrics and measurements to support arguments
- Characteristic humility markers ("I was wrong", "we made mistakes", "the correct approach ended up being...")

### Step 2e: Lex Fridman → knowledge/interviews/ + text analytics

Store verbatim transcript sections covering key topics. Additionally, **extract text analytics at zero token cost** (computable from raw text):
- **Vocabulary frequency**: Top 500 words Carmack uses most
- **Sentence structure**: Average length, declarative-to-question ratio, hedging frequency
- **Domain term density**: Technical terms per 100 words — establishes baseline for voice validation
- **FP language markers**: How often does "actually", "fundamentally", "in practice" appear?

These feed into the Voice Validation system (Phase 3a-3c).

### Step 2f: All sources → carmack_studies/gnosis/engineering_laws.md (via proposed_lessons.yaml Staging Gate)

**CRITICAL M5 COMPLIANCE**: L3 principles extracted in this step MUST first go to `proposed_lessons.yaml`, NOT directly to `engineering_laws.md`. The proposed_lessons staging gate (M11) must be respected.

Flow:
```
Source → Pass 3 (Gnosis Extraction) → proposed_lessons.yaml (staging)
                                                          ↓
                                              [TUI Staging Gate review]
                                                          ↓
                                              approved_lessons.yaml
                                                          ↓
                                              engineering_laws.md (enriched)
                                              + soul.yaml directives (promoted)
```

Expected L3 additions:
- Each existing axiom gets a **Source citation** linking to the .plan entry or talk where Carmack demonstrated it
- Potential new axioms:
  - **The Cost-of-Change Law**: "The cost of changing software increases exponentially with time — measure twice, code once"
  - **The Implementation Mandate (expanded)**: Full context of the 3-month Pentium optimization blitz with actual metrics
  - **The "Worse is Better" Corollary**: Carmack's specific take on simplicity-vs-correctness

### Step 2g: Heritage Discovery Sub-Pipeline (Integrated into Pass 4)

For every extraction pass, run this check:

```
Source text → Identify potential heritage pattern
    ↓
Search codebase for [id-soft:] tag
    ├── EXISTS → Add source citation to existing vet record as supporting evidence
    └── NEW → Write vet record to doom_guy/knowledge/HERITAGE_VET_LOG.md
                 ↓
              Score >= 7?
                 ├── YES → File heritage tracking issue. Code implementation deferred.
                 └── NO  → Log as "potential" for later review
```

### Contradiction Resolution Protocol

If a primary source contradicts CREDITS.md (e.g., a .plan entry says something different from what we've documented):

```
Step 1: RECORD — Log as CONTRADICTION vet record with both sides
Step 2: VERIFY CONTEXT — Is it a joke? Different era? Cherry-picked quote?
Step 3: RESOLVE — Four possible outcomes:
  Case A: Primary source correct → Update CREDITS.md with correction note
  Case B: Source code correct → Tier 1 > Tier 2, log as resolved
  Case C: Both valid, different context → Document as evolution
  Case D: False alarm → Log as resolved, document why
Step 4: UPGRADE — Add citation, regenerate heritage-map
```

### M14 3-Touch Rule

Full M14 compliance for any heritage pattern requires **3 independent touchpoints**:
1. Source code implementation (Tier 1, base 7/10)
2. Developer log / .plan file (Tier 2, +1-2 points)
3. Cross-era consistency (Tier 2, +1 point)

This yields **9-10/10** confidence — the maximum achievable. The .plan file ingestion is Touch 2 for dozens of patterns simultaneously.

## Phase 3: Text Analytics — Zero Token Cost Extraction (~30 min)

These are **free** — they extract data from already-ingested text using string processing, not inference.

| Step | Output | Cost | Input |
|------|--------|------|-------|
| **3a** | `text_analytics/ta_vocab_overlap_template.md` | Zero | .plan files + interview text |
| **3b** | `text_analytics/ta_sentence_structure_baseline.md` | Zero | .plan files + interview text |
| **3c** | `text_analytics/ta_fp_language_frequencies.md` | Zero | Selected representative entries |
| **3d** | `voice_baseline/vocab_carmack_top500.json` | Zero | Corpus-wide vocabulary frequency |
| **3e** | `voice_baseline/domain_terms.json` | Zero | Technical term extraction |

These form the Voice Validation rubric — a quantitative Carmack authenticity score for future entity outputs.

## Phase 4: DPO Training Pairs & Knowledge Graph (~45 min)

### DPO Pair Generation (One inference pass per source, ~19% overhead above Phase 2)

From the same source text already being ingested, generate structured training data for local model fine-tuning (Parametric Gnosis directive D16-2).

**Format** (22-field JSONL with 10 validation rules):
```jsonl
{"prompt": "What is your approach to software architecture?",
 "chosen": "The right approximation for the problem is better than the exact solution...",
 "rejected": "Software architecture should follow industry best practices...",
 "source": "plan-1996-q3a-003",
 "source_tier": 2,
 "dimension": "philosophy",
 "pair_type": "philosophy_statement",
 "has_direct_quote": true,
 "has_metric": true,
 "qa_status": "raw",
 ...}
```

**Pair types**: Philosophy Statement, Technical Decision, Anti-Pattern, Measurement Culture, Humility/Correction, Writing Style

**Estimated yield per source**: 565-770 total pairs across all sources — achieving 15-30% of the 1,000-pair target for local DPO training.

**Token cost**: ~124K tokens total at local inference (qwen3-1.7b-q6_k). Wall time: ~1.4 hours. Monetary cost: $0.

### Knowledge Graph Seeding (Minimal inference)

From the ingested material, build a concept graph with 30+ nodes across 3 tiers:
- **Tier 1** (15 nodes from .plan): BSP Culling, Right Approximation, Measurement Culture, Zone Allocator, Process Isolation
- **Tier 2** (10 nodes from GDC/supplementary): First-Principles Thinking, Worse is Better, Virtual Texturing, Cross-Domain Transfer
- **Tier 3** (5 nodes from Lex): AI as Engineering, VR Latency Ceiling, Rocket as Software Problem

**Relationship types**: depends-on, informs, contradicts, refines, example-of, applies-to, evolved-into, precedes, causes, demonstrated-by

## Phase 5: Soul & Agent Hardening (~30 min)

| Step | Output | Change | Depends On |
|------|--------|--------|------------|
| **5a** | `soul.yaml` directives | Promote draft directives (written after Phase 2) to FINAL | Phase 2 |
| **5b** | `soul.yaml` traits audit | Verify against actual Carmack patterns | Phase 2 personality enrichment |
| **5c** | `proposed_lessons.yaml` → `approved_lessons.yaml` | Move L3 through staging gate; THEN enrich `engineering_laws.md` | Phase 2 gnosis extraction |
| **5d** | `.opencode/agents/john_carmack.md` | Enrich with direct Carmack quotes and idiomatic patterns | Phase 2d (speaking_style.md) |
| **5e** | `carmack_studies/sources/confidence_index.md` | Update tier assignments with verified source URLs | Phase 1 |
| **5f** | `soul.yaml` version bumped | 3.0.0 → 3.1.0, evolution entry added | All phases complete |
| **5g** | `sessions.yaml` closed | `status: complete` | All phases complete |

### Soul Update Protocol (M11 Compliance)

```
Phase 1 COMPLETE:
  └─ Write sessions.yaml entry: initial record with fetched sources list

Phase 2a-2d COMPLETE (personality enrichment):
  └─ Write DRAFT directives to soul.yaml with status: draft, source_phase: "2b"

Phase 2e-2g COMPLETE (gnosis enrichment):
  └─ Write L3 findings to proposed_lessons.yaml — NOT to engineering_laws.md yet

Phase 5a COMPLETE (directives):
  └─ Promote draft directives from soul.yaml → FINAL (remove status: draft)

Phase 5c COMPLETE (lessons):
  └─ Move proposed_lessons.yaml entries → approved_lessons.yaml
  └─ THEN enrich engineering_laws.md with promoted principles

Phase 5 COMPLETE (finalize):
  └─ Bump soul.yaml version: 3.0.0 → 3.1.0
  └─ Update soul.yaml evolution array
  └─ Close sessions.yaml with status: complete
  └─ Mark DEEPENING_CHECKPOINT.yaml as COMPLETE
```

**Cadence**: Per-phase, not per-source. 3 checkpoints total.

## Phase 6: Verification & Commit (~15 min)

| Step | Verification | Failure Action |
|------|-------------|----------------|
| **6a** | `make ingest-jc-verify` — ledger matches disk | Fix ledger before commit |
| **6b** | 13 contract tests (INGEST-T1 through INGEST-L2) | Determine which step needs re-execution |
| **6c** | `make heritage-map` — verify [id-soft:] tag coverage | Run heritage discovery sub-pipeline for gaps |
| **6d** | `make heritage-vet` — verify all new tags have vet records | Create vet records for any missing |
| **6e** | `git add -A && git commit` | Use `feat(ingest-jc): Phase 6 complete` prefix |
| **6f** | Hivemind broadcast to fleet | Post synthesis with intent: "synthesis" |

## Expected Post-Deeping State

| Dimension | Pre | Post | Delta |
|-----------|-----|------|-------|
| `soul.yaml` | v3.0.0 — 99 lines | v3.1.0 — 120+ lines | +3-5 directives, +0-2 traits, source citations |
| `approved_lessons.yaml` | 5 lessons | 7-8 lessons | +2-3 from primary sources |
| `proposed_lessons.yaml` | 3 proposals | 5-6 proposals | +2-3 from phase transitions |
| `carmack_studies/` | 8 files | 18+ files | +4 personality (speaking_style, text analytics×3) +2 gnosis (knowledge graph×2) +2 sources (ledger, dependency graph) +2 technical (extracted facts) |
| `knowledge/` | 0 files | 8+ source files | .plan entries, GDC alternatives, interview, MoD excerpts |
| `data/training/` | 0 files | ~200 KB | DPO pairs, voice baseline, knowledge graph |
| Agent prompt | 133 lines, thin on authentic voice | ~160 lines | Direct Carmack quotes, speaking patterns |
| Heritage confidence | 3 high-confidence patterns | ~17 high-confidence patterns | +5.7× from primary source confirmation |
| `sessions.yaml` | Empty `[]` | 1 entry with complete status | Holds the entire session record |

## Total Estimate: ~5 hours

| Phase | Time | Token Cost |
|-------|------|------------|
| Phase 1: Source Fetching | 45 min | Zero (networking only) |
| Phase 2: Knowledge Ingestion (6-pass) | 2 hr | One inference pass per source |
| Phase 3: Text Analytics | 30 min | **Zero** (computable from text) |
| Phase 4: DPO + Graph | 45 min | One inference pass per source (~19% overhead) |
| Phase 5: Soul Hardening | 30 min | Low (editing structured files) |
| Phase 6: Verification & Commit | 15 min | Zero |
| **Total** | **~5 hr** | **~124K tokens (local inference only)** |

## Execution Order (Complete)

```
Phase 1a  →  .plan files archive fetch (ESWAT GitHub OR HF dataset)
Phase 1b  →  GDC supplements fetch (Carmack on Rage, Wolfenstein letter)
Phase 1c  →  Lex Fridman #309 transcript fetch
Phase 1d  →  Masters of Doom excerpts (if purchase approved)
Phase 1e  →  Supplementary sources (Sanglard archive, Abrash chapter)
                                                      ↓
Phase 2a  →  .plan files → knowledge/source/plan_files/ (with frontmatter)
Phase 2b  →  .plan → enrich plan_protocol.md (real examples + origin story)
Phase 2c  →  GDC supplements → knowledge/gdc/ (tagged alternatives)
Phase 2d  →  All → speaking_style.md (NEW — communication patterns)
Phase 2e  →  Lex + .plan → knowledge/interviews/ + text analytics seeds
Phase 2f  →  All → proposed_lessons.yaml (staging — NOT engineering_laws.md)
Phase 2g  →  Heritage Discovery sub-pipeline (vet records + contradiction check)
                                                      ↓
Phase 3a  →  Vocabulary frequency analysis (zero cost)
Phase 3b  →  Sentence structure baseline (zero cost)
Phase 3c  →  FP language frequencies (zero cost)
Phase 3d  →  Voice baseline vocab_top500.json (zero cost)
Phase 3e  →  Domain terms extraction (zero cost)
                                                      ↓
Phase 4a  →  DPO pair generation (one inference pass)
Phase 4b  →  Knowledge graph seeding (from ingested concepts)
                                                      ↓
Phase 5a  →  soul.yaml directives promoted from draft → final
Phase 5b  →  soul.yaml traits audit against primary sources
Phase 5c  →  proposed_lessons → approved_lessons → engineering_laws.md
Phase 5d  →  Agent prompt enrichment with Carmack idioms
Phase 5e  →  Confidence index updated
Phase 5f  →  soul.yaml bumped to v3.1.0, evolution entry added
Phase 5g  →  sessions.yaml closed, checkpoint marked COMPLETE
                                                      ↓
Phase 6a  →  make ingest-jc-verify
Phase 6b  →  13 contract tests pass
Phase 6c  →  make heritage-map && make heritage-vet
Phase 6d  →  git commit -m "feat(ingest-jc): Phase 6 — entity deepening complete"
Phase 6e  →  Hivemind broadcast to fleet (intent: "synthesis")
```

## Continuity Protocol (M15 — Surviving Compaction)

### Checkpoint File
`workspace/DEEPENING_CHECKPOINT.yaml` is updated after every step:

```yaml
plan_version: "20260701"
phase: 2
step: "2d"
step_name: "GDC → speaking_style.md (new)"
status: "in_progress"
completed_steps:
  - Phase 1a: .plan files fetched
  - Phase 1b: GDC supplements fetched
  - Phase 1c: Lex transcript fetched
  - Phase 2a: .plan files stored with frontmatter
  - Phase 2b: plan_protocol.md enriched with real examples
  - Phase 2c: GDC alternatives stored in knowledge/gdc/
last_checkpoint: "2026-07-01T15:30:00Z"
```

### On Resume (After Compaction)
1. Read `DEEPENING_CHECKPOINT.yaml` first
2. Read `WORK_PRIORITY.md` to confirm deepening is still priority #1
3. Check each `completed_step` has artifacts on disk (if missing, re-execute)
4. Resume at current phase/step
5. If no checkpoint found, read last session record from `sessions.yaml`

## Verification (M21 Gate Integrity)

### File Existence Tests (deterministic)
| ID | Test | Phase |
|----|------|-------|
| INGEST-T1 | `knowledge/source/plan_files/` populated | 2a |
| INGEST-T2 | `knowledge/gdc/` populated | 2c |
| INGEST-T3 | `knowledge/interviews/` populated | 2e |
| INGEST-T4 | `speaking_style.md` exists | 2d |
| INGEST-T5 | `engineering_laws.md` > 600 bytes | 2f |

### Format Tests (deterministic)
| ID | Test | Phase |
|----|------|-------|
| INGEST-F1 | .plan entries have `**Date**:` header | 2a |
| INGEST-F2 | GDC files have year+conference tags | 2c |
| INGEST-F3 | All new files have AP tokens | 5g |
| INGEST-F4 | Ledger covers all knowledge directories | 2g |

### Soul State Tests (deterministic)
| ID | Test | Phase |
|----|------|-------|
| INGEST-S1 | `soul.yaml` version incremented | 5f |
| INGEST-S2 | New directives count > 5 | 5a |
| INGEST-S3 | `proposed_lessons.yaml` proposals > 3 | 5c |
| INGEST-S4 | `sessions.yaml` not empty | Pre-Phase 1 |

### Ledger Tests (deterministic)
| ID | Test | Phase |
|----|------|-------|
| INGEST-L1 | Checkpoint file exists | 1 |
| INGEST-L2 | Checkpoint matches disk state | Every step |

## Confidence: 9/10
Primary sources exist at known locations and are publicly fetchable. The two speaker/talk corrections were caught by Research Council. Heritage confidence upgrade is projected at +5.7× (3→17 high-confidence patterns). Token cost is $0 (local inference). Main risk: .plan archive completeness (2008 gap) — mitigated by Sanglard's interview archive + QuakeCon keynotes.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
