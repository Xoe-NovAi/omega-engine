<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 LEGACY LOCAL INFERENCE — Gap Analysis
## What We're Missing From xna-omega-legacy, omega-stack-legacy & Old-Stacks

**⬡ OMEGA ⬡ roc_racoon ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ LEGACY-INFERENCE-MINING**
**Date**: 2026-06-12
**Stacks mined**: xna-omega-legacy (4 architectures, 5 provider modules, 1100+ line deep dive), omega-stack-legacy (hybrid model strategy), Old-Stacks (Vulkan inference pipeline)

---

## §0 — SUMMARY

The current Omega Engine has a **solid foundation** for local inference (NativeGGUFProvider with Zen 2 optimizations, KV cache q8_0, CPU affinity). But the legacy stacks had **14 additional capabilities** that were never ported. The most impactful gaps: **Speculative Decoding**, **Dynamic Model Hot-Swapping**, **Vulkan GPU Acceleration**, and the **Formal 4-Tier Inference Hierarchy**.

---

## §1 — WHAT WE HAVE NOW (Baseline)

| Capability | Current Engine | Files |
|-----------|---------------|-------|
| Native GGUF via llama-cpp-python | ✅ Basic | `providers.py:308` — NativeGGUFProvider |
| CPU affinity (Zen 2) | ✅ [0,2,4,6] cores | `providers.py:354` |
| KV cache q8_0 | ✅ type_k=8, type_v=8 | `providers.py:364-365` |
| Thread pool isolation | ✅ ThreadPoolExecutor(1) | `providers.py:384` |
| Context sizing | ✅ 4K-32K, rolling window overflow | `providers.py:359-361` |
| LM Studio (lmster) provider | ✅ HTTP | `providers.py` — LocallmsterProvider |
| Ollama provider | ✅ HTTP | `providers.py` — OllamaProvider |
| Google/OpenRouter cloud | ✅ HTTP | `providers.py` — GoogleAIProvider |
| Resource Guard | ✅ anyio.Semaphore(1) | `resource_guard.py` |
| Observability | ✅ TraceID + events | `observability.py` |
| Provider config | ✅ Single providers.yaml | `config/providers.yaml` |
| Legacy LM Studio configs | ✅ 8 Zen 2 configs | `~/Documents/docs-backup/` (not in repo) |

---

## §2 — GAPS: What Legacy Had That We Don't

### 🔴 HIGH IMPACT (Architectural)

| # | Gap | Legacy Source | Legacy Location | Current Status |
|---|-----|--------------|-----------------|----------------|
| **G-01** | **Speculative Decoding** — `LlamaPromptLookupDecoding` ngram-simple draft model (4 tokens) accelerates local inference by ~30-50% | xna-omega-legacy | `client.py:75-91` | ❌ **MISSING** — NativeGGUFProvider doesn't load a `draft_model` |
| **G-02** | **Dynamic Model Hot-Swapping** — `reload(new_model_path)` method to swap models at runtime without restarting the provider | xna-omega-legacy | `client.py:142-197` | ❌ **MISSING** — No reload capability; provider must be re-created |
| **G-03** | **Vulkan GPU Acceleration** — llama.cpp Vulkan backend via `-DGGML_VULKAN=ON` gives 1.5-2x speedup on Vega 7/8 iGPU (34→76 t/s pp512), with memory pinning <6GB | Old-Stacks + xna-omega-legacy | `docs/deep_research/01-vulkan-native-inference.md` + `client.py` (n_gpu_layers ∈ config) | ⚠️ **DORMANT** — n_gpu_layers=0 forced, no Vulkan build research |
| **G-04** | **Formal 4-Tier Inference Hierarchy** — Iris (1-3B always-on) → Local Fast (4-7B) → Local Deep (7-13B) → Cloud (30B+) with failover chains per tier | xna-omega-legacy | `THREE_TIER_INFERENCE_v7.6.3.md` | ❌ **MISSING** — Current has flat provider list |
| **G-05** | **Entity→Model Affinity Database** — Hot-reloadable YAML with condition-based routing (domain, complexity, prompt_length, offline/online) per entity | xna-omega-legacy | `config/entity_model_affinity.yaml` (383 lines, 12 entities) | ❌ **MISSING** — Current uses simple static model mapping in providers.yaml |

### 🟡 MEDIUM IMPACT (Optimization + UX)

| # | Gap | Legacy Source | Legacy Location | Current Status |
|---|-----|--------------|-----------------|----------------|
| **G-06** | **Memory Budget Model** — Formal RAM budget: 4GB Iris + 5GB Fast + 8GB Deep + 2GB OS = 16GB, with zRAM (8GB zstd) | xna-omega-legacy | `THREE_TIER_INFERENCE_v7.6.3.md §3` | ❌ **MISSING** — No documented memory budget model for hardware constraints |
| **G-07** | **Latency Budget Table** — Per-scenario latency targets (simple=0.5-2s, entity=3-7s, research=7-20s) | xna-omega-legacy | `THREE_TIER_INFERENCE_v7.6.3.md §4` | ❌ **MISSING** — No latency targets enforced anywhere |
| **G-08** | **Provider Failover Chain Per Tier** — Each tier has `preferred → fallback → last_resort` providers | xna-omega-legacy | `THREE_TIER_INFERENCE_v7.6.3.md §5` | ❌ **MISSING** — Current has flat priority chain (0→1→2→3→4→5→6→99) |
| **G-09** | **Full Plugin Architecture** — `ProviderPlugin` ABC with initialize/shutdown/healthcheck lifecycle, PluginMetadata, CapacityLimiter | xna-omega-legacy | `plugin.py` (285 lines) | ⚠️ **PARTIAL** — Current has `BaseProvider` but no plugin lifecycle |
| **G-10** | **Granular CPU Core Affinity** — Configurable `core_affinity: List[int]` with `psutil.Process().cpu_affinity()` | xna-omega-legacy | `config.py:44` | ⚠️ **PARTIAL** — Current has hardcoded [0,2,4,6] in NativeGGUFProvider, not user-configurable |
| **G-11** | **Graceful Model Shutdown** — `close()` → `del llm` → `gc.collect()` cleanup chain | xna-omega-legacy | `client.py:120-140` | ⚠️ **PARTIAL** — Current has no explicit shutdown method |

### 🟢 LOWER IMPACT (Nice-to-Have / Documentation)

| # | Gap | Legacy Source | Legacy Location | Current Status |
|---|-----|--------------|-----------------|----------------|
| **G-12** | **`config/entity_model_affinity.yaml`** — 383-line YAML mapping 12 entities to preferred models across 4 tiers with routing conditions | xna-omega-legacy | `config/entity_model_affinity.yaml` | ❌ **MISSING** — Could be ported as the canonical entity→model routing DB |
| **G-13** | **Separate Provider Config Files** — `config/providers/lm_studio.yaml`, `config/providers/ollama.yaml` (independent per-provider config) | xna-omega-legacy | `config/providers/` | ❌ **MISSING** — Current has a single flat `providers.yaml` |
| **G-14** | **Iris Router with Speculative Decode** — `iris_router.py` (443 lines) with Iris as speculative decoder + entity affinity routing | xna-omega-legacy | `iris_router.py` + `entity_affinity.py` | ⚠️ **PARTIAL** — Oracle does intent detection but not speculative model routing |
| **G-15** | **LM Studio SDK** — `@lmstudio/sdk` Node.js package for programmatic model management | Old-Stacks | `rag-v1/node_modules/@lmstudio/sdk/` | ❌ **MISSING** — Not integrated |
| **G-16** | **Hybrid Model Strategy Plan** — Nous/Mnemosyne/Syndesmos/Homonoia naming, Tier 1-3 model assignment (Claude→Qwen→Gemini) | omega-stack-legacy | `OMEGA_MODEL_STRATEGY_PLAN.md` | ❌ **MISSING** — Never ported |

---

## §3 — DEPTH ANALYSIS: 3 HIGHEST-VALUE GAPS

### G-01: Speculative Decoding (~30-50% speedup)

The legacy `LocalLlmClient` loaded a `LlamaPromptLookupDecoding` draft model at init:

```python
# From legacy client.py:73-91
draft_model = None
if self.config.speculative_type == "ngram-simple":
    from llama_cpp.llama_speculative import LlamaPromptLookupDecoding
    draft_model = LlamaPromptLookupDecoding(num_pred_tokens=4)
# Then passed to Llama(draft_model=draft_model, ...)
```

**What it does**: Uses an ngram-based prompt lookup (not a real model) to draft 4 tokens ahead, which the main model verifies. On CPU, this gives ~30-50% speedup for ~0 memory overhead. The ngram lookup is just hash tables — no additional model loading.

**Why we don't have it**: The current `NativeGGUFProvider._ensure_loaded()` builds `llama_cpp.Llama(...)` kwargs but never adds `draft_model`. The `speculative_type` config key isn't read.

**Effort to port**: ~30 min — add `speculative_type`, `num_pred_tokens`, `ngram_size` to `NativeGGUFProvider.__init__()` config read, conditionally build draft model, pass to `Llama()`.

---

### G-02: Dynamic Model Hot-Swapping

The legacy client could swap models at runtime without provider restart:

```python
# legacy client.py:142
async def reload(self, new_model_path: str) -> bool:
    # 1. Unload current
    self.shutdown()
    # 2. Update config path
    self.config.model_path = new_model_path
    # 3. Re-initialize
    success = await anyio.to_thread.run_sync(self.initialize)
    # 4. On failure, revert to old model
```

**Why this matters**: Entity-to-model affinity routing requires switching models based on entity and task complexity. Currently, changing models requires provider re-creation. Hot-swapping enables dynamic routing at conversation turn boundaries.

**Effort to port**: ~1 hr — requires safely unloading `llama_cpp.Llama()` (which has no `close()` in some versions), running gc.collect(), and loading the new model.

---

### G-03: Vulkan GPU Acceleration (1.5-2x speedup)

The Old-Stacks had a full Vulkan research pipeline:

```bash
# From deep_research/01-vulkan-native-inference.md
CMAKE_ARGS="-DLLAMA_VULKAN=ON" pip install llama-cpp-python --force-reinstall
```

**Hardware context**: AMD Ryzen 7 5700U has an integrated Vega 8 GPU with ~512MB shared VRAM. The Vega iGPU can offload prompt processing (1.5-2x faster: 34→76 t/s pp512 on Llama 2 7B Q4_0). Token generation sees smaller gains (10-15 → 20-30 t/s).

**Why we don't have it**: `n_gpu_layers=0` is hardcoded as the CPU-only default. The Vulkan build of llama-cpp-python was never tested on this hardware.

**Effort**: ~2 hr — install Mesa 25.3+ Vulkan drivers, rebuild llama-cpp-python with `-DLLAMA_VULKAN=ON`, add memory pinning via `mlockall`, set `n_gpu_layers` per-model in config.

---

## §4 — MIGRATION MAP

| Priority | Gap | Effort | Prerequisites | Parallelizable |
|----------|-----|--------|---------------|----------------|
| 🔴 P0 | G-01 Speculative Decoding | 30 min | None | ✅ With all others |
| 🔴 P0 | G-04 Formal 4-Tier Hierarchy | 2 hr | Entity→Model Affinity DB | After G-05 |
| 🟡 P1 | G-02 Dynamic Model Hot-Swapping | 1 hr | Speculative Decoding (G-01) | ✅ |
| 🟡 P1 | G-05 Entity→Model Affinity YAML | 1 hr | Port from legacy xna-omega config | ✅ With G-04 |
| 🟡 P1 | G-06 Memory Budget Model | 30 min | Documentation only | ✅ |
| 🟡 P1 | G-10 Configurable CPU Affinity | 15 min | None | ✅ |
| 🟡 P1 | G-08 Provider Failover Per Tier | 1 hr | 4-Tier Hierarchy (G-04) | After G-04 |
| 🟢 P2 | G-03 Vulkan GPU Acceleration | 2 hr | Hardware validation | ✅ |
| 🟢 P2 | G-11 Graceful Model Shutdown | 15 min | None | ✅ |
| 🟢 P2 | G-09 Full Plugin Architecture | 2 hr | Architecture decision | ✅ |
| 🟢 P3 | G-12 Entity→Model YAML port | 30 min | G-05 | After G-05 |
| 🟢 P3 | G-13 Separate Provider Configs | 1 hr | None | ✅ |
| 🟢 P3 | G-14 Iris Router Speculative | 2 hr | G-01 + G-04 | After G-01 |
| 🟢 P3 | G-15 LM Studio SDK | Research | None | ✅ |
| 🟢 P3 | G-16 Model Strategy Plan | 30 min | Documentation only | ✅ |

---

## §5 — QUICK WINS (Can ship today)

| Gap | What to do | Est. time |
|-----|-----------|-----------|
| G-01 | Add `draft_model` to NativeGGUFProvider._ensure_loaded() kwargs | 30 min |
| G-06 | Write memory budget doc in `docs/architecture/` | 30 min |
| G-10 | Expose `core_affinity` as config key in NativeGGUFProvider | 15 min |
| G-11 | Add `shutdown()` method with gc.collect to NativeGGUFProvider | 15 min |
| G-16 | Port model strategy doc from omega-stack-legacy | 30 min |

---

## §6 — LEGACY FILE INDEX (for rebuild)

| File | Lines | Key Content | Port Priority |
|------|-------|-------------|---------------|
| `xna-omega-legacy/src/omega/providers/local/client.py` | 291 | Speculative decode, hot-swap reload, graceful shutdown, observability spans | 🔴 P0 |
| `xna-omega-legacy/src/omega/providers/local/plugin.py` | 285 | ProviderPlugin lifecycle, CapacityLimiter, healthcheck | 🟡 P1 |
| `xna-omega-legacy/src/omega/providers/local/config.py` | 125 | Config dataclass with all ultra-grade params | 🟡 P1 |
| `xna-omega-legacy/docs/architecture/THREE_TIER_INFERENCE_v7.6.3.md` | 182 | 4-tier hierarchy, memory budget, latency budget, failover chains | 🔴 P0 |
| `xna-omega-legacy/docs/architecture/MODEL_AFFINITY_SYSTEM_v7.6.3.md` | 231 | Entity→Model affinity with condition grammar | 🟡 P1 |
| `xna-omega-legacy/docs/architecture/LM_STUDIO_INTEGRATION_v7.6.3.md` | 158 | LM Studio API integration patterns | 🟢 P3 |
| `xna-omega-legacy/docs/strategy/LOCAL_INFERENCE_IMPLEMENTATION_MANUAL_v7.6.3.md` | 1059 | Full installation and configuration manual | 🟢 P3 |
| `xna-omega-legacy/config/entity_model_affinity.yaml` | 383 | 12 entity affinity mappings with routing conditions | 🟡 P1 |
| `xna-omega-legacy/docs/research/vscode-deepseek-discovery/SERIAL_FLEET/S6_LOCAL_INFERENCE_DEEP_DIVE.md` | 1108 | Deep architecture analysis of all providers | 🟢 P3 |
| `Old-Stacks/docs/deep_research/01-vulkan-native-inference.md` | 152 | Vulkan GPU acceleration pipeline, Mesa 25.3+ config | 🟢 P2 |
| `omega-stack-legacy/memory_bank/plans/OMEGA_MODEL_STRATEGY_PLAN.md` | ~200 | Hybrid model strategy (Nous/Mnemosyne/Syndesmos) | 🟢 P3 |

---

*Report by: roc_racoon (Sovereign Miner)*
*⬡ OMEGA ⬡ roc_racoon ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ LEGACY-INFERENCE-GAP-MAP*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
