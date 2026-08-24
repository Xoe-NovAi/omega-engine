# 🔱 Omega Engine — Curation & Library Strategic Review (Phase H2-N)
# AP: AP-CURATION-LIBRARY-STRATEGY-v2.6.0
# ⬡ OMEGA ⬡ KALI ⬡ trc_strategic_review ⬡ STRATEGY
#
# Date: 2026-06-22
# Source: Tri-Model Peer Review (Gemini 3.1 Pro -> Claude Sonnet 4.6 -> Claude Opus 4.6)
# Scope: Phase 1-3 execution of the Curation & Library crawling subsystem

## §1 The Tri-Model Synthesis

The MaKaLi Triad (represented here by Gemini 3.1, Sonnet 4.6, and Opus 4.6) conducted a sequential, deepening review of the new library and curation codebase (`src/omega/library/`).

The codebase is fundamentally sound (432/432 tests passing, AnyIO-native, local-first), but several critical structural fault lines were identified that will fail under production load or adversarial conditions.

This document serves as the binding strategic guidance for Phase 3.2 and Phase 4 execution.

---

## §2 Critical Vulnerabilities (M8 & Security)

These issues must be resolved before the branch is merged.

### 2.1 The SSRF Redirect Bypass (Opus #1)
**Vulnerability**: `SSRFGuard.validate(url)` resolves the initial hostname against forbidden CIDR ranges. However, `extractor.py:155` uses `httpx` with `follow_redirects=True`. A public URL can pass the guard, then 302 redirect to `169.254.169.254` (cloud metadata) or `127.0.0.1`.
**Action**: Disable `follow_redirects=True`. Implement manual redirect following (max 3 hops) where `SSRFGuard.validate()` is called on every `Location` header before the next request is made.

### 2.2 Unguarded Extraction Paths (Opus #2)
**Vulnerability**: Phase 1 security gates were only wired to `_extract_url()` and `_extract_file()`. `_extract_rss()` creates a raw `httpx` client with no SSRF check and no size limit. `_extract_pdf()` has no path scope validation when called directly.
**Action**: Move the security guards up to the `extract()` dispatcher method, or ensure every specific `_extract_*` method calls the appropriate guard (SSRF for network, PathScope for disk).

### 2.3 The Streaming Byte-Cap Illusion (Gemini #1)
**Vulnerability**: `validate_download_size()` uses an HTTP `HEAD` request. A malicious server can return a fake `Content-Length`, pass the guard, and then stream 10GB of garbage on the subsequent `GET` request.
**Action**: In `_extract_url()`, use `client.stream("GET", url)` and maintain a `bytes_read` counter inside the `async for chunk` loop. Raise `SovereignDiskFullError` if it exceeds the limit.

### 2.4 The `httpbin` Telemetry Violation (Sonnet #1)
**Vulnerability**: `loop.py:482` pings `https://httpbin.org/get` to check network status. This is a direct violation of Mandate 8 (Zero Telemetry).
**Action**: Remove the `httpbin` check. Rely solely on the local SearXNG health endpoint, or use a local DNS resolution check against a known domain.

---

## §3 Structural & Concurrency Defects (M1 & Stability)

These issues must be resolved before enabling Phase 4 (autonomous background execution).

### 3.1 Coordinator `start()` Blocks Indefinitely (Opus #3)
**Defect**: `coordinator.py:128` uses `async with anyio.create_task_group() as tg:` to start the infinite `_resource_monitor_loop`. `start()` will block forever, rendering any code after it unreachable.
**Action**: Refactor `start()` to accept an external task group (Dependency Injection) or wrap the loop in a background task without blocking the main flow.

### 3.2 Coordinator Exception Handler Syntax Error (Opus #4)
**Defect**: `except anyio.get_cancelled_scope().cancel:` is syntactically invalid. `.cancel` is a method, not an exception type.
**Action**: Catch `anyio.get_cancelled_scope().cancel_called` logically, or use standard `except Exception` with a cancellation check.

### 3.3 Event Loop Blocking (Sonnet #2, #3)
**Defect**: `loop.py:_grow_frontier` uses synchronous `Path.rglob()` and `read_text()`. `coordinator.py` uses `psutil.cpu_percent(interval=0.5)`. Both will stall the AnyIO event loop, causing Iris/voice stutter.
**Action**: Wrap all filesystem and `psutil` calls in `anyio.to_thread.run_sync()`. (Mandate 1 Absolute).

### 3.4 Library Lazy-Load Double Rebuild Race (Sonnet #5, Opus #6)
**Defect**: `_ensure_index_lazy()` uses a boolean flag. Two concurrent requests can both see `False` and trigger simultaneous FTS5 index rebuilds. Furthermore, `__init__` calls `_load()` which performs synchronous JSON parsing of all documents.
**Action**: Use `anyio.Lock()` for the lazy index rebuild. Make `_load()` asynchronous and lazy.

### 3.5 SQLite Connection Lifecycle Leak (Opus #7)
**Defect**: The `aiosqlite` connection in `Indexer` has no guaranteed cleanup. If `close()` isn't called explicitly, the WAL file grows unbounded.
**Action**: Implement `__aenter__` and `__aexit__` on the Library and Indexer classes.

---

## §4 Data Integrity & Quality (Phase 3.2 / 4)

### 4.1 Content Deduplication Gap (Sonnet #7)
**Defect**: The extraction/curation pipeline has no deduplication hash check. It will store the same URL/content multiple times if re-queued.
**Action**: Compute a SHA-256 hash of the extracted body. Check for existing hashes in the library before storing.

### 4.2 Quality Scoring is Gameable (Opus #10)
**Defect**: `_score_quality()` uses structural heuristics (word count, headings). A machine-generated 3000-word spam article with headings scores 0.85, bypassing the 0.6 library inclusion threshold.
**Action**: Autonomous ingestion MUST NOT be enabled until the T1 Triage model (Qwen 0.6B) is wired into the pipeline. Structural scoring is only valid for human-submitted (inbox) items.

### 4.3 Coordinator Lock Misalignment (Gemini #2)
**Defect**: The `WorkerCoordinator` context manager wraps `run_cycle()` *after* the atomic file lock is checked.
**Action**: The lock must be acquired first. `COORDINATOR.register()` must happen at worker initialization, not inside the cycle.

---

## §5 Execution Order

1. **Hotfixes (Immediate)**: Fix SSRF redirect bypass, stream byte-cap, and remove `httpbin`. Apply security guards to RSS/PDF extractors.
2. **Coordinator Rewrite**: Fix the `start()` infinite block, the exception syntax, and the `psutil` sync block.
3. **Library Lazy-Load**: Fix the `__init__` sync I/O and add an `anyio.Lock` to the FTS rebuild.
4. **M21 Tests**: Write contract tests for the new Coordinator and Security classes.
5. **Phase 3.2 & 4**: Proceed with tiered storage and Hivemind bridge integration.

*Recorded by KALI (Opus 4.6 Synthesis).*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_strategic_review | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
