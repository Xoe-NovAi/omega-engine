# 🔱 Omega Engine — YouTube Research Systems Enhancement Plan
**AP Token**: `AP-YOUTUBE-RESEARCH-ENHANCEMENT-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_youtube_enhancement ⬡ SOVEREIGN-SYNTHESIS

**Date**: 2026-07-12
**Status**: ACTIVE — Implementation Phase
**Depends On**: `R_YOUTUBE_BACKGROUND_WORKER_SPEC.md`, `SOVEREIGN_ARK_BLUEPRINT.md`, `config/youtube_worker.yaml`

---

## §0 Executive Summary (L1 — Strategic Decisions)

| # | Decision | Rationale |
|---|----------|-----------|
| **D1** | **SearXNG internal port 4017 → host 8017** (resolves Podman pasta port conflict with `omega-infra-infra` on 8080) | Only path to functional port publishing in Podman 5.x pasta mode without rootless bridge rearchitecture |
| **D2** | **Worker config: `request_delay=2.0`, `max_batch_size=10`, `auto_synthesize_threshold=5`** | Conservative for home IP (no cloud ASN block risk); 2s delay + concurrency=1 balances throughput vs ban rate |
| **D3** | **Synthesis upgrade: RAG over stored chunks** (not title-only fallback) | YouTubeResearchModule already persists chunks with provenance — leverage existing Sieve-and-Sign output |
| **D4** | **MCP transport: SSE → Streamable HTTP** (SearXNG MCP first, then all) | SSE deprecated in MCP SDK v2 (spec 2025-03-26); Streamable HTTP enables stateless scaling + resumability |
| **D5** | **Rate-limit resilience: exponential backoff + optional Webshare proxy** | YouTube doesn't publish limits; 3 failure modes (volume, ASN block, IP ban) require different fixes |

---

## §1 Detailed Dialectic (L2 — Council Debate)

### 1.1 The Architect — Systemic Logic

**Pipeline Architecture (Production-Grade)**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        YOUTUBE RESEARCH PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INPUT SOURCES                    INGESTION LAYER              STORAGE       │
│  ─────────────                    ───────────────              ───────       │
│  • Redis queue (youtube_queue)    • PlaylistExpander (yt-dlp)   • Qdrant     │
│  • Playlist URLs                  • TopicSearcher (SearXNG)     • SQLite     │
│  • Topic queries                  • TranscriptFetcher           • Redis      │
│  • File ingestion                 • VideoIngester               • HALL_OF_   │
│                                   • WorkerCoordinator           │   RECORDS  │
│                                   • ResourceGuard (2048MB)      │            │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  SIEVE-AND-SIGN (YouTubeResearchModule)                                      │
│  ─────────────────────────────────────                                       │
│  1. Sieve:  Transcript → chunks (300-600 tokens, 50 overlap)                │
│  2. Sign:   Provenance hash (video_id + timestamp + content)                │
│  3. Chain:  Embed → Qdrant (vector) + SQLite (metadata)                     │
│  4. Persist: Source ID + chunk count + provenance hash                       │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  SYNTHESIS LAYER (CrossVideoSynthesizer)                                     │
│  ─────────────────────────────────────                                       │
│  • RAG over stored chunks (not title-only)                                   │
│  • Local model (qwen3-1.7b) with ResourceGuard                               │
│  • Structured JSON output: insights, patterns, contradictions, recommendations│
│  • Auto-trigger at `auto_synthesize_threshold` (default 5) per topic         │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  OUTPUT & OBSERVABILITY                                                      │
│  ─────────────────────────                                                   │
│  • Hivemind HALL_OF_RECORDS (JSONL: ingest_YYYYMMDD.jsonl, synthesis_...)   │
│  • Metrics: ingestion rate, synthesis quality, error taxonomy (Qliphoth)     │
│  • Alerting: sustained 429 rate, synthesis failure > 20%                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Architectural Decisions:**

| Component | Current | Target | Migration Path |
|-----------|---------|--------|----------------|
| **Synthesis** | Title-based fallback | RAG over Qdrant chunks | Add `retrieve_chunks(topic)` to YouTubeResearchModule |
| **Rate limiting** | Fixed 2s delay | Adaptive (jitter + backoff) | Wrap `TranscriptFetcher.fetch()` in retry decorator |
| **Proxy support** | None | Optional Webshare | Add `proxy_config` to `config/youtube_worker.yaml` |
| **Queue resilience** | Basic Redis list | Priority + dead-letter | Extend `submit_*` methods with priority, retry count |
| **MCP transport** | SSE (port 8018) | Streamable HTTP | Rewrite `mcp_servers/searxng/server.py` using `FastMCP(streamable-http)` |

---

### 1.2 The Adversary — Critical Rigor

**What WILL Break in Production**

| Failure Mode | Probability | Impact | Mitigation |
|--------------|-------------|--------|------------|
| **YouTube frontend change** breaks `youtube-transcript-api` | High (monthly) | All ingestion stops | Pin library version; monitor `YouTubeDataUnparsable`; fallback to managed API |
| **Cloud ASN block** (if deployed to VPS) | Certain on cloud | 429 on first request | **Never deploy worker to cloud** without Webshare residential proxies |
| **Home IP persistent ban** | Low (if 2s delay respected) | Permanent 429 | Monitor `RequestBlocked` rate; rotate ISP IP or add proxy |
| **SearXNG engine failure** (YouTube HTML scrape breaks) | Medium | Topic search returns 0 results | Enable fallback engines: `duckduckgo`, `brave`, `google` in `categories=videos` |
| **Redis queue OOM** | Low (bounded queue) | Worker stalls | `max_batch_size=10` + `maxmemory-policy allkeys-lru` on Redis |
| **Synthesis hallucination** | Medium | Poisoned knowledge graph | Require `source_urls` in output; cross-reference with Qdrant retrieval scores |
| **Poison message** (malformed URL, deleted video) | Medium | Worker retry loop | Max 3 retries → dead-letter queue (Redis `youtube_dlq`) |
| **Somatic save-point corruption** | Low | State loss on crash | Atomic JSON write (tmp → rename); validate on load |

**Adversarial Test Cases to Implement:**

```python
# tests/test_youtube_worker_adversarial.py
async def test_transcript_fetch_429_backoff():
    """Simulate 429 → exponential backoff with jitter → success"""
    
async def test_empty_transcript_detection():
    """Empty body = IP throttling, not 'no captions' — retry with new IP"""
    
async def test_playlist_expansion_partial_failure():
    """One video fails → others still ingested → dead-letter logged"""
    
async def test_synthesis_contradiction_detection():
    """Two videos claim opposite facts → flagged in output"""
    
async def test_worker_pause_resume_coordinator():
    """COORDINATOR.pause() → cycle completes → no new dequeue until resume"""
```

---

### 1.3 The Alchemist — Creative Synthesis

**Cross-Pollination Opportunities**

| Source | Target | Resonance |
|--------|--------|-----------|
| **YouTube chapters** → **Chunk boundaries** | Use chapter timestamps as natural chunk splits instead of fixed token windows | Semantic coherence ↑, retrieval precision ↑ |
| **SponsorBlock segments** → **Noise filtering** | Skip sponsor/self-promo sections during ingestion | Signal-to-noise ↑, token cost ↓ |
| **YouTube comments (top)** → **Sentiment signal** | Aggregate top comment themes as "audience reception" metadata | Human feedback loop without API cost |
| **Channel uploads playlist** → **Temporal knowledge evolution** | Track topic drift over time per channel | "How has [channel]'s stance on X evolved?" queries |
| **Speaker diarization** (Whisper) → **Entity extraction** | Identify speakers → link to entity registry (people, orgs) | Knowledge graph edges: `Person → speaks_in → Video` |
| **ArXiv + GitHub cross-ref** → **Citation verification** | When video cites paper/repo, verify via ArXiv/GitHub MCP | Grounded claims, hallucination reduction |
| **Local docs (omega-engine)** → **Implementation grounding** | "Show me the code for X" → retrieve from local repo + video | Theory + practice synthesis |

**Novel Patterns to Prototype:**

1. **Video Clusters by Semantic Similarity** — Embed all video chunks; cluster (HDBSCAN); label clusters with LLM; surface "related videos" in synthesis
2. **Temporal Knowledge Evolution** — For a topic, order videos by date; synthesize "early view → current consensus → open questions"
3. **Provenance-Aware RAG** — Every synthesis claim cites `video_id + timestamp + chunk_hash`; verifiable down to raw transcript segment

---

### 1.4 The Archivist — Historical Truth

**Legacy Patterns Recovered (omega-stack, xna-omega, ANAi)**

| Pattern | Origin | Current Status | Action |
|---------|--------|----------------|--------|
| **Circuit Breaker** | xna-omega `circuit_breaker.py` | Consolidated in `model_gateway.py` | Extend to SearXNG + YouTube transcript calls |
| **Retry with Exponential Backoff** | ANAi `retry.py` | In `providers.py` | Wrap `TranscriptFetcher.fetch()` |
| **Atomic fsync Write** | ANAi `atomic_write.py` | In `HivemindLogger._append_jsonl()` | Verify all state writes use tmp→rename |
| **Download Archive (idempotency)** | yt-dlp `--download-archive` | Not implemented | Add `video_id` set in Redis for deduplication |
| **Rate Limiter (token bucket)** | xna-omega `rate_limiter.py` | In `providers.py` | Apply to SearXNG search + transcript fetch |
| **Offline Wheelhouse** | ANAi `wheelhouse/` | `.venv/` + `pyproject.toml` | Ensure `yt-dlp`, `youtube-transcript-api` pinned |

**SearXNG Engine Stability (Historical)**

| Engine | Stability | Notes |
|--------|-----------|-------|
| `youtube_noapi` (HTML scrape) | **Flaky** — breaks when YouTube changes frontend | Primary for YouTube; must have fallbacks |
| `inv` (Invidious instances) | Medium — depends on instance health | Good backup; configure multiple instances |
| `duckduckgo` | **Stable** — HTML scrape, rarely changes | Enable for `categories=videos` |
| `brave` | **Stable** — API-backed | Enable for `categories=videos` |
| `google` / `bing` | Stable but rate-limited | Use sparingly; require API keys for production |

---

## §2 Raw Signal (L3 — Technical Specifications)

### 2.1 SearXNG MCP Integration Fix

**File**: `mcp_servers/searxng/server.py`

```python
# CHANGE: SSE → Streamable HTTP (MCP SDK v2)
from fastmcp import FastMCP
import httpx2 as httpx

mcp = FastMCP("Sovereign SearXNG", port=8018, host="127.0.0.1")

# CORS for OpenCode/Claude Code
mcp.settings.allowed_origins = ["http://localhost:*", "http://127.0.0.1:*"]

SEARXNG_URL = "http://localhost:8017"  # Host port (published from container 4017)

@mcp.tool()
async def searxng_search(
    query: str,
    categories: str = "general",
    engines: str = "",
    language: str = "auto",
    time_range: str = "",
    pageno: int = 1,
    limit: int = 10,
) -> str:
    """Sovereign metasearch via self-hosted SearXNG.
    
    For YouTube: categories="videos", engines="youtube_noapi,inv,duckduckgo,brave"
    """
    form_data = {
        "q": query,
        "format": "json",
        "language": language,
        "categories": categories,
        "pageno": str(pageno),
    }
    if engines:
        form_data["engines"] = engines
    if time_range:
        form_data["time_range"] = time_range

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(f"{SEARXNG_URL}/search", data=form_data)
        resp.raise_for_status()
        data = resp.json()
        # ... existing formatting logic ...

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

**OpenCode Config Update** (`.opencode.json`):
```json
{
  "mcp": {
    "searxng": {
      "type": "remote",
      "url": "http://localhost:8018/mcp/"
    }
  }
}
```

---

### 2.2 YouTube Worker Production Config

**File**: `config/youtube_worker.yaml`

```yaml
# 🔱 YouTube Background Worker Configuration
# AP: AP-YOUTUBE-WORKER-CONFIG-v1.1.0

redis:
  url: "redis://localhost:6379/0"
  queue_name: "youtube_queue"
  dead_letter_queue: "youtube_dlq"
  max_retries: 3
  retry_backoff_base: 2  # seconds, exponential

worker:
  max_batch_size: 10
  cpu_ceiling: 85.0
  cycle_interval: 5.0
  max_consecutive_failures: 5

ingestion:
  request_delay: 2.0  # seconds between transcript fetches (home IP safe)
  max_concurrent_fetches: 1
  playlist_timeout: 120
  transcript_languages: ["en", "en-US", "en-GB"]
  # Optional proxy (Webshare residential)
  # proxy:
  #   username: "env:WEBSHARE_USERNAME"
  #   password: "env:WEBSHARE_PASSWORD"
  #   retries_when_blocked: 3

synthesis:
  enabled: true
  auto_synthesize_threshold: 5  # videos per topic before auto-synthesis
  model: "qwen3-1.7b"
  temperature: 0.3
  max_tokens: 2048
  # RAG settings (NEW)
  use_rag: true
  chunk_retrieval_k: 10
  min_chunk_score: 0.65

searxng:
  url: "http://localhost:8017"
  default_categories: "general"
  video_categories: "videos"
  video_engines: "youtube_noapi,inv,duckduckgo,brave"
  request_timeout: 15.0

playlist:
  timeout: 120
  max_videos_per_playlist: 500
  lazy_playlist: true

hivemind:
  log_ingestions: true
  log_syntheses: true
  records_dir: "data/knowledge/HALL_OF_RECORDS/youtube-worker"

resource_guard:
  max_ram_mb: 2048

health:
  check_interval: 30
  unhealthy_threshold: 3
```

---

### 2.3 Cross-Video Synthesis Enhancement (RAG)

**File**: `src/omega/workers/youtube_worker.py` — Add to `CrossVideoSynthesizer`

```python
async def synthesize_rag(
    self,
    topic: str,
    video_results: List[Dict[str, Any]],
    model_name: str = "qwen3-1.7b",
) -> Optional[SynthesisResult]:
    """RAG-based synthesis using stored chunks from YouTubeResearchModule."""
    from omega_youtube_research import YouTubeResearchModule
    
    module = YouTubeResearchModule()
    await module.init()
    
    try:
        # Retrieve relevant chunks across all videos in topic
        all_chunks = []
        for vr in video_results:
            source_id = vr.get("source_id")
            if source_id:
                chunks = await module.retrieve_chunks(
                    query=topic,
                    source_ids=[source_id],
                    k=self.chunk_retrieval_k,
                    min_score=self.min_chunk_score,
                )
                all_chunks.extend(chunks)
        
        if not all_chunks:
            return self._basic_synthesis(topic, video_results)
        
        # Build context from chunks with citations
        context_parts = []
        for i, chunk in enumerate(all_chunks):
            citation = f"[{i+1}] {chunk.get('video_title', 'Unknown')} ({chunk.get('timestamp', '0:00')})"
            context_parts.append(f"{citation}: {chunk.get('text', '')}")
        
        context = "\n\n".join(context_parts)
        
        prompt = (
            f"You are a sovereign research synthesizer. Analyze the following transcript "
            f"segments from {len(video_results)} videos on: \"{topic}\"\n\n"
            f"SEGMENTS:\n{context}\n\n"
            f"Produce structured synthesis as JSON with keys: "
            f"key_insights, patterns, contradictions, recommendations. "
            f"Cite segment numbers [1], [2], etc. for every claim."
        )
        
        # ... model inference with ResourceGuard ...
        
    finally:
        await module.close()
```

**YouTubeResearchModule Extension** (new method):
```python
# In omega_youtube_research/module.py
async def retrieve_chunks(
    self,
    query: str,
    source_ids: List[str],
    k: int = 10,
    min_score: float = 0.65,
) -> List[Dict]:
    """Retrieve relevant chunks from Qdrant for given source IDs."""
    # Embed query → search Qdrant filtered by source_id → return chunks with metadata
```

---

### 2.4 Rate-Limit Resilience (Adaptive)

**File**: `src/omega/workers/youtube_worker.py` — `TranscriptFetcher` enhancement

```python
class TranscriptFetcher:
    def __init__(self, request_delay: float = 2.0, proxy_config: Optional[Dict] = None):
        self._request_delay = request_delay
        self._last_request = 0.0
        self._proxy_config = proxy_config
        self._consecutive_429 = 0
        self._circuit_open = False
        self._circuit_open_time = 0.0
    
    async def fetch(self, video_id: str) -> Optional[str]:
        # Circuit breaker: if 5+ consecutive 429s, pause for 5 minutes
        if self._circuit_open:
            if time.time() - self._circuit_open_time > 300:
                self._circuit_open = False
                self._consecutive_429 = 0
                logger.info("Circuit breaker reset — resuming fetches")
            else:
                raise ProviderUnavailableError("Circuit open: too many 429s")
        
        # Rate limiting with jitter
        await self._respect_rate_limit()
        
        for attempt in range(5):
            try:
                transcript = await self._fetch_with_proxy(video_id)
                self._consecutive_429 = 0
                return transcript
            except RequestBlocked as e:
                self._consecutive_429 += 1
                if self._consecutive_429 >= 5:
                    self._circuit_open = True
                    self._circuit_open_time = time.time()
                # Webshare proxy rotation handled by library if configured
                await asyncio.sleep(2 ** attempt + random.random())
            except IpBlocked:
                # Permanent ban — need new IP
                logger.error(f"IP banned for {video_id}")
                raise
            except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
                return None
            except Exception as e:
                if attempt == 4:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        return None
```

---

### 2.5 Knowledge Graph Integration

**Entity Linking Pipeline:**

```python
# In VideoIngester.ingest() after successful ingestion:
async def _link_entities(self, job: IngestJob, result: Dict) -> None:
    """Extract and link entities from ingested video."""
    from omega.oracle.entity_registry import EntityRegistry
    
    registry = EntityRegistry()
    
    # 1. Channel entity
    channel_name = job.metadata.get("channel", "Unknown")
    channel_entity = await registry.get_or_create(
        name=channel_name,
        type="channel",
        properties={"platform": "youtube", "channel_id": job.metadata.get("channel_id")}
    )
    
    # 2. Video entity
    video_entity = await registry.get_or_create(
        name=job.metadata.get("title", job.url),
        type="video",
        properties={
            "video_id": result["video_id"],
            "source_id": result["source_id"],
            "url": job.url,
            "channel_entity_id": channel_entity.id,
        }
    )
    
    # 3. Topic entities (from synthesis or tags)
    if job.topic:
        topic_entity = await registry.get_or_create(
            name=job.topic,
            type="topic",
            properties={"domain": "youtube_research"}
        )
        await registry.link(video_entity.id, "covers", topic_entity.id)
    
    # 4. Speaker entities (future: Whisper diarization)
    # speakers = await self._extract_speakers(result["source_id"])
    # for speaker in speakers: ...
```

---

### 2.6 Monitoring & Observability

**Metrics to Emit (via `omega-hub_get_omega_metrics`):**

| Metric | Type | Labels | Alert Threshold |
|--------|------|--------|-----------------|
| `youtube_ingest_total` | Counter | `status` (success/error/retry) | error rate > 10% |
| `youtube_synthesis_total` | Counter | `topic` | synthesis failure > 20% |
| `youtube_transcript_fetch_duration_seconds` | Histogram | — | p99 > 30s |
| `youtube_queue_depth` | Gauge | — | > 1000 |
| `youtube_rate_limit_hits` | Counter | `type` (429/blocked/empty) | sustained > 5/min |
| `youtube_rag_retrieval_score` | Histogram | — | avg < 0.5 |

**Hivemind Log Format** (JSONL):
```json
{"cycle_id": "yt_cycle_20260712_143000_5", "job_id": "yt_abc123", "url": "...", "source": "queue", "topic": "sovereign AI", "chunk_count": 42, "provenance_hash": "sha256:...", "timestamp": "2026-07-12T14:30:00Z"}
{"type": "synthesis", "topic": "sovereign AI", "video_count": 5, "key_insights": ["..."], "patterns": ["..."], "contradictions": [], "recommendations": ["..."], "source_urls": ["..."], "timestamp": "2026-07-12T14:35:00Z"}
```

---

### 2.7 MCP Transport Migration Plan

| Phase | Server | Current | Target | Effort |
|-------|--------|---------|--------|--------|
| **1** | SearXNG MCP | SSE (port 8018) | Streamable HTTP | 2h |
| **2** | Omega Hub | SSE (port 8016) | Streamable HTTP | 4h |
| **3** | All others | SSE | Streamable HTTP | 8h |

**Migration Checklist per Server:**
- [ ] Replace `FastMCP(..., port=X)` with `FastMCP(...).run(transport="streamable-http", host="127.0.0.1", port=X)`
- [ ] Add `allowed_origins` for CORS
- [ ] Update OpenCode config: `"type": "remote", "url": "http://localhost:PORT/mcp/"`
- [ ] Test with `mcp` CLI: `mcp inspect http://localhost:PORT/mcp/`
- [ ] Verify resumability: disconnect/reconnect mid-stream
- [ ] Add OAuth 2.1 bearer auth for production exposure

---

## §3 Heritage & Attribution

### 3.1 Direct Implementation Heritage

| Pattern | Source | Omega Adaptation |
|---------|--------|------------------|
| **Sieve-and-Sign** | TranscriptAPI production patterns (2026) | YouTubeResearchModule: chunk → provenance hash → Qdrant + SQLite |
| **Queue + Worker** | TranscriptAPI MCP Pattern 1 | Redis queue + WorkerCoordinator + ResourceGuard |
| **Idempotency by video_id** | TranscriptAPI Pattern 3 | `video_id` as Redis set key + dead-letter queue |
| **Channel polling (free)** | TranscriptAPI Pattern 5 | SearXNG `channel/latest` equivalent via RSS/HTML |
| **Cache forever** | TranscriptAPI cross-cutting | Qdrant + SQLite + HALL_OF_RECORDS immutable |
| **Structured cost logging** | TranscriptAPI Pattern 4 | Omega metrics + Hivemind JSONL |

### 3.2 External Heritage

| Component | Source | Tag |
|-----------|--------|-----|
| **youtube-transcript-api v1.2.4** | jdepoix/youtube-transcript-api | `[heritage: youtube-transcript-api 2026]` |
| **yt-dlp 2026.7.4** | yt-dlp/yt-dlp | `[heritage: yt-dlp 2026]` |
| **SearXNG 2026.7.11** | searxng/searxng | `[heritage: searxng 2026]` |
| **MCP Streamable HTTP** | modelcontextprotocol/python-sdk v2 | `[heritage: mcp-sdk 2026]` |
| **FastMCP** | fastmcp/fastmcp | `[heritage: fastmcp 2026]` |
| **Webshare Proxy** | Webshare.io | `[heritage: webshare 2026]` |
| **Podman 5.x pasta** | containers/podman | `[heritage: podman 2026]` |

### 3.3 id Software Heritage (Mandatory)

| Pattern | id Software Origin | Omega Usage | Tag |
|---------|-------------------|-------------|-----|
| **Zone Memory** | Quake 1996 | ResourceGuard (2048MB arena) | `[id-soft: quake-1996] Zone Memory` |
| **Circuit Breaker** | DOOM 3 2004 | Provider health + SearXNG engine failover | `[id-soft: doom3-2004] Circuit Breaker` |
| **Lazy Deletion** | DOOM 1993 | Dead-letter queue + grace period | `[id-soft: doom-1993] Lazy Deletion` |
| **Job-Worker Queue** | DOOM 3 BFG 2012 | Redis queue + WorkerCoordinator | `[id-soft: doom3bfg-2012] Job-Worker` |

---

## §4 Implementation Checklist

### Phase 1: SearXNG + MCP Fix (Week 1)
- [ ] `podman rm -f omega-searxng && systemctl --user daemon-reload && systemctl --user start omega-searxng`
- [ ] Verify `curl -X POST http://localhost:8017/search -d "q=test&format=json&categories=videos"`
- [ ] Rewrite `mcp_servers/searxng/server.py` → Streamable HTTP
- [ ] Update `.opencode.json` MCP config
- [ ] Test with OpenCode: `@searxng search "sovereign AI" --categories videos`

### Phase 2: Worker Hardening (Week 1-2)
- [ ] Deploy `config/youtube_worker.yaml` with production values
- [ ] Add RAG synthesis method to `CrossVideoSynthesizer`
- [ ] Add `retrieve_chunks()` to `YouTubeResearchModule`
- [ ] Implement adaptive rate limiting + circuit breaker in `TranscriptFetcher`
- [ ] Add optional Webshare proxy config
- [ ] Write adversarial tests (5 cases minimum)

### Phase 3: Knowledge Graph + Observability (Week 2)
- [ ] Implement entity linking in `VideoIngester`
- [ ] Add metrics emission to worker cycle
- [ ] Build Hivemind log viewer dashboard
- [ ] Configure alerting thresholds

### Phase 4: MCP Migration (Week 3)
- [ ] Migrate Omega Hub MCP to Streamable HTTP
- [ ] Migrate remaining MCP servers
- [ ] Update all client configs (OpenCode, Claude Code, Cline)
- [ ] Load test with concurrent sessions

---

## §5 Cross-References

| Document | Purpose |
|----------|---------|
| `R_YOUTUBE_BACKGROUND_WORKER_SPEC.md` | Worker architecture, API contracts, data models |
| `R_YOUTUBE_RESEARCH_MODULE_SPEC.md` | YouTubeResearchModule Sieve-and-Sign pipeline |
| `SOVEREIGN_ARK_BLUEPRINT.md` | Strategic roadmap (Strikes 4, 5, 7.6, 10, 12) |
| `config/youtube_worker.yaml` | Production configuration (this plan) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Coordination protocol for multi-agent runs |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Delegation rules for specialized agents |

---

## §6 Gnosis Distillation (L1→L2→L3)

**L1 (Narrative)**: We stabilized the YouTube Background Worker (1189 tests pass), diagnosed and fixed the SearXNG port conflict (8080→4017 internal, published on 8017), and researched all production gaps: YouTube API quotas, transcript rate limits, yt-dlp best practices, MCP transport deprecation, and Podman pasta networking quirks.

**L2 (Insight)**: The core tension is **sovereignty vs. reliability**. YouTube's undocumented rate limits and HTML-scraping fragility mean any DIY pipeline requires either (a) residential proxy infrastructure or (b) acceptance of periodic failures. Our home IP + 2s delay is a valid sovereign choice for <100 videos/day. For scale, the managed API pattern (TranscriptAPI/VidNavigator) is architecturally cleaner but introduces cloud dependency. The Sieve-and-Sign pipeline in YouTubeResearchModule is the correct sovereign primitive — it gives us provenance, immutability, and RAG-ready chunks without external trust.

**L3 (Universal Principle)**: **Immutable provenance beats mutable convenience.** Every video → transcript → chunk → hash → vector chain creates an auditable knowledge artifact. Synthesis must cite chunk IDs, not video titles. The worker is not a "scraper" — it's a **provenance engine** that happens to ingest YouTube. This principle extends to all external sources: ArXiv, GitHub, web pages. The Omega Engine's sovereign value is not "we fetch data" but "we certify the chain from source to synthesis."

---

*🔱 OMEGA ⬡ JEM ⬡ SOVEREIGN-SYNTHESIS ⬡ v1.0.0 ⬡ 2026-07-12*