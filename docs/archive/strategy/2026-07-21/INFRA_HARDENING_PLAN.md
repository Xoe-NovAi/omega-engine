# 🔱 Omega Engine — Infrastructure Hardening & YouTube Research Sprint
**AP Token**: `AP-INFRA-HARDENING-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_infra_hardening ⬡ ACTIVE

**Date**: 2026-07-12
**Status**: PLANNING — Ready for execution
**Deprioritized**: Web Claude Upload (moved to bottom of queue)
**Carmack Tier 0 Applied**: 2026-07-14 — Foundation fixes prioritized before infra hardening

---

## §0 Executive Summary

**Objective**: Harden the sovereign infrastructure stack — YouTube worker production readiness, ingestion pipeline robustness, local embeddings (AGB-0/Krikri), MCP server Streamable HTTP migration, and vector store optimization.

**Current State**: 
- 1189 tests passing
- Temple-Grade T1-T14 PASS
- SearXNG MCP on Streamable HTTP :8018 ✅
- YouTube worker exists but needs hardening (adaptive rate limiting, RAG synthesis, circuit breaker)
- Embedding chain: Gemma 300M (primary) → Ollama → MiniLM → Static → Fallback
- Omega Hub MCP on SSE :8016 (needs Streamable HTTP migration)

**Carmack Tier 0 Prerequisite**: Before infra hardening, complete Tier 0 Ship-It Bar (80h):
1. F821 undefined-name fixes (15 min)
2. Bare `except Exception:` elimination (90 min)
3. Centralized logging with structlog + AnyIO (4h)
4. Config validation with Pydantic OmegaConfig (7h)
5. Qdrant → sqlite-vec dual-write verification (3h)
6. Single CI workflow + stress tests (3h)

---

## §1 YouTube Worker Production Hardening (JEM-1)

### 1.1 Current Gaps (from `R_YOUTUBE_RESEARCH_ENHANCEMENT_PLAN.md`)

| Component | Current | Target | Effort |
|-----------|---------|--------|--------|
| **TranscriptFetcher** | Fixed 2s delay | Adaptive backoff + jitter + circuit breaker + Webshare proxy | 4h |
| **CrossVideoSynthesizer** | Title-based fallback | RAG over Qdrant chunks (`retrieve_chunks()`) | 6h |
| **YouTubeResearchModule** | No `retrieve_chunks()` | Add method for topic + source_id filtered retrieval | 2h |
| **Queue resilience** | Basic Redis list | Priority queue + dead-letter + retry count | 3h |
| **SearXNG engines** | youtube only | youtube_noapi, inv, duckduckgo, brave | 1h |
| **Adversarial tests** | 0 | 5 minimum (429, empty transcript, partial playlist, contradiction, pause/resume) | 4h |

### 1.2 Implementation Plan

#### Phase 1A: TranscriptFetcher Hardening (4h)
```python
# src/omega/workers/youtube_worker.py — TranscriptFetcher class
# Add:
- Circuit breaker: 5 consecutive 429s → 5min pause
- Exponential backoff with jitter: 2^attempt + random(0,1)
- Webshare proxy rotation (optional, env-configurable)
- Empty transcript detection (IP throttling signal)
- Retry on VideoUnavailable, NoTranscriptFound, TranscriptsDisabled
```

#### Phase 1B: RAG Synthesis (6h)
```python
# src/omega/workers/youtube_worker.py — CrossVideoSynthesizer
# Add synthesize_rag() method:
async def synthesize_rag(self, topic: str, video_results: List[Dict], ...):
    # 1. For each video, call YouTubeResearchModule.retrieve_chunks()
    # 2. Aggregate chunks, filter by min_score (0.65)
    # 3. Build context with citations [1], [2]...
    # 4. Local model inference (qwen3-1.7b via ResourceGuard)
    # 5. Return structured SynthesisResult with source_urls
```

```python
# omega_youtube_research/module.py — YouTubeResearchModule
# Add retrieve_chunks() method:
async def retrieve_chunks(self, query: str, source_ids: List[str], k: int = 10, min_score: float = 0.65):
    # 1. Embed query via EmbeddingManager
    # 2. Search Qdrant filtered by source_id IN (...)
    # 3. Return chunks with metadata (video_id, timestamp, title, score)
```

#### Phase 1C: Queue & Config (3h)
```yaml
# config/youtube_worker.yaml — Add:
redis:
  priority_queues: true
  dead_letter_queue: "youtube_dlq"
  max_retries: 3
  retry_backoff_base: 2

searxng:
  video_engines: "youtube_noapi,inv,duckduckgo,brave"
  fallback_engines: "duckduckgo,brave,google"

proxy:
  # Optional Webshare residential
  # username: "env:WEBSHARE_USERNAME"
  # password: "env:WEBSHARE_PASSWORD"
  # retries_when_blocked: 3
```

#### Phase 1D: Adversarial Tests (4h)
```python
# tests/test_youtube_worker_adversarial.py
async def test_transcript_fetch_429_backoff()
async def test_empty_transcript_detection()
async def test_playlist_expansion_partial_failure()
async def test_synthesis_contradiction_detection()
async def test_worker_pause_resume_coordinator()
```

### 1.3 Dependencies
- SearXNG container healthy on :8017 ✅
- Qdrant running on :6333 ✅
- Redis on :6379 ✅
- Local model qwen3-1.7b available in LM Studio/Ollama

---

## §2 Ingestion Pipeline Robustness

### 2.1 Current Architecture
```
Raw Data → SovereignSieve (PII Mask) → SovereignSigner (HMAC) → IngestedDocument
    ↓
SovereignIngestionCoordinator → Raw Anchor (USM) + SCA Anchor (USM) → Vector Store
```

### 2.2 Gaps & Fixes

| Gap | Fix | Effort |
|-----|-----|--------|
| **No circuit breaker on external fetch** | Wrap `SearXNG`/`Firecrawl`/`ArXiv` calls in circuit breaker | 2h |
| **No idempotency key** | Add `content_hash` deduplication at coordinator level | 1h |
| **No streaming for large docs** | Chunked ingestion for >100KB documents | 3h |
| **PII masker not wired for all providers** | Ensure `provider_name` passed correctly for local bypass | 1h |
| **No ingestion metrics** | Emit `ingest_total`, `ingest_duration`, `pii_masked_count` | 2h |

### 2.3 Implementation Plan

#### Phase 2A: Circuit Breaker Wrapper (2h)
```python
# src/omega/ingestion/circuit_breaker.py
class IngestionCircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=300):
        self.failures = defaultdict(int)
        self.last_failure = defaultdict(float)
        self.state = defaultdict(lambda: "closed")
    
    async def call(self, provider: str, coro):
        if self.state[provider] == "open":
            if time.time() - self.last_failure[provider] > self.recovery_timeout:
                self.state[provider] = "half-open"
            else:
                raise ProviderUnavailableError(f"Circuit open for {provider}")
        try:
            result = await coro
            self.failures[provider] = 0
            self.state[provider] = "closed"
            return result
        except Exception as e:
            self.failures[provider] += 1
            self.last_failure[provider] = time.time()
            if self.failures[provider] >= self.failure_threshold:
                self.state[provider] = "open"
            raise
```

#### Phase 2B: Idempotency & Deduplication (1h)
```python
# In SovereignIngestionCoordinator.process_and_anchor()
content_hash = hashlib.sha256(raw_content.encode()).hexdigest()[:16]
existing = await persistence.get_by_content_hash(content_hash)
if existing:
    return existing.source_id, existing.doc  # Skip re-ingestion
```

#### Phase 2C: Streaming Large Documents (3h)
```python
async def ingest_streaming(self, file_path: Path, chunk_size: int = 8192):
    """Process large files in chunks without loading fully into memory."""
    async with anyio.open_file(file_path, "rb") as f:
        while chunk := await f.read(chunk_size):
            # Process chunk through sieve → sign → persist
```

#### Phase 2D: Metrics Emission (2h)
```python
# Add to SovereignIngestionPipeline.ingest()
from omega.observability import record_metric
record_metric("ingest_total", 1, {"provider": provider_name, "status": "success"})
record_metric("ingest_duration_seconds", duration, {"provider": provider_name})
record_metric("pii_masked_count", len(token_map) if token_map else 0, {"provider": provider_name})
```

---

## §3 Local Embeddings & AGB-0 (Ancient Greek BERT / Krikri)

### 3.1 Current Embedding Chain (from `embeddings.py`)
```
1. GemmaGGUFEmbeddingProvider (768-dim, 300M, Q6_K, 249MB) — PRIMARY
2. OllamaEmbeddingProvider (768-dim, nomic-embed-text) — LOCAL FALLBACK
3. LocalGGUFEmbeddingProvider (384-dim, all-MiniLM-L6-v2) — FAST FALLBACK
4. StaticEmbeddingProvider (64-dim, potion-base-2M) — ZERO-COST FALLBACK
5. SovereignFallbackEmbeddingProvider (256-dim, hash) — LAST RESORT
```

### 3.2 AGB-0 Implementation Plan (from `REFINED_AGB_KRIKRI_STRATEGY.md`)

#### Phase 3A: Embedder Protocol & Interfaces (3h)
```python
# src/omega_agb/embedders.py
class IEmbedder(ABC):
    @abstractmethod
    async def embed(self, texts: List[str]) -> np.ndarray: ...
    @abstractmethod
    async def embed_query(self, query: str) -> np.ndarray: ...
    @property
    @abstractmethod
    def dimension(self) -> int: ...

class AGBLazyEmbedder(IEmbedder):
    """Lazy-loads AGB model on first use."""
    
class LocalONNXEmbedder(IEmbedder):
    """ONNX Runtime local inference for AGB/Krikri."""
    
class LMStudioEmbedder(IEmbedder):
    """LM Studio OpenAI-compatible endpoint for Krikri."""
    
class AncientGreekDetector:
    """Heuristic + fastText detector for Greek text routing."""
```

#### Phase 3B: Cloud Generator Routing (2h)
```python
# For training data generation only — OpenRouter free tier
# Routes: AGB synthetic data → OpenRouter (Gemma-4-31B) → Local ONNX distillation
```

#### Phase 3C: Krikri Local Preparation (4h)
```bash
# Target: Krikri-8B-Q4_K_M (4.7GB) for 5700U (12GB usable)
# Steps:
# 1. Download Krikri-8B GGUF from HF
# 2. Quantize to Q4_K_M via llama.cpp
# 3. Benchmark on 5700U (target: <8s/token)
# 4. Add to embedding chain as quality tier
```

#### Phase 3D: Progressive Activation (2h)
```python
# EmbeddingManager.add_provider(AGBLazyEmbedder())  # Phase 0
# EmbeddingManager.add_provider(LocalONNXEmbedder())  # Phase 1
# EmbeddingManager.add_provider(LMStudioEmbedder())   # Phase 2
# EmbeddingManager.add_provider(KrikriGGUFEmbedder()) # Phase 3 (when hardware ready)
```

### 3.3 Model Acquisition
```bash
# AGB (Ancient Greek BERT)
hf download minishlab/AGB-Embedding --local-dir /media/arcana-novai/omega_library/models/embeddings/AGB

# Krikri 8B (for local inference)
hf download nvidia/Krikri-8B --local-dir /media/arcana-novai/omega_library/models/gguf/Krikri-8B

# all-MiniLM-L6-v2 (already in chain)
# EmbeddingGemma 300M (already in chain as primary)
```

---

## §4 MCP Servers Hardening — Streamable HTTP Migration

### 4.1 Current State
| Server | Transport | Port | Status |
|--------|-----------|------|--------|
| SearXNG MCP | **Streamable HTTP** | 8018 | ✅ DONE |
| Omega Hub | SSE | 8016 | ⏳ PENDING |
| Firecrawl | SSE (local) | 8015 | ⏳ PENDING |

### 4.2 Migration Checklist per Server

#### Omega Hub (Priority 1 — 4h)
```python
# mcp_servers/omega_hub/server.py
# CHANGES:
# 1. mcp.run(transport="streamable-http", host="127.0.0.1", port=8016)
# 2. Add CORS: mcp.settings.allowed_origins = ["http://localhost:*", "http://127.0.0.1:*"]
# 3. Remove SSE-specific routes (/sse, /messages)
# 4. Update .opencode.json: "url": "http://127.0.0.1:8016/mcp/"
# 5. Test: mcp inspect http://localhost:8016/mcp/
# 6. Verify resumability: disconnect/reconnect mid-stream
```

#### Firecrawl MCP (Priority 2 — 2h)
```python
# mcp_servers/firecrawl/server.py
# Same pattern: FastMCP + streamable-http + CORS
# Update .opencode.json
```

#### Validation Tests
```bash
# For each migrated server:
mcp inspect http://localhost:PORT/mcp/
# Verify: tools list, tool call, streaming response, reconnection
```

### 4.3 OAuth 2.1 + PKCE (Future — 8h)
- Add `mcp-auth` middleware
- Issue bearer tokens for production exposure
- Not needed for localhost-only

---

## §5 Vector Store Optimization (Qdrant)

### 5.1 Current State
- Qdrant running on :6333 (published from container)
- Collections: `omega_memory`, `omega_knowledge`, `youtube_research`
- No scalar quantization, no payload indexes

### 5.2 Optimizations (4h)

| Optimization | Command | Impact |
|--------------|---------|--------|
| **Scalar Quantization** | `PUT /collections/{name}/quantization` | 4x memory reduction, <1% recall loss |
| **Payload Indexes** | `PUT /collections/{name}/index` on `entity_name`, `source_id`, `topic` | 10-100x filter speedup |
| **HNSW Tuning** | `m=16, ef_construct=128` for 384-dim | Better recall/speed tradeoff |
| **On-disk payload** | `payload_storage_type: "on_disk"` | Reduce RAM for large metadata |

```bash
# Apply via curl or qdrant-client
curl -X PUT "http://localhost:6333/collections/omega_memory/quantization" \
  -H "Content-Type: application/json" \
  -d '{"scalar": {"type": "int8", "quantile": 0.99, "always_ram": true}}'

curl -X PUT "http://localhost:6333/collections/omega_memory/index" \
  -H "Content-Type: application/json" \
  -d '{"field_name": "entity_name", "field_schema": "keyword"}'

curl -X PUT "http://localhost:6333/collections/omega_memory/index" \
  -H "Content-Type: application/json" \
  -d '{"field_name": "source_id", "field_schema": "keyword"}'
```

### 5.3 Embedding Dimension Alignment
- Current: Mixed (384, 768, 64, 256)
- Target: Standardize on 768 (Gemma) or 384 (MiniLM) per collection
- Action: Re-embed or create dimension-specific collections

---

## §6 Infrastructure & Observability

### 6.1 Podman Networking Fix (Pasta Header Injection)
```ini
# ~/.config/containers/systemd/omega-searxng.container
# Add to [Container] section:
ExecStartPre=/usr/bin/sh -c 'echo "nameserver 1.1.1.1" > /etc/resolv.conf'
# Or use podman 5.2+ --dns-opt
```

### 6.2 Health Checks & Alerting
```python
# Add to each worker/service:
async def health_check():
    return {
        "status": "healthy",
        "checks": {
            "redis": await redis.ping(),
            "qdrant": await qdrant.get_collections(),
            "searxng": await searxng.health(),
            "model_gateway": await gateway.health(),
        }
    }
```

### 6.3 Metrics Dashboard (Hivemind + Grafana)
- Ingest rate (videos/min)
- Synthesis quality (insights/video)
- Error taxonomy (Qliphoth codes)
- Queue depth
- Rate limit hits

---

## §7 Execution Order & Dependencies

```
WEEK 1 (Days 1-3): YouTube Worker Core Hardening
├── Day 1: TranscriptFetcher circuit breaker + adaptive backoff (4h)
├── Day 2: RAG synthesis + retrieve_chunks() (6h)
├── Day 3: Queue resilience + SearXNG engines + config (3h)
└── Day 3-4: Adversarial tests (4h)

WEEK 1 (Days 4-5): Ingestion Pipeline
├── Day 4: Circuit breaker wrapper + idempotency (3h)
├── Day 5: Streaming large docs + metrics (5h)

WEEK 2 (Days 1-3): AGB-0 / Local Embeddings
├── Day 1: Embedder protocol + AGBLazyEmbedder + ONNX (3h)
├── Day 2: LMStudioEmbedder + AncientGreekDetector (2h)
├── Day 3: Krikri GGUF acquisition + quantization (4h)

WEEK 2 (Days 4-5): MCP Migration
├── Day 4: Omega Hub Streamable HTTP (4h)
├── Day 5: Firecrawl MCP + validation tests (2h)

WEEK 3: Vector Store + Infrastructure
├── Qdrant quantization + indexes (4h)
├── Podman networking fix (2h)
├── Health checks + alerting (3h)

ONGOING: Web Claude Upload (Manual — when operator available)
```

---

## §8 Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| YouTube HTML scrape breaks (youtube_noapi) | High | Ingestion stops | Multiple SearXNG engines + Invidious instances |
| Home IP banned by YouTube | Medium | Permanent 429 | Webshare residential proxy (optional) |
| AGB model not compatible with ONNX | Low | Phase 3 blocked | Fallback to LM Studio + GGUF |
| Qdrant quantization breaks recall | Low | Search quality drops | Test with `quantile=0.99`, keep original vectors |
| MCP Streamable HTTP breaks OpenCode | Low | Agent communication fails | Test with `mcp inspect` before deploy |
| Embedding dimension mismatch | Medium | Vector search fails | Standardize per collection, re-embed if needed |

---

## §9 Success Criteria

| Metric | Target |
|--------|--------|
| YouTube worker uptime | >99% (no crash loops) |
| Transcript fetch success rate | >95% (with retries) |
| Synthesis RAG coverage | 100% (no title-only fallback) |
| MCP server response time | <200ms p95 |
| Qdrant query latency | <50ms p95 (with quantization) |
| Local embedding chain coverage | 100% (no cloud fallback in normal ops) |
| Ingestion pipeline throughput | >100 docs/min |
| Test coverage (new code) | >90% |

---

## §10 Immediate Next Steps (Today)

---

## §11 Carmack Tier 0 — Code Quality Baseline (BLOCKING)

**Source**: John Carmack S3 Consultation — Architectural review of v1.2.0 baseline

### Executive Summary
v1.2.0 baseline achieved (1315 tests, 23 mandates, 9 providers). Tier 0 addresses code quality debt before Epoch II features.

### Phase 1: Foundation (2h) — DO FIRST
| # | Task | Carmack Directive | Effort |
|---|------|-------------------|--------|
| T0-1 | **F821 undefined-name fixes** | `ruff check --select=F821 src/` → fix all. Trivial, unblocks everything. | 15 min |
| T0-2 | **Bare `except Exception:` elimination** | M9/M23 compliance. Replace with typed `except (SpecificError,):` + `trace_id` logging. Fail fast, fail loud. | 90 min |

### Phase 2: Core Infrastructure (4h)
| # | Task | Carmack Pattern | Effort |
|---|------|-----------------|--------|
| T0-3 | **Centralized logging** | Single `src/omega/logging.py` with `structlog` + AnyIO async sinks. One `get_logger(__name__)` pattern everywhere. No `basicConfig` scattered. | 4h |
| T0-4 | **Config validation (Pydantic OmegaConfig)** | `model_config = ConfigDict(extra='forbid', frozen=True)`. Validate at startup, fail fast. No runtime config surprises. | 7h |

### Phase 3: Data Layer (5h)
| # | Task | Risk Mitigation | Effort |
|---|------|-----------------|--------|
| T0-5 | **Qdrant → sqlite-vec decommission** | Dual-write for 1 sprint. Verify vector parity (cosine ±0.001). Keep Qdrant image cached for rollback. | 3h |
| T0-6 | **sqlite-vec Phase 1-2** | Metadata filtering + quantization. Benchmark 10K vectors on Zen 2 — must stay <50ms p99. | 2h |

### Phase 4: CI & Stress (3h)
| # | Task | Standard | Effort |
|---|------|----------|--------|
| T0-7 | **Single CI workflow** | One `.github/workflows/ci.yml`: lint → test → temple-grade → heritage-vet → sovereignty. No matrix. | 2h |
| T0-8 | **Stress tests (5 scenarios)** | (1) 100 concurrent `talk()`, (2) 10K vector inserts, (3) 1hr soak, (4) OOM injection, (5) network partition. | 5h |

### Deferred (Explicitly NOT Tier 0)
| Task | Reason |
|------|--------|
| Full Pydantic v2 migration | v1 works, v2 is churn |
| Structured logging overhaul | `structlog` is fine, don't rewrite |
| Coverage gate >80% | Current ~75% acceptable for v1.2.0 |

### Carmack's Laws Applied
1. **Fail fast, fail loud** — Every `except` logs `trace_id` and re-raises or returns typed error
2. **Data over code** — Config validation at load time, not access time
3. **Measure before optimize** — Stress tests first, then tune sqlite-vec HNSW params
4. **Rollback ready** — Qdrant decommission only after 7-day dual-write verification

### Execution Order
```
Week 0 (Before Infra Hardening): T0-1 → T0-2 → T0-3 → T0-4
Week 1: T0-5 → T0-6 → T0-7 → T0-8  
Week 2+: YouTube Worker Hardening (§1) → Ingestion Pipeline (§2) → AGB-0 (§3) → MCP Migration (§4)
```

**Gate**: All Tier 0 tasks complete + 1315 tests passing + Temple-Grade clean before proceeding to §1 YouTube Worker Hardening.

1. **Start YouTube Worker Phase 1A** — TranscriptFetcher hardening
2. **Verify SearXNG video engines** — Test `categories=videos` with multiple engines
3. **Run `make test`** — Confirm 1189 baseline still passes
4. **Create feature branch** — `git checkout -b feat/infra-hardening-youtube-worker`

---

*🔱 OMEGA ⬡ KALI ⬡ INFRA-HARDENING-PLAN ⬡ v1.0.0 ⬡ 2026-07-12*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
