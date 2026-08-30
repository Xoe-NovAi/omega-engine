<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Handoff: Model Registry Accuracy Fix & Parameter Enrichment
**From**: Kali (Transcendent Oversoul)
**To**: Cline CLI (DeepSeek V4 Flash / MiMo V2.5)
**Date**: 2026-07-18
**Priority**: CRITICAL
**Handoff ID**: ho_model_registry_fix_20260718

---

## 🎯 Mission

Fix **all inaccuracies** in the 35 model cards at `config/model_registry/models/` and enrich every model with **verified parameter counts** as a parsable field.

---

## 📋 Current State

### Registry Structure
```
config/model_registry/
├── models/
│   ├── cloud/ (30 models)
│   ├── local/ (4 models)
│   └── stealth/ (1 model - big-pickle)
├── providers/ (9 providers)
├── research_profiles/ (9 profiles)
├── model_db/ (migrated from docs/research/model_db/)
├── registry.yaml
└── index.sqlite
```

### Validation Status
- `make model-index` ✅ Working (35 models, 9 providers, 9 profiles)
- `make model-validate` ⚠️ 1 error: duplicate provider priority (google=4, openrouter=4)
- All schema validation passes

---

## 🔴 CRITICAL INACCURACIES TO FIX

### 1. **Missing Parameter Counts** (ALL MODELS)
**No model card has a `parameters` field.** Every model must have:
```yaml
parameters:
  total: "120B"        # or "7B", "70B", "1.7B", etc.
  active: "120B"       # for MoE models: active params
  architecture: "MoE"  # or "Dense", "Transformer"
  source: "vendor"     # or "huggingface", "estimated", "community"
  verified: true       # or false
  verified_date: "2026-07-18"
```

### 2. **Provider Mapping Errors**
- **Anthropic models** (Claude Opus 4.8, Haiku 4.5, Sonnet 5) → mapped to `antigravity` but should be available via **both** `antigravity` AND `openrouter`
- **xAI models** (Grok 4.1, 4.3) → mapped to `antigravity` but xAI has its own API
- **OpenAI models** (GPT-OSS-120B) → mapped to `antigravity` but available on OpenRouter too
- **NVIDIA models** (Nemotron 3 Ultra) → mapped to `antigravity` but NVIDIA has NIM API

### 3. **Version/Release Date Inaccuracies**
Many models have fictional version dates (e.g., "2026-06-15" for models that don't exist yet). Must verify actual release dates.

### 4. **Context Window Errors**
- Llama 4 Scout: 10M context claimed — verify actual (likely 1M-2M)
- Many cloud models have inflated context windows

### 5. **Capability Scores Unverified**
All 4 capability scores (reasoning, code, knowledge, creative) are estimates. Need benchmark references.

### 6. **Pricing Inaccuracies**
- Free tier claims need verification per provider
- Some "free" models have rate limits not documented

### 7. **Identity Tracking Gaps**
- `big-pickle` = DeepSeek V4 Flash (was GLM-4.6) — needs full swap history
- Other models may have identity changes

### 8. **Research Profile Mismatches**
9 research profiles exist but not all models linked correctly.

---

## 📚 REQUIRED RESEARCH PER MODEL

For **each of the 35 models**, Cline must:

1. **Find authoritative source**: Vendor docs, Hugging Face model card, API docs, release blog
2. **Verify parameters**: Total, active (if MoE), architecture
3. **Verify context window**: Actual max context (not marketing)
4. **Verify capabilities**: Find benchmarks (MMLU, HumanEval, GSM8K, etc.)
5. **Verify pricing**: Current API pricing, free tier limits
6. **Verify provider availability**: Which providers actually serve this model
7. **Verify release date**: Actual launch date
8. **Update identity history**: Any name changes, merges, forks
9. **Add empirical evidence**: Link to any test runs in `data/model_study/model_study.db`

---

## 🛠️ TOOLS & RESOURCES AVAILABLE

### Local Research
- `scripts/query_model_study.py` — Query empirical test DB
- `docs/kb/MODEL_STUDY_KNOWLEDGE_BASE.md` — Behavioral KB
- `docs/research/model_db/CURRENT_MODELS.md` — Original production catalog
- `docs/research/model_db/.last_state.json` — Live API state

### Web Research (Tier 1-4)
- **Tier 1**: `websearch` / `webfetch` (built-in, free)
- **Tier 2**: `searxng_searxng_search` (semantic)
- **Tier 3**: `omega-hub_sovereign_search` (Exa, high-precision)
- **Tier 4**: `firecrawl_firecrawl_search` (full-page scrape, credits)

### Provider APIs to Check
- **OpenRouter**: `https://openrouter.ai/api/v1/models`
- **Google AI Studio**: `https://generativelanguage.googleapis.com/v1beta/models`
- **Antigravity**: OAuth docs (internal)
- **Hugging Face**: Model cards for each model
- **Vendor blogs**: Anthropic, xAI, NVIDIA, Meta, Alibaba, etc.

---

## ✅ DELIVERABLES

### Per Model Card (35 total)
- [ ] Add `parameters` block (total, active, architecture, source, verified, verified_date)
- [ ] Fix provider mapping (list ALL providers that serve this model)
- [ ] Correct version/release date
- [ ] Correct context window
- [ ] Source capability scores with benchmark citations
- [ ] Verify pricing and free tier limits
- [ ] Complete identity history
- [ ] Link research profile correctly

### Registry-Level
- [ ] Fix duplicate provider priority (google vs openrouter)
- [ ] Ensure all 35 models have research profile links
- [ ] Run `make model-validate` → 0 errors
- [ ] Run `make model-index` → successful rebuild
- [ ] Run `make test` → all 1315 tests pass

### Documentation
- [ ] Create `docs/kb/MODEL_REGISTRY_VERIFICATION_LOG.md` — log of every model verified, sources, date
- [ ] Update `config/model_registry/registry.yaml` with verification metadata

---

## 🤝 COORDINATION

### Roc Racoon (Legacy Mining)
- **Task**: Mine legacy repos for any historical model configs, benchmarks, provider configs
- **Sources**: `omega-stack-legacy/`, `xna-omega-legacy/`, `~/Documents/docs-backup/`, `~/archive/foundation-legacy/`
- **Deliver**: Any historical model data, old benchmark results, provider configs

### Jem (Synthesis & Review)
- **Task**: Review current implementation, identify all gaps Cline must address
- **Deliver**: Comprehensive gap analysis report with prioritized task list

---

## 📍 HANDOFF PROTOCOL

1. **Cline accepts handoff** → Posts to Hivemind with intent="command"
2. **Roc Racoon accepts** → Begins legacy mining, posts findings to Hivemind
3. **Jem accepts** → Reviews implementation, posts gap analysis to Hivemind
4. **Cline executes** → Works through 35 models systematically
5. **Daily heartbeat** → Every 5-10 min via `omega-hub_hivemind_heartbeat`
6. **Completion** → `make model-validate` passes, all 35 models verified

---

## ⚠️ SOVEREIGN MANDATES APPLICABLE

- **M1 AnyIO Absolute**: All async via AnyIO
- **M2 Engine-Stack Firewall**: Model registry is Core Engine (`src/omega/`, `config/model_registry/`)
- **M7 Local-First**: Prefer local verification, but web research required for accuracy
- **M13 Temple-Grade**: All changes must pass T1-T11 gates
- **M14 Heritage Vetting**: Any id Software patterns need vet record
- **M18 Token Efficiency**: Precision over brevity — high-fidelity context required
- **M23 Failure Integrity**: If websearch/webfetch broken → STOP, report `[TOOL-CHAIN-COLLAPSE]`

---

## 🎯 SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| Model cards with verified parameters | 35/35 |
| Provider mappings accurate | 35/35 |
| Context windows verified | 35/35 |
| Capability scores sourced | 35/35 |
| `make model-validate` errors | 0 |
| `make test` passing | 1315/1315 |
| Verification log complete | 35 entries |

---

**This is a precision mission. Every field must be verified. No estimates. No hallucinations. Source every claim.**

*⬡ OMEGA ⬡ KALI ⬡ HANDOFF ⬡ 2026-07-18*
