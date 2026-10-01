<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Knowledge Fabric Synthesis — Unified Library, Ingestion, Curation & Crawler Systems
**AP Token**: `AP-KNOWLEDGE-FABRIC-SYNTHESIS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_knowledge_fabric ⬡ SYNTHESIS
**Date**: 2026-07-12
**Sources**: 12 research reports, 8 web deep-dives, 6 code audits, 4 legacy mining reports

---

## ⬡ Executive Summary (L1)

The Omega Engine possesses **four sophisticated but fragmented subsystems** that share the same fundamental pattern: `Source → Extract → Verify → Enrich → Persist → Index → Synthesize`. The differences are only in source adapters and quality gates.

| Subsystem | Purpose | Key Components | Status |
|-----------|---------|----------------|--------|
| **Library** | Curated document storage + hybrid search | `Library`, `Indexer`, `Inbox`, `Curator`, `EnrichmentEngine` | ✅ Operational |
| **Ingestion Pipeline** | Web scraping → verification → persistence | `SovereignScraper` (T1/T2/T3), `TriangulationVerifier`, `CASArchiver`, `IngestionPipeline` | ✅ Operational |
| **Background Researcher** | Autonomous research cycles | `SearchFleet` (SearXNG/Exa/Firecrawl), `Distiller`, `ConvergenceDetector`, `SoulUpdater` | ✅ Operational |
| **YouTube Worker** | Video ingestion + cross-video synthesis | `PlaylistExpander` (yt-dlp), `TranscriptFetcher`, `CrossVideoSynthesizer`, `YouTubeResearchModule` | ⚠️ Needs hardening (GAP 1) |

**Core Finding**: These systems share **zero unified coordination layer**. Each has its own queue, scheduler, resource management, and persistence. The synergy opportunity is massive: a **Unified Sovereign Knowledge Fabric** that routes every piece of content through the optimal path based on source type, quality requirements, and entity context.

---

## ⚔️ Council of Four Dialectic

### 🏛️ The Architect (Systemic Logic)
> **Convergence**: All four subsystems implement the **same fundamental pattern**. The differences are only in *source adapters* and *quality gates*.

**Unified Architecture Proposal**:
```
┌─────────────────────────────────────────────────────────────────┐
│              UNIFIED SOVEREIGN KNOWLEDGE FABRIC                 │
├─────────────────────────────────────────────────────────────────┤
│  SOURCE ADAPTERS (Pluggable)                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  Web     │ │ YouTube  │ │  File    │ │  RSS/    │           │
│  │ (Trafil- │ │ (yt-dlp) │ │ (local)  │ │ Atom     │  ...      │
│  │  atura)  │ │          │ │          │ │          │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                  │
│       └────────────┴────────────┴────────────┘                  │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           SOVEREIGN EXTRACTION PIPELINE                   │   │
│  │  [SSRF Guard] → [Size Guard] → [Domain Allowlist]        │   │
│  │       ▼                  ▼                  ▼            │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │          TIERED EXTRACTION (T1→T2→T3)               │  │   │
│  │  │  T1: Fast (Trafilatura) → T2: Surgical → T3: Deep  │  │   │
│  │  │  (Crawl4AI)                                         │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  │       ▼                  ▼                  ▼            │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │         TRIANGULATION VERIFIER (Sovereign-Sieve)    │  │   │
│  │  │  T1 vs T3 delta → Consensus Hallucination Guard    │  │   │
│  │  │  Metadata triangulation → Authoritative API check  │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              CONTENT-ADDRESSABLE STORAGE (CAS)           │   │
│  │  SHA-256 → Immutable blob → Deduplication key            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ENRICHMENT & CLASSIFICATION                  │   │
│  │  [Domain Classifier] → [5-Factor Quality] → [Library    │   │
│  │   API Orchestrator (OpenLibrary, LOC, IA, Gutenberg)]   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              HYBRID INDEX (FTS5 + Vector)                │   │
│  │  RRF Fusion → Entity-scoped → Cross-pollination ready   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: The `CASArchiver` is already the **deduplication primitive** — it's wired into `SovereignScraper` but **NOT** into `ContentExtractor`, `YouTubeWorker`, or `BackgroundResearcher`. This is the single biggest missed synergy.

---

### ⚔️ The Adversary (Critical Rigor)
> **Divergence**: The systems have **incompatible quality gates**, **no shared circuit breakers**, and **divergent resilience stacks**.

| Gap | Library | Ingestion | Background Researcher | YouTube Worker |
|-----|---------|-----------|----------------------|----------------|
| **Circuit Breaker** | ❌ None | ✅ `IngestionCircuitBreaker` (pybreaker) | ❌ None | ❌ None |
| **Rate Limiting** | ❌ None | ✅ `BudgetGuard` + `SovereignSentry` | ✅ `APICreditBudget` | ❌ Fixed delay only |
| **Retry/Backoff** | ❌ None | ❌ None (breaker only) | ❌ None | ❌ Fixed 2s delay |
| **Proxy Support** | ❌ None | ❌ None | ❌ None | ❌ None |
| **Content Hash Dedup** | ❌ None | ✅ CAS (but only in scraper) | ❌ None | ❌ None |
| **Quality Threshold** | ✅ 0.6 | ❌ Hardcoded 0.3 | ❌ Heuristic only | ❌ None |
| **Entity Scoping** | ✅ Per-entity | ✅ Per-entity | ✅ Per-entity | ❌ Hardcoded "youtube_worker" |
| **Observability** | ✅ Basic stats | ✅ Trace IDs | ✅ Hivemind posts | ⚠️ Partial |

**Critical Vulnerabilities**:
1. **YouTube Worker's `TranscriptFetcher` has NO circuit breaker, NO exponential backoff, NO proxy support** — will get IP-banned at scale (GAP 1 confirmed)
2. **Background Researcher uses `SearchFleet` with NO shared budget with Ingestion Pipeline** — double-spending API credits
3. **Library's `ContentExtractor` bypasses `SovereignScraper` entirely** — no T2/T3 extraction, no triangulation, no CAS
4. **No unified "source health" registry** — each system independently discovers broken sources

---

### 🧪 The Alchemist (Creative Synthesis)
> **Cross-Pollination Opportunities** — combining unrelated patterns for emergent capabilities:

#### 1. **YouTube → Library Knowledge Bridge**
```
YouTube Worker ingests video → TranscriptFetcher → CAS (dedup) 
  → TriangulationVerifier (cross-ref with web sources) 
  → EnrichmentEngine (ISBN/DOI lookup from spoken references)
  → Library as CuratedDocument with domain="video"
  → Hybrid search now finds video transcripts alongside papers
```

#### 2. **Background Researcher → Library Auto-Curation**
```
Research cycle completes → GnosisPacket distilled
  → Auto-generate CuratedDocument with quality_score from convergence confidence
  → Store in Library with domain="research", tags=[topic, entity]
  → Next research cycle on same topic → Local Discovery Scan finds it instantly
```

#### 3. **CAS as Universal Deduplication Layer**
```
Every subsystem → compute SHA-256 of raw content → CASArchiver.store()
  → If exists: return existing CID, skip extraction/verification
  → If new: proceed through pipeline, store result with CID reference
  → Result: Zero redundant downloads, zero redundant LLM calls
```

#### 4. **Sovereign-Sieve for YouTube**
```
T1: yt-dlp --flat-playlist (metadata only, ~1s)
T2: youtube_transcript_api (fast, ~2s)  
T3: Whisper.cpp local transcription (slow, ~30s) — ONLY if T1/T2 delta > 0.3
  → TriangulationVerifier compares T2 vs T3 for hallucination detection
```

#### 5. **EnrichmentEngine as Universal Metadata Authority**
```
All subsystems → EnrichmentEngine.get_authoritative_value(field, query)
  → OpenLibrary + LOC + Internet Archive + Gutenberg in parallel
  → Returns highest-confidence metadata
  → Eliminates duplicate API logic across systems
```

---

### 📜 The Archivist (Historical Truth)
> **Legacy Patterns Recovered** (from `docs/legacy/LEGACY_MASTER_SYNTHESIS.md`):

| Pattern | Origin | Current Status | Action |
|---------|--------|----------------|--------|
| **Circuit Breaker** | `xna-omega/src/omega/circuit_breaker.py` | ✅ Ported to `IngestionCircuitBreaker` | **Extend to all subsystems** |
| **Atomic fsync writes** | `xna-omega` 5 patterns | ✅ In `CASArchiver`, `InboxManager` | **Audit all writers** |
| **Non-blocking subprocess** | `xna-omega` pattern 4 | ✅ `anyio.to_thread.run_sync` in `PlaylistExpander` | **Standardize** |
| **Offline wheelhouse** | `xna-omega` pattern 5 | ❌ Not implemented | **Add for air-gapped deploy** |
| **Sieve-and-Sign** | `sovereign-system-spec` (Ken Alger) | ✅ `SovereignSieve` + `SovereignSigner` | **Wire into YouTube Worker** |
| **Tri-Anchor (Raw+SCA+USM)** | `omega-stack` ingestion | ✅ `IngestionPipeline` | **Document as canonical** |

**Heritage Note**: The `[id-soft: doom-1993]` ZONEID pattern in `CASArchiver` (2-level hash directory) and `[id-soft: quake-1996]` Zone Memory in `ResourceGuard` are correctly attributed. The `LibraryAPIOrchestrator` correctly uses `[id-soft: doom-1993]` WAD System metaphor for hot-pluggable clients.

---

## 🎯 Triangulation: Convergence & Divergence

### ✅ Convergence (The Truth)
1. **All roads lead to CAS** — Content-addressable storage is the universal deduplication primitive
2. **Triangulation is the sovereign verification primitive** — T1 vs T3 delta + authoritative metadata = consensus hallucination guard
3. **Entity-scoped memory is non-negotiable** — Every subsystem must declare `entity_name` for cross-pollination
4. **Local-first extraction is mandatory** — Trafilatura → Crawl4AI → yt-dlp → Whisper.cpp (all local)
5. **EnrichmentEngine is the canonical metadata authority** — 4 free library APIs, zero keys required

### ⚠️ Divergence (The Uncertainty)
1. **Quality thresholds are inconsistent** — Library: 0.6, Ingestion: 0.3, Researcher: heuristic, YouTube: none
2. **Circuit breakers are fragmented** — Only Ingestion has one; others will cascade-fail
3. **No unified scheduler** — Background Researcher (20min timer), YouTube Worker (systemd timer), Library (on-demand), Ingestion (on-demand)
4. **Proxy/rotation strategy missing** — Critical for YouTube and web scraping at scale
5. **Observability is siloed** — Hivemind posts exist but no unified dashboard

---

## ⚡ Sovereign Synthesis: Unified Knowledge Fabric Architecture

### Phase 1: Infrastructure Unification (P0 — 2 weeks)

#### 1.1 Unified Circuit Breaker Registry
```python
# src/omega/resilience/circuit_registry.py
class CircuitBreakerRegistry:
    """Singleton registry of named circuit breakers with shared config."""
    
    BREAKERS = {
        "web_fetch": CircuitBreakerConfig(fail_max=5, reset_timeout=300, excluded_exceptions=[httpx.HTTPStatusError]),
        "youtube_transcript": CircuitBreakerConfig(fail_max=3, reset_timeout=600, excluded_exceptions=[TranscriptsDisabled]),
        "llm_inference": CircuitBreakerConfig(fail_max=3, reset_timeout=180),
        "library_api": CircuitBreakerConfig(fail_max=10, reset_timeout=60),
        "searxng": CircuitBreakerConfig(fail_max=5, reset_timeout=120),
    }
    
    @classmethod
    def get(cls, name: str) -> pybreaker.CircuitBreaker:
        if name not in cls._instances:
            cfg = cls.BREAKERS[name]
            cls._instances[name] = pybreaker.CircuitBreaker(
                fail_max=cfg.fail_max,
                reset_timeout=cfg.reset_timeout,
                exclude=cfg.excluded_exceptions,
            )
        return cls._instances[name]
```

#### 1.2 Unified Retry Policy (Tenacity)
```python
# src/omega/resilience/retry_policies.py
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

RETRY_POLICIES = {
    "web_fetch": retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=30),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True,
    ),
    "youtube_transcript": retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=2, max=60),
        retry=retry_if_exception_type((VideoUnavailable,)),
        reraise=True,
    ),
    "llm_inference": retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(initial=5, max=60),
        retry=retry_if_exception_type((InferenceOOMError, InferenceRuntimeError)),
        reraise=True,
    ),
}
```

#### 1.3 Shared Proxy Pool (Webshare Integration)
```python
# src/omega/proxy/proxy_pool.py
class SovereignProxyPool:
    """Rotating proxy pool with health checking and per-domain affinity."""
    
    def __init__(self, config: ProxyConfig):
        self.proxies: List[Proxy] = []
        self.domain_affinity: Dict[str, Proxy] = {}  # Sticky sessions
        self.health_check_interval = 300
    
    async def get_proxy(self, domain: str) -> Optional[Proxy]:
        # Prefer sticky proxy for domain
        if domain in self.domain_affinity:
            proxy = self.domain_affinity[domain]
            if await proxy.is_healthy():
                return proxy
        
        # Round-robin with health check
        for proxy in self.proxies:
            if await proxy.is_healthy():
                self.domain_affinity[domain] = proxy
                return proxy
        return None
```

---

### Phase 2: Pipeline Unification (P1 — 3 weeks)

#### 2.1 Universal Extraction Pipeline
```python
# src/omega/pipeline/universal_extractor.py
class UniversalExtractor:
    """Single extraction entry point for ALL source types."""
    
    def __init__(self):
        self.adapters = {
            "url": WebAdapter(SovereignScraper()),
            "youtube": YouTubeAdapter(TranscriptFetcher(), WhisperAdapter()),
            "file": FileAdapter(),
            "rss": RSSAdapter(),
            "pdf": PDFAdapter(),
        }
        self.cas = CASArchiver()
        self.verifier = TriangulationVerifier(EnrichmentEngine())
        self.enrichment = EnrichmentEngine()
    
    async def extract(self, source: SourceSpec) -> ExtractionResult:
        # 1. Compute content hash for CAS dedup
        raw_content = await self.adapters[source.type].fetch_raw(source)
        content_hash = sha256(raw_content).hexdigest()
        
        # 2. CAS check — return existing if deduplicated
        if await self.cas.exists(content_hash):
            return ExtractionResult(cached=True, cas_cid=content_hash, ...)
        
        # 3. Tiered extraction (T1→T2→T3) via adapter
        t1_result = await self.adapters[source.type].extract_tier1(raw_content)
        t3_result = await self.adapters[source.type].extract_tier3(raw_content)
        
        # 4. Triangulation verification
        verification = await self.verifier.verify(t1_result, t3_result, source.domain)
        if not verification.is_verified and verification.confidence_score < 0.4:
            return ExtractionResult(failed=True, reason="verification_failed")
        
        # 5. Enrichment
        metadata = await self.enrichment.enrich(t3_result.title, t3_result.authors)
        
        # 6. Store in CAS
        cas_cid = await self.cas.store(raw_content)
        
        return ExtractionResult(
            content=t3_result.content,
            metadata=metadata,
            quality_score=verification.confidence_score,
            cas_cid=cas_cid,
            verification=verification,
        )
```

#### 2.2 Unified Scheduler (APScheduler + Redis Streams)
```python
# src/omega/scheduler/unified_scheduler.py
class UnifiedKnowledgeScheduler:
    """Single scheduler for all background knowledge work."""
    
    JOB_DEFINITIONS = {
        "library_curation": JobDef(
            trigger="interval", minutes=30,
            func=curate_inbox_batch,
            max_instances=1,
            coalesce=True,
        ),
        "background_research": JobDef(
            trigger="interval", minutes=20,
            func=run_research_cycle,
            max_instances=1,
        ),
        "youtube_ingestion": JobDef(
            trigger="interval", minutes=15,
            func=process_youtube_queue,
            max_instances=2,  # Can parallelize playlist expansion
        ),
        "cross_pollination": JobDef(
            trigger="cron", hour="*/6",
            func=run_cross_pollination,
            max_instances=1,
        ),
    }
```

---

### Phase 3: Synergistic Capabilities (P2 — 4 weeks)

#### 3.1 Cross-Pollination Engine
```python
# src/omega/synthesis/cross_pollination.py
class CrossPollinationEngine:
    """Discovers and synthesizes connections across entity knowledge bases."""
    
    async def run_cycle(self):
        # 1. Find entities with overlapping topics
        topic_overlaps = await self._find_topic_overlaps(min_overlap=3)
        
        # 2. For each overlap, retrieve relevant documents from each entity
        for overlap in topic_overlaps:
            docs_by_entity = await self._gather_documents(overlap.entities, overlap.topic)
            
            # 3. Synthesize cross-entity perspective
            synthesis = await self._synthesize_cross_entity(
                topic=overlap.topic,
                documents=docs_by_entity,
                model="qwen3-4b-thinking"  # Local thinking model
            )
            
            # 4. Store as new CuratedDocument in each entity's library
            for entity_name, docs in docs_by_entity.items():
                await self.library.store(CuratedDocument(
                    title=f"Cross-Entity Synthesis: {overlap.topic}",
                    body=synthesis,
                    domain="synthesis",
                    tags=["cross_pollination", overlap.topic] + list(docs_by_entity.keys()),
                    quality_score=0.85,
                    metadata={"source_entities": list(docs_by_entity.keys())},
                ), entity_name=entity_name)
```

#### 3.2 Adaptive Quality Gates
```python
# src/omega/quality/adaptive_gates.py
class AdaptiveQualityGate:
    """Quality thresholds that adapt based on source type and entity context."""
    
    BASE_THRESHOLDS = {
        "web": 0.6,
        "youtube": 0.5,      # Transcripts are noisy
        "pdf": 0.7,          # Structured content
        "rss": 0.55,
        "file": 0.65,
    }
    
    ENTITY_MODIFIERS = {
        "kali": 0.1,         # Chaos — accept more noise for pattern detection
        "prometheus": -0.1,  # Will — demand higher precision
        "lucifer": 0.05,     # Gnosis — tolerate ambiguity
        "researcher": 0.0,   # Baseline
    }
    
    def get_threshold(self, source_type: str, entity_name: str) -> float:
        base = self.BASE_THRESHOLDS.get(source_type, 0.6)
        modifier = self.ENTITY_MODIFIERS.get(entity_name, 0.0)
        return max(0.3, min(0.9, base + modifier))
```

#### 3.3 Unified Observability Dashboard
```python
# src/omega/observability/knowledge_fabric_metrics.py
class KnowledgeFabricMetrics:
    """Unified metrics for the entire knowledge fabric."""
    
    METRICS = {
        # Throughput
        "extractions_total": Counter("source_type", "status"),
        "extractions_deduplicated": Counter("source_type"),
        "verifications_passed": Counter("source_type"),
        "verifications_failed": Counter("source_type", "reason"),
        
        # Quality
        "quality_score_distribution": Histogram("source_type", "entity"),
        "cas_hit_rate": Gauge(),
        
        # Resource
        "api_credits_consumed": Counter("provider", "operation"),
        "proxy_rotations": Counter("domain"),
        "circuit_breaker_state": Gauge("breaker_name"),
        
        # Synthesis
        "cross_pollination_events": Counter("topic"),
        "synthesis_quality": Histogram("topic"),
    }
```

---

## 🏗️ Infrastructure Requirements

### 1. **Proxy Infrastructure** (Critical for YouTube + Web Scale)
| Component | Spec | Cost |
|-----------|------|------|
| Webshare.io Residential | 50 GB/mo, 100 threads | ~$30/mo |
| Self-hosted rotation (Squid + custom) | 10 datacenter IPs | ~$5/mo (VPS) |
| **Total** | | **~$35/mo** |

### 2. **Local Transcription (Whisper.cpp)**
| Model | VRAM/RAM | Speed (RTX 3060) | Quality |
|-------|----------|------------------|---------|
| `tiny.en` | 1 GB | 15x realtime | Low |
| `base.en` | 1.5 GB | 8x realtime | Medium |
| `small.en` | 2.5 GB | 4x realtime | **Good** |
| `medium.en` | 5 GB | 2x realtime | **Excellent** |

**Recommendation**: `small.en` quantized (Q4_K_M) — fits in 12GB RAM, 4x realtime, excellent quality.

### 3. **Vector Search Upgrade**
| Current | Target | Effort |
|---------|--------|--------|
| MD5 Feature Hash (256-dim) | BGE-M3 (1024-dim) ONNX | 1 week |
| Qdrant MemoryVectorAdapter | Qdrant + INT8 quantization | 2 days |
| No payload indexes | Payload indexes on `entity_name`, `domain`, `topic` | 1 day |

### 4. **Unified Queue Backend**
| Current | Target |
|---------|--------|
| Inbox (file-based) | Redis Streams + Consumer Groups |
| YouTube Worker (Redis list) | Same Redis Streams |
| Background Researcher (in-memory queue) | Same Redis Streams |
| Ingestion Pipeline (direct calls) | Same Redis Streams |

---

## 📋 Implementation Roadmap

| Sprint | Focus | Deliverables | Owner |
|--------|-------|--------------|-------|
| **Sprint 1** | Resilience Unification | CircuitBreakerRegistry, RetryPolicies, ProxyPool | Ma'at/P3 |
| **Sprint 2** | CAS Integration | Wire CAS into ContentExtractor, YouTubeWorker, BackgroundResearcher | Ma'at/P2 |
| **Sprint 3** | Universal Extractor | Single entry point for all source types | Lilith/P6 |
| **Sprint 4** | Unified Scheduler | APScheduler + Redis Streams for all background work | Lilith/P9 |
| **Sprint 5** | YouTube Hardening | TranscriptFetcher + circuit breaker + backoff + proxy | Ma'at/P3 (GAP 1) |
| **Sprint 6** | Cross-Pollination | CrossPollinationEngine + adaptive quality gates | Lilith/P7 |
| **Sprint 7** | Vector Upgrade | BGE-M3 ONNX + Qdrant INT8 + payload indexes | Lilith/P6 |
| **Sprint 8** | Observability | KnowledgeFabricMetrics dashboard + alerts | Lilith/P8 |

---

## 🔱 Key Architectural Decisions (Record in PIVOT_LOG)

| Decision | Rationale | Heritage |
|----------|-----------|----------|
| **CAS as universal deduplication primitive** | SHA-256 content addressing eliminates redundant work across all subsystems | `[id-soft: doom3-2004] idHeap` |
| **TriangulationVerifier as sovereign verification kernel** | T1 vs T3 delta + authoritative metadata = consensus hallucination guard | `[heritage: sovereign-kliewer-2026] In-path governance` |
| **Unified CircuitBreakerRegistry** | Prevents cascade failures; single source of truth for resilience config | `[id-soft: doom3bfg-2012] Job-Worker Queue` |
| **Entity-scoped all operations** | Enables cross-pollination; respects sovereignty boundaries | `[heritage: a2a-standard-2025] Agent Card` |
| **Local-first extraction tiering** | T1 (Trafilatura) → T2 (Surgical) → T3 (Crawl4AI/Whisper) — pay for quality only when needed | `[heritage: logos-2026] Frame-Stripping` |
| **EnrichmentEngine as canonical metadata authority** | 4 free library APIs, zero keys — build once, use everywhere | `[heritage: spdx-standard-2021] SBOM` |

---

## 🎯 Next Actions for This Session

1. **Create `CircuitBreakerRegistry`** — `src/omega/resilience/circuit_registry.py`
2. **Wire `CASArchiver` into `ContentExtractor._extract_url()`** — 5-line change, massive dedup gain
3. **Add `ProxyPool` config to `youtube_worker.yaml`** — unblocks GAP 1
4. **Design `UniversalExtractor` interface** — unify all 4 source adapters
5. **Propose `UnifiedScheduler` spec** — consolidate 4 timers into 1

---

## 🔱 L3 Principles Distilled

- **L3-UNIFIED-PRIMITIVES**: CAS, Triangulation, Circuit Breaker, Retry Policy — build once, use everywhere
- **L3-ENTITY-SCOPED-ALL-THINGS**: No operation without `entity_name` — enables cross-pollination
- **L3-LOCAL-FIRST-TIERING**: T1→T2→T3 extraction — pay for quality only when needed
- **L3-SOVERIGN-SIEVE-AS-KERNEL**: Verification is not a feature — it's the architecture
- **L3-FORMAT-CONSENSUS-OVER-NOVELTY**: ZIP+JSON is the universal sovereign portability baseline (not Parquet)
- **L3-CALIBRATION-OVER-ACCURACY**: An uncalibrated judge (ECE 0.18) is worse than a calibrated one (ECE 0.06)
- **L3-REDIS-STREAMS-OVER-PUBSUB**: Pub/Sub drops messages; Streams + Consumer Groups = exactly-once + crash recovery
- **L3-CLASSICAL-ML-FOR-ROUTING**: TF-IDF+SVM (0MB, 93.2% acc, μs latency) beats LLM routing for intent classification

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_knowledge_fabric_synthesis ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
