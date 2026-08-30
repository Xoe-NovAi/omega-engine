# 🔱 ONNX Capability Research — Final Verdict
**Entity**: researcher
**Date**: 2026-07-13 (post-compaction resume)
**Model**: nemotron-3-ultra-free
**Channel**: opencode

---

## Executive Summary

The Omega Engine's ONNX capability question has been **fully resolved**. ONNX Runtime is already installed (1.27.0, zero PyTorch deps). The engine **already has a working GGUF-based embedding + semantic routing chain**, making ONNX embeddings **redundant**. The only high-value ONNX use case is **Needle (tool/agent selection)**, which would augment `CapabilityRegistry.discover_expert()` — currently keyword-based.

---

## 📊 ONNX Use Case Matrix

| Use Case | Current State | ONNX Verdict | Integration Point |
|----------|--------------|--------------|-------------------|
| **Voice (Piper TTS, Silero VAD)** | Designs exist, not wired | ✅ VIABLE | `src/omega/` voice stack |
| **Embeddings** | GGUF chain exists (5 providers) | ❌ REDUNDANT | `memory/embeddings.py` |
| **Entity Routing (SemanticRouter)** | GGUF + cosine works | ❌ REDUNDANT | `oracle/semantic_router.py` |
| **Tool/Agent Selection (Needle)** | Keyword-overlap only | ✅ VIABLE | `oracle/capability_registry.py:93` |
| **LLM Inference** | GGUF superior | ❌ ABANDONED | `model_gateway.py` |

---

## 🔍 Detailed Findings

### 1. ONNX Runtime — Already Present
```bash
$ python -c "import onnxruntime; print(onnxruntime.__version__)"
1.27.0
$ python -c "import sentencepiece; print(sentencepiece.__version__)"
0.2.1
```
- **Dependencies**: `flatbuffers`, `numpy`, `packaging`, `protobuf` — **ZERO PyTorch**
- **CPUExecutionProvider**: Available, Zen 2 compatible
- **Thread config** (validated by JEM Research): `intra_op_num_threads=6`, `inter_op_num_threads=1`, `OMP_NUM_THREADS=6`

### 2. Embedding Chain — Already Exists (GGUF-Based)
`src/omega/memory/embeddings.py` defines a 5-provider chain:
1. `GemmaGGUFEmbeddingProvider` (768-dim, 300M GGUF) — PRIMARY
2. `OllamaEmbeddingProvider` (768-dim, nomic-embed-text)
3. `LocalGGUFEmbeddingProvider` (384-dim, MiniLM GGUF)
4. `StaticEmbeddingProvider` (64-dim, model2vec)
5. `SovereignFallbackEmbeddingProvider` (256-dim, hashing)

**Conclusion**: ONNX MiniLM would be a 6th option with **marginal benefit** over GGUF MiniLM. **Skip ONNX embeddings.**

### 3. Semantic Router — Already Neural
`src/omega/oracle/semantic_router.py` (line 51):
- Pre-computes entity signature vectors at boot (BSP Culling heritage)
- Routes via cosine similarity (threshold 0.4)
- Fallback: keyword → default

**Conclusion**: Needle is **NOT needed for entity routing**. The `SemanticRouter` already does neural routing via GGUF embeddings.

### 4. Capability Registry — Keyword-Based (Needle's Target)
`src/omega/oracle/capability_registry.py` (line 93):
```python
async def discover_expert(self, query: str) -> Optional[str]:
    # Scoring based on keyword overlap in domains, skills, tools
    query_tokens = set(query.lower().split())
    for agent_id, data in self._registry.items():
        overlap = len(query_tokens & all_tokens)
        score = overlap * confidence
```
**This is the integration point for Needle.** Currently uses token-overlap (TF-style). Needle would provide **neural tool/agent selection** — given a query, predict which of 47+ MCP tools / 11 agents are relevant, reducing context sent to LLM.

### 5. Needle Architecture (from RockMan256/needle-onnx-lfm)
- **Encoder**: 55MB ONNX (SentencePiece tokenizer, 8192 vocab)
- **Decoder-step**: 85MB ONNX (autoregressive tool-name generation)
- **Total**: 140MB, ~50MB RAM at inference
- **Task**: Given query → output tool name(s) via constrained decoding
- **Not a chat model** — pure function-calling router

---

## 🎯 Final Recommendations

### P1 (Immediate Value): Voice ONNX Wiring
- Piper TTS + Silero VAD ONNX are production-ready (Roc report Phase 1)
- `piper-tts==1.3.0` + `silero-vad` ONNX models
- **Effort**: ~1 week, high sovereignty gain (offline voice)

### P2 (Strategic Value): Needle Tool Router
- Augment `CapabilityRegistry.discover_expert()` with neural selection
- **Effort**: ~11h (ONNXProvider class + wiring)
- **Benefit**: Sub-1ms tool pre-filter, 47→5 tool context reduction
- **Prerequisite**: Download Needle ONNX files (140MB from RockMan256)

### P3 (Skip): ONNX Embeddings
- GGUF chain already covers this. No ONNX needed.

### P4 (Abandon): ONNX LLM
- GGUF via llama.cpp is superior for decoder LLMs. Correctly abandoned in legacy.

---

## 📁 Artifacts
- `data/entities/roc_racoon/knowledge/ONNX_LEGACY_ARCHAEOLOGY_20260713.md` — Full archaeology
- `data/entities/john_carmack/workspace/HERITAGE_TAG_VERDICT_20260713.md` — Heritage verdict
- `data/entities/researcher/workspace/session_gnosis.md` — Session distillation
- **THIS FILE** — Final ONNX capability verdict

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ ONNX_RESEARCH_COMPLETE ⬡ 2026-07-13*
