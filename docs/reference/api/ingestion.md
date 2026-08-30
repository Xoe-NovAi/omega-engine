# API Reference: Ingestion Pipeline

> IngestionPipeline, SovereignScraper, TriangulationVerifier — the core ingestion API.

---

## Overview

The Omega Engine's ingestion pipeline is built on the **omega-sieve** standalone package (`pip install omega-sieve`), which provides the T1→T2→T3 tiered extraction and verification core. The engine wraps this with entity scoping, CAS persistence, MemoryStore integration, and Hivemind coordination.

**Standalone Package**: `omega-sieve` v0.1.0 — `docs/reference/api/omega_sieve.md`

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
| `pipeline.scraper` | `SovereignScraper` | Tiered web scraper (wraps `omega_sieve.SovereignScraper`) |
| `pipeline.verifier` | `TriangulationVerifier` | Sovereign-Sieve verification (wraps `omega_sieve.TriangulationVerifier`) |
| `pipeline.persistence` | `IngestionPersistence` | MemoryStore + sqlite-vec writer |
| `pipeline.breaker` | `IngestionCircuitBreaker` | Circuit breaker (5 failures → open) |
| `pipeline.sentry` | `SovereignSentry` | Pre-flight canary probes |
| `pipeline.budget` | `BudgetGuard` | Token/USD budget enforcement |

---

## SovereignScraper (Omega Wrapper)

**File**: `src/omega/ingestion/scraper.py`

Omega-specific wrapper around `omega_sieve.SovereignScraper` adding:
- Domain allowlist from WAD config (M2 Firewall compliance)
- CAS integration for automatic deduplication
- Entity-scoped metadata

### Constructor

```python
SovereignScraper(cas_archiver: Optional[CASArchiver] = None, domain_config_path: Optional[str] = None)
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

#### `scrape_auto(url: str, min_chars: int = 200) -> ScrapeResult`

Auto-tier: starts at T1, escalates to T2/T3 if content is insufficient.

---

## TriangulationVerifier (Omega Wrapper)

**File**: `src/omega/ingestion/verifier.py`

Omega-specific wrapper around `omega_sieve.TriangulationVerifier` adding:
- Entity-scoped verification context
- Integration with `EnrichmentEngine` for metadata triangulation

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

---

## Further Reading

- **Standalone Package**: `docs/reference/api/omega_sieve.md` — Full omega-sieve API
- **Architecture**: `docs/explanation/ingestion-architecture.md` — Pipeline flow diagram
- **CAS Reference**: `docs/reference/api/cas.md` — Content-Addressable Storage
- **Selective Hydration**: `docs/reference/selective-hydration.md` — L3 principle retrieval