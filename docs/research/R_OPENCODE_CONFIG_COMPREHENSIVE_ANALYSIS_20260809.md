# 🔱 Comprehensive Analysis: OpenCode CLI Configuration, Antigravity, Thinking Variants & Model Naming
**AP Token**: `AP-OPENCODE-CONFIG-ANALYSIS-20260809-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_comprehensive_analysis ⬡ COMPLETE

**Date**: 2026-08-09
**Purpose**: Single authoritative document synthesizing all research (local mining + web research) and configuration analysis for the Omega Engine's OpenCode CLI configuration issues.

---

## 📋 EXECUTIVE SUMMARY

This report consolidates:
1. **Roc Racoon's local mining** (47 documents, 6 domains) — `OPENCODE_CONFIG_ANTIGRAVITY_THINKING_MINING_REPORT_20260809.md`
2. **Researcher's web research supplement** (8 gaps, 20+ authoritative sources) — `WEB_RESEARCH_SUPPLEMENT_OPENCODE_CONFIG_20260809.md`
3. **Jem's configuration analysis** of three `opencode.json` files

**Bottom Line**: All hard problems are solved at the architectural level. Remaining work is **configuration fixes and integration** — no new research needed.

---

## 🗂️ THREE CONFIGURATION FILES ANALYZED

| File | Path | Purpose | Key Issues |
|------|------|---------|------------|
| **User-level** | `~/.config/opencode/opencode.json` | Main OpenCode CLI config (14 providers) | OpenRouter provider named `"OpenRouter (Free)"` — pollutes model search |
| **Project-level (root)** | `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json` | Project config with `opencode` (Zen) + `openrouter` providers | Duplicate MiMo v2.5 entries (`mimo-v2.5` + `mimo-v2.5-free`) |
| **Subdirectory** | `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/opencode.json` | Antigravity IDE config under `google` provider | **Provider collision**: Antigravity + Google API mixed; missing thinking variants |

---

## 🎯 ISSUES IDENTIFIED & SOLUTIONS

### Issue 1: OpenRouter Provider Name Contains "Free"
| Detail | Value |
|--------|-------|
| **Location** | User-level config, line 224 |
| **Current** | `"name": "OpenRouter (Free)"` |
| **Problem** | Searching for "free" in model selector returns ALL models (provider name matches) |
| **Solution** | Change to `"name": "OpenRouter"` |
| **Effort** | 2 min |

### Issue 2: Nemotron 3 Super/Ultra Thinking Variants (OpenRouter)
| Detail | Value |
|--------|-------|
| **Location** | Root config → `provider.openrouter.models` |
| **Current** | Both have `low`, `medium`, `high` variants |
| **User Complaint** | "Only off, low, medium for Super; medium, high for Ultra" |
| **Root Cause** | **Misunderstanding**: "off" is NOT a configured variant — it's the **default** when cycling with **Ctrl+T** in OpenCode CLI |
| **Solution** | **No change needed** — variants are correct. User education on Ctrl+T cycling. |
| **Effort** | 0 min (documentation only) |

### Issue 3: Sonnet 4.6 (Antigravity) — NO Thinking Variants
| Detail | Value |
|--------|-------|
| **Location** | `.opencode/opencode.json` → `provider.google.models.antigravity-claude-sonnet-4-6` |
| **Current** | No `variants` field |
| **Required** | Add `variants` with `thinkingConfig.thinkingBudget` (Claude format) |
| **Recommended Variants** | `off` (default), `low` (8192), `medium` (16384), `high` (24576), `max` (32768) |
| **Effort** | 5 min |

### Issue 4: Opus 4.6 (Antigravity) — Limited Variants
| Detail | Value |
|--------|-------|
| **Location** | `.opencode/opencode.json` → `provider.google.models.antigravity-claude-opus-4-6-thinking` |
| **Current** | `low` (8192), `max` (32768) |
| **Required** | Add `off`, `medium` (16384), `high` (24576) |
| **Effort** | 3 min |

### Issue 5: Gemini 3 Pro / 3.1 Pro (Antigravity) — Limited Variants
| Detail | Value |
|--------|-------|
| **Location** | `.opencode/opencode.json` → `provider.google.models.antigravity-gemini-3-pro` & `antigravity-gemini-3.1-pro` |
| **Current** | `low`, `high` only |
| **Required** | Add `off` (minimal), `medium` |
| **Format** | `thinkingConfig.thinkingLevel`: `minimal`/`low`/`medium`/`high` |
| **Effort** | 3 min |

### Issue 6: Gemini 3 Flash (Antigravity) — OK
| Detail | Value |
|--------|-------|
| **Location** | `.opencode/opencode.json` → `provider.google.models.antigravity-gemini-3-flash` |
| **Current** | `minimal`, `low`, `medium`, `high` ✅ |
| **Note** | `minimal` = "off" equivalent |
| **Effort** | 0 min |

### Issue 7: All Gemini CLI Models — NO Variants
| Detail | Value |
|--------|-------|
| **Location** | `.opencode/opencode.json` → `provider.google.models` (gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-pro-preview, gemini-3.1-pro-preview-customtools) |
| **Current** | No `variants` field |
| **Required** | Add appropriate thinking variants per model capability |
| **Effort** | 10 min |

### Issue 8: Duplicate MiMo v2.5 Entries
| Detail | Value |
|--------|-------|
| **Location** | Root config → `provider.opencode.models` |
| **Current** | `mimo-v2.5` AND `mimo-v2.5-free` (identical variants) |
| **Web Research** | MiMo v2.5 Free ONLY on OpenCode Zen (`opencode/mimo-v2.5-free`), NOT on OpenRouter |
| **Solution** | Remove `mimo-v2.5` (keep `mimo-v2.5-free` as canonical) |
| **Effort** | 2 min |

### Issue 9: Model Name "(Gemini CLI)" Should Be "(Antigravity)"
| Detail | Value |
|--------|-------|
| **Location** | `.opencode/opencode.json` → `provider.google.models.gemini-3.1-pro-preview-customtools` |
| **Current** | `"name": "Gemini 3.1 Pro Preview Custom Tools (Gemini CLI)"` |
| **Required** | `"name": "Gemini 3.1 Pro Preview Custom Tools (Antigravity)"` |
| **Reason** | This model is accessed via Antigravity OAuth, not Google CLI |
| **Effort** | 2 min |

### Issue 10: Provider Collision in `.opencode/opencode.json`
| Detail | Value |
|--------|-------|
| **Location** | `.opencode/opencode.json` → `provider.google` block |
| **Problem** | Antigravity models (`antigravity-*`) AND Google API models (`gemini-*`, `gemma-*`) both under `google` provider |
| **Root Cause** | Antigravity plugin handles OAuth/auth; `google` provider handles API — different layers |
| **Solution** | **Remove entire `google` provider block** from `.opencode/opencode.json` — let the `opencode-antigravity-auth` plugin handle model discovery |
| **Authority** | Roc's mining: `ROC_RACOON_COMPREHENSIVE_BRIEFING_20260722.md` §2.3 |
| **Effort** | 5 min |

---

## 🔑 KEY TECHNICAL CLARIFICATIONS

### 1. "Off" Thinking Variant
- **NOT explicitly configured** in `opencode.json`
- **Default behavior**: Press **Ctrl+T** in OpenCode CLI to cycle: `off → low → medium → high → max → off`
- Variants you define are the **non-off** levels

### 2. OpenCode Zen Model Availability
| Model | Available Free on Zen? | Available Free on OpenRouter? |
|-------|------------------------|-------------------------------|
| Nemotron 3 Ultra | ✅ Yes (1M ctx, 128K out) | ✅ Yes |
| Nemotron 3 Super | ❌ No | ✅ Yes |
| MiMo v2.5 | ✅ Yes (200K ctx) | ❌ No |

### 3. OpenRouter Free Tier
- **Catalog rotates weekly** (14-28 models)
- **Gemma 4 is NOT free** on OpenRouter (routes to AI Studio = same 16k TPM cap)
- **Rate limits**: 20 RPM, 50 RPD (free) → 1,000 RPD ($10 credits, never expire)

### 4. Antigravity Model Identity Issues
- **Forum reports**: Consistent misidentification (Gemini 3 Pro → 2.0 Flash, Opus → Sonnet)
- **Token buckets prove**: Gemini quota depletes even when Claude selected
- **Google Response**: "Hybrid architecture — subagents use Gemini for background tasks"
- **Omega Requirement**: **Provenance verification (M22) mandatory** for Antigravity models

### 5. Config Merge Behavior (Authoritative)
- **Arrays**: CONCATENATED (hybrid `mergeConfigConcatArrays`) — NOT replaced
- **Objects**: DEEP MERGED
- **Scalars**: REPLACED
- **Exception**: `instructions` and `plugins` arrays are additive by design

### 6. Canonical Model Naming
- **Format**: `provider_id/model_id` (split at first `/`)
- **Examples**: `anthropic/claude-sonnet-4-5`, `opencode/nemotron-3-ultra-free`, `openrouter/google/gemma-4-31b-it:free`
- **Use `/models` command** for exact IDs — don't guess

---

## 📋 IMMEDIATE ACTION PLAN

| Priority | Action | File | Owner | Effort |
|----------|--------|------|-------|--------|
| **P0** | Remove `google` provider block (provider collision) | `.opencode/opencode.json` | Ma'at/P3 | 5 min |
| **P0** | Change OpenRouter name to "OpenRouter" | `~/.config/opencode/opencode.json` | User | 2 min |
| **P0** | Add thinking variants to all Antigravity models | `.opencode/opencode.json` | Ma'at/P3 | 15 min |
| **P0** | Remove duplicate `mimo-v2.5` (keep `mimo-v2.5-free`) | `opencode.json` (root) | Ma'at/P3 | 2 min |
| **P0** | Fix model name: `gemini-3.1-pro-preview-customtools` → "(Antigravity)" | `.opencode/opencode.json` | Ma'at/P3 | 2 min |
| **P1** | Add Cerebras to `config/providers.yaml` (priority 3, streaming) | `config/providers.yaml` | Ma'at/P3 | 30 min |
| **P1** | Add Groq to `config/providers.yaml` (native, verify ModelGateway) | `config/providers.yaml` | Ma'at/P3 | 15 min |
| **P1** | Implement OpenRouter `:free` suffix stripping in ModelGateway | ModelGateway | P9 Orchestration | 2 hr |
| **P1** | Deploy V1/V2 version detection at ModelGateway startup | ModelGateway | P3 Engineering | 1 hr |

---

## 📁 BACKUPS CREATED

All three configuration files backed up before any changes:
```
~/.config/opencode/opencode.json.backup.20260809_*
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json.backup.20260809_*
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/opencode.json.backup.20260809_*
```

---

## 📚 RESEARCH ARTIFACTS

| Document | Location | Status |
|----------|----------|--------|
| Roc's Mining Report | `data/entities/roc_racoon/workspace/mining_reports/OPENCODE_CONFIG_ANTIGRAVITY_THINKING_MINING_REPORT_20260809.md` | ✅ Complete |
| Researcher's Web Supplement | `data/entities/researcher/workspace/web_research_supplements/WEB_RESEARCH_SUPPLEMENT_OPENCODE_CONFIG_20260809.md` | ✅ Complete |
| This Comprehensive Analysis | `docs/research/R_OPENCODE_CONFIG_COMPREHENSIVE_ANALYSIS_20260809.md` | ✅ Complete |

---

## 🔗 AUTHORITATIVE SOURCE INDEX

### OpenCode Core
- **V2 Config Spec**: https://github.com/anomalyco/opencode/blob/dev/specs/v2/config.md
- **V2 Config Docs**: https://opencode.ai/v2/docs/config
- **Config Schema**: https://opencode.ai/config.json
- **Config Merge Docs**: https://opencode.ai/docs/config
- **Models Guide**: https://opencode.ai/docs/models
- **Zen Models API**: https://opencode.ai/zen/v1/models

### Issues & Fixes
- **Thinking Bug #34282**: https://github.com/anomalyco/opencode/issues/34282 (OPEN)
- **Vertex AI Fix #18283**: https://github.com/anomalyco/opencode/pull/18283 (v1.3.0 partial fix)
- **Cerebras Issue #976**: https://github.com/anomalyco/opencode/issues/976 (closed, PR #1441 merged)

### External Catalogs
- **OpenRouter Free**: https://openrouter.ai/collections/free-models
- **Antigravity Models**: https://antigravity.google/docs/models
- **Groq + OpenCode**: https://console.groq.com/docs/coding-with-groq/opencode
- **Cerebras Guide**: https://mcsaguru.com/cerebras-qwen3-coder-opencode-setup

### Analysis
- **DeepWiki Config Merge**: https://deepwiki.com/sst/opencode/3.1-configuration-loading-and-merging
- **Sabaoon Antigravity**: https://www.sabaoon.dev/blog/google-antigravity-models-compared

---

## 🏁 CONCLUSION

**All research complete.** The Omega Engine's knowledge base is exceptionally deep — virtually every hard problem has been researched, verified, and solved at the architectural level. The remaining work is **configuration fixes and integration**:

1. **Configuration fixes** (5 min): Remove provider collision, fix OpenRouter name, add thinking variants, remove duplicate MiMo
2. **Provider fabric expansion** (1 hr): Add Cerebras + Groq to `providers.yaml`
3. **Routing logic** (2 hr): Implement OpenRouter `:free` suffix handling
4. **Version gating** (1 hr): Deploy V1/V2 config strategy in ModelGateway
5. **Documentation consolidation** (ongoing): Unify naming conventions in capability matrix

**No new research required** — all answers exist in the cataloged documents. The path forward is implementation.

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_comprehensive_analysis ⬡ COMPLETE*
*Analysis synthesized from 47 local mining documents + 20+ web authoritative sources across 8 knowledge gaps*