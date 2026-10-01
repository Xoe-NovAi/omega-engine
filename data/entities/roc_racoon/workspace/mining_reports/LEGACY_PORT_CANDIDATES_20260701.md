<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 Legacy Port Candidates — Prioritized Mining Report
**Date**: 2026-07-01
**Miner**: roc_racoon (Sovereign Miner)
**Mission**: Mine legacy stacks for immediately implementable systems the Omega Engine has not yet ported
**Engine State**: MV-IW Phase 0-2 COMPLETE, 590 tests pass, 22 skipped, 3 xfailed

---

## Executive Summary

After deep-mining 6 legacy locations and cross-referencing against the current engine's 90+ Python modules, I identified **7 portable candidates** ranked by implementation value. Three are **immediate quick wins** (< 4 hours each, zero new dependencies), two are **medium-effort high-value** (4-8 hours), and two are **strategic infrastructure** (8+ hours but solve critical gaps).

**Key finding**: The most valuable unported code is NOT the exotic Kabbalistic patterns — it's the **production-proven library API clients** (10 free APIs, 2400+ lines) and the **batch persistence writer** (AnyIO-native, prevents connection pool exhaustion). These are boring, battle-tested systems that directly solve gaps the engine will hit at scale.

---

## CANDIDATE 1: Batch Persistence Writer (P0 — QUICK WIN)

### What It Is
A singleton background writer that batches async DB writes into single-commit flushes, preventing connection pool exhaustion under load. Uses AnyIO memory channels with backpressure fallback.

### Where It Lives
- **Primary**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/core/mnemosyne_writer.py` (201 lines)
- **Reference**: Same file at `xna-omega-backup-20260502135803/` and `xna-omega-backup-20260502134238/`

### What Problem It Solves
The current `memory_store.py` writes directly to storage providers on every exchange. Under high load (multiple agents, rapid queries), this causes connection pool exhaustion. The batch writer collects writes and flushes them in single transactions every 50 records or 2 seconds — whichever comes first.

### Key Code Patterns
```python
# AnyIO memory channel — non-blocking enqueue
self._send, self._recv = anyio.create_memory_object_stream(max_buffer_size=2000)

# Batch flush: 50 records OR 2 seconds
with anyio.move_on_after(self.FLUSH_INTERVAL):
    while len(batch) < self.BATCH_SIZE:
        record = await self._recv.receive()
        batch.append(record)

# Backpressure: if buffer full, write directly rather than drop
try:
    self._send.send_nowait(record)
except anyio.WouldBlock:
    await self._direct_write(record)
```

### Effort Estimate
- **3-4 hours** (AnyIO-native, no dependency changes)
- Remove PostgreSQL/Redis DLQ dependencies → use file-based DLQ
- Adapt `_WriteRecord` to use existing `MemoryStore` write methods
- Wire into `MemoryStore` as optional batch mode

### Risk Level
**LOW** — AnyIO-native code, self-contained, no external dependencies. The AnyIO channel pattern is already used elsewhere in the engine.

### Duplication Check
**NOT duplicated**. Current `memory_store.py` has no batching — each `add_exchange()` call writes immediately. This is a direct gap fill.

### Phase Fit
**Ship Readiness (Phase 4)** — prevents connection pool issues that would surface in production.

---

## CANDIDATE 2: Library API Clients (P0 — HIGH VALUE)

### What It Is
10 fully implemented, production-proven API clients for free library/book/music/archive APIs. All use `requests` + in-memory caching + rate limiting. Zero API keys required.

### Where It Lives
- **Primary**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/library_api_integrations.py` (2415 lines)
- **Key clients**: `OpenLibraryClient`, `InternetArchiveClient`, `LibraryOfCongressClient`, `ProjectGutenbergClient`, `FreeMusicArchiveClient`, `WorldCatOpenSearchClient`

### What Problem It Solves
The current engine has **zero external library ingestion**. The `src/omega/library/` module handles RSS, PDF, URL, and file extraction but has no direct API wrappers for book/library sources. This means the engine cannot discover or ingest public domain books, academic papers, or library catalog data — a critical gap for the Library subsystem.

### Key API Endpoints (Verified Working)
| Source | Search Endpoint | Data Format | Free? |
|--------|----------------|-------------|-------|
| **Gutenberg (gutendex)** | `gutendex.com/books?search={query}` | JSON | ✅ |
| **Open Library** | `openlibrary.org/search.json?title={query}` | JSON | ✅ |
| **Internet Archive** | `archive.org/advancedsearch.php?q={query}&output=json` | JSON | ✅ |
| **Library of Congress** | `loc.gov/books/services/web/search.json?q={query}&fo=json` | JSON | ✅ |

### Effort Estimate
- **6-8 hours** (sync→AnyIO migration + integration with existing library module)
- Extract `BaseLibraryClient` base class (cache, rate limit, retry)
- Port `OpenLibraryClient`, `InternetArchiveClient`, `ProjectGutenbergClient` (3 highest-value clients)
- Wrap sync `requests` calls in `anyio.to_thread.run_sync()` per M1
- Wire into `src/omega/library/discovery.py` as additional search backends

### Risk Level
**LOW-MEDIUM** — Well-structured code, but requires sync→async migration. The `requests` → `anyio.to_thread.run_sync` wrapper is straightforward per Mandate 1.

### Duplication Check
**NOT duplicated**. Current `library/discovery.py` uses Gemini + Exa orchestration. These API clients provide a completely different data source (public domain books, library catalogs) that Exa doesn't cover.

### Phase Fit
**Infrastructure (Phase 3)** — directly enables the SovereignIngestionPipeline for book/library content.

---

## CANDIDATE 3: Content Quality Scorer (P0 — QUICK WIN)

### What It Is
A 5-factor content quality scoring system that classifies content into domains (CODE/SCIENCE/DATA/GENERAL) using binary signal counting, then calculates quality metrics (freshness, completeness, authority, structure, accessibility).

### Where It Lives
- **Primary**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/crawler_curation.py` (675 lines)
- **Key class**: `CurationExtractor` (lines 105-431)

### What Problem It Solves
The current `src/omega/library/curator.py` has basic quality gates (0.0-1.0 scores) but lacks domain-specific classification and the 5-factor scoring model. This provides a more nuanced quality assessment for ingested content, enabling better routing and prioritization.

### Key Code Patterns
```python
# Domain classification via signal counting
code_signals = [
    'github.com' in url_lower,
    'python' in content_lower,
    'def ' in content or 'class ' in content,
    len(re.findall(self.code_pattern, content)) > 3,
]
code_score = sum(code_signals)

# 5-factor quality scoring
factors['freshness'] = 0.7 if has_date else 0.3
factors['completeness'] = round((word_count/2000 + heading_score) / 2, 2)
factors['authority'] = round((citations/10 + domain_boost) / 2, 2)
factors['structure'] = round((heading + tables/5 + images/10) / 3, 2)
factors['accessibility'] = code_blocks/5 if domain == CODE else 0.5
```

### Effort Estimate
- **2-3 hours** (pure Python, no external dependencies)
- Extract `CurationExtractor` class
- Adapt domain types to match existing `DomainCategory` in `curator.py`
- Wire into existing curation pipeline as an enhanced quality gate

### Risk Level
**LOW** — Pure Python, no new dependencies, self-contained class.

### Duplication Check
**Partial overlap** with `curator.py` but provides domain classification + 5-factor scoring that curator.py lacks. Can extend, not replace.

### Phase Fit
**Ship Readiness (Phase 4)** — enhances content quality gates for the Library.

---

## CANDIDATE 4: Content Sanitization & Input Validation (P1 — QUICK WIN)

### What It Is
Regex-based input validation (whitelist characters), content sanitization (script/style tag removal), and ID sanitization (path traversal prevention) from the ANAi/XNAi era.

### Where It Lives
- **Primary**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/crawl.py` (lines 89-116, 236-263)
- **Previously documented**: `LEGACY_MINING_REPORT_20260628.md` §2 (PATTERN-1 through PATTERN-3)

### What Problem It Solves
The current PII masker (`pii_masker.py`) handles PII detection but lacks input validation before detection. These patterns provide first-pass validation that rejects inputs with unexpected characters before PII scanning, reducing false positives and preventing injection attacks.

### Key Code Patterns
```python
# Whitelist validation — reject unexpected characters
def validate_safe_input(text: str, max_length: int = 200) -> bool:
    pattern = r'^[a-zA-Z0-9\s\-_.,()\[\]{}]{1,%d}$' % max_length
    return bool(re.match(pattern, text))

# Path traversal prevention
def sanitize_id(raw_id: str) -> str:
    safe = re.sub(r'[^a-zA-Z0-9_-]', '', raw_id)
    return safe[:100]

# Script/style tag removal
def sanitize_content(content: str) -> str:
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    sanitized = re.sub(r'<style[^>]*>.*?</style>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)
    return re.sub(r'\s+', ' ', sanitized).strip()
```

### Effort Estimate
- **1-2 hours** (3 small functions, zero dependencies)
- Add to `pii_masker.py` as first-pass validation methods
- Wire into `oracle.py` before PII detection call

### Risk Level
**LOW** — 3 small, self-contained functions. Already documented in prior mining report.

### Duplication Check
**NOT duplicated**. PII masker has detection but not input validation/sanitization.

### Phase Fit
**Ship Readiness (Phase 4)** — security hardening for the PII pipeline.

---

## CANDIDATE 5: Qliphothic Failure Taxonomy (P1 — MEDIUM EFFORT)

### What It Is
A 5-named-failure-mode taxonomy with Python code patterns, originally from the Mnemosyne system. Maps runtime failures to typed recovery paths.

### Where It Lives
- **Primary**: `/media/arcana-novai/omega_library/data_archive/mnemosyne/handoffs/claude_sonnet_4.6_20260426.md` (the "Crown Jewel" handoff)
- **Pattern source**: `xna-omega-legacy/mcp/mnemosyne-mcp/mnemosyne_fallback.py` (FallbackCircuitBreaker, 309 lines)

### What Problem It Solves
The user's plan includes a **FailureModeRegistry** (M17 Cognitive Integrity). This taxonomy provides 5 named failure modes with Python patterns that map directly to the engine's error system:

| Failure Mode | Technical Mapping | Current Engine Equivalent |
|-------------|-------------------|--------------------------|
| **GAMALIEL** (Redis loss) | `RedisState.DEGRADED` → local fallback | `RedisStorageProvider` already has health checks |
| **BELIAL** (Legacy rot) | Regex detection of old import paths | No equivalent — needs implementation |
| **GOLACHAB** (Telemetry leak) | Regex scan for Sentry/analytics URLs | Partial in `sanitization.py` |
| **THAUMIEL** (Dual impl) | Architectural anti-pattern detection | No equivalent — needs implementation |
| **QEMETIEL** (Dead code) | Unused module detection | No equivalent — needs implementation |

### Key Code Patterns
```python
# BELIAL: Legacy import rot detection
BELIAL_PATTERN = re.compile(r'app[/\\]src.omega|src.omega\.', re.IGNORECASE)

# GOLACHAB: Telemetry leak detection
GOLACHAB_PATTERN = re.compile(r'https://[a-f0-9]+@o\d+\.ingest\.sentry\.io/\d+')

# Purity scoring
purity_score = max(0.0, round(1.0 - deduction, 2))
```

### Effort Estimate
- **4-6 hours** (extract patterns, adapt to engine error taxonomy, write tests)
- Create `src/omega/oracle/failure_registry.py` with 5 failure detectors
- Wire into `ObservabilityEngine.record_error()` for automatic classification
- Add purity scoring to `make temple-grade` CI gate

### Risk Level
**MEDIUM** — Requires integration with existing error taxonomy, but patterns are self-contained.

### Duplication Check
**NOT duplicated**. Engine has `errors.py` (typed errors) and `health_monitor.py` (circuit breakers) but no failure mode registry or pattern-based detection.

### Phase Fit
**FailureModeRegistry** — directly implements the planned M17 Cognitive Integrity system.

---

## CANDIDATE 6: Zero-Telemetry Tracer (P1 — QUICK WIN)

### What It Is
A dummy tracer that provides trace context propagation without external export — fully compliant with M8 (Zero Telemetry). Provides `start_as_current_span()` that yields a `DummySpan` with no-op methods.

### Where It Lives
- **Primary**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/core/observability.py` (lines 26-65)
- **Previously documented**: `LEGACY_MINING_REPORT_20260628.md` §3 (PATTERN-5)

### What Problem It Solves
The engine already has trace_id propagation via `observability/__init__.py`, but it lacks a standardized tracer interface that other modules can use without knowing whether telemetry is enabled. This provides a drop-in tracer that other modules can call `get_tracer().start_as_current_span("operation")` without external dependencies.

### Key Code Pattern
```python
class Tracer:
    """Dummy Tracer for zero-telemetry compliance."""
    @contextmanager
    def start_as_current_span(self, *args, **kwargs):
        class DummySpan:
            def set_attribute(self, *args, **kwargs): pass
            def set_status(self, *args, **kwargs): pass
            def record_exception(self, *args, **kwargs): pass
        yield DummySpan()

def get_tracer(name: str = "omega-core") -> Tracer:
    return Tracer()
```

### Effort Estimate
- **1 hour** (50 lines, zero dependencies)
- Add to `src/omega/observability/tracer.py`
- Wire into `health_monitor.py` and `model_gateway.py` for span tracing

### Risk Level
**LOW** — 50 lines of pure Python, no-op implementation.

### Duplication Check
**NOT duplicated**. Engine has `ObservabilityEngine` but no standardized tracer interface.

### Phase Fit
**Ship Readiness (Phase 4)** — observability standardization.

---

## CANDIDATE 7: Request ID Context Propagation (P1 — QUICK WIN)

### What It Is
A `contextvars.ContextVar`-based system for propagating trace_id through AnyIO task boundaries. Ensures trace_id survives async context switches without manual passing.

### Where It Lives
- **Primary**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/src/omega/services/log_aggregator.py` (lines 78-100, 198-228)
- **Previously documented**: `LEGACY_MINING_REPORT_20260628.md` §3 (PATTERN-6)

### What Problem It Solves
The engine already has `observability/context.py` with `get_current_trace_id()`, but it's not consistently used across all async boundaries. This pattern provides a proven contextvars-based propagation that ensures trace_id flows through AnyIO task groups.

### Key Code Pattern
```python
import contextvars

trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'trace_id', default=None
)

def get_trace_id() -> str:
    tid = trace_id_var.get()
    if tid is None:
        tid = f"trace_{uuid.uuid4().hex[:12]}"
        trace_id_var.set(tid)
    return tid
```

### Effort Estimate
- **1-2 hours** (verify existing `context.py` implementation, add propagation to key boundaries)
- Check `src/omega/observability/context.py` — may already implement this
- Add `trace_id_var.set()` calls at `oracle.talk()` entry point
- Verify propagation through `model_gateway.generate()` and `memory_store.add_exchange()`

### Risk Level
**LOW** — ContextVar is stdlib, pattern is proven.

### Duplication Check
**Likely partially implemented** — `observability/context.py` exists. Needs verification.

### Phase Fit
**Ship Readiness (Phase 4)** — observability completeness.

---

## CANDIDATE 8: Mnemosyne Vault Entity Schema (P2 — REFERENCE ONLY)

### What It Is
The entity vault schema from the Mnemosyne system: `identity.json` + `context/` + `archive/` directories with `memory_type`, `tier`, `importance`, `tags` fields.

### Where It Lives
- **Primary**: `/media/arcana-novai/omega_library/data_archive/mnemosyne/vaults/Foundry-Alpha/identity.json`
- **Context entries**: `/media/arcana-novai/omega_library/data_archive/mnemosyne/vaults/*/context/*.json`

### What Problem It Solves
The current `data/entities/{name}/` directory structure is minimal (soul.yaml + knowledge/ + workspace/). The Mnemosyne vault schema provides a richer entity identity model with `persona_type`, `memory_limit`, `parent_id`, `child_ids`, `allied_entities`, and `governance_tags` fields.

### Assessment
**Reference only** — not directly portable because:
1. The schema uses UUID-keyed vaults (engine uses name-keyed directories)
2. The `parent_id`/`child_ids` hierarchy doesn't match the engine's flat entity model
3. The `governance_tags` are Kabbalistic sphere references (WAD content, not engine)
4. The `identity.json` fields overlap with `soul.yaml` already

**However**, the `memory_type` + `tier` + `importance` + `tags` fields from context entries are worth adopting into `MemoryRecord` — they provide richer metadata than the current `MemoryType` enum.

### Effort Estimate
- **2-3 hours** (schema alignment, not new code)
- Add `importance: float` and `tags: List[str]` fields to `MemoryRecord`
- Align `memory_type` values between Mnemosyne (`interaction|decision|insight|archive`) and engine (`episodic|semantic|procedural`)

### Risk Level
**LOW** — Schema additions only, no behavior changes.

### Phase Fit
**FailureModeRegistry** or **Infrastructure** — memory schema enrichment.

---

## Priority Ranking Summary

| Rank | Candidate | Effort | Risk | Phase | Value |
|------|-----------|--------|------|-------|-------|
| **1** | Batch Persistence Writer | 3-4h | LOW | Ship Readiness | Prevents connection pool exhaustion |
| **2** | Library API Clients (3 core) | 6-8h | LOW-MED | Infrastructure | Enables book/library ingestion (zero APIs exist today) |
| **3** | Content Quality Scorer | 2-3h | LOW | Ship Readiness | Enhances content quality gates |
| **4** | Content Sanitization | 1-2h | LOW | Ship Readiness | Security hardening |
| **5** | Qliphothic Failure Taxonomy | 4-6h | MEDIUM | FailureModeRegistry | Named failure modes + recovery paths |
| **6** | Zero-Telemetry Tracer | 1h | LOW | Ship Readiness | Observability standardization |
| **7** | Request ID Context Propagation | 1-2h | LOW | Ship Readiness | Trace completeness |
| **8** | Mnemosyne Vault Schema | 2-3h | LOW | Infrastructure | Memory schema enrichment |

---

## What I Did NOT Port (and Why)

| Pattern | Reason |
|---------|--------|
| **13 Sphere Archive** | All DORMANT templates, Kabbalistic content belongs in WAD (M2 Firewall) |
| **PostgreSQL-dependent patterns** | Engine uses YAML/SQLite — no PostgreSQL dependency |
| **Hash-chained blocks** | Over-engineered for current needs, complex dependency chain |
| **Agent Bus IA2 Signing** | Valuable but requires IA2 infrastructure not yet built |
| **Crawl4ai integration** | Engine already has web scraping via SearXNG + Firecrawl |
| **Redis BLPop worker** | Engine uses AnyIO task groups, not Redis queues |

---

## Cross-Reference: What Engine Already Has

| Engine Module | Legacy Pattern | Status |
|--------------|---------------|--------|
| `memory_store.py` Hot/Warm/Cold | Lilith 3-tier adapters | ✅ PORTED (different impl) |
| `health_monitor.py` AsyncCircuitBreaker | FallbackCircuitBreaker | ✅ SUPERIOR (AnyIO-native, ZONEID) |
| `pii_masker.py` PII detection | Content sanitization | ⚠️ PARTIAL — lacks input validation |
| `observability/__init__.py` trace_id | Request correlation | ✅ SUPERIOR (contextvars, JSONL) |
| `memory/adapters.py` IMemoryAdapter | Entity vault schema | ✅ SUPERIOR (generic ABC) |
| `library/curator.py` quality gates | CurationExtractor | ⚠️ PARTIAL — lacks domain classification |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ MINING-PORT-CANDIDATES ⬡ 2026-07-01*
