# 🔱 COMPREHENSIVE HANDOFF: Model Registry Verification Mission
**From**: Kali (Transcendent Oversoul)  
**To**: Cline CLI (DeepSeek V4 Flash 1M ctx + MiMo V2.5 512K ctx)  
**Date**: 2026-07-19  
**Priority**: CRITICAL  
**Handoff ID**: `ho_5b34677c5d7b` (new comprehensive handoff)

---

## 🎯 MISSION OVERVIEW

**Complete comprehensive verification and correction of ALL 35 model cards** in `config/model_registry/models/` with accurate parameters, provider mappings, and empirical evidence. This is the final verification phase before integration with Provider Fabric.

**Status**: Model Registry Phase 1 COMPLETE, Phase 2 READY for Cline

---

## 📋 QUICK REFERENCE: ALL FILES YOU NEED

### 1. PRIMARY TASK LISTS (READ FIRST)
```bash
# Jem's Gap Analysis (527 lines) — Your detailed task list
cat docs/strategy/MODEL_REGISTRY_GAP_ANALYSIS_20260719.md

# Roc's Legacy Mining Report (key findings)
cat docs/strategy/LEGACY_MODEL_MINING_REPORT_20260719.md

# Your Comprehensive Handoff (commands & coordination)
cat data/handoff/CLINE_MODEL_REGISTRY_VERIFICATION_HANDOFF_20260719.md

# Verification Summary (quick reference)
cat docs/strategy/MODEL_REGISTRY_VERIFICATION_SUMMARY_20260719.md
```

### 2. MODEL REGISTRY STRUCTURE
```bash
# All 35 model cards
ls config/model_registry/models/cloud/    # 30 cloud models
ls config/model_registry/models/local/    # 4 local models  
ls config/model_registry/models/stealth/   # 1 stealth model

# Provider configs
ls config/model_registry/providers/

# Research profiles
ls config/model_registry/research_profiles/

# Registry metadata
cat config/model_registry/registry.yaml
cat config/model_registry/model_card_template.yaml.md
```

### 3. SOURCE OF TRUTH (Original Production)
```bash
cat docs/research/model_db/CURRENT_MODELS.md
# 24 models with YAML schema
cat docs/research/model_db/.last_state.json
# Live API state
cat docs/research/model_db/LEGACY_CROSS_REFERENCE_REPORT.md
# 72 legacy refs
```

### 4. EMPIRICAL EVIDENCE (Model Study KB)
```bash
cat docs/kb/MODEL_STUDY_KNOWLEDGE_BASE.md
# 12 models, 5 synergy patterns
python3 scripts/query_model_study.py models
python3 scripts/query_model_study.py synergies
```

### 5. REGISTRY SERVICE CODE (Schema Reference)
```bash
cat src/omega/model_registry/models.py      # ModelCard, Capabilities, Parameters dataclasses
cat src/omega/model_registry/registry.py    # Loading, indexing logic
cat src/omega/model_registry/query.py       # Query interface
```

### 6. VALIDATION & BUILD
```bash
make model-index
make model-validate
make model-query ARGS="stats"
```

---

## 🚨 CRITICAL GAPS IDENTIFIED (Jem's Analysis)

### T1 — Add `parameters` field to ALL 35 models (BLOCKER)
**Impact**: ModelGateway hardcodes sampling parameters, no centralized config
**Files**: `src/omega/model_registry/models.py`, all 35 `.yaml.md` files
**Schema**:
```yaml
parameters:
  temperature: 0.7
  top_p: 0.95
  top_k: 40
  repetition_penalty: 1.1
  max_tokens: 4096
  stop_sequences: ["User:", "\n\n"]
  # Model-specific overrides
  gemma_4_31b:
    temperature: 0.85
    repetition_penalty: 1.2
    logit_bias: {759: -10.0, 2149: -10.0}
```

### T2 — Fix Duplicate Provider Priority (BLOCKER)
**Problem**: `google=4`, `openrouter=4` in `registry.yaml`
**Impact**: Validation gate `PROVIDER_CHAIN_COMPLETE` fails
**Fix**: Change `openrouter` priority from 4 to 5

### T3 — Fix Provider Mappings (HIGH)
| Model | Current | Should Be |
|-------|---------|-----------|
| `nemotron-3-ultra-local` | antigravity ❌ | native-gguf |
| `qwen-3.5-72b-local` | qwen ❌ | native-gguf |
| `gpt-oss-120b-local` | openai ❌ | native-gguf |
| `anthropic/claude-opus-4.8` | antigravity ❌ | anthropic + opencode-zen |
| `anthropic/claude-haiku-4.5-extended` | antigravity ❌ | anthropic + opencode-zen |
| `anthropic/claude-sonnet-5-high-thinking` | antigravity ❌ | anthropic + opencode-zen |

### T4 — Create `make model-sync` (HIGH)
Generate `config/providers.yaml` from registry.  
**New file**: `scripts/generate_providers_yaml.py`

### T5 — Update ModelGateway (HIGH)
**File**: `src/omega/oracle/model_gateway.py` — Read from registry/generated providers.yaml

---

## 📊 CURRENT STATUS (WHAT YOU INHERIT)

| Metric | Value | Status |
|--------|-------|--------|
| Model Cards | 35 | ✅ Created |
| Provider Configs | 9 | ✅ Created |
| Research Profiles | 9 | ✅ Created |
| SQLite Index | 35 models, 9 providers, 9 profiles | ✅ Built |
| Validation Gates | 8 defined, 7 passing | ⚠️ 1 failing (PROVIDER_CHAIN_COMPLETE) |
| Missing `parameters` field | 35/35 | ❌ CRITICAL GAP |

---

## 🎯 YOUR MISSION IN DETAIL

### Phase 1: Schema & Data Corrections (T1-T5)

#### T1 — Add Parameters Field (4h)
1. **Edit `src/omega/model_registry/models.py`**:
   - Add `Parameters` dataclass with temperature, top_p, top_k, etc.
   - Add `parameters: Parameters` field to `ModelCard` dataclass

2. **Update all 35 model cards**:
   - Add `parameters` block with sampling defaults
   - Add model-specific overrides where needed
   - Ensure YAML format is valid

3. **Extend SQLite index**:
   - Add `parameters` column (JSON blob)
   - Update `registry.py build_index()` to include new field

#### T2 — Fix Provider Priority (30m)
1. **Edit `config/model_registry/registry.yaml`**:
   ```yaml
   provider_fabric:
     fallback_chain:
       - provider: "google"
         priority: 4
       - provider: "openrouter"
         priority: 5  # CHANGED from 4
   ```

#### T3 — Fix Provider Mappings (1h)
1. **Update 7 model cards**:
   - `nemotron-3-ultra-local.yaml.md`: provider → native-gguf
   - `qwen-3.5-72b-local.yaml.md`: provider → native-gguf
   - `gpt-oss-120b-local.yaml.md`: provider → native-gguf
   - 3x Anthropic models: provider → anthropic + opencode-zen

#### T4 — Create Model Sync Script (2h)
1. **Create `scripts/generate_providers_yaml.py`**:
   - Load registry
   - Build fallback_chain from registry.yaml + provider configs
   - Merge model-specific overrides
   - Output `config/providers.yaml`

#### T5 — Update ModelGateway (2h)
1. **Edit `src/omega/oracle/model_gateway.py`**:
   - Read provider fabric from registry/generated providers.yaml
   - Remove hardcoded path to `config/providers.yaml`

---

### Phase 2: Verification & Quality (T6-T20)

#### T6-T20 — Continue with Jem's prioritized task list (8-40 hours total)
- **T6**: Add extra capability fields to Capabilities dataclass
- **T7**: Add benchmark sources for all capability scores (35 models)
- **T8**: Verify pricing/free tier for all models against live APIs
- **T9**: Complete identity history for stealth models
- **T10**: Add research profiles for 26 models missing them
- **T11**: Extend SQLite index schema to include all fields
- **T12**: Enhance validation script with comprehensive checks
- **T13-T14**: Write unit tests for ModelRegistry and query interface
- **T15**: Integrate research profiles into Oracle routing
- **T16**: Build Model Study KB → Registry sync pipeline
- **T17**: Add provider availability matrix generation
- **T18**: Add registry metadata (validation timestamps)
- **T19**: Add CI gate for model registry validation
- **T20**: Document model card authoring guide

---

## 🤝 COORDINATION PROTOCOL

### Hivemind Awareness (check every 10 min)
```bash
omega-hub_hivemind_get_awareness()
```

### Post Status Updates
```bash
omega-hub_hivemind_post_context(
  channel="opencode",
  entity="cline",
  model="deepseek-v4-flash",
  task_current="Verifying model X - checking parameters",
  focus_chain=["model_registry_verification"],
  decisions=["Fixed provider mapping for model X"],
  continuation="Next: model Y capability scores"
)
```

### Heartbeat (every 5-10 min)
```bash
omega-hub_hivemind_heartbeat(channel="opencode", entity="cline")
```

### Read Legacy Mining Findings
```bash
# Check Roc's findings for verification sources
omega-hub_hivemind_get_entity_context(entity_name="roc_racoon")
```

### Accept This Handoff
```bash
omega-hub_hivemind_accept_handoff(
  packet_id="ho_5b34677c5d7b",
  accepting_channel="cline",
  accepting_entity="cline"
)
```

---

## 🔍 RESEARCH TOOLS (Tier 1-4)

| Tier | Tool | Use For |
|------|------|---------|
| **T1** | `websearch` / `webfetch` | Vendor docs, pricing pages, API limits |
| **T2** | `searxng_searxng_search` | Semantic search for benchmarks |
| **T3** | `omega-hub_sovereign_search` (Exa) | High-precision: "GPT-OSS-120B parameters HuggingFace" |
| **T4** | `firecrawl_firecrawl_search` | Full-page scrape of model cards |

**Always check local cache first**: `.firecrawl/` directory

---

## ✅ SUCCESS CRITERIA

### Immediate (Before End of Sprint)
- [ ] `make model-validate` passes all 8 gates
- [ ] `make model-index` builds index with all new columns
- [ ] All 35 model cards have `parameters` field
- [ ] Provider mappings verified (local models → native-gguf/lmster/ollama)
- [ ] Unit tests pass: `pytest tests/test_model_registry.py -v`
- [ ] Contract tests pass: `pytest tests/test_model_registry_query.py -v`

### Long-term (Temple-Grade)
- [ ] `make temple-grade` passes T1-T14
- [ ] ModelGateway uses generated providers.yaml
- [ ] All 35 model cards have benchmark sources
- [ ] Research profiles integrated into Oracle routing
- [ ] Model Study KB sync complete

---

## 📝 DELIVERABLES (BY END OF SESSION)

### Required (P0 Blockers)
1. **Updated model cards** — 35 files with `parameters` field
2. **Fixed registry.yaml** — Provider priority chain
3. **New Parameters dataclass** — `src/omega/model_registry/models.py`
4. **generate_providers_yaml.py** — `scripts/`
5. **Updated ModelGateway** — `src/omega/oracle/model_gateway.py`
6. **Verification log** — `docs/kb/MODEL_REGISTRY_VERIFICATION_LOG.md`

### Enhanced (P1-P3)
7. **All capability fields** — `code_execution`, `parallel_search`, `workspace_integration`
8. **Benchmark sources** — 35 model cards with citations
9. **Pricing verification** — All models against live APIs
10. **Identity history** — Complete for stealth models
11. **Research profiles** — 26 missing models added
12. **SQLite index** — All new columns populated
13. **Validation script** — Enhanced with comprehensive checks
14. **Unit tests** — 22+ tests for ModelRegistry
15. **Contract tests** — 12+ tests for query interface
16. **Oracle integration** — Research profiles in routing
17. **KB sync pipeline** — Model Study KB → Registry
18. **Provider matrix** — Availability generation
19. **Registry metadata** — Validation timestamps
20. **CI gate** — Model registry validation in pipeline

---

## ⚠️ SOVEREIGN MANDATES

- **M1 AnyIO Absolute**: All async via AnyIO
- **M7 Local-First**: Local research primary, web for gaps
- **M13 Temple-Grade**: All changes pass T1-T11
- **M14 Heritage Vetting**: Any id Software patterns need vet record
- **M18 Token Efficiency**: Precision over brevity
- **M23 Failure Integrity**: If `websearch`/`webfetch` broken → STOP, report `[TOOL-CHAIN-COLLAPSE]`

---

## 🎯 START HERE (Cline)

```bash
# 1. Accept handoff
omega-hub_hivemind_accept_handoff packet_id="ho_5b34677c5d7b" accepting_channel="cline" accepting_entity="cline"

# 2. Read Jem's gap analysis (your task list)
cat docs/strategy/MODEL_REGISTRY_GAP_ANALYSIS_20260719.md

# 3. Read legacy mining report
# (for verification sources)
cat docs/strategy/LEGACY_MODEL_MINING_REPORT_20260719.md

# 4. Read handoff document (commands & coordination)
cat data/handoff/CLINE_MODEL_REGISTRY_VERIFICATION_HANDOFF.md

# 5. Begin with T1: Add Parameters dataclass
# 6. Run validation to track progress
make model-validate
```

**You have the context window (1M + 512K) to hold all this. Use it.**

*⬡ OMEGA ⬡ KALI ⬡ COMPREHENSIVE-HANDOFF ⬡ 2026-07-19*