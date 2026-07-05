# API Reference: Ingestion Pipeline

> IngestionPipeline, SovereignScraper, TriangulationVerifier — the core ingestion API.

---

## IngestionPipeline

**File**: `src/omega/ingestion/pipeline.py`

The orchestrator that wires all ingestion components and runs the resilience ladder.

### Constructor

```python
IngestionPipeline(config: IngestionConfig, extractor: BaseExtractor)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | `IngestionConfig` | Pipeline configuration (entity name, model, budget) |
| `extractor` | `BaseExtractor` | LLM extractor (e.g., `GoogleExtractor`) |

### Methods

#### `run_source(source) -> Optional[IngestionResult]`

Processes a single source through the full resilience ladder.

```python
pipeline = IngestionPipeline(config, extractor)
result = await pipeline.run_source("https://example.com/article")
# or
result = await pipeline.run_source(FileSource("path/to/doc.md"))
```

**Flow**: Sentry → Budget → T1 Scrape → T3 Scrape → Triangulate → CAS Store → Extract → Persist

**Returns**: `IngestionResult` or `None` if pre-flight fails.

### Internal Components

| Component | Access | Description |
|-----------|--------|-------------|
| `pipeline.cas` | `CASArchiver` | Content-Addressable Storage |
| `pipeline.scraper` | `SovereignScraper` | Tiered web scraper |
| `pipeline.verifier` | `TriangulationVerifier` | Sovereign-Sieve verification |
| `pipeline.persistence` | `IngestionPersistence` | MemoryStore + Qdrant writer |
| `pipeline.breaker` | `IngestionCircuitBreaker` | Circuit breaker (5 failures → open) |
| `pipeline.sentry` | `SovereignSentry` | Pre-flight canary probes |
| `pipeline.budget` | `BudgetGuard` | Token/USD budget enforcement |

---

## SovereignScraper

**File**: `src/omega/ingestion/scraper.py`

Hardened web scraper with tiered modes, powered by `crawl4ai` `AsyncWebCrawler`.

### Constructor

```python
SovereignScraper(cas_archiver: Optional[CASArchiver] = None)
```

### Methods

#### `scrape(url: str, tier: str = "fast") -> ScrapeResult`

Scrapes a URL at the specified tier.

| Tier | Speed | Depth | Use Case |
|------|-------|-------|----------|
| `"fast"` | ~2-5s | Basic content + metadata | Initial extraction, T1 |
| `"deep"` | ~10-30s | Full content + enriched metadata | Verification, T3 |
| `"surgical"` | ~5-15s | Interactive DOM manipulation | SPA/lazy-loaded content, T2 |

**Returns**: `ScrapeResult` dataclass:

```python
@dataclass
class ScrapeResult:
    success: bool
    content: str
    metadata: Dict[str, Any]
    latency_ms: float
    provider: str
    error: Optional[str] = None
```

---

## TriangulationVerifier

**File**: `src/omega/ingestion/verifier.py`

The Sovereign-Sieve. Verifies knowledge by triangulating T1 and T3 extraction results.

### Constructor

```python
TriangulationVerifier(enrichment_engine=None)
```

### Methods

#### `verify(t1_result: Dict, t3_result: Dict, domain_key: Optional[str] = None) -> VerificationResult`

Cross-checks T1 (fast) and T3 (deep) extraction results.

```python
verifier = TriangulationVerifier(EnrichmentEngine())
result = await verifier.verify(
    t1_result={"content": t1_content, "metadata": t1_meta},
    t3_result={"content": t3_content, "metadata": t3_meta},
    domain_key="engineering"
)
```

**Returns**: `VerificationResult` dataclass:

```python
@dataclass
class VerificationResult:
    is_verified: bool          # True if confidence > 0.7
    confidence_score: float    # 0.0 - 1.0
    resolved_metadata: Dict    # Triangulated author, date, DOI
    disputes: List[str]        # Contradictions found
    provenance_chain: List[str] # Source attribution chain
```

### Verification Logic

1. **Factual Delta**: Jaccard distance between T1 and T3 content. Delta > 0.3 = contradiction.
2. **Metadata Triangulation**: Cross-reference author, date, DOI across tiers + enrichment APIs.
3. **Consensus Hallucination Guard**: If all sources mirror the same original, confidence is halved.

---

## IngestionConfig

**File**: `src/omega/ingestion/ingestion_types.py`

```python
@dataclass
class IngestionConfig:
    entity_name: str          # Entity namespace for this ingestion
    model_name: str = "qwen3:1.7b"  # LLM for extraction
    max_tokens: int = 10000   # Budget cap
    max_cost_usd: float = 0.0 # Budget cap (0 = unlimited for local)
    extraction_schema: ExtractionSchema = EXTRACTION_SCHEMA
```

---

## ExtractionSchema

The 5-dimension extraction model used by all extractors:

| Dimension | Description |
|-----------|-------------|
| `technical_facts` | Code patterns, API specs, configuration details |
| `personality_patterns` | Writing style, voice, communication patterns |
| `gnosis_principles` | Universal principles, L3 distillations |
| `heritage_patterns` | id Software patterns, legacy attributions |
| `dpo_pairs` | Preferred/rejected response pairs for DPO training |

---

## Error Hierarchy

```
IngestionError (base)
├── SovereigntyError    — sovereignty violation (e.g., cloud-only source)
├── TransportError      — network/HTTP errors
├── ProviderServerError — LLM provider errors
├── SchemaError         — extraction schema mismatch
├── BudgetExceededError — token/USD budget exhausted
└── SentryFailure       — pre-flight probe failed
```
