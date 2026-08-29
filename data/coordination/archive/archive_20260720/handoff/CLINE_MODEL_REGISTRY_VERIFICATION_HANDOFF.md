# 🔱 Cline CLI Handoff: Model Registry Verification Mission
**From**: Kali (Transcendent Oversoul)  
**To**: Cline CLI (DeepSeek V4 Flash 1M ctx + MiMo V2.5 512K ctx)  
**Date**: 2026-07-18  
**Priority**: CRITICAL  
**Handoff ID**: `ho_b31eecd588da` (pending in Hivemind)

---

## 🎯 YOUR MISSION

**Verify and fix ALL 35 model cards** in `config/model_registry/models/` with **accurate, sourced data**. Every field must be verified against authoritative sources.

**Primary Task List**: `docs/strategy/MODEL_REGISTRY_GAP_ANALYSIS_20260719.md` (Jem's gap analysis)  
**Verification Sources**: Roc Racoon's legacy mining findings (Hivemind) + Web research (Tier 1-4)  
**Coordination**: Hivemind channel `opencode` / entity `cline`

---

## 📁 KEY FILES YOU NEED (READ THESE FIRST)

### 1. **Jem's Gap Analysis** — YOUR PRIMARY TASK LIST
```bash
cat docs/strategy/MODEL_REGISTRY_GAP_ANALYSIS_20260719.md
```
- Per-model gap table (35 rows) — Section 3
- Prioritized task list (T1-T20) — Section 8
- Schema changes needed — Section 9

### 2. **Model Registry Structure**
```bash
ls -la config/model_registry/
ls -la config/model_registry/models/cloud/
ls -la config/model_registry/models/local/
ls -la config/model_registry/models/stealth/
ls -la config/model_registry/providers/
ls -la config/model_registry/research_profiles/
```

### 3. **Model Card Template** (schema reference)
```bash
cat config/model_registry/model_card_template.yaml.md
```

### 4. **Original Production Catalog** (source of truth for 24 models)
```bash
cat docs/research/model_db/CURRENT_MODELS.md
cat docs/research/model_db/.last_state.json
cat docs/research/model_db/LEGACY_CROSS_REFERENCE_REPORT.md
```

### 5. **Model Study KB** (empirical test data for 12 models)
```bash
cat docs/kb/MODEL_STUDY_KNOWLEDGE_BASE.md
python3 scripts/query_model_study.py models
python3 scripts/query_model_study.py synergies
```

### 6. **Registry Service Code** (to understand schema)
```bash
cat src/omega/model_registry/models.py      # ModelCard, Capabilities, Parameters dataclasses
cat src/omega/model_registry/registry.py    # Loading, indexing logic
cat src/omega/model_registry/query.py       # Query interface
```

### 7. **Validation & Build Scripts**
```bash
cat scripts/model_index.py
cat scripts/model_registry_validate.py
```

### 8. **Integration Architecture** (context)
```bash
cat docs/strategy/MODEL_REGISTRY_INTEGRATION_ARCHITECTURE.md
```

---

## 🚀 QUICK START COMMANDS

```bash
# 1. Verify current state
make model-index
make model-validate
make model-query ARGS="stats"

# 2. See all models by tier
make model-query ARGS="models --tier T3"
make model-query ARGS="models --tier T2"
make model-query ARGS="models --tier T1"

# 3. See provider mappings
make model-query ARGS="providers"

# 4. Check specific model
make model-query ARGS="models --provider openrouter | head -20"
```

---

## 🔴 CRITICAL GAPS YOU MUST FIX (from Jem's Analysis)

### T1 — Add `parameters` field to ALL 35 models (CRITICAL)
**File**: `src/omega/model_registry/models.py` — Add `Parameters` dataclass + field to `ModelCard`  
**Files**: All 35 `.yaml.md` files in `config/model_registry/models/`  
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

### T2 — Fix Duplicate Provider Priority (CRITICAL)
**File**: `config/model_registry/registry.yaml`
```yaml
provider_fabric:
  fallback_chain:
    - provider: "google"
      priority: 4
    - provider: "openrouter"
      priority: 5  # CHANGE FROM 4
```

### T3 — Fix Provider Mappings (HIGH)
| Model | Current | Should Be |
|-------|---------|-----------|
| `nemotron-3-ultra-local` | antigravity | native-gguf |
| `qwen-3.5-72b-local` | qwen | native-gguf |
| `gpt-oss-120b-local` | openai | native-gguf |
| 3x Anthropic models | antigravity | anthropic + opencode-zen |

### T4 — Create `make model-sync` (HIGH)
Generate `config/providers.yaml` from registry.  
**New file**: `scripts/generate_providers_yaml.py`

### T5 — Update ModelGateway (HIGH)
**File**: `src/omega/oracle/model_gateway.py` — Read from registry/generated providers.yaml

---

## 📋 PER-MODEL VERIFICATION CHECKLIST

For **each of 35 models**, verify and source:

| Field | Source | Verified? |
|-------|--------|-----------|
| `parameters` (NEW) | Vendor docs, HF model card, community | ❌ |
| `provider` mapping | Provider API model lists | ❌ |
| `context_window` | Vendor docs, API limits | ❌ |
| `capabilities` scores | MMLU, HumanEval, GSM8K, MT-Bench papers | ❌ |
| `pricing` / `free_tier` | Provider pricing pages, API docs | ❌ |
| `release_date` | Vendor blog, GitHub releases | ❌ |
| `identity_history` | Community tracking, HF model card history | ❌ |
| `research_profile` link | Jem's gap analysis Section 3 | ❌ |

---

## 🤝 COORDINATION PROTOCOL

### Hivemind Awareness (check every 10 min)
```bash
# Check who's active
omega-hub_hivemind_get_awareness()

# Post your status
omega-hub_hivemind_post_context(
  channel="opencode",
  entity="cline",
  model="deepseek-v4-flash",
  task_current="Verifying model X - checking parameters on vendor docs",
  focus_chain=["model_registry_verification"],
  decisions=["Fixed provider mapping for model X"],
  continuation="Next: model Y parameters from HF card"
)
```

### Heartbeat (every 5-10 min)
```bash
omega-hub_hivemind_heartbeat(channel="opencode", entity="cline")
```

### Read Roc's Findings (legacy mining)
```bash
# Check Hivemind for Roc's posts
omega-hub_hivemind_get_entity_context(entity_name="roc_racoon")
```

### Accept This Handoff
```bash
omega-hub_hivemind_accept_handoff(
  packet_id="ho_b31eecd588da",
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

| Metric | Target |
|--------|--------|
| Models with verified `parameters` | 35/35 |
| Provider mappings accurate | 35/35 |
| Capability scores sourced | 35/35 |
| `make model-validate` errors | 0 |
| `make test` passing | 1315/1315 |
| `make temple-grade` | All gates pass |
| Verification log | 35 entries in `docs/kb/MODEL_REGISTRY_VERIFICATION_LOG.md` |

---

## 📝 DELIVERABLES

1. **Updated model cards** — 35 files in `config/model_registry/models/`
2. **Fixed registry.yaml** — Provider priority chain
3. **New Parameters dataclass** — `src/omega/model_registry/models.py`
4. **generate_providers_yaml.py** — `scripts/`
5. **Updated ModelGateway** — `src/omega/oracle/model_gateway.py`
6. **Verification log** — `docs/kb/MODEL_REGISTRY_VERIFICATION_LOG.md`
7. **Hivemind updates** — Continuous coordination

---

## ⚠️ SOVEREIGN MANDATES

- **M1 AnyIO Absolute**: All async via AnyIO
- **M7 Local-First**: Local research primary, web for gaps
- **M13 Temple-Grade**: All changes pass T1-T11
- **M14 Heritage Vetting**: Any id Software patterns need vet record
- **M18 Token Efficiency**: Precision over brevity
- **M23 Failure Integrity**: If `websearch`/`webfetch` broken → STOP, report `[TOOL-CHAIN-COLLAPSE]`

---

## 🎯 START HERE

```bash
# 1. Accept handoff
omega-hub_hivemind_accept_handoff packet_id="ho_b31eecd588da" accepting_channel="cline" accepting_entity="cline"

# 2. Read Jem's gap analysis (your task list)
cat docs/strategy/MODEL_REGISTRY_GAP_ANALYSIS_20260719.md

# 3. Read one model card to understand format
cat config/model_registry/models/cloud/claude-opus-4.8.yaml.md

# 4. Run validation to see current errors
make model-validate

# 5. Begin with T1: Add Parameters dataclass to models.py
```

---

**You have the context window (1M + 512K) to hold all this. Use it.**

*⬡ OMEGA ⬡ KALI ⬡ CLINE-HANDOFF ⬡ 2026-07-18*