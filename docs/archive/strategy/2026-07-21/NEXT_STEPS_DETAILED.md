# 🔱 Omega Engine — Detailed Next Steps Plan (Post-Research)
**Date**: 2026-07-12
**Baseline**: 1189 tests passing, Temple-Grade T1-T14 PASS
**Research Sources**: JEM-2 (644 lines) + Researcher Deep-Dive (1421 lines) + Jem MaKaLi Deep Research (544 lines via Exa/Firecrawl)

---

## Executive Summary

**Two parallel workstreams validated and ready**:

**Workstream A — 9 Infrastructure Gaps** (JEM-2 + Researcher Deep-Dive, ~25h):
Implementation-ready, 4 phases. **GAP 5 is a documentation task** (dual-transport already exists). **GAP 4 belongs in `src/omega/memory/`** (M2 firewall). **youtube-transcript-api must be installed** before GAP 1.

**Workstream B — 5 Sovereignty Gaps** (Jem MaKaLi Deep Research via Exa/Firecrawl, ~60h):
Validated with 3 major corrections to the council's hypotheses. See `R_JEM_MAKALI_DEEP_RESEARCH_20260712.md`.

**Key Corrections from Jem**:
1. **S1 (Export)**: ZIP+JSON `.omega` bundle — NOT Parquet (Parquet is ML-only, conflicts with every 2026 standard)
2. **S2 (Eval)**: LLM-as-Judge requires **calibration** (isotonic regression, ECE 0.18→0.06) — uncalibrated small judges are dangerously overconfident
3. **S5 (Orchestration)**: **Redis Streams + Consumer Groups** — NOT Pub/Sub (Pub/Sub drops messages under load)

---

## Combined Dependency Graph

```
═════════════════════════════════════════════════════
WORKSTREAM A — Infrastructure (from JEM-2 + Researcher)
═════════════════════════════════════════════════════

GAP 9 (Doc Drift)          ──────┐
GAP 6 (Qdrant Indexes)     ──────┼──► Phase A1 (Foundation, 3.5h)
GAP 7 (Caddy Proxy)        ──────┘

GAP 3 (CASArchiver)        ──────┐
GAP 1 (TranscriptFetcher)  ──────┼──► Phase A2 (Core, 11h)
GAP 2 (RAG Synthesis)      ──────┘

GAP 4 (AGB-0 Embedding)    ──────► Phase A3 (Specialist, 6h)

GAP 8 (Contract Tests)     ──────► Phase A4 (Validation, 4h)

═════════════════════════════════════════════════════
WORKSTREAM B — Sovereignty (from Jem MaKaLi Deep Research)
═════════════════════════════════════════════════════

S2 (Eval Pipeline)         ──────┐  (P1, 8h)
S3 (Adaptive RAG)          ──────┼──► Phase B1 (Sprint 1, 24h)
P1-3 (Hivemind Event Bus)  ──────┘  Parallel with S2+S3

S5 (Redis Streams)         ──────┐  (P2, 20h)
S1 (Export Bundle)         ──────┼──► Phase B2 (Sprint 2, 40h)
S4 (Knowledge Graph)       ──────┘  Sequential from B1
```

Total Workstream B effort: **~60h** across 5 domains. Recommended execution order: **S2 → S3 → S5 → S1 → S4** (per Jem's priority matrix).

---

## Phase A1: Foundation (3.5h — Parallel, No Dependencies)

### GAP 9: Documentation Drift Fix (30min)

**Owner**: Kali
**Files**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`

| Change | Current | Corrected | Status |
|--------|---------|-----------|--------|
| Omega Hub transport | "SearXNG MCP on :8018 Streamable HTTP ✅" | Add "Omega Hub: SSE :8016 (Streamable HTTP pending)" | ✅ DONE (v3.6) |
| Local inference ratio | "0% in test env" | "TARGET: ≥80% (runtime metric, 0% in CI)" | ✅ DONE (v3.6) |
| Test count | (stale) | "1189 passed, 42 skipped, 3 xfailed" | ✅ DONE (v3.6) |
| Add timestamps | (none) | "LAST_VERIFIED: 2026-07-12" | ✅ DONE (v3.6) |
| Jem's 5 corrections | (missing) | Added §IV Validated Sovereignty Gaps | ✅ DONE (v3.6) |

**Verification**: `grep -c "LAST_VERIFIED" docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` should return ≥6

### GAP 9: Documentation Drift Fix (30min)

**Owner**: Verity
**Files**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`

| Change | Line | Current | Corrected |
|--------|------|---------|-----------|
| Omega Hub transport | 20 | "SearXNG MCP on :8018 Streamable HTTP ✅" | Add "Omega Hub: SSE :8016 (Streamable HTTP pending)" |
| Local inference ratio | 22 | "0% in test env" | "TARGET: ≥80% (runtime metric, 0% in CI)" |
| Test count | 19 | (stale) | "1189 passed, 42 skipped, 3 xfailed" |
| Add timestamps | all | (none) | "LAST_VERIFIED: 2026-07-12" |

**Verification**: `grep -c "LAST_VERIFIED" docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` should return ≥3

---

### GAP 6: Qdrant Payload Indexes (1h)

**Owner**: Ma'at/P2
**File**: `src/omega/memory/vector_adapters.py` — `_ensure_collection()` method

**Step 1**: Add payload index creation after collection creation:

```python
# src/omega/memory/vector_adapters.py — _ensure_collection()
async def _ensure_collection(self, collection_name: str, dimension: int = 768):
    # ... existing collection creation code ...

    # ── Payload Indexes (62x speedup on selective filters) ──
    # [heritage: qdrant-2021] Filter-before-search optimization
    payload_indexes = [
        {"field_name": "entity_name", "field_schema": "keyword"},
        {"field_name": "session_id", "field_schema": "keyword"},
        {"field_name": "content_type", "field_schema": "keyword"},
        {"field_name": "timestamp", "field_schema": "integer"},
    ]
    for idx in payload_indexes:
        try:
            await self._client.create_payload_index(
                collection_name=collection_name,
                field_name=idx["field_name"],
                field_schema=idx["field_schema"],
            )
        except Exception as e:
            # Index may already exist — log and continue
            if "already exists" not in str(e).lower():
                logger.warning("Payload index creation failed: %s", e)
```

**Step 2**: Update `QdrantAdapter.query()` to use Qdrant `Filter` objects instead of Python post-filtering:

```python
# src/omega/memory/vector_adapters.py — query()
async def query(self, query_vector: List[float], entity_name: str = None, limit: int = 10):
    # Build Qdrant Filter (server-side, uses payload indexes)
    must_conditions = []
    if entity_name:
        must_conditions.append(
            models.FieldCondition(key="entity_name", match=models.MatchValue(value=entity_name))
        )
    query_filter = models.Filter(must=must_conditions) if must_conditions else None

    results = await self._client.search(
        collection_name=self._collection_name,
        query_vector=query_vector,
        limit=limit,
        query_filter=query_filter,
    )
    return results
```

**Verification**:
```bash
curl -s http://localhost:6333/collections/omega_memory | jq '.payload_schema'
# Should show entity_name, session_id, content_type, timestamp indexes
```

---

### GAP 7: Caddy + SearXNG Header Injection (2h)

**Owner**: Doom Guy
**Files**: `docs/research/omega-searxng.container`, SearXNG `settings.yml`

**Problem**: Pasta networking strips X-Forwarded-For → SearXNG sees all requests from gateway IP → bot detection triggers.

**Solution**: Deploy Caddy reverse proxy on same Podman network as SearXNG.

**Step 1**: Create Caddy container:

```bash
# Deploy Caddy on same Podman network as SearXNG
podman run -d \
  --name omega-caddy \
  --network omega-searxng-net \
  -v /path/to/Caddyfile:/etc/caddy/Caddyfile:ro \
  -p 127.0.0.1:8017:80 \
  caddy:alpine
```

**Step 2**: Create Caddyfile:

```
# Caddyfile — SearXNG reverse proxy with X-Forwarded-For injection
:80 {
    reverse_proxy omega-searxng:8080
}
```

**Step 3**: Update SearXNG `settings.yml`:

```yaml
# data/searxng/config/settings.yml
server:
  use_forwarded_for: true
  image_proxy: false
```

**Step 4**: Update `omega-searxng.container`:

```ini
# Remove PublishPort (Caddy handles proxying)
# Add to omega-searxng-net network
Network=omega-searxng-net
# Remove: PublishPort=127.0.0.1:8017:8080
```

**Verification**:
```bash
# Test header injection
curl -s -H "X-Forwarded-For: 1.2.3.4" http://localhost:8017/search?q=test | head -5
# Should see bot detection bypass
```

---

## Phase A2: Core Infrastructure (11h — Sequential)

### GAP 3: CASArchiver Wiring + Circuit Breaker Fix (3h)

**Owner**: Ma'at/P3
**Files**: `src/omega/ingestion/pipeline.py`, `src/omega/archive/cas.py`

**Step 1**: Fix `IngestionCircuitBreaker.record_failure()` to accept error_type:

```python
# src/omega/ingestion/pipeline.py — lines 39-55
class IngestionCircuitBreaker:
    """Sovereign Circuit Breaker with error-type awareness.
    [M23] Failure Integrity — distinguishes transient (429) from persistent errors.
    """
    def __init__(self, fail_max: int = 5, reset_timeout: int = 300):
        self.breaker = pybreaker.CircuitBreaker(fail_max=fail_max, reset_timeout=reset_timeout)
        self.consecutive_failures = 0
        self._transient_failures = 0  # 429/503 — retry, don't trip

    def can_proceed(self) -> bool:
        return self.breaker.current_state != "open"

    def record_success(self):
        self.consecutive_failures = 0
        self._transient_failures = 0

    def record_failure(self, error: Exception, error_type: str = "persistent"):
        """Record failure with type classification.
        Args:
            error: The exception that occurred.
            error_type: "transient" (429, 503) or "persistent" (400, DNS).
        """
        if error_type == "transient":
            self._transient_failures += 1
            logger.debug("Transient failure (%d): %s", self._transient_failures, error)
            return  # Don't trip breaker on transient errors

        self.consecutive_failures += 1
        if self.consecutive_failures >= self.breaker.fail_max:
            logger.warning("Circuit breaker tripping after %d persistent failures", self.consecutive_failures)

    @staticmethod
    def classify_error(error: Exception) -> str:
        """Classify error as transient or persistent."""
        error_name = type(error).__name__
        if error_name in ("TransportError", "TimeoutError", "ConnectionError"):
            msg = str(error).lower()
            if "429" in msg or "too many" in msg or "503" in msg:
                return "transient"
        if error_name in ("SchemaError", "SovereigntyError", "BudgetExceededError"):
            return "persistent"
        return "persistent"  # Safe default

    def call(self, func, *args, **kwargs):
        return self.breaker.call(func, *args, **kwargs)
```

**Step 2**: Wire CASArchiver dedup gate into `IngestionPipeline.run_source()`:

```python
# src/omega/ingestion/pipeline.py — after line 206
raw_content = t3_res.content.encode('utf-8')

# ── CAS Deduplication Gate ──
# [heritage: quake-1996] Zone Memory — store once, reference by hash
content_hash = hashlib.sha256(raw_content).hexdigest()
if await self.cas.exists(content_hash):
    logger.info("Dedup: skipping %s (already ingested)", content_hash[:12])
    return None  # Already ingested — skip
await self.cas.store(raw_content)

text = t3_res.content
```

**Verification**:
```bash
# Re-ingest same URL — should show "Dedup: skipping" log
python -m omega.ingestion.pipeline --url "https://example.com"
```

---

### GAP 1: TranscriptFetcher Hardening (4h)

**Owner**: Kali/P3
**Files**: `src/omega/workers/youtube_worker.py:265-310`, `src/omega_youtube_research/errors.py`

**Prerequisite**: `pip install youtube-transcript-api>=1.2.4`

**Step 1**: Add `EmptyTranscriptError` to errors module:

```python
# src/omega_youtube_research/errors.py
class EmptyTranscriptError(Exception):
    """Raised when transcript is empty or contains only whitespace."""
    pass
```

**Step 2**: Rewrite `TranscriptFetcher` class:

```python
# src/omega/workers/youtube_worker.py — lines 265-310
# ── Transcript Fetcher (Hardened) ───────────────────────────────────────────
# [heritage: odysseus-2025] Rate limiting with exponential backoff + jitter
# [M23] Failure Integrity — no soft failures on transcript fetch

import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_random,
    retry_if_exception_type,
    RetryError,
)

class TranscriptFetcher:
    """Hardened YouTube transcript fetcher with retry, circuit breaker, and proxy.

    Failure modes handled:
    1. Volume throttling → exponential backoff with jitter (tenacity)
    2. IP reputation blocking → proxy rotation (WebshareProxyConfig)
    3. Persistent bans → circuit breaker fail-fast (pybreaker via IngestionCircuitBreaker)
    """

    def __init__(
        self,
        request_delay: float = 2.0,
        max_retries: int = 3,
        proxy_config: Optional[Any] = None,
        circuit_breaker: Optional[Any] = None,
    ):
        self._request_delay = request_delay
        self._last_request = 0.0
        self._max_retries = max_retries
        self._proxy_config = proxy_config
        self._circuit_breaker = circuit_breaker
        self._fetch_lock = anyio.Lock()  # Serialize fetches

    async def fetch(self, video_id: str) -> Optional[str]:
        """Fetch transcript text for a video ID with hardened retry logic."""
        async with self._fetch_lock:
            # Rate limiting
            now = time.monotonic()
            since_last = now - self._last_request
            if since_last < self._request_delay:
                await anyio.sleep(self._request_delay - since_last)
            self._last_request = time.monotonic()

            def _fetch_with_retry() -> Optional[str]:
                return self._fetch_sync(video_id)

            try:
                if self._circuit_breaker and self._circuit_breaker.can_proceed():
                    return await anyio.to_thread.run_sync(
                        self._circuit_breaker.call, _fetch_with_retry
                    )
                elif not self._circuit_breaker:
                    return await anyio.to_thread.run_sync(_fetch_with_retry)
                else:
                    logger.warning("Circuit breaker open — skipping %s", video_id)
                    return None
            except Exception as e:
                logger.error("Transcript fetch failed for %s: %s", video_id, e)
                return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=60) + wait_random(0, 2),
        retry=retry_if_exception_type((RequestBlocked, IpBlocked)),
        reraise=True,
    )
    def _fetch_sync(self, video_id: str) -> Optional[str]:
        """Synchronous fetch with tenacity retry — runs in thread pool."""
        try:
            from youtube_transcript_api import (
                YouTubeTranscriptApi,
                TranscriptsDisabled,
                NoTranscriptFound,
                VideoUnavailable,
            )
            from youtube_transcript_api._errors import RequestBlocked, IpBlocked

            try:
                if self._proxy_config:
                    ytt_api = YouTubeTranscriptApi(proxy_config=self._proxy_config)
                else:
                    ytt_api = YouTubeTranscriptApi()
                transcript = ytt_api.fetch(video_id)
            except (RequestBlocked, IpBlocked):
                raise  # Let tenacity retry
            except VideoUnavailable:
                logger.warning("Video %s unavailable — not retrying", video_id)
                return None
            except (TranscriptsDisabled, NoTranscriptFound):
                logger.info("No transcript for %s — not retrying", video_id)
                return None

            if transcript and transcript.snippets:
                return " ".join(
                    s.text.strip() for s in transcript.snippets if s.text.strip()
                )
            return None

        except RetryError:
            logger.error("Transcript fetch exhausted retries for %s", video_id)
            return None
```

**Step 3**: Add config to `config/youtube_worker.yaml`:

```yaml
transcript_fetcher:
  request_delay: 2.0
  max_retries: 3
  circuit_breaker:
    fail_max: 5
    reset_timeout: 300  # 5 minutes
  proxy:
    enabled: false
    # username: "env:WEBSHARE_USERNAME"
    # password: "env:WEBSHARE_PASSWORD"
    # retries_when_blocked: 3
```

**Verification**:
```bash
# Test retry on 429
python -c "from youtube_transcript_api import YouTubeTranscriptApi; api = YouTubeTranscriptApi(); print(api.fetch('test_video'))"
# Should show retry logs on 429
```

---

### GAP 2: RAG Synthesis + Chunking (4h)

**Owner**: Jem/Lilith
**Files**: `src/omega/workers/youtube_worker.py:380-510`, `omega_youtube_research/module.py`

**Step 1**: Add `TranscriptChunker` class:

```python
# src/omega/workers/youtube_worker.py — after line 310
@dataclass
class TranscriptChunk:
    """A single chunk of a YouTube transcript with provenance metadata."""
    text: str
    video_id: str
    chunk_index: int
    char_start: int
    char_end: int
    token_estimate: int

class TranscriptChunker:
    """Splits transcripts into 512-token sentence-boundary chunks.

    Uses recursive splitting: paragraph → sentence → word boundaries.
    No overlap per 2026 evidence (arXiv Jan 2026 systematic analysis).
    """

    def __init__(
        self,
        max_tokens: int = 512,
        chars_per_token: float = 4.0,
        separators: Optional[List[str]] = None,
    ):
        self._max_chars = int(max_tokens * chars_per_token)
        self._separators = separators or [". ", "! ", "? ", "\n\n", "\n", " "]

    def chunk(self, transcript: str, video_id: str) -> List[TranscriptChunk]:
        """Split transcript into sentence-boundary chunks with metadata."""
        if not transcript or not transcript.strip():
            return []

        chunks: List[TranscriptChunk] = []
        remaining = transcript.strip()
        char_offset = 0
        chunk_index = 0

        while remaining:
            split_pos = self._find_split_point(remaining)
            chunk_text = remaining[:split_pos].strip()

            if chunk_text:
                token_est = len(chunk_text) // 4
                chunks.append(TranscriptChunk(
                    text=chunk_text,
                    video_id=video_id,
                    chunk_index=chunk_index,
                    char_start=char_offset,
                    char_end=char_offset + len(chunk_text),
                    token_estimate=token_est,
                ))
                chunk_index += 1

            char_offset += split_pos
            remaining = remaining[split_pos:].lstrip()

        return chunks

    def _find_split_point(self, text: str) -> int:
        """Find best sentence-boundary split point within max_chars."""
        if len(text) <= self._max_chars:
            return len(text)

        for sep in self._separators:
            last_sep = text.rfind(sep, 0, self._max_chars)
            if last_sep > 0:
                return last_sep + len(sep)

        last_space = text.rfind(" ", 0, self._max_chars)
        if last_space > 0:
            return last_space
        return self._max_chars
```

**Step 2**: Add `synthesize_rag()` to `CrossVideoSynthesizer`:

```python
# src/omega/workers/youtube_worker.py — CrossVideoSynthesizer class
async def synthesize_rag(
    self,
    topic: str,
    video_results: List[Dict[str, Any]],
    memory_search_fn: Optional[callable] = None,
    model_name: str = "qwen3-1.7b",
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> Optional[SynthesisResult]:
    """RAG-enhanced synthesis: retrieve relevant chunks, then synthesize."""
    if not video_results:
        return None

    # 1. Retrieve relevant chunks via memory search
    retrieved_chunks = []
    if memory_search_fn:
        try:
            results = await memory_search_fn(
                query=topic,
                entity_name="youtube_research",
                limit=10,
            )
            retrieved_chunks = results
        except Exception as e:
            logger.warning("RAG retrieval failed, falling back to metadata: %s", e)

    # 2. Build context from retrieved chunks
    context_parts = []
    for chunk in retrieved_chunks[:5]:
        text = chunk.get("text", chunk.get("content", ""))
        video_id = chunk.get("video_id", "unknown")
        if text:
            context_parts.append(f"[{video_id}] {text[:500]}")

    # 3. Build synthesis prompt with RAG context
    rag_context = "\n\n".join(context_parts) if context_parts else ""
    prompt = self._build_synthesis_prompt(topic, video_results, rag_context)

    # 4. Run local model inference (reuse existing synthesize() logic)
    return await self.synthesize(topic, video_results, model_name, temperature, max_tokens)
```

**Verification**:
```bash
# Test chunking
python -c "from omega.workers.youtube_worker import TranscriptChunker; c = TranscriptChunker(); print(len(c.chunk('test transcript ' * 100, 'test_video')))"
# Should return ~10 chunks
```

---

## Phase A3: Specialist (6h — Parallel with Phase A2)

### GAP 4: AGB-0 Embedding Provider (6h)

**Owner**: Roc Racoon + Researcher
**Files**: `src/omega/memory/agb_embedder.py` (NEW), `src/omega/memory/embeddings.py`

**CRITICAL**: Must be in `src/omega/memory/` — NOT `src/omega_agb/` (M2 Engine-Stack Firewall)

**Step 1**: Create `src/omega/memory/agb_embedder.py`:

```python
# src/omega/memory/agb_embedder.py
# [heritage: pranaydeeps-2022] Ancient Greek BERT embeddings
# [M7] Local-First — ONNX inference, no cloud dependency

from typing import List, Optional
import anyio
from omega.memory.embeddings import IEmbeddingProvider

class AGBEmbeddingProvider(IEmbeddingProvider):
    """Ancient Greek BERT embedding provider using ONNX Runtime.

    Model: Paulanerus/AncientGreekVariantSBERT-ONNX
    - 768-dim, MIT license, 4 downloads
    - Matches existing GemmaGGUF dimension (768)
    - Lazy-loaded on-demand for rare language support
    """

    def __init__(self, model_path: Optional[str] = None):
        self._model_path = model_path or "Paulanerus/AncientGreekVariantSBERT-ONNX"
        self._session = None
        self._tokenizer = None
        self._dimension = 768

    async def _ensure_loaded(self):
        """Lazy-load ONNX model in thread pool."""
        if self._session is not None:
            return

        def _load():
            import onnxruntime as ort
            from transformers import AutoTokenizer
            self._session = ort.InferenceSession(self._model_path)
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_path)

        await anyio.to_thread.run_sync(_load)

    async def get_embedding(self, text: str) -> List[float]:
        """Embed text using Ancient Greek BERT ONNX model."""
        await self._ensure_loaded()

        def _embed():
            inputs = self._tokenizer(text, return_tensors="np", padding=True, truncation=True)
            outputs = self._session.run(None, dict(inputs))
            return outputs[0][0].tolist()  # [CLS] token embedding

        return await anyio.to_thread.run_sync(_embed)

    @property
    def dimension(self) -> int:
        return self._dimension


class AncientGreekDetector:
    """Detect Ancient Greek text via Unicode block analysis.

    Greek Unicode blocks:
    - U+0370-U+03FF (Greek and Coptic)
    - U+1F00-U+1FFF (Greek Extended)
    """

    GREEK_BLOCKS = [
        (0x0370, 0x03FF),  # Greek and Coptic
        (0x1F00, 0x1FFF),  # Greek Extended
    ]

    @classmethod
    def detect(cls, text: str, threshold: float = 0.3) -> bool:
        """Return True if text is predominantly Ancient Greek."""
        if not text:
            return False

        greek_chars = sum(
            1 for char in text
            if any(start <= ord(char) <= end for start, end in cls.GREEK_BLOCKS)
        )
        total_chars = len(text.strip())
        return (greek_chars / total_chars) >= threshold if total_chars > 0 else False
```

**Step 2**: Wire into `EmbeddingManager`:

```python
# src/omega/memory/embeddings.py — add to _providers list
from omega.memory.agb_embedder import AGBEmbeddingProvider, AncientGreekDetector

class EmbeddingManager:
    def __init__(self, ...):
        self._providers = [
            AGBEmbeddingProvider(),  # Highest priority for Ancient Greek
            GemmaGGUFEmbeddingProvider(),
            OllamaEmbeddingProvider(),
            LocalGGUFEmbeddingProvider(),
            StaticEmbeddingProvider(),
            SovereignFallbackEmbedding(),
        ]
```

**Verification**:
```bash
# Test detection
python -c "from omega.memory.agb_embedder import AncientGreekDetector; print(AncientGreekDetector.detect('λόγος'))"
# Should return True
```

---

## Phase A4: Validation (4h)

### GAP 8: Contract Tests (4h)

**Owner**: Verity
**Files**: `tests/test_transcript_fetcher_hardened.py` (NEW), `tests/test_cas_archiver.py` (NEW), `tests/test_ingestion_circuit_breaker.py` (NEW)

**Test 1**: TranscriptFetcher retry/circuit breaker:

```python
# tests/test_transcript_fetcher_hardened.py
class TestTranscriptFetcherRetry:
    @pytest.mark.asyncio
    async def test_retry_on_request_blocked(self):
        """Tenacity retries RequestBlocked up to max_retries times."""
        with mock.patch("youtube_transcript_api.YouTubeTranscriptApi") as mock_api:
            mock_api.side_effect = RequestBlocked("test")
            fetcher = TranscriptFetcher(max_retries=2)
            result = await fetcher.fetch("test_video")
            assert result is None
            assert mock_api.call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_transcripts_disabled(self):
        """TranscriptsDisabled is NOT retried."""
        with mock.patch("youtube_transcript_api.YouTubeTranscriptApi") as mock_api:
            mock_api.side_effect = TranscriptsDisabled("test")
            fetcher = TranscriptFetcher()
            result = await fetcher.fetch("test_video")
            assert result is None
            assert mock_api.call_count == 1  # No retry

    @pytest.mark.asyncio
    async def test_success_after_transient_failure(self):
        """Success on 3rd attempt after 2 RequestBlocked failures."""
        mock_instance = mock.MagicMock()
        mock_instance.fetch.side_effect = [
            RequestBlocked("attempt 1"),
            RequestBlocked("attempt 2"),
            mock.MagicMock(snippets=[mock.MagicMock(text="hello world")]),
        ]
        with mock.patch("youtube_transcript_api.YouTubeTranscriptApi", return_value=mock_instance):
            fetcher = TranscriptFetcher(max_retries=3)
            result = await fetcher.fetch("test_video")
            assert result == "hello world"

class TestTranscriptFetcherContract:
    def test_fetch_returns_optional_str(self):
        """M21: fetch() return type is Optional[str]."""
        fetcher = TranscriptFetcher()
        import inspect
        sig = inspect.signature(fetcher.fetch)
        assert sig.return_annotation == Optional[str]
```

**Test 2**: CASArchiver dedup:

```python
# tests/test_cas_archiver.py
class TestCASArchiverDedup:
    @pytest.mark.asyncio
    async def test_store_returns_hash(self):
        """store() returns SHA-256 hash of content."""
        cas = CASArchiver()
        content = b"test content for dedup"
        hash1 = await cas.store(content)
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 hex

    @pytest.mark.asyncio
    async def test_exists_returns_true_for_stored(self):
        """exists() returns True for stored content."""
        cas = CASArchiver()
        content = b"test dedup check"
        hash1 = await cas.store(content)
        assert await cas.exists(hash1) is True

    @pytest.mark.asyncio
    async def test_dedup_same_content(self):
        """Same content stored twice produces same hash."""
        cas = CASArchiver()
        content = b"dedup test content"
        hash1 = await cas.store(content)
        hash2 = await cas.store(content)
        assert hash1 == hash2
```

**Test 3**: Circuit breaker 429 handling:

```python
# tests/test_ingestion_circuit_breaker.py
class TestIngestionCircuitBreaker:
    def test_transient_failure_does_not_trip_breaker(self):
        """429 (transient) does NOT trip circuit breaker."""
        cb = IngestionCircuitBreaker(fail_max=3)
        error = TransportError("429 Too Many Requests")
        cb.record_failure(error, error_type="transient")
        assert cb.consecutive_failures == 0  # Not counted
        assert cb.can_proceed() is True

    def test_persistent_failure_trips_breaker(self):
        """Connection failure (persistent) trips breaker."""
        cb = IngestionCircuitBreaker(fail_max=3)
        error = ConnectionError("Connection refused")
        for _ in range(3):
            cb.record_failure(error, error_type="persistent")
        assert cb.can_proceed() is False  # Tripped

    def test_classify_error(self):
        """classify_error returns correct type."""
        assert IngestionCircuitBreaker.classify_error(TransportError("429")) == "transient"
        assert IngestionCircuitBreaker.classify_error(ConnectionError("refused")) == "persistent"
```

**Verification**:
```bash
pytest tests/test_transcript_fetcher_hardened.py -v
pytest tests/test_cas_archiver.py -v
pytest tests/test_ingestion_circuit_breaker.py -v
```

---

## Quick Reference: File Changes

| File | Phase | Change |
|------|-------|--------|
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | 1 | Fix 3 drift items |
| `src/omega/memory/vector_adapters.py` | 1 | Add payload indexes |
| `docs/research/omega-searxng.container` | 1 | Caddy proxy config |
| `data/searxng/config/settings.yml` | 1 | `use_forwarded_for: true` |
| `src/omega/ingestion/pipeline.py` | 2 | CAS dedup + CB fix |
| `src/omega/workers/youtube_worker.py:265-310` | 2 | TranscriptFetcher hardening |
| `src/omega/workers/youtube_worker.py:380-510` | 2 | TranscriptChunker + RAG |
| `src/omega_youtube_research/errors.py` | 2 | EmptyTranscriptError |
| `config/youtube_worker.yaml` | 2 | Proxy + CB config |
| `src/omega/memory/agb_embedder.py` | 3 | NEW: AGB provider |
| `src/omega/memory/embeddings.py` | 3 | Wire AGB provider |
| `tests/test_transcript_fetcher_hardened.py` | 4 | NEW: M21 tests |
| `tests/test_cas_archiver.py` | 4 | NEW: M21 tests |
| `tests/test_ingestion_circuit_breaker.py` | 4 | NEW: M21 tests |

---

## Dependency Version Matrix

| Package | Installed | Required | Status |
|---------|-----------|----------|--------|
| tenacity | 9.1.4 | ≥8.0 | ✅ Ready |
| pybreaker | 1.4.1 | ≥1.0 | ⚠️ Sync only |
| httpx2 | 2.5.0 | ≥2.0 | ✅ Ready |
| fastmcp | 3.4.4 | ≥1.8 | ✅ Dual-transport |
| qdrant-client | 1.18.0 | ≥1.7 | ✅ Payload indexes |
| onnxruntime | 1.27.0 | ≥1.15 | ✅ BERT ONNX |
| youtube-transcript-api | ❌ NOT INSTALLED | ≥1.2.4 | ❌ Must install |
| tiktoken | ❌ NOT INSTALLED | ≥0.5 | Optional |

---

---

## Workstream B: Sovereignty Gaps (from Jem MaKaLi Deep Research v1.2.0)

**Source**: `docs/research/R_JEM_MAKALI_DEEP_RESEARCH_20260712.md` (544 lines, Exa/Firecrawl Tier 3/4)
**Total Effort**: ~60h across 5 domains
**Execution Order**: S2 → S3 → S5 → S1 → S4 (per Jem's priority matrix)

### Phase B1: Sprint 1 — Cognitive Acceleration (24h)

#### S2: Sovereign Eval Pipeline (8h)

**Owner**: Lilith/P6+P10
**Priority**: P1
**Status**: 🟡 READY (Jem corrected: must calibrate judge)

**Key corrections from Jem**:
- ❌ Uncalibrated 7B judges are overconfident by 0.18 ECE in the 0.8-0.95 band
- ✅ Isotonic regression reduces ECE from 0.18 → 0.06 (single sklearn import)
- Minimum viable judge: 7B Q4_K_M (4.7GB); Recommended: Qwen3:14b (8.4GB)

**Implementation**:
```python
# data/eval/golden_v1.jsonl — 100-150 seed cases
# Core: 40-60%, Edge: 20-30%, Adversarial: 10-20%
{"question": "...", "answer": "...", "contexts": [...], "ground_truth": "...", "tags": ["core"]}

# Makefile target
eval:
	@python -m omega.eval.runner --dataset data/eval/golden_v1.jsonl --judge mistral:7b
	@python -m omega.eval.check --thresholds config/eval/thresholds.yaml

# Calibration target (weekly)
eval-calibrate:
	@python -m omega.eval.calibrate --dataset data/eval/calibration_v1.jsonl --output config/eval/calibrated_model.pkl
```

**Thresholds**: Faithfulness ≥0.85, Answer Relevancy ≥0.80, Context Precision ≥0.75, Context Recall ≥0.80

**CI Gate**: `make eval` runs on every PR. Fails build if any threshold regresses by >0.05.

**Dependencies**: RAGAS v0.2+, sklearn (for isotonic regression). No new infrastructure.

**Files**:
| File | Change | Status |
|------|--------|--------|
| `src/omega/eval/runner.py` | NEW | 🟡 PENDING |
| `src/omega/eval/check.py` | NEW | 🟡 PENDING |
| `src/omega/eval/calibrate.py` | NEW | 🟡 PENDING |
| `data/eval/golden_v1.jsonl` | NEW | 🟡 PENDING |
| `config/eval/thresholds.yaml` | NEW | 🟡 PENDING |
| `Makefile` | Add `eval` and `eval-calibrate` targets | 🟡 PENDING |

---

#### S3: Tiny-Critic RAG Router (12h)

**Owner**: Lilith/P6
**Priority**: P1
**Status**: 🟡 READY (Jem confirmed feasible on 14Gi RAM)

**Key confirmation from Jem**:
- ✅ TF-IDF+SVM router: 0MB GPU RAM, 93.2% accuracy, <1ms classification
- ✅ 7B Q4_K_M (4.7GB) + router + Q8 KV cache → ~7-8GB total on 14Gi system
- ✅ 3-3.5GB headroom for context
- Tiny-Critic LoRA (1.7B, ~1GB) is optional upgrade path

**Implementation**:
```python
# src/omega/rag/router.py
# ── Adaptive RAG Classifier [heritage: tiny-critic-rag 2026]
class RAGRouter:
    MODES = {"tfidf_svm", "tiny_critic", "llm"}
    
    async def classify(self, query: str) -> Literal["simple", "complex"]:
        # TF-IDF+SVM: ~50MB, <1ms, 93.2% accuracy
        features = self.vectorizer.transform([query])
        return "complex" if self.classifier.predict(features)[0] else "simple"
```

**Files**:
| File | Change | Status |
|------|--------|--------|
| `src/omega/rag/__init__.py` | NEW | 🟡 PENDING |
| `src/omega/rag/router.py` | NEW | 🟡 PENDING |
| `src/omega/rag/simple_rag.py` | NEW | 🟡 PENDING |
| `src/omega/rag/iterative_rag.py` | NEW | 🟡 PENDING |
| `tests/test_rag_router.py` | NEW | 🟡 PENDING |

---

#### P1-3: Hivemind Event Bus (4h)

**Owner**: Lilith/P9
**Priority**: P1
**Status**: 🟡 READY

**Implementation**: Replace file-based workspace locks with Redis Pub/Sub ephemeral bus.
- Pub/Sub channels: `hivemind:awareness`, `hivemind:locks`, `hivemind:heartbeat`
- File-based fallback during transition

**Files**:
| File | Change | Status |
|------|--------|--------|
| `mcp_servers/omega_hub/hivemind_redis.py` | NEW | 🟡 PENDING |
| `mcp_servers/omega_hub/tools.py` | Add Redis Pub/Sub client | 🟡 PENDING |

---

### Phase B2: Sprint 2 — Sovereign Refinement (40h)

#### S5: Redis Streams Hivemind (20h)

**Owner**: Lilith/P9
**Priority**: P2
**Status**: 🟡 READY (Jem corrected: Streams, NOT Pub/Sub)

**Key corrections from Jem**:
- ❌ Pub/Sub drops messages under load — cannot be used for task-critical coordination
- ✅ Redis Streams + Consumer Groups = exactly-once semantics, crash recovery via XCLAIM
- Temporal for production-grade complex DAGs (optional upgrade)

**Stream Architecture**:
```
plan:{agent_id}:stream    — Task decomposition plans
execute:{agent_id}:stream — Tool call execution
observe:{agent_id}:stream — State observation
coordination:notifications — Pub/Sub ONLY for ephemeral heartbeats
```

**Files**:
| File | Change | Status |
|------|--------|--------|
| `src/omega/hivemind/streams.py` | NEW | 🟡 PENDING |
| `mcp_servers/omega_hub/hivemind_v2.py` | NEW | 🟡 PENDING |
| `tests/test_hivemind_streams.py` | NEW | 🟡 PENDING |

---

#### S1: Sovereign Export Bundle (4h)

**Owner**: Lilith/P7
**Priority**: P2
**Status**: 🟡 READY (Jem corrected: ZIP+JSON, NOT Parquet)

**Key corrections from Jem**:
- ❌ Parquet is ML-only — incompatible with Soul Protocol v0.4.0, ALF v1.0.0-rc.1, PAM v1.0
- ✅ ZIP+JSON `.omega` bundle is the 2026 consensus across all standards

**Bundle Format**:
```
entity_name.omega
├── manifest.json           # schema_version, export_id, timestamp, SHA-256 checksums
├── identity.json           # DID (did:omega:), entity name, persona, slot
├── soul.yaml               # Preserved verbatim
├── memory/
│   ├── core.jsonl          # Stable identity-level facts
│   ├── episodic.jsonl      # Conversation history (significance-gated)
│   ├── semantic.jsonl      # Extracted knowledge with confidence scores
│   ├── procedural.jsonl    # Learned skills and patterns
│   └── graph.jsonl         # Entity relationships
├── embeddings.json         # Optional — regenerated on import
├── evolution.jsonl         # Append-only soul mutation history
└── trust_chain/            # Optional Ed25519 signatures
    ├── chain.json
    └── entry_NNN.json
```

**CLI**: `omega bundle export <entity> [--output <path>]` and `omega bundle import <path>`

**Files**:
| File | Change | Status |
|------|--------|--------|
| `src/omega/export/omega_bundle.py` | NEW | 🟡 PENDING |
| `src/omega/cli/oracle_cli.py` | Add `bundle` subcommand | 🟡 PENDING |
| `tests/test_omega_bundle.py` | NEW | 🟡 PENDING |

---

#### S4: Qdrant+SQLite Hybrid Knowledge Graph (16h)

**Owner**: Lilith/P7
**Priority**: P2
**Status**: 🟡 READY (Jem confirmed: start with SQLite)

**Key confirmation from Jem**:
- ✅ Qdrant v1.12+ prefetch API enables native fusion without separate Postgres hop
- ✅ Start with Qdrant + SQLite for entity relationships; PostgreSQL at scale
- ✅ Recursive CTEs enable graph traversal without external graph database

**Schema**:
```sql
-- library.entities: knowledge graph nodes
CREATE TABLE library.entities (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,  -- 'person', 'concept', 'document'
    description TEXT,
    metadata JSONB,
    embedding_id UUID REFERENCES qdrant_points(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- library.relationships: knowledge graph edges
CREATE TABLE library.relationships (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES library.entities(id),
    target_id UUID REFERENCES library.entities(id),
    relationship_type TEXT NOT NULL,  -- 'derived_from', 'contradicts', 'supports'
    confidence FLOAT,
    provenance TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Files**:
| File | Change | Status |
|------|--------|--------|
| `src/omega/knowledge/__init__.py` | NEW | 🟡 PENDING |
| `src/omega/knowledge/graph_store.py` | NEW | 🟡 PENDING |
| `src/omega/knowledge/hybrid_query.py` | NEW | 🟡 PENDING |
| `tests/test_knowledge_graph.py` | NEW | 🟡 PENDING |

---

## Combined Hydration Checklist

```bash
# ═══════════════════════════════════════════════
# WORKSTREAM A — Infrastructure (25h total)
# ═══════════════════════════════════════════════

# 1. Read research reports
cat docs/research/R_RESEARCHER_DEEP_DIVE_20260712.md
cat docs/research/R_JEM_KNOWLEDGE_GAP_RESEARCH_20260712.md
cat docs/research/R_JEM_MAKALI_DEEP_RESEARCH_20260712.md  # NEW

# 2. Verify baseline
make test  # 1189 must pass

# 3. Install missing dependencies
pip install youtube-transcript-api>=1.2.4

# 4. Execute Phase A1 (Foundation, 3.5h)
# GAP 9: Fix Ark Blueprint drift ✅ DONE (v3.6)
# GAP 6: Add Qdrant payload indexes
# GAP 7: Deploy Caddy reverse proxy

# 5. Execute Phase A2 (Core, 11h)
# GAP 3: Fix IngestionCircuitBreaker + wire CAS dedup
# GAP 1: Harden TranscriptFetcher with tenacity + pybreaker
# GAP 2: Implement TranscriptChunker + synthesize_rag()

# 6. Execute Phase A3 (Specialist, 6h)
# GAP 4: Create src/omega/memory/agb_embedder.py

# 7. Execute Phase A4 (Validation, 4h)
# GAP 8: Write contract tests for all new code

# 8. Final verification
make test
make temple-grade

# ═══════════════════════════════════════════════
# WORKSTREAM B — Sovereignty (60h total)
# ═══════════════════════════════════════════════

# 9. Phase B1 — Sprint 1 (24h)
# S2: make eval pipeline — RAGAS + calibrated judge
# S3: Tiny-Critic RAG Router — TF-IDF+SVM in src/omega/rag/
# P1-3: Hivemind Event Bus — Redis Pub/Sub for workspace locks

# 10. Phase B2 — Sprint 2 (40h)
# S5: Redis Streams Hivemind — Consumer groups, PEL recovery
# S1: .omega export bundle — ZIP+JSON CLI
# S4: Qdrant+SQLite hybrid knowledge graph

# 11. Final verification
make test
make temple-grade
make sovereignty  # Must show ≥80% local in CI
```

```bash
# 1. Read research reports
cat docs/research/R_RESEARCHER_DEEP_DIVE_20260712.md
cat docs/research/R_JEM_KNOWLEDGE_GAP_RESEARCH_20260712.md

# 2. Verify baseline
make test  # 1189 must pass

# 3. Install missing dependency
pip install youtube-transcript-api>=1.2.4

# 4. Execute Phase 1 (Foundation)
# GAP 9: Fix Ark Blueprint drift
# GAP 6: Add Qdrant payload indexes
# GAP 7: Deploy Caddy reverse proxy

# 5. Execute Phase 2 (Core)
# GAP 3: Fix IngestionCircuitBreaker + wire CAS dedup
# GAP 1: Harden TranscriptFetcher with tenacity + pybreaker
# GAP 2: Implement TranscriptChunker + synthesize_rag()

# 6. Execute Phase 3 (Specialist)
# GAP 4: Create src/omega/memory/agb_embedder.py

# 7. Execute Phase 4 (Validation)
# GAP 8: Write contract tests for all new code

# 8. Final verification
make test  # Must still pass
make temple-grade  # T1-T14 must pass
```

---

*🔱 OMEGA ⬡ DETAILED-NEXT-STEPS ⬡ v2.0.0 ⬡ 85H-COMBINED-EXECUTION-PLAN ⬡ 9-INFRASTRUCTURE-GAPS + 5-SOVEREIGNTY-GAPS*

*Research sources: JEM-2 (644 lines) + Researcher Deep-Dive (1421 lines) + Jem MaKaLi Deep Research (544 lines via Exa/Firecrawl)*
