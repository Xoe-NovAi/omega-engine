# API Reference: omega-sieve

> Standalone Sovereign-Sieve package for tiered web research & extraction.
> **Install**: `pip install omega-sieve` | **CLI**: `sieve --help` | **PyPI**: `omega-sieve`

---

## Quick Start

```python
from omega_sieve import scrape, research
import anyio

async def main():
    # Auto-tier scrape (T1 → T2 → T3 escalation)
    result = await scrape("https://example.com/article")
    if result:
        print(result.content[:500])

    # Full research pipeline
    results = await research("latest LLM quantization methods", max_sources=3, depth="balanced")
    for source in results.successful_sources:
        print(f"✅ {source.url} ({source.latency_ms}ms)")

anyio.run(main)
```

```bash
# CLI usage
sieve research "what is speculative decoding"
sieve scrape https://example.com --tier auto
sieve youtube https://youtube.com/watch?v=...
sieve verify https://example.com
sieve providers
sieve config
sieve init
```

---

## Core Classes

### SovereignScraper

**Unified scraper with automatic tier selection.**

```python
from omega_sieve import SovereignScraper

scraper = SovereignScraper()

# Specific tier
result = await scraper.scrape(url, tier="fast")   # T1: Trafilatura
result = await scraper.scrape(url, tier="surgical") # T2: Domain rules
result = await scraper.scrape(url, tier="deep")   # T3: Crawl4AI

# Auto-tier (recommended)
result = await scraper.scrape_auto(url, min_chars=200)

# All tiers for comparison
results = await scraper.scrape_all(url)
# {"fast": ScrapeResult, "surgical": ScrapeResult, "deep": ScrapeResult}
```

**Available tiers**: `scraper.available_tiers` → `["fast", "surgical", "deep"]`

---

### ScrapeResult

```python
@dataclass
class ScrapeResult:
    url: str
    content: str
    tier: str              # "fast" | "surgical" | "deep"
    success: bool
    error: Optional[str] = None
    provider_name: str = ""
    latency_ms: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not self.content.strip()

    def __bool__(self) -> bool:
        return self.success and not self.is_empty
```

---

### T1Scraper (Fast)

**Trafilatura-based extraction. No JS rendering.**

```python
from omega_sieve import T1Scraper

t1 = T1Scraper()
if t1.available:
    result = await t1.scrape(url)
```

**Dependencies**: `trafilatura` (installed with `pip install "omega-sieve[fast]"`)

---

### T2Scraper (Surgical)

**Domain-specific boundary stripping on top of T1.**

```python
from omega_sieve import T2Scraper

t2 = T2Scraper(domain_rules={
    "gutenberg": {"start": r"\*\*\* START OF.*\*\*\*", "end": r"\*\*\* END OF.*\*\*\*"},
    "arxiv": {"start": r"Abstract\s*:\s*", "end": ""},
})
result = await t2.scrape(url)
```

**Built-in domains**: `gutenberg`, `arxiv`, `pubmed`, `wikipedia`, `github`

---

### T3Scraper (Deep)

**Crawl4AI + Playwright. Full JS rendering.**

```python
from omega_sieve import T3Scraper

t3 = T3Scraper(timeout=30)
if t3.available:
    result = await t3.scrape(url)
```

**Dependencies**: `crawl4ai`, `playwright` (installed with `pip install "omega-sieve[full]"`)

**Note**: Runs in isolated subprocess to protect event loop (M1 compliance).

---

### TriangulationVerifier

**Cross-references T1 vs T3 for hallucination detection.**

```python
from omega_sieve import TriangulationVerifier

verifier = TriangulationVerifier(threshold=0.3)  # Jaccard distance threshold

result = verifier.verify_t1_t3(t1_result, t3_result)
# VerificationResult(passed, confidence, lexical_similarity, content_delta, warnings)

# Get best result
best, verification = verifier.best_result(t1_result, t3_result)
```

**VerificationResult**:

```python
@dataclass
class VerificationResult:
    passed: bool
    confidence: float              # 0.0 - 1.0
    lexical_similarity: float = 0.0
    semantic_similarity: float = 0.0
    content_delta: str = ""
    warnings: list[str] = field(default_factory=list)
```

---

### YouTubeSieve

**Tiered YouTube extraction: T1(meta) → T2(captions) → T3(Whisper+VAD).**

```python
from omega_sieve import YouTubeSieve

sieve = YouTubeSieve(data_dir="/tmp/omega-sieve-youtube")

# Auto-tier (recommended)
result = await sieve.extract(url, tier="auto")

# Specific tier
result = await sieve.extract(url, tier="metadata")      # T1: yt-dlp --flat-playlist
result = await sieve.extract(url, tier="captions")      # T2: youtube-transcript-api
result = await sieve.extract(url, tier="transcription") # T3: Whisper + Silero VAD
```

**YouTubeResult**:

```python
@dataclass
class YouTubeResult:
    video_id: str
    metadata: YouTubeMetadata
    transcript: str = ""
    tier: str = ""           # "metadata" | "captions" | "transcription"
    success: bool = False
    error: Optional[str] = None
    latency_ms: int = 0

    @property
    def has_content(self) -> bool:
        return bool(self.transcript.strip())
```

**YouTubeMetadata**:

```python
@dataclass
class YouTubeMetadata:
    video_id: str
    title: str = ""
    channel: str = ""
    duration: int = 0
    view_count: int = 0
    description: str = ""
    tags: list[str] = field(default_factory=list)
    upload_date: str = ""
```

**Dependencies**:
- T1: `yt-dlp` (`pip install "omega-sieve[youtube]"`)
- T2: `youtube-transcript-api` (same extra)
- T3: `whisper-cpp-python`, `silero-vad` (`pip install "omega-sieve[transcription]"`)

---

### SovereignSentry

**Pre-flight canary probes for external providers.**

```python
from omega_sieve import SovereignSentry

sentry = SovereignSentry()

result = await sentry.probe("exa", api_key="...")
result = await sentry.probe("firecrawl", api_key="...")
result = await sentry.probe("searxng")  # Uses config.searxng_url
```

**SentryResult**:

```python
@dataclass
class SentryResult:
    provider: str
    healthy: bool
    latency_ms: int = 0
    error: Optional[str] = None
```

**Circuit Breaker**: `sentry.get_circuit_breaker(provider)` → `CircuitBreaker`

---

### BudgetGuard

**Atomic API credit tracking across agents.**

```python
from omega_sieve import BudgetGuard, SieveConfig

config = SieveConfig()
budget = BudgetGuard(config)

# Check before spending
if await budget.can_afford("exa", estimated_cost=1):
    await budget.spend("exa", cost=1)

# Get remaining
remaining = await budget.remaining("exa")

# Daily reset
await budget.reset_daily()
```

**Config** (from `SieveConfig.budget`):

```python
BudgetConfig(
    exa_max_calls=100,
    firecrawl_max_calls=100,
    openrouter_max_calls=500,
    warn_at=0.8  # Warn at 80% consumption
)
```

---

### SovereignProxyPool

**Domain-affinity proxy rotation.**

```python
from omega_sieve import SovereignProxyPool, ProxyConfig

pool = SovereignProxyPool()
pool.configure([
    ProxyConfig(url="http://proxy1:8080", type="datacenter"),
    ProxyConfig(url="http://proxy2:8080", type="residential"),
])

proxy = pool.get_proxy("https://example.com/page1")
# Returns proxy with domain affinity (sticky session)

pool.record_success("https://example.com/page1")
pool.record_failure("https://example.com/page1")  # After 3 failures, rotates
```

**ProxyConfig**:

```python
@dataclass
class ProxyConfig:
    url: str
    type: str = "datacenter"  # "datacenter" | "residential"
    username: str = ""
    password: str = ""
    region: str = "auto"
```

---

## Research Pipeline

### Researcher

**Full research: search → scrape → verify.**

```python
from omega_sieve import Researcher, SovereignScraper

researcher = Researcher(scraper=SovereignScraper())

result = await researcher.research(
    query="latest quantization methods 2026",
    max_sources=5,
    depth="balanced"  # "quick" | "balanced" | "deep"
)
```

**ResearchResult**:

```python
@dataclass
class ResearchResult:
    query: str
    sources: list[ScrapeResult]
    depth: str
    latency_ms: int
    error: Optional[str] = None

    @property
    def successful_sources(self) -> list[ScrapeResult]:
        return [s for s in self.sources if s.success]
```

---

## Configuration

### SieveConfig

```python
from omega_sieve import SieveConfig, load_config, init_config

# Load from ~/.config/omega-sieve/config.yaml
config = load_config()

# Or create default
config = init_config()  # Creates file if missing
```

**Config structure**:

```yaml
providers:
  exa:
    api_key: ""           # From EXA_API_KEY env var
    base_url: ""
    enabled: true
  firecrawl:
    api_key: ""           # From FIRECRAWL_API_KEY env var
    base_url: ""
    enabled: true
  openrouter:
    api_key: ""           # From OPENROUTER_API_KEY env var
    base_url: ""
    enabled: true

budget:
  exa_max_calls: 100
  firecrawl_max_calls: 100
  openrouter_max_calls: 500
  warn_at: 0.8

proxy:
  enabled: false
  datacenter: []
  residential: []

cache:
  enabled: true
  backend: "sqlite"       # "sqlite" | "memory" | "none"
  path: "~/.cache/omega-sieve/"
  ttl_days: 7

domains:
  allowlist:
    gutenberg: "^https?://[^.]*\.gutenberg\.org/.*$"
    arxiv: "^https?://arxiv\.org/.*$"
    pubmed: "^https?://pubmed\.ncbi\.nlm\.nih\.gov/.*$"
    wikipedia: "^https?://[^.]*\.wikipedia\.org/.*$"
    github: "^https?://github\.com/.*$"

searxng_url: "http://localhost:4004"  # From SEARXNG_URL env var
```

---

## Convenience Functions

```python
from omega_sieve import scrape, research

# Auto-tier scrape
result = await scrape(url, tier="auto")

# Full research
results = await research(query, max_sources=5, depth="balanced")
```

---

## CLI Reference

```bash
sieve research "query" [--max 5] [--depth balanced] [--output results.json]
sieve scrape <url> [--tier auto] [--output file.txt]
sieve youtube <url> [--tier auto]
sieve verify <url>                    # T1 vs T3 triangulation
sieve providers                       # List available tiers
sieve config                          # Show current config
sieve init                            # Initialize config file
sieve --version
```

---

## Extras

| Extra | Includes | Install |
|-------|----------|---------|
| `fast` | Trafilatura | `pip install "omega-sieve[fast]"` |
| `full` | fast + Crawl4AI | `pip install "omega-sieve[full]"` |
| `youtube` | yt-dlp, youtube-transcript-api | `pip install "omega-sieve[youtube]"` |
| `transcription` | youtube + Whisper + VAD | `pip install "omega-sieve[transcription]"` |
| `all` | Everything | `pip install "omega-sieve[all]"` |

---

## Error Hierarchy

```python
from omega_sieve.errors import (
    SieveError,           # Base
    ScrapeError,          # Scraping failures
    VerificationError,    # Verification failures
    ProviderError,        # External provider errors
    BudgetExceededError,  # Budget exhausted
    ProxyError,           # Proxy configuration errors
    ConfigError,          # Configuration errors
    YouTubeError,         # YouTube extraction errors
    TranscriptionError,   # Transcription failures
)
```

---

## Integration with Omega Engine

The Omega Engine wraps `omega_sieve` with:

| Omega Layer | Purpose |
|-------------|---------|
| `src/omega/ingestion/scraper.py` | Entity scoping, CAS persistence, Hivemind coordination |
| `src/omega/ingestion/verifier.py` | EnrichmentEngine integration for metadata triangulation |
| `src/omega/ingestion/pipeline.py` | Full resilience ladder (Sentry → Budget → T1 → T3 → Verify → CAS → Extract → Persist) |
| `src/omega/ingestion/guards.py` | Omega-specific BudgetGuard with Redis backend |

**Import pattern**:

```python
# Standalone
from omega_sieve import SovereignScraper

# Omega Engine
from omega.ingestion.scraper import SovereignScraper  # Wrapper
```