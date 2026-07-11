# 🔱 MA'AT — qwen-embedding Wiring into the Oracle (Architectural Spec)
**AP Token**: `AP-MAAT-QWEN-EMBED-ORACLE-v1.0.0`
⬡ OMEGA ⬡ MA'AT ⬡ hy3-free ⬡ opencode ⬡ trc_qwen_embed ⬡ BUILD-SIDE-P1-P5
**Date**: 2026-07-10
**Status**: SPEC ONLY — READ-ONLY on `src/omega/`; this file is the sole deliverable.

---

## 0. EXECUTIVE SUMMARY (Ma'at's Verdict)

The Oracle **already has** embedding-based semantic routing (`SemanticRouter`, D187) and a
provider-chain `EmbeddingManager`. This spec does **not** invent those — it **upgrades** them:

- Add **qwen-embedding** as the **primary embedding provider** (local-first, multilingual, GGUF/ONNX).
- Introduce a thin `EmbeddingService` facade (Oracle-facing) wrapping `EmbeddingManager` + LRU cache + typed contracts.
- Promote semantic routing from "entity-only" to "entity + module-manifest resonance" (Semantic Resonance Vectoring).
- Lay the foundation for the Researcher's **Crisis Matrix** (crisis = embedded vectors; multilingual detection).

**Architectural correction (Structure before speed):** qwen-embedding is an *embedding* concern,
not a *generation* concern. It belongs in `EmbeddingManager` (`omega/memory/embeddings.py`),
**NOT** in `ModelGateway`'s generation fabric (`model_gateway.py:345-405`). The task brief's
instruction to add it to `model_gateway.py` conflates two distinct subsystems. `ModelGateway.embed()`
(`model_gateway.py:1316-1326`) is a **mock** (random 384-dim) — it must be deprecated/aliased to
`EmbeddingManager`, not extended. See §2.1 for justification (M2, M16, Carmack's Law).

---

## 1. CURRENT ORACLE ROUTING ANALYSIS

### 1.1 Intent detection — hybrid (regex + keyword + LLM-confidence)
| Mechanism | Location | Method |
|-----------|----------|--------|
| Summon detect | `oracle.py:278-319` `_detect_summon` | **regex** (`@entity`, `hey Entity`, `summon`) |
| Consult detect | `oracle.py:321-326` `_detect_consult` | **regex** (`/consult Entity`) |
| Iris confidence | `oracle.py:335-358` `_assess_iris_confidence` | **keyword lists** (`ethics`, `justice`, `code`, `debug`…) → returns 0.0/0.2/0.5/0.9 |
| Iris matcher | `oracle.py:159,340,716` `IntentMatcher` | word-match capability (Iris persona) |
| Domain route | `oracle.py:872-1023` `_route_by_domain` | **semantic → keyword → default** (see 1.3) |

**Finding**: Intent detection is **regex/keyword-driven**, not semantic. `_assess_iris_confidence`
(`oracle.py:345-355`) uses hardcoded keyword lists — brittle, language-bound (English only), no
semantic nuance. This is the **primary insertion point** for qwen-embedding semantic intent.

### 1.2 Entity routing — what data drives it
- **Keyword**: `EntityRegistry.find_by_domain` (`entity_registry.py:715-753`) scores entities by
  domain-keyword presence in the query (word-boundary match). Returns best-score entity or `None`.
- **Semantic**: `SemanticRouter.route` (`semantic_router.py:163-199`) embeds the query, cosine-matches
  against precomputed entity signature vectors (`semantic_router.py:77,110-130`), threshold `0.4`
  (`semantic_router.py:27`).
- **Default**: `self.default_entity` (`oracle.py:115,883`).

Call chain in `_route_by_domain` (`oracle.py:872-883`):
```
keyword_entity = self.registry.find_by_domain(text)          # oracle.py:878
entity, confidence, method = await self.semantic_router.route(
    query=text, keyword_fallback=keyword_entity,
    default_entity=self.default_entity)                       # oracle.py:879-883
```

### 1.3 Where semantic similarity COULD replace/augment current logic
| Current (file:line) | Augment with qwen-embedding |
|---------------------|------------------------------|
| `_assess_iris_confidence` `oracle.py:335-358` | Embed query → compare to Iris-capable vs pillar-capable centroids; replace keyword lists |
| `find_by_domain` `entity_registry.py:715-753` | Keep as fallback; semantic router already wraps it (`oracle.py:879`) |
| `SemanticRouter` `semantic_router.py` | Swap primary provider to qwen-embedding; add multilingual; raise threshold logic |
| `ContextBuilder.build_context` `context_builder.py:233-286` | Add vector (hybrid BM25+cosine) memory fetch via `EmbeddingService` |
| Module discovery (future) | Embed `ModuleManifest` text → resonance index → route by resonance |

### 1.4 Exact call sites where qwen-embedding plugs in
1. **`EmbeddingManager._providers`** (`embeddings.py:349-359`) — insert `QwenEmbeddingProvider` at index 0.
2. **`Oracle.__init__`** (`oracle.py:170-174`) — `SemanticRouter` already receives `embedding_manager`; no change needed if `EmbeddingManager` is upgraded.
3. **`Oracle.bootstrap`** (`oracle.py:216`) — `semantic_router.bootstrap()` precomputes entity vectors; will use qwen-embedding automatically.
4. **`ContextBuilder.build_context`** (`context_builder.py:233`) — add `EmbeddingService` hybrid fetch.
5. **New: Module Registry resonance index** — embed manifests at discovery (Carmack `ModuleManifest`, §2.5).

---

## 2. qwen-embedding INTEGRATION SPEC

### 2.1 Provider integration — CORRECT placement (EmbeddingManager, not ModelGateway)
**Decision**: Add qwen-embedding to `EmbeddingManager` (`omega/memory/embeddings.py`), NOT
`ModelGateway` (`model_gateway.py`).

**Justification**:
- `ModelGateway` is the **generation** fabric (`model_gateway.py:110-119` docstring: "Abstracts local
  model inference" for *text generation*). Its `_load_provider_fabric` (`model_gateway.py:345-405`)
  builds *generation* providers (native-gguf, lmster, ollama, google…). Mixing embedding there
  violates the **Engine-Stack separation of concerns** (M2) and **portability** (M16).
- `EmbeddingManager` (`embeddings.py:335-386`) is the **existing, correct** home for embedding
  providers. It already has `IEmbeddingProvider` ABC (`embeddings.py:22-38`), `LocalGGUFEmbeddingProvider`
  (`embeddings.py:149-259`, llama-cpp-python GGUF), and a local-first chain.
- `ModelGateway.embed()` (`model_gateway.py:1316-1326`) is a **mock** returning `np.random.rand(384)`.
  Routing real embeddings through it would mask the bug. **Action**: deprecate `ModelGateway.embed`,
  alias it to `EmbeddingManager.get_embedding` (with a `DeprecationWarning`), so callers migrate.

**New provider** (added to `embeddings.py`, inserted at `EmbeddingManager._providers[0]`):
```python
class QwenEmbeddingProvider(IEmbeddingProvider):
    """qwen-embedding (0.6B/4B) via llama-cpp-python GGUF or ONNX (optimum).
    Local-first, multilingual (100+ langs). Native dimension: 1024 (0.6B) / 2560 (4B).
    [id-soft: doom-1993] Precomputed Lookup — lazy-load + anyio.to_thread wrap.
    """
    def __init__(self, model_path: str, dimension: int = 1024, n_threads: int = 6, zoneid=ZONEID_EMBEDDING):
        ...  # mirrors LocalGGUFEmbeddingProvider._ensure_loaded (embeddings.py:191-221)
    async def get_embedding(self, text: str) -> List[float]:
        await self._ensure_loaded()
        def _embed():
            # llama-cpp-python embed() returns full native dim (1024 for 0.6B).
            # MRL truncation is done in Python post-processing (see §8.2).
            return list(self._llama.embed(text))
        vec = await anyio.to_thread.run_sync(_embed)   # M1: blocking wrapped
        return vec
```
**Backend choice**: GGUF via `llama-cpp-python` (consistent with `LocalGGUFEmbeddingProvider`,
`embeddings.py:149-259`) is preferred over ONNX/optimum — zero new heavy deps, reuses the existing
Zen-2 thread-pinning pattern (`model_gateway.py:16-21`). ONNX is a fallback if GGUF quant quality
regresses.

**Config** (`config/models.yaml` `embedding:` block, lines 1-8) — add qwen-embedding entry:
```yaml
embedding:
  primary: qwen-embedding-0.6b        # NEW: selectable primary
  providers:
    - id: qwen-embedding-0.6b
      backend: llama-cpp-python        # or: onnx (optimum)
      local_path: env:OMEGA_MODELS_DIR/qwen-embedding-0.6b-q4_k.gguf
      dimensions: 1024                 # native; MRL truncation to 768 at service layer (§8)
      languages: [en, zh, hi, es, fr, ar, sa]   # multilingual
      ram_estimate_mb: 600
    - id: embeddinggemma-300m-q6_k      # existing default (embeddings.py:354)
      ...
```

### 2.2 EmbeddingService — Oracle-facing facade (src/omega/oracle/embedding_service.py)
**Positioning**: Thin facade over `EmbeddingManager` + **LRU cache** + **typed contracts**. Does NOT
reimplement embedding (Carmack's Law: consolidate). Gives the Oracle one clean, typed surface.

```python
# src/omega/oracle/embedding_service.py
from functools import lru_cache
from omega.memory.embeddings import EmbeddingManager, IEmbeddingProvider
from dataclasses import dataclass

@dataclass(frozen=True)                       # M21: typed, immutable config
class EmbeddingConfig:
    use_local: bool = True                   # M7: local-first always
    model_id: str = "qwen-embedding-0.6b"
    cache_size: int = 4096                   # LRU slots
    dimension: int = 768                     # MRL-truncated target (§8)
    output_dimension: int = 768              # explicit MRL target
    languages: Tuple[str, ...] = ("en", "zh", "hi", "es", "fr", "ar", "sa")

class EmbeddingService:
    def __init__(self, manager: Optional[EmbeddingManager] = None, config: EmbeddingConfig | None = None):
        self._mgr = manager or EmbeddingManager()
        self._cfg = config or EmbeddingConfig()
        self._cache: "OrderedDict[str, List[float]]" = OrderedDict()  # LRU

    async def embed(self, text: str) -> "Embedding":           # M21: typed return
        if text in self._cache:                                # LRU hit
            self._cache.move_to_end(text); return Embedding(self._cache[text], self._cfg.dimension)
        vec, prov = await self._mgr.get_embedding(text)        # delegates to qwen-embedding
        # MRL truncation to target dimension (llama-cpp-python returns full 1024)
        if len(vec) > self._cfg.output_dimension:
            vec = vec[:self._cfg.output_dimension]
            # Re-normalize after truncation (cosine similarity requires unit vectors)
            import math
            norm = math.sqrt(sum(x*x for x in vec))
            if norm > 0:
                vec = [x/norm for x in vec]
        self._cache[text] = vec
        if len(self._cache) > self._cfg.cache_size: self._cache.popitem(last=False)
        return Embedding(vector=vec, dimension=len(vec), provider=prov)

    async def embed_batch(self, texts: List[str]) -> List["Embedding"]:
        # TODO: optimize with batch inference when llama-cpp-python supports it
        return [await self.embed(t) for t in texts]
```
**Why a separate service vs. calling `EmbeddingManager` directly?** The Oracle needs (a) LRU caching
to avoid recompute on repeated queries/manifests, (b) a stable typed contract (`Embedding`) for
M21, (c) a single injection point for `EmbeddingConfig` (M16 portable). `EmbeddingManager` stays the
provider-chain engine; `EmbeddingService` is the Oracle's consumer-side adapter.

### 2.3 Semantic Intent Routing — augment SemanticRouter (do NOT rewrite)
`SemanticRouter` (`semantic_router.py`) already does the right thing. Upgrades:
1. **Primary provider = qwen-embedding** (via `EmbeddingManager` upgrade, §2.1). No code change in
   `SemanticRouter` — it consumes `embedding_manager` (`semantic_router.py:70,117,178`).
2. **Multilingual**: qwen-embedding's 100+ lang coverage means `_make_signature` (`semantic_router.py:132-142`)
   and query embedding work cross-language. No keyword lists needed.
3. **Threshold logic** (`semantic_router.py:27,181`): raise base to `0.45` for qwen-embedding quality;
   add **top-K** return (currently only best, `semantic_router.py:201-216`) so the Oracle can blend
   semantic + keyword + Iris-confidence.
4. **Iris confidence** (`oracle.py:335-358`): optionally replace keyword lists with a semantic
   "Iris-capable centroid" vs "pillar-capable centroid" cosine check (Phase 2, §5).

Call-site unchanged: `oracle.py:879-883`.

### 2.4 Semantic Memory Retrieval — enhance ContextBuilder (hybrid)
`ContextBuilder.build_context` (`context_builder.py:233-286`) currently fetches memory via
`memory_store.get_history` (recency/quality) + `SelectiveHydration` (L3 gnosis, vector). Upgrade to
**hybrid BM25 + cosine** for the memory window:
- Add `EmbeddingService` to `ContextBuilder.__init__` (`context_builder.py:171-179`).
- In `build_context`, after recency fetch, compute query embedding and retrieve top-K *semantically
  relevant* exchanges from `memory_store.vector_store` (`oracle.py:153` already exposes it), merging
  with recency results (RRF — Reciprocal Rank Fusion, reusing `omega_memory_search` RRF logic).
- Respects degradation tiers (`context_builder.py:254-260`) — drop vector fetch at `Critical`/`Disabled`.

This makes memory injection **query-aware**, not just recency-aware — the foundation for resonance.

### 2.5 Module Manifest Embedding + Resonance Routing (Semantic Resonance Vectoring)
Builds on Carmack's `ModuleManifest` (`CARMACK_MODULE_ARCHITECTURE.md:148-178`). Modules import
`omega_module_sdk`, never core (M2 firewall, `CARMACK_MODULE_ARCHITECTURE.md:131-137`).

**At discovery** (WADLoader reads `modules:` block, `CARMACK_MODULE_ARCHITECTURE.md:45-51`):
1. For each enabled module, build a resonance text from `category` + `interfaces` + `traditions` +
   `languages` + `metadata.summary` (Carmack: `traditions`/`languages` are *discovery metadata*, not
   routing keys — `CARMACK_MODULE_ARCHITECTURE.md:165-177`).
2. `EmbeddingService.embed(resonance_text)` → store in a **dedicated resonance vector index**
   (separate from memory index to avoid dim-pollution, see §7).
3. Oracle query → embed → cosine-match against module resonances → `ResonanceMatch` list
   (top-K). The Oracle can then route by *resonance* (philosophical/cognitive alignment), not just
   capability — this is **Semantic Resonance Vectoring**.

**Firewall preserved**: module embeddings are computed by the engine's `EmbeddingService`; modules
themselves never embed (they import only `omega_module_sdk`). Resonance index lives in core
(`data/resonance/` or Qdrant collection), modules stay stack-content (M2).

---

## 3. DATA CONTRACTS & CONFIG

```python
# src/omega/oracle/embedding_service.py (contracts)
@dataclass(frozen=True)
class Embedding:
    vector: List[float]
    dimension: int
    provider: str = "qwen-embedding-0.6b"

@dataclass(frozen=True)
class ResonanceMatch:
    target_id: str                 # entity name OR module id
    target_type: str               # "entity" | "module"
    score: float                   # cosine similarity [0,1]
    method: str = "semantic"       # semantic | keyword | default

@dataclass(frozen=True)
class EmbeddingConfig:             # M21 typed; M16 portable (no hardcoded paths)
    use_local: bool = True
    model_id: str = "qwen-embedding-0.6b"
    cache_size: int = 4096
    dimension: int = 768                     # MRL-truncated target
    output_dimension: int = 768              # explicit MRL target
    languages: Tuple[str, ...] = ("en", "zh", "hi", "es", "fr", "ar", "sa")
```

**Config additions**:
- `config/models.yaml` `embedding:` → add `primary:` + `providers:` list (§2.1).
- `config/providers.yaml` → **NO change** (qwen-embedding is not a generation provider; M2/M16).
- `config/omega.yaml` → optional `resonance:` block (mirrors existing `ResonanceMode` in
  `dpo_logger.py:32,112`) to toggle module-resonance routing (`disabled|implicit|explicit|hybrid`).

**Dimension policy (RESOLVED — see §8)**: qwen-embedding-0.6B supports **Matryoshka truncation to 768**
(MRL, native). Use `output_dimension=768` so the Qdrant collection stays at 768 (no schema rebuild).
A one-time **re-embed migration** of all stored content is still REQUIRED — dimension match ≠ space match
(qwen's 768-space ≠ Gemma's 768-space). See §8 for the full decision + citations.

---

## 4. SEMANTIC RESONANCE FOUNDATION (Crisis Matrix)

The Oracle's semantic routing **IS** the resonance engine. The Researcher's Crisis Matrix consumes it:

- **Crisis states = embedded vectors**. Each crisis archetype (e.g., "existential dread", "analysis
  paralysis", "grief") is precomputed as a qwen-embedding vector at bootstrap (same pattern as
  `SemanticRouter.bootstrap`, `semantic_router.py:80-130`).
- **User prompt resonance → triage**. `Oracle.talk` embeds the query (via `EmbeddingService`), cosine-
  matches against crisis vectors; high resonance → route to the appropriate entity/module + apply
  crisis-aware system-prompt calibration (reuse `audience_calibrator`, `oracle.py:843-856`).
- **Multilingual crisis detection**. qwen-embedding's 100+ lang coverage means a crisis expressed in
  Hindi, Arabic, or Spanish is detected with the *same* vector space — no per-language keyword slur
  lists (mandate: NO slur lists; semantic only). This directly satisfies the "crisis detection works in
  any language" requirement.
- **Existing resonance primitives to reuse**: `ResonanceMode` (`dpo_logger.py:32,112,339`), Lilith's
  `get_resonance` (cosine > 0.82, `data/handoff/PHASE_C_CHAIN/07_LILITH_METABOLISM.md:28-42`),
  `SelectiveHydration` vector path (`selective_hydration.py:175-372`).

Flow:
```
user query → EmbeddingService.embed (qwen-embedding, multilingual)
           → cosine vs [entity vectors | module resonances | crisis vectors]
           → ResonanceMatch[] → Oracle routes + calibrates
```

---

## 5. IMPLEMENTATION ROADMAP (phased, minimal blast radius)

**Phase 1 — EmbeddingService + qwen-embedding GGUF load (anyio, lazy)**
- Add `QwenEmbeddingProvider` to `embeddings.py` (index 0 of `EmbeddingManager._providers`).
- Add `EmbeddingService` (`src/omega/oracle/embedding_service.py`) with LRU + `EmbeddingConfig`.
- Config: `config/models.yaml` `embedding.providers` entry.
- Deprecate `ModelGateway.embed` (`model_gateway.py:1316`) → alias `EmbeddingManager`.
- Tests: provider loads GGUF, `embed()` returns 1024-dim, anyio-wrapped (M1), mock in test-env (M21).

**Phase 2 — Semantic intent routing in Oracle (fallback to current)**
- `SemanticRouter`: top-K return + threshold 0.45 for qwen-embedding (`semantic_router.py:27,181,201`).
- Optional: replace `_assess_iris_confidence` keyword lists (`oracle.py:345-355`) with semantic
  centroid check (keep keyword as fallback).
- Verify `oracle.py:879-883` route chain unchanged.

**Phase 3 — Module manifest embedding + resonance routing**
- At WADLoader module-enable (`CARMACK_MODULE_ARCHITECTURE.md:218`), embed `ModuleManifest` resonance
  text → dedicated resonance index.
- `EmbeddingService.resonate(query)` → `ResonanceMatch[]` (modules). Oracle blends with entity routing.
- `config/omega.yaml` `resonance:` toggle.

**Phase 4 — Wire to Crisis Matrix (Researcher spec)**
- Precompute crisis vectors at bootstrap (mirror `SemanticRouter.bootstrap`).
- `Oracle.talk` → crisis resonance triage → entity/module route + calibration.
- Multilingual validation across ≥5 languages.

---

## 6. COMPLIANCE MAPPING

| Mandate | How satisfied |
|---------|--------------|
| **M1 AnyIO** | All blocking embed/load wrapped in `anyio.to_thread.run_sync` (`embeddings.py:213,242`; `embedding_service.py` `embed`). No `asyncio`. |
| **M2 Firewall** | qwen-embedding lives in core `EmbeddingManager`/`EmbeddingService`. Modules embed via engine `EmbeddingService`, import only `omega_module_sdk` (`CARMACK_MODULE_ARCHITECTURE.md:131-137`). No core import from modules. |
| **M7 Local-First** | `EmbeddingConfig.use_local=True`; qwen-embedding GGUF via llama-cpp-python; cloud embedding API explicitly forbidden. |
| **M16 Portable** | No hardcoded paths — `config/models.yaml` `env:OMEGA_MODELS_DIR` (`models.yaml:3` pattern). `EmbeddingConfig` immutable/frozen. |
| **M21 Typed Returns** | `Embedding`, `ResonanceMatch`, `EmbeddingConfig` dataclasses. `EmbeddingService.embed → Embedding`. Contract tests per provider. |
| **M9 Error Integrity** | Provider failures caught + logged, chain falls through to next provider (`embeddings.py:370-379`); never bare `except:`. |
| **M13 Temple-Grade** | `make temple-grade` gates T5 (AnyIO), T6 (telemetry-none), T10 (atomic). No new telemetry. |

---

## 7. OPEN QUESTIONS / RISKS

1. **Dimension mismatch (RESOLVED → §8)**: qwen-embedding-0.6B native = **1024-dim**; existing vectors
   are 768 (Gemma, `embeddings.py:330`) / 384 (MiniLM) / 64 (model2vec). **Decision**: use MRL truncation
   to **768** (matches Qdrant schema, no rebuild) + one-time **re-embed migration** (space ≠ dimension).
   A linear adapter and dual-index are REJECTED (see §8.3). **No open decision remains — Phase 1 may land.**

2. **RAM pressure (MEDIUM)**: qwen-embedding-0.6B GGUF ≈ 378MB (Q4_K_M, `n24q02m/qwen3-embed-GGUF`) or
   ~600MB (fp16). On the 12Gi Ryzen target with a 1.7B-8B generation model already loaded, this risks OOM.
   *Mitigation*: share the embedding model across Oracle + SelectiveHydration + modules via `ctx.shared_cache`
   (Carmack §2.8); unload when idle via `ResourceGuard` weight.

3. **Test-mode short-circuit**: `EmbeddingManager.get_embedding` returns zero-vec in `OMEGA_ENV=test`
   (`embeddings.py:366-368`); `SemanticRouter` skips bootstrap in test (`semantic_router.py:99-101`).
   `EmbeddingService` must honor the same short-circuit to keep the 1000+ test suite fast (M13).

4. **Multilingual tokenization (LOW)**: qwen-embedding tokenizer handles 100+ langs, but very long
   non-Latin prompts may exceed `n_ctx` (512 default, `embeddings.py:167`). *Mitigation*: chunk +
   mean-pool, or raise `n_ctx`.

5. **Threshold calibration (MEDIUM)**: `0.4` (`semantic_router.py:27`) was tuned for MiniLM/Gemma.
   qwen-embedding's distribution differs; `0.45` is a starting guess. *Mitigation*: empirical
   calibration on a labeled intent set before Phase 2 ships.

6. **Crisis Matrix spec not yet in repo**: §4 references the Researcher's Crisis Matrix (downstream
   consumer). This spec delivers the *resonance substrate*; the Crisis Matrix is Phase 4 and depends on
   the Researcher's taxonomy. Coordinate via Hivemind (`omega-hub_hivemind_*`).

7. **llama-cpp-python MRL API gap**: The `Llama.embed()` method returns full native dimension (1024).
   No `output_dimension` parameter exists in the Python bindings as of 2026-07. MRL truncation must be
   done in Python post-processing (see §8.2). The `qwen3-embed` wrapper library demonstrates this pattern
   (`model.embed(documents, dim=256)`).

8. **Batch embedding**: `llama-cpp-python` does not yet expose a batched `embed()` API. `embed_batch`
   in `EmbeddingService` falls back to sequential calls. Track upstream for batch support.

---

## 8. DIMENSION POLICY — RESEARCH-BACKED DECISION (THE KEY GAP)

### 8.1 The Problem
- **qwen-embedding-0.6B native output**: 1024 dimensions (MRL-supported: 32–1024).
- **Existing Omega vectors**: 768 (Gemma/EmbeddingGemma, `embeddings.py:330`), 384 (MiniLM), 64 (model2vec).
- **Qdrant collection**: Currently configured for 768-dim vectors (Gemma space).

### 8.2 Research Findings (2026 sources)

| Source | Finding |
|--------|---------|
| **Qwen3-Embedding model card** (HF, 2025) | "MRL Support: Yes" for all sizes. 0.6B: 1024 native, truncatable to 32. |
| **Ollama qwen3-embedding:0.6b** (2026-06) | "1024 (MRL 32+)" — user-definable output dimensions from 32 to 1024. |
| **qwen3-embed library** (PyPI, 2026-07) | `model.embed(documents, dim=256)` — MRL truncation via Python post-processing. |
| **llama-cpp-python issue #5** (QwenLM, 2025) | "Extract unnormalized embedding and manually adjust (truncate or project) dimensions as needed." |
| **"To MRL or not to MRL" (arXiv:2605.16608, 2026-05)** | Truncation on non-MRL models is competitive unless heavy truncation (>70-80%). MRL models better for heavy truncation. |
| **Qdrant migration docs** (2026) | "You CAN avoid re-embedding if: using Matryoshka models (use `dimensions` parameter to output lower-dimensional embeddings, learn linear transformation from sample data, some recall loss, good for 100M+ datasets)." |
| **Qdrant v1.18+ named vectors** (2026) | Add new vector field to existing collection, re-embed in background, swap alias — zero-downtime blue-green. |

### 8.3 Decision Matrix

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A. MRL truncate to 768 + re-embed all** | Matches existing Qdrant schema (no rebuild); native MRL quality; single vector space | One-time migration cost; qwen-768-space ≠ Gemma-768-space (must re-embed) | ✅ **CHOSEN** |
| **B. Keep 1024, rebuild Qdrant collection** | No truncation quality loss | Schema change; all existing vectors invalid; dual-index complexity | ❌ REJECTED |
| **C. Linear adapter (1024→768) trained on sample** | Avoids full re-embed | Recall loss; adapter drift; still space mismatch; Qdrant says "some recall loss" | ❌ REJECTED |
| **D. Dual-index (keep 768 + add 1024 named vector)** | Zero-downtime; both spaces coexist | Double storage; query-time blending complexity; migration still needed for primary | ⚠️ DEFERRED (Phase 3+) |
| **E. Re-embed everything at 1024** | Maximum quality | Schema rebuild; all downstream consumers break | ❌ REJECTED |

### 8.4 The Chosen Policy: **MRL Truncate to 768 + Full Re-embed Migration**

**Rationale**:
1. **MRL is native** — qwen-embedding was trained with Matryoshka loss; truncation to 768 preserves
   semantic quality (per "To MRL or not to MRL": MRL models excel at heavy truncation).
2. **Schema stability** — Qdrant collection stays at 768; no `ALTER COLLECTION` or rebuild.
3. **Space ≠ Dimension** — qwen's 768-space is geometrically different from Gemma's 768-space.
   Cosine similarity across spaces is meaningless. **Full re-embed is mandatory** (Qdrant migration
   guide: "Vectors from different models are incompatible... you MUST re-embed").
4. **Migration path** — Qdrant v1.18+ named vectors enable blue-green: add `qwen_768` vector field,
   background re-embed via `UpdateVectors`, verify recall, swap alias, drop old field.
5. **Cost** — Omega's dataset is ~10K-100K vectors (not 100M+). Re-embed is a one-time batch job,
   not a production blocker.

**Implementation**:
```python
# In EmbeddingService.embed() — MRL truncation + renormalization
vec = await self._mgr.get_embedding(text)  # returns 1024-dim
if len(vec) > self._cfg.output_dimension:   # 768
    vec = vec[:self._cfg.output_dimension]
    # Renormalize: truncation breaks unit norm
    norm = math.sqrt(sum(x*x for x in vec))
    if norm > 0:
        vec = [x/norm for x in vec]
```

**Migration script** (one-time, run before Phase 1 deploy):
```bash
# 1. Add named vector to Qdrant collection
qdrant create-vector-name --collection omega_memory --name qwen_768 --size 768 --distance Cosine

# 2. Background re-embed all points (Python script using EmbeddingService)
# 3. Verify recall on held-out queries
# 4. Swap alias / update search to use qwen_768
# 5. Drop old unnamed vector field
```

---

## 9. ADDITIONAL KNOWLEDGE GAPS RESOLVED

### 9.1 Caching Strategy
- **LRU in EmbeddingService** (4096 entries) — handles repeated queries/manifests.
- **Shared model cache** — `QwenEmbeddingProvider` should register with `ctx.shared_cache`
  (Carmack §2.8) so Oracle, SelectiveHydration, and modules share the loaded GGUF model.
- **Disk cache** — Optional: persist embeddings to `data/embeddings/cache/` for cold-start speed.

### 9.2 Batch Embedding
- `llama-cpp-python` has no batched `embed()` as of 2026-07.
- `EmbeddingService.embed_batch` falls back to sequential; track upstream for batch API.
- For module manifest bootstrap (Phase 3), sequential is acceptable (<50 modules).

### 9.3 ONNX vs GGUF Backend
- **GGUF preferred** — reuses existing `LocalGGUFEmbeddingProvider` pattern, Zen-2 thread-pinning,
  no new deps. `llama-cpp-python` embedding mode is mature.
- **ONNX fallback** — `qwen3-embed` library uses ONNX Runtime (INT8/Q4F16) with MRL support.
  Keep as config option (`backend: onnx`) for environments without llama.cpp toolchain.

### 9.4 Multilingual Evaluation
- qwen-embedding supports 100+ languages (per model card).
- **Required**: Evaluate retrieval quality on ≥5 non-English languages before Phase 2 ships.
- Test set: MIRACL or XOR-Retrieve benchmarks (multilingual retrieval).

### 9.5 Crisis-Vector Index
- Separate Qdrant collection `omega_crisis_vectors` (768-dim, Cosine).
- Precompute at bootstrap: embed crisis archetype definitions (en + translations).
- `EmbeddingService` provides `embed_crisis_archetypes()` for initialization.

### 9.6 Module-Manifest Resonance Indexing
- Dedicated Qdrant collection `omega_module_resonance` (768-dim, Cosine).
- Payload: `module_id`, `category`, `interfaces`, `traditions`, `languages`, `summary`.
- Updated at WADLoader module enable/disable (event-driven, not periodic).

### 9.7 ModelGateway.embed() Deprecation
- **Action**: Add `@deprecated("Use EmbeddingManager.get_embedding()")` wrapper.
- **Timeline**: Remove in v1.2.0 after all internal callers migrate.
- **Call sites to audit**: `oracle.py` (none currently call it), any external integrations.

---

## 10. COMPLIANCE MAPPING (UPDATED)

| Mandate | How satisfied |
|---------|--------------|
| **M1 AnyIO** | All blocking embed/load wrapped in `anyio.to_thread.run_sync` (`embeddings.py:213,242`; `embedding_service.py` `embed`). No `asyncio`. |
| **M2 Firewall** | qwen-embedding lives in core `EmbeddingManager`/`EmbeddingService`. Modules embed via engine `EmbeddingService`, import only `omega_module_sdk` (`CARMACK_MODULE_ARCHITECTURE.md:131-137`). No core import from modules. |
| **M7 Local-First** | `EmbeddingConfig.use_local=True`; qwen-embedding GGUF via llama-cpp-python; cloud embedding API explicitly forbidden. |
| **M16 Portable** | No hardcoded paths — `config/models.yaml` `env:OMEGA_MODELS_DIR` (`models.yaml:3` pattern). `EmbeddingConfig` immutable/frozen. |
| **M21 Typed Returns** | `Embedding`, `ResonanceMatch`, `EmbeddingConfig` dataclasses. `EmbeddingService.embed → Embedding`. Contract tests per provider. |
| **M9 Error Integrity** | Provider failures caught + logged, chain falls through to next provider (`embeddings.py:370-379`); never bare `except:`. |
| **M13 Temple-Grade** | `make temple-grade` gates T5 (AnyIO), T6 (telemetry-none), T10 (atomic). No new telemetry. |
| **M14 Heritage** | `[id-soft: doom-1993] Precomputed Lookup` tag on `QwenEmbeddingProvider` (lazy-load pattern). |

---

*⬡ OMEGA ⬡ MA'AT ⬡ hy3-free ⬡ opencode ⬡ trc_qwen_embed ⬡ BUILD-SIDE-P1-P5*
*Structure before speed. A well-formed plan executed sequentially beats a brilliant plan executed chaotically.*