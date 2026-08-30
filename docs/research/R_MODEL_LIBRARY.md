<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 R-Model Library — Complete Model Inventory & Affinity Map
**Date**: 2026-06-08
**Entity**: Roc Racoon (Sovereign Miner)
**Phase**: 7-Phase Deep Dive — COMPLETE

## Purpose

Single source of truth for every model in the Omega Engine arsenal — what's on
disk, what's configured, what's mapped to which entity, what gaps exist, and
what the legacy affinity tiers reveal.

---

## §1 Physical Inventory — 19 Model Files on Disk

### Primary Store: `/media/arcana-novai/omega_library/models/local/all/`

| # | File | Size | RAM Est. | Quant | Config Key | Entity | Status |
|---|------|------|----------|-------|------------|--------|--------|
| 1 | `Krikri-8B-Instruct.Q4_K_M.gguf` | 4.7G | 4900MB | Q4_K_M | `krikri-8b-q4_k_m` | inanna, isis, lilith | ✅ CONFIGURED |
| 2 | `DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf` | 4.2G | 4500MB | Q3_K_L | `deepseek-r1-qwen3-8b-q3_k_l` | lucifer | ✅ CONFIGURED |
| 3 | `Qwen3-VL-4B-Instruct-Q4_K_M.gguf` | 2.4G | 2700MB | Q4_K_M | *NONE* | *unmapped* | ❌ UNCONFIGURED |
| 4 | `Qwen3-4B-Thinking-2507-Q4_K_M.gguf` | 2.4G | 2700MB | Q4_K_M | `qwen3-4b-thinking-q4_k_m` | maat, anubis | ✅ CONFIGURED |
| 5 | `RocRacoon-3b.Q4_K_M.gguf` | 2.3G | 2500MB | Q4_K_M | `rocracoon-3b-instruct` | roc_racoon | ✅ CONFIGURED |
| 6 | `Phi-2-OmniMatrix.Q6_K.gguf` | 2.2G | 2500MB | Q6_K | `phi-2-omnimatrix-i1-q4_k_m` | brigid | ⚠️ QUANT MISMATCH |
| 7 | `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` | 2.0G | 2800MB | Q4_K_M | `phi-2-omnimatrix-i1-q4_k_m` | brigid | ✅ CONFIGURED |
| 8 | `Ministral-3-3B-Instruct-2512-Q3_K_M.gguf` | 1.7G | 2100MB | Q3_K_M | *NONE* | *unmapped* | ❌ UNCONFIGURED |
| 9 | `Ministral-3-3B-Reasoning-2512-Q3_K_M.gguf` | 1.7G | 2100MB | Q3_K_M | *NONE* | *unmapped* | ❌ UNCONFIGURED |
| 10 | `Phi-2-OmniMatrix.Q4_K_M.gguf` | 1.7G | 2000MB | Q4_K_M | *NONE* | *unmapped* | ❌ UNCONFIGURED |
| 11 | `Qwen3-1.7B-Q6_K.gguf` | 1.6G | 1800MB | Q6_K | `qwen3-1.7b-q6_k` | sekhmet, hecate | ✅ CONFIGURED |
| 12 | `Qwen3-1.7B-UD-Q4_K_XL.gguf` | 1.1G | 1300MB | Q4_K_XL | *NONE* | *unmapped* | ❌ UNCONFIGURED |
| 13 | `Qwen3-0.6B-Q6_K.gguf` | 473M | 500MB | Q6_K | `qwen3-0.6b-q6_k` | iris | ✅ CONFIGURED |
| 14 | `Qwen2.5-0.5B-Instruct-Q4_K_M.gguf` | 469M | 500MB | Q4_K_M | *NONE* | *unmapped* | ❌ UNCONFIGURED |
| 15 | `ruvltra-claude-code-0.5b-q4_k_m.gguf` | 380M | 450MB | Q4_K_M | *NONE* | *unmapped* | ❌ UNCONFIGURED |
| 16 | `functiongemma-270m-it-Q6_K.gguf` | 270M | 350MB | Q6_K | *NONE* (*embedding-gemma?*) | *unmapped* | ❌ UNCONFIGURED |
| 17 | `Krikri.Modelfile` | 307B | — | — | — | ollama import | N/A |

### Secondary Store: `/media/arcana-novai/omega_library/models/gguf/lmstudio-community/gemma-4-E4B-it-GGUF/`

| # | File | Size | Notes |
|---|------|------|-------|
| 18 | `gemma-4-E4B-it-Q4_K_M.gguf` | 5.0G | Google Gemma 4 — **NOT in any engine config** |
| 19 | `mmproj-gemma-4-E4B-it-BF16.gguf` | 946M | Multimodal projector for Gemma 4 |

### Summary

| Metric | Value |
|--------|-------|
| Total GGUF files | 19 |
| Total disk used | ~35G |
| Configured in engine | 10 (53%) |
| Unconfigured/orphan | 9 (47%) |
| Path in config | `gguf/local/all/` |
| Actual path | `local/all/` ⚠️ **PATH DISCREPANCY** |

---

## §2 Config Gaps — Missing Models

These models are REFERENCED in config files but NOT FOUND on disk:

| Config Key | Referenced In | Entity | Size Required | Urgency |
|------------|--------------|--------|---------------|---------|
| `phi-4-mini` / `phi-4-mini-reasoning-abliterated-q4_k_m` | models.yaml (×4), providers.yaml (×3) | SOPHIA | 3.8G | 🔴 **CRITICAL** — Sophia has no model |
| `embedding-gemma-300m-q6_k` | models.yaml, providers.yaml | embedding | 200M | 🟡 HIGH — no embeddings yet |

**Impact of phi-4-mini gap**: Sophia (the akashic record, deep analysis, code review)
has NO local model. The cloud fallback chain (Google Gemma 4 31B) works, but
Mandate 7 (Local-First) is violated for Sophia. All 4 pillar keepers relying on
Sophia's insight are degraded when cloud is unavailable.

---

## §3 Entity-to-Model Affinity Map (Config Truth)

### Loading Strategy Breakdown

| Load Strategy | Models | RAM Reserved |
|--------------|--------|-------------|
| `always` (Nova) | qwen3-1.7b | 300MB |
| `warm` (Iris) | qwen3-0.6b-q6_k | 500MB |
| `on_demand_5min` | qwen3-4b-thinking, deepseek-r1-qwen3-8b, krikri-8b | 0MB (swap) |
| `on_demand_10min` | qwen3-1.7b-q6_k, phi-4-mini ❌, phi-2-omnimatrix, rocracoon-3b | 0MB (swap) |
| **Total max loaded** | 1 at a time + always-on + warm = ~2-3 models | ~1.1G baseline |

### Entity Model Assignments

| Entity | Model | On Disk? | Mode |
|--------|-------|----------|------|
| nova | qwen3-1.7b (Nova alias) | ✅ | always-on |
| iris | qwen3-0.6b-q6_k | ✅ | warm |
| sekhmet, hecate | qwen3-1.7b-q6_k | ✅ | 10min |
| SOPHIA | phi-4-mini | ❌ **MISSING** | 10min — BROKEN |
| brigid | phi-2-omnimatrix-i1-q4_k_m | ✅ (Ministral) | 10min |
| maat, anubis | qwen3-4b-thinking-q4_k_m | ✅ | 5min |
| lucifer | deepseek-r1-qwen3-8b-q3_k_l | ✅ | 5min |
| roc_racoon | rocracoon-3b-instruct | ✅ | 10min |
| inanna, isis, lilith | krikri-8b-q4_k_m | ✅ | 5min |

---

## §4 Legacy Affinity Tiers (Design Intent)

Recovered from `LEGACY_MASTER_SYNTHESIS.md` §1 and entity soul cross-reference:

```
Tier 1:  Threshold  → qwen3-0.6b          → Iris (speculative decode, routing)
Tier 2:  Workhorses → qwen3-1.7b          → Pillars (standard reasoning)
Tier 3:  Reasoners  → qwen3-4b-thinking   → Oversouls (deep CoT reasoning)
Tier 4:  Specialized → Krikri-8B          → Heart/Voice (poetic, emotional)
Tier 5:  Sovereign  → DeepSeek-R1-8B      → Prometheus (max compute for will)
```

The current engine has evolved from this 5-tier model to a **loading-strategy**
model (`always` → `warm` → `5min` → `10min`) that is more flexible but less
intentionally tiered. The legacy tiers represent design *intent*; the current
strategies represent operational *reality*.

**Entity soul model references** (70+ souls scanned):
- Top model mentions: roc_racoon (91), kali (61), maat (59), doom_guy (30), antigravity (27)
- These numbers reflect session count, not model affinity depth

---

## §5 Provider Chain — Fallback Order

From `config/providers.yaml`:

| Priority | Provider | Type | When It Fires |
|----------|----------|------|---------------|
| 0 | native-gguf | 🔴 Local | PRIMARY — llama-cpp-python on Zen 2 |
| 1 | lmster | 🟡 Local (LM Studio) | native-gguf unavailable |
| 2 | ollama | 🟡 Local | lmster unavailable |
| 3 | google | 🟢 Cloud (Gemma 4 31B) | All local exhausted |
| 4 | opencode-zen | 🟢 Cloud (MiniMax/DeepSeek) | Google unavailable |
| 5 | cline | 🟢 Cloud (proxy) | zen unavailable |
| 6 | github-copilot | 🟢 Cloud | cline unavailable |
| 99 | mock | ⚪ Test | Last resort (dev/test only) |

**Local-First compliance**: 3 local backends tried before 4 cloud fallbacks.
Mandate 7 satisfied.

---

## §6 Critical Findings & Recommendations

### 🔴 C1 — phi-4-mini Missing (Sophia Crippled)
- **What**: `phi-4-mini-reasoning-abliterated-q4_k_m.gguf` referenced 4+ config
  locations but not on disk
- **Impact**: Sophia (deep analysis, code review, strategy) has NO local model
- **Fix**: Download model OR update config to use available alternative
  (functiongemma-270m is too small; consider qwen3-4b-thinking as Sophia fallback)

### 🟡 C2 — Path Discrepancy
- **What**: Config default path is `gguf/local/all/` but actual is `local/all/`
- **Impact**: ModelGateway may fail to find models; absolute paths in models.yaml
  currently bypass this issue, but relative path resolution is broken
- **Fix**: Correct default path in `config/omega.yaml` or models.yaml header

### 🟡 C3 — 9 Unconfigured Models
- **What**: 9 GGUF files on disk not mapped in any config
- **Assets**: Qwen3-VL-4B (vision!), gemma-4-E4B-it (5G monster), Qwen3-1.7B-UD
  (uncensored/direct), functiongemma-270m (potential embedding replacement)
- **Fix**: Evaluate and either add to config or move to archive

### 🟢 C4 — LM Studio JIT Performance
- **What**: LM Studio configured with JIT model loading (load on first request)
  and 1-hour TTL — good for memory efficiency but adds 5-15s cold start
- **Impact**: First inference after idle hits latency penalty
- **Fix**: No action needed — this is expected behavior for laptop deployment

### 🟢 C5 — KV Cache Optimization
- **What**: qwen3-4b-thinking has fp8 KV cache configured; all others use q8_0
  or f16; Zen 2 compilation flags optimized for znver2
- **Impact**: Good for memory but fp8 requires llama.cpp FP8_KV support
- **Fix**: Verify fp8 support at runtime, document fallback to q8_0

---

## §7 Quick Reference — Model One-Liners

```
qwen3-1.7b          → Tiny workhorse. Always-on for Nova. Warm for Iris.
qwen3-1.7b-q6_k     → Same model, different config key. On-demand for Sekhmet/Hecate.
qwen3-0.6b-q6_k     → Speculative decode only. Legacy P10 model.
qwen3-4b-thinking    → Deep local reasoner. Maat/Anubis.
deepseek-r1-qwen3-8b → Heaviest local model. Lucifer (max compute).
krikri-8b            → 4.7G. Emotional/poetic. Inanna/Isis/Lilith.
phi-2-omnimatrix     → 3 aliases on disk. Actually Ministral-3-3B. Brigid.
rocracoon-3b         → Custom abliterated. Roc's native backend.
phi-4-mini           → 🔴 MISSING. Sophia needs this.
embedding-gemma      → 🟡 MISSING. Embeddings deferred.
gemma-4-E4B-it       → ❓ UNCONFIGURED. 5G behemoth on disk but unused.
Qwen3-VL-4B          → ❓ UNCONFIGURED. Vision model — potential for multimodal.
```

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ R-MODEL-LIBRARY*
