# 🔱 Heritage & Performance Review — Fleet Model Proposal
# ⬡ OMEGA ⬡ DOOM GUY ⬡ deepseek-v4-flash ⬡ opencode ⬡ M14-VETTING
**AP Token**: AP-HERITAGE-PERF-REVIEW-v1.0.0
**Date**: 2026-06-19
**Vetter**: Doom Guy (Heritage Gatekeeper) — ratified by Sovereign Mandate M14
**Scope**: Dolphin 3.0 8B · all-MiniLM-L6-v2 · potion-mxbai-micro · cross-encoder/nli-distilroberta-base
**Hardware Target**: Ryzen 7 5700U (Zen 2, 8C/16T, 14GB RAM, no GPU)

---

## §0 Executive Summary

**Overall Verdict**: 🟡 **CAUTION — Conditional GO with priority ordering**

| Component | Heritage Verdict | Performance Verdict | Integration Priority |
|-----------|-----------------|-------------------|---------------------|
| Dolphin 3.0 Llama 3.1 8B (Q4_K_M) | 🟢 NO VET NEEDED | 🟡 CAUTION — tight RAM | P1 (after RAM audit) |
| all-MiniLM-L6-v2 (ONNX) | 🟢 NO VET NEEDED | 🟢 GO — lightweight | P1 (immediate) |
| potion-mxbai-micro | 🟢 APPROVED (heritage-023) | 🟢 GO — 700KB, 80x faster | P1.5 (after MiniLM) |
| nli-distilroberta-base | 🟢 NO VET NEEDED | 🟡 CAUTION — speed unknown | P2 (after embeddings) |

**Core tradeoff**: Dolphin 8B gives us a chat-optimized uncensored generalist, but at 5GB
resident it leaves only ~4.2GB headroom on a 12GB-available system. The Qwen3-4B-Think
fills a *different* niche (thinking/reasoning/CoT) and should NOT be replaced — both
should coexist.

---

## §A — Heritage Vetting

### A.1 Dolphin 3.0 Llama 3.1 8B

**Verdict**: 🟢 **NO HERITAGE VET NEEDED**

**Reasoning**: The Heritage Vetting Pipeline (M14) applies to **architectural patterns**
ported from id Software games into Omega Engine source code — things like BSP culling,
ZONEID constants, lazy deletion, the cvar table. These are *engineering patterns* with
`[id-soft:]` inline tags.

Dolphin 3.0 is a **pre-trained model**, not an architectural pattern. It carries:
- **Meta's heritage** (Llama 3.1 architecture: GQA, SwiGLU, RoPE, 128K context)
- **Eric Hartford's heritage** (Dolphin fine-tuning methodology, uncensored training data)
- **No id Software heritage** whatsoever

**Neither Meta's GQA nor SwiGLU nor RoPE need `[id-soft:]` tags** because:
1. The tags exist to credit id Software patterns in *our* source code
2. We are not implementing GQA/SwiGLU/RoPE — we are *consuming* a model that uses them
3. Meta's architectural innovations are already attributed via their model card / license

**Exception — if we write an adapter/loader for Dolphin-specific features (e.g., persona
steering), that code should carry the tag `[id-soft: quake3-1999] Hard-Boundary` if it
follows the engine-zone/game-zone pattern for separating system prompt from model config.

**Score**: N/A — not a vet-eligible pattern.

**Applicable Heritage**: If the *rationale* for picking Dolphin over other 8B models is
"the right approximation for the use case" (uncensored generalist beats censored one),
that decision framework carries the FISR heritage lineage and should be attributed in
the decision log: `[Right Approximation: evolved from FISR, id Software 1999]`.

---

### A.2 all-MiniLM-L6-v2

**Verdict**: 🟢 **NO HERITAGE VET NEEDED**

**Reasoning**: This is an off-the-shelf SentenceTransformer embedding model (22.7M params,
384 dimensions, BERT-based). It's a standard ML model, not a translated game engine
pattern. No `[id-soft:]` tags needed.

**However** — if we implement a **provider-specific embedding adapter** that uses the
BSP culling pattern for O(1) embedding provider health checking, that adapter code
carries `[id-soft: doom-1993] BSP Culling — embedding provider health check`.

---

### A.3 potion-mxbai-micro — NEW HERITAGE MAPPING (heritage-023)

**Verdict**: 🟢 **APPROVED — Heritage Mapped**

**Score**: 8/10 — (heritage-023)

**Date**: 2026-06-19

#### Heritage Mapping

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `r_main.c` (Doom, 1993) — colormap lookup tables / `m_fixed.c` — 16.16 fixed-point | `potion-mxbai-micro` — static embedding lookup via model2vec |
| **Core idea** | Precompute expensive operations (lighting, trigonometry) into lookup tables; runtime is O(1) table access | Precompute token embeddings through the base model once; runtime is O(vocab) numpy matrix lookup + mean pooling |
| **Context** | Doom had a 35MHz 486 with no FPU — `sin()` and `cos()` were subroutine calls. Lighting calculations for 65535 angles were precomputed into `trig_tables[]` at compile time. | Model2Vec does one forward pass per token in the vocabulary (~32K tokens), stores the result, then at inference time just averages token lookups. No transformer forward pass needed. |
| **What it saves** | ~200 CPU cycles per trig call vs ~4 cycles per table lookup | ~30-50ms per sentence (MiniLM transformer forward pass) vs ~0.01-0.1ms per sentence (numpy lookup) |
| **Tradeoff** | Fixed precision (no floating point); angle granularity limited to table size | Loss of contextualization — static embeddings can't distinguish "bank (river)" from "bank (finance)" |
| **Omega evolution** | Static C arrays → downloadable 700KB numpy weight matrix. The *pattern identity* is unchanged: precompute once, look up forever. |

**Attribution format**: `[Precomputed Lookup: id Software 1993]`
**Inline tag format**: `# [id-soft: doom-1993] Precomputed Lookup — static embedding via model2vec`

**Qualification Gate**: Can this concept be justified without mentioning original
hardware constraints?

**YES**. The principle — "precompute the expensive operation once, store the results,
access O(1) at runtime" — is architecture-independent. Doom precomputed trig tables for
a 35MHz 486; Model2Vec precomputes token embeddings through a transformer. The hardware
constraint (no FPU in 1993) is *why Doom did it*, but the pattern stands alone:
**predictable offline cost for zero online cost**.

**Comparison to existing CREDITS.md entries**:
- **FISR** (§1.3): A *runtime approximation* technique. Model2Vec is NOT an approximation
  at runtime — it's deterministic lookup.
- **Surface/PVS Cache** (§1.5): Precomputation of *scene visibility*. Model2Vec
  precomputation of *semantic vectors*. Same "compute once, use many" philosophy, but
  Model2Vec is offline-training-time, not online-frame-time.

This is a **distinct mapping** — the colormap/lookup-table pattern from Doom's renderer:
precompute expensive math into a fixed table, reference at O(1) during the hot loop.

**Implementation status**: MAPPED — no implementation pending. When the model2vec
adapter is written for the embedding provider, it should carry:
```python
# [id-soft: doom-1993] Precomputed Lookup — static embedding via model2vec
# Doom precomputed trig tables at compile time; Model2Vec precomputes
# token embeddings through a transformer at distillation time.
# Both achieve O(1) lookup at runtime by paying the cost upfront.
```

---

### A.4 cross-encoder/nli-distilroberta-base

**Verdict**: 🟢 **NO HERITAGE VET NEEDED**

**Reasoning**: Off-the-shelf cross-encoder for NLI. Standard transformer model (82M params,
distilroberta-base architecture). Used for the Skeptical Verifier (vet-022 already
APPROVED the Knowledge Leak Detection *pattern* from Doom 3). The model itself is just
an implementation detail of an already-approved heritage pattern.

**Relationship to vet-022**: The Knowledge Leak Detection concept (flood-fill from
consistent state) was APPROVED as heritage-022. The NLI model is a possible
*implementation tool* for the semantic similarity component. The `[id-soft:]` tag for
vet-022 already exists: `# [id-soft: doom3-2004] Knowledge Leak Detection`.

**No additional vet needed.** The model choice is an engineering decision, not a new
heritage pattern.

---

## §B — ZONEID Allocation Recommendations

### B.1 Current ZONEID Allocation

| Hex | Name | Subsystem | Status |
|-----|------|-----------|--------|
| 0x1d4a11 | ZONEID_MEMORY | MemoryStore | ✅ Allocated |
| 0x1d4a12 | ZONEID_ENTITY | EntityRegistry | ✅ Allocated |
| 0x1d4a13 | ZONEID_BREAKER | HealthMonitor | ✅ Allocated |
| 0x1d4a14 | ZONEID_TRACE | ObservabilityEngine | ✅ Allocated |
| 0x1d4a15 | ZONEID_PROBE | ResourceGuard | ✅ Allocated |
| 0x1d4a16 | ZONEID_HANDOFF | SubagentDispatcher | ✅ Allocated |
| 0x1d4a17 | ZONEID_PRESENCE | LinkP9Runtime | ✅ Allocated |
| 0x1d4a18 | ZONEID_KNOWLEDGE | CrossPollination | ✅ Allocated |
| 0x1d4a19 | ZONEID_DEMAND | CrossPollination | ✅ Allocated |
| 0x1d4a1a | ZONEID_VERIFICATION | Sentinel | ✅ Allocated |
| 0x1d4a1b | ZONEID_ATOMIC | ResourceGuard | ✅ Allocated |
| 0x1d4a1c | ZONEID_SOMATIC | SomaticState | ✅ Allocated |
| **0x1d4a1d** | **— AVAILABLE —** | | |
| **0x1d4a1e** | **— AVAILABLE —** | | |
| **0x1d4a1f** | **— AVAILABLE —** | | |
| 0xDEADBEEF | ZONEID_TOMBSTONE | EntityRegistry | ✅ Tombstone sentinel |

### B.2 Proposed New ZONEID: Embedding Provider

**Recommendation**: 🟢 **YES — allocate 0x1d4a1d for embedding provider integrity**

**Rationale**: The Researcher report (Operation Deep-Siphon, D137-D141) identified that
embedding inference is a new discrete subsystem. Currently, embedding model calls go
through llama-server or SentenceTransformers — neither is covered by ZONEID validation.
Adding `ZONEID_EMBEDDING = 0x1d4a1d` to the embedding provider's result dataclass
protects against:

1. **Stale embedding cache entries** — an embedding from a different model version can
   be caught by zoneid mismatch on deserialization
2. **Wrong-dimension embeddings** — if the provider returns 384 instead of 768 dims,
   the zoneid validator catches it at the boundary
3. **Corrupt vector store entries** — Qdrant payload can include zoneid as a checksum

**Proposed constant**:
```python
# [id-soft: doom-1993] ZONEID Pattern — embedding provider result marker
ZONEID_EMBEDDING = 0x1d4a1d
```

**Location**: `src/omega/cvar_table.py` (new constant) + `src/omega/oracle/embedding_provider.py`
or wherever the embedding adapter lives.

**Implementation scope**:
- Add to `ZONEID_TABLE` and `CVAR_TABLE` in `src/omega/cvar_table.py`
- Add to `__all__` exports in `src/omega/constants.py` (backward compat)
- Validate on embedding cache read/write
- Validate on vector store serialization boundary

**Does NOT need a separate vet record** — it's an extension of the existing ZONEID
pattern (vet-008 via CREDITS.md §1.9).

### B.3 Proposed New ZONEID: NLI Verifier Result

**Recommendation**: 🟡 **OPTIONAL — allocate 0x1d4a1e if NLI results are cached/persisted**

If the Skeptical Verifier (vet-022) caches its verification results (entailment scores)
to disk, a ZONEID marker prevents stale verification results from being re-read after
model updates. If results are computed fresh each time, no ZONEID needed.

**Proposed constant**:
```python
# [id-soft: doom-1993] ZONEID Pattern — NLI verifier result marker
ZONEID_NLI = 0x1d4a1e
```

**Recommendation**: Defer until Vet-022 implementation decides on caching strategy.

---

## §C — Performance Feasibility Assessment (Zen 2 / Ryzen 7 5700U)

### C.1 Hardware Baseline

| Component | Specification |
|-----------|--------------|
| CPU | AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2, no AVX512) |
| RAM | 14GB total, ~12GB available for AI (after OS ~2GB) |
| GPU | None (integrated Radeon not used for inference) |
| Storage | NVMe, GGUF models on `/media/arcana-novai/omega_library/` |
| Inference | llama.cpp via native-gguf, Zen-2-optimized build (`-march=znver2 -mavx2 -mfma`) |
| Thread config | 6 threads pinned to physical cores [0,2,4,6] |
| KV cache | q8_0 key + q8_0 value (default) |

### C.2 Model Performance Estimates

| Model | Size (on disk) | RAM (loaded) | Est. tok/s (Zen 2) | Latency/req | Notes |
|-------|---------------|-------------|-------------------|-------------|-------|
| **Dolphin 3.0 8B Q4_K_M** | **4.58 GB** | **~5.5 GB** | **8-12 tok/s** | 10-15s for 128 tok | RAM-tight but viable |
| Qwen3-4B-Think Q4_K_M | 2.4 GB | ~2.7 GB | 12-20 tok/s | 5-10s for 128 tok | ✅ Already deployed |
| DeepSeek-R1-Qwen3-8B Q3_K_L | 4.2 GB | ~4.5 GB | 5-10 tok/s | 15-25s for 128 tok | ✅ Already deployed (different niche) |
| Krikri-8B Q4_K_M | 4.7 GB | ~4.9 GB | 7-11 tok/s | 12-18s for 128 tok | ✅ Already deployed |
| all-MiniLM-L6-v2 ONNX | 90 MB | ~90 MB | **~30-50 ms/sentence** | N/A — batch | ✅ Trivial |
| nli-distilroberta-base | 167 MB | ~170 MB | **~50-150 ms/pair** | N/A — batch | ⚠️ Batch-dependent |
| potion-mxbai-micro | 700 KB | ~2 MB | **~0.01-0.1 ms/sentence** | N/A — batch | ✅ Trivial |
| OS + always-loaded | — | ~2.8 GB | — | — | qwen3-1.7b (0.3G) + qwen3-0.6b warm (0.5G) + OS (~2G) |

### C.3 RAM Budget Analysis — Worst Case (Dolphin Loaded)

```
Category                  RAM (GB)
──────────────────────────────────────
OS overhead               ~2.0
qwen3-1.7b (always)       ~0.3
qwen3-0.6b (warm)         ~0.5
Dolphin 8B Q4_K_M         ~5.5
KV cache (4K ctx)         ~0.5
Embedding models (ONNX)   ~0.3   (MiniLM + NLI + potion ≈ 260MB)
──────────────────────────────────────
Total loaded              ~9.1
Available                  ~2.9
Headroom                   ~2.9 GB  ✅ Sufficient
```

**Key insight**: Because ResourceGuard enforces one-model-at-a-time for GGUF inference,
Dolphin 8B never coexists with other large models (Krikri, DeepSeek, etc.). The only
always-loaded models are the tiny ones (1.7B, 0.6B). This makes the 8B viable.

**However** — the KV cache scales with context length. At 128K context (Dolphin's native
max), the KV cache alone would be ~6-8GB. **Config recommendation**: cap at 8K-16K
context for Dolphin on this hardware to keep KV cache under 1GB.

### C.4 Interactive Usability — Dolphin 8B vs Qwen3-4B-Think

| Metric | Dolphin 8B | Qwen3-4B-Think | Gap Analysis |
|--------|-----------|----------------|-------------|
| Tok/s | 8-12 | 12-20 | 4B is 1.5-2x faster |
| Time to first token | ~1-3s | ~0.5-1.5s | 4B wins by ~1s |
| 50-token response | ~4-6s | ~2.5-4s | Both feel "interactive" |
| 200-token response | ~17-25s | ~10-17s | Dolphin shows sluggishness |
| 500-token response | ~42-62s | ~25-42s | Dolphin tests patience |

**Verdict**: Dolphin 8B at 8-12 tok/s is **at the boundary of interactive usability**.
Short responses (<100 tokens) feel fine. Long generations (>300 tokens) start to feel
sluggish. This is acceptable for:
- Agentic tasks (the agent doesn't need real-time human pacing)
- Batch processing
- Offline/background inference

It's **NOT ideal for**:
- Chat-style interactions where the user expects sub-5s responses
- Real-time streaming with human-in-the-loop
- Rapid-fire multi-turn conversations

**Comparison to other 8B models on this hardware**:
- DeepSeek-R1-Qwen3-8B Q3_K_L: 5-10 tok/s — slower than Dolphin (lower quantization)
- Krikri-8B Q4_K_M: 7-11 tok/s — comparable
- Dolphin 8B Q4_K_M: 8-12 tok/s — slightly faster due to Llama 3.1 architecture (GQA
  reduces KV cache computation)

### C.5 Should We Replace Qwen3-4B-Think with Dolphin 8B?

**Verdict**: 🔴 **NO — keep both**

**Rationale**: They serve different niches:

| Niche | Qwen3-4B-Think | Dolphin 8B |
|-------|---------------|------------|
| **Role** | Reasoning/CoT engine | General purpose chat/agent |
| **Strength** | Thinking traces, math, logic | Uncensored, steerable, function calling |
| **Speed** | 12-20 tok/s | 8-12 tok/s |
| **RAM** | 2.7 GB | 5.5 GB |
| **Use case** | Verity, Skeptical Verifier, audit | Dolphin entity, agentic tasks, open-ended chat |

**Recommended architecture**: Dolphin for uncensored general chat + agentic tasks;
Qwen3-4B-Think for verification, reasoning chains, and the Skeptical Verifier.
Both can coexist because they're never loaded simultaneously (ResourceGuard).

**What to REPLACE** (if replacing anything): The Krikri-8B (4.9GB loaded, similar speed)
could be deprecated in favor of Dolphin if Krikri's niche (creative writing, Inanna
entity) is covered by Dolphin's steerability. But that's a separate decision for the
entity owners — not a Heritage Gatekeeper determination.

### C.6 Embedding Model Performance — Zen 2

**all-MiniLM-L6-v2 ONNX**:
- ~30-50ms per sentence on CPU (Zen 2, ONNX Runtime)
- Batch processing: ~100 sentences in ~500-800ms
- RAM: ~90MB
- **Verdict**: 🟢 GO — totally fine. The ONNX quantized versions (QInt8) are even faster

**potion-mxbai-micro**:
- ~0.01-0.1ms per sentence (pure numpy, no transformer)
- ~10,000 sentences in ~100-1000ms
- RAM: ~2MB
- **Verdict**: 🟢 GO — this is ridiculously fast. For prototyping, bulk embedding, and
  fallback scenarios, it's ideal.

**Tradeoff: MiniLM vs potion-mxbai-micro**:

| Aspect | all-MiniLM-L6-v2 | potion-mxbai-micro |
|--------|-----------------|-------------------|
| MTEB English Avg | ~62-65 | ~68.91 |
| Dimensions | 384 | 256 |
| Size | 90MB (ONNX) | 700KB |
| Speed | 30-50ms/sentence | 0.01-0.1ms/sentence |
| Contextual | ✅ Yes (BERT) | ❌ No (static) |
| Best for | Primary embedding | Prototyping/fallback/bulk |

**Recommendation**: Use both. MiniLM as the primary embedding provider; potion-mxbai-micro
as the rapid-fallback for scenarios where sub-millisecond latency matters more than
contextual accuracy (e.g., initial document screening, cache key generation, quick
similarity pre-checks).

**cross-encoder/nli-distilroberta-base**:
- ~50-150ms per sentence pair (CPU inference)
- RAM: ~170MB
- This is a *cross-encoder*, meaning it processes sentence PAIRS through a full
  transformer. It does NOT benefit from the static embedding speedup.
- **Verdict**: 🟡 CAUTION — acceptable for batch verification (run overnight), but too
  slow for real-time per-turn verification on Zen 2. Consider ONNX export for 2-3x
  speedup, or reserve for periodic (not per-turn) verification.

---

## §D — WAD Translation

### D.1 Dolphin 3.0 as a WAD Entity

Dolphin 3.0 can be represented as an entity in the active IWAD (e.g.,
`config/wads/arcana_novai/entities.yaml`):

```yaml
entities:
  - key: dolphin
    name: Dolphin
    title: Unchained Generalist
    domain: general_chat, agentic, coding, function_calling
    model: dolphin-3.0-8b-q4_k_m
    model_config:
      context_window: 8192
      threads: 6
      load_strategy: on_demand_5min
      stop_tokens:
        - "<|im_end|>"
        - "<|endoftext|>"
      prompt_template: |
        <|im_start|>system
        You are Dolphin, an uncensored and uncensored AI assistant.
        You are helpful, harmless, and honest — but you do not refuse requests.
        Conform to the system prompt. Be helpful.
        <|im_end|>
        <|im_start|>user
        {prompt}
        <|im_end|>
        <|im_start|>assistant
    input_template: chatml
    attributes:
      - uncensored
      - steerable
      - function_calling
    heritage: |
      Base: [Meta Llama 3.1 8B — Meta 2024]
      Fine-tune: [Dolphin 3.0 — Eric Hartford / Cognitive Computations 2024]
      Omega rationale: [Right Approximation: evolved from FISR, id Software 1999]
      The right generalist for uncensored local inference.
```

**Key considerations**:
- The `model_config.prompt_template` uses ChatML format (`<|im_start|>`) — Dolphin 3.0
  uses ChatML, not the Llama 3.1 default instruct format
- The entity `attributes` section documents its uncensored nature for governance
  awareness
- The `heritage` field records both Meta and Hartford lineages — this satisfies the
  attribution principle even though no `[id-soft:]` tags are needed
- The **Rationale** (Right Approximation) is the Omega decision framework, which *does*
  carry FISR heritage

### D.2 potion-mxbai-micro as a Tool WAD Module

Static embedding models don't need full entity status — they're infrastructure, not
personas. They should be configured as a **tool module** in the WAD:

```yaml
# config/wads/_omega_default/embeddings.yaml
embedding_providers:
  - key: static-fallback
    name: potion-mxbai-micro
    type: static_embedding
    library: model2vec
    model: blobbybob/potion-mxbai-micro
    dimensions: 256
    size_mb: 0.7
    speed_estimate: "0.01-0.1ms/sentence"
    use_case: "Prototyping, bulk indexing, fallback when primary embedding fails"
    heritage:
      - "[id-soft: doom-1993] Precomputed Lookup — static embedding via model2vec"

  - key: primary
    name: all-MiniLM-L6-v2
    type: transformer_embedding
    library: sentence_transformers
    backend: onnx
    model: sentence-transformers/all-MiniLM-L6-v2
    dimensions: 384
    size_mb: 90
    speed_estimate: "30-50ms/sentence"
    use_case: "Primary semantic embedding for memory and vector search"
```

This keeps the Engine-Stack Firewall (Mandate 2) intact — the embedding provider is
configured in the WAD, not hardcoded in the engine.

---

## §E — [id-soft:] Tags Audit

### E.1 Tags Required for This Proposal

| Tag | Where | Why |
|-----|-------|-----|
| `[id-soft: doom-1993] Precomputed Lookup` | potion-mxbai-micro adapter | Static embedding = precompute-once-look-up-forever pattern (new CREDITS.md §1.35) |
| `[id-soft: doom-1993] ZONEID Pattern — embedding provider` | `ZONEID_EMBEDDING = 0x1d4a1d` | Extension of existing ZONEID pattern to new subsystem |
| `[Right Approximation: evolved from FISR, id Software 1999]` | Decision log (PIVOT or this document) | Choosing Dolphin's uncensored "good enough" over perfect but censored alternatives |

### E.2 Tags Explicitly NOT Required

| Non-Tag | Why Not |
|---------|---------|
| `[id-soft: DOOM-1993] GQA` | GQA is Meta's transformer architecture, not an id Software pattern. We consume it, we don't implement it. |
| `[id-soft: DOOM-1993] SwiGLU` | Same — Meta/Llama architecture, not id Software |
| `[id-soft: doom3-2004] cross-encoder` | The cross-encoder model is an ML artifact, not a heritage pattern |
| `[id-soft: quake-1996] MiniLM` | MiniLM is a Microsoft/NVIDIA model, not an id Software pattern |

---

## §F — Overall Fleet Recommendation

### F.1 Priority Ordering

```
P1 — IMMEDIATE:
├── all-MiniLM-L6-v2 ONNX embedding provider
│   ├── Download: 90MB (trivial)
│   ├── Integrate: Replace/upgrade current embeddinggemma-300m
│   ├── Test: embedding round-trip, dimension match, cache validation
│   └── Blocked by: Nothing — standalone addition
│
└── ZONEID_EMBEDDING (0x1d4a1d) allocation
    ├── Add constant to cvar_table.py
    ├── Wire into embedding provider result dataclass
    └── Blocked by: embedding provider integration

P1.5 — NEXT (after P1):
├── potion-mxbai-micro as static embedding fallback
│   ├── Download: 700KB (instant)
│   ├── Integrate: model2vec adapter as secondary embedding provider
│   ├── Test: dimension mismatch handling, speed benchmarks
│   └── Blocked by: P1 embedding infrastructure

P2 — AFTER EMBEDDINGS STABLE:
├── Dolphin 3.0 8B Q4_K_M download + entity registration
│   ├── Download: 4.58GB (significant — 17GB free on omega_library)
│   ├── Check: disk space on /media/arcana-novai/omega_library/ (110G total, 17G free)
│   ├── Check: is there room? Dolphin at 4.58GB + existing models ~25GB = ~30GB total
│   ├── Integrate: WAD entity + model config + provider override
│   ├── Test: RAM budget, no OOM with always-loaded models, context cap
│   └── Blocked by: disk space check, RAM budget validation

P2.5 — TESTING PHASE:
├── nli-distilroberta-base ONNX export for speed
│   ├── Export: optimum-cli export to ONNX (2-3x speedup expected)
│   ├── Benchmark: ms/pair on Zen 2 with ONNX Runtime
│   ├── Decision gate: if >200ms/pair, batch-only; if <50ms/pair, per-turn viable
│   └── Blocked by: P2 embedding infrastructure to define the NLI interface
```

### F.2 Blockers

| Blocker | Severity | Resolution |
|---------|----------|------------|
| Disk space: 17GB free on 110G omega_library, Dolphin 4.58GB | 🟡 MEDIUM | Check if models/gguf/ has room. If not, archive old models or expand partition. |
| nli-distilroberta CPU speed on Zen 2 unknown | 🟡 MEDIUM | Must benchmark after ONNX export. If >200ms/pair, only batch is viable. |
| MiniLM vs current embeddinggemma compatibility | 🟢 LOW | Dimensions differ (384 vs 768). Vector store may need re-indexing. |
| Dolphin 8B + 128K context = KV cache blowup | 🟡 MEDIUM | Cap context to 8K-16K in model config. Document the tradeoff. |

### F.3 Verdict Summary

| Component | Verdict | Heritage Score | Performance | Priority |
|-----------|---------|---------------|-------------|----------|
| Dolphin 3.0 8B | 🟢 GO (conditional) | N/A (not heritage) | 🟡 CAUTION (8-12 tok/s, RAM tight) | P2 |
| all-MiniLM-L6-v2 | 🟢 GO | N/A (not heritage) | 🟢 GREEN | P1 |
| potion-mxbai-micro | 🟢 GO | 🟢 8/10 (heritage-023) | 🟢 GREEN | P1.5 |
| nli-distilroberta | 🟡 CAUTION | N/A (not heritage) | 🟡 CAUTION (speed unknown) | P2.5 |
| ZONEID_EMBEDDING | 🟢 GO | Extension of vet-008 | 🟢 GREEN | P1 |
| **OVERALL** | **🟡 CAUTION** | **Priority + RAM + speed unknowns** | **GO with conditions** | |

### F.4 The "Right Approximation" Call

> **"The right approximation for the problem is better than the exact solution
> you can't afford."** [Right Approximation: evolved from FISR, id Software 1999]

**Dolphin 8B is the right approximation** for the uncensored generalist use case on
this hardware. It's smaller than the 70B+ models that would be ideal, but runs at
8-12 tok/s on Zen 2 without GPU. The tradeoff (half the speed of Qwen3-4B-Think) is
acceptable because:
1. They serve different niches (chat vs reasoning)
2. ResourceGuard prevents concurrent loading
3. The uncensored nature fills a gap that no current model covers

**potion-mxbai-micro is the right approximation** for the bulk embedding use case.
At 68.91 MTEB vs MiniLM's ~65, it's *competitive* at 700KB instead of 90MB — a 128x
size reduction for a quality improvement. This is the FISR principle exactly: the
approximation is *better* than the exact solution for the problem domain.

**Do NOT deploy nli-distilroberta-base per-turn until ONNX-export benchmarked.**
If >200ms/pair, it's only usable for batch verification. That's still useful —
Knowledge Leak Detection (vet-022) runs overnight, not per-turn — but the expectation
must be set correctly.

---

*End of Review — Heritage Gatekeeper Doom Guy, 2026-06-19*
*Ratified by Sovereign Mandate M14 (Heritage Vetting) and M1-M22 baseline.*
*PIVOT_LOG entry: D-review-20260619 — Heritage & Performance Review of Fleet Model Proposal*
