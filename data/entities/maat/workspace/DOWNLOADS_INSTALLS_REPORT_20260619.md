<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MA'AT — Downloads & Installs Report 2026-06-20
⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_embedding_deployment ⬡ P1

---

## Summary
**Status**: ✅ ALL EMBEDDING PROVIDERS WORKING
**Test Suite**: 444/444 passing (up from 440 baseline)
**Benchmark**: Complete — 3 models tested, Potion is **80.3x faster** than MiniLM

---

## §1 What Was Downloaded

### 1.1 all-MiniLM-L6-v2-Q4_K_M.gguf (20MB)
- **Source**: `second-state/all-MiniLM-L6-v2-Embedding-GGUF`
- **File**: `/media/arcana-novai/omega_library/models/gguf/all-MiniLM-L6-v2-Q4_K_M.gguf`
- **Size**: 20 MB (Q4_K_M quantization — good quality/size tradeoff)
- **Status**: ✅ Loads in 0.18s, works with llama-cpp-python 0.3.28
- **Note**: The old 44MB `all-MiniLM-L6-v2-f16.gguf` at `lmstudio-models/local/all/` is **incompatible** with llama-cpp-python 0.3.28 (GGUF format mismatch). The new one works.

### 1.2 potion-base-2M (cached from HuggingFace Hub)
- **Source**: `minishlab/potion-base-2M`
- **Path**: Cached in `~/.cache/huggingface/hub/` and saved to `/media/arcana-novai/omega_library/models/gguf/potion-base-2M/`
- **Size**: ~2MB (10 files: model.safetensors, config.json, tokenizer files, onnx)
- **Status**: ✅ Loads in 1.33s (first time), 0.3ms per sentence after loading
- **Dimension**: 64

### 1.3 potion-mxbai-micro (cached from HuggingFace Hub)
- **Source**: `blobbybob/potion-mxbai-micro`
- **Path**: Cached in `~/.cache/huggingface/hub/`
- **Size**: ~14MB (6 files: model.safetensors, config, tokenizer, etc.)
- **Status**: ✅ Loads in 0.45s, 0.3ms per sentence after loading
- **Dimension**: 256

---

## §2 What Was Installed

### Pre-existing (no new installs needed)
| Package | Version | Status |
|---------|---------|--------|
| `llama-cpp-python` | 0.3.28 | ✅ Already installed |
| `model2vec` | 0.8.2 | ✅ Already installed |
| `huggingface-hub` | Latest | ✅ Already installed |

No new packages were installed — all dependencies were already present in the venv.

### Ollama nomic-embed-text Model
| Model | Size | Status |
|-------|------|--------|
| `nomic-embed-text:v1.5` | 274 MB | ✅ Already pulled in Ollama |

---

## §3 What Was Wired

### 3.1 LocalGGUFEmbeddingProvider Path Updated
**File**: `src/omega/memory/embeddings.py`
- **Old path**: `/media/arcana-novai/omega_library/lmstudio-models/local/all/all-MiniLM-L6-v2-f16.gguf` (incompatible)
- **New path**: `/media/arcana-novai/omega_library/models/gguf/all-MiniLM-L6-v2-Q4_K_M.gguf` (20MB, working)

### 3.2 Flat List Output Fix
**File**: `src/omega/memory/embeddings.py` — `LocalGGUFEmbeddingProvider.get_embedding()`
- **New GGUF behavior**: `llama.embed()` returns flat `List[float]` (384 elements), not nested `List[List[float]]`
- **Fix**: Handles both formats transparently
  ```python
  if isinstance(result[0], float):
      return list(result)  # new GGUF: flat list
  return result[0]          # old GGUF: nested list
  ```

### 3.3 New StaticEmbeddingProvider Added
**File**: `src/omega/memory/embeddings.py` — new class `StaticEmbeddingProvider`
- Uses `model2vec.StaticModel` for sub-millisecond embedding inference
- **Default model**: `minishlab/potion-base-2M` (64-dim, ~2MB)
- **Alternative**: `blobbybob/potion-mxbai-micro` (256-dim, ~14MB)
- **[id-soft: doom-1993] Precomputed Lookup** pattern

### 3.4 EmbeddingManager Chain Updated
**File**: `src/omega/memory/embeddings.py` — `EmbeddingManager.__init__()`
- **New chain**: LocalGGUF → StaticEmbedding → Ollama → Fallback
- Previously: LocalGGUF → Ollama → Fallback

---

## §4 Test Results

| Test | Result | Details |
|------|--------|---------|
| `make test` | ✅ **444 passed** | Up from 440 baseline |
| Provider: LocalGGUF | ✅ 384-dim, 0.18s load, 24.1ms/sent | all-MiniLM Q4_K_M |
| Provider: StaticEmbedding (potion-base-2M) | ✅ 64-dim, 1.33s load, 0.3ms/sent | Tiny & fast |
| Provider: StaticEmbedding (potion-mxbai-micro) | ✅ 256-dim, 0.45s load, 0.3ms/sent | Medium quality |
| Provider: Ollama | ✅ 768-dim, 0.09s first call | nomic-embed-text |
| Provider: Fallback | ✅ 256-dim, zero-dependency | Hashing trick |
| EmbeddingManager chain | ✅ All 4 providers chain correctly | Graceful fallback |
| `make temple-grade` | ⚠️ Pre-existing failures | 5 antigravity module files missing [id-soft:] tags (not my changes) |

---

## §5 Embedding Benchmark Results

### Speed Comparison
| Model | Dim | Load Time | Per Sentence | RSS | Speed vs MiniLM |
|-------|-----|-----------|-------------|-----|-----------------|
| **MiniLM (Q4_K_M)** | 384 | **0.18s** | **24.1ms** | 107MB | 1x (baseline) |
| **Potion (base-2M)** | 64 | 1.33s* | **0.3ms** | 108MB | **80.3x faster** |
| **Potion (mxbai-micro)** | 256 | **0.45s** | **0.3ms** | 108MB | **80.3x faster** |

*\*First load downloads from HF Hub; subsequent loads use local cache.*

### Key Findings
1. **Potion is 80x faster** than MiniLM for inference (0.3ms vs 24ms per sentence)
2. **Potion-mxbai-micro (256-dim)** is the recommended default — balances quality and speed
3. **MiniLM (384-dim)** is still valuable as primary for highest quality needs
4. **Ollama (768-dim)** is best for quality-critical tasks (when Ollama is running)
5. All providers load < 1.5s on Ryzen 7 5700U

### Recommendation
Set `EmbeddingManager` default to `StaticEmbeddingProvider("blobbybob/potion-mxbai-micro")`
for general use, with MiniLM as primary for quality-critical queries.

---

## §6 Files Modified

| File | Change |
|------|--------|
| `src/omega/memory/embeddings.py` | Updated MiniLM path, added flat-list fix, added StaticEmbeddingProvider, updated EmbeddingManager chain |
| `scripts/test_potion_embedding.py` | Updated model paths, fixed GGUF output format handling, fixed model2vec API usage, added 3-model comparison |

---

## §7 Blockers Remaining

| Issue | Severity | Details |
|-------|----------|---------|
| Temple-grade heritage tags | 🟡 Low | 5 files in antigravity/ module pre-existing; not my changes |
| potion models cached in HF hub | 🟢 None | Already cached and saved locally for offline use |
| Old 44MB MiniLM still present | 🟢 None | Can be deleted to save space, but harmless |

---

*Report generated: 2026-06-20 22:13 UTC*
*Next step: Wire potion as PRIMARY embedding in EmbeddingManager or keep MiniLM as primary*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
