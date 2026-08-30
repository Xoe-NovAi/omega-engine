<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Curation Pipeline Tooling Comparison
# ⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_curation_tooling ⬡ CURATION-REPORT
**AP Token**: AP-CURATION-TOOLING-v1.0.0
**Date**: 2026-06-22
**Hardware Context**: AMD Ryzen 7 5700U (8C/16T Zen 2, AVX2), 14Gi RAM (~12Gi for AI), no GPU, ~17GB free on omega_library
**License Baseline**: Omega Engine = Apache 2.0

---

## §0 Executive Summary

**The primary crawler should be crawl4ai, with Trafilatura as a lightweight extraction fallback, and the existing MarkItDown + pdfminer.six for document parsing.** Firecrawl's self-hosted offering is a heavy-weight Docker-based infrastructure play (Redis, PostgreSQL, Playwright, Chromium) that consumes 4-8GB RAM — too heavy for the 5700U's 14Gi budget. It's better suited for cloud-proxy anti-bot scraping, which is not this pipeline's primary use case. **Crawl4AI is MIT/Apache-2.0 licensed, runs on `pip install` with Playwright, is fully local/sovereign, and aligns perfectly with the engine's AnyIO-native architecture.**

**The real leverage** doesn't come from the crawler at all — it comes from the 10 free library API clients (Gutenberg, Open Library, Internet Archive, arXiv) already recovered from the legacy curation pipeline. These provide high-quality, structured book and paper metadata without any crawling. The crawler is only needed for general web content. The recommended architecture is: library API clients for discovery → crawl4ai for web content when needed → Trafilatura for fast article extraction → MarkItDown for document parsing → FTS5 for indexing.

**The supporting ecosystem** is equally critical. The pipeline needs: `fast-langdetect` (45-60MB, 95% accuracy, offline) for language identification; `textstat` (pure Python, zero deps) for quality scoring; SHA256 hashing for exact dedup with optional simhash for near-duplicate detection; systemd timers (already proven) for scheduling; and a SQLite-based queue (avoid Redis overhead). The total additional RAM for the full pipeline is ~150MB — negligible against the 14Gi budget.

---

## §1 Firecrawl vs crawl4ai — Direct Comparison

### Core Capabilities

| Aspect | Firecrawl | crawl4ai |
|--------|-----------|----------|
| **Architecture** | Node.js API server + Playwright + Redis + PostgreSQL | Python library + Playwright + Chromium |
| **Install** | Docker Compose (6+ containers), or cloud SaaS API key | `pip install crawl4ai && crawl4ai-setup` |
| **License** | AGPL-3.0 | Apache-2.0 |
| **GitHub Stars** | ~115K | ~69K |
| **Primary Output** | Markdown, JSON, HTML, screenshots | Markdown, JSON, structured extraction |
| **JavaScript Rendering** | ✅ Built-in via Playwright | ✅ Built-in via Playwright |
| **Deep Crawl** | ✅ Multi-page with map → crawl | ✅ BFS/DFS/BestFirst strategies |
| **Structured Extraction** | ✅ JSON schema extraction (+ LLM) | ✅ CSS/XPath + LLM extraction |
| **Anti-Bot** | ✅ Fire-engine (cloud), proxy rotation | ❌ BYO proxies, weak built-in |
| **Search API** | ✅ (/v1/search) with SearXNG support | ❌ Not built-in |
| **Self-Hosted** | ✅ AGPL open source, Docker required | ✅ pip install, no cloud needed |
| **SDKs** | Python, JS/TS, Go, Rust | Python only |
| **CLI** | ✅ `npx firecrawl-mcp` | ✅ `crwl` command |
| **RAM (idle)** | ~500MB - 1GB (5 services) | ~300MB (Chromium + Python) |
| **Disk (Docker)** | ~2GB (5 images) | ~1.5GB (Chromium + Python deps) |

### Are They Direct Competitors?

**No — they do different jobs, though there is overlap.**

**Firecrawl** is a **full-stack scraping product** — an API server with queue management, job tracking, authentication, rate limiting, proxy rotation, and a cloud offering. You deploy it as an infrastructure service (Docker) and hit its REST API. It's designed for teams running scraping operations at scale, particularly against anti-bot-protected sites. The self-hosted version is missing `/agent`, `/browser`, and Fire-engine features.

**crawl4ai** is a **Python library for AI-ready content extraction** — you `import` it into your code, configure a browser context, and extract content inline. It's designed for Python developers building automated extraction into their data pipelines, RAG systems, or AI agents. It has no queue, no auth, no multi-tenant — it's a library, not a service.

**For the Omega Engine's curation worker**, crawl4ai is the better fit because:
1. It's a library, importable into the AnyIO-native worker — no Docker dependency
2. Apache-2.0 license matches the engine's license
3. Lighter resource footprint (one Chromium process)
4. No infrastructure to manage (Redis, PostgreSQL, etc.)

### Firecrawl Self-Hosting Assessment

**Can it be self-hosted?** Yes — fully open source under AGPL-3.0. Requires Docker Compose with 5 services:
- `api-server` (Node.js Express)
- `queue-worker` (BullMQ job processor)
- `scrape-worker` (Playwright-based scraper)
- `playwright-service` (browser management)
- `redis` (job queues + rate limiting + cache)

**Requirements**: 8GB+ RAM recommended, 2+ CPU cores, Docker + Docker Compose. The self-hosted version supports all API endpoints (+ local LLMs via Ollama) but **not** the `/agent`, `/browser`, or Fire-engine features.

**Capability gap**: Self-hosted Firecrawl is missing ~20% of cloud features, specifically the intelligent anti-bot infrastructure. For general web content, this is acceptable. For heavy anti-bot sites, it's a limitation.

**Verdict**: Run-only if needed for specific anti-bot-heavy targets. Too heavy for default use.

### crawl4ai Sovereignty Assessment

**Truly local/sovereign**: ✅ Zero cloud dependency. `pip install` + `playwright install chromium`. Everything runs locally, can run fully offline with no phone-home. The library itself is Apache-2.0. Playwright is Apache-2.0 as well.

**Telemetry**: ✅ None. The open-source library has no telemetry. The closed-beta Cloud API is a separate service — using the library does not require it. The privacy policy explicitly states the open-source library is governed by its own Apache-2.0 license, not the cloud terms.

**CPU-only performance**: Runs on Playwright + Chromium, which is a real browser. On the 5700U, expect:
- Page load + render: 1-3 seconds
- Content extraction: 0.1-0.5 seconds  
- Full crawl (10 pages): 15-30 seconds
- RAM during crawl: ~300-500MB (Chromium)

This is acceptable for a background worker that runs every 15-30 minutes on 1-5 pages per cycle.

---

## §2 Sovereignty & License Assessment

| Tool | License | Sovereign? | Telemetry | Can Run Offline? | AGPL Risk? |
|------|---------|-----------|-----------|------------------|------------|
| **crawl4ai** | Apache-2.0 | ✅ Fully | None | ✅ Yes | None |
| **Firecrawl** | AGPL-3.0 | ⚠️ With Docker | PostHog (configurable) | ⚠️ Needs infra | ⚠️ AGPL > Apache 2.0 (distribution risk) |
| **Trafilatura** | Apache-2.0 | ✅ Fully | None | ✅ Yes | None |
| **markitdown** | MIT | ✅ Fully | None | ✅ Yes | None |
| **newspaper4k** | MIT | ✅ Fully | None | ✅ Yes (except NLP model) | None |
| **readability-lxml** | Apache-2.0 | ✅ Fully | None | ✅ Yes | None |
| **scrapy** | BSD | ✅ Fully | None | ✅ Yes | None |
| **tika-python** | Apache-2.0 | ✅ Fully | None | ✅ Yes (heavy) | None |
| **yt-dlp** | Unlicense | ✅ Fully | None | ✅ Yes (with FFmpeg) | None |
| **pdfplumber** | MIT | ✅ Fully | None | ✅ Yes | None |
| **PyMuPDF** | AGPL-3.0 / Commercial | ⚠️ | None | ✅ Yes | ⚠️ AGPL if not licensed |
| **SearXNG** | AGPL-3.0 | ✅ Fully | None | ✅ Yes (self-host) | None (self-hosted, not distributed) |
| **beautifulsoup4** | MIT | ✅ Fully | None | ✅ Yes | None |
| **ebooklib** | AGPL-3.0 | ⚠️ | None | ✅ Yes | ⚠️ AGPL |
| **pandoc** | GPL-2.0 | ⚠️ | None | ✅ Yes | ⚠️ GPL |

### AGPL Risk Analysis

The Omega Engine is Apache-2.0. AGPL-3.0/GPL-2.0 code **cannot be imported/copied** into the engine's source — it would force the entire project to AGPL. However, these tools can be:
- Called as **subprocesses** (pandoc, yt-dlp, ebook-convert)
- Used as **external services** (SearXNG as Docker container)
- Used as **pip dependencies** (the AGPL license applies to the library itself, not to code that calls it via API)

**Firecrawl AGPL note**: Using the self-hosted Firecrawl Docker containers is fine internally (not distributed). The AGPL risk triggers if you modify and distribute the code. The Omega Engine does not distribute Firecrawl — it runs it internally or calls the cloud API.

**ebooklib AGPL note**: AGPL-3.0. However, MarkItDown already handles EPUB conversion. If you need standalone EPUB processing, use MarkItDown's EPUB support (MIT) or call ebook-convert (GPL, subprocess) instead.

**PyMuPDF (fitz)**: AGPL-3.0 for open-source use without commercial license. The engine already has a fallback to pdfminer.six (MIT). Recommend avoiding PyMuPDF unless explicitly licensed.

---

## §3 Other Tool Options — Deep Dives

### 3.1 Trafilatura — **RECOMMENDED as lightweight extraction fallback**

- **License**: Apache-2.0 ✅
- **Stars**: 6.2K
- **Install**: `pip install trafilatura[all]`
- **RAM**: ~30-50MB
- **Key strength**: **Highest F1 (0.958) on ScrapingHub article extraction benchmark** — beats readability (0.922) and newspaper4k (0.949). Best heuristic-based extraction with no ML dependency.
- **Key features**: Metadata extraction (title, author, date), sitemap/feed crawling, parallel processing, Markdown/JSON/XML output, language detection built-in.
- **CPU performance**: Fastest of all JS-free extractors. Rust port does 71 articles/second.
- **Why for Omega**: Perfect for fast extraction of book descriptions, article text, and structured content WITHOUT loading a full browser. Use as T1 extraction (try Trafilatura first, fall back to crawl4ai only if content is missing).
- **Reference**: `trafilatura.fetch_url()` + `trafilatura.extract(html, output_format='markdown')` — 2 lines of code.

### 3.2 Microsoft MarkItDown — **ALREADY INTEGRATED, USE IT MORE**

- **License**: MIT ✅
- **Stars**: 157K
- **Install**: `pip install markitdown[all]`
- **Key strength**: Converts 15+ file formats to Markdown — PDF, DOCX, XLSX, PPTX, HTML, EPUB, images (OCR), audio, YouTube transcripts, ZIP. Single API.
- **Current status**: Already referenced in the engine's architecture. `markitdown` is a dependency in `pyproject.toml`. ContentExtractor should be upgraded to use MarkItDown instead of raw HTML parsing.
- **Why for Omega**: Dramatically simplifies the extractor. One call to `MarkItDown().convert(path)` replaces 100+ lines of fragile regex parsing. Handles EPUB books natively (replacing need for ebooklib).
- **Implementation note**: Optional deps per format — install only what's needed (`pip install markitdown[pdf,epub]` — ~30MB).

### 3.3 newspaper4k — **RECOMMENDED for news/current events**

- **License**: MIT ✅
- **Stars**: 3.7K (active fork)
- **Install**: `pip install newspaper4k`
- **Key strength**: Object-oriented article extraction with built-in NLP (keywords, summary). Best for news websites. 0.949 F1 score (ScrapingHub benchmark).
- **CPU performance**: Lightweight — no browser dependency. Uses `requests` + `lxml`.
- **Why for Omega**: Perfect for the background researcher to extract clean text from news, blogs, and current events articles. Faster than crawl4ai (no browser) with comparable quality.
- **Limitation**: Doesn't handle JS-rendered pages natively. Needs Playwright integration for SPAs.

### 3.4 Scrapy — **NOT RECOMMENDED for this pipeline**

- **License**: BSD ✅
- **Stars**: 53K
- **Why not**: Scrapy is a full **crawling framework** — it has its own event loop, middleware pipeline, item pipelines, and shell. It fights the AnyIO-native architecture rather than complementing it. For the curation worker's needs (fetch page → extract text → save), Scrapy is overengineered. Use crawl4ai for JS rendering or Trafilatura for quick extraction instead.

### 3.5 SearXNG — **ALREADY INTEGRATED, FIREWALL BEHIND M9**

- **License**: AGPL-3.0 (self-hosted, not distributed — OK)
- **Key strength**: Self-hosted meta-search engine — no Google dependencies, complete privacy.
- **Current status**: Already wired into background researcher + Firecrawl. Used as search source.
- **Why for Omega**: Fills the "discovery" gap — search across 100+ engines without phoning home. The @m9_safe decorator is already applied.

### 3.6 yt-dlp — **RECOMMENDED for audio/video content**

- **License**: Unlicense (public domain) ✅
- **Install**: `pip install yt-dlp`
- **Key strength**: Downloads audio/video from YouTube + 1000+ sites. Can extract audio for transcription (via whisper or MarkItDown).
- **Why for Omega**: The legacy crawl.py already had YouTube extraction. yt-dlp is the successor to youtube-dl, actively maintained, and handles lectures/talks/podcasts that are rich knowledge sources.
- **Usage**: Called as subprocess (cURL-like), not imported as library. Avoids dependency conflicts.

### 3.7 tika-python — **NOT RECOMMENDED for this pipeline**

- **License**: Apache-2.0
- **Why not**: Apache Tika requires a Java runtime (JRE). This adds ~200MB of Java dependencies to the Python environment. While Tika is excellent for document parsing, MarkItDown does the same job without requiring Java. Skip.

### 3.8 BeautifulSoup4 + lxml — **ALREADY DEPENDENCY, KEEP FOR FALLBACK**

- **License**: MIT/BSD ✅
- **Current status**: Already available in the environment (lxml and beautifulsoup4 are in `pyproject.toml`). The ContentExtractor currently uses raw regex for parsing — should be upgraded to use BeautifulSoup for HTML parsing fallback.
- **Why needed**: When crawl4ai/Trafilatura fail (e.g., malformed HTML), BeautifulSoup can still extract content.

### 3.9 pdfplumber / pdfminer.six — **ALREADY IN USE**

- **License**: MIT ✅
- **Current status**: Both are referenced in ContentExtractor (pdfminer.six as primary, PyMuPDF as fallback). MarkItDown uses pdfminer.six for PDF extraction internally.
- **Note**: Prefer MarkItDown for PDFs (it uses pdfminer.six internally but provides better structure preservation). Use pdfminer.six directly only when MarkItDown is unavailable.

---

## §4 Supporting Tools Ecosystem

### 4.1 Scheduling & Orchestration

| Tool | Recommendation | Rationale |
|------|---------------|-----------|
| **Systemd timers** | ✅ **PRIMARY** | Already proven (omega-research.timer). No Python dependency, survives crashes. |
| **APScheduler** | ⚠️ Secondary | Already in engine dependencies but adds complexity. Use for in-process scheduling only. |
| **Cron** | ⚠️ Fallback | Works but no logging/journald integration like systemd |

**Verdict**: Use systemd timers for the library worker (parallel to `omega-research.timer`), with an AnyIO-native worker loop that checks the queue on each tick.

### 4.2 Rate Limiting

| Tool | Recommendation | Rationale |
|------|---------------|-----------|
| **Custom token bucket** | ✅ **PRIMARY** | Simple, no deps, integrates with AnyIO's `sleep()`. 50 lines of code. |
| **aiolimiter** | ✅ ✅ Same effect | Third-party, AnyIO-compatible, 1 dependency. Good alternative. |
| **tenacity** | ⚠️ Retry only | Already in legacy code. Use for retry (exponential backoff), not for rate limiting. |

**Verdict**: Implement a simple token-bucket rate limiter (one per API domain). The legacy code's `time.sleep(min_interval)` pattern should be upgraded to use `anyio.sleep()` with a token bucket.

### 4.3 Content Deduplication

| Method | Use Case | Performance | Implementation |
|--------|----------|-------------|----------------|
| **SHA256 hash (full content)** | Exact duplicates | O(n), 10MB/s | `hashlib.sha256()` — available, no install |
| **SHA256 hash (normalized text)** | Near-exact (minor whitespace changes) | O(n), 10MB/s | Normalize (strip tags, collapse whitespace) → hash |
| **Simhash** | Near-duplicate detection (95%+ similar) | O(n), ~50K docs/s | `pip install simhash` (pure Python, MIT, 1K stars) |
| **MinHash + LSH** | Near-duplicate at scale (millions) | O(n log n), slower | `pip install datasketch` — overkill for Omega scale |

**Verdict for Omega**: Use SHA256 on normalized content for exact dedup (primary). Add simhash for near-duplicate detection if needed (the library worker processes dozens, not millions, of documents — exact dedup is sufficient for MVP).

### 4.4 Language Detection

| Tool | Accuracy | RAM | Speed | License | Recommendation |
|------|----------|-----|-------|---------|----------------|
| **fast-langdetect** (fastText) | 95%+ | 45-60MB (lite), 170-210MB (full) | Very fast | MIT | ✅ **PRIMARY** |
| **lingua-py** | 99%+ (long texts) | ~200MB (full model) | Slow on first load | MIT | ✅ BEST ACCURACY |
| **langdetect** | ~80% | ~10MB | Fast | Apache-2.0 | ⚠️ Fallback only |
| **CLD2/CLD3** | ~90% | ~30MB | Very fast | Apache-2.0 | ✅ Good balance |
| **Trafilatura built-in** | ~85% | Included | Fast | Apache-2.0 | ✅ Use when Trafilatura is already loaded |

**Verdict**: Use `fast-langdetect` in "lite" mode (45MB, 95% accuracy, offline). It's fast, MIT-licensed, and good enough for filtering purposes. Upgrade to lingua-py only if accuracy requirements demand it.

### 4.5 Content Classification

| Method | Accuracy | Training Needed | RAM | Recommendation |
|--------|----------|----------------|-----|----------------|
| **Keyword-based (regex + scoring)** | ~80% for domain classification | No | <1MB | ✅ **PRIMARY** — legacy code style |
| **Qwen-0.6B LLM** | ~90%+ | No | ~500MB | ✅ **For deep classification** |
| **fastText classifier** | ~85-90% | Yes (labeled data) | ~10MB | ⚠️ If keyword rules insufficient |
| **scikit-learn (TF-IDF + SVM)** | ~85% | Yes | ~50MB | ⚠️ If labeled data available |

**Verdict**: Start with keyword-based classification (the legacy crawler_curation.py had a working signal-based classifier with 5 factors — freshness, completeness, authority, structure, accessibility). Upgrade to Qwen-0.6B for edge cases. The 1.7B model can be used for batch reclassification during idle cycles.

### 4.6 Metadata Extraction

| Tool | What It Extracts | Effort |
|------|------------------|--------|
| **Gutendex API** | Gutenberg books: title, author, subjects, language, downloads | Already recovered — ~20 lines to port |
| **Open Library API** | Books by ISBN: title, author, publish date, subjects | Already recovered — ~30 lines to port |
| **Internet Archive API** | Full metadata: creator, date, subjects, language | Already recovered — ~40 lines to port |
| **Crossref API** | Academic papers: DOI, title, authors, journal, year | Free, no key needed |
| **arXiv API** | Papers: title, authors, abstract, categories | Free, no key needed, structured XML |
| **PubMed API** | Medical papers: title, authors, abstract, MeSH terms | Free, no key needed |
| **DOI regex extraction** | Any document text | Built-in — `re.search(r'10\.\d{4,}/[^\s]+', text)` |

**Verdict**: The 10 library API clients from legacy code cover almost everything needed. Port them first — they require zero API keys. Crossref and arXiv are high-value additions.

### 4.7 EPUB Processing

| Tool | License | Recommendation |
|------|---------|----------------|
| **MarkItDown (EPUB support)** | MIT | ✅ **PRIMARY** — already in engine, handles EPUB natively |
| **ebooklib** | AGPL-3.0 | ⚠️ Use only when MarkItDown insufficient |
| **calibre (ebook-convert)** | GPL-2.0 | ⚠️ Heavy (~500MB install), use as subprocess for bulk conversion |
| **pandoc** | GPL-2.0 | ⚠️ Subprocess for format conversion |

**Verdict**: MarkItDown handles EPUB natively — no additional library needed for basic EPUB text extraction. Use calibre's `ebook-convert` as a subprocess only if you need format conversion (EPUB→PDF).

### 4.8 Quality Scoring

| Tool | Metrics | RAM | Recommendation |
|------|---------|-----|----------------|
| **textstat** | Flesch-Kincaid, Gunning Fog, SMOG, Coleman-Liau, ARI | <5MB | ✅ **PRIMARY** — 7+ metrics, pure Python |
| **textstat-py** | Same + sentiment, lexical diversity, passive voice | <1MB | ✅ LIGHTER ALTERNATIVE — zero deps, single file |
| **Legacy quality scorer** | Freshness, completeness, authority, structure, accessibility | <1MB | ✅ ALREADY RECOVERED — 5-factor model from crawler_curation.py |

**Verdict**: Use `textstat-py` for readability scoring (zero dependencies, single file, covers all readability formulas) combined with the legacy quality scorer (freshness, completeness, authority, structure, accessibility). This gives a comprehensive quality score without heavy dependencies.

### 4.9 Storage & Indexing

| Tool | Query Speed | Index Size | License | Recommendation |
|------|-------------|------------|---------|----------------|
| **SQLite FTS5** | Fast (10ms for 10K docs) | ~50% of text size | Public domain | ✅ **ALREADY IN USE** — stay with FTS5 |
| **Tantivy** | Very fast (1ms for 10K docs) | ~30% of text size | MIT | ⚠️ Overkill for current scale |
| **Whoosh** | Moderate | ~60% of text size | BSD | ⚠️ Pure Python, slower than FTS5 |
| **Meilisearch** | Very fast | ~20% of text size | MIT | ❌ Requires a running server (Rust binary) |

**Verdict**: FTS5 is already integrated and works well for the expected document volume (hundreds to low thousands). The hybrid FTS5 + embedding search pipeline is already built. No upgrade needed. Tantivy could be evaluated if document volume exceeds 100K and search latency becomes a concern.

### 4.10 Queue & Persistence

| Tool | Persistence | Crash Recovery | Complexity | Recommendation |
|------|-------------|----------------|------------|----------------|
| **SQLite + JSON** | ✅ Durable | ✅ Atomic writes | Low | ✅ **PRIMARY** — no Redis needed |
| **Redis (BLPop)** | ⚠️ Volatile (unless RDB/AOF) | ⚠️ Loss possible | Medium | ❌ Overhead for single-machine use |
| **File-based JSONL** | ✅ Durable | ✅ Append-only | Minimal | ✅ Good for logging queue operations |
| **APScheduler job store** | ✅ SQLite-backed | ✅ | Medium | ⚠️ Already in deps, use for scheduling |

**Verdict**: Use a SQLite-backed queue with atomic `.tmp → .json` file renames (the pattern already used by the engine). The legacy Redis BLPop pattern is overengineered for a single-machine background worker. Avoid Redis unless multi-machine distribution becomes necessary.

### 4.11 Monitoring

| Tool | Effort | What It Tells You | Recommendation |
|------|--------|-------------------|----------------|
| **JSONL logging** (custom) | Low | Every job: timestamp, source, status, duration, errors | ✅ **PRIMARY** — 5 lines of code per log |
| **Omega ObservabilityEngine** | Already exists | Trace IDs, events, provider stats | ✅ **ALREADY INTEGRATED** |
| **Prometheus + grafana** | Medium | Real-time metrics, dashboards | ❌ Overkill — single machine, 2 workers |
| **Systemd journal** | Zero | Crash logs, stdout/stderr | ✅ **ALREADY AVAILABLE** |

**Verdict**: Use JSONL per-worker logs (appended to `data/logs/library-worker/`) + systemd journald for crash monitoring. The ObservabilityEngine already has trace_id propagation. No need for Prometheus at this scale.

---

## §5 Sovereignty Heat Map

### 🟢 GREEN — Fully Sovereign (Apache-2.0/MIT/BSD, zero cloud dependency)
| Tool | Notes |
|------|-------|
| crawl4ai | Apache-2.0, local, no telemetry |
| Trafilatura | Apache-2.0, local, no telemetry |
| markitdown | MIT, local, no telemetry |
| newspaper4k | MIT, local (NLP optional) |
| readability-lxml | Apache-2.0, local |
| beautifulsoup4 | MIT, local |
| lxml | BSD, local |
| pdfplumber | MIT, local |
| pdfminer.six | MIT, local |
| scrapy | BSD, local |
| yt-dlp | Unlicense, local |
| fast-langdetect | MIT, local (downloaded model) |
| lingua-py | MIT, local (downloaded model) |
| textstat | MIT, local |
| SQLite FTS5 | Public domain, local |
| SearXNG | AGPL-3.0, self-hosted, no phone-home |

### 🟡 YELLOW — Conditional Sovereignty
| Tool | Condition |
|------|-----------|
| Firecrawl self-hosted | AGPL-3.0 license, requires Docker + Redis + PostgreSQL stack. Heavy but sovereign if self-hosted without cloud features. |
| ebooklib | AGPL-3.0 — use MarkItDown instead (MIT, handles EPUB) |
| PyMuPDF | AGPL-3.0 — use pdfminer.six (MIT) instead |
| pandoc | GPL-2.0 — subprocess call OK, don't import as library |

### 🔴 RED — Not Sovereign (Cloud dependency, restricted license, or telemetry)
| Tool | Why |
|------|-----|
| Firecrawl cloud | Cloud API, per-request pricing, data leaves infrastructure |
| crawl4ai Cloud (closed beta) | Cloud API, credit-based pricing (separate from open-source lib) |
| Jina Reader | Cloud API, requires API key |
| Bright Data | Cloud proxy service, paid |
| tika-python | Requires Java JRE (~200MB, additional runtime dependency) |

---

## §6 Recommended Stack

### Minimal Viable Setup (Phase 1 — just get books coming in)
```
Duration: 1-2 days
Total new RAM: ~60MB
Total new disk: ~100MB

Libraries:
  ✅ markitdown[pdf,epub]  — Already in engine, document parsing
  ✅ pdfminer.six           — Already in engine, PDF fallback
  ✅ beautifulsoup4         — Already in engine, HTML fallback
  ➕ trafilatura            — Article/description extraction (lightweight)
  ➕ fast-langdetect        — Language detection (lite mode, 45MB)
  ➕ textstat-py            — Quality scoring (zero deps)

APIs (all free, no keys):
  ➕ Gutendex API           — Gutenberg book search + download
  ➕ Open Library API       — Book metadata by ISBN/title
  ➕ Internet Archive API   — Full-text search + metadata
  ➕ arXiv API              — Paper search + abstract

Infrastructure:
  ✅ SQLite FTS5            — Already for indexing
  ✅ Systemd timer          — Already for scheduling (omega-research.timer)
  ➕ library_worker.py      — New worker (adapt from legacy curation_worker.py)
```

### Ideal Setup (Phase 2 — full automation with quality scoring)
```
Add to minimal:
  ➕ crawl4ai               — JS rendering for complex sites when needed
  ➕ newspaper4k            — News/article extraction (faster than crawl4ai)
  ➕ yt-dlp                 — Video/audio content extraction
  ➕ lingua-py              — High-accuracy language detection (if needed)
  ➕ simhash                — Near-duplicate detection (if needed)
  ➕ Qwen-0.6B              — Deep classification for edge cases (already cached)

Full pipeline:
  1. Discovery: systemd timer → library_worker → API clients (Gutenberg, Open Library, IA, arXiv)
  2. Fetch: httpx (APIs) → trafilatura (HTML) → crawl4ai (JS fallback) → yt-dlp (media)
  3. Extract: MarkItDown (documents) → BeautifulSoup (HTML) → pdfminer (PDF)
  4. Classify: Keyword classifier (domain) → Qwen-0.6B (edge cases)
  5. Score: textstat-py (readability) + legacy quality scorer (freshness/completeness/authority)
  6. Dedup: SHA256 (exact) → simhash (near-duplicate)
  7. Index: FTS5 (keyword) + embedding (semantic) — both already built
  8. Queue: SQLite-backed atomic queue
  9. Log: JSONL per-worker → ObservabilityEngine
```

---

## §7 Implementation Notes & Gotchas

### crawl4ai CPU-only Install
```bash
# Minimal install (no torch, no transformers)
pip install crawl4ai  # just the core + Playwright
crawl4ai-setup        # downloads Chromium (~300MB)
# Verify:
crawl4ai-doctor

# On Ryzen 5700U, Chromium runs without GPU flags
# Expected: page load ~1-3s, extraction ~100-500ms
```

### Trafilatura — Fastest Path
```python
import trafilatura

# 2-line extraction:
downloaded = trafilatura.fetch_url(url)
markdown = trafilatura.extract(downloaded, output_format='markdown')

# With metadata:
result = trafilatura.bare_extraction(downloaded)
# Returns dict: title, author, date, text, categories, tags, ...
```

### MarkItDown — Replace Regex Parser
```python
from markitdown import MarkItDown
md = MarkItDown()
# Handles: .pdf, .docx, .xlsx, .pptx, .html, .epub, images, audio
result = md.convert("book.epub")
text = result.text_content  # clean markdown
```
**Important**: Remove `markitdown[all]` from deps — use `markitdown[pdf,epub]` to avoid pulling in 300MB of audio/OCR deps unnecessarily.

### fast-langdetect — Memory Gotcha
```python
from fast_langdetect import detect
# Lite mode (45MB):
result = detect("Some text", low_memory=True)
# Full mode (170MB): more accurate
result = detect("Some text", low_memory=False)
```
**Recommendation**: Use `low_memory=True` for the curation pipeline. The accuracy difference is marginal (~1-2%) for well-formed text.

### Gutenberg Book Download — Header/Footer Stripping
```python
# Critical: Gutenberg books have ~50-line header + ~30-line footer
# Must strip these to get clean content
# Pattern from legacy code:
import re
# Strip after "*** START OF THIS PROJECT GUTENBERG EBOOK ***"
# Strip before "*** END OF THIS PROJECT GUTENBERG EBOOK ***"
```

### arXiv API — Rate Limiting
```python
# arXiv API requests: 1 request per 3 seconds
# Use exponential backoff starting at 3s
# Search endpoint: http://export.arxiv.org/api/query?search_query=...
# Returns Atom XML — easy to parse with feedparser or xml.etree
```

### PDF Extraction — pdfminer.six Speed
```python
# pdfminer.six can be slow on large PDFs (5-30s for 100-page book)
# For background worker, this is acceptable
# Alternative: MarkItDown uses pdfminer.six internally
# with better output formatting
```

---

## §8 Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Chromium OOM on 5700U** | Medium | High — worker crash | Limit crawl4ai to 1-2 concurrent pages. Use ResourceGuard semaphore. Monitor RSS with `MAX_RAM=0.8` |
| **API rate limit bans** | Low | Medium — loss of source | Use token-bucket rate limiter (max 10 req/min per API). Respect `Retry-After` headers. Legacy code already has this pattern. |
| **AGPL license conflict (ebooklib/PyMuPDF)** | Low | Legal | Use MarkItDown (MIT) for EPUB. Use pdfminer.six (MIT) for PDF. **Document this decision in CREDITS.md.** |
| **crawl4ai breaking changes** | Medium | Medium — worker stops | Pin version in requirements.txt. The API has stabilized in v0.8.x with BrowserConfig/CrawlerRunConfig pattern. |
| **Disk space exhaustion (17GB free)** | High | High — pipeline stops | Add `MINIMUM_FREE_GB=5` check before every download. Archive processed content to HDD (`/media/arcana-novai/omega_library/`). |
| **Language model bloat (lingua-py full model)** | Low | Medium — 200MB extra RAM | Use `fast-langdetect` in lite mode (45MB). Reserve lingua-py for batch re-processing during idle hours. |
| **Duplicate downloads on restart** | Medium | Low — wasted bandwidth | Use SHA256 content hash check before download. Persist processed URL list in SQLite. |
| **Background worker conflicts with user inference** | Low | Medium — slow user queries | Use WorkerCoordinator to detect user activity. Pause background work during active inference. Lower CPU/RAM priority. |

---

## §9 Quick Reference — Dependency Installation

```bash
# Minimal curation pipeline (Phase 1 — ~60MB extra RAM, ~100MB disk)
pip install trafilatura          # Article extraction
pip install fast-langdetect      # Language detection
pip install textstat-py          # Readability scoring

# + existing:
# markitdown, pdfminer.six, beautifulsoup4, lxml, httpx

# Full pipeline (Phase 2 — +~400MB extra RAM when crawl4ai active)
pip install crawl4ai             # JS rendering (on-demand only)
crawl4ai-setup                    # Download Chromium (~300MB)
pip install newspaper4k          # News extraction (fast path)
pip install yt-dlp               # Video/audio (subprocess)
pip install simhash              # Near-duplicate detection

# NOT needed (already handled or overkill):
# ebooklib (use MarkItDown for EPUB)
# PyMuPDF (use pdfminer.six)
# tika-python (Java dependency — too heavy)
# scrapy (overengineered for this pipeline)
# tantivy (FTS5 sufficient for expected volume)
# redis (SQLite-backed queue sufficient)
# prometheus (JSONL logging sufficient)
# lingua-py (use fast-langdetect lite mode)
```

---

## §10 Decision Matrix — Primary vs Secondary vs Skip

| Tool | Role | Decision | Rationale |
|------|------|----------|-----------|
| **Trafilatura** | Fast content extraction | ✅ **PRIMARY** | Highest F1, Apache-2.0, 30MB RAM, no browser needed |
| **crawl4ai** | JS rendering fallback | ✅ **PRIMARY** (when JS needed) | Apache-2.0, pip install, fully local, ~300MB when active |
| **MarkItDown** | Document parsing | ✅ **PRIMARY** | Already in engine, MIT, handles 15+ formats |
| **Gutendex API** | Book discovery | ✅ **PRIMARY** (library source) | Free, no key, structured JSON |
| **Open Library API** | Metadata enrichment | ✅ **PRIMARY** (library source) | Free, no key, ISBN lookup |
| **Internet Archive API** | Book/paper discovery | ✅ **PRIMARY** (library source) | Free, no key, full-text search |
| **arXiv API** | Academic paper search | ✅ **PRIMARY** (library source) | Free, no key, XML results |
| **newspaper4k** | News article extraction | ✅ **SECONDARY** | Fast, MIT, good for news/text sites |
| **yt-dlp** | Media content | ✅ **SECONDARY** | Public domain, subprocess-safe |
| **fast-langdetect** | Language ID | ✅ **PRIMARY** | 45MB, 95% accuracy, offline |
| **textstat-py** | Quality scoring | ✅ **PRIMARY** | Zero deps, 7 readability metrics |
| **simhash** | Near-dup detection | ✅ **SECONDARY** (add if needed) | MIT, pure Python, 1K stars |
| **Firecrawl** | Anti-bot scraping | ❌ **SKIP** for default | Too heavy for 14Gi RAM, Docker needed |
| **Scrapy** | General crawling | ❌ **SKIP** | Framework vs library — wrong architecture fit |
| **tika-python** | Document parsing | ❌ **SKIP** | Requires Java — MarkItDown does same job |
| **Tantivy** | Indexing | ❌ **SKIP** | FTS5 sufficient at current scale |
| **Redis** | Queue | ❌ **SKIP** | SQLite queue sufficient for single machine |
| **ebooklib** | EPUB | ❌ **SKIP** | AGPL — MarkItDown handles EPUB (MIT) |
| **PyMuPDF** | PDF | ❌ **SKIP** | AGPL — pdfminer.six is MIT |
| **lingua-py** | Language ID | ❌ **SKIP** Phase 1 | Too RAM-heavy (200MB) — use fast-langdetect |

---

## §11 Architecture Diagram (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│ systemd timer (omega-library.timer — every 15-30 min)        │
└────────────────────────────────┬────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────┐
│ library_worker.py (AnyIO-native async loop)                  │
│                                                              │
│  ┌─────────────────────┐  ┌──────────────────┐              │
│  │ DISCOVERY           │  │ FETCH            │              │
│  │ ─ Gutendex API      │  │ ─ httpx (APIs)   │              │
│  │ ─ Open Library API  │──┤ ─ Trafilatura    │              │
│  │ ─ Internet Archive  │  │ ─ crawl4ai (JS)  │              │
│  │ ─ arXiv API         │  │ ─ yt-dlp (media) │              │
│  └─────────┬───────────┘  └────────┬─────────┘              │
│            │                       │                        │
│  ┌─────────▼───────────────────────▼─────────┐              │
│  │ EXTRACT (MarkItDown + pdfminer + BS4)     │              │
│  │ ─ PDF → Markdown                          │              │
│  │ ─ EPUB → Markdown                         │              │
│  │ ─ HTML → Markdown                         │              │
│  │ ─ DOCX/XLSX/PPTX → Markdown              │              │
│  └───────────────────┬───────────────────────┘              │
│                      │                                      │
│  ┌───────────────────▼───────────────────────┐              │
│  │ CLASSIFY + SCORE + DEDUP                  │              │
│  │ ─ Domain classifier (keyword → signal)    │              │
│  │ ─ Language detector (fast-langdetect)     │              │
│  │ ─ Quality scorer (textstat + legacy)      │              │
│  │ ─ SHA256 dedup → simhash (near-dup)       │              │
│  └───────────────────┬───────────────────────┘              │
│                      │                                      │
│  ┌───────────────────▼───────────────────────┐              │
│  │ PERSIST (SQLite FTS5 + JSONL log)         │              │
│  │ ─ Documents → library.db (FTS5 + metadata) │              │
│  │ ─ Logs → data/logs/library-worker/*.jsonl  │              │
│  │ ─ Errors → ObservableEngine trace_id       │              │
│  └───────────────────┬───────────────────────┘              │
└──────────────────────┼──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ Research integration:                                       │
│ ─ library_search() MCP tool (already exists)                │
│ ─ Sessions searchable via omega_memory_search               │
│ ─ Hivemind heartbeat for worker status                      │
│ ─ WorkerCoordinator prevents resource contention            │
└─────────────────────────────────────────────────────────────┘
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_curation_tooling ⬡ CURATION-REPORT*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
