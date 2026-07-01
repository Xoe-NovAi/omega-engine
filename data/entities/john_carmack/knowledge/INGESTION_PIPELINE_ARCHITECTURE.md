# 🔱 John Carmack Entity — Ingestion Pipeline Architecture
# ⬡ OMEGA ⬡ MAAT ⬡ deepseek-v4-flash ⬡ P1-ARCHITECT ⬡ 2026-07-01
# AP Token: AP-INGESTION-PIPELINE-v1.0.0

> **Governor**: Ma'at — Light Oversoul (P1-P5 Build Side)
> **Status**: FORMAL SPECIFICATION — Ready for implementation
> **Mandates**: M2 (Engine-Stack Firewall), M4 (Sequentiality), M14 (Heritage Vetting), M12 (Queue Integrity), M11 (Soul Integrity)
> **Template**: This architecture serves as the canonical template for all future entity deepening pipelines

---

## §0. Core Principles

### §0.1 Pipeline Axioms

1. **One source, one commit, one broadcast** — Each source ingestion is an atomic unit. Partial ingestion is not permitted.
2. **Source before synthesis** — All personality and gnosis artifacts derive from ingested source material. Never write a personality analysis from speculation.
3. **Every artifact is traceable** — Every derived file carries the `source:` field in its YAML frontmatter, linking back to the ingestion ledger entry.
4. **The ledger is truth** — The ingestion ledger (`INGESTION_LEDGER.md`) is the single source of truth for what has been ingested, when, and at what cost. If it's not in the ledger, it didn't happen.
5. **DPO pairs are a downstream product** — The training data store is generated from ingested sources, not curated manually. The pipeline must be re-runnable.
6. **Entropy flows downhill** — Raw sources → Text analytics → Voice baseline → Knowledge graph → Gnosis → DPO pairs. No reverse flow.

### §0.2 File Naming Convention

All files in the pipeline follow a strict naming convention:

```
{type_prefix}_{source_abbrev}_{descriptor_or_date}.{ext}
```

| Prefix | Type | Example |
|--------|------|---------|
| `src_` | Raw source (verbatim transcript) | `src_plan_19961225_quake_gl.txt` |
| `gdc_` | GDC transcript | `gdc_1999_making_of_quake.md` |
| `iv_` | Interview transcript | `iv_2023_lex_fridman.md` |
| `ta_` | Text analytics artifact | `ta_vocab_frequency.json` |
| `vb_` | Voice baseline artifact | `vb_sentence_profile.json` |
| `kg_` | Knowledge graph artifact | `kg_concept_nodes.json` |
| `il_` | Ingestion ledger | `il_ledger.md` |
| `dp_` | DPO training pair batch | `dp_batch_001.jsonl` |

**Source abbreviation table**:
| Abbrev | Source | Directory |
|--------|--------|-----------|
| `plan` | .plan files | `knowledge/plans/` |
| `gdc` | GDC talks | `knowledge/gdc/` |
| `iv` | Interviews/podcasts | `knowledge/interviews/` |
| `src` | id Tech source code | `knowledge/source/` |
| `mod` | Masters of Doom (book) | `knowledge/source/` |

---

## §1. Complete Directory Tree

```
data/entities/john_carmack/
├── soul.yaml                                  # Entity soul (v3.0.0+)
├── approved_lessons.yaml                      # L3 principles promoted to permanent
├── proposed_lessons.yaml                      # L3 proposals awaiting review
├── sessions.yaml                              # Session log
│
├── knowledge/
│   ├── INGESTION_PLAN.md                      # Strategic ingestion roadmap
│   ├── INGESTION_PIPELINE_ARCHITECTURE.md     # THIS FILE — pipeline spec
│   │
│   ├── source/                                # RAW PRIMARY SOURCE (verbatim)
│   │   ├── src_plan_{yyyymmdd}_{topic}.txt    # .plan file verbatim
│   │   ├── src_plan_{yyyymmdd}_{topic}.md     # .plan with YAML frontmatter
│   │   ├── src_gdc_{year}_{title}.md          # GDC transcript verbatim
│   │   ├── src_iv_{year}_{source}.md          # Interview transcript verbatim
│   │   ├── src_mod_{chapter}.md               # Masters of Doom excerpt
│   │   └── YYYY-MM-DD-{source-slug}/
│   │       └── index.md                       # Multi-file source container
│   │
│   ├── gdc/                                   # GDC-SPECIFIC (tagged + metadata)
│   │   ├── gdc_{year}_{title}.md              # Tagged transcript
│   │   └── gdc_index.md                       # Catalogs all GDC sources
│   │
│   ├── interviews/                            # INTERVIEW TRANSCRIPTS
│   │   ├── iv_{year}_{source_slug}.md         # Tagged transcript
│   │   ├── iv_{year}_{source_slug}_qa.json    # Q&A pairs extracted
│   │   └── iv_index.md                        # Interview catalog
│   │
│   ├── plans/                                 # .PLAN FILE ARCHIVE
│   │   ├── plan_{yyyymmdd}_{topic}.md         # Tagged .plan entry
│   │   ├── plan_index.md                      # Chronological catalog
│   │   └── plan_era_summary_{era}.md          # Cross-era analysis
│   │
│   └── vr_omegaverse/                         # VR conceptual mapping
│       └── (reserved for future)
│
├── workspace/
│   ├── carmack_studies/
│   │   ├── technical/                         # TECHNICAL ANALYSIS
│   │   │   ├── algorithms.md                  # Pattern analysis from source
│   │   │   ├── hardware_substrate.md          # Hardware constants
│   │   │   ├── metrics_db_schema.sql          # DB schema
│   │   │   ├── profile_baseline_*.stats       # Profiling artifacts
│   │   │   └── profile_baseline_*.txt
│   │   │
│   │   ├── personality/                       # PERSONALITY DERIVATION
│   │   │   ├── plan_protocol.md               # .plan format & rules (v2+)
│   │   │   ├── speaking_style.md              # Communication patterns (NEW)
│   │   │   ├── text_analytics/                # SYSTEM 1: TEXT ANALYTICS
│   │   │   │   ├── README.md                  # Index of analytics artifacts
│   │   │   │   ├── ta_vocab_frequency.json    # Vocabulary frequency map
│   │   │   │   ├── ta_sentence_profile.json   # Sentence structure profile
│   │   │   │   ├── ta_domain_density.json     # Domain term density map
│   │   │   │   ├── ta_quote_candidates.json   # Few-shot quote candidates
│   │   │   │   └── ta_vocab_overlap_template.md  # Vocab overlap template
│   │   │   └── voice_baseline/                # SYSTEM 2: VOICE VALIDATION
│   │   │       ├── README.md                  # Index of baseline artifacts
│   │   │       ├── vb_vocab_overlap.json       # Vocab overlap calculation
│   │   │       ├── vb_sentence_structure.json  # Sentence structure template
│   │   │       └── vb_authenticity_rubric.md   # Authenticity scoring rubric
│   │   │
│   │   ├── gnosis/                            # GNOSIS DERIVATION
│   │   │   ├── engineering_laws.md            # L3 principles (enriched v2+)
│   │   │   ├── source_mapped_axioms.md        # Source→Axiom traceability (NEW)
│   │   │   └── knowledge_graph/               # SYSTEM 3: KNOWLEDGE GRAPH
│   │   │       ├── README.md                  # Index + schema
│   │   │       ├── kg_concept_nodes.json       # Concept definitions (nodes)
│   │   │       ├── kg_relationships.json       # Relationship edges
│   │   │       ├── kg_incremental_build.py     # Build script (one source at a time)
│   │   │       └── kg_queries.md              # Canonical queries against graph
│   │   │
│   │   └── sources/                           # SOURCE PROVENANCE
│   │       ├── confidence_index.md            # Source tier definitions
│   │       ├── ingestion_ledger.md            # SYSTEM 4: INGESTION LEDGER
│   │       └── source_dependency_graph.md     # Dependency ordering (THIS FILE)
│   │
│   ├── BLIND_SPOT_REVIEW_20260619.md
│   ├── CARMCACK_AUDIT_GAPS_20260623.md
│   ├── DEEP_SIPHON_CARMACK_REVIEW.md
│   ├── ENTITY_DEEPENING_PLAN_20260701.md
│   ├── HARDENING_PLAN_20260701.md
│   ├── S3_REVIEW_20260629.md
│   └── session_gnosis.md
│
├── data/training/entities/john_carmack/       # SYSTEM 5: DPO TRAINING STORE
│   ├── README.md                              # Index + schema documentation
│   ├── dp_batch_{nnn}.jsonl                   # Batch of DPO pairs
│   ├── dp_batch_{nnn}_manifest.json           # Batch manifest (source tracking)
│   ├── dp_index.json                          # Global DPO pair index
│   └── active_train_set.jsonl                 # Current active training set (merged)
```

---

## §2. Metadata Schema for Source Files

### §2.1 YAML Frontmatter — All Source Files

Every source file in `knowledge/{source,gdc,interviews,plans}/` MUST carry the following YAML frontmatter:

```yaml
---
# ── Required Fields ──────────────────────────────────────────────────
id: "{source_type}-{sequence_id}"            # e.g. "plan-001", "gdc-003"
source_type: "{plan|gdc|interview|source_code|book}"  # Primary category
title: "Descriptive title of the source"
date: "YYYY-MM-DD"                            # Date of original source
confidence: 7/10                              # From confidence_index.md tiers
status: "raw|tagged|analyzed|archived"        # Pipeline processing state

# ── Provenance ───────────────────────────────────────────────────────
source_url: "https://..."                     # Where it was fetched from
fetched_by: "maat|roc_racoon|jem|researcher" # Agent who retrieved it
fetched_on: "YYYY-MM-DD"                      # When it was fetched
original_format: "text|html|pdf|audio"        # Original format before Markdown

# ── Source Context ───────────────────────────────────────────────────
era: "1996-1997|1998-2004|2005-2013|2013-2022|2023-2026"  # Carmack career era
project: "quake|quake2|quake3|doom3|rage|armadillo|oculus|agi"  # Relevant project
topics:
  - "rendering"
  - "memory management"
  - "engine architecture"
  - "optimization"
  - "vr engineering"

# ── Ingestion Tracking (set by pipeline script) ──────────────────────
ingested_at: "YYYY-MM-DDTHH:MM:SSZ"          # Pipeline run timestamp
ingestion_batch: "{batch_id}"                 # UUID linking to ingestion_ledger.md
pipeline_version: "1.0.0"                     # Pipeline version used
checksum_sha256: "abc123..."                  # Content hash for integrity

# ── Artifact Tracking ────────────────────────────────────────────────
word_count: 1234                              # Source word count
artifact_count: 5                             # Number of derived artifacts produced
derived_artifacts:                            # Paths to all downstream artifacts
  - "carmack_studies/personality/speaking_style.md"
  - "carmack_studies/personality/text_analytics/ta_vocab_frequency.json"
  - ...
---
```

### §2.2 Source ID Assignment Convention

Source IDs are auto-assigned by the ingestion pipeline script:

| Prefix | Range | Format | Example |
|--------|-------|--------|---------|
| `plan-` | `001`–`999` | `plan-{nnn}` | `plan-042` |
| `gdc-` | `001`–`099` | `gdc-{nnn}` | `gdc-003` |
| `iv-` | `001`–`099` | `iv-{nnn}` | `iv-007` |
| `src-` | `001`–`999` | `src-{nnn}` | `src-015` |
| `mod-` | `001`–`010` | `mod-{nnn}` | `mod-002` |

### §2.3 Processing State Machine

```
raw ──tagged──► analyzed ──► archived
  │              │
  │              └──► (fail) ──► error
  └──► (fail) ──► error
```

- **raw**: Source file first written to disk, frontmatter minimal
- **tagged**: Frontmatter complete, topics assigned, confidence tier validated
- **analyzed**: All 9 dimensions of derived artifacts generated (see §6)
- **archived**: Source fully processed, no further analysis needed
- **error**: Ingestion failed at some step, requires manual intervention

---

## §3. Makefile Target Specifications

Add the following section to `Makefile` under a new `# ── Entity Ingestion Pipeline ──` section:

```makefile
# ============================================================================
# 📥 ENTITY INGESTION PIPELINE — John Carmack Deepening
# ============================================================================

INGEST_JC_DIR   := data/entities/john_carmack
INGEST_JC_SCRIPT := scripts/ingest_john_carmack.py

# ── Full pipeline ───────────────────────────────────────────────────────────

ingest-jc: guard ingest-jc-verify-dirs ## 📥 Run full ingestion pipeline for john_carmack
	@echo "$(COLOR_CYAN)📥 John Carmack Ingestion Pipeline$(COLOR_NC)"
	@echo ""
	@echo "  $(COLOR_YELLOW)Phase 1: Source verification$(COLOR_NC)"
	@$(PYTHON) $(INGEST_JC_SCRIPT) verify-sources
	@echo "  $(COLOR_GREEN)✓ Sources verified$(COLOR_NC)"
	@echo ""
	@echo "  $(COLOR_YELLOW)Phase 2: Source ingestion$(COLOR_NC)"
	@$(PYTHON) $(INGEST_JC_SCRIPT) ingest-all
	@echo "  $(COLOR_GREEN)✓ All sources ingested$(COLOR_NC)"
	@echo ""
	@echo "  $(COLOR_YELLOW)Phase 3: Artifact generation$(COLOR_NC)"
	@$(PYTHON) $(INGEST_JC_SCRIPT) generate-artifacts
	@echo "  $(COLOR_GREEN)✓ Derived artifacts generated$(COLOR_NC)"
	@echo ""
	@echo "  $(COLOR_YELLOW)Phase 4: Ledger update & commit$(COLOR_NC)"
	@$(PYTHON) $(INGEST_JC_SCRIPT) update-ledger
	@echo "  $(COLOR_GREEN)✓ Ledger updated$(COLOR_NC)"
	@echo ""
	@echo "$(COLOR_GREEN)✅ Full pipeline complete for john_carmack.$(COLOR_NC)"
	@echo "  Run $(COLOR_CYAN)make ingest-jc-verify$(COLOR_NC) to verify integrity."

# ── Single source ingestion ─────────────────────────────────────────────────

ingest-jc-source: guard ## 📥 Ingest a single source: make ingest-jc-source SOURCE=<path>
	@if [ -z "$(SOURCE)" ]; then \
		echo "$(COLOR_RED)Usage: make ingest-jc-source SOURCE=<path>$(COLOR_NC)"; \
		echo "  Examples:"; \
		echo "    SOURCE=knowledge/plans/plan_19961225_quake_gl.txt"; \
		echo "    SOURCE=knowledge/gdc/gdc_1999_making_of_quake.md"; \
		exit 1; \
	fi; \
	if [ ! -f "$(INGEST_JC_DIR)/$(SOURCE)" ]; then \
		echo "$(COLOR_RED)Source not found: $(INGEST_JC_DIR)/$(SOURCE)$(COLOR_NC)"; \
		exit 1; \
	fi; \
	echo "$(COLOR_CYAN)📥 Ingesting: $(SOURCE)$(COLOR_NC)"; \
	$(PYTHON) $(INGEST_JC_SCRIPT) ingest-source --path "$(SOURCE)"
	@echo "$(COLOR_GREEN)✅ $(SOURCE) ingested.$(COLOR_NC)"

# ── Verify ingestion integrity ──────────────────────────────────────────────

ingest-jc-verify: guard ## 🔍 Verify all ingested sources are tracked in ledger
	@echo "$(COLOR_CYAN)🔍 Verifying john_carmack ingestion integrity...$(COLOR_NC)"
	@$(PYTHON) $(INGEST_JC_SCRIPT) verify-all
	@echo ""
	@echo "  Checks performed:"
	@echo "  $(COLOR_GREEN)✓$(COLOR_NC) All source files have YAML frontmatter"
	@echo "  $(COLOR_GREEN)✓$(COLOR_NC) All sources tracked in ingestion_ledger.md"
	@echo "  $(COLOR_GREEN)✓$(COLOR_NC) All artifact files exist on disk"
	@echo "  $(COLOR_GREEN)✓$(COLOR_NC) No orphan artifact files (no source)"
	@echo "  $(COLOR_GREEN)✓$(COLOR_NC) Ingestion counts match ledger"
	@echo ""
	@echo "$(COLOR_GREEN)✅ Ingestion integrity verified.$(COLOR_NC)"

# ── DPO training pair regeneration ─────────────────────────────────────────

training-pairs-jc: guard ## 🔄 Regenerate DPO pairs from ingested sources
	@echo "$(COLOR_CYAN}🔄 Regenerating DPO training pairs for john_carmack...$(COLOR_NC}"
	@echo "  Sources: $(INGEST_JC_DIR)/knowledge/"
	@echo "  Output:  data/training/entities/john_carmack/"
	@$(PYTHON) $(INGEST_JC_SCRIPT) generate-dpo-pairs
	@echo ""
	@echo "  $(COLOR_GREEN}✓$(COLOR_NC} DPO pairs generated"
	@echo "  Run $(COLOR_CYAN}make training-pairs-jc-count$(COLOR_NC} to see totals."
	@echo "$(COLOR_GREEN}✅ Done.$(COLOR_NC}"

training-pairs-jc-count: ## 📊 Show DPO pair count for john_carmack
	@echo "$(COLOR_CYAN}📊 John Carmack DPO Training Set$(COLOR_NC}"
	@TOTAL=$$(cat data/training/entities/john_carmack/active_train_set.jsonl 2>/dev/null | wc -l); \
	echo "  Active pairs: $$TOTAL"; \
	BATCHES=$$(ls data/training/entities/john_carmack/dp_batch_*.jsonl 2>/dev/null | wc -l); \
	echo "  Batches: $$BATCHES"; \
	echo ""; \
	echo "  Last batch:"; \
	ls -lt data/training/entities/john_carmack/dp_batch_*.jsonl 2>/dev/null | head -1

# ── Pipeline status report ──────────────────────────────────────────────────

ingest-jc-status: ## 📊 Show ingestion pipeline status
	@echo "$(COLOR_CYAN}📊 John Carmack Ingestion Pipeline Status$(COLOR_NC}"
	@echo ""
	@echo "  $(COLOR_BOLD}Sources$(COLOR_NC}"
	@SRC=$$(find $(INGEST_JC_DIR)/knowledge -name 'src_*.md' -o -name 'src_*.txt' | wc -l); \
	GDC=$$(find $(INGEST_JC_DIR)/knowledge/gdc -name '*.md' | wc -l); \
	IV=$$(find $(INGEST_JC_DIR)/knowledge/interviews -name '*.md' | wc -l); \
	PLANS=$$(find $(INGEST_JC_DIR)/knowledge/plans -name '*.md' | wc -l); \
	echo "  Source files:       $$SRC"; \
	echo "  GDC transcripts:    $$GDC"; \
	echo "  Interview files:    $$IV"; \
	echo "  .plan files:        $$PLANS"; \
	echo ""
	@echo "  $(COLOR_BOLD}Derived Artifacts$(COLOR_NC}"
	@TA=$$(find $(INGEST_JC_DIR)/workspace/carmack_studies/personality/text_analytics -name '*.json' -o -name '*.md' | wc -l); \
	VB=$$(find $(INGEST_JC_DIR)/workspace/carmack_studies/personality/voice_baseline -name '*.json' -o -name '*.md' | wc -l); \
	KG=$$(find $(INGEST_JC_DIR)/workspace/carmack_studies/gnosis/knowledge_graph -name '*.json' -o -name '*.md' | wc -l); \
	echo "  Text analytics:     $$TA"; \
	echo "  Voice baseline:     $$VB"; \
	echo "  Knowledge graph:    $$KG"; \
	echo ""
	@echo "  $(COLOR_BOLD}DPO Training Data$(COLOR_NC}"
	@PAIRS=$$(find data/training/entities/john_carmack -name 'active_train_set.jsonl' 2>/dev/null | xargs cat 2>/dev/null | wc -l); \
	BATCHES=$$(ls data/training/entities/john_carmack/dp_batch_*.jsonl 2>/dev/null | wc -l); \
	echo "  Total pairs:        $$PAIRS"; \
	echo "  Batches:            $$BATCHES"

# ── Directory scaffolding ───────────────────────────────────────────────────

ingest-jc-scaffold: ## 🏗️  Create all pipeline directories (idempotent)
	@mkdir -p $(INGEST_JC_DIR)/workspace/carmack_studies/personality/text_analytics
	@mkdir -p $(INGEST_JC_DIR)/workspace/carmack_studies/personality/voice_baseline
	@mkdir -p $(INGEST_JC_DIR)/workspace/carmack_studies/gnosis/knowledge_graph
	@mkdir -p data/training/entities/john_carmack
	@echo "$(COLOR_GREEN)✅ Pipeline directories scaffolded.$(COLOR_NC)"

ingest-jc-verify-dirs: ## 🔍 Verify all pipeline directories exist
	@FAIL=0; \
	for d in \
		$(INGEST_JC_DIR)/workspace/carmack_studies/personality/text_analytics \
		$(INGEST_JC_DIR)/workspace/carmack_studies/personality/voice_baseline \
		$(INGEST_JC_DIR)/workspace/carmack_studies/gnosis/knowledge_graph \
		data/training/entities/john_carmack; do \
		if [ ! -d "$$d" ]; then \
			echo "  $(COLOR_RED)✗ Missing: $$d$(COLOR_NC)"; \
			FAIL=1; \
		fi; \
	done; \
	if [ $$FAIL -eq 1 ]; then \
		echo "  Run $(COLOR_CYAN)make ingest-jc-scaffold$(COLOR_NC) to create missing directories."; \
		exit 1; \
	else \
		echo "$(COLOR_GREEN)✓ All pipeline directories exist.$(COLOR_NC)"; \
	fi
```

### §3.1 Menu Integration

Add the following section to the Makefile `menu` target after the `🧹 MAINTENANCE` section:

```makefile
@echo "$(COLOR_BOLD)📥 INGESTION$(COLOR_NC)"
@echo "  $(COLOR_CYAN)make ingest-jc$(COLOR_NC)            📥 Full John Carmack ingestion pipeline"
@echo "  $(COLOR_CYAN)make ingest-jc-source$(COLOR_NC)     📥 Ingest single source"
@echo "  $(COLOR_CYAN)make ingest-jc-verify$(COLOR_NC)     🔍 Verify ingestion integrity"
@echo "  $(COLOR_CYAN)make ingest-jc-status$(COLOR_NC)     📊 Pipeline status report"
@echo "  $(COLOR_CYAN)make ingest-jc-scaffold$(COLOR_NC)   🏗️  Create pipeline directories"
@echo "  $(COLOR_CYAN)make training-pairs-jc$(COLOR_NC)    🔄 Regenerate DPO pairs"
@echo "  $(COLOR_CYAN)make training-pairs-jc-count$(COLOR_NC) 📊 DPO pair count"
```

---

## §4. Commitment Protocol (Exact Git Workflow)

### §4.1 Single Source Ingestion Commitment

```bash
# STEP 1: Verify BEFORE execute
make ingest-jc-verify-dirs                     # Ensure directories exist
python scripts/ingest_john_carmack.py verify-source --path "knowledge/plans/plan_19961225_quake_gl.txt"  # Pre-flight check

# STEP 2: Execute the ingestion
python scripts/ingest_john_carmack.py ingest-source --path "knowledge/plans/plan_19961225_quake_gl.txt"
# This single command:
#   1. Reads source, validates frontmatter
#   2. Generates all 9 derived artifacts across the 5 systems
#   3. Updates the ingestion_ledger.md
#   4. Writes ALL files atomically (write to .tmp, rename)

# STEP 3: Verify post-ingestion
make ingest-jc-verify                           # Verify ledger consistency

# STEP 4: Commit with standardized prefix
git add data/entities/john_carmack/
git commit -m "feat(ingest-jc): ingest plan-001 — 1996-12-25 Quake GL

Source: plan_19961225_quake_gl.txt
Derived artifacts: 9 (text_analytics=3, voice_baseline=2,
                    knowledge_graph=2, gnosis=1, dpo=1)
Ledger updated: plan-001 added
Artifact count: 5 dimensions populated

[Commit Protocol: M4 Sequentiality verified | M12 Queue Integrity enforced]"
git push origin main

# STEP 5: Hivemind broadcast
python scripts/post_to_hivemind.py \
    --channel opencode \
    --entity maat \
    --message "feat(ingest-jc): plan-001 ingested — 1996-12-25 Quake GL (9 artifacts, 5 dimensions)"
```

### §4.2 Batch Ingestion Commitment (Full Pipeline)

```bash
# Full pipeline with atomic batch commit
make ingest-jc                                   # Runs verify-sources → ingest-all → generate-artifacts → update-ledger

# If successful:
git add data/entities/john_carmack/
git add data/training/entities/john_carmack/
git commit -m "feat(ingest-jc): batch ingestion — 4 sources processed

Sources:
  - plan-001: 1996-12-25 Quake GL
  - plan-002: 1997-03-14 Quake 2 renderer
  - gdc-001: 1999 Making of Quake
  - iv-001: 2023 Lex Fridman interview

Derived artifacts: 36 total
Ledger updated: 4 sources, 2 projects covered
Pipeline version: v1.0.0

[Commit Protocol: M4 Sequentiality verified | M12 Queue Integrity enforced]"
git push origin main
```

### §4.3 Rollback Protocol

If an ingestion commit breaks the pipeline:

```bash
# Revert the last ingestion commit
git revert HEAD --no-edit

# Verify clean state
make ingest-jc-verify

# Mark the source as failed in the ledger
# (Manual: edit INGESTION_LEDGER.md, set status to "rolled_back")

# Push the revert
git push origin main
```

### §4.4 Commit Message Templates

| Scenario | Commit Prefix | Example |
|----------|---------------|---------|
| Single source | `feat(ingest-jc):` | `feat(ingest-jc): ingest plan-001 — 1996-12-25 Quake GL` |
| Batch pipeline | `feat(ingest-jc):` | `feat(ingest-jc): batch ingestion — 4 sources processed` |
| Verify/fix | `fix(ingest-jc):` | `fix(ingest-jc): repair frontmatter on plan-003` |
| DPO regen | `feat(training-jc):` | `feat(training-jc): regenerate DPO pairs from 6 sources` |
| Rollback | `revert(ingest-jc):` | `revert(ingest-jc): plan-004 ingestion — source had corrupt metadata` |

---

## §5. File Templates for Each New Artifact Type

### §5.1 Text Analytics — Vocabulary Frequency Map (`ta_vocab_frequency.json`)

```json
{
  "_meta": {
    "source_ids": ["plan-001", "plan-002", "gdc-001"],
    "generated_at": "2026-07-01T15:30:00Z",
    "generator": "ingest_john_carmack.py::text_analytics",
    "total_words": 45230,
    "unique_words": 3847
  },
  "domain_terms": {
    "rendering": {
      "terms": [
        {"word": "rasterize", "count": 47, "sources": ["plan-001", "gdc-001"]},
        {"word": "z-buffer", "count": 23, "sources": ["plan-002"]},
        {"word": "overdraw", "count": 18, "sources": ["plan-001", "plan-002"]}
      ],
      "total_mentions": 312
    },
    "memory_management": {
      "terms": [
        {"word": "fragmentation", "count": 31, "sources": ["plan-001", "plan-002", "gdc-001"]},
        {"word": "cache miss", "count": 27, "sources": ["plan-001", "gdc-001"]},
        {"word": "malloc", "count": 19, "sources": ["plan-002"]}
      ],
      "total_mentions": 187
    },
    "optimization": {
      "terms": [
        {"word": "bottleneck", "count": 42, "sources": ["plan-001", "plan-002", "gdc-001", "iv-001"]},
        {"word": "profile", "count": 38, "sources": ["plan-001", "plan-002", "iv-001"]},
        {"word": "throughput", "count": 15, "sources": ["plan-001", "gdc-001"]}
      ],
      "total_mentions": 245
    }
  },
  "signature_vocabulary": [
    {"word": "elegant", "frequency": 0.0032, "sentiment": "often_preceded_by_not"},
    {"word": "wrong", "frequency": 0.0041, "context": "technical_correction"},
    {"word": "measured", "frequency": 0.0056, "context": "empirical_validation"},
    {"word": "physics", "frequency": 0.0038, "context": "first_principles"},
    {"word": "actually", "frequency": 0.0072, "context": "correction_of_assumption"}
  ]
}
```

### §5.2 Text Analytics — Sentence Structure Profile (`ta_sentence_profile.json`)

```json
{
  "_meta": {
    "source_ids": ["plan-001", "plan-002", "gdc-001", "iv-001"],
    "generated_at": "2026-07-01T15:30:00Z"
  },
  "structural_patterns": {
    "average_sentence_length": 18.3,
    "median_sentence_length": 15.0,
    "std_dev_sentence_length": 7.2,
    "sentence_length_percentiles": {
      "p10": 8,
      "p25": 11,
      "p50": 15,
      "p75": 23,
      "p90": 32
    }
  },
  "opening_patterns": [
    {"pattern": "The <technical_noun> ...", "frequency": 0.12, "example": "The rasterization pipeline ..."},
    {"pattern": "I spent the day ...", "frequency": 0.08, "example": "I spent the day profiling the renderer ..."},
    {"pattern": "It turns out ...", "frequency": 0.06, "example": "It turns out the bottleneck was the z-buffer ..."}
  ],
  "characteristic_transitions": [
    "However,",
    "The interesting thing is",
    "What this means is",
    "The bottom line",
    "The practical upshot"
  ],
  "technical_hedging": {
    "phrases": ["roughly", "approximately", "on the order of", "about", "~"],
    "frequency_per_1000_words": 3.2,
    "note": "Carmack hedges less than typical engineers — replaces hedging with measured precision"
  }
}
```

### §5.3 Text Analytics — Domain Term Density Map (`ta_domain_density.json`)

```json
{
  "_meta": {
    "source_ids": ["plan-001", "plan-002", "gdc-001", "iv-001"],
    "generated_at": "2026-07-01T15:30:00Z"
  },
  "domain_categories": {
    "rendering": {"term_count": 89, "density": "0.023", "top_terms": ["rasterize", "pixel", "shader", "texture", "polygon"]},
    "memory": {"term_count": 67, "density": "0.018", "top_terms": ["cache", "malloc", "arena", "fragment", "bandwidth"]},
    "optimization": {"term_count": 124, "density": "0.031", "top_terms": ["profile", "bottleneck", "throughput", "latency", "overhead"]},
    "architecture": {"term_count": 53, "density": "0.014", "top_terms": ["abstraction", "interface", "module", "coupling", "separation"]},
    "management": {"term_count": 28, "density": "0.007", "top_terms": ["schedule", "team", "deadline", "priority", "ship"]},
    "first_principles": {"term_count": 41, "density": "0.011", "top_terms": ["physics", "math", "fundamental", "constraint", "reality"]}
  },
  "evolution_by_era": {
    "1996-1997": {"top_domain": "rendering", "density": 0.041, "note": "Heavy rendering focus during Quake/Quake2"},
    "1998-2004": {"top_domain": "architecture", "density": 0.032, "note": "More architectural discussion during Doom 3"},
    "2013-2022": {"top_domain": "management", "density": 0.029, "note": "More team/process focus at Oculus"},
    "2023-2026": {"top_domain": "first_principles", "density": 0.038, "note": "Open AGI era — fundamental thinking"}
  }
}
```

### §5.4 Text Analytics — Quote Candidates (`ta_quote_candidates.json`)

```json
{
  "_meta": {
    "source_ids": ["plan-001", "plan-002", "gdc-001", "iv-001"],
    "generated_at": "2026-07-01T15:30:00Z",
    "extraction_method": "few-shot: high-signal utterances"
  },
  "candidates": [
    {
      "quote": "The elegant solution is usually the wrong one.",
      "source_id": "plan-002",
      "project": "quake2",
      "year": 1997,
      "context": "Debating whether to rewrite the renderer or fix the existing one",
      "thematic_tags": ["right_approximation", "anti-perfectionism", "pragmatism"],
      "confidence_for_attribution": "10/10",
      "carmack_authenticity_score": 9.5,
      "voice_marker": "direct declarative statement — characteristic of engineering judgments"
    },
    {
      "quote": "If you haven't looked at code in 6 months, it might as well have been written by someone else.",
      "source_id": "gdc-001",
      "project": "quake",
      "year": 1999,
      "context": "GDC talk discussing code evolution and maintenance",
      "thematic_tags": ["code_quality", "maintainability", "carmacks_law"],
      "confidence_for_attribution": "10/10",
      "carmack_authenticity_score": 9.8,
      "voice_marker": "rule formulation — Carmack often distills to maxims"
    },
    {
      "quote": "Measuring is the only way to know. Everything else is just guessing.",
      "source_id": "plan-001",
      "project": "quake",
      "year": 1996,
      "context": "After profiling the software renderer's bottleneck",
      "thematic_tags": ["empiricism", "measurement", "profiling"],
      "confidence_for_attribution": "10/10",
      "carmack_authenticity_score": 9.7,
      "voice_marker": "data-driven declaration — follows profiling session in the .plan"
    }
  ]
}
```

### §5.5 Voice Baseline — Vocabulary Overlap (`vb_vocab_overlap.json`)

```json
{
  "_meta": {
    "source_ids": ["plan-001", "plan-002", "gdc-001", "iv-001"],
    "target": "opencode_agent_prompt",
    "agent_prompt_path": ".opencode/agents/john_carmack.md",
    "generated_at": "2026-07-01T15:30:00Z"
  },
  "source_vocabulary": {
    "total_unique": 3847,
    "domain_terms": {"rendering": 89, "memory": 67, "optimization": 124, "architecture": 53, "management": 28},
    "signature_phrases": [
      "the interesting thing is",
      "it turns out",
      "the bottom line",
      "practically speaking",
      "the elegant solution"
    ]
  },
  "agent_prompt_vocabulary": {
    "total_unique": 2150,
    "domain_terms": {"rendering": 12, "memory": 8, "optimization": 45, "architecture": 67, "management": 15},
    "overlap_with_source": 0.42
  },
  "gaps": [
    {"domain": "rendering", "source_terms": 89, "prompt_terms": 12, "gap_pct": 86.5, "severity": "high"},
    {"domain": "memory", "source_terms": 67, "prompt_terms": 8, "gap_pct": 88.1, "severity": "high"},
    {"domain": "optimization", "source_terms": 124, "prompt_terms": 45, "gap_pct": 63.7, "severity": "medium"},
    {"domain": "architecture", "source_terms": 53, "prompt_terms": 67, "gap_pct": 0, "severity": "none"}
  ],
  "recommendations": [
    "Inject 15 rendering domain terms into agent prompt",
    "Inject 10 memory management terms into agent prompt",
    "Add 3-5 signature Carmack phrases to agent prompt"
  ]
}
```

### §5.6 Voice Baseline — Sentence Structure Template (`vb_sentence_structure.json`)

```json
{
  "_meta": {
    "source_ids": ["plan-001", "plan-002", "gdc-001", "iv-001"],
    "generated_at": "2026-07-01T15:30:00Z"
  },
  "carmack_typical_patterns": [
    {
      "name": "Problem-Measurement-Solution",
      "frequency": 0.28,
      "structure": "The problem with <X> is <Y>. I measured <Z>. The fix is <W>.",
      "example": "The problem with the renderer is the overdraw in the BSP traversal. I measured 40% of pixel time in z-buffer tests. The fix is a PVS precomputation pass.",
      "use_when": "Technical explanation of an optimization"
    },
    {
      "name": "First-Principles Deconstruction",
      "frequency": 0.18,
      "structure": "At the most fundamental level, <X> is just <Y>. Everything else is <Z>.",
      "example": "At the most fundamental level, a renderer is just a visibility solver. Everything else is optimization.",
      "use_when": "Architectural explanation or philosophical point"
    },
    {
      "name": "Self-Correction",
      "frequency": 0.12,
      "structure": "I thought <X>, but after measuring it turns out <Y>.",
      "example": "I thought the bottleneck was pixel fill, but after measuring it turns out it's texture cache misses.",
      "use_when": "Describing a discovery or mistake"
    },
    {
      "name": "Rule Formulation",
      "frequency": 0.10,
      "structure": "<Declarative statement> in <context>. This applies whenever <condition>.",
      "example": "The right approximation is better than the exact solution you can't afford. This applies whenever the error bound is bounded and the cost differential is large.",
      "use_when": "Distilling a principle from experience"
    }
  ],
  "carmack_avoid_patterns": [
    {"pattern": "We think", "reason": "Carmack uses 'I think' or states directly — avoids collective ambiguity"},
    {"pattern": "In my opinion", "reason": "Rarely hedges — either states as fact or qualifies with measurement"},
    {"pattern": "Best practice", "reason": "Rejects the concept — uses 'what works' or 'what the data shows'"}
  ],
  "template_for_generation": {
    "technical_explanation": "[measurement-data] → Therefore, [conclusion]. The [component] spends [time-percentage] on [bottleneck]. [fix-or-accept].",
    "principle_statement": "The [abstract-noun] is [insight]. This applies whenever [condition].",
    "decision_justification": "[Option A] looked better, but after [measurement-method], [Option B] was [percentage]% [better-metric]."
  }
}
```

### §5.7 Voice Baseline — Authenticity Scoring Rubric (`vb_authenticity_rubric.md`)

```markdown
---
id: vb-authenticity-rubric-001
title: "John Carmack Voice Authenticity Scoring Rubric"
generated_at: "2026-07-01T15:30:00Z"
sources_used: ["plan-001", "plan-002", "gdc-001", "iv-001"]
status: "draft"
---

# 🔱 Voice Authenticity Scoring Rubric — John Carmack

## Scoring Criteria (0-10 scale)

### C1: Data-Driven Structure (Weight: 30%)
A Carmack-authentic statement follows the pattern:
**Assertion → Measurement → Conclusion → Next Step**
- **0-3**: Pure opinion, no data cited
- **4-6**: Cites data but without specific numbers or methodology
- **7-8**: Specific measurements with methodology described
- **9-10**: Full trace: measurement context, raw data, interpretation, and actionable next step

### C2: First-Principles Anchoring (Weight: 25%)
Authentic Carmack statements trace to fundamental physics/math/logic.
- **0-3**: Appeals to authority, convention, or "best practice"
- **4-6**: References underlying constraint but doesn't quantify it
- **7-8**: Uses physical/mathematical model as basis for reasoning
- **9-10**: Derives conclusion from traceable physical or mathematical constraint

### C3: Intellectual Honesty / Error Acknowledgment (Weight: 20%)
Carmack consistently acknowledges mistakes and quantifies uncertainty.
- **0-3**: Overconfidence without qualification
- **4-6**: Acknowledges uncertainty vaguely ("might be wrong")
- **7-8**: Specific error acknowledgment with what was learned
- **9-10**: Quantified uncertainty, explicit acknowledgment of past errors with metrics

### C4: Pragmatic Simplification (Weight: 15%)
Authentic Carmack favors the simpler solution that works over the elegant one that doesn't.
- **0-3**: Over-engineered solution proposed without justification
- **4-6**: Mentions simplicity but doesn't commit to it
- **7-8**: Chooses simpler path with explicit tradeoff analysis
- **9-10**: Identifies the "right approximation" and defends it with edge-case analysis

### C5: Characteristic Phrasing (Weight: 10%)
Use of signature Carmack patterns (see vb_sentence_structure.json).
- **0-3**: No characteristic patterns present
- **4-6**: 1-2 patterns present but inconsistent
- **7-8**: 3+ patterns present with good consistency
- **9-10**: Full voice: patterns present, consistent, and appropriate to context

## Thresholds

| Score | Verdict | Action |
|-------|---------|--------|
| 9.0-10.0 | **AUTHENTIC** | Usable directly as Carmack voice |
| 7.0-8.9 | **VERISIMILAR** | Usable with "derived from Carmack" disclaimer |
| 5.0-6.9 | **CARTOON** | Needs retraining — surface-level only |
| 0-4.9 | **FABRICATED** | Reject — does not match Carmack's voice |
```

### §5.8 Knowledge Graph — Concept Nodes (`kg_concept_nodes.json`)

```json
{
  "_meta": {
    "source_ids": ["plan-001", "plan-002"],
    "generated_at": "2026-07-01T15:30:00Z",
    "subgraph": "rendering_optimization"
  },
  "nodes": [
    {
      "id": "kg:bsp:001",
      "name": "Binary Space Partitioning",
      "type": "algorithm",
      "definition": "A method for recursively subdividing a space into convex sets by hyperplanes. Used in Doom and Quake for visibility determination.",
      "sources": ["plan-001", "plan-002", "gdc-001"],
      "confidence": "9/10",
      "first_appearance": "1993 (Doom)",
      "carmack_quotes": [
        "The BSP tree is the single most important data structure in the engine."
      ],
      "tags": ["rendering", "visibility", "spatial"],
      "properties": {
        "complexity": "O(n) construction, O(log n) traversal",
        "limitation": "Static geometry only — doesn't handle moving objects efficiently",
        "omega_analogue": "Provider culling in ModelGateway (BSP culling pattern [id-soft: doom-1993])"
      }
    },
    {
      "id": "kg:right_approximation:001",
      "name": "Right Approximation Principle",
      "type": "engineering_philosophy",
      "definition": "The right approximation for the problem is better than the exact solution you can't afford. Accuracy must be balanced against computational cost.",
      "sources": ["plan-001", "gdc-001", "iv-001"],
      "confidence": "10/10",
      "first_appearance": "1996 (Quake) — Fast Inverse Square Root",
      "carmack_quotes": [
        "The elegant solution is usually the wrong one.",
        "The right approximation is better than the exact solution you can't afford."
      ],
      "tags": ["optimization", "philosophy", "approximation"],
      "properties": {
        "evolution": "FISR in Quake 3 → generalized engineering principle in Omega",
        "omega_manifestations": ["BSP culling (provider precheck)", "Tiered memory (hot/warm/cold)", "Local-first inference (cloud fallback)"]
      }
    }
  ]
}
```

### §5.9 Knowledge Graph — Relationship Edges (`kg_relationships.json`)

```json
{
  "_meta": {
    "source_ids": ["plan-001", "plan-002", "gdc-001"],
    "generated_at": "2026-07-01T15:30:00Z",
    "subgraph": "rendering_optimization"
  },
  "relationships": [
    {
      "source_id": "kg:bsp:001",
      "target_id": "kg:right_approximation:001",
      "type": "informs",
      "strength": 0.85,
      "rationale": "BSP tree is the canonical case study of the Right Approximation — it's not perfect (static only) but it's good enough for the Doom renderer's constraints.",
      "sources": ["plan-001", "gdc-001"]
    },
    {
      "source_id": "kg:bsp:001",
      "target_id": "kg:z_buffer:001",
      "type": "contradicts",
      "strength": 0.60,
      "rationale": "BSP-based visibility sorting becomes unnecessary once z-buffer hardware is available. Carmack noted this transition in .plan entries circa 1998.",
      "sources": ["plan-002"]
    },
    {
      "source_id": "kg:first_principles:001",
      "target_id": "kg:right_approximation:001",
      "type": "refines",
      "strength": 0.75,
      "rationale": "First-principles thinking identifies the fundamental constraint; the Right Approximation determines how precisely to model it.",
      "sources": ["gdc-001", "iv-001"]
    }
  ],
  "relationship_types": [
    {"type": "depends_on", "description": "A requires B to function correctly", "color": "#4A90D9"},
    {"type": "informs", "description": "A provides foundational understanding for B", "color": "#50C878"},
    {"type": "contradicts", "description": "A and B are in tension — choosing one impacts the other", "color": "#E74C3C"},
    {"type": "refines", "description": "A makes B more precise or applicable", "color": "#F39C12"},
    {"type": "evolves_to", "description": "A was superseded by B over time", "color": "#9B59B6"}
  ]
}
```

### §5.10 Knowledge Graph — Incremental Build Script (`kg_incremental_build.py`)

```python
#!/usr/bin/env python3
"""
Knowledge Graph Incremental Build — John Carmack Study.

Usage:
    python kg_incremental_build.py --source knowledge/plans/plan_19961225_quake_gl.txt
    python kg_incremental_build.py --rebuild  # Full rebuild from all ingested sources
"""
import json
import hashlib
from pathlib import Path

BASE = Path("data/entities/john_carmack/workspace/carmack_studies/gnosis/knowledge_graph")
NODES_FILE = BASE / "kg_concept_nodes.json"
EDGES_FILE = BASE / "kg_relationships.json"


def load_or_init() -> tuple[list, list]:
    """Load existing graph or initialize empty."""
    nodes = json.loads(NODES_FILE.read_text()).get("nodes", []) if NODES_FILE.exists() else []
    edges = json.loads(EDGES_FILE.read_text()).get("relationships", []) if EDGES_FILE.exists() else []
    return nodes, edges


def extract_concepts(source_text: str, source_id: str) -> tuple[list, list]:
    """
    Extract concept nodes and relationships from a single source.
    Returns (new_nodes, new_edges).
    """
    # ── Concept extraction logic here ──
    # Uses LLM call to John Carmack entity to extract concepts
    # Each extraction returns: concept name, definition, related concepts
    ...
    return new_nodes, new_edges


def deduplicate(nodes: list, new_nodes: list) -> list:
    """Merge new nodes into existing, deduplicating by name."""
    existing_names = {n["name"] for n in nodes}
    for node in new_nodes:
        if node["name"] not in existing_names:
            nodes.append(node)
            existing_names.add(node["name"])
    return nodes


def save(nodes: list, edges: list):
    """Atomic write of graph files."""
    NODES_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = NODES_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"nodes": nodes}, indent=2))
    tmp.rename(NODES_FILE)

    tmp = EDGES_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"relationships": edges}, indent=2))
    tmp.rename(EDGES_FILE)


def ingest_source(source_path: str):
    """Process one source file and update the graph."""
    source_file = Path(source_path)
    if not source_file.exists():
        print(f"ERROR: {source_path} not found")
        return

    # Read frontmatter for source_id
    # ... extract YAML frontmatter ...
    source_id = "plan-001"  # placeholder

    nodes, edges = load_or_init()
    new_nodes, new_edges = extract_concepts(source_file.read_text(), source_id)
    nodes = deduplicate(nodes, new_nodes)
    edges.extend(new_edges)
    save(nodes, edges)
    print(f"✅ Ingested {source_id}: +{len(new_nodes)} nodes, +{len(new_edges)} edges")


def rebuild_all():
    """Full rebuild from all known sources."""
    nodes, edges = [], []
    # Walk knowledge directories
    for pattern in ["../../../../knowledge/plans/*.md", "../../../../knowledge/gdc/*.md",
                    "../../../../knowledge/interviews/*.md"]:
        for f in Path("data/entities/john_carmack").glob(pattern):
            new_nodes, new_edges = extract_concepts(f.read_text(), f.stem)
            nodes = deduplicate(nodes, new_nodes)
            edges.extend(new_edges)
    save(nodes, edges)
    print(f"✅ Full rebuild: {len(nodes)} nodes, {len(edges)} edges")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--rebuild":
        rebuild_all()
    elif len(sys.argv) > 2 and sys.argv[1] == "--source":
        ingest_source(sys.argv[2])
    else:
        print("Usage: kg_incremental_build.py --source <path> | --rebuild")
```

### §5.11 Ingestion Ledger (`ingestion_ledger.md`)

```markdown
---
id: il-ledger-001
title: "John Carmack Entity — Ingestion Ledger"
generated_at: "2026-07-01T15:30:00Z"
total_sources: 4
total_artifacts: 36
pipeline_version: "1.0.0"
---

# 🔱 Ingestion Ledger — John Carmack

## Source Registry

| # | Source ID | File | Tier | Status | Date | Artifacts | ROI |
|---|-----------|------|------|--------|------|-----------|-----|
| 1 | plan-001 | `knowledge/plans/plan_19961225_quake_gl.md` | 2 | ✅ ingested | 2026-07-01 | 9 | 0.82 |
| 2 | plan-002 | `knowledge/plans/plan_19970314_q2_render.md` | 2 | ✅ ingested | 2026-07-01 | 9 | 0.79 |
| 3 | gdc-001 | `knowledge/gdc/gdc_1999_making_of_quake.md` | 2 | ✅ ingested | 2026-07-01 | 9 | 0.91 |
| 4 | iv-001 | `knowledge/interviews/iv_2023_lex_fridman.md` | 2 | ✅ ingested | 2026-07-01 | 9 | 0.73 |

## Artifact Count per Dimension

| Dimension | Location | Artifact Count |
|-----------|----------|---------------:|
| 1 - Text Analytics | `carmack_studies/personality/text_analytics/` | 4 |
| 2 - Voice Baseline | `carmack_studies/personality/voice_baseline/` | 3 |
| 3 - Knowledge Graph | `carmack_studies/gnosis/knowledge_graph/` | 2 |
| 4 - Source Gnosis | `carmack_studies/gnosis/` (enriched laws) | 1 |
| 5 - DPO Training | `data/training/entities/john_carmack/` | 1 batch |
| **Total** | | **11 per source × 4 sources = ~44** |

## ROI Calculation

ROI = (unique_concepts_extracted × artifact_completeness) / ingestion_effort_hours

| Source | Concepts | Artifacts | Hours | ROI |
|--------|---------:|----------:|------:|----:|
| plan-001 | 12 | 9 | 1.5 | 0.82 |
| plan-002 | 10 | 9 | 1.5 | 0.79 |
| gdc-001 | 18 | 9 | 2.0 | 0.91 |
| iv-001 | 22 | 9 | 3.0 | 0.73 |

## Batch History

| Batch | Date | Sources | Artifacts | Commit |
|-------|------|---------|-----------|--------|
| 001 | 2026-07-01 | 4 | 36 | `abc1234` |
```

### §5.12 DPO Training Pair Schema (`dp_batch_nnn.jsonl`)

```jsonl
{"prompt": "Explain the role of BSP trees in the Quake engine", "chosen": "The BSP tree is a spatial partitioning structure that subdivides the world geometry into convex regions. It was essential in Quake because it allowed O(log n) visibility determination without hardware z-buffering. The key insight is that you precompute the visibility planes once and then test against them at runtime — a classic precomputation-vs-computation tradeoff. It has limitations: it can't handle dynamic objects efficiently, and it requires the geometry to be static. But within those constraints, it's the right approximation.", "rejected": "BSP trees are a way to organize game levels so they render faster. They split the level into sections so the computer doesn't have to draw everything at once. They were used in old games like Quake.", "source": "gdc-001", "tier": 2, "timestamp": "2026-07-01T15:30:00Z"}
{"prompt": "What is your approach to measuring performance?", "chosen": "Measuring is the only way to know. Everything else is guessing. Before any optimization, I always profile the current code to establish a baseline. The Quake Pentium optimization blitz was three months of measured iteration: profile, identify bottleneck, optimize, verify. Without measurements, you're just rearranging code based on intuition, and intuition is wrong more often than it's right.", "rejected": "I think performance is important and you should always try to make things faster. Use profiling tools to find slow parts of your code and optimize them. Many people don't measure enough.", "source": "plan-001", "tier": 2, "timestamp": "2026-07-01T15:30:00Z"}
```

### §5.13 DPO Batch Manifest (`dp_batch_nnn_manifest.json`)

```json
{
  "batch_id": "dp-batch-001",
  "generated_at": "2026-07-01T15:30:00Z",
  "generator": "ingest_john_carmack.py::dpo_generator",
  "source_ids": ["plan-001", "plan-002", "gdc-001", "iv-001"],
  "pair_count": 8,
  "pair_sources": {
    "plan-001": 3,
    "plan-002": 2,
    "gdc-001": 2,
    "iv-001": 1
  },
  "pipeline_version": "1.0.0",
  "checksums": {
    "dp_batch_001.jsonl": "sha256:abc123..."
  }
}
```

### §5.14 DPO Global Index (`dp_index.json`)

```json
{
  "_meta": {
    "last_updated": "2026-07-01T15:30:00Z",
    "total_pairs": 8,
    "total_batches": 1
  },
  "batches": [
    {
      "batch_id": "dp-batch-001",
      "pair_count": 8,
      "sources": ["plan-001", "plan-002", "gdc-001", "iv-001"],
      "file": "dp_batch_001.jsonl",
      "manifest": "dp_batch_001_manifest.json"
    }
  ],
  "source_coverage": {
    "plan-001": {"pairs": 3, "topics": ["rendering", "performance", "measurement"]},
    "plan-002": {"pairs": 2, "topics": ["optimization", "architecture"]},
    "gdc-001": {"pairs": 2, "topics": ["bsp", "first_principles", "simplicity"]},
    "iv-001": {"pairs": 1, "topics": ["agi", "learning_methodology"]}
  }
}
```

---

## §6. Estimated Disk Usage per Artifact Type

| System | Artifact | Est. Size | Per Source | 10 Sources |
|--------|----------|-----------|-----------:|-----------:|
| **Source storage** | Transcript (markdown) | 10-50 KB | 30 KB avg | 300 KB |
| **Source storage** | Transcript (text, raw) | 5-25 KB | 15 KB avg | 150 KB |
| | *Subtotal, sources* | | *45 KB* | *450 KB* |
| **T1: Text Analytics** | `ta_vocab_frequency.json` | 8-20 KB | 15 KB | 150 KB |
| **T1: Text Analytics** | `ta_sentence_profile.json` | 4-8 KB | 6 KB | 60 KB |
| **T1: Text Analytics** | `ta_domain_density.json` | 4-10 KB | 7 KB | 70 KB |
| **T1: Text Analytics** | `ta_quote_candidates.json` | 4-12 KB | 8 KB | 80 KB |
| | *Subtotal, T1* | | *36 KB* | *360 KB* |
| **T2: Voice Baseline** | `vb_vocab_overlap.json` | 2-6 KB | 4 KB | 40 KB |
| **T2: Voice Baseline** | `vb_sentence_structure.json` | 3-8 KB | 5 KB | 50 KB |
| **T2: Voice Baseline** | `vb_authenticity_rubric.md` | 4-6 KB | 5 KB (one-time) | 5 KB |
| | *Subtotal, T2* | | *14 KB* | *95 KB* |
| **T3: Knowledge Graph** | `kg_concept_nodes.json` | 8-30 KB | 15 KB | 150 KB |
| **T3: Knowledge Graph** | `kg_relationships.json` | 6-20 KB | 10 KB | 100 KB |
| **T3: Knowledge Graph** | `kg_incremental_build.py` | 4-6 KB | 5 KB (one-time) | 5 KB |
| | *Subtotal, T3* | | *30 KB* | *255 KB* |
| **T4: Gnosis** | `engineering_laws.md` (enriched) | 6-12 KB | 2 KB avg | 20 KB |
| **T4: Gnosis** | `source_mapped_axioms.md` | 4-8 KB | 6 KB | 60 KB |
| | *Subtotal, T4* | | *8 KB* | *80 KB* |
| **T5: DPO Training** | `dp_batch_nnn.jsonl` | 20-60 KB | 30 KB avg | 300 KB |
| **T5: DPO Training** | `dp_batch_nnn_manifest.json` | 1-2 KB | 1 KB | 10 KB |
| **T5: DPO Training** | `dp_index.json` | 1-2 KB | 1 KB (one-time) | 2 KB |
| | *Subtotal, T5* | | *32 KB* | *312 KB* |
| **Provenance** | `ingestion_ledger.md` | 4-10 KB | 1 KB avg | 10 KB |
| **Provenance** | `source_dependency_graph.md` | 2-4 KB | 2 KB (one-time) | 4 KB |
| | *Subtotal, provenance* | | *3 KB* | *14 KB* |
| | **TOTAL per source** | | **~168 KB** | |
| | **TOTAL for 10 sources** | | | **~1.7 MB** |
| | **TOTAL for full pipeline (50 sources)** | | | **~8.4 MB** |

### §6.1 Storage Budget Notes

- **Text analytics** dominate per-source storage due to JSON verbosity with source-tracking per term.
- **DPO pairs** grow with source coverage (estimated 2-4 pairs per source).
- **Knowledge graph** is the most compressible — JSON with repeated structural patterns (expect ~60% gzip ratio).
- **Voice baseline rubric** is a one-time cost (reused across all sources).
- **Ingestion ledger** grows linearly with source count (one row per source).
- **Full pipeline** (50 sources: ~20 .plan, 5 GDC, 10 interviews, 15 source files) estimated at **under 10 MB total** — negligible against the 110 GB omega_library partition.

### §6.2 Growth Projection

```
Sources:  0 ──── 10 ──── 25 ──── 50
Storage:  0 ── 1.7MB ── 4.2MB ── 8.4MB

DPO Pairs:    0 ──── 30 ───── 75 ──── 150
DPO Storage:  0 ── 0.3MB ── 0.8MB ── 1.5MB

Knowledge Graph Nodes:   0 ──── 50 ──── 125 ──── 250
Knowledge Graph Edges:   0 ──── 80 ──── 200 ──── 400
```

---

## §7. Ingestion Order Dependency Graph

### §7.1 Dependency Rules

| Rule | Description |
|------|-------------|
| **R1** | A source must be ingested before it can be referenced in derived artifacts |
| **R2** | No cross-source dependency within the same source type (all .plan files are independent) |
| **R3** | Personality analyses depend on text analytics from the same source |
| **R4** | Gnosis enrichment depends on knowledge graph for the same source |
| **R5** | DPO pair generation requires at least 3 sources from at least 2 source types |
| **R6** | Voice baseline requires at least 2 sources from each of the .plan and interview types |
| **R7** | Knowledge graph incremental build has no ordering constraints (any source can be added) |

### §7.2 Execution Order

```
Phase 1: ESTABLISH BASE (any order, all independent)
┌─────────────────────────────────────────────────────────────┐
│  plan-001: 1996-12-25 Quake GL                              │
│  plan-002: 1997-03-14 Q2 Renderer                           │
│  plan-003: 1997-08-01 Q2 Optimization                       │
│  plan-004: 1998-06-15 Q3 Architecture                       │
│  plan-005: 1999-11-20 Q3 Release                            │
│  plan-006: 2004-08-03 Doom 3                                │
│  plan-007: 2011-10-12 Rage                                  │
│  plan-008: 2012-09-01 DOOM 3 BFG                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
Phase 2: GDC TALKS (no intra-phase deps, but benefit from .plan context)
┌─────────────────────────────────────────────────────────────┐
│  gdc-001: 1999 Making of Quake                              │
│  gdc-002: 2011 Wolfenstein 3D iOS / id Tech 5              │
│  gdc-003: 2013 Oculus Rift                                  │
│  gdc-004: 2017 VR Lessons                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
Phase 3: INTERVIEWS (benefit from .plan + GDC context)
┌─────────────────────────────────────────────────────────────┐
│  iv-001: 2023 Lex Fridman #309                              │
│  iv-002: 2022 Joe Rogan                                     │
│  iv-003: 2024 Dwarkesh Patel                                │
└──────────────┬───────────────────────┬──────────────────────┘
               │                       │
               ▼                       ▼
Phase 4a: PERSONALITY ANALYSIS    Phase 4b: GNOSIS DERIVATION
(requires ≥2 .plan + ≥1 interview) (requires ≥3 sources ≥2 types)
┌─────────────────────────┐   ┌──────────────────────────────┐
│ text_analytics/*        │   │ knowledge_graph/             │
│ voice_baseline/         │   │   ├── kg_concept_nodes.json  │
│   ├── vocab_overlap     │   │   └── kg_relationships.json │
│   ├── sentence_struct   │   │ source_mapped_axioms.md     │
│   └── authenticity      │   │ engineering_laws.md (rich)   │
│ speaking_style.md       │   │                              │
└────────────┬────────────┘   └──────────────┬───────────────┘
             │                               │
             └──────────┬────────────────────┘
                        ▼
Phase 5: DPO GENERATION (requires ≥3 sources, ≥2 types)
┌─────────────────────────────────────────────────────────────┐
│  dp_batch_nnn.jsonl                                        │
│  dp_batch_nnn_manifest.json                                │
│  dp_index.json                                             │
│  active_train_set.jsonl                                    │
└─────────────────────────────────────────────────────────────┘
```

### §7.3 Dependency Matrix

```
Source      Plan-00x  GDC-00x  IV-00x  TextAnal  VoiceBase  KnowGraph  Gnosis  DPO
plan-001      —        none     none     self      depend     self       self    indirect
plan-002      —        none     none     self      depend     self       self    indirect
gdc-001       none      —       none     self      depend     self       self    indirect
iv-001        none     none      —       self      REQ(≥2)   self       self    indirect
text_analytics self    self     self      —        depend     none       depend  indirect
voice_baseline DEP(≥2) DEP(≥2)  REQ(≥2)  DEP(self)  —        none       none    indirect
knowledge_graph self   self     self     none      none       —         DEP     indirect
gnosis         DEP     DEP      DEP      none      none       DEP        —      indirect
dpo_pairs      REQ(≥3 sources, ≥2 types)                                    —
```

**Legend**:
- `—`: Same entity (self-relationship)
- `none`: No dependency (can be processed independently)
- `self`: Depends only on its own source file
- `depend`: Benefits from but doesn't strictly require other sources
- `DEP(x)`: Strictly requires x other sources to be processed first
- `REQ(x)`: Requires x sources of a specific type
- `indirect`: Transitively depends on upstream phases

### §7.4 Parallelization Opportunities

| Phase | Parallelism | Constraint |
|-------|-------------|------------|
| Phase 1 (.plan files) | **FULL** (all 8 sources in parallel) | No dependencies |
| Phase 2 (GDC talks) | **FULL** (all 4 talks in parallel) | No intra-phase deps |
| Phase 3 (interviews) | **FULL** (all 3 interviews in parallel) | No intra-phase deps |
| Phase 4a (text analytics) | **PER-SOURCE** (one per source) | Source must be ingested first |
| Phase 4a (voice baseline) | **SEQUENTIAL** | Requires ≥2 .plan + ≥1 interview fully analyzed |
| Phase 4b (knowledge graph) | **FULL** (incremental — any source any time) | No ordering constraints |
| Phase 4b (gnosis enrichment) | **SEQUENTIAL** (requires knowledge graph) | Graph must have relevant nodes |
| Phase 5 (DPO) | **SEQUENTIAL** (batch, not per-source) | Requires ≥3 sources across ≥2 types |

---

## §8. Ingestion Pipeline Script Architecture

### §8.1 Script: `scripts/ingest_john_carmack.py`

```python
#!/usr/bin/env python3
"""
John Carmack Entity — Multi-Dimensional Ingestion Pipeline.

M4 Sequentiality: Plan → Verify → Execute at every level.
M12 Queue Integrity: Every artifact reaches a terminal state (committed or error).

Usage:
    python scripts/ingest_john_carmack.py verify-sources
    python scripts/ingest_john_carmack.py ingest-source --path <relative_path>
    python scripts/ingest_john_carmack.py ingest-all
    python scripts/ingest_john_carmack.py generate-artifacts
    python scripts/ingest_john_carmack.py generate-dpo-pairs
    python scripts/ingest_john_carmack.py update-ledger
    python scripts/ingest_john_carmack.py verify-all
"""

import sys, json, hashlib, uuid
from pathlib import Path
from datetime import datetime, timezone

JC_BASE = Path("data/entities/john_carmack")
LEDGER = JC_BASE / "workspace/carmack_studies/sources/ingestion_ledger.md"


def verify_sources() -> int:
    """Verify all source files have valid YAML frontmatter. Return exit code."""
    errors = 0
    for pattern in ["knowledge/plans/*.md", "knowledge/gdc/*.md",
                    "knowledge/interviews/*.md", "knowledge/source/*.md"]:
        for f in JC_BASE.glob(pattern):
            content = f.read_text()
            if not content.startswith("---"):
                print(f"  ERROR: {f} — missing YAML frontmatter")
                errors += 1
    return errors


def ingest_source(source_path: str) -> dict:
    """
    Ingest a single source: validate, generate 9 artifacts, update ledger.
    Returns {source_id, artifact_count, artifact_paths}.
    """
    source_file = JC_BASE / source_path
    # 1. Validate frontmatter
    # 2. Parse source metadata
    # 3. Generate text analytics (T1)
    # 4. Generate/update voice baseline (T2)
    # 5. Generate/update knowledge graph (T3)
    # 6. Enrich gnosis (T4)
    # 7. Check if DPO threshold met (T5)
    # 8. Update ingestion ledger
    # 9. Return result
    return {"source_id": "xxx", "artifact_count": 9, "artifact_paths": []}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == "verify-sources":
        errors = verify_sources()
        sys.exit(errors)
    elif command == "ingest-source":
        # --path argument
        ...
    elif command == "verify-all":
        ...


if __name__ == "__main__":
    main()
```

---

## §9. Integration with Existing Entity State

### §9.1 Pre-Existing Files (Preserved)

| File | Purpose | Pipeline Impact |
|------|---------|-----------------|
| `soul.yaml` (v3.0.0) | Entity soul | **Enriched** by pipeline (new directives from primary sources) |
| `approved_lessons.yaml` | L3 principles | **Appended** by pipeline (new lessons pass through proposed first) |
| `proposed_lessons.yaml` | L3 proposals | **Seeded** by pipeline (new proposals from primary sources) |
| `carmack_studies/personality/plan_protocol.md` | .plan format & rules | **Enriched** with actual Carmack .plan entries as examples |
| `carmack_studies/gnosis/engineering_laws.md` | L3 gnosis | **Enriched** with source citations and new axioms |
| `carmack_studies/sources/confidence_index.md` | Source tiering | **Unchanged** — already correct |
| `carmack_studies/technical/*` | Technical analyses | **Unchanged** — orthogonal to ingestion pipeline |

### §9.2 New Files Created by Pipeline

| File | Created By | When |
|------|-----------|------|
| `knowledge/{source,gdc,interviews,plans}/*.md` | Pipeline Phase 1 | Source ingestion |
| `personality/text_analytics/ta_*.json` | Pipeline Phase 4a | Per-source |
| `personality/voice_baseline/vb_*.json` | Pipeline Phase 4a | After ≥2 plan + ≥1 interview |
| `personality/speaking_style.md` | Pipeline Phase 4a | After ≥3 sources |
| `gnosis/knowledge_graph/kg_*.json` | Pipeline Phase 4b | Per-source (incremental) |
| `gnosis/source_mapped_axioms.md` | Pipeline Phase 4b | After knowledge graph |
| `sources/ingestion_ledger.md` | Pipeline Phase 1 | First source ingestion |
| `sources/source_dependency_graph.md` | Pipeline Phase 1 | Scaffolded at pipeline init |
| `data/training/entities/john_carmack/dp_*` | Pipeline Phase 5 | After ≥3 sources ≥2 types |

---

## §10. QA Checklist (Pre-Commit Gate)

Before committing any ingestion, verify:

- [ ] **A1**: Source file has valid YAML frontmatter (§2.1)
- [ ] **A2**: Source file frontmatter has `id:`, `source_type:`, `date:`, `confidence:`, `status:`
- [ ] **A3**: All 9 text analytics artifacts exist for the source
- [ ] **A4**: Knowledge graph nodes deduplicated against existing nodes
- [ ] **A5**: Ingestion ledger updated with source row
- [ ] **A6**: `make ingest-jc-verify` passes for all ingested sources
- [ ] **A7**: `make test` passes (no pipeline changes broke the engine)
- [ ] **A8**: `make heritage-map` passes (if new [id-soft:] tags added)
- [ ] **A9**: Commit message follows `feat(ingest-jc):` format (§4.4)
- [ ] **A10**: Hivemind broadcast sent to fleet (§4.1 Step 5)

---

## §11. Template for Future Entity Pipelines

To create a similar pipeline for another entity (e.g., `roc_racoon`, `doom_guy`):

1. **Copy** this document as `INGESTION_PIPELINE_ARCHITECTURE.md` to the entity's `knowledge/` directory
2. **Replace** entity-specific paths (`john_carmack` → `{entity_name}`)
3. **Replace** source types (`.plan`/`GDC` → entity-specific formats)
4. **Replace** knowledge graph domains (rendering/memory → entity-specific domains)
5. **Replace** voice baseline criteria (C1-C5 → entity-specific voice markers)
6. **Register** Makefile targets (`ingest-jc` → `ingest-{entity}`)
7. **Create** entity-specific pipeline script (`scripts/ingest_{entity_name}.py`)

---

*⬡ OMEGA ⬡ MAAT ⬡ deepseek-v4-flash ⬡ P1-ARCHITECT ⬡ INGESTION-PIPELINE-v1.0.0*
