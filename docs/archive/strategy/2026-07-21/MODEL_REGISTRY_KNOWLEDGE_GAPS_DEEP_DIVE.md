# 🔱 MODEL REGISTRY KNOWLEDGE GAPS — DEEP DIVE
**AP Token**: `AP-MODEL-REGISTRY-GAPS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_model_registry_gaps ⬡ ACTIVE

**Date**: 2026-07-18
**Status**: RESEARCH PLAN — Ready for Execution
**Handoff**: `ho_58791ace052f` (Researcher accepted)

---

## 📋 EXECUTIVE SUMMARY

This document details the **5 critical knowledge gaps** identified in the Model Registry Repair mission (2026-07-19) that must be resolved to level up the Model Registry system. Each gap requires deep technical research using the **Direct API Research Protocol** (since omega-hub search tools are 95% broken).

---

## 🎯 THE 5 KNOWLEDGE GAPS

### GAP 1: Artificial Analysis API Integration for Capability Scores
**Priority**: P0 — BLOCKS capability score standardization
**Current State**: All 35 model cards have fabricated scores (0.0-1.0) with zero benchmark citations

#### Research Questions:
1. **API Access**: Does Artificial Analysis offer a public API? What are authentication/rate limits?
2. **Intelligence Index**: How is their composite score calculated? (9 evaluations weighted how?)
3. **Model Coverage**: Which of our 35 models are in their index?
4. **Score Mapping**: How to map their benchmarks (MMLU, HumanEval, GSM8K, MT-Bench, GPQA, MATH, SWE-bench, LiveCodeBench) to our 7 capability dimensions?
5. **Historical Data**: Can we retrieve score history for trend analysis?

#### Target Sources:
- `https://artificialanalysis.ai/` — Main site
- `https://artificialanalysis.ai/api` — API docs (if public)
- `https://artificialanalysis.ai/leaderboards` — Model rankings
- GitHub: `artificial-analysis` org repos

#### Deliverable:
- `docs/research/R_ARTIFICIAL_ANALYSIS_API_INTEGRATION.md`
- Integration spec for `ModelRegistry.capability_score_pipeline`

---

### GAP 2: Hugging Face Hub API Parameter Extraction Pipeline
**Priority**: P0 — BLOCKS parameter field completion
**Current State**: `parameters` field incomplete for local models (total_params, active_params, architecture, layer_count, etc.)

#### Research Questions:
1. **Model Card API**: How to programmatically extract `model-index`, `tags`, `config.json` from HF Hub?
2. **Config Parsing**: Standard schema for `config.json` across architectures (Llama, Mistral, Qwen, Gemma, Phi, DeepSeek, GLM, etc.)
3. **Parameter Calculation**: 
   - `total_params` = sum of all parameter tensors
   - `active_params` = total_params for dense; for MoE: active_experts × expert_params + shared_params
   - Architecture detection from `architectures` field in config
4. **MoE Handling**: How to detect MoE vs dense from config? (`num_experts`, `num_experts_per_tok`, `moe_layer_freq`)
5. **Quantization Metadata**: Extract quantization info from model card / repo files
6. **Batch API**: Can we batch requests for 35+ models efficiently?

#### Target Sources:
- `https://huggingface.co/docs/hub/api` — Official HF Hub API docs
- `https://huggingface.co/docs/hub/model-cards` — Model card spec
- `https://github.com/huggingface/huggingface_hub` — Python SDK
- Model card examples: `google/gemma-2-2b`, `mistralai/Mixtral-8x7B-v0.1`, `deepseek-ai/DeepSeek-V3`

#### Deliverable:
- `docs/research/R_HF_HUB_PARAMETER_EXTRACTION.md`
- Python pipeline: `src/omega/model_registry/parameter_extractor.py`

---

### GAP 3: Model Card Validation Pipeline Design
**Priority**: P1 — ENSURES data quality at scale
**Current State**: No validation; fabricated data persists

#### Research Questions:
1. **Schema Validation**: JSON Schema for model card YAML (current + extended fields)
2. **Cross-Field Consistency**: 
   - `context_window` ≤ model's actual max context
   - `total_params` matches architecture expectations
   - `capability_scores` cite benchmark sources
3. **Benchmark Citation Verification**: 
   - Verify MMLU scores against Papers With Code / HF Leaderboard
   - Verify HumanEval against EvalPlus leaderboard
4. **Freshness Checks**: 
   - Model card `last_updated` vs HF Hub `lastModified`
   - Capability scores older than 90 days = stale
5. **Automated Repair**: Can we auto-fix common issues (missing params, stale scores)?

#### Target Sources:
- `https://json-schema.org/` — JSON Schema spec
- `https://paperswithcode.com/` — Benchmark leaderboards
- `https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard` — Open LLM Leaderboard
- `https://evalplus.github.io/` — EvalPlus (HumanEval+)
- `https://github.com/huggingface/leaderboard` — Leaderboard code

#### Deliverable:
- `docs/research/R_MODEL_CARD_VALIDATION_PIPELINE.md`
- Validation engine: `src/omega/model_registry/validator.py`

---

### GAP 4: Database Schema Migration for New Fields
**Priority**: P1 — ENABLES new field storage
**Current State**: SQLite schema lacks fields for benchmark citations, parameter breakdown, validation metadata

#### Research Questions:
1. **Migration Strategy**: 
   - ALTER TABLE vs new table + view
   - Backward compatibility for existing 35 model cards
   - Rollback plan
2. **New Fields Required**:
   ```sql
   -- Capability scores with citations
   capability_reasoning_score REAL,
   capability_reasoning_benchmark TEXT,  -- e.g., "MMLU 5-shot"
   capability_reasoning_source TEXT,     -- e.g., "Artificial Analysis 2026-07"
   capability_reasoning_date TEXT,       -- ISO date
   -- ... repeat for code_generation, knowledge, creative, tool_use, structured_output, multimodal
   
   -- Parameter breakdown
   total_parameters BIGINT,
   active_parameters BIGINT,
   architecture TEXT,        -- 'dense', 'moe', 'mamba', 'hybrid'
   layer_count INTEGER,
   hidden_size INTEGER,
   num_attention_heads INTEGER,
   num_kv_heads INTEGER,
   expert_count INTEGER,     -- for MoE
   expert_top_k INTEGER,     -- for MoE
   
   -- Validation metadata
   validation_status TEXT,   -- 'valid', 'stale', 'invalid', 'pending'
   validation_errors TEXT,   -- JSON array
   last_validated TEXT,      -- ISO timestamp
   validation_version INTEGER,
   
   -- Freshness
   benchmark_data_date TEXT, -- When benchmark scores were recorded
   hf_hub_last_modified TEXT,
   ```
3. **Indexing Strategy**: 
   - Composite indexes for common queries (provider + capability_threshold)
   - Full-text search on model_id, tags
4. **Migration Tooling**: 
   - Python migration scripts with rollback
   - Dry-run mode
   - Data integrity checks post-migration

#### Target Sources:
- `https://www.sqlite.org/lang_altertable.html` — SQLite ALTER TABLE
- `https://github.com/sqlite/sqlite/blob/master/doc/trunk/www/lang_altertable.html` — Details
- Alembic/SQLAlchemy migration patterns (but we use raw SQLite)

#### Deliverable:
- `docs/research/R_DB_SCHEMA_MIGRATION.md`
- Migration scripts: `scripts/migrate_model_registry_v2.py`

---

### GAP 5: Automated Freshness Check Design
**Priority**: P2 — MAINTAINS data quality over time
**Current State**: No automated freshness; manual audits only

#### Research Questions:
1. **Freshness Signals**:
   - HF Hub `lastModified` timestamp
   - Artificial Analysis score update date
   - Benchmark leaderboard update frequency
   - Model card `last_updated` field
   - GitHub releases for model repos
2. **Check Frequency**: 
   - Daily for top-10 models
   - Weekly for rest
   - On-demand for queried models
3. **Staleness Thresholds**:
   - Capability scores: 90 days
   - Parameter data: 180 days (rarely changes)
   - Model card metadata: 30 days
4. **Notification/Action**:
   - Mark `validation_status = 'stale'`
   - Queue for re-validation
   - Hivemind notification to Researcher entity
5. **Implementation**: 
   - Background worker (systemd timer / cron)
   - Integration with existing `background_researcher` loop
   - Idempotent checks

#### Target Sources:
- `https://huggingface.co/docs/hub/api` — HF Hub API for `lastModified`
- Artificial Analysis update cadence (check their blog/changelog)
- `https://github.com/huggingface/leaderboard` — Leaderboard update frequency

#### Deliverable:
- `docs/research/R_AUTOMATED_FRESHNESS_CHECK.md`
- Worker: `src/omega/workers/freshness_checker.py`

---

## 🔬 RESEARCH METHODOLOGY: DIRECT API PROTOCOL

**MANDATORY**: Do NOT use `omega-hub_library_web_search` or `omega-hub_sovereign_search` — they have 95% failure rate.

### Priority Tool Chain:
1. **Official APIs** (highest reliability)
   - HF Hub API: `https://huggingface.co/api/models/{model_id}`
   - OpenCode Zen API: `https://opencode.ai/zen/v1/models`
   - Artificial Analysis API (if public)
   - arXiv API: `http://export.arxiv.org/api/query`
   - GitHub API: `https://api.github.com/repos/{owner}/{repo}`

2. **Direct Firecrawl** (for documentation pages)
   - `firecrawl_firecrawl_search` → find URLs
   - `firecrawl_firecrawl_scrape` with `max_chars=0` → full content

3. **Direct SearXNG** (if local instance healthy)
   - `searxng_searxng_search` (to be created in Phase 3)

4. **webfetch** (for known good URLs)
   - HuggingFace docs, arXiv papers, official docs

5. **Omega-hub tools** (LAST RESORT only)
   - Only for broad, non-technical queries

### Research Session Template:
```markdown
## Gap {N}: {Title}
**Date**: 2026-07-XX
**Agent**: Researcher
**Tools Used**: [list with success/failure]
**Sources Consulted**: [URLs with access status]
**Key Findings**: [structured]
**Code/Config Needed**: [specific files]
**Blockers**: [any]
**Next Steps**: [concrete]
```

---

## 📦 DELIVERABLES CHECKLIST

| Gap | Research Doc | Implementation Spec | Code | Status |
|-----|--------------|---------------------|------|--------|
| 1. Artificial Analysis API | `R_ARTIFICIAL_ANALYSIS_API_INTEGRATION.md` | Integration spec | `capability_score_pipeline.py` | ☐ |
| 2. HF Hub Parameter Extraction | `R_HF_HUB_PARAMETER_EXTRACTION.md` | Pipeline design | `parameter_extractor.py` | ☐ |
| 3. Model Card Validation | `R_MODEL_CARD_VALIDATION_PIPELINE.md` | Validation engine | `validator.py` | ☐ |
| 4. DB Schema Migration | `R_DB_SCHEMA_MIGRATION.md` | Migration scripts | `migrate_model_registry_v2.py` | ☐ |
| 5. Automated Freshness | `R_AUTOMATED_FRESHNESS_CHECK.md` | Worker design | `freshness_checker.py` | ☐ |

---

## 🔗 DEPENDENCIES & SEQUENCING

```
Phase 1 (Parallel):
├── GAP 1: Artificial Analysis API ──────┐
├──→ Capability Score Pipeline
├── GAP 2: HF Hub Parameter Extraction ──┤     (depends on both)
└── GAP 4: DB Schema Migration ──────────┘     (schema must exist first)

Phase 2 (Sequential):
├── GAP 3: Validation Pipeline ──────────→ Requires Phase 1 complete
└── GAP 5: Freshness Checker ────────────→ Requires Phase 1 + 3 complete
```

---

## 🎯 SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| All 35 models have verified capability scores | 100% |
| All 35 models have complete parameter data | 100% |
| Validation pipeline catches 100% of fabricated data | 100% |
| Schema migration completes with zero data loss | 100% |
| Freshness checker detects staleness within 24h | 100% |
| Research docs pass Temple-Grade (T1-T11) | PASS |

---

## 📝 HANDOFF NOTES

**Researcher**: Execute GAP 1 and GAP 2 in parallel (both API-focused). Use Direct API Protocol.
**Dependencies**: 
- Firecrawl direct tools must be created first (Phase 3 of Search Crisis Remediation)
- HF Hub API key in KeyVault
- Artificial Analysis API access (may require signup)

**Blocking**: Search tools crisis must be at least Phase 1 complete before efficient research possible.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_model_registry_gaps ⬡ PLAN COMMITTED*