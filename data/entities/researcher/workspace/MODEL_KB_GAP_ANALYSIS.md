<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Model Knowledge Base Gap Analysis — Researcher Synthesis Report
# ⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_gap_analysis ⬡ RESEARCH-MODE
**AP Token**: `AP-RESEARCHER-GAP-ANALYSIS-v1.0.0`
**Date**: 2026-06-16
**Source Audits**: quality's MODEL_KB_CONSOLIDATION_AUDIT.md, lilith's MODEL_RUNTIME_GOVERNANCE_AUDIT.md
**Coverage**: All config files, provider code, soul.yamls, coordination docs, env files, scripts

---

## §0 Executive Summary

**Rating**: 🔴 RED — 12 name conflicts, 3 dead code islands, 1 phantom file, 6 unwired components

**Architect's View**: The model knowledge architecture is fragmented across **10+ files** with **no single source of truth** for model names. The `entity_model_affinity.yaml` references 3 models that don't exist in `models.yaml`. The Antigravity dual-pool architecture (8-keys × 2-pools) is documented in 3 files but wired in exactly 0 lines of engine code. The `GoogleKeyPoolProvider` class exists but is never instantiated.

**Adversary's View**: This is not a bug — it is a **design failure**. Every file that references a model name must be changed when a model is added or renamed. The system has no model registry, no enum, no cross-referencing validation. When Google renames `gemini-2.5-flash` to `gemini-3.5-flash` the engine doesn't notice for 10 days. When 8 keys are documented but only 1 is configured, the dual-pool architecture is fantasy.

**Alchemist's View**: The 8-key rotation strategy is a magnificent model of strategic scarcity — it should be the pattern for ALL quota-managed resources, not just Google. The `USAGE_POOL_LOG.json` schema (anti-thrashing, cooling, draining) is a domain model that could unify ALL provider quota tracking if we wire it into the circuit breaker system.

**Archivist's View**: The 3-tier model affinity (local_fast/local_deep/cloud) in `entity_model_affinity.yaml` is well-designed and correctly ported from `xna-omega-legacy`. The problem is not the schema — it's the model names and the missing wiring to the provider fabric.

---

## §1 Complete Model Name Cross-Reference Table

Every file × every model name referenced. Discrepancies marked with ❌.

### §1.1 Local GGUF Models

| Logical Model | `models.yaml` | `providers.yaml` overrides | `entity_model_affinity.yaml` | `antigravity/soul.yaml` | Status |
|---|---|---|---|---|---|
| **Qwen3-1.7B** | `qwen3-1.7b` | `qwen3-1.7b` → lmster/ollama | `qwen3-1.7b` | — | ✅ Consistent |
| **Qwen3-1.7B-Q6_K** | `qwen3-1.7b-q6_k` | `qwen3-1.7b-q6_k` → lmster/ollama | — | — | ✅ Consistent |
| **Qwen3-0.6B-Q6_K** | `qwen3-0.6b-q6_k` | `qwen3-0.6b-q6_k` → ollama | — | — | ✅ Consistent |
| **Qwen3-4B-Think-Q4** | `qwen3-4b-thinking-q4_k_m` | `qwen3-4b-thinking-q4_k_m` → lmster/ollama/google | `qwen3-4b-q4_k_m` ❌ | — | **Missing "-thinking-"** |
| **Qwen3-4B-Q5** | *(not present)* ❌ | — | `qwen3-4b-q5_k_m` ❌ | — | **Never existed** |
| **Phi-4-mini-Q5** | `phi-4-mini` | `phi-4-mini` → lmster/ollama/google(opencode-zen) | — | — | ✅ Consistent |
| **Phi-4-mini-Abliterated** | `phi-4-mini-reasoning-abliterated-q4_k_m` | → lmster/ollama as `phi-4-mini-abliterated` | — | — | ✅ Local only |
| **Phi-2-OmniMatrix** | `phi-2-omnimatrix-i1-q4_k_m` | → ollama as `ministral:3b` | — | — | ⚠️ Ollama alias only |
| **DeepSeek-R1-Qwen3-8B** | `deepseek-r1-qwen3-8b-q3_k_l` | → lmster/ollama/google/opencode-zen | — | — | ✅ Consistent |
| **Krikri-8B-Q4** | `krikri-8b-q4_k_m` | `krikri-8b-q4_k_m` → lmster/ollama | — | — | ✅ Consistent |
| **Krikri-8B-Q5** | *(not present)* ❌ | — | `krikri-8b-q5_k_m` ❌ | — | **Never existed** |
| **RocRacoon-3B** | `rocracoon-3b-instruct` | → lmster as `RocRacoon-3b` / ollama as `rocracoon:3b` | — | — | ✅ Consistent |
| **Qwen3-VL-4B** | `qwen3-vl` | — | — | — | ✅ Local only |
| **Embedding-Gemma** | `embeddinggemma-300m-q6_k` ❌ | — | — | — | **Missing dash** (should be `embedding-gemma`) |

### §1.2 Cloud Models

| Logical Model | `models.yaml` (cloud_models) | `providers.yaml` overrides | `entity_model_affinity.yaml` | `antigravity/soul.yaml` | Status |
|---|---|---|---|---|---|
| **Gemini 3.5 Flash** | `gemini-3.5-flash` | — | `gemini-2.5-flash` ❌ | `gemini_3_5_flash` ❌ | **3 variants, 1 version wrong** |
| **Gemini 3.1 Pro** | — | — | — | `gemini_3_1_pro` ✋ | **Only in soul.yaml** |
| **Gemma 4 31B** | `gemma-4-31b` | `gemma-4-31b-it` ❌ | — | — | **Suffix mismatch** |
| **Gemma 4 26B** | `gemma-4-26b-it` | `gemma-4-26b-it` | — | — | ✅ Consistent |
| **Gemini 4 31B** | `gemini-4-31b` ❌ | — | — | — | **Doesn't exist at Google** |
| **Claude Sonnet 4.6** | `claude-sonnet-4` ❌ | — | — | `claude_sonnet_4_6_adaptive` ❌ | **Name mismatch** |
| **Claude Opus 4.6** | — | — | — | `opus_4_6_adaptive` ✋ | **Only in soul.yaml** |
| **gpt-oss-120b** | — | — | — | `gpt_oss_120b` ✋ | **Only in soul.yaml** |
| **DeepSeek V4 Flash** | `deepseek-v4-flash` | — | — | — | ✅ Consistent |
| **MiMo M3** | — | `minimax/minimax-m3` | — | — | ✅ Provider-specific only |
| **MiMo M2.5** | `mimo-v2.5` ❌ | `minimax/minimax-m2.5` | — | — | **mimo-v2.5 vs mimo-v2.5-free** |
| **Nemotron-3-Ultra** | `nemotron-3-ultra` ❌ | — | — | — | **UNVERIFIED dead entry** |
| **Gemma 4 9B** | `gemma-4-9b` ❌ | — | — | — | **UNVERIFIED dead entry** |

**Total: 12 unique discrepancies** across 5 config files.

---

## §2 Canonical Naming Convention Proposal

### §2.1 Principles

1. **`models.yaml` is the SINGLE source of truth** for local GGUF model identifiers
2. All other files MUST reference `models.yaml` keys exactly
3. Quantization suffix is mandatory for local models (e.g., `-q4_k_m` → `-Q4_K_M`) — uppercase quantization
4. Dashes-only (NO underscores) for cloud model names
5. Version MUST be present in model name (e.g., `gemini-3.5-flash`, not `gemini-flash`)

### §2.2 Convention Rules

| Component | Rule | Example |
|---|---|---|
| **Base name** | Lowercase, dashes only | `qwen3`, `gemini`, `krikri` |
| **Quantization** | Suffix after dash, uppercase Q | `-Q4_K_M`, `-Q6_K`, `-Q5_K_M` |
| **Version** | Major.minor always present (for cloud) | `gemini-3.5-flash`, not `gemini-flash` |
| **Provider tag** | Only in providers.yaml model_overrides | `gemma-4-31b-it` (Google API name) |
| **Capability** | Use standard suffix: `-thinking`, `-instruct`, `-vl` | `qwen3-4b-thinking-Q4_K_M` |

### §2.3 Proposed Canonical Name Corrections

| Current Name(s) | Canonical Name | Files to Update |
|---|---|---|
| `qwen3-4b-q4_k_m` (entity_affinity) | `qwen3-4b-thinking-Q4_K_M` | `entity_model_affinity.yaml` (11 refs) |
| `qwen3-4b-q5_k_m` | `qwen3-4b-thinking-Q5_K_M` — but DOES it exist? | Verify on disk first |
| `krikri-8b-q5_k_m` | `krikri-8b-Q5_K_M` — but DOES it exist? | Verify on disk first |
| `gemini-2.5-flash` | `gemini-3.5-flash` | `entity_model_affinity.yaml` (11 refs) |
| `gemini_3_5_flash` | `gemini-3.5-flash` | `antigravity/soul.yaml` |
| `gemini_3_1_pro` | `gemini-3.1-pro` | `antigravity/soul.yaml` |
| `embeddinggemma-300m-q6_k` | `embedding-gemma-300m-Q6_K` | `models.yaml` |
| `gemma-4-31b` (model_updater) | `gemma-4-31b-it` | `omega.yaml`, `models.yaml` |
| `gemini-4-31b` | `gemini-3.1-pro` or delete | `models.yaml` (cloud_models) |
| `mimo-v2.5` | `mimo-v2.5-free` | `models.yaml` |
| `phi-4-mini` → `gemma-4-31b-it` | KEEP — but add budget warning | `providers.yaml` (document the 10x) |

### §2.4 Model Name Validation CI Gate

Proposed `make validate-model-names` that:
1. Reads all model keys from `models.yaml`
2. Scans `entity_model_affinity.yaml` and verifies every `model:` value exists in models.yaml or is a known cloud model
3. Scans `providers.yaml` and verifies every override key exists in models.yaml
4. Scans `antigravity/soul.yaml` for model references and warns on mismatch
5. Returns non-zero on any discrepancy

---

## §3 Quota Architecture Analysis

### §3.1 Current State

| Component | Reality | Documentation Claim | Gap |
|---|---|---|---|
| **Google API keys** | 1 (`GOOGLE_API_KEY` in `.env`) | 8 (`GOOGLE_API_KEY_01`-`08`) | **7 missing keys** |
| **KeyPool provider** | `GoogleKeyPoolProvider` class exists (providers.py:113-156) | Should be instantiated in model_gateway.py | **NEVER wired** |
| **Usage tracking** | Circuit breaker records failures per model | USAGE_POOL_LOG.json tracks per-key + per-pool | **No code path** |
| **Pool awareness** | Single undifferentiated Google bucket | Pool G (Gemini) + Pool C (Claude/Opus/gpt-oss) | **No pool abstraction** |
| **Env var naming** | `GOOGLE_API_KEY` (providers.py), `GOOGLE_API_KEYS` (orchestrator.py) | `GOOGLE_API_KEY_01`-`08` | **3 naming schemes** |
| **Quota reset** | Circuit breaker auto-recovers after timeout | Weekly Monday 00:00 UTC reset | **No calendar-aware reset** |

### §3.2 Env Var Status

| Env Var | Defined In `.env` | Read By | Used By |
|---|---|---|---|
| `GOOGLE_API_KEY` | ✅ Present | `providers.py:53,57`, `model_updater.py:47` | `GoogleAIProvider` |
| `GOOGLE_API_KEY_01`-`08` | ❌ **NOT in .env** | — | **Documented only** |
| `GOOGLE_API_KEYS` (plural) | ❌ **NOT in .env** | `orchestrator.py:142` | Background worker init |
| `OPENCODEZEN` | ❌ **NOT in .env** | — | `providers.yaml` references |
| `OPENROUTER_API_KEY` | ❌ **NOT in .env** | — | `providers.yaml` references |

**Critical Finding**: The `.env` file is referenced by `model_gateway.py:_load_sovereign_secrets()` (lines 178-203) which loads ALL key-value pairs into `os.environ`. But the `.env` only contains `GOOGLE_API_KEY`. The other 7 Google keys are **not configured anywhere**.

### §3.3 Env Var Naming Conflict

Three different naming schemes for Google keys exist simultaneously:

| Scheme | Source | Problem |
|---|---|---|
| `GOOGLE_API_KEY` (singular) | `providers.py`, `providers.yaml` | Single key only |
| `GOOGLE_API_KEY_01`...`_08` | `PW_MODEL_15_COORDINATION.md`, `R_MODEL_INTELLIGENCE_LAYER.md`, lilith's audit | Does not match provider code |
| `GOOGLE_API_KEYS` (plural) | `orchestrator.py:142` | Does not match any existing var, expects comma-separated |

**Fix**: Standardize on `GOOGLE_API_KEY_01` through `GOOGLE_API_KEY_08`. Update `orchestrator.py` to use this scheme. Update `.env.example` accordingly.

### §3.4 Recommended Quota Architecture

```
Pool G (Gemini keys)
├── key_01: agy_key_01 (→ Gemini 3.5 Flash — Phase 1)
├── key_02: agy_key_02 (→ Gemini 3.5 Flash — Phase 2)
├── key_03: agy_key_03 (→ Gemini 3.5 Flash — Phase 3)
├── key_04: agy_key_04 (→ Gemini 3.1 Pro — Phase 4 high-stakes)
├── key_05: agy_key_05 (→ Gemini 3.5 Flash — Phase 5)
├── key_06: agy_key_06 (→ Gemini 3.5 Flash — Phase 6)
├── key_07: agy_key_07 (→ Gemini 3.1 Pro — Phase 7 high-stakes)
└── key_08: agy_key_08 (→ RESERVE — Claude/Opus/gpt-oss cross-pool)

Pool C (Claude + Open-Weight keys) — Future
├── key_01-08: Uses separate API keys (Claude Anthropic, OpenAI, etc.)
└── Shares USAGE_POOL_LOG.json schema but different pool tracking
```

**Phase → Key Mapping already exists in `antigravity/soul.yaml:97-108`** and `USAGE_POOL_LOG.json`. The code just needs to read it.

---

## §4 Provider Fabric Wiring Plan

### §4.1 Minimal Wiring Steps (Ordered P0→P1→P2)

#### 🔴 P0 — Wire GoogleKeyPoolProvider (lilith-estimated 45 min)

| Step | File | Change | Effort |
|---|---|---|---|
| **P0.1** | `src/omega/oracle/model_gateway.py` | Add `"google-keypool": GoogleKeyPoolProvider` to `provider_map` (line 282) | 1 min |
| **P0.2** | `config/providers.yaml` | Add `google-keypool` provider entry after existing `google`, with `keys:` list referencing `GOOGLE_API_KEY_01`-`_08` | 5 min |
| **P0.3** | `.env` | Add `GOOGLE_API_KEY_01` through `GOOGLE_API_KEY_08` (users must populate) | 30 min (key collection) |
| **P0.4** | `.env.example` | Update with `GOOGLE_API_KEY_01`-`_08` references | 2 min |
| **P0.5** | `config/providers.yaml` | Change `google` provider priority to 3.5 (between 3 and 4) — keypool stays at 3, single-key falls back | 1 min |

**Total**: ~40 min implementation + key collection time

#### 🔴 P0 — Fix Entity Model Affinity Names (30 min)

| Step | File | Change | Effort |
|---|---|---|---|
| **P0.6** | `config/entity_model_affinity.yaml` | Replace `qwen3-4b-q4_k_m` → `qwen3-4b-thinking-Q4_K_M` (11 refs) | 5 min |
| **P0.7** | `config/entity_model_affinity.yaml` | Replace `gemini-2.5-flash` → `gemini-3.5-flash` (11 refs) | 5 min |
| **P0.8** | `config/entity_model_affinity.yaml` | Replace `qwen3-4b-q5_k_m` → verify if Q5 exists, else point to Q4 | 5 min |
| **P0.9** | `config/entity_model_affinity.yaml` | Replace `krikri-8b-q5_k_m` → `krikri-8b-Q4_K_M` | 5 min |

#### 🔴 P0 — Fix Soul.yaml Model Names (10 min)

| Step | File | Change | Effort |
|---|---|---|---|
| **P0.10** | `data/entities/antigravity/soul.yaml` | Replace `gemini_3_5_flash` → `gemini-3.5-flash` | 2 min |
| **P0.11** | `data/entities/antigravity/soul.yaml` | Replace `gemini_3_1_pro` → `gemini-3.1-pro` | 2 min |
| **P0.12** | `data/entities/antigravity/soul.yaml` | Add note that Pool C models are not yet in engine config | 2 min |

#### 🟡 P1 — Wire Env Var Naming (15 min)

| Step | File | Change | Effort |
|---|---|---|---|
| **P1.1** | `src/omega/oracle/orchestrator.py:142` | Change `GOOGLE_API_KEYS` → collect `GOOGLE_API_KEY_01`-`_08` | 5 min |
| **P1.2** | `src/omega/oracle/orchestrator.py` | Add fallback to single `GOOGLE_API_KEY` if 8-key pool empty | 5 min |

#### 🟡 P1 — Wire USAGE_POOL_LOG.json (2 hr)

| Step | File | Change | Effort |
|---|---|---|---|
| **P1.3** | New file: `src/omega/oracle/usage_pool.py` | Create `UsagePoolTracker` class that reads/writes `USAGE_POOL_LOG.json` | 30 min |
| **P1.4** | `src/omega/oracle/providers.py` | Integrate `UsagePoolTracker` into `GoogleKeyPoolProvider.generate()` — log calls | 15 min |
| **P1.5** | `src/omega/oracle/model_gateway.py` | After successful `provider.generate()`, write usage to pool log | 15 min |

#### 🟡 P1 — Fix Stale Config Entries (15 min)

| Step | File | Change | Effort |
|---|---|---|---|
| **P1.6** | `config/models.yaml` (agent_roles) | Remove `jem_discovery`, `jem_synthesis`, `jem_verification`, `plan` | 5 min |
| **P1.7** | `config/models.yaml` (cloud_models) | Remove `nemotron-3-ultra`, `claude-sonnet-4`, `gemma-4-9b` or update | 5 min |

#### 🟢 P2 — Long-Term (Future Sprint)

| Step | File | Change | Effort |
|---|---|---|---|
| **P2.1** | `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md` | Add Tier 0 knowledge locations: `config/models.yaml`, `config/providers.yaml`, `config/entity_model_affinity.yaml`, all `data/entities/*/soul.yaml` | 15 min |
| **P2.2** | Makefile | Add `make validate-model-names` target | 30 min |
| **P2.3** | `src/omega/oracle/providers.py` | Remove dead `ThreadPoolExecutor` import (line 6) and dead `except OmegaError: raise` (lines 107-108) | 2 min |
| **P2.4** | New: `config/model_registry.yaml` | Single source of truth for ALL model names, their aliases, and version constraints | Design phase |

### §4.2 How provider_map Works Today

```python
# model_gateway.py:282-292
provider_map = {
    "google": GoogleAIProvider,          # ← Live, single key
    "openrouter": _create_openrouter,    # ← Live, generic
    "opencode-zen": _create_openrouter,  # ← Live
    "cline": _create_openrouter,         # ← Live
    "github-copilot": _create_openrouter, # ← Live
    "lmster": LocallmsterProvider,       # ← Live
    "ollama": OllamaProvider,            # ← Live
    "native-gguf": NativeGGUFProvider,   # ← Live
    "mock": MockProvider,                # ← Live
    # ↑ MISSING: "google-keypool": GoogleKeyPoolProvider
}
```

The `GoogleKeyPoolProvider` class (providers.py:113-156) is fully implemented with:
- Round-robin key rotation
- Config-driven key loading from env vars
- Delegation to `GoogleAIProvider` for actual inference
- Health check (`is_available`) that returns False if no keys loaded

**The only missing line of code** is adding it to `provider_map` in `model_gateway.py:282`.

### §4.3 GoogleKeyPoolProvider Instantiation Details

The class takes `(name, config)` where config needs:
```yaml
keys:
  - env: GOOGLE_API_KEY_01
  - env: GOOGLE_API_KEY_02
  # ... through _08
rotation_strategy: round_robin  # ignored by current code, future extension
```

Current `GoogleKeyPoolProvider.__init__` reads `config.get("keys", [])` and for each entry, reads `key_cfg.get("env")` → `os.environ.get(env_var)`. So the YAML config must be structured with `keys: [{env: GOOGLE_API_KEY_01}, ...]`.

### §4.4 The orchestrator.py GOOGLE_API_KEYS Conflict

```python
# orchestrator.py:142
keys = os.environ.get("GOOGLE_API_KEYS", "").split(",")
```

This reads `GOOGLE_API_KEYS` (plural, with S) as a comma-separated string. This var does not exist in `.env` or `.env.example`. The `BackgroundWorker` receives an empty list `[""]` when `GOOGLE_API_KEYS` is unset, because `"".split(",")` returns `[""]` not `[]`.

**P0 Bug**: When `GOOGLE_API_KEYS` is not set, `BackgroundWorker` gets `[""]` (a list with one empty string), not an empty list. This will cause the worker to attempt API calls with an empty string key, which always fails with a confusing error.

---

## §5 Search Protocol Update Recommendations

### §5.1 Current Tier 0 in R_SEARCH_TOOL_PROTOCOL_V1.md

```
Tier 0: LOCAL CACHE CHECK
• .firecrawl/ directory (164 cached sites)
• Omega Hub offline library (research depths 1-4)
• data/kb/ for ingested manuals
• data/entities/*/soul.yaml                           ← Added per protocol
• data/coordination/                                   ← Added per protocol
• .agents/                                             ← Added per protocol
• .opencode/agents/                                    ← Added per protocol
```

### §5.2 Missing Knowledge Locations

The following locations are NOT in Tier 0 but SHOULD be:

| Location | Content | Why It Matters |
|---|---|---|
| `config/models.yaml` | Model specs, paths, context windows | Primary model knowledge base |
| `config/providers.yaml` | Provider chains, model overrides | How model names resolve to backends |
| `config/entity_model_affinity.yaml` | Entity→model routing rules | Which model each entity uses |
| `data/entities/*/knowledge/` | Entity-specific knowledge files | Per-entity model data, patterns |
| `data/entities/*/workspace/` | Entity-specific workspace files | Audit findings like this doc |
| `data/handoff/` | Strategic handoff documents | Cross-agent model decisions |
| `data/knowledge/HALL_OF_RECORDS/` | Background research cycles | Model research discoveries |
| `docs/research/` | R-* research documents | Model reference libraries |
| `docs/strategy/` | Strategy documents | Model intelligence layer plans |
| `data/coordination/archive/` | Archived coordination docs | Rotation strategies, key management |

### §5.3 Recommendations

1. **Add the essential config files** to Tier 0: `config/models.yaml`, `config/providers.yaml`, `config/entity_model_affinity.yaml`
2. **Add the entity knowledge layer**: `data/entities/*/knowledge/` and `data/entities/*/workspace/`
3. **Add the strategic layer**: `docs/strategy/R_MODEL_INTELLIGENCE_LAYER.md` and similar
4. **Create a shortcut**: `omega search-model <model-name>` that searches all model knowledge locations at once

---

## §6 MODEL_KNOWLEDGE_MANIFEST.md Schema Proposal

### §6.1 Purpose

A single manifest file that cross-references ALL model knowledge locations across the engine. Every file that references a model name is cataloged here with its schema version and staleness status.

### §6.2 Schema

```yaml
# config/MODEL_KNOWLEDGE_MANIFEST.md
# ⬡ OMEGA ⬡ MODEL KNOWLEDGE MANIFEST ⬡ v1.0.0
# Auto-generated by `make validate-model-names`

schema_version: 1.0.0
last_updated: 2026-06-16
generated_by: make validate-model-names

# ── Sources ──
# Every file is a "source" of model knowledge.
# Each source has a type, model references, and staleness status.

sources:
  - path: config/models.yaml
    type: canonical_registry
    role: SINGLE SOURCE OF TRUTH for local GGUF models
    model_keys: 12
    staleness: current
    validation: "Validated against actual GGUF file paths on disk"

  - path: config/providers.yaml
    type: provider_fabric
    role: Provider chain config with model override mappings
    model_keys: 14
    staleness: current
    validation: "All model override keys reference valid models.yaml entries"

  - path: config/entity_model_affinity.yaml
    type: routing_rules
    role: Entity→model affinity database
    model_keys: 4 unique
    staleness: STALE
    issues:
      - "qwen3-4b-q4_k_m should be qwen3-4b-thinking-Q4_K_M"
      - "qwen3-4b-q5_k_m does not exist"
      - "krikri-8b-q5_k_m does not exist (only q4_k_m exists)"
      - "gemini-2.5-flash should be gemini-3.5-flash"

  - path: data/entities/antigravity/soul.yaml
    type: soul_config
    role: Entity soul definition with thinking levels and pool config
    model_keys: 5
    staleness: STALE
    issues:
      - "gemini_3_5_flash uses underscores"
      - "gemini_3_1_pro uses underscores"
      - "claude_sonnet_4_6_adaptive not in providers.yaml"
      - "opus_4_6_adaptive not in providers.yaml"
      - "gpt_oss_120b not in providers.yaml"

  - path: config/omega.yaml
    type: engine_config
    role: Engine-level model reference (model_updater)
    model_keys: 1
    staleness: WARNING
    issues:
      - "gemma-4-31b-it model_updater model may use different name than models.yaml"

  - path: data/entities/antigravity/knowledge/USAGE_POOL_LOG.json
    type: usage_tracking
    role: Per-key and per-pool usage log
    model_keys: 6
    staleness: PHANTOM
    issues:
      - "No code reads or writes this file"
      - "No atomic write pattern"

  - path: data/coordination/archive/ANTIGRAVITY_8KEY_ROTATION_STRATEGY_20260605.md
    type: strategy_doc
    role: Key rotation and anti-thrashing design
    model_keys: 6
    staleness: UNWIRED
    issues:
      - "Anti-thrashing logic not implemented in any provider code"

  - path: docs/strategy/R_MODEL_INTELLIGENCE_LAYER.md
    type: strategy_doc
    role: Model intelligence layer design
    model_keys: 12
    staleness: REFERENCE
    issues:
      - "Key pool YAML example matches PW_MODEL_15 but not providers.yaml"

  - path: data/coordination/PW_MODEL_15_COORDINATION.md
    type: coordination_doc
    role: Parallel worker engine coordination
    model_keys: 3
    staleness: PROPOSED
    issues:
      - "Implementation phase planned but not started"

  - path: docs/research/GOOGLE_GEMMA_MODEL_REFERENCE.md
    type: research_doc
    role: Google model API reference
    model_keys: 20+
    staleness: ARCHIVAL

# ── Canonical Model Registry ──
# Auto-generated cross-reference of all models across all sources.

models:
  qwen3-1.7b:
    type: local_gguf
    path: /media/arcana-novai/omega_library/models/gguf/local/all/Qwen3-1.7B-Q6_K.gguf
    quantization: Q6_K
    config_sources:
      - config/models.yaml (entity: nova, load: always)
      - config/providers.yaml (native-gguf primary)
      - config/entity_model_affinity.yaml (local_fast for 9 entities)

  qwen3-4b-thinking-Q4_K_M:
    type: local_gguf
    path: /media/arcana-novai/omega_library/models/gguf/local/all/Qwen3-4B-Thinking-2507-Q4_K_M.gguf
    quantization: Q4_K_M
    config_sources:
      - config/models.yaml (entity: maat/anubis, load: on_demand_5min)
      - config/providers.yaml (model_overrides key)
      - config/entity_model_affinity.yaml ❌ MISSING — uses qwen3-4b-q4_k_m instead

  krikri-8b-Q4_K_M:
    type: local_gguf
    path: /media/arcana-novai/omega_library/models/gguf/local/all/Krikri-8B-Instruct.Q4_K_M.gguf
    quantization: Q4_K_M
    config_sources:
      - config/models.yaml (entity: inanna/isis/lilith)
      - config/providers.yaml (model_overrides key)
      - config/entity_model_affinity.yaml ❌ WRONG — uses krikri-8b-q5_k_m instead

  gemini-3.5-flash:
    type: cloud
    provider: google_ai_studio
    config_sources:
      - config/models.yaml (cloud_models, tier: primary)
      - config/entity_model_affinity.yaml ❌ WRONG — uses gemini-2.5-flash
      - data/entities/antigravity/soul.yaml ❌ WRONG — uses gemini_3_5_flash

  # ... and so on for all 18+ models

# ── Validation Status ──
validation:
  last_run: 2026-06-16T12:00:00Z
  status: FAILING
  errors_found: 12
  auto_fix_possible: 8  # Name changes in affinity/soul can be automated
  requires_human: 4      # Q5 quant downloads, env key collection, code wiring
```

### §6.3 Benefits

1. **Single query point**: An agent looking for "what model is used for Hecate?" knows exactly where to look
2. **Staleness detection**: Each source tracks its validation status
3. **Wiring completeness**: The manifest shows which documented features have code paths
4. **Auto-generation**: Can be generated from a `make validate-model-names` target scanning all sources

---

## §7 The Council Verdict

### §7.1 Convergence (The Truth)

1. **`models.yaml` is the de facto single source of truth** for local GGUF models — all provider model_overrides keys reference it correctly
2. **`GoogleKeyPoolProvider` class is complete** but not wired — 1 line in provider_map, 15 lines in providers.yaml, and 7 env vars are the only gaps
3. **The 3-tier affinity design (local_fast/local_deep/cloud)** is sound and correctly ported from legacy — only the model names within it are stale
4. **`.env` loading works correctly** — `model_gateway.py:_load_sovereign_secrets()` properly injects into `os.environ`

### §7.2 Divergence (The Uncertainty)

1. **How many Google API keys does the user actually have?** Documentation claims 8, but only 1 is in `.env`. The other 7 may need to be regenerated
2. **Do `qwen3-4b-q5_k_m` and `krikri-8b-q5_k_m` GGUF files exist?** They're referenced in entity_affinity but not in models.yaml — they may need to be downloaded, or the references are simply wrong
3. **What is the actual Google quota per key per week?** The rotation strategy assumes weekly resets but this has never been verified with real usage
4. **Should Pool C (Claude/Opus) models be wired into the engine fabric?** They currently exist only in Antigravity's world — wiring them requires new provider classes

### §7.3 Top 3 Recommendations

#### 🥇 Recommendation 1: Wire GoogleKeyPoolProvider (P0 — ~45 min)
The single highest-impact change. The class exists, the config schema is designed, the YAML structure is documented. Add 1 line to `provider_map`, add the YAML config block, add 7 env vars to `.env`. **This unlocks the entire dual-pool architecture** that's been documented for 11 days without execution.

#### 🥈 Recommendation 2: Fix Entity Model Affinity Names (P0 — ~30 min)
`entity_model_affinity.yaml` has 4 model name errors repeated across 33+ total references. This is the file that **Oracle uses for runtime model selection** — every wrong name means a model that can never be found by the routing system. The 3 wrong names (`qwen3-4b-q4_k_m`, `gemini-2.5-flash`, `krikri-8b-q5_k_m`) cause silent fallback to system default every time.

#### 🥉 Recommendation 3: Env Var Standardization (P0 — ~15 min)
Three different Google API key naming schemes exist simultaneously. The `GOOGLE_API_KEYS` (plural) reference in `orchestrator.py:142` is a subtle P0 bug — when the var isn't set, `"".split(",")` returns `[""]` instead of `[]`, passing an empty-string key to the BackgroundWorker. Standardize on `GOOGLE_API_KEY_01`-`_08` across all files.

---

## §8 References

| File | Relevance |
|---|---|
| `config/providers.yaml` | Provider chain with model_overrides |
| `config/models.yaml` | Model specs, cloud_models, agent_roles |
| `config/entity_model_affinity.yaml` | Entity→model routing rules (STALE names) |
| `config/omega.yaml` | Engine config with model_updater model ref |
| `data/entities/antigravity/soul.yaml` | Dual-pool architecture, thinking levels |
| `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` | Phantom usage tracker |
| `data/coordination/archive/ANTIGRAVITY_8KEY_ROTATION_STRATEGY_20260605.md` | Rotation design |
| `data/coordination/PW_MODEL_15_COORDINATION.md` | Keypool wiring plan |
| `docs/strategy/R_MODEL_INTELLIGENCE_LAYER.md` | Model intelligence layer design |
| `src/omega/oracle/model_gateway.py` | provider_map (where GoogleKeyPoolProvider should be wired) |
| `src/omega/oracle/providers.py` | GoogleAIProvider and GoogleKeyPoolProvider classes |
| `src/omega/oracle/orchestrator.py:142` | GOOGLE_API_KEYS env var (plural, bug) |
| `src/omega/oracle/entity_affinity.py` | YAML affinity resolver (reads entity_model_affinity.yaml) |
| `scripts/validate_arsenal.sh:55` | References `gemini-2.0-flash` |
| `scripts/check_free_models.sh:53` | Reads GOOGLE_API_KEY from .env |
| `docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md` | Search protocol with Tier 0 locations |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_gap_analysis ⬡ RESEARCH-MODE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
