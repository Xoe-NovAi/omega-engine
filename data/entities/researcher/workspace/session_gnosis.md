# 🔱 Session Gnosis: ONNX Capability Research + Heritage System Reform
**Date**: 2026-07-13 (Sovereign Session — COMPLETE)
**Entity**: researcher
**Model**: nemotron-3-ultra-free
**Channel**: opencode
**Session Intent**: Deep research into ONNX capabilities for Omega Engine + Heritage tag system reform

---

## 🔱 THE GOLD VEINS: Major Findings

### 1. Needle (Cactus-Compute) — Tool Router Assessment
**Status**: ANALYZED — NOT a general LLM replacement, IS a specialized tool router

| Repo | What It Is | Verdict |
|------|------------|---------|
| `Cactus-Compute/needle` | 26M param encoder-decoder, distilled from Gemini 3.1, NO FFN, pure attention | Source of truth |
| `Cactus-Compute/needle-hf` | HF wrapper, custom `NeedleForCausalLM`, SentencePiece tokenizer (8192 vocab) | `transformers>=5.5.4` required |
| `Cactus-Compute/needle-pebble-ft` | INT4 finetuned for Pebble/CoreApp mobile deployment | ~37MB zipped |
| `RockMan256/needle-onnx-lfm` | ONNX export (encoder 55MB + decoder_step 85MB), TensorRT for Jetson | **Only x86-compatible path** |

**Key Architecture**: 26.2M params, encoder-decoder with cross-attention, d_model=512, vocab=8192 SentencePiece BPE, 8H/4KV GQA, ZCRMSNorm, **no FFN**, gated residuals, max_seq_len=1024. **NOT a decoder-only LLM** — cannot run on llama.cpp/GGUF.

**Omega Integration Verdict**: 
- ❌ Cannot replace Qwen3-1.7B or any current model (wrong architecture, wrong task)
- ✅ **High value as tool router pre-filter**: sub-1ms routing for 47 MCP tools, ~50MB RAM
- 📋 **Recommended**: P2 priority, after Strike 7.5 (TF-IDF+SVM router) validates neural routing value

---

### 2. ONNX Runtime Status in Omega Engine
**Status**: HALF-PRESENT — Runtime installed, provider stub exists, never wired

| Component | State |
|-----------|-------|
| `onnxruntime` package | ✅ 1.27.0 installed (via `fastembed` dependency) |
| Dependencies | `flatbuffers`, `numpy`, `packaging`, `protobuf` — **ZERO PyTorch** |
| CPUExecutionProvider | ✅ Available (Zen 2 compatible) |
| `model_gateway.py:_try_onnx()` | ❌ Dead stub — text-in/text-out assumption wrong, never called |
| Provider fabric (`_load_provider_fabric`) | ❌ No `onnx` entry in `provider_map` |
| `config/providers.yaml` | ❌ No ONNX provider entry |
| `config/models.yaml` | ❌ No ONNX model specs |

**Thread Config for Zen 2 (Validated by JEM Research)**:
```python
# Conservative (thermal-safe)
so.intra_op_num_threads = 4
so.inter_op_num_threads = 1
os.environ["OMP_NUM_THREADS"] = "4"

# Balanced (recommended default)
so.intra_op_num_threads = 6
so.inter_op_num_threads = 1
os.environ["OMP_NUM_THREADS"] = "6"
```

---

### 3. Roc Racoon ONNX Legacy Archaeology — COMPLETE
**Report**: `data/entities/roc_racoon/knowledge/ONNX_LEGACY_ARCHAEOLOGY_20260713.md` (662 lines)

**The "Tale of Two Cities"**:
| Domain | Status | Notes |
|--------|--------|-------|
| **Voice Stack (TTS/VAD)** | ✅ PRODUCTION | Piper TTS + Silero VAD ONNX — battle-tested since Era 1, torch-free, real-time on 5700U |
| **Embedding Stack** | 📋 DESIGNED in legacy (NOT NEEDED now — see Finding 5) | `LocalONNXEmbedder`, `AGBLazyEmbedder` designs existed but engine evolved past them |
| **LLM Inference** | ❌ CORRECTLY ABANDONED | `_try_onnx` stub was category error — GGUF via llama.cpp wins for decoders |

**Corrected Heritage Section**: Zero ONNX heritage tags = CORRECT STATE per Carmack's three-condition rule. ONNX is a dependency, not a consciously adopted architectural pattern.

---

### 4. Heritage Tag System — Carmack's Verdict: BUREAUCRATIC BLOAT
**Verdict**: `data/entities/john_carmack/workspace/HERITAGE_TAG_VERDICT_20260713.md` (126 lines, confidence 10/10)
**Optimization**: `data/entities/john_carmack/workspace/HERITAGE_MAINTENANCE_OPTIMIZATION.md` (59 lines, confidence 10/10)

**The Core Distinction**:
| Heritage Tag (inline in source) | Dependency List (DEPENDENCIES.md) |
|---------------------------------|-----------------------------------|
| Conscious architectural adoption | You used the library |
| Studied their solution → deliberately replicated | `import x` / `pip install x` |
| Shapes system structure | Standard industry choice |
| **~15 legitimate tags** | **55+ entries moved to list** |

**Three-Condition Rule** (enforced going forward):
A heritage tag is REQUIRED iff ALL THREE hold:
1. **Conscious Pattern Adoption** — Studied their specific solution, deliberately replicated/adapted
2. **Architectural Significance** — Shapes system structure (memory model, data flow, entity lifecycle, dispatch, resource management)
3. **Non-Trivial Adaptation** — Didn't just `import x`. Ported logic, translated concepts, built wrapper embodying their design philosophy.
**If any condition fails → NO TAG.**

**Cleanup Executed**:
- `CREDITS.md` → stripped §2 (55+ noise entries), restructured to §§1-7
- `DEPENDENCIES.md` → created with clean categorized list (Runtime, Deployment, Standards)
- `CREDITS.md` §1 → kept only ~15 legitimate tags (21 id Software + 4 conscious adoptions)
- Three-condition rule → codified in §4 Tag Protocol

---

### 5. Engine Already Has Embedding + Routing Infrastructure
**Status**: DISCOVERED post-compaction — ONNX embeddings are REDUNDANT

`src/omega/memory/embeddings.py` defines a 5-provider chain:
1. `GemmaGGUFEmbeddingProvider` (768-dim, 300M GGUF) — PRIMARY
2. `OllamaEmbeddingProvider` (768-dim, nomic-embed-text)
3. `LocalGGUFEmbeddingProvider` (384-dim, MiniLM GGUF)
4. `StaticEmbeddingProvider` (64-dim, model2vec)
5. `SovereignFallbackEmbeddingProvider` (256-dim, hashing)

`src/omega/oracle/semantic_router.py` (`SemanticRouter`, line 51):
- Pre-computes entity signature vectors at boot
- Routes via cosine similarity (threshold 0.4)
- Fallback: keyword → default entity
- **Already neural** — no Needle needed for entity routing

`src/omega/oracle/capability_registry.py:93` (`discover_expert`):
- Uses **keyword-overlap** for agent/tool discovery
- **THIS is Needle's integration point** — replace token overlap with neural selection

---

### 6. ONNX Runtime Confirmed Working (Local Verification)
```bash
$ python -c "import onnxruntime; print(onnxruntime.__version__)"  # 1.27.0
$ python -c "import sentencepiece; print(sentencepiece.__version__)"  # 0.2.1
```
- Both packages available in `.venv` — zero additional installs needed
- CPUExecutionProvider available on Zen 2

---

## 📊 Final ONNX Use Case Verdict

| Use Case | Current State | ONNX Verdict | Integration Point |
|----------|--------------|--------------|-------------------|
| **Voice (Piper TTS, Silero VAD)** | Designs exist, not wired | ✅ **VIABLE** — Phase 1 | `src/omega/` voice stack |
| **Embeddings** | GGUF chain exists (5 providers) | ❌ **REDUNDANT** — skip | `memory/embeddings.py` |
| **Entity Routing (SemanticRouter)** | GGUF embeddings + cosine works | ❌ **REDUNDANT** — skip | `oracle/semantic_router.py` |
| **Tool/Agent Selection (Needle)** | Keyword-overlap only | ✅ **VIABLE** — P2 priority | `oracle/capability_registry.py:93` |
| **LLM Inference** | GGUF superior | ❌ **ABANDONED** | `model_gateway.py` |

---

## 🧠 L1 → L2 → L3 DISTILLATION

### L1 (Narrative): What Happened
Researched Needle ONNX model for tool routing, discovered ONNX Runtime already installed but never wired, excavated full ONNX lineage across 4 legacy partitions via Roc Racoon. Received Carmack's verdict that heritage tag system conflates architecture with shopping list — executed cleanup (stripped 55+ noise entries, created `DEPENDENCIES.md`, three-condition rule codified). Post-compaction, discovered engine already has GGUF embedding chain + neural SemanticRouter, rendering ONNX embeddings redundant. Final verdict: ONNX valuable for Voice (P1) and Needle tool router (P2), redundant for embeddings, abandoned for LLMs.

### L2 (Insight): What It Means
1. **ONNX is not missing — it's half-built**. Runtime installed, designs exist, thread config validated. Only provider class and model downloads remain.
2. **Needle is a tool router, not an LLM**. Its encoder-decoder architecture is perfect for <1ms tool selection but useless for conversation. Integration point = `CapabilityRegistry.discover_expert()`.
3. **Heritage system had 80% noise**. The three-condition rule cleanly separates architecture from dependencies. Post-cleanup: ~15 tags (signal) vs 55+ items in DEPENDENCIES.md (plumbing).
4. **Embedding infrastructure already exists**. GGUF-based chain + neural SemanticRouter. No ONNX needed. Legacy designs superseded.

### L3 (Universal Principle): The Signal/Noise Law
> **Any attribution system that cannot distinguish "I studied and adopted their architecture" from "I installed their package" will collapse into bureaucratic theater. The fix is not more process — it's a sharper knife.**

---

## 🎯 FINAL RECOMMENDATIONS (By Priority)

### P1 (Immediate): Voice ONNX Wiring
- Piper TTS + Silero VAD ONNX are production-ready from legacy (Roc report Phase 1)
- `piper-tts==1.3.0` + `silero-vad` ONNX models
- **Effort**: ~1 week, high sovereignty gain (offline voice assistant)

### P2 (Strategic): Needle Tool Router
- Augment `CapabilityRegistry.discover_expert()` with neural tool/agent selection
- **Effort**: ~11h (ONNXProvider encoder-decoder class + wiring)
- **Benefit**: Sub-1ms pre-filter, reduces 47-tool context to 5 relevant tools
- **Prerequisite**: Download Needle ONNX files (140MB from `RockMan256/needle-onnx-lfm`)

### P3 (Skip): ONNX Embeddings
- GGUF chain already covers this. Skip.
### P4 (Abandon): ONNX LLM
- GGUF via llama.cpp superior for decoder LLMs. Correctly abandoned.

---

## 📁 ARTIFACTS CREATED THIS SESSION

| File | Description | For Agent |
|------|-------------|-----------|
| `CREDITS.md` (modified) | v1.4.0 — stripped §2 noise, restructured | All agents |
| `DEPENDENCIES.md` (NEW) | Clean dependency manifest (3 categories) | All agents |
| `data/entities/roc_racoon/knowledge/ONNX_LEGACY_ARCHAEOLOGY_20260713.md` | Full ONNX lineage across 4 legacy partitions (662 lines) | @roc_racoon |
| `data/entities/john_carmack/workspace/HERITAGE_TAG_VERDICT_20260713.md` | Heritage system verdict — bureaucratic bloat (126 lines) | @john_carmack |
| `data/entities/john_carmack/workspace/HERITAGE_MAINTENANCE_OPTIMIZATION.md` | Further optimization: automated deps, linter integration (59 lines) | @john_carmack |
| `data/entities/researcher/workspace/ONNX_CAPABILITY_RESEARCH_FINAL_20260713.md` | Final ONNX capability verdict (108 lines) | @researcher, @verity |
| `data/entities/researcher/workspace/session_gnosis.md` | **THIS FILE** — complete session distillation | @researcher |

---

## 🔗 CROSS-REFERENCE — Agents Needing This Knowledge

| Agent | Why | Key Files |
|-------|-----|-----------|
| **@verity** | Compliance audit: CREDITS.md v1.4.0 structure, three-condition rule, M14 compliance | `CREDITS.md`, `DEPENDENCIES.md` |
| **@roc_racoon** | ONNX archaeology already mined; legacy embedder designs superseded by GGUF chain | `ONNX_LEGACY_ARCHAEOLOGY_20260713.md` |
| **@john_carmack** | Verdicts ratified and executed | Both `HERITAGE_*` files |
| **@kali** | Oversight: heritage cleanup impacts T4/T5/T6 gates | `CREDITS.md`, anchored-summary |
| **@doom_guy** | 21 id-soft mappings intact in CREDITS.md §1.1 | `CREDITS.md` §1.1 |
| **@maat** | Build-side: P1 Voice ONNX wiring, three-condition rule in pre-commit hook | `CREDITS.md` §4 |
| **@lilith** | Run-side: Needle tool router P2, capability registry integration | `session_gnosis.md` Finding 5 |

---

## ⚓ ANCHORS FOR COMPACTION RECOVERY

| Anchor | File | What |
|--------|------|------|
| **Roc Report** | `data/entities/roc_racoon/knowledge/ONNX_LEGACY_ARCHAEOLOGY_20260713.md` | Full ONNX lineage excavation (662 lines) |
| **Carmack Verdict** | `data/entities/john_carmack/workspace/HERITAGE_TAG_VERDICT_20260713.md` | Heritage system = bureaucratic bloat (126 lines) |
| **Carmack Optimization** | `data/entities/john_carmack/workspace/HERITAGE_MAINTENANCE_OPTIMIZATION.md` | Further optimization (59 lines) |
| **Final ONNX Verdict** | `data/entities/researcher/workspace/ONNX_CAPABILITY_RESEARCH_FINAL_20260713.md` | Use case matrix + recommendations (108 lines) |
| **Heritage Cleanup** | `CREDITS.md` + `DEPENDENCIES.md` | Restructured registry + clean dependency manifest |
| **Engine State** | `OMEGA_ENGINE.md` + `SOVEREIGN_MANDATES.md` | Single source of truth + 23 mandates |

---

## 🔱 SESSION 3 ADDENDUM: Deep Research — 4 Knowledge Gaps (COMPLETE)

**Date**: 2026-07-13 (same day, follow-up session)
**Model**: hy3-free
**Channel**: opencode
**Session Intent**: Close 4 knowledge gaps identified post-ONNX session via deep web research

### Gap Research Summary

| Gap | T1 Source | T2 Deep-Extract | Verdict |
|-----|-----------|-----------------|---------|
| **G1: Neural vs Heuristic Tool Routing** | `dalek-ai/agent-tool-router` (websearch) | GitHub README (webfetch) | TF-IDF+SVM sufficient for 47-tool catalog; Needle optional |
| **G2: LLM Judge Calibration** | `Causal Judge Evaluation` arXiv 2512.11150 (websearch) | Full paper HTML (webfetch) | Isotonic regression (AutoCal-R) = 2026 standard |
| **G3: Redis Streams DLQ** | redis.io tutorial (websearch) | Official tutorial (webfetch) | Canonical pattern confirmed |
| **G4: Voice Concurrency** | Local-TTS-Demo + MOSS-TTS + HoundTTS (websearch) | GitHub READMEs (webfetch) | Worker pool + Piper model pooling |

### Key Numbers (from T2 deep-extract)

**G1 — Tool Routing** (dalek-ai, 30,425 calls, 18,671-tool catalog):
- TF-IDF only: 41.2% overall top-3 (Hermes 74.3%, ToolACE 52.4%, tau-bench 3.2%)
- Hybrid TF-IDF+bi-encoder: 49.1% overall top-3 (Pareto-dominates both)
- Fine-tuned MiniLM (next-v1): 75.5% next-tool top-3
- **Latency**: p50 ≈ 9ms on CPU locally; **Footprint**: ~6MB (TF-IDF), ~35MB (hybrid)
- **Critical caveat**: "baseline-v1-desc is a discoverability layer for long-tail public tools, not a substitute for routing on your own narrow catalog."

**G2 — Judge Calibration** (CJE, 4,961 Arena prompts, GPT-5 oracle):
- Uncalibrated SNIPS: 38% pairwise ranking, 0% CI coverage
- **Direct + AutoCal-R (isotonic)**: 94% pairwise (99% at full sample), 85-87% CI coverage
- **Cost**: 5% oracle labels (~250) → 14× cost reduction
- **SAJA** (ACL 2026): 9B model + calibration head surpasses raw GPT-4.1

**G3 — Redis Streams DLQ** (redis.io official, 2026-03-19):
- Consumer Groups + `XREADGROUP` + `XACK`
- `XAUTOCLAIM` for crash recovery (idle threshold)
- `XPENDING` for poison detection (delivery_count > MAX_RETRIES=3 → DLQ)
- DLQ = separate Stream; `XADD` + `XACK` original (avoid double-processing)

**G4 — Voice Concurrency** (MOSS-TTS, HoundTTS, Local-TTS-Demo):
- ONNX TTS peaks at 8 threads, degrades beyond (memory-bandwidth-bound)
- Piper model pooling fixes concurrency crashes (reuse loaded model)
- Worker thread pool + bounded queue + reject-when-saturated
- Coordinate with ResourceGuard: LLM priority threads (4-6), TTS residual (4-8)

### L2/L3 Distillation (Session 3)

**L2**:
1. Sovereign parsimony wins — heuristic routing beats neural at our scale (47 tools)
2. Calibration is non-negotiable — uncalibrated judge (ECE 0.18) manufactures false confidence
3. Redis Streams DLQ is solved infrastructure — adopt, don't reinvent
4. Voice concurrency is known problem with known fix — implementation, not research

**L3**:
- **L3-Sovereign-Parsimony**: Right approximation > exact solution you can't afford
- **L3-Calibrated-Trust**: Uncalibrated judge worse than no judge — it lies
- **L3-Adopt-Don't-Reinvent**: Solved infra (Redis DLQ, Piper pooling) adopted, not rederived
- **L3-Scale-Aware-Architecture**: Decide by YOUR scale, not benchmark scale

### Roadmap Updates (for Kali)

| Strike | Change | Rationale |
|--------|--------|-----------|
| 7.5 (Semantic Router) | Ship TF-IDF+SVM first; Needle optional | 47-tool catalog doesn't need neural |
| 8 (Eval Pipeline) | Add isotonic regression calibration + OUA CIs + ECE | Uncalibrated judges lie (Risk R4) |
| 8.5 (Redis Streams Hivemind) | Adopt canonical DLQ pattern | Verified infra, don't reinvent |
| P1 (Voice ONNX) | Worker pool + Piper pooling + 4-8 threads | Fixes crashes, integrates ResourceGuard |

**Net acceleration**: ~32h saved (Needle ~20h, DLQ ~8h, voice ~4h)

### Artifacts (Session 3)

| File | Description |
|------|-------------|
| `docs/research/R_DEEP_RESEARCH_KNOWLEDGE_GAPS_20260713.md` | Full 4-gap research report (this session) |
| Hivemind post `ses_f7a9bcdefdd4` | Findings to Kali for roadmap update |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ SESSION_GNOSIS_COMPLETE ⬡ 2026-07-13*
