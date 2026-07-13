# 🔱 omega-sieve — Sovereign-Sieve

**T1→T2→T3 tiered web research & extraction. Your data. Your computer. No cloud required.**

```
pip install omega-sieve
sieve research "latest developments in local LLM quantization"
```

---

## What is omega-sieve?

A sovereign, local-first web research toolkit that extracts clean text from any URL using a **tiered extraction pipeline**:

| Tier | Name | Tool | What It Does | Latency |
|------|------|------|-------------|---------|
| **T1** | Fast | Trafilatura | Clean article extraction from text-based pages | ~2s |
| **T2** | Surgical | Domain rules | Boundary-stripped extraction (Gutenberg, arXiv, etc.) | ~3s |
| **T3** | Deep | Crawl4AI + Playwright | Full JS rendering for SPAs and dynamic content | ~10-30s |

The **TriangulationVerifier** cross-references T1 vs T3 to catch hallucinations and contradictions.

### Why "Sieve"?

Just as a sieve separates grain from chaff, the Sovereign-Sieve separates **verified knowledge** from **noise** by running content through multiple independent extraction paths and comparing the results.

---

## Quick Start

```bash
# Install core
pip install omega-sieve

# Install with all features
pip install "omega-sieve[all]"

# Initialize config
sieve init

# Research a topic
sieve research "what is speculative decoding in LLMs"

# Scrape a URL
sieve scrape https://example.com/article

# Verify content across tiers
sieve verify https://example.com/article
```

### YouTube Extraction

```bash
# Install YouTube support
pip install "omega-sieve[youtube]"

# Get video metadata + captions
sieve youtube https://youtube.com/watch?v=...

# Full transcription (requires Whisper + VAD)
pip install "omega-sieve[transcription]"
sieve youtube https://youtube.com/watch?v=... --tier transcription
```

---

## Python API

```python
from omega_sieve import scrape, research
import anyio

async def main():
    # Auto-tier scrape (T1 → T2 → T3 escalation)
    result = await scrape("https://example.com/article")
    if result:
        print(result.content[:500])

    # Full research pipeline
    results = await research(
        "latest quantization methods 2026",
        max_sources=3,
        depth="balanced",
    )
    for source in results.successful_sources:
        print(f"✅ {source.url} ({source.latency_ms}ms)")

anyio.run(main())
```

### Verification

```python
from omega_sieve import SovereignScraper
from omega_sieve.verifier import TriangulationVerifier

scraper = SovereignScraper()
verifier = TriangulationVerifier()

results = await scraper.scrape_all("https://example.com")
t1, t3 = results["fast"], results["deep"]

if t1.success and t3.success:
    check = verifier.verify_t1_t3(t1, t3)
    print(f"Confidence: {check.confidence:.1%}")
    if not check.passed:
        print(f"Warnings: {check.warnings}")
```

---

## Configuration

Configuration lives at `~/.config/omega-sieve/config.yaml`:

```yaml
providers:
  exa:
    api_key: ""           # Optional: speeds up search
  firecrawl:
    api_key: ""           # Optional: speeds up extraction

searxng_url: "http://localhost:4004"  # Self-hosted SearXNG

budget:
  exa_max_calls: 100
  firecrawl_max_calls: 100

cache:
  enabled: true
  backend: sqlite         # sqlite | memory | none
  path: ~/.cache/omega-sieve/
  ttl_days: 7
```

**No API keys required.** The sieve runs fully on free, sovereign tools:
- **SearXNG** for metasearch (self-hosted, zero cost)
- **Trafilatura** for text extraction (MIT, 14k+ stars)
- **Crawl4AI** for JS rendering (Apache-2.0, `pip install`)

Add Exa and Firecrawl API keys only if you want faster/better search.

---

## Architecture

```
                    ┌─────────────────────┐
                    │    Research Query    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  SENTRY PROBE        │
                    │  Circuit breaker?    │
                    │  Budget available?   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  SEARCH               │
                    │  SearXNG → Exa → FC  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
       ┌──────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
       │  T1: Fast   │  │ T2: Surgical│  │ T3: Deep   │
       │  Trafilatura│  │ Domain rules│  │ Crawl4AI   │
       └──────┬──────┘  └─────┬──────┘  └─────┬──────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  TRIANGULATION      │
                    │  VERIFIER           │
                    │  T1 vs T3 cross-ref │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │    RESULT           │
                    │  Verified content   │
                    └────────────────────┘
```

---

## Extras

| Extra | Includes | Install |
|-------|----------|---------|
| `fast` | Trafilatura | `pip install "omega-sieve[fast]"` |
| `full` | Trafilatura + Crawl4AI | `pip install "omega-sieve[full]"` |
| `youtube` | yt-dlp + transcript API | `pip install "omega-sieve[youtube]"` |
| `transcription` | youtube + Whisper + VAD | `pip install "omega-sieve[transcription]"` |
| `all` | Everything | `pip install "omega-sieve[all]"` |

---

## License

Apache-2.0 — Free for any use, commercial or personal.

Built by the [Xoe-NovAi Foundation](https://github.com/Xoe-NovAi) as a community tool for sovereign AI. No telemetry. No phone-home. No cloud dependency.