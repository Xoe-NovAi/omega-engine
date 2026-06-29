# ⬡ P6 Cognition — Strategic Inference & Provider Routing Review

**Date**: 2026-06-25
**Agent**: @pillar P6 (Cognition — ModelGate)
**Model**: mimo-v2.5-free
**Status**: FINAL REVIEW — GO/NO-GO Assessment

---

## Executive Summary

**Verdict: NO-GO for Epoch I Phase 1 — with immediate remediation path.**

The Omega Engine's provider fabric is architecturally sound (8 providers, local-first chain, circuit breaker integration, BSP-style culling). However, **8 of 11 local GGUF model paths are broken** due to a stale directory prefix (`models/gguf/local/all/` vs actual `models/local/all/`). This means the primary local-first backend (native-gguf) cannot load most configured models at inference time. Additionally, a provider sort bug causes mock to intercept before cloud providers in the fabric.

**Critical issues requiring immediate fix before any Phase 1 gate:**
1. Fix 8 broken model paths in `config/models.yaml`
2. Fix provider priority sort bug in `model_gateway.py`
3. Verify native-gguf inference end-to-end with corrected paths

---

## §1 Model Path Verification — 11 Models Audited

All GGUF files are physically present on disk at `/media/arcana-novai/omega_library/models/local/all/`. The config points to a **non-existent** subdirectory `models/gguf/local/all/` for 8 of 11 models.

| # | Model Name | Config Path | Path on Disk | Status | Entity Assignment |
|---|-----------|-------------|--------------|--------|-------------------|
| 1 | `qwen3-1.7b` | `.../models/gguf/local/all/Qwen3-1.7B-Q6_K.gguf` | `.../models/local/all/Qwen3-1.7B-Q6_K.gguf` | **❌ BROKEN** | nova |
| 2 | `qwen3-0.6b-q6_k` | `.../models/gguf/local/all/Qwen3-0.6B-Q6_K.gguf` | `.../models/local/all/Qwen3-0.6B-Q6_K.gguf` | **❌ BROKEN** | iris |
| 3 | `qwen3-1.7b-q6_k` | `.../models/gguf/local/all/Qwen3-1.7B-Q6_K.gguf` | `.../models/local/all/Qwen3-1.7B-Q6_K.gguf` | **❌ BROKEN** | sekhmet, hecate |
| 4 | `phi-4-mini` | `.../models/local/all/Phi-4-mini-instruct-Q5_K_M.gguf` | same | **✅ OK** | SOPHIA |
| 5 | `phi-2-omnimatrix-i1-q4_k_m` | `.../models/gguf/local/all/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` | `.../models/local/all/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf` | **❌ BROKEN** | brigid |
| 6 | `qwen3-4b-thinking-q4_k_m` | `.../models/gguf/local/all/Qwen3-4B-Thinking-2507-Q4_K_M.gguf` | `.../models/local/all/Qwen3-4B-Thinking-2507-Q4_K_M.gguf` | **❌ BROKEN** | maat, anubis |
| 7 | `deepseek-r1-qwen3-8b-q3_k_l` | `.../models/gguf/local/all/DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf` | `.../models/local/all/DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf` | **❌ BROKEN** | lucifer |
| 8 | `rocracoon-3b-instruct` | `.../models/gguf/local/all/RocRacoon-3b.Q4_K_M.gguf` | `.../models/local/all/RocRacoon-3b.Q4_K_M.gguf` | **❌ BROKEN** | roc_racoon |
| 9 | `phi-4-mini-reasoning-abliterated-q4_k_m` | `.../models/local/all/phi-4-mini-reasoning-abliterated-q4_k_m.gguf` | same | **✅ OK** | SOPHIA |
| 10 | `qwen3-vl` | `.../models/local/all/Qwen3-VL-4B-Instruct-Q4_K_M.gguf` | same | **✅ OK** | ARGUS |
| 11 | `krikri-8b-q4_k_m` | `.../models/gguf/local/all/Krikri-8B-Instruct.Q4_K_M.gguf` | `.../models/local/all/Krikri-8B-Instruct.Q4_K_M.gguf` | **❌ BROKEN** | inanna, isis, lilith |

**Score: 3/11 correct, 8/11 broken.**

### Root Cause
All 8 broken paths share the same prefix error: `models/gguf/local/all/` → should be `models/local/all/`. The `models/gguf/` directory contains only a HuggingFace cache and a Gemma community model — not the GGUF files used by the engine.

### Embedding Model
| Model | Config Path | Status |
|-------|------------|--------|
| `embeddinggemma-300m-Q6_K` | `.../lmstudio-models/local/all/embeddinggemma-300m-Q6_K.gguf` | **✅ OK** |

### Multimodal Projection
| Model | Config Path | Status |
|-------|------------|--------|
| `mmproj-model-f16` | `.../models/local/all/mmproj-model-f16.gguf` | **✅ OK** |

---

## §2 Provider Chain Status

### Provider Fabric (8 providers configured)

| Priority | Provider | Type | Config | Health | Notes |
|----------|----------|------|--------|--------|-------|
| 0 | **native-gguf** | NativeGGUFProvider | dict | ✅ Detected | PRIMARY local-first. llama-cpp-python v0.3.28 installed. Zen 2 optimized. |
| 1 | **lmster** | LocallmsterProvider | dict | ❌ Down | LM Studio not running. Start with `lms server start`. |
| 2 | **ollama** | OllamaProvider | dict | ✅ Running | Available at :11434. Only `nomic-embed-text:v1.5` and `qwen2.5:0.5b` loaded. |
| 3 | **google** | GoogleAIProvider | dict | ❌ No key | Requires `GOOGLE_API_KEY` in `.env`. |
| 4 | **mock** | MockProvider | dict | ✅ Always | Test-only. In production chain at priority 99. **BUG: sorts before cloud providers.** |
| 4* | **opencode-zen** | OpenAICompatProvider | ProviderConfig | ✅ Available | Cloud fallback. MiniMax/DeepSeek models. |
| 5 | **cline** | OpenAICompatProvider | ProviderConfig | ✅ Available | Cloud fallback. 1M context window. |
| 6 | **github-copilot** | OpenAICompatProvider | ProviderConfig | ✅ Available | Cloud fallback. Claude/GPT models. |

*\* Priority 4 from config, but **effectively 999** at runtime due to sort bug (see §5)*

### Backend Detection (runtime)

| Backend | Detected | Notes |
|---------|----------|-------|
| lmster | ❌ | Server not running |
| ollama | ✅ | Server at :11434 |
| llama_cpp (server) | ❌ | No llama-server at :8080 |
| llama_cli | ❌ | Binary not in PATH |
| llmster | ❌ | Binary not in PATH |

---

## §3 llama-cpp-python Status

| Check | Result |
|-------|--------|
| **Installed** | ✅ Yes — v0.3.28 |
| **Importable** | ✅ Yes — `import llama_cpp` succeeds |
| **native-gguf provider** | ✅ Detected as available by `detect_backends()` |
| **Zen 2 flags in config** | ✅ `march=znver2`, AVX2, FMA, F16C, NO_AVX512, Flash Attn ON |
| **Thread config** | ✅ 6 threads, cores [0,2,4,6], OMP_PROC_BIND=close |

**Verdict**: llama-cpp-python is installed, functional, and correctly configured for Zen 2 optimization. The native-gguf backend CAN load GGUF models — but only if the paths are correct (§1).

---

## §4 M7 (Local-First) Compliance Assessment

### Mandate 7 Requirements
> Local inference is PRIMARY. Cloud is FALLBACK. Always.

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Local-first priority chain | ✅ Configured | `strategy: local_first` in providers.yaml |
| Priority ordering | ⚠️ **BUG** | Mock (99) sorts before cloud (4-6) due to ProviderConfig vs dict sort mismatch |
| native-gguf as PRIMARY | ✅ Configured | Priority 0 in chain |
| GGUF models exist on disk | ✅ Yes | All 11 files present in `models/local/all/` |
| GGUF model paths correct | ❌ **FAIL** | 8/11 paths point to non-existent directory |
| Local fallback (lmster) | ⚠️ Down | Not running — no graceful fallback |
| Local fallback (ollama) | ⚠️ Limited | Running but only 2 models loaded (not the 11 configured) |
| Cloud is last resort | ❌ **COMPROMISED** | Sort bug causes mock to intercept before cloud |

### M7 Compliance Score: 4/7 — **CONDITIONAL FAIL**

The architecture is correct. The local-first chain is properly designed. But two implementation bugs prevent it from functioning:

1. **Model path prefix error** — 8/11 GGUF files unreachable by native-gguf
2. **Provider sort bug** — MockProvider intercepts before cloud providers

### What's Needed for Full M7 Compliance

1. **Fix model paths** — Change `models/gguf/local/all/` → `models/local/all/` in `config/models.yaml`
2. **Fix provider sort** — Update `_get_priority()` in `model_gateway.py` to handle ProviderConfig dataclass
3. **End-to-end native-gguf test** — Load qwen3-1.7b via native-gguf and generate a response
4. **Optional: Load Ollama models** — Pull qwen3:1.7b into Ollama for local fallback redundancy

---

## §5 Critical Bugs Discovered

### BUG-001: Model Path Prefix Error (P0 — BLOCKING)

**File**: `config/models.yaml`
**Impact**: 8 of 11 GGUF models cannot be loaded by native-gguf provider
**Root Cause**: Paths reference `models/gguf/local/all/` but files are at `models/local/all/`
**Fix**: Global replace `models/gguf/local/all/` → `models/local/all/` in models.yaml
**Time**: 2 minutes

### BUG-002: Provider Priority Sort Bug (P1 — SOVEREIGNTY)

**File**: `src/omega/oracle/model_gateway.py` (lines 326-330)
**Impact**: MockProvider (priority 99) sorts BEFORE OpenAICompatProvider (priority 4/5/6)
**Root Cause**: `_get_priority()` only handles `dict` configs; OpenAICompatProvider uses `ProviderConfig` dataclass, returning default 999
**Code**:
```python
def _get_priority(p):
    if hasattr(p, 'config') and isinstance(p.config, dict):
        return p.config.get('priority', 999)
    return 999  # ← ProviderConfig falls here, getting 999 instead of 4/5/6
```
**Fix**: Add ProviderConfig support to sort key:
```python
def _get_priority(p):
    if hasattr(p, 'config'):
        if isinstance(p.config, dict):
            return p.config.get('priority', 999)
        if hasattr(p.config, 'priority'):
            return p.config.priority
    return 999
```
**Time**: 2 minutes
**Impact**: Without this fix, mock (always available) intercepts before cloud providers, potentially returning test responses in production.

### BUG-003: Ollama Model Gap (P2 — RESILIENCE)

**File**: Ollama instance at :11434
**Impact**: Ollama only has `nomic-embed-text:v1.5` and `qwen2.5:0.5b` — none of the 11 configured models
**Impact**: Ollama fallback (priority 2) cannot serve any configured model
**Fix**: Pull required models into Ollama, or accept that Ollama is currently a dead fallback
**Time**: Variable (model download)

---

## §6 Architecture Quality Assessment

### Strengths
1. **Sovereignty-Tiered Active Sets** — Local LRU → Local Fabric → Cloud LRU → Cloud Fabric prevents sovereignty drift (Mandate 7)
2. **BSP Culling** — O(1) circuit breaker pre-check skips broken providers (id Software heritage)
3. **Budget Gate** — Cloud inference requires entity budget approval
4. **ResourceGuard** — AnyIO Semaphore(1) prevents OOM on 14Gi RAM system
5. **Entity Affinity** — YAML-backed entity→model routing with 4-tier fallback chain
6. **Health Monitor** — Circuit breaker integration with HALF_OPEN probing
7. **Token Ledger** — Sovereign token tracking per entity per trace

### Concerns
1. **Model path staleness** — The `models/gguf/local/all/` prefix suggests a migration was incomplete
2. **Mock in production chain** — MockProvider is always loaded even in production; should be gated on `OMEGA_ENV=test` only
3. **Cloud providers lack circuit breakers** — Google/OpenCode-Zen/Cline/Copilot have no breaker integration
4. **Embedding function is mock** — `embed()` returns random vectors; needs real embedding backend for RAG
5. **No health probe persistence** — Backend detection is ephemeral; no persistent health state across restarts

---

## §7 GO / NO-GO Recommendation

### **NO-GO for Epoch I Phase 1**

| Gate | Criterion | Status |
|------|-----------|--------|
| G1 | native-gguf can load configured models | **❌ FAIL** — 8/11 paths broken |
| G2 | At least 3 local models loadable | **⚠️ PARTIAL** — Only phi-4-mini, phi-4-mini-reasoning, qwen3-vl correct |
| G3 | Provider chain respects local-first | **❌ FAIL** — Sort bug causes mock interception |
| G4 | Cloud fallback functional | **✅ PASS** — opencode-zen, cline, github-copilot detected |
| G5 | Circuit breaker operational | **✅ PASS** — HealthMonitor integrated |
| G6 | No telemetry (M8) | **✅ PASS** — No external calls detected |
| G7 | AnyIO compliance (M1) | **✅ PASS** — All async paths use AnyIO |

### Remediation Path (Estimated: 15 minutes)

1. **[2 min]** Fix 8 model paths in `config/models.yaml`:
   - Change `models/gguf/local/all/` → `models/local/all/`
2. **[2 min]** Fix provider sort in `model_gateway.py`:
   - Update `_get_priority()` to handle ProviderConfig
3. **[5 min]** Run `make test` to verify no regressions
4. **[5 min]** End-to-end native-gguf test:
   - Load qwen3-1.7b via native-gguf
   - Generate a test response
   - Verify M22 provenance tracking

**After these 3 fixes → re-evaluate for GO.**

---

## §8 Recommendations

### Immediate (Before Phase 1)
1. Fix model paths (BUG-001) — P0 blocking
2. Fix provider sort (BUG-002) — P1 sovereignty
3. Add `OMEGA_ENV=production` gate to MockProvider loading (currently only gated on `test`)

### Short-Term (Phase 1)
4. Load qwen3:1.7b and qwen3:0.6b into Ollama for fallback redundancy
5. Wire real embedding backend (embeddinggemma-300m is available but not wired to native-gguf)
6. Add cloud provider health probes (Google API key validation, OpenCode Zen ping)

### Medium-Term (Phase 2)
7. Implement persistent health state (survive Gateway restarts)
8. Add model hot-swap (load/unload without Gateway restart)
9. Budget gate per-entity cloud spend tracking with alerts

---

*⬡ OMEGA ⬡ P6-COGNITION ⬡ mimo-v2.5-free ⬡ opencode ⬡ FINAL-REVIEW ⬡ EPOCH-I-GATE*
