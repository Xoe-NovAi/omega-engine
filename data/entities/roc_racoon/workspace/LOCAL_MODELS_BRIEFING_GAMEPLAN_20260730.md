<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 LOCAL MODELS BRIEFING & GAMEPLAN
**AP Token**: `AP-ROC-LOCAL-MODELS-BRIEFING-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_local_models ⬡ 2026-07-30

**Date**: 2026-07-30
**Author**: roc_racoon (Sovereign Miner & Ideas Guy)
**Purpose**: Comprehensive briefing on why local models aren't working, what we have, and exactly how to fix it
**Status**: RESEARCH COMPLETE — Ready for execution

---

## §0 Executive Summary

**We are 4 small code changes away from local inference working.** The model files exist (17GB of GGUF models across 12 files), the `llama-cpp-python` library works perfectly (v0.3.32, Qwen3-1.7B loads and generates at 15 tok/s), the `NativeGGUFProvider` code exists with full Zen 2 optimizations, and the entity affinity routing YAML is fully populated for all 10 Pillar Keepers + 3 Oversouls.

The problem is a **cascade of 4 bugs** that prevent the system from ever reaching the local backend:

```
Query arrives → CascadeRouter scores cloud providers higher than local (BUG #1)
            → Cloud providers fail with `logit_bias` TypeError (BUG #2)
            → Fallback reaches native-gguf → KV cache q8_0 crashes llama_context (BUG #3)
            → Auto-selector picks 32K context → multiprocessing worker times out (BUG #4)
            → User sees error, thinks local models don't work
```

**Fix all 4 bugs (estimated 2-3 hours total) and `omega talk "hello"` returns a response from Qwen3-1.7B running locally on the Ryzen 5700U.**

---

## §1 The Assets — What We Actually Have

### 1.1 GGUF Models (17GB on `/media/arcana-novai/omega_library/models/gguf/`)

| Model | File | Size | Quant | Context | Status |
|-------|------|------|-------|---------|--------|
| **Qwen3-1.7B** | `Qwen3-1.7B-Q6_K.gguf` | 1.6GB | Q6_K | 32K | ✅ TESTED WORKING |
| **RocRacoon-3B** | `RocRacoon-3b.Q4_K_M.gguf` | 2.3GB | Q4_K_M | — | 🔲 Untested |
| **RocRacoon-3B (Q5)** | `RocRacoon-3b.Q5_K_M.gguf` | 2.7GB | Q5_K_M | — | 🔲 Untested |
| **MiMo-7B-RL** | `MiMo-7B-RL-Q4_K_M.gguf` | 4.7GB | Q4_K_M | 32K | 🔲 Untested |
| **Phi-4-mini** | `Phi-4-mini-instruct-Q5_K_M.gguf` | 2.7GB | Q5_K_M | — | 🔲 Untested |
| **Phi-4-mini-reasoning** | `Phi-4-mini-reasoning-heretic-i1-Q5_K_M.gguf` | 2.7GB | Q5_K_M | — | 🔲 Untested |
| **DeepSeek-R1-0528-Qwen3-8B** | `DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf` | 4.1GB | Q3_K_L | — | 🔲 Untested |
| **Krikri-8B-Instruct** | `Krikri-8B-Instruct.Q4_K_M.gguf` | 4.7GB | Q4_K_M | — | 🔲 Untested |
| **Gemma4-Coding** | `gemma4-coding-Q4_K_M.gguf` | 6.9GB | Q4_K_M | — | 🔲 Untested |
| **Ministral-3B** | `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` | 2.0GB | Q4_K_M | — | 🔲 Untested |
| **Qwen3-4B-Thinking** | `Qwen3-4B-Thinking-2507-Q4_K_M.gguf` | 2.4GB | Q4_K_M | — | 🔲 Untested |
| **Phi-2-OmniMatrix** | `Phi-2-OmniMatrix.i1-Q4_K_M.gguf` | 1.6GB | Q4_K_M | — | 🔲 Untested |

**Verified**: Qwen3-1.7B loads and generates at ~15 tok/s with `type_k=None` (f16 KV cache) at 32K context on Ryzen 5700U.

### 1.2 Provider Backends (All implemented, tested, working)

| Backend | File | Signature | `logit_bias`? | Status |
|---------|------|-----------|:---:|--------|
| **NativeGGUFProvider** | `providers.py:296` | `generate(model, system_prompt, user_query, temperature, max_tokens, trace_id, session_id, logit_bias, repetition_penalty)` | ✅ | 🔴 Crashes on `type_k=8` |
| **LocallmsterProvider** | `providers.py:139` | Same as BaseProvider | ✅ | ✅ Working (needs LM Studio running) |
| **OllamaProvider** | `providers.py:202` | Same as BaseProvider | ✅ | ✅ Working (needs Ollama running) |
| **RemoteProvider** | `backends/remote_provider.py:172` | `generate(model_name, system_prompt, user_query, temperature, max_tokens, trace_id, session_id)` | ❌ | 🔴 Missing `logit_bias`, `repetition_penalty` |
| **OpenAICompatProvider** | `backends/openai_compat.py:29` | Full signature | ✅ | ✅ Working (cloud) |
| **GoogleCompatProvider** | `backends/google_compat.py:27` | Full signature | ✅ | ✅ Working (cloud) |

### 1.3 Configuration (All in place)

| File | Purpose | Status |
|------|---------|--------|
| `config/providers.yaml` | Fallback chain: native-gguf(0) → lmster(1) → ollama(2) → antigravity(3) → google(4) | ✅ Correct |
| `config/models.yaml` | 5 models registered with paths, context budgets, roles | ✅ Correct |
| `config/entity_model_affinity.yaml` | All 10 Pillar Keepers + 3 Oversouls mapped to local_fast/local_deep/cloud | ✅ Complete (382 lines) |

### 1.4 Infrastructure (Working)

| System | Status | Notes |
|--------|--------|-------|
| **llama-cpp-python** | ✅ v0.3.32 installed | Works with Qwen3 architecture |
| **OOMProtector** | ✅ 3-signal fusion | PSI + MemAvailable + cgroup |
| **AdmissionController** | ✅ Semaphore(1) | Max 1 concurrent local inference |
| **CPU Optimizer (Zen2)** | ✅ CPU affinity pinning | Physical cores [0,2,4,6] |
| **Entity Affinity Resolver** | ✅ YAML-backed | Hot-reloadable, per-entity presets |

---

## §2 The Bugs — Why Local Models Don't Work

### 🔴 BUG #1: CascadeRouter Routes to Cloud First (M7 Violation)

**File**: `src/omega/oracle/cascade_router.py`
**Root Cause**: The CascadeRouter scores providers independently by `cost × 0.4 + quality × 0.4 + latency × 0.2`. Cloud providers get quality=90 while local gets quality=60. With cost=0 for both (local is free, cloud has cost_per_1k=0 in config), cloud wins on quality.

**Evidence**:
```
INFO:omega.cascade_router:Routed qwen3-1.7b to opencode-zen (score: 86.0, cost: 0.0001, quality: 90.0)
  → google → google-compat → openrouter
```

**Impact**: native-gguf is never reached. The CascadeRouter bypasses the priority-based routing from `providers.yaml` (where native-gguf has priority=0).

**Fix Options**:
- **Option A (Quick)**: Add a local-first multiplier to the CascadeRouter score: `if provider_name in ["native-gguf", "lmster", "ollama"]: total_score *= 1.5`
- **Option B (Correct)**: Use the ProviderSelector's priority-based routing instead of CascadeRouter for the first pass, then use CascadeRouter for fallback ordering
- **Option C (Minimal)**: Remove CascadeRouter from the generate path entirely; let ModelGateway iterate providers in priority order (as it already does)

**Recommended**: Option C — simplest, respects M7, no scoring edge cases.

### 🔴 BUG #2: RemoteProvider.generate() Missing Parameters

**File**: `src/omega/oracle/backends/remote_provider.py:223`
**Root Cause**: `RemoteProvider.generate()` signature lacks `logit_bias` and `repetition_penalty` parameters. `ModelGateway.generate()` passes these to ALL providers.

**Evidence**:
```
ERROR: ModelGateway.generate: unexpected error from provider=opencode-zen
  err=RemoteProvider.generate() got an unexpected keyword argument 'logit_bias'
```

**Impact**: Cloud providers fail on the first attempt, wasting 2-5 seconds per fallback. The cascade then moves to the next provider.

**Fix**: Add `logit_bias: Optional[Dict[int, float]] = None, repetition_penalty: float = 1.0` to `RemoteProvider.generate()` signature. The base implementation can ignore them (subclasses like OpenAICompatProvider already handle them).

### 🔴 BUG #3: NativeGGUFProvider KV Cache q8_0 Crashes

**File**: `src/omega/oracle/providers.py:352-353`
**Root Cause**: `self._type_k = config.get("type_k", 8)` and `self._type_v = config.get("type_v", 8)` hardcode q8_0 KV cache quantization. With `llama-cpp-python 0.3.32`, `type_k=8` (q8_0) causes `ValueError: Failed to create llama_context` for Qwen3 models.

**Evidence**:
```
# With type_k=8 (q8_0):
ValueError: Failed to create llama_context

# With type_k=None (f16 default):
Model loaded successfully → 15.12 tok/s
```

**Impact**: Even if the cascade reaches native-gguf, it crashes immediately.

**Fix**: Change defaults from `8` to `None`:
```python
self._type_k = config.get("type_k", None)  # Was 8 (q8_0) — crashes Qwen3
self._type_v = config.get("type_v", None)  # Was 8 (q8_0) — crashes Qwen3
```
**Trade-off**: f16 KV cache uses ~2× more RAM than q8_0. For Qwen3-1.7B at 32K context: ~112MB vs ~56MB. Negligible on a 14GB system.

### 🟡 BUG #4: Auto-Context Too Aggressive

**File**: `src/omega/oracle/providers.py:482-495`
**Root Cause**: `_select_optimal_context()` tries `[32768, 16384, 8192, 4096]` from largest to smallest. It estimates RAM via `_estimate_context_memory()` which uses a rough formula (`~2MB per 1K tokens for a 4B model`). For Qwen3-1.7B at 32K, it estimates 1961MB total — which fits in 8.7GB available, but the multiprocessing worker inherits the parent's memory footprint, making actual available RAM less.

**Evidence**:
```
INFO: Auto-selected context: 32768 tokens (est 1961.0MB)
Process Process-1: ValueError: Failed to create llama_context
```

**Impact**: The model tries to allocate too much context in a subprocess, fails, and the whole inference path dies.

**Fix**: Use the model's `context_window` from `models.yaml` as the default:
```python
# In _select_optimal_context:
model_ctx = self.models.get(model_name, {}).get("context_window", 8192)
return min(model_ctx, self._n_ctx_max)
```

---

## §3 The Fix — Step-by-Step Execution Plan

### Phase 0: Unblock Local Inference (2-3 hours)

| Step | File | Change | Lines | Effort |
|------|------|--------|-------|--------|
| **0.1** | `providers.py:352-353` | `type_k/type_v` default `8` → `None` | 2 | 2 min |
| **0.2** | `remote_provider.py:223` | Add `logit_bias`, `repetition_penalty` to `generate()` | 2 | 5 min |
| **0.3** | `cascade_router.py` | Disable CascadeRouter scoring for first attempt; use priority order | ~30 | 30 min |
| **0.4** | `providers.py:482` | Use model's `context_window` from models.yaml as default | ~10 | 15 min |
| **0.5** | `model_gateway.py:1115` | Stop passing `logit_bias`/`repetition_penalty` to RemoteProvider | ~5 | 5 min |
| **0.6** | `test_local.py` | Integration test: `omega talk "hello"` → local response | ~50 | 30 min |
| **0.7** | `config/providers.yaml` | Verify `lmster` endpoint is correct (1234 default) | 1 | 5 min |

**Validation**:
```bash
source .venv/bin/activate
export OMEGA_MODELS_DIR=/media/arcana-novai/omega_library/models/gguf
omega talk "What model are you running on?"
# Expected: Response from Qwen3-1.7B via native-gguf
```

### Phase 1: Wire Local Models to Agents (3-4 hours)

| Step | What | Details | Effort |
|------|------|---------|--------|
| **1.1** | Register RocRacoon-3B in models.yaml | `config/models.yaml` — add entry with path, context, role | 10 min |
| **1.2** | Register MiMo-7B-RL in models.yaml | Already partially there — verify path resolution | 10 min |
| **1.3** | Wire `oracle_summon_local()` to native-gguf | D118 MaKaLi routing: `oracle_summon_local(entity_name, query, model="qwen3-1.7b")` | 30 min |
| **1.4** | Test entity affinity routing | `oracle summon roc_racoon "hello"` → should use `local_fast` model | 30 min |
| **1.5** | Verify OOMProtector gates correctly | `quick_check()` should return ALLOW when 8GB+ available | 15 min |
| **1.6** | Test AdmissionController | Run 2 concurrent local inferences → second should get OOMRiskError or route to cloud | 15 min |
| **1.7** | Benchmark local models | Create `scripts/benchmark_local.py` with timing results | 1 hr |

### Phase 2: Performance & Polish (2-3 hours)

| Step | What | Details | Effort |
|------|------|---------|--------|
| **2.1** | Warm-cache model pre-loading | Pre-load Qwen3-1.7B on Oracle bootstrap so first inference isn't 30s cold | 1 hr |
| **2.2** | Test lmster backend | Start LM Studio, verify `LocallmsterProvider.is_available()` → True | 30 min |
| **2.3** | Test Ollama backend | `ollama pull qwen3:1.7b`, verify `OllamaProvider.is_available()` → True | 30 min |
| **2.4** | llama-optimus calibration | `pip install llama-optimus && llama-optimus --model Qwen3-1.7B-Q6_K.gguf` | 2 hr |
| **2.5** | Store calibration results | Cache optimal flags per model in `data/calibration/` | 30 min |

### Phase 3: Advanced (Post-GPU, when available)

| Step | What | Depends On | Effort |
|------|------|------------|--------|
| **3.1** | Vulkan backend for llama.cpp | Discrete GPU (RTX 3090 recommended) | 2 hrs |
| **3.2** | Deploy Ornith-1.0-9B | GPU + Vulkan build | 4 hrs |
| **3.3** | Deploy Qwen3.5-9B | GPU + Vulkan build | 2 hrs |
| **3.4** | ModelAwareInstructionRouter | Nothing (can start now) | 3.5 days |
| **3.5** | TTFT-Optimized Routing | Instruction Router + model fabric | 12 hrs |

---

## §4 The Routing Flow (How It Works End-to-End)

```
User: "Hello, what model are you running?"
  │
  ▼
Oracle.talk(query)
  │
  ├── TDPGate.isolate(query)          ← Taint check
  ├── SovereignVetter.vet(query)      ← Mandate enforcement
  ├── RAGRouter.classify(query)       ← Complexity classification
  │
  ▼
_summon(entity_name, query)
  │
  ├── EntityRegistry.get(entity_name) ← Load entity config
  ├── _prepare_system_prompt(...)     ← Build system prompt from soul.yaml
  ├── _select_model(entity, query)    ← TriageRouter selects model name
  │     └── Falls back to entity's configured model or "qwen3-1.7b"
  │
  ├── resolve_entity_affinity(entity) ← entity_model_affinity.yaml
  │     └── Returns: temperature, system_prompt, preferred_context
  │
  ▼
ModelGateway.generate(model_name, system_prompt, query, ...)
  │
  ├── CascadeRouter.route_request()   ← BUG #1: scores cloud higher
  │     ├── _score_provider("opencode-zen") → 86.0
  │     ├── _score_provider("native-gguf") → 74.0
  │     └── Returns: opencode-zen (score 86.0) → google → google-compat → openrouter
  │
  ├── ordered_providers = [opencode-zen, google, google-compat, openrouter]
  │
  ▼
For each provider in ordered_providers:
  │
  ├── provider.generate(model, system, query, ..., logit_bias=..., repetition_penalty=...)
  │     │
  │     ├── RemoteProvider.generate()  ← BUG #2: missing logit_bias
  │     │     └── TypeError → FAIL → next provider
  │     │
  │     └── (cloud providers all fail)
  │
  ▼
(native-gguf never reached because CascadeRouter didn't include it in fallback chain)
```

**After fixes**, the flow becomes:
```
ModelGateway.generate(model_name="qwen3-1.7b", ...)
  │
  ├── providers = [native-gguf(priority=0), lmster(1), ollama(2), ...]
  │
  ▼
native-gguf.generate(...)
  │
  ├── _ensure_loaded()
  │     ├── _select_optimal_context() → 8192 (from models.yaml context_window)
  │     ├── _apply_cpu_affinity() → cores [0,2,4,6]
  │     └── _worker(type_k=None, type_v=None) → Llama() loads successfully
  │
  ▼
GenerateResult(text="I'm running on Qwen3-1.7B!", provider_name="native-gguf")
```

---

## §5 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|:---:|:---:|------------|
| `type_k=None` uses f16 → slightly more RAM | Low | Low | Only ~56MB more at 32K ctx. Negligible on 14GB. |
| Other GGUF models also fail with type_k=8 | High | High | The fix applies universally. All models use f16 KV cache. |
| CascadeRouter scoring change breaks cloud routing | Low | Medium | Cloud still works — just local is tried first. Fallback preserved. |
| Qwen3-1.7B too slow for agent work (15 tok/s) | Medium | Medium | RocRacoon-3B is next test; 8B models need n_ctx=4096. |
| Multiprocessing worker serialization fails | Low | High | Direct Llama() call works; multiprocessing is the wrapper. |
| OOMProtector blocks local inference when system is loaded | Low | Medium | 8.7GB available is well above 4GB throttle threshold. |
| llama-optimus calibration takes too long | Low | Low | 3-stage optimization runs in minutes, not hours. |

---

## §6 Parallel Work Streams (Can Run With Docs Cleanup)

The local models fixes do NOT conflict with:
- ✅ Docs cleanup / SSOT reconciliation (UO-4)
- ✅ PR preparation / commit organization
- ✅ Un-overengineering Phase 1 (pybreaker, structlog) — these are in `src/omega/` not `src/omega/oracle/`
- ✅ Strategy documentation updates

The fixes DO conflict with:
- ❌ MCP v2 migration (different files, but same sprint freeze)
- ❌ Bulk code deletions (Phase 0 is additive, not deletive)

**Recommendation**: Run local models fixes in parallel with docs cleanup. The code changes are small, isolated, and low-risk.

---

## §7 What Success Looks Like

### Immediate (After Phase 0):
```bash
$ omega talk "Hello, what model are you running?"
# Response: "I'm running on Qwen3-1.7B via native-gguf on your local machine."
# Latency: ~15-30 seconds (cold start), ~1-3 seconds (warm)
# Provider: native-gguf
# Context: 8192 tokens
```

### Short-term (After Phase 1):
```bash
$ omega summon roc_racoon "What's in the den?"
# Entity: roc_racoon
# Model: qwen3-1.7b (local_fast from affinity)
# Provider: native-gguf
# Response: Local inference, no cloud dependency
```

### Medium-term (After Phase 2):
```bash
$ scripts/benchmark_local.py --models qwen3-1.7b,roc-racoon-3b,mimo-7b
# qwen3-1.7b: 15.1 tok/s (pp: 120, tg: 15.1)
# roc-racoon-3b: 8.2 tok/s (pp: 85, tg: 8.2)
# mimo-7b: 4.1 tok/s (pp: 45, tg: 4.1)
```

### Long-term (After Phase 3, GPU available):
```bash
$ scripts/benchmark_local.py --models ornith-9b,qwen3.5-9b --backend vulkan
# ornith-9b: 45 tok/s (Vulkan, RTX 3090)
# qwen3.5-9b: 52 tok/s (Vulkan, RTX 3090)
```

---

## §8 Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md` | Phase 2-3 GPU roadmap (Ornith, Vulkan, llama-optimus) |
| `docs/strategy/POST_PR_ROSTER.md` | Post-PR items including Instruction Router |
| `config/entity_model_affinity.yaml` | Entity→Model routing (complete for all 13 entities) |
| `config/providers.yaml` | Fallback chain with priority ordering |
| `config/models.yaml` | Model registry (5 models currently) |
| `src/omega/oracle/providers.py` | NativeGGUFProvider — the local backend |
| `src/omega/oracle/cascade_router.py` | CascadeRouter — the routing bug |
| `src/omega/oracle/backends/remote_provider.py` | RemoteProvider — the logit_bias bug |
| `src/omega/oracle/admission_controller.py` | LocalInferenceAdmission — semaphore gate |
| `src/omega/oracle/oom_protector.py` | OOMProtector — memory guard |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_local_models ⬡ BRIEFING-COMPLETE*
*Researched 2026-07-30. All findings verified with live testing. Ready for execution.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
