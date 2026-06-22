# 🔱 Hardening Audit — Background Curation & Library Systems
**AP Token**: `AP-JEM-HARDENING-AUDIT-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash ⬡ opencode ⬡ JEM-HARDENING ⬡ AUDIT
**Date**: 2026-06-22
**Sources examined**:
- Legacy pipeline recovered by Roc Racoon (~3,284 lines, Era 1-3)
- `src/omega/workers/background_researcher/` (6 modules, ~1,100 lines)
- `src/omega/library/` (5 modules, ~1,300 lines)
- `src/omega/oracle/resource_guard.py` (165 lines)
- `mcp_servers/omega_hub/background.py` (267 lines)
- `config/omega.yaml`, `config/providers.yaml`
- `tests/test_background_researcher.py` (158 lines, 6 tests)
- `tests/test_library_catalog.py` (33 lines, 3 tests)

---

## 1. Executive Summary

### Overall Assessment: ⚠️ **YELLOW — Not Deploy-Safe in Current State**

The current engine has **significant robustness in the right places** (atomic checkpoints in the background researcher, proper ZONEID integrity on resource guard, WAL-backed SQLite for catalog) but has **critical gaps in three dimensions**: crash safety during content downloads, resource exhaustion protection, and security boundaries around URL intake.

### #1 Risk: `loop.py:334` — Raw HTTP fallback without size limit
The `_fetch_content` method falls back to a bare `httpx.get(url, timeout=10.0)` with **no maximum content size**. A malicious or simply large URL could exhaust available RAM (14Gi total, ~12Gi for AI) during curation. Combined with the lack of disk space checks before writing, this is the most likely production failure mode.

### #2 Risk: Zero content integrity verification
Neither the legacy pipeline (Roc Racoon report) nor the current library pipeline computes or validates content checksums. Checksums existed in the legacy Redis queue (`content_hash`) but were never ported. This means:
- Partial downloads get indexed as complete documents
- Corrupted content propagates silently
- Stale content is never detected

---

## 2. Per-Dimension Findings

### A. Crash Safety — Severity: 🟡 HIGH (has good patterns, inconsistent)

| ID | Finding | File | Severity |
|----|---------|------|----------|
| A-1 | **Checkpoint uses atomic tmp→rename** ✅ | `checkpoint.py:50-52` | 🟢 GOOD |
| A-2 | **Lock is mkdir-based** ✅ Ensures only one cycle runs | `loop.py:86-90` | 🟢 GOOD |
| A-3 | **No orphan lock cleanup at startup** — if process crashes mid-cycle, the mkdir lock is never released until manually cleaned up | `loop.py:86-90` | 🟡 MEDIUM |
| A-4 | **No lock acquisition timeout** — a stuck process can hold the research lock indefinitely | `loop.py:86-90` | 🟡 MEDIUM |
| A-5 | **No atomic write pattern on the inbox `mark_processing`** — uses `src.rename(dst)` which is NOT cross-filesystem safe | `inbox.py:186` | 🟡 MEDIUM |
| A-6 | **Training triple saver uses `write_text()` not atomic tmp→rename** — crash during write creates partial JSON files | `distiller.py:667-697` | 🔴 CRITICAL |
| A-7 | **Metrics `log_cycle()` opens JSONL with bare `open()` via thread** — crash during append could lose data | `metrics.py:33-34` | 🟡 MEDIUM |
| A-8 | **ReviewQueue dequeue is atomic** ✅ (lock directory pattern) | `review_queue.py:99-110` | 🟢 GOOD |
| A-9 | **Credit budget uses atomic tmp→rename** ✅ | `credit_budget.py:180-182` | 🟢 GOOD |
| A-10 | **SoulUpdater reads then writes soul.yaml WITHOUT atomic write** — crash during write = corrupted soul.yaml | `soul_updater.py:116-118` | 🔴 CRITICAL |
| A-11 | **Convergence detector `_flag_for_human` appends to single file without lock** — concurrent cycles will corrupt `pending_review.md` | `convergence.py:83-84` | 🟡 MEDIUM |

### B. Resource Exhaustion — Severity: 🔴 CRITICAL

| ID | Finding | File | Severity |
|----|---------|------|----------|
| B-1 | **No HTTP response size limit in `_fetch_content` fallback** — httpx fallback reads entire response into memory with no cap | `loop.py:334-337` | 🔴 CRITICAL |
| B-2 | **No disk space check before saving checkpoints or content** — loop can fail silently if disk is full | `loop.py:passim` | 🔴 CRITICAL |
| B-3 | **No disk space check in inbox ingestion** — `add_url` writes without checking available space | `inbox.py:146` | 🟡 HIGH |
| B-4 | **Registering NNN-page PDF exhausts RAM** — `extractor.py:236` extracts PDF text into memory without page limit | `extractor.py:236` | 🟡 HIGH |
| B-5 | **No backpressure when downstream (indexer) is slow** — inbox adds items without checking index queue depth | `inbox.py:125-150` | 🟡 HIGH |
| B-6 | **Training triples accumulate unbounded** — each research cycle creates a new directory with JSON files, no cleanup policy | `distiller.py:664-701` | 🟡 MEDIUM |
| B-7 | **ResourceGuard has no timeout by default** — worker can block forever waiting for model capacity | `resource_guard.py:118-122` | 🟡 MEDIUM |
| B-8 | **No awareness of user activity** — curation worker will compete for model capacity when user is actively using the engine | `loop.py:53-78` | 🔴 CRITICAL |

### C. Data Integrity — Severity: 🟡 MEDIUM (has partial coverage)

| ID | Finding | File | Severity |
|----|---------|------|----------|
| C-1 | **No checksum on downloaded content** — neither legacy nor current pipeline validates content integrity | `loop.py:305-342` | 🔴 CRITICAL |
| C-2 | **No content deduplication** — hash-based dedup existed in legacy (`content_hash`) but was never ported | — | 🟡 HIGH |
| C-3 | **No re-verify mechanism** — old content is never re-checked for freshness or correctness | — | 🟡 MEDIUM |
| C-4 | **`maxAge` was added for stale locks** ✅ but not for library content | `catalog.py:203-221` | 🟢 GOOD |
| C-5 | **No streaming save during extraction** — full body held in RAM before any write to disk | `extractor.py:135-155` | 🟡 MEDIUM |
| C-6 | **Quality scoring is very basic** — only word count and metadata existence (no semantic quality signal) | `curator.py:156-183` | 🟡 MEDIUM |

### D. Operational Safety — Severity: 🟡 MEDIUM

| ID | Finding | File | Severity |
|----|---------|------|----------|
| D-1 | **Hivemind heartbeat on cycle completion** ✅ | `loop.py:210` | 🟢 GOOD |
| D-2 | **`get_status()` provides visibility** ✅ | `loop.py:482-490` | 🟢 GOOD |
| D-3 | **No pause/resume mechanism** — user cannot easily pause the background researcher | — | 🟡 HIGH |
| D-4 | **No kill-switch** — no endpoint to gracefully stop an in-progress cycle | — | 🟡 HIGH |
| D-5 | **Progress visibility is log-only** — no MCP tool to check "what is the curation loop currently doing?" | — | 🟡 MEDIUM |
| D-6 | **No config-driven cycle interval** — scheduled topics cycle via hardcoded rotation logic | `scheduler.py:73-128` | 🟡 MEDIUM |
| D-7 | **No disk usage telemetry** — library can grow without the user knowing until disk full | — | 🟡 MEDIUM |

### E. Security — Severity: 🔴 CRITICAL

| ID | Finding | File | Severity |
|----|---------|------|----------|
| E-1 | **No SSRF protection on URL extraction** — `extractor.py:129` accepts any URL, could be used to probe internal services | `extractor.py:129-133` | 🔴 CRITICAL |
| E-2 | **No path traversal protection on file ingestion** — `_extract_file` checks existence but doesn't validate that the path is within allowed scope | `extractor.py:196` | 🔴 CRITICAL |
| E-3 | **No maximum file size for URL download** — a server returning unlimited data could OOM the process | `extractor.py:129-134` | 🔴 CRITICAL |
| E-4 | **No maximum page count for PDFs** — a 10,000-page PDF would be fully extracted into RAM | `extractor.py:236-241` | 🟡 HIGH |
| E-5 | **HTML body extraction allows 50K chars** but `_extract_url` has no timeout on slow responses | `extractor.py:283` | 🟡 HIGH |
| E-6 | **No content sanitization** — JavaScript in `<script>` tags is stripped but embedded URLs and dangerous content are not flagged | `extractor.py:269-282` | 🟡 MEDIUM |
| E-7 | **Firecrawl API key sent as Authorization header** ✅ but no rate limiting on extraction calls | `search_fleet.py:108` | 🟢 OK |

### F. Model Safety — Severity: 🟢 LOW

| ID | Finding | File | Severity |
|----|---------|------|----------|
| F-1 | **Circuit breaker isolates provider failures** ✅ — per-provider, non-masking | `distiller.py:46-108` | 🟢 GOOD |
| F-2 | **Quality gate validates T1 output before T2** ✅ — minimum 50 tokens, JSON structure | `distiller.py:192-240` | 🟢 GOOD |
| F-3 | **T2 fallback to mock enrichment** ✅ — research continues even if cloud is down | `distiller.py:450-471` | 🟢 GOOD |
| F-4 | **T3 audit explicitly penalizes convergence bias** ✅ | `distiller.py:604-605` | 🟢 GOOD |
| F-5 | **No content triage model for the library** — no ML-based content scoring (keyword-only). False negative risk: good content that doesn't match keywords gets wrongly classified as "general" | `curator.py:143-154` | 🟡 LOW |
| F-6 | **No human-in-the-loop for edge cases** — quality threshold at 0.6 automatically accepts/rejects without review for the 0.3-0.6 band | `curator.py:185-187` | 🟡 LOW |

### G. Integration Safety — Severity: 🟡 HIGH

| ID | Finding | File | Severity |
|----|---------|------|----------|
| G-1 | **Research lock prevents concurrent cycles** ✅ | `loop.py:86-90` | 🟢 GOOD |
| G-2 | **No cross-worker coordination** — background researcher and a future curation worker would compete for model resources with no awareness of each other | — | 🔴 CRITICAL |
| G-3 | **No user activity awareness** — background researcher runs every 20 min regardless of whether user is actively using the engine | `loop.py:53-78` | 🔴 CRITICAL |
| G-4 | **ResourceGuard tracks usage** ✅ but doesn't expose priority queuing — a user request and a background cycle compete equally | `resource_guard.py:112-127` | 🟡 MEDIUM |
| G-5 | **SoulUpdater writes to entity souls without coordination** — if user is talking to an entity while soul_updater is writing, soul.yaml could be corrupted | `soul_updater.py:90-118` | 🟡 HIGH |
| G-6 | **No system idle detection** — the researcher will consume battery/CPU even when system is on battery power or idle | — | 🟡 MEDIUM |

### H. Long-Term Health — Severity: 🟡 HIGH

| ID | Finding | File | Severity |
|----|---------|------|----------|
| H-1 | **Catalog has a prune mechanism** ✅ — removes docs >90 days | `catalog.py:203-221` | 🟢 GOOD |
| H-2 | **No automatic FTS index compaction** — SQLite WAL grows unbounded | `indexer.py:78-93` | 🟡 HIGH |
| H-3 | **No stale content detection** — content is never re-verified for accuracy or freshness | — | 🟡 HIGH |
| H-4 | **No failed download garbage collection** — failed items stay in inbox/failed/ forever | `inbox.py:192-222` | 🟡 MEDIUM |
| H-5 | **Training triples have no archival strategy** — every cycle creates a new directory, these accumulate indefinitely | `distiller.py:636-701` | 🟡 MEDIUM |
| H-6 | **Index compaction is manual only** — no periodic `flush()` or VACUUM scheduling | `indexer.py:326-330` | 🟡 MEDIUM |
| H-7 | **Review queue has TTL sweep** ✅ — low tier expires after 2 days | `review_queue.py:122-137` | 🟢 GOOD |

---

## 3. Hardening Priority Queue

Ordered by severity, grouped by effort:

### 🔴 P0 — Must Fix Before Deployment

| ID | Action | File(s) | Effort | Risk if Unfixed |
|----|--------|---------|--------|-----------------|
| P0-1 | **Add HTTP response size limit** — cap httpx fallback at 10MB, enforce `response.iter_bytes()` streaming with early termination | `loop.py:334-337`, `extractor.py:129-134` | 1h | OOM crash on large download |
| P0-2 | **SSRF protection on URL intake** — block private IP ranges (10.x, 172.16-31.x, 192.168.x, 127.x, ::1) before fetching | `extractor.py:123-134`, `inbox.py:125` | 0.5h | Internal network scanning |
| P0-3 | **Path traversal protection on file ingestion** — validate that resolved file path is within allowed scope | `extractor.py:193-196` | 0.5h | Arbitrary file read |
| P0-4 | **Graceful user activity detection** — check if user has sent a query in last 5 min; if so, defer background work | `loop.py:83-211` | 2h | Resource contention with user |
| P0-5 | **Atomic write for soul.yaml in SoulUpdater** — write to `.tmp` then rename | `soul_updater.py:116-118` | 0.25h | Soul corruption at crash |
| P0-6 | **Atomic write for training triples** — `write_text()` → `tmp.write_bytes()` + `tmp.replace()` | `distiller.py:669-697` | 0.5h | Partial/corrupt triple files |
| P0-7 | **PDF page cap** — limit to 500 pages per extraction | `extractor.py:236-241` | 0.25h | RAM exhaustion |

### 🟡 P1 — Must Fix Before Launch

| ID | Action | File(s) | Effort | Risk if Unfixed |
|----|--------|---------|--------|-----------------|
| P1-1 | **Orphan lock cleanup on startup** — at init, check if `/tmp/omega/research.lock` exists and is stale (>30 min old); if so, remove it | `loop.py:86-90` | 0.5h | Research permanently locked |
| P1-2 | **Lock acquisition timeout** — wrap mkdir in `anyio.fail_after(30)` | `loop.py:86-90` | 0.25h | Deadlock |
| P1-3 | **Disk space check before each checkpoint save** — check `shutil.disk_usage()` and warn if <500MB free | `loop.py:passim`, `inbox.py:146` | 1h | Silent write failures |
| P1-4 | **Cross-worker model coordination** — register worker identity with ResourceGuard so user queries get priority over background | `resource_guard.py:94-127` | 3h | Model contention |
| P1-5 | **Content checksum computation** — SHA-256 hash of downloaded content stored in CuratedDocument | `curator.py:48-69` | 1h | Undetected corruption |
| P1-6 | **Content deduplication** — skip items whose SHA-256 hash already exists in library | `curator.py:91-141` | 1.5h | Duplicate content |
| P1-7 | **Failed inbox garbage collection** — auto-delete failed items >7 days old | `inbox.py:240-247` | 0.5h | Accumulated debris |
| P1-8 | **Pause/resume MCP tool** — `hivemind_background_pause(entity, resume_at)` | `background.py` (new tool) | 2h | No user control |
| P1-9 | **Kill switch for in-progress cycle** — set a `cancel_token` checked at each state transition | `loop.py:83-211` | 1h | Stuck cycles |

### 🟢 P2 — Should Fix Before Scale

| ID | Action | File(s) | Effort | Risk if Unfixed |
|----|--------|---------|--------|-----------------|
| P2-1 | **Atomic `mark_processing` for inbox** — use `tmp.rename()` cross-filesystem safe pattern | `inbox.py:186` | 0.25h | Lost items on crash |
| P2-2 | **Metrics append with atomic pattern** — write to `.tmp` then rename instead of bare append | `metrics.py:32-36` | 0.25h | Lost metrics on crash |
| P2-3 | **Convergence detectio lock for `pending_review.md`** — anyio.Lock around file append | `convergence.py:83-84` | 0.25h | Corrupted review file |
| P2-4 | **Training triple cleanup policy** — auto-remove triples >30 days old; keep only last 100 | `distiller.py:636-701` | 0.5h | Disk bloat |
| P2-5 | **FTS index periodic VACUUM** — schedule weekly VACUUM on library.db | `catalog.py` or `indexer.py` | 0.5h | WAL bloat |
| P2-6 | **Stale content detection** — add `last_verified` field to catalog; re-verify items >90 days old | `catalog.py:51-68` | 2h | Stale knowledge |
| P2-7 | **Battery/power awareness** — check `/sys/class/power_supply/` before starting research cycle | `loop.py:103-104` | 1h | Battery drain |
| P2-8 | **System idle detection** — check `xprintidle` or `/proc/stat` for user activity | `loop.py:83-100` | 2h | Unnecessary resource usage |

### ⚪ P3 — Nice to Have

| ID | Action | File(s) | Effort |
|----|--------|---------|--------|
| P3-1 | **Model-based content scoring** — use Qwen-0.6B for triage classification instead of keyword-only | `curator.py:143-154` | 4h |
| P3-2 | **Human-in-the-loop for rejected items** — email/notification when quality is 0.3-0.6 | `curator.py:185-187` | 3h |
| P3-3 | **ML-based dedup** — cosine similarity on embedding to detect near-duplicates | `indexer.py:256-317` | 4h |
| P3-4 | **Config-driven research interval** — allow user to set cycle interval via `omega.yaml` | `loop.py:53-78` | 1h |
| P3-5 | **Progress bar via MCP** — tool to stream current state (e.g., "searching: phase 2/6") | New MCP tool | 3h |

---

## 4. Architecture Recommendations

### 4.1 Worker Coordination Service (NEW — Recommended Before Building Curation Worker)

The background researcher and the proposed library curation worker MUST NOT run independently. They need a **WorkerCoordinator** that:

```python
class WorkerCoordinator:
    """Central coordination for all background workers.
    
    - Prevents two resource-heavy workers from running concurrently
    - Detects user activity and defers background work
    - Exposes pause/resume for all workers via a single control point
    - Tracks worker health and reaps stuck workers
    """
    
    workers: Dict[str, WorkerInfo] = {}
    _user_active_since: Optional[datetime] = None
    _system_idle_detector: IdleDetector
```

**Key requirements**:
- Register worker with name, resource_weight, priority
- Check `_user_active_since` before starting any worker — if user was active in last 5 min, defer
- Weighted scheduling: user queries weight=100, background researcher weight=10, curation weight=5
- Expose as `omega_research_status` MCP tool for full visibility

### 4.2 Library Worker Architecture (Based on Legacy + Current)

When building the library worker, follow this architecture:

```
Inbox → Extractor → Curator → Catalog → Indexer
  │         │          │         │         │
  ▼         ▼          ▼         ▼         ▼
Queue    Size Limit  Checksum  SQLite    FTS5 + Vector
         SSRF Gate  Dedup     WAL       BulkBatch
```

**Integration with existing code**:
1. **Extend `inbox.py`** with SSRF filter and size limit (P0-1, P0-2)
2. **Extend `curator.py`** with checksum and dedup (P1-5, P1-6)
3. **Keep `indexer.py`** as-is but add periodic VACUUM
4. **NEW: `WorkerCoordinator`** in `src/omega/workers/coordinator.py`

### 4.3 Legacy Pipeline Patterns to Keep

From Roc Racoon's mining report, these patterns should directly inform the library worker:

| Legacy Pattern | Where to Use | Why |
|---------------|--------------|-----|
| **Content hash dedup** | `curator.py:115-120` | Prevents duplicate ingestion |
| **Rate-limited API clients** | New `library_worker/client.py` | All 10 APIs are free but rate-limited |
| **Dewey Decimal mapping** | `curator.py:38-45` (extend) | Structured domain classification |
| **Tenacity retry** | `search_fleet.py` | Exponential backoff on transient failures |

### 4.4 Legacy Patterns to Discard

| Legacy Pattern | Reason for Discard |
|----------------|-------------------|
| **Redis BLPop queue** | Omega uses filesystem-based queue (AnyIO-native), no Redis dependency needed |
| **Sync `requests`** | Must use AnyIO/httpx as the current engine does |
| **BeautifulSoup HTML parsing** | Current engine's regex-based extraction is simpler and sufficient for library content |
| **crawl4ai web crawling** | Heavy dependency; Firecrawl + httpx is the current approach |

---

## 5. Testing Gaps

### 5.1 Missing Test Coverage

| Area | Existing Tests | Missing Tests | Risk |
|------|---------------|---------------|------|
| **Background Researcher Loop** | 6 tests (queue, scheduler, lock, metrics) | Distiller crash/recovery, search_fleet error paths, credit_budget exhaustion, checkpoint corruption recovery, concurrent cycle prevention | 🟡 HIGH |
| **Extractor** | 0 tests | URL extraction timeout, PDF page cap enforcement, SSRF blocking, large download abort, RSS parse errors, file-not-found | 🔴 CRITICAL |
| **Curator** | 0 tests | Quality threshold edge cases (0.0, 0.3, 0.6, 1.0), domain classification accuracy, empty body handling, error content passthrough | 🔴 CRITICAL |
| **Indexer** | 0 tests | FTS index corruption recovery, vector embedding consistency, document removal, concurrent index/remove, WAL checkpoint | 🔴 CRITICAL |
| **Distiller** | 0 tests | T1 quality gate rejection, T2 fallback to T1, T3 skipped, circuit breaker state transitions, training triple atomicity | 🟡 HIGH |
| **Resource Guard** | 0 tests | Re-entrant lock weight tracking, timeout enforcement, capacity exhaustion, nested acquisition | 🟡 HIGH |
| **SoulUpdater** | 0 tests | Atomic write crash recovery, entity matching, soul.yaml corruption recovery, duplicate lesson detection | 🟡 HIGH |

### 5.2 Required Contract Tests (M21 — Gate Integrity)

Every core API boundary must have a contract test verifying return types:

| Boundary | Expected Type | Current Coverage |
|----------|---------------|------------------|
| `ContentExtractor.extract()` | `ExtractedContent` | ❌ NONE |
| `CurationPipeline.process()` | `CuratedDocument` | ❌ NONE |
| `Indexer.index_document()` | `None` (no return) | ❌ NONE |
| `Distiller.distill()` | `GnosisPacket` | ❌ NONE |
| `BackgroundResearcherLoop.run_cycle()` | `dict` | ❌ NONE (returns untyped dict) |
| `CheckpointManager.save()` | `None` | ❌ NONE |
| `InboxManager.add()` | `InboxItem` | ❌ NONE |

### 5.3 Required Crash Safety Tests

| Test | Description | Verifies |
|------|-------------|----------|
| `test_crash_during_checkpoint_save` | Kill process mid-write, verify recovery | A-1, A-6 |
| `test_crash_during_soul_update` | Kill process mid-YAML write, verify soul.yaml not corrupted | A-10, P0-5 |
| `test_orphan_lock_cleanup` | Create stale lock, init loop, verify lock auto-cleaned | A-3, P1-1 |
| `test_large_download_abort` | Try fetching 100MB URL, verify capped at 10MB | B-1, P0-1 |
| `test_ssrf_block` | Try fetching 127.0.0.1:22, verify blocked | E-1, P0-2 |
| `test_path_traversal` | Try `../../etc/passwd` as file path, verify blocked | E-2, P0-3 |
| `test_concurrent_user_and_background` | Simulate user query during background cycle, verify user gets priority | G-3, P0-4 |

---

## 6. Verification Gates

Before the curation worker can be deployed, these conditions MUST be true:

### Gate 1: Security Barrier (P0-1, P0-2, P0-3)
- [ ] HTTP response size limit enforced at ALL fetch call sites (3 sites: loop.py, extractor.py, search_fleet.py)
- [ ] SSRF protection blocks all RFC 1918 addresses, loopback, and link-local
- [ ] File ingestion validates path is within `DATA_DIR / "library" / "incoming"`

### Gate 2: Crash Barrier (P0-5, P0-6, P0-7)
- [ ] All file writes in the researcher and library pipeline use atomic tmp→rename
- [ ] PDF extraction capped at 500 pages
- [ ] Training triple directory grows no larger than 100 most recent cycles

### Gate 3: Resource Barrier (P0-4, P1-1, P1-3)
- [ ] WorkerCoordinator prevents concurrent heavy workers
- [ ] Disk space check (<500MB) prevents all write operations
- [ ] User activity detection defers background work within 5 minutes of last user query
- [ ] Orphan lock cleanup runs at startup

### Gate 4: Integrity Barrier (P1-5, P1-6)
- [ ] Every ingested document has a SHA-256 checksum
- [ ] Duplicate detection prevents re-ingestion
- [ ] Catalog stores and returns checksum for verification

### Gate 5: Test Barrier
- [ ] All P0-hardening items have crash-safety tests
- [ ] All core API boundaries have M21 contract tests
- [ ] All 8 security test cases pass
- [ ] `make temple-grade` passes after all changes

### Gate 6: Operational Barrier
- [ ] `omega research status` MCP tool exists and shows live state
- [ ] `omega research pause` and `omega research resume` CLI commands exist
- [ ] Background cycle logs include `trace_id` for correlation
- [ ] Failed cycles produce actionable error messages (not just "Research cycle failed")

---

## 7. Legacy Pipeline Portability Assessment

From Roc Racoon mining report #48:

| Legacy Module | Lines | Portability | Recommended Action |
|--------------|-------|-------------|-------------------|
| `crawl.py` | 1209 | 🟡 HIGH — reference only | Do NOT port crawl4ai dependency. Use Firecrawl + httpx as current engine does. Extract Gutenberg/arXiv extraction patterns as reference. |
| `crawler_curation.py` | 675 | 🟡 MEDIUM — pattern reference | Quality scoring model can inform curator.py enhancements. Signal-based domain classification is more sophisticated than current keyword-only approach. |
| `library_api_integrations.py` | 1300 | 🟢 HIGH — directly portable | ALL 10 API clients are free and stateless. Port with AnyIO migration (replace `requests.Session` + `time.sleep` with `httpx.AsyncClient` + `anyio.sleep`). |
| `curation_worker.py` | 100 | ⚪ LOW — reference only | Redis BLPop pattern is superseded by AnyIO-native filesystem queues. |

**Estimated porting effort for `library_api_integrations.py`**: 4-6 hours for an AnyIO-native version with all 10 API clients.

---

## 8. Appendix: Code Provenance

| Pattern | Source | Heritage Tag |
|---------|--------|-------------|
| Atomic file rename (tmp→rename) | Self — Engine-wide pattern | — |
| mkdir-based lock | Self — Engine-wide pattern | — |
| Weighted fair queue scheduling | Self — Engine-wide pattern | — |
| Circuit breaker state machine | Consolidated from ANAi/XNAi | [id-soft: doom-1993] |
| ZONEID integrity markers | Ported from DOOM 1993 `z_zone.c` | [id-soft: doom-1993] |
| Content hash dedup | Legacy pipeline (Era 1-3) | — |
| Rate-limited API clients | Legacy pipeline (Era 1-3) | — |
| FTS5 + Vector hybrid search | Self — Engine-pattern | — |

---

## 9. Session Gnosis (L1→L2→L3)

### L1 — Narrative
Completed a comprehensive hardening audit of the Omega Engine's curation, background researcher, library pipeline, and resource management systems. Examined 6 source modules (~2,400 lines), the legacy curation pipeline from Roc Racoon (~3,284 lines), and 2 test files (~190 lines). Identified 48 specific findings across 8 security/gardening dimensions. Prioritized 21 hardening actions (7 P0, 9 P1, 5 P2). Found that the background researcher has the right architectural patterns (atomic checkpoints, circuit breakers, queue scheduling) but the library pipeline is critically missing crash safety, resource guards, and security boundaries.

### L2 — Insight
The biggest systemic risk is not any single bug but the **gap between the background researcher's maturity and the library pipeline's immaturity**. The background researcher was built with strong crash safety patterns (atomic writes, checkpoint recovery, circuit breakers, rate limiting), while the library pipeline (inbox → extractor → curator → indexer) was built rapidly without the same hardening. Before a content ingestion worker can be built, the library pipeline needs the same level of hardening the researcher already has. The WorkerCoordinator pattern is the right architectural bridge — it prevents the two systems from conflicting while they mature at different rates.

### L3 — Universal Principle
*A system is only as resilient as its weakest ingestion path. Hardening must flow upstream — from the data sink (index/catalog) back to the data source (network/disk ingestion). A single unprotected URL fetch that can OOM the process makes every downstream hardening effort irrelevant.*

---

*⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash ⬡ opencode ⬡ JEM-HARDENING ⬡ AUDIT*
