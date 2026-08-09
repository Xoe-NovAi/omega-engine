---
account: arcana.novai@gmail.com
pack_version: 2026-08-08
pack_profile: sovereign-audit
pack_files: 32
pack_tokens: 173464
session_date: 2026-08-08
session_type: implementation
---

# Implementation: Un-overengineering Fixes

## 1. `fetch_and_fuse()` — Consolidated FTS+Vector Fusion Helper

**New code — add to `src/omega/memory/hybrid_search.py`** (bottom of file, after `HybridSearchEngine`):

```python
# ── Consolidated Fetch-and-Fuse Helper ──────────────────────────────────
# Eliminates duplicated "fetch FTS + fetch vec concurrently, wrap into
# FTSResult/VecResult, fuse" boilerplate previously copy-pasted in
# MemoryStore.search() and SQLiteVecAdapter.hybrid_search().

from typing import Awaitable, Callable

async def fetch_and_fuse(
    *,
    fts_fetch: Callable[[], Awaitable[List[Dict[str, Any]]]],
    vec_fetch: Callable[[], Awaitable[List[Tuple[float, Dict[str, Any]]]]],
    limit: int = 20,
    fts_weight: float = 1.0,
    vec_weight: float = 1.0,
    k: int = HybridSearchEngine.DEFAULT_K,
    doc_id_fn: Optional[Callable[[Dict[str, Any]], str]] = None,
) -> List[HybridSearchResult]:
    """Fetch FTS + vector results concurrently and fuse via RRF.

    Single call site for the fetch-wrap-fuse pattern duplicated across
    MemoryStore.search() and SQLiteVecAdapter.hybrid_search(). Callers
    supply the two fetch coroutines (already scoped to their own query,
    entity_name, embedding provider, etc.) — this function owns only the
    concurrency and fusion mechanics.

    Args:
        fts_fetch: Zero-arg async callable returning raw FTS result dicts.
        vec_fetch: Zero-arg async callable returning (score, metadata) tuples.
        limit: Max fused results to return.
        fts_weight / vec_weight: RRF source weights.
        k: RRF constant (default 60, Cormack et al. 2009).
        doc_id_fn: Optional custom doc_id extractor. Defaults to
            "{session_id}:{timestamp}" composite key.

    Returns:
        List[HybridSearchResult], sorted by fused_score descending.
    """
    fts_results: List[Dict[str, Any]] = []
    vec_results: List[Tuple[float, Dict[str, Any]]] = []

    async def _run_fts():
        nonlocal fts_results
        fts_results = await fts_fetch()

    async def _run_vec():
        nonlocal vec_results
        vec_results = await vec_fetch()

    # [M1 AnyIO] Structured concurrency — both fetches run in parallel,
    # task group guarantees both complete (or both are cancelled) before
    # fusion proceeds.
    async with anyio.create_task_group() as tg:
        tg.start_soon(_run_fts)
        tg.start_soon(_run_vec)

    def _doc_id(meta: Dict[str, Any]) -> str:
        if doc_id_fn is not None:
            return doc_id_fn(meta)
        return f"{meta.get('session_id', '')}:{meta.get('timestamp', '')}"

    fts_objects = [
        FTSResult(doc_id=_doc_id(r), rank=i + 1, metadata=r)
        for i, r in enumerate(fts_results)
    ]
    vec_objects = [
        VecResult(doc_id=_doc_id(meta), rank=i + 1, score=score, metadata=meta)
        for i, (score, meta) in enumerate(vec_results)
    ]

    engine = get_hybrid_search_engine(k=k)
    return engine.fuse(
        fts_objects, vec_objects,
        fts_weight=fts_weight, vec_weight=vec_weight, limit=limit,
    )
```

Add `import anyio` to the top of `hybrid_search.py` (it currently has no `anyio` import).

**Call site 1 — `src/omega/memory_store.py`, replace `MemoryStore.search()`:**

```python
async def search(
    self,
    query: str,
    entity_name: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Hybrid search: FTS5 + Vector, re-ranked via RRF.

    [C3: entity_name REQUIRED] for sovereign isolation.
    """
    if not query.strip():
        return []

    from .memory.hybrid_search import fetch_and_fuse

    async def _fts_fetch() -> List[Dict[str, Any]]:
        return await self.search_fts(query, entity_name, limit * 2)

    async def _vec_fetch() -> List[Tuple[float, Dict[str, Any]]]:
        vector_adapter = await self._ensure_vector_store()
        if not vector_adapter:
            return []
        embedding, _ = await self.embedding_manager.get_embedding(query)
        return await vector_adapter.query(
            entity_name=entity_name, vector=embedding, limit=limit * 2
        )

    fused = await fetch_and_fuse(
        fts_fetch=_fts_fetch, vec_fetch=_vec_fetch, limit=limit,
    )

    final_results = []
    for result in fused:
        doc_copy = result.metadata.copy()
        doc_copy["_rrf_score"] = result.fused_score
        final_results.append(doc_copy)
    return final_results
```

**Call site 2 — `src/omega/memory/sqlite_vec_adapter.py`, replace `SQLiteVecAdapter.hybrid_search()`:**

```python
async def hybrid_search(
    self,
    query: str,
    entity_name: str,
    vector: List[float],
    limit: int = 20,
    fts_weight: float = 0.5,
    vec_weight: float = 0.5,
) -> List[Dict[str, Any]]:
    """Hybrid search combining FTS5 and vec0 with Reciprocal Rank Fusion."""
    await self._ensure_initialized()

    if not query.strip() and not vector:
        return []

    from .hybrid_search import fetch_and_fuse

    async def _fts_fetch() -> List[Dict[str, Any]]:
        if not query.strip():
            return []

        def _sync_fts():
            conn = self._get_conn()
            cursor = conn.execute("""
                SELECT rowid, session_id, role, content, timestamp
                FROM omega_memory_fts
                WHERE omega_memory_fts MATCH ? AND entity_name = ?
                ORDER BY rank
                LIMIT ?
            """, (query, entity_name, limit * 2))
            return [
                {
                    "rowid": row[0], "entity_name": entity_name,
                    "session_id": row[1], "role": row[2],
                    "content": row[3], "timestamp": row[4],
                }
                for row in cursor.fetchall()
            ]

        try:
            return await anyio.to_thread.run_sync(_sync_fts)
        except (sqlite3.Error, OSError) as e:
            logger.warning("FTS search failed: %s", e)
            return []

    async def _vec_fetch() -> List[Tuple[float, Dict[str, Any]]]:
        if not vector:
            return []
        try:
            return await self.query(entity_name=entity_name, vector=vector, limit=limit * 2)
        except (ProviderError, RuntimeError) as e:
            logger.warning("Vector search failed: %s", e)
            return []

    fused = await fetch_and_fuse(
        fts_fetch=_fts_fetch, vec_fetch=_vec_fetch,
        limit=limit, fts_weight=fts_weight, vec_weight=vec_weight,
    )

    final_results = []
    for result in fused:
        doc = result.metadata.copy()
        doc["_rrf_score"] = result.fused_score
        doc["_source_rank_fts"] = result.source_rank_fts
        doc["_source_rank_vec"] = result.source_rank_vec
        final_results.append(doc)
    return final_results
```

Net effect: both call sites drop from ~40 lines of manual task-group + object-wrapping boilerplate to ~15 lines of query-specific logic. The concurrency, doc-id derivation, and fusion math now live in exactly one place.

---

## 2. Gemma Sampling Overrides — Moved to Config

**Add to `config/models.yaml`** (new top-level key, sibling to `models:`):

```yaml
# ── Sovereign Sampling Layer: Per-Model Stability Overrides ──────────────
# [M2 Firewall] Moved out of model_gateway.py's generate() hot path.
# Any model can get safety/stability floors here without touching code.
# `match: substring` checks if `key` appears anywhere in the requested
# model_name (case-insensitive). `match: exact` requires full equality.
sampling_overrides:
  gemma-4-31b:
    match: substring
    min_temperature: 0.85
    min_repetition_penalty: 1.2
    forced_logit_bias:
      759: -10.0        # ' la'
      2149: -10.0       # 'la-'
      236772: -10.0     # 'la-' (variant)
    reason: >
      Eliminates repetition-loop failure mode documented in
      COGNITIVE_STABILITY_PLAN.md. Verified token IDs — do not
      renumber without re-verifying against the model's tokenizer.
```

**`src/omega/oracle/model_gateway.py` — add loader in `ModelGateway.__init__`**, next to the existing `self._kv_cache_config = self._load_kv_cache_config()` line:

```python
        self.models = self._load_models()
        self._kv_cache_config = self._load_kv_cache_config()
        self._sampling_overrides = self._load_sampling_overrides()
        self._backend_cache: Dict[str, bool] = {}
```

**Add two new methods**, near `_load_kv_cache_config`:

```python
def _load_sampling_overrides(self) -> dict:
    """Load per-model sampling overrides (safety/stability floors).

    [Sovereign Sampling Layer] Generalizes model-specific tuning that
    was previously hardcoded in generate() (M2 Firewall violation —
    stack-specific logic did not belong in the core engine's hot path).
    """
    if not self.config_path.exists():
        return {}
    with open(self.config_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("sampling_overrides", {}) if data else {}

def _resolve_sampling_override(self, model_name: str) -> Optional[dict]:
    """Find the sampling override entry matching model_name, if any.

    First match wins (dict preserves insertion order, Python 3.7+).
    """
    name_lower = model_name.lower()
    for key, cfg in self._sampling_overrides.items():
        match_mode = cfg.get("match", "substring")
        if match_mode == "exact":
            if name_lower == key.lower():
                return cfg
        elif key.lower() in name_lower:
            return cfg
    return None

def _apply_sampling_overrides(
    self,
    model_name: str,
    temperature: float,
    repetition_penalty: float,
    logit_bias: Optional[Dict[int, float]],
) -> Tuple[float, float, Optional[Dict[int, float]]]:
    """Apply config-driven per-model sampling floors and forced logit biases.

    Replaces the previous hardcoded 'gemma-4-31b' special case in
    generate(). New models get stability overrides via
    config/models.yaml `sampling_overrides` — no code change required.
    """
    override = self._resolve_sampling_override(model_name)
    if not override:
        return temperature, repetition_penalty, logit_bias

    min_temp = override.get("min_temperature")
    if min_temp is not None:
        temperature = max(temperature, min_temp)

    min_rep = override.get("min_repetition_penalty")
    if min_rep is not None:
        repetition_penalty = max(repetition_penalty, min_rep)

    forced_bias = override.get("forced_logit_bias")
    if forced_bias:
        # Defensive cast — YAML plain int keys parse as int already,
        # but this guards against string keys from a hand-edited file.
        forced_bias = {int(k): float(v) for k, v in forced_bias.items()}
        logit_bias = {**(logit_bias or {}), **forced_bias}

    return temperature, repetition_penalty, logit_bias
```

**Replace the hardcoded block in `generate()`:**

```python
        # ── Sovereign Sampling Layer ──────────────────────────────────────────
        # [Sovereign Sampling] Intervention for Gemma 4 31B to eliminate repetition loops.
        # Target: gemma-4-31b-it (or any model identified as Gemma 4 31B)
        if "gemma-4-31b" in model_name.lower():
            # Increase temperature and repetition penalty to escape local probability peaks.
            temperature = max(temperature, 0.85)
            repetition_penalty = max(repetition_penalty, 1.2)

            # Verified token IDs for ' la' and 'la-' from COGNITIVE_STABILITY_PLAN.md
            # These are used to mathematically forbid the model from selecting them.
            GEMMA_LA_TOKENS = {
                759: -10.0,    # ' la'
                2149: -10.0,   # 'la-'
                236772: -10.0, # 'la-' (variant)
            }
            if logit_bias is None:
                logit_bias = GEMMA_LA_TOKENS
            else:
                logit_bias.update(GEMMA_LA_TOKENS)
```

**becomes:**

```python
        # ── Sovereign Sampling Layer ──────────────────────────────────────────
        # Config-driven per-model stability overrides — see
        # config/models.yaml `sampling_overrides`. New models needing
        # stability floors are added there, not here.
        temperature, repetition_penalty, logit_bias = self._apply_sampling_overrides(
            model_name, temperature, repetition_penalty, logit_bias
        )
```

`generate()` drops from 15 lines of model-specific logic to 3. `model_gateway.py` is model-agnostic again.

---

## 3. `_resolve_google_api_key()` — Typed Errors, AnyIO-Compliant

**`src/omega/oracle/providers.py`** — add `import anyio` to the top-level imports (currently missing from this file), then replace the function:

```python
def _resolve_google_api_key() -> str:
    """Resolve the Google API key from the sovereign vault.

    Replaces the previous scattered ``os.environ.get("GOOGLE_API_KEY")`` read
    so the encrypted VaultCore is the single source of truth for API keys.
    """
    try:
        from omega.vault import VaultCore
        vault = VaultCore()
        vault._load_sync()
        cred = vault._credentials.get("google:api_key")
        return cred.encrypted_blob if cred else ""
    except Exception:
        return ""
```

**becomes:**

```python
async def _resolve_google_api_key(trace_id: Optional[str] = None) -> str:
    """Resolve the Google API key from the sovereign vault.

    Single source of truth for API keys (replaces scattered
    ``os.environ.get("GOOGLE_API_KEY")`` reads). Per M9 Error Integrity,
    this NEVER silently swallows a failure into an empty string — every
    failure mode is logged and raised as a typed ProviderAuthError so
    callers can distinguish "not configured" from "vault broken."

    [M1 AnyIO] vault._load_sync() is a blocking, potentially disk-bound
    call — offloaded via anyio.to_thread.run_sync rather than called
    directly on the event loop.

    Args:
        trace_id: Optional trace ID for observability correlation.

    Raises:
        ProviderAuthError: VaultCore is unavailable, fails to load, or
            has no usable 'google:api_key' credential.
    """
    try:
        from omega.vault import VaultCore
    except ImportError as e:
        logger.error("VaultCore import failed while resolving Google API key: %s", e)
        raise ProviderAuthError(
            provider="google",
            message=f"VaultCore unavailable: {e}",
            trace_id=trace_id,
            raw_error=e,
        ) from e

    vault = VaultCore()
    try:
        await anyio.to_thread.run_sync(vault._load_sync)
    except (OSError, RuntimeError, ValueError) as e:
        logger.error(
            "VaultCore failed to load while resolving Google API key: %s",
            e, exc_info=True,
        )
        raise ProviderAuthError(
            provider="google",
            message=f"Vault load failed: {e}",
            trace_id=trace_id,
            raw_error=e,
        ) from e

    # NOTE: vault._credentials is a private attribute reached into from
    # outside VaultCore. This is a pre-existing leaky abstraction, not
    # introduced here — flagged for VaultCore to expose a public
    # get_credential() accessor in a follow-up.
    cred = vault._credentials.get("google:api_key")
    if cred is None or not getattr(cred, "encrypted_blob", None):
        logger.error("No usable 'google:api_key' credential found in vault")
        raise ProviderAuthError(
            provider="google",
            message="No Google API key found in sovereign vault",
            trace_id=trace_id,
        )

    return cred.encrypted_blob
```

**Update the two call sites in the same file** — `GoogleAIProvider`:

```python
class GoogleAIProvider(BaseProvider):
    """Google AI Studio provider (handles Gemini and Gemma models)."""

    async def is_available(self) -> bool:
        # [M9 carve-out] Health probes may catch broadly to prevent crash
        # loops, PROVIDED the error is logged — ProviderAuthError here is
        # typed and expected (not-configured is a routine state).
        try:
            await _resolve_google_api_key()
            return True
        except ProviderAuthError as e:
            logger.warning("Google provider unavailable: %s", e)
            return False

    async def generate(
        self, model: str, system_prompt: str, user_query: str,
        temperature: float, max_tokens: int, trace_id: Optional[str] = None,
        session_id: Optional[str] = None, logit_bias: Optional[Dict[int, float]] = None,
        repetition_penalty: float = 1.0, api_key: Optional[str] = None,
    ) -> Optional[str]:
        # Explicit api_key wins; otherwise resolve from vault. A vault
        # failure now raises ProviderAuthError directly from the resolver
        # — no separate "if not key: raise" needed.
        key = api_key or await _resolve_google_api_key(trace_id=trace_id)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        # ... rest of generate() unchanged from here ...
```

**One caveat worth flagging back to you**: `cred.encrypted_blob` is passed straight into the `x-goog-api-key` header. That field name implies ciphertext. `VaultCore` isn't in the audited pack, so I can't confirm whether decryption happens before `_credentials` is populated or whether this line has always been sending an encrypted blob as a plaintext API key. Worth a direct check of `src/omega/vault/vault_core.py` before this ships — it's an orthogonal bug from the M9 fix, not something I can resolve from the pack alone.
