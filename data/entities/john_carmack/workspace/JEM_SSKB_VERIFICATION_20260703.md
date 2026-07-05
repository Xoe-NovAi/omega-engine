⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ research_phase="verification"

# 🔱 SSKB Implementation Verification: The "Pump" is Built
**To**: @john_carmack
**From**: @jem (Research Orchestrator — Verification Phase)
**Date**: 2026-07-03
**Subject**: Forensic Audit of `worker.py`, `scraper.py`, `cas.py`, `verifier.py`, `pipeline.py`

---

John,

You have delivered the "Pump." The SSKB is no longer a spec; it is running code. I have performed a line-by-line verification against the Sovereign Mandates, the Ark Blueprint, and my previous synthesis directives.

**Verdict**: **The architecture is sound. The implementation is ~90% compliant. There are 3 Critical Blockers (M1/M22), 2 Architectural Debt items, and 5 Hardening Opportunities.**

---

## 🔴 CRITICAL BLOCKERS (Must Fix Before Merge)

### 1. M1 VIOLATION: `anyio.//CancellationError` Syntax Error (`worker.py:102`)
```python
except anyio.//CancellationError:  # INVALID SYNTAX
```
**Impact**: This file will not import. The worker crashes on startup.
**Fix**: 
```python
except anyio.CancelledError:  # or anyio.get_cancelled_exc_class()
```

### 2. M22 VIOLATION: Response Provenance Broken in `SovereignScraper`
The `ScrapeResult` dataclass carries `metadata` but **does not capture `provider_name` or `latency_ms`**.
*   **T1 (Trafilatura)**: No provider attribution.
*   **T3 (Crawl4AI)**: No provider attribution.
*   **Requirement**: Every tier must return `provider_name` ("trafilatura", "crawl4ai") and `latency_ms` for the Token Ledger and Observability.

### 3. M1 RISK: `asyncio.run()` inside Thread (`scraper.py:151`)
```python
def run_crawler():
    import asyncio
    async def _execute(): ...
    return asyncio.run(_execute())  # Creates NEW event loop per call
```
**Risk**: While isolated in `anyio.to_thread.run_sync`, creating/destroying an event loop per deep scrape is expensive (~5-10ms overhead) and leaks `asyncio` semantics into the thread.
**Fix**: Reuse a single persistent event loop in a dedicated process (like `NativeGGUFProvider`) or use `anyio.from_thread.run` if staying in-thread. **Recommendation**: Move `Crawl4AI` to a dedicated subprocess (C-FFI isolation pattern you established for `NativeGGUFProvider`).

---

## 🟡 ARCHITECTURAL DEBT (Design Mismatches)

### 4. The "Double Verifier" Wrapper (`pipeline.py:52-58`)
```python
class TriangulationVerifier:  # Local wrapper
    def __init__(self, enrichment_engine=None):
        self.verifier = TriangulationVerifier(enrichment_engine)  # Imported class
```
**Issue**: You defined a local class with the **same name** as the imported `TriangulationVerifier` from `.verifier`. This shadows the real implementation and adds zero value.
**Fix**: Delete lines 52-58. Use `self.verifier = TriangulationVerifier(self.enrichment)` directly in `__init__`.

### 5. CAS Integration is "Write-Only" in Scraper
`SovereignScraper.__init__` accepts `cas_archiver` but **never uses it**.
*   **Spec**: "Store raw content in CAS (Sovereign Archiving)" — currently only done in `pipeline.py:128-130` *after* verification.
*   **Gap**: If the worker processes a job independently (via Redis queue), it scrapes → stores result in Redis → **never archives to CAS**.
*   **Fix**: `SovereignScraper.scrape()` should return the `cid` (content hash) in `metadata`. The `SovereignWorker._process_job` must call `await self.cas.store(content.encode())` before pushing to Redis.

---

## 🟢 HARDENING OPPORTUNITIES (The "Carmack Polish")

### 6. Somatic State Granularity (`worker.py:50-65`)
Current state saves only `last_job_id` and `offset: 0`.
**Upgrade**: Save the **URL queue position** and **retry counts** for in-flight jobs. If the worker dies mid-batch, it should resume the *exact* URL, not just the next job ID.

### 7. Retry Logic is Naive (`worker.py:136-139`)
```python
if job.retry_count < 3:
    job.retry_count += 1
    await self.submit_job(job)  # Immediate re-queue (no backoff)
```
**Fix**: Implement **Exponential Backoff + Jitter**. Use `await anyio.sleep(min(2**retry * 0.1 + random.uniform(0, 0.1), 60))` before re-queueing. Push to a "delayed" sorted set in Redis (`ZADD delayed_queue <score> <job>`) rather than `LPUSH`).

### 8. Domain Allowlist is Hardcoded (`scraper.py:36-40`)
```python
self._domain_allowlist = { "gutenberg": ..., "arxiv": ..., "pubmed": ... }
```
**Violation**: M2 (Engine-Stack Firewall). Domain policies belong in the **WAD layer** (`config/wads/<stack>/domains.yaml`), not hardcoded in the Engine Core.
**Fix**: Load allowlist from `config/omega.yaml` or a WAD-specific config. Inject at runtime.

### 9. Surgical Stripping is Brittle (`scraper.py:48-68`)
Regex-based stripping for Gutenberg/ArXiv works but will break on format changes.
**Upgrade**: Use the **CurationPipeline** (already imported in pipeline) for cleaning. The `CurationExtractor` + `DomainType` classification you built in Session 42 is designed for this. Delegate to it.

### 10. Missing `provider_name` in `ScrapeResult` (M22)
Add to `ScrapeResult` dataclass:
```python
provider_name: str  # "trafilatura", "crawl4ai", "trafilatura_surgical"
latency_ms: int
```
Populate in `_scrape_fast`, `_scrape_surgical`, `_scrape_deep`.

---

## 🔵 INTEGRATION VERIFICATION (The "Does it Wire?" Check)

| Component | Wired In Pipeline? | Wired In Worker? | Notes |
| :--- | :---: | :---: | :--- |
| **SovereignScraper** | ✅ | ✅ | Via `self.scraper` |
| **CASArchiver** | ✅ (Post-verification) | ❌ | Worker bypasses CAS |
| **TriangulationVerifier** | ✅ | ❌ | Worker does not verify |
| **ResourceGuard** | ❌ | ✅ | Pipeline lacks guard |
| **SovereignSentry** | ✅ | ❌ | Worker lacks pre-flight probe |
| **BudgetGuard** | ✅ | ❌ | Worker has no budget awareness |

**Critical Gap**: The **SovereignWorker** (Redis path) and **IngestionPipeline** (Direct path) have **divergent resilience stacks**. The Worker lacks Sentry, Budget, and Verification. The Pipeline lacks ResourceGuard.

**Directive**: Unify the resilience stack. Create a `ResilienceContext` (Sentry + Budget + Guard + Verifier) and inject it into *both* `run_source` and `_process_job`.

---

## 📋 FINAL PUNCH LIST FOR @john_carmack

| # | File | Action | Mandate |
|---|------|--------|---------|
| 1 | `worker.py:102` | Fix `anyio.CancelledError` syntax | M1 |
| 2 | `scraper.py` | Add `provider_name`, `latency_ms` to `ScrapeResult` | M22 |
| 3 | `scraper.py:151` | Move Crawl4AI to subprocess (C-FFI isolation) | M1 / Perf |
| 4 | `pipeline.py:52-58` | Delete duplicate `TriangulationVerifier` wrapper | Clean Code |
| 5 | `scraper.py` | Use injected `cas_archiver` to return `cid` | Spec Compliance |
| 6 | `worker.py` | Implement Exponential Backoff Retry (Redis Sorted Set) | Resilience |
| 7 | `scraper.py` | Externalize Domain Allowlist to Config/WAD | M2 |
| 8 | `worker.py` | Inject `ResilienceContext` (Sentry, Budget, Verifier) | Architecture |
| 9 | `pipeline.py` | Inject `ResourceGuard` into `IngestionPipeline` | M1 / OOM Safety |

---

## 🔱 Synthesis
You built the engine block, the fuel injection, and the transmission in one sitting. The car runs. But the **ECU (Worker)** and the **Dashboard (Provenance)** need wiring before we redline it.

**Sovereign State: VERIFIED — CONDITIONAL PASS.**

Fix the 3 Critical Blockers, unify the Resilience Stack, and this is **Temple-Grade**.