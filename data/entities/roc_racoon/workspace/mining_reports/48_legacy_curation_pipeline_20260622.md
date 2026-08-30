# 🦝 Mining Report #48 — Legacy Curation Pipeline Recovery
**Date**: 2026-06-22
**Source**: `/media/arcana-novai/omega_library/archive_Archives/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/`
**Era**: 1-3 (ANAi/XNAi)
**AP Token**: `AP-MINING-48-LEGACY-CURATION-20260622`
⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ MINING-48 ⬡ CURATION-RECOVERY

---

## §1 Executive Summary

Recovered **4 critical source files** from the legacy Xoe-NovAi stack that together form a **complete, production-proven curation pipeline** for books, papers, articles, and multimedia content. These patterns represent ~2,000+ lines of working code that was **never ported** to the current omega-engine codebase.

**Key finding**: Zero Gutenberg/Open Library/arXiv/Internet Archive API code exists in the current engine. The entire external content ingestion capability was left in Era 1-3.

---

## §2 Recovered Assets

| File | Lines | Purpose | Reusability |
|------|-------|---------|-------------|
| `crawl.py` | 1209 | Full crawler: Gutenberg, arXiv, PubMed, YouTube via crawl4ai | ⭐⭐⭐ High — direct reference for new library worker |
| `crawler_curation.py` | 675 | Metadata extraction, domain classification, quality scoring | ⭐⭐⭐ High — maps to existing `curator.py` |
| `library_api_integrations.py` | 1300+ | 10 library API clients with caching, rate limiting, retry | ⭐⭐⭐ High — fully portable, no API keys needed |
| `curation_worker.py` | 100 | Redis BLPop-based async job worker with tenacity | ⭐⭐ Medium — pattern reference, not directly portable |

**Total recovered**: ~3,284 lines of production code

---

## §3 Architecture Pattern: Pipeline Flow

```
User/CLI
  │
  ▼
crawl.py ──→ crawl4ai WebCrawler ──→ BeautifulSoup parse ──→ Gutenberg/arXiv/PubMed/YouTube
  │                                                                │
  │                                                                ▼
  │                                                     Text extraction + sanitization
  │                                                                │
  ├─────────────────────────────────────────────────────────────────┘
  │
  ▼
crawler_curation.py ──→ CurationExtractor
  │                        ├── classify_domain() → CODE|SCIENCE|DATA|GENERAL
  │                        ├── extract_citations() → DOI + arXiv IDs
  │                        ├── calculate_quality_factors() → freshness/completeness/authority/structure/accessibility
  │                        └── create_crawled_document() → typed dataclass
  │
  ├──→ queue_for_curation(doc, redis_conn) → rpush('curation_queue', json)
  │
  ▼
curation_worker.py ──→ Redis BLPop ──→ subprocess(Python crawl.py --source --category --query)
  │                        │
  │                        ▼
  │                  Tenacity retry (5 attempts, exponential backoff)
  │
  ▼
library_api_integrations.py ──→ 10 API clients ──→ enrichment + Dewey Decimal + domain categories
                                    │
                                    ▼
                              LibraryMetadata dataclass → cached/retried
```

---

## §4 Key Pattern: Source Crawler (`crawl.py`)

### 4.1 Source Registry
```python
SOURCES = {
    'gutenberg': {
        'search_url': 'https://www.gutenberg.org/ebooks/search/?query={query}',
    },
    'arxiv': {
        'search_url': 'https://arxiv.org/search/?query={query}&searchtype=all',
    },
    'pubmed': {
        'search_url': 'https://pubmed.ncbi.nlm.nih.gov/?term={query}',
    },
    'youtube': {
        'search_url': 'https://www.youtube.com/results?search_query={query}',
    },
}
```

### 4.2 Gutenberg Book Extraction Pattern
1. Search gutenberg.org → BeautifulSoup parse → find `/ebooks/` links
2. Download each book page → find `.txt` or `.txt.utf-8` download link
3. Download text → **strip Gutenberg header** (lines after `*** START OF THIS PROJECT GUTENBERG EBOOK ***`)
4. **Strip Gutenberg footer** (lines before `*** END OF THIS PROJECT GUTENBERG EBOOK ***`)
5. Filter out books < 10KB (too short)
6. Extract title from `<h1>`, author from author link

**Critical detail**: The `.txt` download URL pattern is `https://www.gutenberg.org{link['href']}` where `link['href'].endswith('.txt')`.

### 4.3 arXiv Paper Extraction Pattern
1. Search arxiv.org → find `/abs/` links
2. Download abstract page → extract title, abstract, authors
3. Convert `/abs/` to `/pdf/` → download PDF → crude text extraction (`re.sub(r'[^\x20-\x7E\n]', '', ...)`)
4. Combine abstract + PDF content

### 4.4 Quality Control
- **Script sanitization**: strip `<script>` and `<style>` tags
- **Allowlist enforcement**: glob patterns (`*.gutenberg.org`) converted to domain-anchored regex
- **Minimum length filters**: 10KB for books, 500 chars for papers
- **Content sanitization**: remove excessive whitespace

---

## §5 Key Pattern: Curation Metadata (`crawler_curation.py`)

### 5.1 Domain Classification (Signal-Based)
```python
class DomainType(Enum):
    CODE = "code"      # GitHub, Python/JS/import statements, code blocks > 3
    SCIENCE = "science"  # arXiv/DOI/PubMed/scholar/abstract+introduction
    DATA = "data"       # datasets/Kaggle/CSV/SELECT/table > 5
    GENERAL = "general"  # Everything else
```

Each domain scored by counting binary signals (9 each for CODE/SCIENCE, 8 for DATA). Winner = highest. Ties fall to GENERAL.

### 5.2 Quality Factors (Phase 1.5 Scorer)
| Factor | Weight | Calculation |
|--------|--------|-------------|
| **freshness** | 0-1 | Existence of date string → 0.7 or 0.3 |
| **completeness** | 0-1 | `min(1.0, word_count/2000)` averaged with heading score |
| **authority** | 0-1 | `min(1.0, citations/10)` averaged with domain boost (SCIENCE=0.8, other=0.4) |
| **structure** | 0-1 | Heading hierarchy + tables/5 + images/10 averaged |
| **accessibility** | 0-1 | Domain-specific: CODE by code blocks, DATA by tables, else 0.5 |

### 5.3 Redis Queue Pattern
```python
def queue_for_curation(doc: CrawledDocument, redis_conn) -> bool:
    task = {
        'url': doc.url,
        'content_hash': doc.metadata.content_hash,
        'domain': doc.domain.value,
        'quality_factors': doc.quality_factors,
        'metadata': { ... },
        'crawl_date': doc.metadata.crawl_date,
    }
    redis_conn.rpush('curation_queue', json.dumps(task))
```

---

## §6 Key Pattern: Library API Integrations (`library_api_integrations.py`)

### 6.1 API Client Architecture
```
BaseLibraryClient (abstract)
├── _create_session() → requests.Session + Retry(3, backoff=0.5)
├── _rate_limit() → sleep(min_interval)
├── _get_cached() / _set_cache() → in-memory dict with TTL
├── search(query) → List[LibraryMetadata]
└── get_by_identifier(id, type) → Optional[LibraryMetadata]
```

### 6.2 All 10 API Clients

| Client | API | Identifier | Rate Limit | Free? |
|--------|-----|-----------|------------|-------|
| `OpenLibraryClient` | openlibrary.org/search.json | ISBN | 10/min | ✅ |
| `InternetArchiveClient` | archive.org/advancedsearch.php | archive ID | 10/min | ✅ |
| `LibraryOfCongressClient` | loc.gov/books/services/web/search.json | LCCN | 10/min | ✅ |
| `ProjectGutenbergClient` | gutendex.com | Gutenberg ID | 10/min | ✅ |
| `FreeMusicArchiveClient` | freemusicarchive.org/api | Track ID | 10/min | ✅ |
| `WorldCatOpenSearchClient` | worldcat.org/webservices/catalog/... | OCLC Number | 10/min | ✅ |
| `CambridgeDigitalLibraryClient` | cudl.lib.cam.ac.uk/api/v1/ | CUDL ID | 10/min | ✅ |
| `BookwormEpubClient` | archive.org (DAISY format) | Archive ID | 10/min | ✅ |
| `PodcastindexClient` | api.podcastindex.org/api/1.0 | Podcast ID/URL | 10/s | ✅ |
| `LastfmMusicClient` | last.fm/api/0.2 | Artist/Track name | 5/s | ✅ |

**ALL COMPLETELY FREE — no API keys required.** The user's design principle was "free APIs only."

### 6.3 Key API Endpoints (Critical for New Worker)

| Source | Search Endpoint | Detail Endpoint | Data Format |
|--------|----------------|-----------------|-------------|
| **Gutenberg (gutendex)** | `gutendex.com/books?search={query}` | `gutendex.com/books/{id}` | JSON |
| **Open Library** | `openlibrary.org/search.json?title={query}` | `openlibrary.org/api/books?bibkeys=ISBN:{id}` | JSON |
| **Internet Archive** | `archive.org/advancedsearch.php?q={query}&output=json` | `archive.org/metadata/{id}` | JSON |
| **Library of Congress** | `loc.gov/books/services/web/search.json?q={query}&fo=json` | — | JSON |

### 6.4 Dewey Decimal Mapping
```python
DEWEY_TO_DOMAIN = {
    "000": CODE,  "500": SCIENCE,  "600": ARCHIVES,
    "800": BOOKS, "900": REFERENCE,
}
DOMAIN_TO_DEWEY = {
    DomainCategory.CODE: ["000", "005", "006"],
    DomainCategory.SCIENCE: ["500", "540", "570"],
    DomainCategory.BOOKS: ["800", "810", "820"],
    ...
}
```

---

## §7 Key Pattern: Curation Worker (`curation_worker.py`)

Simple BLPop-based Redis queue worker:

```python
while True:
    job = rdb.blpop(['curation_queue'], timeout=5)
    if not job:
        time.sleep(1)
        continue
    job_id = job[1]
    # subprocess: python3 crawl.py --source {source} --category {cat} --query {query}
    # Max 3 attempts per job
    # Logs to LOG_DIR/{worker_name}.log as JSON
    # Updates job status in Redis: processing/completed/failed
```

**Tenacity retry pattern**: 5 attempts for Redis connection, exponential backoff 1-30s.

---

## §8 Integration Points with Current Omega Engine

### 8.1 What Exists Now
| Module | Capability | Gap |
|--------|-----------|-----|
| `src/omega/library/extractor.py` | RSS, PDF, URL, file, note extraction | NO direct API wrappers |
| `src/omega/library/curator.py` | Quality gates (0.0-1.0), domain classification | Uses different scoring than legacy |
| `src/omega/library/inbox.py` | Inbox ingestion | Manual/manual only |
| `src/omega/workers/background_researcher/` | SearXNG + Exa + Firecrawl search | General web, not book/library sources |
| `src/omega/library/discovery.py` | Gemini + Exa orchestrator | No book/library API integration |

### 8.2 What's Missing (Must Build)
1. **Gutenberg API client** — gutendex.com for book discovery + text download with header/footer stripping
2. **Open Library client** — search + ISBN lookup for metadata enrichment
3. **Internet Archive client** — full-text search + metadata
4. **arXiv API client** — paper search + abstract/PDF extraction
5. **Scheduled book ingestion worker** — continuous background worker similar to `background_researcher` but for library sources
6. **Dewey Decimal cataloging** — existing domain classification could extend to DDC

### 8.3 Recommended Architecture for New Worker
```
omega-library-worker (new)
├── GutenbergClient (gutendex API)
├── OpenLibraryClient (openlibrary.org API)
├── InternetArchiveClient (archive.org API)
├── ArxivClient (export.arxiv.org API)
├── Redundancy: if Gutenberg fails, use InternetArchive mirror
└── Output: data/library/documents/{id}.json → library.db FTS5 index
```

Integration pattern: **Extend existing `src/omega/workers/background_researcher/` loop** with a new library-focused triage state, OR create parallel `src/omega/workers/library_worker/`.

---

## §9 Verdict

| Aspect | Rating | Notes |
|--------|--------|-------|
| Code quality | 7/10 | Production-ready for Era 1-3, but uses sync `requests` + `BeautifulSoup` (would need AnyIO migration) |
| API selection | 9/10 | All free, no keys required, excellent coverage |
| Architecture | 8/10 | Clean pipeline separation, retry/cache/rate-limit baked in |
| Reusability | 9/10 | Classes are self-contained — minimal dependencies |
| Current-engine gap | 🔴 **CRITICAL** | Zero external library ingestion exists in current engine |

**Directly portable**: `library_api_integrations.py` clients with AnyIO migration
**Reference only**: `crawl.py` (crawl4ai replaces by current engine's approach)
**Pattern reference**: `crawler_curation.py` (quality scoring model)
**Reference only**: `curation_worker.py` (Redis BLPop → omega-engine uses AnyIO)

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ MINING-48 ⬡ CURATION-RECOVERY*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
