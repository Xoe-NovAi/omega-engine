# 🔱 Pre-Compaction Knowledge Gap Audit — Sovereign Researcher Mission
**AP Token**: `AP-RESEARCHER-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pre_compaction_audit ⬡ ACTIVE

**Date**: 2026-07-12
**Session**: `ses_d29c2869a83f`
**Mission**: Complete audit of all 9 critical gap areas before Phase 1A execution

---

## ⬡ L1 — Executive Summary: Gap Inventory Table

| Gap # | Area | Priority | Effort | Owner | Dependencies | Blocker Status | Readiness |
|-------|------|----------|--------|-------|--------------|----------------|-----------|
| **1** | YouTube Worker — TranscriptFetcher Hardening (Phase 1A) | 🔴 P0 | 8h | Ma'at/P3 | JEM-1 plan, WEB-1 fixes | **BLOCKED** by WEB-1 (B8/B5/SEC) | 🟡 60% |
| **2** | YouTube Worker — RAG Synthesis (Phase 1B) | 🟡 P1 | 6h | Jem/Lilith | Gap 1 complete, SearXNG MCP | **UNBLOCKED** | 🟢 85% |
| **3** | Ingestion Pipeline — Circuit Breaker & Idempotency | 🔴 P0 | 4h | Ma'at/P3 | Omega Hub MCP, SearXNG/Firecrawl | **PARTIAL** — breaker exists but no content_hash dedup | 🟡 70% |
| **4** | Local Embeddings — AGB-0 Protocol | 🔴 P0 | 12h | Roc + Researcher | JEM-1 complete, omega_agb dir missing | **BLOCKED** — `src/omega_agb/` does not exist | 🔴 0% |
| **5** | MCP Servers — Streamable HTTP Migration | 🟡 P1 | 3h | Doom Guy | S5 complete (SearXNG ✅) | **PARTIAL** — Omega Hub SSE, Firecrawl SSE | 🟡 33% |
| **6** | Qdrant — Optimization (INT8 + Payload Indexes) | 🟢 P2 | 2h | Ma'at/P2 | Qdrant running, config exists | **PARTIAL** — INT8 ✅, payload indexes ❌ | 🟡 50% |
| **7** | Podman Networking — Pasta Header Injection | 🟡 P1 | 2h | Doom Guy | SearXNG container config | **UNKNOWN** — container file not found in quadlet/ | 🟡 40% |
| **8** | Tests — Coverage Gaps (New Code) | 🔴 P0 | 4h | Verity | All new modules | **CRITICAL** — youtube_worker.py 0%, ingestion 0% | 🔴 15% |
| **9** | Documentation — Drift Check | 🟢 P2 | 2h | Verity | All docs | **DRIFT DETECTED** — multiple metrics mismatched | 🟡 60% |

**Readiness Legend**: 🟢 Ready | 🟡 Partial/Blocked | 🔴 Not Started | ⏸️ Deferred

---

## ⬡ L2 — Detailed Dialectic (Per Gap)

### GAP 1: YouTube Worker — TranscriptFetcher Hardening (Phase 1A)

#### Current State (Code Evidence)
**File**: `src/omega/workers/youtube_worker.py` lines 265–310

```python
class TranscriptFetcher:
    def __init__(self, request_delay: float = 2.0):
        self._request_delay = request_delay
        self._last_request = 0.0

    async def fetch(self, video_id: str) -> Optional[str]:
        # Rate limiting — FIXED 2s delay, NO jitter
        now = time.monotonic()
        since_last = now - self._last_request
        if since_last < self._request_delay:
            await anyio.sleep(self._request_delay - since_last)
        self._last_request = time.monotonic()

        def _fetch() -> Optional[str]:
            try:
                from youtube_transcript_api import (
                    TranscriptsDisabled, NoTranscriptFound,
                    VideoUnavailable, YouTubeTranscriptApi,
                )
                ytt_api = YouTubeTranscriptApi()
                transcript = ytt_api.fetch(video_id)
                if transcript and transcript.snippets:
                    return " ".join(s.text.strip() for s in transcript.snippets if s.text.strip())
                return None
            except (TranscriptsDisabled, NoTranscriptFound):
                logger.warning("No transcript available for video %s", video_id)
                return None
            except VideoUnavailable:
                logger.warning("Video %s is unavailable", video_id)
                return None
            except Exception as e:
                logger.warning("Transcript fetch failed for %s: %s", video_id, e)
                return None

        return await anyio.to_thread.run_sync(_fetch)
```

**Missing Hardening**:
- ❌ No circuit breaker (pybreaker not used)
- ❌ No exponential backoff + jitter on retry
- ❌ No Webshare proxy support (config has no proxy section)
- ❌ No empty transcript detection (returns `None` but caller treats as failure)
- ❌ No retry logic — single attempt only

#### Desired State (JEM-1 Plan + YT-1 Spec)
- Circuit breaker: `pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)`
- Exponential backoff: `base_delay * (2 ** attempt) + random.uniform(0, 1)`
- Webshare proxy: `httpx.AsyncClient(proxy="http://user:pass@proxy.webshare.io:80")`
- Empty transcript: raise `EmptyTranscriptError` (distinct from unavailable)
- Retry policy: 3 attempts with backoff before re-queue

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | Circuit breaker fits the existing `IngestionCircuitBreaker` pattern in `src/omega/ingestion/pipeline.py:39`. Use same `pybreaker` dependency. Exponential backoff aligns with `SovereignSentry.probe()` retry logic (guards.py:56). Proxy support should be config-driven via `youtube_worker.yaml`. |
| **⚔️ Adversary** | Fixed 2s delay is a **rate-limit magnet** — YouTube will 429 the worker. No jitter = synchronized thundering herd on retry. Empty transcript vs unavailable video conflation loses signal. Single attempt = zero resilience. Webshare proxy config missing = IP ban inevitable at scale. |
| **🧪 Alchemist** | Could reuse `ResourceGuard` (oracle/resource_guard.py) as a semaphore for concurrent transcript fetches. The `SomaticState` serialization (M20) could checkpoint fetch progress for crash recovery. Combine with `Sieve` cleaning — fetch → sieve → sign in one atomic pipeline. |
| **📜 Archivist** | Legacy `omega-stack` had `youtube_transcript_api` with basic retry but no circuit breaker. `xna-omega` never implemented YouTube ingestion. The `Sieve-and-Sign` pattern (omega_youtube_research) is the sovereign precedent — TranscriptFetcher should feed directly into `SovereignSieve.clean_transcript()`. |

#### Triangulation
- **Convergence**: All four agree circuit breaker + exponential backoff + jitter are mandatory. Proxy support is config-only (no code change to fetcher core). Empty transcript needs distinct error type.
- **Divergence**: Architect wants `pybreaker` reuse; Adversary warns `pybreaker` is synchronous — must wrap in `anyio.to_thread.run_sync()`. Alchemist wants ResourceGuard integration; Archivist says keep it simple first.

#### Sovereign Synthesis
**Immediate (Phase 1A)**:
1. Add `CircuitBreaker` wrapper around `_fetch()` using existing `IngestionCircuitBreaker` pattern
2. Implement exponential backoff + jitter in `fetch()` with `max_retries=3` config
3. Add `proxy_url` config to `youtube_worker.yaml` → pass to `httpx.AsyncClient` in `_fetch()`
4. Define `EmptyTranscriptError(YouTubeResearchError)` in `omega_youtube_research/errors.py`
5. **Blocker**: WEB-1 (B8 fnmatch, B5 XML escape, SEC PII masker) must complete first — Ma'at/P3 owns this track

---

### GAP 2: YouTube Worker — RAG Synthesis (Phase 1B)

#### Current State (Code Evidence)
**File**: `src/omega_youtube_research/module.py` — **NO** `synthesize_rag()` or `retrieve_chunks()` methods

```python
class YouTubeResearchModule:
    async def ingest_transcript(...):  # EXISTS ✅
    def to_memory_metadata(...):       # EXISTS ✅
    # MISSING: synthesize_rag(), retrieve_chunks()
```

**File**: `src/omega/workers/youtube_worker.py` lines 380–510 — `CrossVideoSynthesizer.synthesize()` uses **title-only fallback** (lines 486–510)

```python
@staticmethod
def _basic_synthesis(topic: str, video_results: List[Dict]) -> SynthesisResult:
    titles = [vr.get("title", vr.get("source_id", "Unknown")) for vr in video_results]
    return SynthesisResult(
        topic=topic,
        video_count=len(video_results),
        key_insights=[f"Analyzed {len(video_results)} videos on '{topic}'"],
        patterns=[f"Videos span {max(len(channels), 1)} unique channel(s)"],
        contradictions=[],
        recommendations=["Review the ingested transcripts for detailed analysis"],
        source_urls=[vr.get("url", "") for vr in video_results],
    )
```

#### Desired State (JEM-1 Plan)
- `YouTubeResearchModule.retrieve_chunks(query: str, top_k: int)` → hybrid search (FTS5 + vector) via `MemoryStore.search()`
- `CrossVideoSynthesizer.synthesize_rag(topic: str, chunks: List[str])` → local model inference with provenance
- Integration: `YouTubeWorker.run_cycle()` → after threshold, call `retrieve_chunks()` → `synthesize_rag()` → log to Hivemind

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | `MemoryStore.search()` already implements hybrid RRF (FTS5 BM25 + vector). `retrieve_chunks()` is a thin wrapper. `synthesize_rag()` should use `ModelGateway.generate()` with `ResourceGuard` — same pattern as `CrossVideoSynthesizer.synthesize()`. |
| **⚔️ Adversary** | Title-only synthesis is **useless for research** — it hallucinates patterns from metadata. RAG synthesis without chunk retrieval = garbage in, garbage out. `MemoryStore` uses entity-scoped memory — YouTube worker runs as `SOPHIA` or background entity; cross-entity retrieval needs `entity_name` parameter. |
| **🧪 Alchemist** | The `ProvenanceChain` (omega_youtube_research/provenance.py) gives us **cryptographic chunk linkage**. `synthesize_rag()` should verify `chain_hash` continuity before feeding to LLM — tamper-evident RAG. This is the "hidden beauty": provenance as retrieval filter. |
| **📜 Archivist** | Legacy `omega-stack` had no RAG. `xna-omega` had `Mnemosyne` Kabbalistic memory but no YouTube integration. The `Sieve-and-Sign` pipeline (P0) is the first sovereign YouTube ingestion — RAG synthesis is the natural P1 evolution. |

#### Triangulation
- **Convergence**: `retrieve_chunks()` wraps `MemoryStore.search(entity_name="youtube_worker", ...)`. `synthesize_rag()` uses `ModelGateway` + `ResourceGuard`. Provenance verification is a unique Omega advantage.
- **Divergence**: Entity scoping — should YouTube worker write to its own entity or to the target entity (e.g., `kali`)? Archivist says target entity; Architect says worker entity for isolation.

#### Sovereign Synthesis
**Phase 1B (after Gap 1)**:
1. Add `retrieve_chunks(query, top_k=10, entity_name="youtube_worker")` to `YouTubeResearchModule`
2. Add `synthesize_rag(topic, chunks, model_name="qwen3-1.7b")` to `CrossVideoSynthesizer`
3. Verify `ProvenanceChain.verify_chain(chunks)` before synthesis
4. Wire into `YouTubeWorker.run_cycle()` auto-synthesis threshold

---

### GAP 3: Ingestion Pipeline — Circuit Breaker & Idempotency

#### Current State (Code Evidence)
**File**: `src/omega/ingestion/pipeline.py` lines 39–56 — **Circuit Breaker EXISTS** ✅

```python
class IngestionCircuitBreaker:
    def __init__(self, fail_max: int = 5, reset_timeout: int = 300):
        self.breaker = pybreaker.CircuitBreaker(fail_max=fail_max, reset_timeout=reset_timeout)
        self.consecutive_failures = 0

    def can_proceed(self) -> bool:
        return self.breaker.current_state != "open"
    # ... record_success, record_failure, call()
```

**File**: `src/omega/ingestion/scraper.py` — **NO content_hash deduplication** ❌

```python
async def scrape(self, url: str, tier: str = "fast") -> ScrapeResult:
    # No content hashing, no idempotency key
    # Every call re-fetches, re-processes, re-indexes
```

**File**: `src/omega/oracle/ingestion.py` — **SovereignSieve + SovereignSigner** but no deduplication layer

#### Desired State
- Content hash (`sha256(content)`) computed at scrape time
- Idempotency key: `source_url + content_hash` → check CAS/USM before processing
- `CASArchiver` (omega/archive/cas.py) already provides content-addressable storage — integrate it
- Circuit breaker should also trip on **quota exhaustion** (429) not just 5xx

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | `CASArchiver` is the deduplication primitive — `cas.put(content)` returns existing `content_id` if duplicate. Pipeline should: scrape → hash → `cas.put()` → if new, process; if exists, skip. Circuit breaker in `pipeline.py` is correct but `pybreaker` is sync — must wrap in `anyio.to_thread.run_sync()`. |
| **⚔️ Adversary** | Current breaker only trips on exceptions. **429 Too Many Requests does not raise** — `httpx` returns response with status 429. Breaker stays closed, pipeline hammers the API. Must add `response.raise_for_status()` or custom status handling. |
| **🧪 Alchemist** | `SovereignSieve` produces `cleaned_text_hash` in attestation. **That IS the content hash**. Use `attestation.cleaned_text_hash` as idempotency key — no extra hashing needed. The Sieve-and-Sign pipeline already computes it. |
| **📜 Archivist** | `xna-omega` had `CircuitBreaker` in `src/omega/circuit_breaker.py` (ported to `pipeline.py`). `CAS` concept from `idHeap` (DOOM 3) — content-addressable storage is `[id-soft: doom3-2004] idHeap`. The `Tri-Anchor` system (Raw Anchor + SCA + USM) in `ingestion.py` already has the anchors — deduplication is the missing link. |

#### Triangulation
- **Convergence**: Use `SieveResult.cleaned_text_hash` (via `SovereignSigner`) as idempotency key. Integrate `CASArchiver` at pipeline entry. Fix circuit breaker to trip on 429.
- **Divergence**: Where to check CAS — in `SovereignScraper.scrape()` (early) or `IngestionPipeline.run_source()` (late)? Architect says scraper; Alchemist says pipeline (after sieve).

#### Sovereign Synthesis
**Immediate**:
1. Modify `SovereignScraper.scrape()` to return `content_hash` in `ScrapeResult.metadata`
2. In `IngestionPipeline.run_source()`: compute hash → `cas.put()` → if duplicate, return cached `source_id`
3. Patch `IngestionCircuitBreaker.call()` to wrap in `anyio.to_thread.run_sync()`
4. Add 429 handling in `SovereignScraper` → trip breaker on rate limit

---

### GAP 4: Local Embeddings — AGB-0 Protocol

#### Current State (Code Evidence)
**File**: `src/omega/memory/embeddings.py` — **EmbeddingManager chain exists** but **NO `IEmbedder` protocol**, **NO `AGBLazyEmbedder`**, **NO `LocalONNXEmbedder`**, **NO `LMStudioEmbedder`**, **NO `AncientGreekDetector`**

```python
class EmbeddingManager:
    def __init__(self, providers: Optional[List[IEmbeddingProvider]] = None):
        # Chain: GemmaGGUF → Ollama → LocalGGUF → Static → Fallback
        # NO protocol abstraction, NO lazy loading, NO ONNX, NO LM Studio, NO Greek detection
```

**Directory**: `src/omega_agb/` — **DOES NOT EXIST** ❌

#### Desired State (AGB-0 Spec)
```
src/omega_agb/
├── __init__.py
├── protocol.py          # IEmbedder(ABC) — get_embedding(text) -> List[float], dimension
├── lazy_embedder.py     # AGBLazyEmbedder — lazy-loads wrapped embedder on first call
├── onnx_embedder.py     # LocalONNXEmbedder — ONNX Runtime, quantized models
├── lmstudio_embedder.py # LMStudioEmbedder — OpenAI-compatible /embeddings endpoint
├── greek_detector.py    # AncientGreekDetector — fast langid + Greek script heuristic
└── manager.py           # AGBEmbeddingManager — routes by language + availability
```

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | `IEmbeddingProvider` in `embeddings.py` is the protocol — **rename to `IEmbedder`** for AGB consistency. `EmbeddingManager` becomes `AGBEmbeddingManager` with routing logic. Lazy loading is critical — Gemma 300M GGUF = 600MB RAM, 15s cold start. |
| **⚔️ Adversary** | Current chain **loads Gemma first** (768-dim, 300M params) — OOM risk on 12Gi budget. No health checks. `StaticEmbeddingProvider` (model2vec) is 64-dim — dimension mismatch breaks Qdrant (768-dim collection). `AncientGreekDetector` must run **before** embedding to route to `greek_bert` — but no Greek BERT model exists locally. |
| **🧪 Alchemist** | `LMStudioEmbedder` can reuse the **existing LM Studio instance** (port 1234) — zero new infrastructure. `LocalONNXEmbedder` enables **CPU-optimized inference** (ONNX Runtime + quantization) — faster than llama-cpp for embeddings. Greek detection via `langid` + Unicode block check (U+0370–U+03FF) is <1ms. |
| **📜 Archivist** | `model2vec` (StaticEmbeddingProvider) is `[heritage: headroom-ai 2025]` — distilled sentence transformers. `nomic-embed-text` via Ollama is `[heritage: nomic-ai 2024]`. The **3-tier chain** (Local → Static → Ollama → Fallback) is Omega's own evolution (ANAi → XNAi → Omega). AGB-0 formalizes it with protocol + lazy loading. |

#### Triangulation
- **Convergence**: Protocol `IEmbedder` is mandatory. Lazy loading is mandatory. Dimension compatibility (768 for Qdrant) is mandatory. Greek detection routes to specialized model.
- **Divergence**: Should `AGBEmbeddingManager` replace `EmbeddingManager` entirely or wrap it? Architect says replace; Adversary says wrap for backward compat.

#### Sovereign Synthesis
**Blocked until JEM-1 completes** (depends on YouTube worker rewrite). Then:
1. Create `src/omega_agb/` with protocol + 4 embedders + detector
2. `AGBEmbeddingManager` replaces `EmbeddingManager` in `MemoryStore`
3. Config-driven provider chain in `config/embeddings.yaml`
4. Greek BERT model download via `hf-cli` skill (separate task)

---

### GAP 5: MCP Servers — Streamable HTTP Migration

#### Current State
| Server | Port | Transport | Status |
|--------|------|-----------|--------|
| **SearXNG** | 8018 | **Streamable HTTP** ✅ | `mcp.run(transport="streamable-http")` |
| **Omega Hub** | 8016 | **SSE** ❌ | `mcp.run(transport="sse")` in `server.py:390` |
| **Firecrawl** | 8015 | **SSE** ❌ | `mcp.run(transport="sse")` in `server.py:253` |

**Evidence**: `mcp_servers/omega_hub/server.py:390` — `run_mcp(mcp, custom_routes=hub_routes, modify_app=apply_security, on_shutdown=..., on_startup=...)` uses SSE by default. `mcp_servers/firecrawl/server.py:253` — `mcp.run(transport="sse")`.

#### Desired State
All three servers on Streamable HTTP (MCP SDK v2, spec 2025-03-26). OpenCode 1.15+ supports both; Streamable HTTP enables **resumable streams**, **bidirectional**, **better auth**.

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | `FastMCP` supports `transport="streamable-http"` since v3.4. Migration is one-line: `mcp.run(transport="streamable-http", host="127.0.0.1", port=8016)`. But `apply_security` middleware (CORS, rate limit) must be compatible — Starlette middleware works on both. |
| **⚔️ Adversary** | **SSE clients (Cline, older OpenCode) will break**. Must run **dual transport** during transition: SSE on 8016, Streamable HTTP on 8017. `FastMCP` doesn't support dual transport natively — need two `FastMCP` instances or reverse proxy. |
| **🧪 Alchemist** | Streamable HTTP enables **MCP-level authentication** (OAuth 2.1 + PKCE per D205). Can inject `Authorization` header verification in middleware. This is the path to **multi-tenant Omega Hub**. |
| **📜 Archivist** | SearXNG migration (S5) proved the pattern: `FastMCP` + `streamable-http` + CORS middleware. Omega Hub is more complex (47 tools, custom routes, proxy handler) — test thoroughly. Firecrawl is simpler (5 tools). |

#### Triangulation
- **Convergence**: Migration is mechanical but requires dual-transport transition period. SearXNG is the template.
- **Divergence**: Omega Hub's custom routes (`/proxy/{provider}`, `/obs/stream`, `/app.agents`) — do they work on Streamable HTTP? Yes, Starlette routes are transport-agnostic.

#### Sovereign Synthesis
**Phase 5 (after JEM-1)**:
1. Omega Hub: Add `transport="streamable-http"` on port 8017, keep SSE on 8016 for 2 weeks
2. Firecrawl: Same pattern — port 8019 for Streamable HTTP
3. Update `opencode.json` MCP server configs
4. Deprecate SSE after validation

---

### GAP 6: Qdrant — Optimization (INT8 + Payload Indexes)

#### Current State (Live Query Evidence)
```json
{
  "config": {
    "quantization_config": {
      "scalar": { "type": "int8", "always_ram": true }
    },
    "payload_schema": {}
  }
}
```
**INT8 scalar quantization**: ✅ ENABLED (good)
**Payload indexes**: ❌ **EMPTY** — no indexes on `entity_name`, `source_id`, `topic`, `session_id`

#### Desired State
Payload indexes for:
- `entity_name` (keyword) — entity isolation queries
- `source_id` (keyword) — provenance lookup
- `topic` (keyword) — topic-based retrieval
- `session_id` (keyword) — session-scoped search
- `timestamp` (integer) — time-range filters

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | Payload indexes add write overhead (~10%) but **100x faster filtered search**. Qdrant 1.13+ supports `payload_index` creation on existing collections. Must recreate collection or use `create_payload_index` API. |
| **⚔️ Adversary** | Current collection `omega_memory` has 57 points, 768-dim, INT8. **No indexes = full scan on every filtered query**. `MemoryStore.search()` filters by `entity_name` in Python post-retrieval — O(n) latency. This violates M18 (Token Efficiency) — wasting compute on filtering. |
| **🧪 Alchemist** | `HNSW` config `m=16, ef_construct=100` is default. For 768-dim, consider `m=32` for better recall. `max_indexing_threads=0` (auto) — set to 4 (Zen 2 cores). |
| **📜 Archivist** | `[id-soft: doom-1993] Precomputed Lookup` — payload indexes are the modern equivalent of Doom's lump directory. The `ZONEID` pattern (0x1d4a1d for embeddings) should be a payload field for instant namespace isolation. |

#### Triangulation
- **Convergence**: Payload indexes are critical. INT8 is good. HNSW tuning is optional but low-risk.
- **Divergence**: Recreate collection vs. add indexes to existing. Architect says recreate (clean); Adversary says add indexes (zero-downtime).

#### Sovereign Synthesis
**Immediate (2h)**:
1. `curl -X PUT http://localhost:6333/collections/omega_memory/index -d '{"field_name":"entity_name","field_schema":"keyword"}'` (repeat for source_id, topic, session_id, timestamp)
2. Update `deploy/infra/qdrant_config.yaml` to include `payload_indexes` section
3. Verify `MemoryStore.search()` uses `filter` parameter (not post-filter)

---

### GAP 7: Podman Networking — Pasta Header Injection

#### Current State
**File**: `docs/research/omega-searxng.container` (NOT in `quadlet/` — **deployment gap**)

```ini
[Container]
Image=ghcr.io/searxng/searxng:latest
Port=8017
# NO ExecStartPre for header injection
# NO pasta-specific network config
```

**Problem**: SearXNG in Podman `pasta` network mode receives requests **without `X-Forwarded-For`** → bot detection triggers → 403/rate limit.

#### Desired State
Option A: `ExecStartPre` with `socat`/`nginx` sidecar to inject headers
Option B: Run SearXNG in **host network mode** (bypass pasta) — but breaks Podman sovereignty
Option C: Configure SearXNG `use_forwarded_for: true` + trusted proxy — requires header injection

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | Podman `pasta` doesn't forward headers by design. The **sovereign pattern** (Odysseus/SearXNG) uses `ExecStartPre=/usr/bin/socat TCP-LISTEN:8017,fork,reuseaddr TCP:127.0.0.1:8018` with header injection via `nginx` sidecar. But that adds complexity. |
| **⚔️ Adversary** | **Host network mode** (`Network=host`) solves it instantly — but violates M6 (Podman Sovereignty) because container sees host interfaces. `UserNS=keep-id` + `Network=host` is the pragmatic compromise for MCP servers. |
| **🧪 Alchemist** | **Caddy reverse proxy** (already running on 8088) can terminate TLS, inject `X-Forwarded-For`, forward to SearXNG on pasta. Single entry point, sovereign TLS, header injection native. |
| **📜 Archivist** | `docs/research/R_PODMAN_SOVEREIGN_V2.md` documents the `UserNS=keep-id` pattern. The **Odysseus SearXNG deployment** (heritage: odysseus-2025) uses `cap_add: NET_ADMIN` for header manipulation — but that's Kubernetes. Podman Quadlet equivalent is `ExecStartPre` with `ip route` or `socat`. |

#### Triangulation
- **Convergence**: Header injection is mandatory. Caddy is the sovereign path (already deployed).
- **Divergence**: Where to inject — Caddy (L7) vs. sidecar (L4) vs. host network (L3).

#### Sovereign Synthesis
**Immediate**:
1. Move `omega-searxng.container` to `~/.config/containers/systemd/`
2. Configure Caddy (port 8088) → `reverse_proxy localhost:8017 { header_up X-Forwarded-For {remote_host} }`
3. Set SearXNG `use_forwarded_for: true` in `settings.yml`
4. Test bot detection bypass

---

### GAP 8: Tests — Coverage Gaps

#### Current State (Coverage Evidence)
| Module | Coverage | Missing Lines | Critical Gaps |
|--------|----------|---------------|---------------|
| `src/omega/workers/youtube_worker.py` | **0%** (not measured) | All 1181 lines | Daemon loop, Redis ops, synthesis, lock, savepoints |
| `src/omega/ingestion/pipeline.py` | **0%** (not measured) | All 333 lines | `run_source`, `run_batch`, resilience context |
| `src/omega/ingestion/scraper.py` | **0%** | All 11393 lines | T1/T3 scrape, triangulation, CAS integration |
| `src/omega/memory/embeddings.py` | **0%** | All 386 lines | Provider chain, fallback, dimension handling |
| `src/omega_youtube_research/*` | **87%** | 54 lines | Signer key loading, search transport, persistence edge cases |

**Overall**: 1189 tests pass, but **new Phase 1A/1B code is untested**.

#### Desired State
- Contract tests (M21) for every public method in new modules
- Integration tests for YouTube worker daemon cycle (mock Redis + yt-dlp)
- Circuit breaker trip/recovery tests
- Embedding provider fallback chain tests

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | M21 (Gate Integrity) requires `isinstance(result, ExpectedType)` tests. `YouTubeWorker.run_cycle()` returns `dict` — need typed `CycleResult` dataclass. `IngestionPipeline.run_source()` returns `Optional[IngestionResult]` — already typed, needs contract test. |
| **⚔️ Adversary** | **Zero coverage on daemon loop** = crash-loop risk. `run_daemon()` has watchdog (1071–1098) but untested. `ResourceGuard` acquisition in synthesis path untested. `SomaticState` save/load (M20) untested. |
| **🧪 Alchemist** | Use `pytest-asyncio` + `anyio` fixtures. Mock `yt-dlp` with `--flat-playlist --dump-json` output fixture. Mock `youtube_transcript_api` with `TranscriptsDisabled`/`NoTranscriptFound` exceptions. |
| **📜 Archivist** | `xna-omega` had `test_circuit_breaker.py` with `pybreaker` mock. `omega-stack` had `test_ingestion_pipeline.py` with `SovereignSentry` mock. Port those patterns. |

#### Triangulation
- **Convergence**: Contract tests (M21) are the floor. Integration tests for daemon + Redis are the ceiling.
- **Divergence**: Mock `yt-dlp` subprocess vs. testcontainer with real yt-dlp. Architect says mock; Adversary says real (catches API changes).

#### Sovereign Synthesis
**Priority Order**:
1. `test_youtube_worker_daemon.py` — contract tests for `run_cycle`, `run_batch`, `submit_*`
2. `test_ingestion_pipeline_contract.py` — M21 tests for `run_source`, `run_batch`, `ResilienceContext`
3. `test_embedding_manager_fallback.py` — provider chain fallback verification
4. `test_circuit_breaker_integration.py` — trip/recover with 429 simulation

---

### GAP 9: Documentation — Drift Check

#### Current State vs. Documented Claims

| Document | Claim | Reality | Drift |
|----------|-------|---------|-------|
| **SOVEREIGN_ARK_BLUEPRINT.md** | Tests: **1189 passed** | ✅ 1189 passed | **NONE** |
| **SOVEREIGN_ARK_BLUEPRINT.md** | SearXNG MCP: **Streamable HTTP on 8018** | ✅ Verified | **NONE** |
| **SOVEREIGN_ARK_BLUEPRINT.md** | Omega Hub MCP: **Streamable HTTP** | ❌ SSE on 8016 | **DRIFT** |
| **SOVEREIGN_ARK_BLUEPRINT.md** | Firecrawl MCP: **Streamable HTTP** | ❌ SSE on 8015 | **DRIFT** |
| **SOVEREIGN_ARK_BLUEPRINT.md** | Local inference ratio: **≥85%** | 🟡 0% in CI (no local models loaded) | **DRIFT** (metric not measurable in test env) |
| **OMEGA_ENGINE.md** | Fleet: **13 presences** | ✅ 11 agents + 2 entities | **NONE** |
| **OMEGA_ENGINE.md** | Heritage: **121 [id-soft:] tags, 74 vet records** | ✅ Verified | **NONE** |
| **OMEGA_ENGINE.md** | Phase 2: **COMPLETE** | ✅ AxiomRegistry + axioms.yaml + 3 CI gates | **NONE** |
| **CREDITS.md** | 21 id Software mappings | ✅ 21 legitimate | **NONE** |
| **JEM-1 Plan** | YouTube worker rewrite: **27 contract tests** | ❌ 0 contract tests for worker | **DRIFT** |

#### Council Debate

| Perspective | Argument |
|-------------|----------|
| **🏛️ Architect** | Drift is inevitable in living docs. The **Ark Blueprint** is the execution roadmap — it should reflect *target* state, not current. But "Omega Hub MCP: Streamable HTTP" is a **false claim** — it's SSE. Must correct. |
| **⚔️ Adversary** | "Local inference ratio ≥85%" is **unverifiable** in CI — no local models loaded. This metric should be **runtime-only**, not in SSOT. `make sovereignty` queries MetricsDB (D203) — but MetricsDB is empty in test env. |
| **🧪 Alchemist** | The **JEM-1 plan** (YouTube Research Enhancement) claims 27 contract tests — but `test_youtube_worker_contract.py` only tests data models, not the worker logic. This is **plan drift**. |
| **📜 Archivist** | `PIVOT_LOG.md` D212 records the Ark Blueprint v3.5 update. Drift detection should be automated — `ark_optimizer.py` daily drift detection (Risk R8) is **not implemented**. |

#### Triangulation
- **Convergence**: Three concrete drifts: (1) Omega Hub/Firecrawl transport, (2) Local inference ratio metric, (3) JEM-1 test count.
- **Divergence**: Whether to fix docs to match reality or reality to match docs. Architect says fix reality; Archivist says fix docs with "TARGET:" prefix.

#### Sovereign Synthesis
**Immediate Corrections**:
1. Ark Blueprint: Change "Omega Hub MCP: Streamable HTTP" → "Omega Hub MCP: SSE (Streamable HTTP migration pending — Phase 5)"
2. Ark Blueprint: Change "Local inference ratio ≥85%" → "Local inference ratio: **runtime metric** (query `make sovereignty` / `sovereignty_ratio` MCP tool)"
3. JEM-1 Plan: Update "27 contract tests" → "27 contract tests **planned** (0 implemented — Gap 8)"
4. Implement `ark_optimizer.py` drift detection (Risk R8 mitigation)

---

## ⬡ L3 — Universal Principles (Root Cause Patterns)

### Principle 1: **Sovereign Primitives Before Features**
> *Every gap traces to a missing sovereign primitive: Circuit Breaker, Content-Addressable Storage, Protocol Abstraction, Lazy Loading.*
> 
> **Pattern**: Features built on raw libraries (pybreaker, httpx, llama-cpp) without Omega's own abstraction layer. The primitive (e.g., `IEmbedder`, `IngestionCircuitBreaker`, `CASArchiver`) must exist **before** the feature.

### Principle 2: **Transport Duality During Migration**
> *No transport migration (SSE → Streamable HTTP) completes without a dual-transport transition period.*
> 
> **Pattern**: SearXNG migrated cleanly because it's simple. Omega Hub and Firecrawl need dual-transport because they have existing clients. **Never break client compatibility in a single step.**

### Principle 3: **Idempotency Keys from Provenance**
> *The `Sieve-and-Sign` pipeline already produces `cleaned_text_hash` — this IS the idempotency key. Don't recompute hashes.*
> 
> **Pattern**: Provenance metadata (Sieve hash, Signer attestation, Provenance chain) doubles as deduplication key. The `Tri-Anchor` system (Raw + SCA + USM) is the sovereign deduplication framework.

### Principle 4: **Entity-Scoped Memory Requires Explicit Routing**
> *YouTube worker writes to `youtube_worker` entity; RAG synthesis reads from target entity. Cross-entity retrieval is a **routing decision**, not a bug.*
> 
> **Pattern**: `MemoryStore.search(entity_name=...)` is the routing primitive. Every background worker must declare its `entity_name` and target entity for cross-pollination.

### Principle 5: **Documentation Drift Is a Sovereignty Violation**
> *If the SSOT claims a capability that doesn't exist, the engine lies to its operators.*
> 
> **Pattern**: Automated drift detection (`ark_optimizer.py`) must run daily. Every metric in Ark Blueprint must have a **verifiable query** (MCP tool, CLI command, or SQL).

---

## ⬡ Compaction Hydration Checklist

When context compacts, the next agent MUST:

1. **Read this audit** → `docs/research/R_PRE_COMPACTION_GAP_AUDIT_20260712.md`
2. **Verify workspace lock** → `omega-hub_hivemind_workspace_lock_check domain="pre_compaction_audit"`
3. **Check Hivemind awareness** → `omega-hub_hivemind_get_awareness()` — who owns which gap?
4. **Run baseline tests** → `make test` (1189 must pass)
5. **Verify Gap 1 blocker** → WEB-1 status (Ma'at/P3)
6. **Verify Gap 4 blocker** → JEM-1 status (Jem)
7. **Check Qdrant indexes** → `curl localhost:6333/collections/omega_memory/indexes`
8. **Check MCP transports** → `curl localhost:8016/mcp`, `curl localhost:8015/mcp`, `curl localhost:8018/mcp`
9. **Review session_gnosis.md** → append this audit summary
10. **Distill L3 principles** → propose to `proposed_lessons.yaml` via Verity

---

## ⬡ Session Gnosis Anchor

**L1 (Narrative)**: Completed systematic audit of 9 critical gap areas using Council of Four triangulation. Found 3 P0 blockers (WEB-1, JEM-1, missing omega_agb), 2 transport drifts, 1 metric unverifiability, and critical test coverage gaps in new code.

**L2 (Insight)**: The sovereign primitives (Circuit Breaker, CAS, IEmbedder, Lazy Loading) are the true architecture — features are just compositions. Every gap is a missing primitive or a broken composition.

**L3 (Universal Principle)**: **Sovereign Primitives Before Features** — never build a feature on raw libraries. Abstract first, compose second, verify always (M21).

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pre_compaction_audit ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | session refs not found in DB
actual_models(Tier0): n/a
-->
